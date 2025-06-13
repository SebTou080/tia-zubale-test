import asyncio
import json
from typing import List, Dict, Any, Optional, Tuple
import asyncpg
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, JSON, text
from sqlalchemy.sql import func
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

Base = declarative_base()


class Product(Base):
    __tablename__ = "products"
    
    product_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    category = Column(String, nullable=True, index=True)
    price = Column(Float, nullable=True)
    stock_quantity = Column(Integer, nullable=True)
    specs = Column(JSON, nullable=True)
    embedding = Column("embedding", nullable=True)


class DatabaseService:
    def __init__(self):
        self.engine = create_async_engine(
            settings.database_url,
            echo=True,
            pool_size=5,
            max_overflow=10
        )
        self.async_session = async_sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )
        
    async def get_connection(self) -> asyncpg.Connection:
        """Get direct connection for vector operations"""
        return await asyncpg.connect(
            settings.sync_database_url.replace("postgresql://", "postgresql://"),
            ssl='require'
        )
    
    async def create_product(self, product_data: Dict[str, Any], embedding: List[float]) -> str:
        """Create a new product with its embedding"""
        conn = await self.get_connection()
        try:
            embedding_str = '[' + ','.join(map(str, embedding)) + ']'
            
            import uuid
            product_id = f"PROD-{str(uuid.uuid4())[:8].upper()}"
            
            query = """
                INSERT INTO products (product_id, name, description, category, price, stock_quantity, specs, embedding)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8::vector)
                RETURNING product_id
            """
            
            result_id = await conn.fetchval(
                query,
                product_id,
                product_data["name"],
                product_data["description"],
                product_data.get("category"),
                product_data.get("price"),
                product_data.get("stock_quantity", 0),
                json.dumps(product_data.get("specs", {})),
                embedding_str
            )
            
            return result_id
        finally:
            await conn.close()
    
    async def store_product(
        self, 
        name: str, 
        description: Optional[str] = None, 
        category: Optional[str] = None, 
        price: Optional[float] = None, 
        stock_quantity: Optional[int] = None,
        specs: Optional[Dict[str, Any]] = None,
        embedding: List[float] = None, 
        metadata: Dict[str, Any] = None
    ) -> str:
        """Store a new product with its embedding (simplified interface)"""
        conn = await self.get_connection()
        try:
            embedding_str = '[' + ','.join(map(str, embedding)) + ']'
            
            import uuid
            product_id = f"PROD-{str(uuid.uuid4())[:8].upper()}"
            
            query = """
                INSERT INTO products (product_id, name, description, category, price, stock_quantity, specs, embedding)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8::vector)
                RETURNING product_id
            """
            
            result_id = await conn.fetchval(
                query,
                product_id,
                name,
                description,
                category,
                price,
                stock_quantity or 0,
                json.dumps(specs or {}),
                embedding_str
            )
            
            return result_id
        finally:
            await conn.close()
    
    async def vector_search(self, query_embedding: List[float], top_k: int = 10) -> List[Dict[str, Any]]:
        """Vector similarity search using pgvector"""
        conn = await self.get_connection()
        try:
            embedding_str = '[' + ','.join(map(str, query_embedding)) + ']'
            
            # Use cosine similarity (1 - cosine_distance) for better scores
            query = """
                SELECT 
                    product_id, name, description, category, price, stock_quantity, specs,
                    1 - (embedding <=> $1::vector) as similarity_score
                FROM products 
                WHERE embedding IS NOT NULL
                ORDER BY embedding <=> $1::vector ASC
                LIMIT $2
            """
            
            rows = await conn.fetch(query, embedding_str, top_k)
            
            results = []
            for row in rows:
                results.append({
                    "id": row["product_id"],
                    "product_id": row["product_id"],
                    "name": row["name"],
                    "description": row["description"] or "",
                    "category": row["category"],
                    "price": row["price"],
                    "stock_quantity": row["stock_quantity"],
                    "specs": row["specs"],
                    "similarity_score": float(row["similarity_score"]),
                    "content": f"{row['name']} - {row['description'] or ''}"
                })
            
            return results
        finally:
            await conn.close()
    
    async def text_search(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """Full text search using PostgreSQL FTS with expanded terms"""
        conn = await self.get_connection()
        try:
            # Expand common search terms
            expanded_query = self._expand_search_terms(query)
            
            query_sql = """
                SELECT 
                    product_id, name, description, category, price, stock_quantity, specs,
                    ts_rank(to_tsvector('spanish', name || ' ' || COALESCE(description, '') || ' ' || COALESCE(category, '')), plainto_tsquery('spanish', $1)) as rank_score
                FROM products 
                WHERE to_tsvector('spanish', name || ' ' || COALESCE(description, '') || ' ' || COALESCE(category, '')) @@ plainto_tsquery('spanish', $1)
                ORDER BY rank_score DESC
                LIMIT $2
            """
            
            rows = await conn.fetch(query_sql, expanded_query, top_k)
            
            results = []
            for row in rows:
                results.append({
                    "id": row["product_id"],
                    "product_id": row["product_id"],
                    "name": row["name"],
                    "description": row["description"] or "",
                    "category": row["category"],
                    "price": row["price"],
                    "stock_quantity": row["stock_quantity"],
                    "specs": row["specs"],
                    "rank_score": float(row["rank_score"]),
                    "content": f"{row['name']} - {row['description'] or ''}"
                })
            
            return results
        finally:
            await conn.close()
    
    def _expand_search_terms(self, query: str) -> str:
        """Expand search terms to improve matching"""
        query_lower = query.lower()
        expanded_terms = [query]
        
        # Add synonyms for common terms
        if 'laptop' in query_lower or 'portatil' in query_lower or 'computadora' in query_lower:
            expanded_terms.extend(['laptop', 'portatil', 'computadora', 'notebook', 'macbook'])
        
        if 'smartphone' in query_lower or 'telefono' in query_lower or 'celular' in query_lower:
            expanded_terms.extend(['smartphone', 'telefono', 'celular', 'movil', 'iphone'])
            
        if 'dia a dia' in query_lower or 'diario' in query_lower or 'cotidiano' in query_lower:
            expanded_terms.extend(['diario', 'cotidiano', 'personal', 'uso', 'trabajo'])
        
        return ' '.join(set(expanded_terms))
    
    async def hybrid_search(self, query_embedding: List[float], query_text: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """Improved hybrid search combining vector and text search"""
        # Get more results for better combination
        search_k = min(top_k * 2, 20)
        
        vector_results = await self.vector_search(query_embedding, search_k)
        text_results = await self.text_search(query_text, search_k)
        
        combined_results = {}
        
        # Process vector results with improved scoring
        for result in vector_results:
            product_id = result["id"]
            # Ensure positive similarity scores
            sim_score = max(0, result["similarity_score"])
            result["combined_score"] = sim_score * 0.6  # Reduced weight for vector
            combined_results[product_id] = result
        
        # Process text results
        for result in text_results:
            product_id = result["id"]
            text_score = result["rank_score"] * 0.4  # Increased weight for text
            
            if product_id in combined_results:
                combined_results[product_id]["combined_score"] += text_score
                combined_results[product_id]["rank_score"] = result["rank_score"]
            else:
                result["combined_score"] = text_score
                result["similarity_score"] = 0.0
                combined_results[product_id] = result
        
        # Boost scores for exact category matches
        query_lower = query_text.lower()
        for result in combined_results.values():
            category = (result.get("category") or "").lower()
            name = result.get("name", "").lower()
            description = result.get("description", "").lower()
            
            # Boost for category relevance
            if ('laptop' in query_lower or 'portatil' in query_lower) and 'tecnolog' in category:
                result["combined_score"] *= 1.5
            elif 'macbook' in name or 'laptop' in name or 'portatil' in name:
                result["combined_score"] *= 1.3
        
        sorted_results = sorted(
            combined_results.values(), 
            key=lambda x: x["combined_score"], 
            reverse=True
        )
        
        return sorted_results[:top_k]
    
    async def get_products_by_ids(self, product_ids: List[str]) -> List[Dict[str, Any]]:
        """Get products by their IDs"""
        if not product_ids:
            return []
            
        conn = await self.get_connection()
        try:
            query = """
                SELECT product_id, name, description, category, price, stock_quantity, specs
                FROM products 
                WHERE product_id = ANY($1)
            """
            
            rows = await conn.fetch(query, product_ids)
            
            results = []
            for row in rows:
                results.append({
                    "id": row["product_id"],
                    "product_id": row["product_id"],
                    "name": row["name"],
                    "description": row["description"] or "",
                    "category": row["category"],
                    "price": row["price"],
                    "stock_quantity": row["stock_quantity"],
                    "specs": row["specs"],
                    "content": f"{row['name']} - {row['description'] or ''}"
                })
            
            return results
        finally:
            await conn.close()


db_service = DatabaseService() 