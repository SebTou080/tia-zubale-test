from fastapi import APIRouter, HTTPException, status
from datetime import datetime
import logging
from app.api.schemas import (
    ProductIngest, QueryRequest, QueryResponse, 
    IngestResponse, HealthResponse, ChatMessage
)
from app.services.database import db_service
from app.services.llm_service import llm_service
from app.graph.builder import rag_agent

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(),
        version="1.0.0"
    )


@router.post("/ingest", response_model=IngestResponse)
async def ingest_product(product: ProductIngest):
    """Ingest a new product into the database"""
    logger.info(f"Ingesting product: {product.name}")
    
    try:
        text_parts = [product.name]
        if product.description:
            text_parts.append(product.description)
        if product.category:
            text_parts.append(product.category)
        
        product_text = " ".join(text_parts)
        embedding = await llm_service.generate_embedding(product_text)
        
        product_id = await db_service.store_product(
            name=product.name,
            description=product.description,
            category=product.category,
            price=product.price,
            stock_quantity=product.stock_quantity,
            specs=product.specs,
            embedding=embedding,
            metadata=product.metadata or {}
        )
        
        logger.info(f"Product ingested successfully with ID: {product_id}")
        return IngestResponse(
            product_id=product_id,
            message="Product ingested successfully",
            status="success"
        )
        
    except Exception as e:
        logger.error(f"Error ingesting product: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error ingesting product: {str(e)}"
        )


@router.post("/query", response_model=QueryResponse)
async def query_products(request: QueryRequest):
    """Query products using RAG"""
    logger.info(f"Processing query: {request.query}")
    
    try:
        conversation_history = []
        if request.conversation_history:
            conversation_history = [
                {"role": msg.role, "content": msg.content} 
                for msg in request.conversation_history
            ]
        
        import time
        result = await rag_agent.ainvoke({
            "original_query": request.query,
            "conversation_history": conversation_history,
            "query_plan": [],
            "retrieved_docs": [],
            "generated_answer": "",
            "final_answer": "",
            "evaluation_result": {},
            "confidence_score": 0.0,
            "processing_steps": [],
            "error_messages": [],
            "start_time": time.time(),
            "end_time": None,
            "max_retries": 1,
            "current_retry": 0
        })
        
        updated_history = conversation_history.copy()
        updated_history.append({"role": "user", "content": request.query})
        updated_history.append({"role": "assistant", "content": result["final_answer"]})
        
        conversation_messages = [
            ChatMessage(role=msg["role"], content=msg["content"]) 
            for msg in updated_history
        ]
        
        sources = []
        for doc in result.get("retrieved_docs", []):
            sources.append({
                "product_id": doc.get("product_id", doc.get("id", "")),
                "product_name": doc.get("name", ""),
                "relevance_score": doc.get("combined_score", doc.get("similarity_score", 0.0)),
                "content_snippet": doc.get("content", f"{doc.get('name', '')} - {doc.get('description', '')}")[:200]
            })
        
        logger.info(f"Query processed successfully")
        return QueryResponse(
            query=request.query,
            answer=result["final_answer"],
            sources=sources,
            confidence_score=result.get("confidence_score", 0.0),
            processing_time_ms=int((result.get("end_time", 0) - result.get("start_time", 0)) * 1000),
            conversation_history=conversation_messages
        )
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing query: {str(e)}"
        )


