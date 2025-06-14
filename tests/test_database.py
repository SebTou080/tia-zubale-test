import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.database import DatabaseService


@pytest.fixture
def db_service():
    return DatabaseService()


@pytest.fixture
def mock_connection():
    mock_conn = AsyncMock()
    return mock_conn


@pytest.mark.asyncio
async def test_store_product_success(db_service, mock_connection, sample_product_data, sample_embedding):
    mock_connection.fetchval.return_value = "PROD-TEST123"
    
    with patch.object(db_service, 'get_connection', return_value=mock_connection):
        result = await db_service.store_product(
            name=sample_product_data["name"],
            description=sample_product_data["description"],
            category=sample_product_data["category"],
            price=sample_product_data["price"],
            stock_quantity=sample_product_data["stock_quantity"],
            specs=sample_product_data["specs"],
            embedding=sample_embedding
        )
        
        assert result == "PROD-TEST123"
        mock_connection.fetchval.assert_called_once()
        mock_connection.close.assert_called_once()


@pytest.mark.asyncio
async def test_store_product_minimal_data(db_service, mock_connection, sample_embedding):
    mock_connection.fetchval.return_value = "PROD-TEST456"
    
    with patch.object(db_service, 'get_connection', return_value=mock_connection):
        result = await db_service.store_product(
            name="Test Product",
            embedding=sample_embedding
        )
        
        assert result == "PROD-TEST456"
        mock_connection.fetchval.assert_called_once()


@pytest.mark.asyncio
async def test_vector_search_success(db_service, mock_connection, sample_embedding):
    mock_rows = [
        {
            "product_id": "PROD-TEST123",
            "name": "Test Product 1",
            "description": "Test description 1",
            "category": "Test Category",
            "price": 99.99,
            "stock_quantity": 10,
            "specs": {"key": "value"},
            "similarity_score": 0.85
        },
        {
            "product_id": "PROD-TEST456",
            "name": "Test Product 2",
            "description": "Test description 2",
            "category": "Test Category",
            "price": 149.99,
            "stock_quantity": 5,
            "specs": {"key": "value2"},
            "similarity_score": 0.75
        }
    ]
    mock_connection.fetch.return_value = mock_rows
    
    with patch.object(db_service, 'get_connection', return_value=mock_connection):
        results = await db_service.vector_search(sample_embedding, top_k=5)
        
        assert len(results) == 2
        assert results[0]["product_id"] == "PROD-TEST123"
        assert results[0]["similarity_score"] == 0.85
        assert results[1]["product_id"] == "PROD-TEST456"
        assert results[1]["similarity_score"] == 0.75
        mock_connection.fetch.assert_called_once()
        mock_connection.close.assert_called_once()


@pytest.mark.asyncio
async def test_text_search_success(db_service, mock_connection):
    mock_rows = [
        {
            "product_id": "PROD-TEST123",
            "name": "MacBook Pro",
            "description": "Powerful laptop for professionals",
            "category": "Laptops",
            "price": 1999.99,
            "stock_quantity": 5,
            "specs": {"processor": "M3"},
            "rank_score": 0.8
        }
    ]
    mock_connection.fetch.return_value = mock_rows
    
    with patch.object(db_service, 'get_connection', return_value=mock_connection):
        results = await db_service.text_search("laptop", top_k=5)
        
        assert len(results) == 1
        assert results[0]["product_id"] == "PROD-TEST123"
        assert results[0]["name"] == "MacBook Pro"
        assert results[0]["rank_score"] == 0.8
        mock_connection.fetch.assert_called_once()


@pytest.mark.asyncio
async def test_hybrid_search_success(db_service, sample_embedding):
    vector_results = [
        {
            "id": "PROD-TEST123",
            "product_id": "PROD-TEST123",
            "name": "Test Product 1",
            "description": "Test description",
            "similarity_score": 0.9,
            "content": "Test Product 1 - Test description"
        }
    ]
    
    text_results = [
        {
            "id": "PROD-TEST123",
            "product_id": "PROD-TEST123", 
            "name": "Test Product 1",
            "description": "Test description",
            "rank_score": 0.7,
            "content": "Test Product 1 - Test description"
        }
    ]
    
    with patch.object(db_service, 'vector_search', return_value=vector_results), \
         patch.object(db_service, 'text_search', return_value=text_results):
        
        results = await db_service.hybrid_search(sample_embedding, "test query", top_k=5)
        
        assert len(results) >= 1
        assert results[0]["product_id"] == "PROD-TEST123"
        assert "combined_score" in results[0]


def test_expand_search_terms_laptop(db_service):
    result = db_service._expand_search_terms("laptop gaming")
    
    assert "laptop" in result
    assert "portatil" in result
    assert "computadora" in result
    assert "notebook" in result
    assert "macbook" in result


def test_expand_search_terms_smartphone(db_service):
    result = db_service._expand_search_terms("smartphone nuevo")
    
    assert "smartphone" in result
    assert "telefono" in result
    assert "celular" in result
    assert "iphone" in result


def test_expand_search_terms_daily_use(db_service):
    result = db_service._expand_search_terms("uso dia a dia")
    
    assert "diario" in result
    assert "cotidiano" in result
    assert "personal" in result


def test_expand_search_terms_no_match(db_service):
    original_query = "random product query"
    result = db_service._expand_search_terms(original_query)
    
    assert original_query in result


@pytest.mark.asyncio
async def test_vector_search_empty_results(db_service, mock_connection, sample_embedding):
    mock_connection.fetch.return_value = []
    
    with patch.object(db_service, 'get_connection', return_value=mock_connection):
        results = await db_service.vector_search(sample_embedding, top_k=5)
        
        assert results == []


@pytest.mark.asyncio
async def test_text_search_empty_results(db_service, mock_connection):
    mock_connection.fetch.return_value = []
    
    with patch.object(db_service, 'get_connection', return_value=mock_connection):
        results = await db_service.text_search("nonexistent", top_k=5)
        
        assert results == []


@pytest.mark.asyncio
async def test_hybrid_search_empty_results(db_service, sample_embedding):
    with patch.object(db_service, 'vector_search', return_value=[]), \
         patch.object(db_service, 'text_search', return_value=[]):
        
        results = await db_service.hybrid_search(sample_embedding, "test query", top_k=5)
        
        assert results == []


@pytest.mark.asyncio
async def test_store_product_connection_error(db_service, sample_embedding):
    with patch.object(db_service, 'get_connection', side_effect=Exception("Connection failed")):
        with pytest.raises(Exception):
            await db_service.store_product("Test Product", embedding=sample_embedding)


@pytest.mark.asyncio
async def test_vector_search_connection_error(db_service, sample_embedding):
    with patch.object(db_service, 'get_connection', side_effect=Exception("Connection failed")):
        with pytest.raises(Exception):
            await db_service.vector_search(sample_embedding, top_k=5)


@pytest.mark.asyncio
async def test_hybrid_search_combines_scores_correctly(db_service, sample_embedding):
    vector_results = [
        {
            "id": "PROD-TEST123",
            "product_id": "PROD-TEST123",
            "name": "Test Product",
            "similarity_score": 0.8,
            "content": "Test content"
        }
    ]
    
    text_results = [
        {
            "id": "PROD-TEST123", 
            "product_id": "PROD-TEST123",
            "name": "Test Product",
            "rank_score": 0.6,
            "content": "Test content"
        }
    ]
    
    with patch.object(db_service, 'vector_search', return_value=vector_results), \
         patch.object(db_service, 'text_search', return_value=text_results):
        
        results = await db_service.hybrid_search(sample_embedding, "test", top_k=5)
        
        assert len(results) == 1
        combined_score = results[0]["combined_score"]
        
        assert combined_score > 0
        assert isinstance(combined_score, float) 