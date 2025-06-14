import pytest
import pytest_asyncio
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from typing import List, Dict, Any
from httpx import AsyncClient
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def mock_llm_service():
    with patch("app.services.llm_service.llm_service") as mock:
        mock.generate_embedding = AsyncMock(return_value=[0.1] * 1536)
        mock.generate_answer_with_memory = AsyncMock(return_value="Mocked response")
        mock.evaluate_answer = AsyncMock(return_value={
            "confidence_score": 0.8,
            "relevance": "high",
            "is_factual": True
        })
        mock.contextualize_query = AsyncMock(return_value="Contextualized query")
        mock.plan_query = AsyncMock(return_value=["test query"])
        yield mock


@pytest.fixture
def mock_db_service():
    with patch("app.services.database.db_service") as mock:
        mock.store_product = AsyncMock(return_value="PROD-TEST123")
        mock.hybrid_search = AsyncMock(return_value=[
            {
                "id": "PROD-TEST123",
                "product_id": "PROD-TEST123",
                "name": "Test Product",
                "description": "Test description",
                "category": "Test Category",
                "price": 99.99,
                "similarity_score": 0.85,
                "combined_score": 0.82,
                "content": "Test Product - Test description"
            }
        ])
        mock.vector_search = AsyncMock(return_value=[
            {
                "id": "PROD-TEST123",
                "product_id": "PROD-TEST123",
                "name": "Test Product",
                "description": "Test description",
                "similarity_score": 0.85,
                "content": "Test Product - Test description"
            }
        ])
        mock.text_search = AsyncMock(return_value=[
            {
                "id": "PROD-TEST123",
                "product_id": "PROD-TEST123",
                "name": "Test Product",
                "description": "Test description",
                "rank_score": 0.75,
                "content": "Test Product - Test description"
            }
        ])
        yield mock


@pytest.fixture
def mock_rag_agent():
    with patch("app.graph.builder.rag_agent") as mock:
        mock.ainvoke = AsyncMock(return_value={
            "original_query": "test query",
            "final_answer": "Test answer",
            "confidence_score": 0.8,
            "retrieved_docs": [
                {
                    "product_id": "PROD-TEST123",
                    "name": "Test Product",
                    "combined_score": 0.82
                }
            ],
            "start_time": 1234567890,
            "end_time": 1234567891
        })
        yield mock


@pytest.fixture
def sample_product_data():
    return {
        "name": "Test MacBook Pro",
        "description": "A test laptop with great specs",
        "category": "Laptops",
        "price": 1999.99,
        "stock_quantity": 10,
        "specs": {
            "processor": "M3",
            "ram": "16GB",
            "storage": "512GB SSD"
        }
    }


@pytest.fixture
def sample_query_data():
    return {
        "query": "What's the best laptop for work?",
        "conversation_history": [
            {"role": "user", "content": "Hi there"},
            {"role": "assistant", "content": "Hello! How can I help you?"}
        ]
    }


@pytest.fixture
def sample_embedding():
    return [0.1] * 1536


@pytest.fixture
def sample_documents():
    return [
        {
            "id": "PROD-TEST123",
            "product_id": "PROD-TEST123",
            "name": "Test Product 1",
            "description": "Test description 1",
            "category": "Test Category",
            "price": 99.99,
            "similarity_score": 0.85,
            "combined_score": 0.82,
            "content": "Test Product 1 - Test description 1"
        },
        {
            "id": "PROD-TEST456",
            "product_id": "PROD-TEST456",
            "name": "Test Product 2",
            "description": "Test description 2",
            "category": "Test Category",
            "price": 149.99,
            "similarity_score": 0.75,
            "combined_score": 0.72,
            "content": "Test Product 2 - Test description 2"
        }
    ] 