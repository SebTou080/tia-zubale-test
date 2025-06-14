import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock


def test_health_endpoint():
    from app.main import app
    client = TestClient(app)
    
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert data["version"] == "1.0.0"


def test_ingest_product_basic():
    from app.main import app
    
    with patch("app.services.llm_service.llm_service.generate_embedding", new_callable=AsyncMock) as mock_embed, \
         patch("app.services.database.db_service.store_product", new_callable=AsyncMock) as mock_store:
        
        mock_embed.return_value = [0.1] * 1536
        mock_store.return_value = "PROD-TEST123"
        
        client = TestClient(app)
        product_data = {"name": "Test Product", "description": "Test description"}
        response = client.post("/ingest", json=product_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["product_id"] == "PROD-TEST123"


def test_query_basic():
    from app.main import app
    
    mock_result = {
        "original_query": "test query",
        "final_answer": "Test answer",
        "confidence_score": 0.8,
        "retrieved_docs": [],
        "start_time": 1234567890,
        "end_time": 1234567891
    }
    
    with patch("app.graph.builder.rag_agent.ainvoke", new_callable=AsyncMock) as mock_agent:
        mock_agent.return_value = mock_result
        
        client = TestClient(app)
        query_data = {"query": "What products do you have?"}
        response = client.post("/query", json=query_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["query"] == query_data["query"]
        assert data["answer"] == "Test answer"
        assert data["confidence_score"] == 0.8


def test_ingest_invalid_data():
    from app.main import app
    client = TestClient(app)
    
    response = client.post("/ingest", json={})
    assert response.status_code == 422


def test_query_invalid_data():
    from app.main import app
    client = TestClient(app)
    
    response = client.post("/query", json={})
    assert response.status_code == 422


def test_query_empty_string():
    from app.main import app
    client = TestClient(app)
    
    response = client.post("/query", json={"query": ""})
    assert response.status_code == 422


def test_ingest_product_with_error():
    from app.main import app
    
    with patch("app.services.llm_service.llm_service.generate_embedding", new_callable=AsyncMock) as mock_embed:
        mock_embed.side_effect = Exception("LLM Error")
        
        client = TestClient(app)
        product_data = {"name": "Test Product"}
        response = client.post("/ingest", json=product_data)
        
        assert response.status_code == 500
        data = response.json()
        assert "Error ingesting product" in data["detail"]


def test_query_with_conversation_history():
    from app.main import app
    
    mock_result = {
        "original_query": "tell me more",
        "final_answer": "Here's more information",
        "confidence_score": 0.7,
        "retrieved_docs": [],
        "start_time": 1234567890,
        "end_time": 1234567891
    }
    
    with patch("app.graph.builder.rag_agent.ainvoke", new_callable=AsyncMock) as mock_agent:
        mock_agent.return_value = mock_result
        
        client = TestClient(app)
        query_data = {
            "query": "Tell me more about that",
            "conversation_history": [
                {"role": "user", "content": "Show me laptops"},
                {"role": "assistant", "content": "Here are some laptops"}
            ]
        }
        response = client.post("/query", json=query_data)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["conversation_history"]) == 4  # 2 original + 2 new
        assert data["answer"] == "Here's more information" 