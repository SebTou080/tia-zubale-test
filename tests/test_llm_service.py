import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from app.services.llm_service import LLMService


@pytest.fixture
def llm_service():
    return LLMService()


@pytest.fixture
def mock_openai_client():
    mock_client = MagicMock()
    
    mock_embedding_response = MagicMock()
    mock_embedding_response.data = [MagicMock()]
    mock_embedding_response.data[0].embedding = [0.1] * 1536
    mock_client.embeddings.create.return_value = mock_embedding_response
    
    mock_chat_response = MagicMock()
    mock_chat_response.choices = [MagicMock()]
    mock_chat_response.choices[0].message.content = "Test response"
    mock_client.chat.completions.create.return_value = mock_chat_response
    
    return mock_client


@pytest.mark.asyncio
async def test_generate_embedding_success(llm_service, mock_openai_client):
    with patch.object(llm_service, 'client', mock_openai_client):
        result = await llm_service.generate_embedding("test text")
        
        assert isinstance(result, list)
        assert len(result) == 1536
        assert all(isinstance(x, float) for x in result)
        mock_openai_client.embeddings.create.assert_called_once()


@pytest.mark.asyncio
async def test_generate_embedding_error(llm_service, mock_openai_client):
    mock_openai_client.embeddings.create.side_effect = Exception("API Error")
    
    with patch.object(llm_service, 'client', mock_openai_client):
        with pytest.raises(Exception):
            await llm_service.generate_embedding("test text")


@pytest.mark.asyncio
async def test_plan_query_simple(llm_service):
    query = "What laptops do you have?"
    result = await llm_service.plan_query(query)
    
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0] == query


@pytest.mark.asyncio
async def test_contextualize_query_no_history(llm_service):
    query = "Show me laptops"
    result = await llm_service.contextualize_query(query, [])
    
    assert result == query


@pytest.mark.asyncio
async def test_contextualize_query_with_history(llm_service, mock_openai_client):
    query = "Tell me more about that one"
    conversation_history = [
        {"role": "user", "content": "Show me MacBooks"},
        {"role": "assistant", "content": "Here are some MacBook options..."}
    ]
    
    with patch.object(llm_service, 'client', mock_openai_client):
        result = await llm_service.contextualize_query(query, conversation_history)
        
        assert isinstance(result, str)
        mock_openai_client.chat.completions.create.assert_called_once()


@pytest.mark.asyncio
async def test_contextualize_query_with_error(llm_service, mock_openai_client):
    query = "Tell me more"
    conversation_history = [{"role": "user", "content": "Hello"}]
    
    mock_openai_client.chat.completions.create.side_effect = Exception("API Error")
    
    with patch.object(llm_service, 'client', mock_openai_client):
        result = await llm_service.contextualize_query(query, conversation_history)
        
        assert result == query


@pytest.mark.asyncio
async def test_generate_answer_with_memory_success(llm_service, mock_openai_client, sample_documents):
    query = "What laptops do you recommend?"
    conversation_history = [
        {"role": "user", "content": "I need a laptop for work"},
        {"role": "assistant", "content": "What type of work?"}
    ]
    
    with patch.object(llm_service, 'client', mock_openai_client):
        result = await llm_service.generate_answer_with_memory(query, sample_documents, conversation_history)
        
        assert isinstance(result, str)
        assert len(result) > 0
        mock_openai_client.chat.completions.create.assert_called_once()


@pytest.mark.asyncio
async def test_generate_answer_with_memory_no_docs(llm_service, mock_openai_client):
    query = "What products do you have?"
    
    with patch.object(llm_service, 'client', mock_openai_client):
        result = await llm_service.generate_answer_with_memory(query, [], [])
        
        assert isinstance(result, str)
        assert len(result) > 0
        mock_openai_client.chat.completions.create.assert_called_once()


@pytest.mark.asyncio
async def test_generate_answer_with_memory_error(llm_service, mock_openai_client, sample_documents):
    query = "What laptops do you have?"
    mock_openai_client.chat.completions.create.side_effect = Exception("API Error")
    
    with patch.object(llm_service, 'client', mock_openai_client):
        result = await llm_service.generate_answer_with_memory(query, sample_documents, [])
        
        assert result == "Lo siento, hubo un error al generar la respuesta."


@pytest.mark.asyncio
async def test_evaluate_answer_with_docs(llm_service, sample_documents):
    query = "What's the best laptop?"
    answer = "The MacBook Pro is excellent for professional work"
    
    result = await llm_service.evaluate_answer(query, answer, sample_documents)
    
    assert isinstance(result, dict)
    assert "confidence_score" in result
    assert "relevance" in result
    assert "is_factual" in result
    assert result["confidence_score"] == 0.8
    assert result["is_factual"] is True


@pytest.mark.asyncio
async def test_evaluate_answer_no_docs(llm_service):
    query = "What's the best laptop?"
    answer = "I don't have enough information"
    
    result = await llm_service.evaluate_answer(query, answer, [])
    
    assert isinstance(result, dict)
    assert result["confidence_score"] == 0.5
    assert result["relevance"] == "medium"
    assert result["is_factual"] is True


@pytest.mark.asyncio
async def test_generate_answer_formats_products_correctly(llm_service, mock_openai_client):
    query = "Show me products"
    context_docs = [
        {
            "name": "MacBook Pro",
            "description": "Powerful laptop",
            "category": "Laptops",
            "price": 1999.99
        },
        {
            "name": "iPhone 15",
            "description": "Latest smartphone",
            "category": "Phones",
            "price": 999.99
        }
    ]
    
    with patch.object(llm_service, 'client', mock_openai_client):
        await llm_service.generate_answer_with_memory(query, context_docs, [])
        
        call_args = mock_openai_client.chat.completions.create.call_args
        prompt = call_args[1]["messages"][1]["content"]
        
        assert "Producto 1:" in prompt
        assert "MacBook Pro" in prompt
        assert "Producto 2:" in prompt
        assert "iPhone 15" in prompt
        assert "$1999.99" in prompt


@pytest.mark.asyncio
async def test_contextualize_query_limits_history(llm_service, mock_openai_client):
    query = "What about pricing?"
    long_history = [
        {"role": "user", "content": f"Message {i}"}
        for i in range(10)
    ]
    
    with patch.object(llm_service, 'client', mock_openai_client):
        await llm_service.contextualize_query(query, long_history)
        
        call_args = mock_openai_client.chat.completions.create.call_args
        prompt = call_args[1]["messages"][1]["content"]
        
        assert "Message 6" in prompt  
        assert "Message 5" not in prompt 