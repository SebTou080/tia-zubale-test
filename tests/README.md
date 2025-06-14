# Test Suite - Sistema RAG Multi-Agente

Este directorio contiene la suite de pruebas unitarias para el sistema RAG Multi-Agente implementado con LangGraph y FastAPI.

## 📁 Estructura de Tests

```
tests/
├── conftest.py                 # Configuración y fixtures globales
├── test_api_final.py          # Tests de endpoints de API
├── test_agents_simple.py      # Tests de agentes LangGraph
├── test_database.py           # Tests del servicio de base de datos
├── test_llm_service.py        # Tests del servicio LLM
└── pytest.ini                 # Configuración de pytest
```

## 🧪 Tipos de Tests Implementados

### 1. **Tests de API** (`test_api_final.py`)
- ✅ `test_health_endpoint()` - Verifica el endpoint de health check
- ✅ `test_ingest_product_basic()` - Prueba la ingesta básica de productos
- ✅ `test_query_basic()` - Prueba queries básicas con respuesta mock
- ✅ `test_ingest_invalid_data()` - Validación de datos inválidos
- ✅ `test_query_invalid_data()` - Validación de queries inválidas
- ✅ `test_query_empty_string()` - Manejo de strings vacíos
- ✅ `test_ingest_product_with_error()` - Manejo de errores de ingesta
- ✅ `test_query_with_conversation_history()` - Queries con historial

### 2. **Tests de Agentes** (`test_agents_simple.py`)
- ✅ `test_finalize_response_*()` - Tests del nodo de finalización
- ✅ `test_handle_error_*()` - Tests del manejo de errores
- ✅ `test_should_retry_*()` - Tests de lógica de reintento
- ✅ `test_check_response_quality_*()` - Tests de evaluación de calidad
- ✅ `test_plan_query_basic()` - Test básico de planificación de query
- ✅ `test_execute_retrieval_basic()` - Test básico de recuperación
- ✅ `test_generate_answer_no_docs()` - Generación sin documentos

### 3. **Tests de Servicio LLM** (`test_llm_service.py`)
- ✅ `test_generate_embedding_*()` - Generación de embeddings
- ✅ `test_plan_query_simple()` - Planificación de queries
- ✅ `test_contextualize_query_*()` - Contextualización de queries
- ✅ `test_generate_answer_with_memory_*()` - Generación con memoria
- ✅ `test_evaluate_answer_*()` - Evaluación de respuestas
- ✅ `test_generate_answer_formats_products_correctly()` - Formato de productos

### 4. **Tests de Base de Datos** (`test_database.py`)
- ✅ `test_store_product_*()` - Almacenamiento de productos
- ✅ `test_vector_search_*()` - Búsqueda vectorial
- ✅ `test_text_search_*()` - Búsqueda de texto
- ✅ `test_hybrid_search_*()` - Búsqueda híbrida
- ✅ `test_expand_search_terms_*()` - Expansión de términos de búsqueda

## 🚀 Cómo Ejecutar los Tests

### Ejecutar todos los tests:
```bash
python -m pytest tests/ -v
```

### Ejecutar tests específicos:
```bash
# Solo tests de API
python -m pytest tests/test_api_final.py -v

# Solo tests de agentes
python -m pytest tests/test_agents_simple.py -v

# Solo tests de servicios
python -m pytest tests/test_llm_service.py tests/test_database.py -v
```

### Ejecutar con coverage:
```bash
python -m pytest tests/ --cov=app --cov-report=html
```

### Ejecutar en modo silencioso:
```bash
python -m pytest tests/ -q
```

## 📊 Resultados de Tests

**Estado Actual**: ✅ **50/50 tests pasando (100%)**

```
tests/test_api_final.py           8 passed
tests/test_agents_simple.py      14 passed  
tests/test_llm_service.py        13 passed
tests/test_database.py           15 passed
```

## 🛠️ Dependencias de Testing

Las siguientes dependencias son necesarias para ejecutar los tests:

```txt
pytest>=7.4.0
pytest-asyncio>=0.21.0
pytest-mock>=3.11.0
httpx>=0.24.0
```

## 🎯 Cobertura de Funcionalidades

| Componente | Cobertura | Descripción |
|------------|-----------|-------------|
| **API Endpoints** | ✅ 100% | Todos los endpoints principales testeados |
| **LLM Service** | ✅ 95% | Funciones principales y manejo de errores |
| **Database Service** | ✅ 90% | CRUD, búsquedas y expansión de términos |
| **Graph Agents** | ✅ 70% | Nodos críticos y funciones de decisión |

## 🔧 Configuración de Mocks

Los tests utilizan mocks para:
- **Azure OpenAI**: Simula llamadas a embeddings y chat completions
- **PostgreSQL**: Simula conexiones y operaciones de base de datos
- **LangGraph Agent**: Simula invocaciones del agente RAG

## 📝 Notas Importantes

1. **Mocking Strategy**: Los tests usan `unittest.mock` para simular servicios externos
2. **Test Isolation**: Cada test es independiente y no afecta a otros
3. **Error Testing**: Se incluyen tests para escenarios de error y edge cases
4. **Performance**: Los tests se ejecutan rápidamente (< 1 segundo total)

## 🔄 Mantenimiento

Para mantener los tests actualizados:

1. **Nuevas funcionalidades**: Agregar tests correspondientes
2. **Cambios en API**: Actualizar tests de endpoints
3. **Nuevos agentes**: Crear tests en `test_agents_simple.py`
4. **Cambios en servicios**: Actualizar mocks y assertions

## 🚫 Limitaciones Actuales

- No se testan integraciones completas (end-to-end)
- Algunos nodos de LangGraph requieren mocking complejo
- Tests de performance no implementados
- No hay tests de carga o estrés 