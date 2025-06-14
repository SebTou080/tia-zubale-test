import pytest
from unittest.mock import patch, AsyncMock
from app.graph.nodes import (
    finalize_response, handle_error,
    should_retry, check_response_quality
)


@pytest.fixture
def initial_state():
    return {
        "original_query": "What laptops do you have?",
        "conversation_history": [],
        "query_plan": [],
        "retrieved_docs": [],
        "generated_answer": "",
        "final_answer": "",
        "evaluation_result": {},
        "confidence_score": 0.0,
        "processing_steps": [],
        "error_messages": [],
        "start_time": 1234567890,
        "end_time": None,
        "max_retries": 1,
        "current_retry": 0,
        "is_factual": True
    }


@pytest.mark.asyncio
async def test_finalize_response_success(initial_state):
    initial_state["generated_answer"] = "Final test answer"
    initial_state["confidence_score"] = 0.8
    
    state = await finalize_response(initial_state)
    
    assert state["final_answer"] == "Final test answer"
    assert state["end_time"] is not None
    assert "response_finalized" in state["processing_steps"]


@pytest.mark.asyncio
async def test_finalize_response_low_confidence(initial_state):
    initial_state["generated_answer"] = "Uncertain answer"
    initial_state["confidence_score"] = 0.2
    
    state = await finalize_response(initial_state)
    
    assert "⚠️ Note: This response might not be completely accurate" in state["final_answer"]
    assert "response_finalized" in state["processing_steps"]


@pytest.mark.asyncio
async def test_handle_error_retry_available(initial_state):
    initial_state["current_retry"] = 0
    initial_state["max_retries"] = 2
    
    state = await handle_error(initial_state)
    
    assert state["current_retry"] == 1
    assert "retry_attempt_1" in state["processing_steps"]


@pytest.mark.asyncio
async def test_handle_error_max_retries_reached(initial_state):
    initial_state["current_retry"] = 1
    initial_state["max_retries"] = 1
    
    state = await handle_error(initial_state)
    
    assert "Sorry, there was an error processing your query" in state["final_answer"]
    assert state["end_time"] is not None
    assert "max_retries_reached" in state["processing_steps"]


def test_should_retry_with_timeout_error(initial_state):
    initial_state["error_messages"] = ["Connection timeout occurred"]
    initial_state["current_retry"] = 0
    initial_state["max_retries"] = 1
    
    result = should_retry(initial_state)
    
    assert result == "retry"


def test_should_retry_with_connection_error(initial_state):
    initial_state["error_messages"] = ["Database connection failed"]
    initial_state["current_retry"] = 0
    initial_state["max_retries"] = 1
    
    result = should_retry(initial_state)
    
    assert result == "retry"


def test_should_retry_no_retriable_error(initial_state):
    initial_state["error_messages"] = ["Some other error"]
    
    result = should_retry(initial_state)
    
    assert result == "continue"


def test_should_retry_max_retries_exceeded(initial_state):
    initial_state["error_messages"] = ["Connection timeout occurred"]
    initial_state["current_retry"] = 1
    initial_state["max_retries"] = 1
    
    result = should_retry(initial_state)
    
    assert result == "continue"


def test_check_response_quality_high_confidence(initial_state):
    initial_state["confidence_score"] = 0.8
    
    result = check_response_quality(initial_state)
    
    assert result == "finalize"


def test_check_response_quality_low_confidence_can_retry(initial_state):
    initial_state["confidence_score"] = 0.1
    initial_state["current_retry"] = 0
    initial_state["max_retries"] = 1
    
    result = check_response_quality(initial_state)
    
    assert result == "regenerate"


def test_check_response_quality_low_confidence_max_retries(initial_state):
    initial_state["confidence_score"] = 0.1
    initial_state["current_retry"] = 1
    initial_state["max_retries"] = 1
    
    result = check_response_quality(initial_state)
    
    assert result == "finalize"


@pytest.mark.asyncio
async def test_plan_query_basic():
    from app.graph.nodes import plan_query
    
    initial_state = {
        "original_query": "What laptops do you have?",
        "conversation_history": [],
        "query_plan": [],
        "processing_steps": [],
        "error_messages": []
    }
    
    with patch("app.services.llm_service.llm_service.plan_query", new_callable=AsyncMock) as mock_plan:
        mock_plan.return_value = ["What laptops do you have?"]
        
        state = await plan_query(initial_state)
        
        assert state["query_plan"] == ["What laptops do you have?"]
        assert "query_planning_completed" in state["processing_steps"]


@pytest.mark.asyncio
async def test_execute_retrieval_basic():
    from app.graph.nodes import execute_retrieval
    
    initial_state = {
        "original_query": "What laptops do you have?",
        "retrieved_docs": [],
        "processing_steps": [],
        "error_messages": []
    }
    
    mock_docs = [{"id": "PROD-123", "name": "Test Laptop", "similarity_score": 0.8}]
    
    with patch("app.services.llm_service.llm_service.generate_embedding", new_callable=AsyncMock) as mock_embed, \
         patch("app.services.database.db_service.hybrid_search", new_callable=AsyncMock) as mock_search:
        
        mock_embed.return_value = [0.1] * 1536
        mock_search.return_value = mock_docs
        
        state = await execute_retrieval(initial_state)
        
        assert len(state["retrieved_docs"]) == 1
        assert "retrieval_completed" in state["processing_steps"]


@pytest.mark.asyncio
async def test_generate_answer_no_docs():
    from app.graph.nodes import generate_answer
    
    initial_state = {
        "original_query": "What laptops do you have?",
        "retrieved_docs": [],
        "conversation_history": [],
        "generated_answer": "",
        "processing_steps": [],
        "error_messages": []
    }
    
    state = await generate_answer(initial_state)
    
    assert "Sorry, I couldn't find relevant information" in state["generated_answer"]
    assert "answer_generation_completed" in state["processing_steps"] 