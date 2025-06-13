# RAG LangGraph Azure - Agentic Product Q&A System

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-green.svg)](https://fastapi.tiangolo.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.0.26+-purple.svg)](https://langchain-ai.github.io/langgraph/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-with_pgvector-blue.svg)](https://github.com/pgvector/pgvector)
[![Azure OpenAI](https://img.shields.io/badge/Azure_OpenAI-GPT--4o--mini-orange.svg)](https://azure.microsoft.com/en-us/products/cognitive-services/openai-service)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com)

## 🚀 Overview

A sophisticated **Retrieval-Augmented Generation (RAG)** system built with **LangGraph** that implements an "Agentic RAG" workflow for intelligent product queries. The system leverages Azure OpenAI, PostgreSQL with pgvector, and a multi-stage agent architecture to provide accurate, contextual responses about product information.

### ✨ Key Features

- 🧠 **Agentic RAG Workflow**: Multi-stage agent pipeline with query planning, hybrid search, and response evaluation
- 🔍 **Hybrid Search**: Combines vector similarity search (70%) with full-text search (30%) for optimal results
- 💬 **Conversational Memory**: Maintains context across conversation history for natural interactions
- 🏗️ **LangGraph Architecture**: State-driven agent workflow with error handling and retry mechanisms
- 🌐 **RESTful API**: Clean FastAPI interface with comprehensive documentation
- 🎨 **Modern Frontend**: Next.js 14 React application with real-time chat interface
- 🐳 **Containerized Deployment**: Docker Compose setup for easy deployment
- 📊 **Confidence Scoring**: Advanced evaluation system for response quality assessment

## 📋 Table of Contents

- [Overview](#-overview)
- [Architecture](#-architecture)
- [Technology Stack](#-technology-stack)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [API Reference](#-api-reference)
- [Agent Architecture](#-agent-architecture)
- [Cloud Architecture](#-cloud-architecture)
- [Database Schema](#-database-schema)
- [Development](#-development)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [Monitoring](#-monitoring)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)
- [Author](#-author)

## 🏗️ Architecture

The system implements a sophisticated **Agentic RAG** architecture using LangGraph for orchestrating a multi-stage workflow:

```mermaid
graph TD
    A[User Query] --> B[Query Planning]
    B --> C[Hybrid Search & Retrieval]
    C --> D[Response Generation]
    D --> E[Response Evaluation]
    E --> F{Quality Check}
    F -->|High Quality| G[Finalize Response]
    F -->|Low Quality| D
    G --> H[Return to User]
    
    subgraph "Hybrid Search"
        C1[Vector Search<br/>70% weight]
        C2[Full-text Search<br/>30% weight]
        C3[Score Combination]
        C1 --> C3
        C2 --> C3
    end
    
    C --> C1
    C --> C2
```

### Core Components

1. **Query Planning Agent**: Contextualizes queries based on conversation history
2. **Hybrid Search Engine**: Combines semantic and keyword-based retrieval
3. **Response Generation Agent**: Synthesizes coherent answers using Azure OpenAI
4. **Evaluation Agent**: Assesses response quality and confidence scores
5. **Error Handling**: Robust retry mechanisms and graceful error recovery

## 💻 Technology Stack

### Backend
- **Framework**: FastAPI 0.110.0 - High-performance async API framework
- **Agent Orchestration**: LangGraph 0.0.26+ - State-driven agent workflow
- **Language Models**: Azure OpenAI GPT-4o-mini-ragia - Advanced reasoning capabilities
- **Embeddings**: Azure OpenAI text-embedding-ada-002 - 1536-dimensional vectors
- **Database**: Azure PostgreSQL with pgvector - Vector similarity search
- **ORM**: SQLAlchemy 2.0+ with async support
- **Authentication**: JWT tokens (if implemented)

### Frontend
- **Framework**: Next.js 14.1.0 - React-based full-stack framework
- **Language**: TypeScript 5.3+ - Type-safe development
- **Styling**: Tailwind CSS 3.4+ - Utility-first CSS framework
- **State Management**: Zustand 4.5+ - Lightweight state management
- **HTTP Client**: Axios 1.6+ - Promise-based HTTP client
- **UI Components**: Custom components with Framer Motion animations

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **Cloud Platform**: Microsoft Azure
- **Vector Database**: PostgreSQL with pgvector extension
- **Monitoring**: Built-in health checks and logging
- **Deployment**: Production-ready container setup

## 📋 Prerequisites

Before setting up the project, ensure you have the following:

### Required Software
- **Docker**: Version 20.10+ and Docker Compose V2
- **Node.js**: Version 18+ (for frontend development)
- **Python**: Version 3.11+ (for local development)
- **Git**: For version control

### Azure Services
- **Azure OpenAI**: Service with deployed models
  - `text-embedding-ada-002` deployment for embeddings
  - `gpt-4o-mini-ragia` deployment for chat completions
- **Azure Database for PostgreSQL**: With pgvector extension enabled
- **Azure Container Registry**: (Optional) For production deployment

### Access Requirements
- Azure subscription with appropriate permissions
- Azure OpenAI API keys and endpoints
- PostgreSQL database credentials

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/username/rag-langgraph-azure.git
cd rag-langgraph-azure
```

### 2. Environment Setup

Create environment configuration from the template:

```bash
cp .env.example .env
```

### 3. Configure Environment Variables

Edit the `.env` file with your actual credentials:

```bash
# PostgreSQL Configuration
AZURE_POSTGRES_HOST=your-postgres-host.postgres.database.azure.com
AZURE_POSTGRES_PORT=5432
AZURE_POSTGRES_DB=your-database-name
AZURE_POSTGRES_USER=your-username
AZURE_POSTGRES_PASSWORD="your-secure-password"

# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-openai-resource.openai.azure.com
AZURE_OPENAI_API_KEY="your-api-key"
AZURE_OPENAI_API_VERSION=2023-05-15
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-ada-002
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o-mini-ragia

# RAG Configuration
TOP_K=10
RERANK_TOP_K=5
```

### 4. Database Setup

Execute the database setup script in your Azure PostgreSQL instance:

```sql
-- Run the contents of database_setup.sql
-- This creates the products table and necessary indexes
```

### 5. Build and Run with Docker

```bash
# Build the application
docker-compose build

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

### 6. Verify Installation

Check that all services are running:

```bash
# Backend health check
curl http://localhost:8000/health

# Frontend access
open http://localhost:3000
```

## ⚙️ Configuration

### Environment Variables Reference

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `AZURE_POSTGRES_HOST` | PostgreSQL server hostname | - | ✅ |
| `AZURE_POSTGRES_PORT` | PostgreSQL server port | 5432 | ❌ |
| `AZURE_POSTGRES_DB` | Database name | - | ✅ |
| `AZURE_POSTGRES_USER` | Database username | - | ✅ |
| `AZURE_POSTGRES_PASSWORD` | Database password | - | ✅ |
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI endpoint URL | - | ✅ |
| `AZURE_OPENAI_API_KEY` | Azure OpenAI API key | - | ✅ |
| `AZURE_OPENAI_API_VERSION` | OpenAI API version | 2023-05-15 | ❌ |
| `AZURE_OPENAI_EMBEDDING_DEPLOYMENT` | Embedding model deployment name | text-embedding-ada-002 | ❌ |
| `AZURE_OPENAI_DEPLOYMENT_NAME` | Chat model deployment name | gpt-4o-mini-ragia | ❌ |
| `TOP_K` | Number of documents to retrieve | 10 | ❌ |
| `RERANK_TOP_K` | Number of documents after reranking | 5 | ❌ |

### RAG Configuration Options

The system can be fine-tuned through various parameters:

- **Retrieval Settings**: Adjust `TOP_K` and `RERANK_TOP_K` for different result sets
- **Search Weights**: Modify vector (70%) vs text search (30%) weights in the code
- **Confidence Thresholds**: Adjust quality gates in the evaluation node
- **Temperature Settings**: Control response creativity in LLM calls

## 🎯 Usage

### Quick Start Example

1. **Ingest a Product**:
```bash
curl -X POST "http://localhost:8000/ingest" \
-H "Content-Type: application/json" \
-d '{
  "name": "MacBook Pro M3",
  "description": "14-inch laptop with M3 chip, 16GB RAM, 512GB SSD",
  "category": "Laptops",
  "price": 1999.99,
  "stock_quantity": 10,
  "specs": {
    "processor": "M3",
    "ram": "16GB",
    "storage": "512GB SSD",
    "display": "14-inch Liquid Retina XDR"
  }
}'
```

2. **Query Products**:
```bash
curl -X POST "http://localhost:8000/query" \
-H "Content-Type: application/json" \
-d '{
  "query": "What laptops do you have under $2000?",
  "conversation_history": []
}'
```

### Web Interface

Access the web interface at `http://localhost:3000` for an interactive chat experience with:
- Real-time product queries
- Conversation history
- Source document references
- Confidence score indicators

### Conversational Examples

The system maintains context across conversations:

```json
{
  "query": "Tell me about gaming laptops",
  "conversation_history": [
    {"role": "user", "content": "I'm looking for a powerful laptop"},
    {"role": "assistant", "content": "I can help you find a powerful laptop..."}
  ]
}
```

## 📚 API Reference

### Health Check
```http
GET /health
```
Returns system health status and version information.

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0"
}
```

### Ingest Product
```http
POST /ingest
```
Ingests a new product into the database with automatic embedding generation.

**Request Body**:
```json
{
  "name": "string",
  "description": "string",
  "category": "string",
  "price": 0.0,
  "stock_quantity": 0,
  "specs": {},
  "metadata": {}
}
```

**Response**:
```json
{
  "product_id": "PROD-12345678",
  "message": "Product ingested successfully",
  "status": "success"
}
```

### Query Products
```http
POST /query
```
Performs intelligent product search using the agentic RAG workflow.

**Request Body**:
```json
{
  "query": "string",
  "conversation_history": [
    {
      "role": "user|assistant",
      "content": "string"
    }
  ]
}
```

**Response**:
```json
{
  "query": "string",
  "answer": "string",
  "sources": [
    {
      "product_id": "string",
      "product_name": "string",
      "relevance_score": 0.0,
      "content_snippet": "string"
    }
  ],
  "confidence_score": 0.0,
  "processing_time_ms": 0,
  "conversation_history": []
}
```

### Error Responses

All endpoints return structured error responses:

```json
{
  "detail": "Error description",
  "path": "/api/endpoint",
  "method": "POST"
}
```

## 🤖 Agent Architecture

The system implements a sophisticated multi-agent architecture using LangGraph:

### Agent Workflow

```mermaid
stateDiagram-v2
    [*] --> QueryPlanning
    QueryPlanning --> HybridSearch
    HybridSearch --> ResponseGeneration
    ResponseGeneration --> ResponseEvaluation
    ResponseEvaluation --> QualityCheck
    QualityCheck --> ResponseGeneration : Low Quality
    QualityCheck --> Finalization : High Quality
    Finalization --> [*]
    
    note right of QualityCheck
        Confidence < 0.2
        triggers regeneration
    end note
```

### Agent State Management

Each agent maintains a comprehensive state object:

```python
class AgentState(TypedDict):
    original_query: str                    # User's original query
    conversation_history: List[Dict]       # Previous conversation context
    query_plan: List[str]                 # Decomposed query components
    retrieved_docs: List[Dict]            # Retrieved product documents
    generated_answer: str                 # LLM-generated response
    final_answer: str                     # Final processed answer
    evaluation_result: Dict               # Quality evaluation metrics
    confidence_score: float               # Response confidence (0-1)
    processing_steps: List[str]           # Execution trace
    error_messages: List[str]             # Error tracking
    start_time: float                     # Processing start timestamp
    end_time: Optional[float]             # Processing end timestamp
    max_retries: int                      # Maximum retry attempts
    current_retry: int                    # Current retry count
```

### Agent Nodes

1. **Query Planning Node** (`plan_query`):
   - Contextualizes queries using conversation history
   - Fallback to original query for robustness
   - Handles multilingual queries

2. **Hybrid Search Node** (`execute_retrieval`):
   - Vector similarity search using embeddings
   - Full-text search with PostgreSQL FTS
   - Intelligent score combination and boosting

3. **Response Generation Node** (`generate_answer`):
   - Context-aware response synthesis
   - Conversation memory integration
   - Multilingual response generation

4. **Evaluation Node** (`evaluate_answer`):
   - Response quality assessment
   - Confidence score calculation
   - Factual accuracy validation

5. **Finalization Node** (`finalize_response`):
   - Final response preparation
   - Low-confidence disclaimers
   - Processing time calculation

### Error Handling & Retry Logic

The system implements sophisticated error handling:

- **Automatic Retries**: Connection and timeout errors trigger retries
- **Graceful Degradation**: Partial failures don't crash the entire workflow
- **Error Context**: Detailed error tracking for debugging
- **Quality Gates**: Low-quality responses trigger regeneration


## 🔧 Troubleshooting

### Common Issues and Solutions

#### Database Connection Errors

**Problem**: `Connection to PostgreSQL failed`
**Solutions**:
1. Verify database credentials in `.env`
2. Check network connectivity to Azure PostgreSQL
3. Ensure PostgreSQL allows connections from your IP
4. Verify SSL configuration (`sslmode=require`)

```bash
# Test connection manually
psql "postgresql://user:password@host:5432/db?sslmode=require"
```

#### Azure OpenAI API Errors

**Problem**: `OpenAI API call failed`
**Solutions**:
1. Verify API key and endpoint in `.env`
2. Check deployment names match Azure configuration
3. Monitor quota usage in Azure portal
4. Verify API version compatibility

```bash
# Test API access
curl -X POST "https://your-endpoint.openai.azure.com/openai/deployments/your-deployment/chat/completions?api-version=2023-05-15" \
-H "api-key: your-api-key" \
-H "Content-Type: application/json" \
-d '{"messages":[{"role":"user","content":"test"}]}'
````


### Support Resources

- **Azure OpenAI Documentation**: https://docs.microsoft.com/azure/cognitive-services/openai/
- **LangGraph Documentation**: https://langchain-ai.github.io/langgraph/
- **PostgreSQL pgvector**: https://github.com/pgvector/pgvector
- **FastAPI Documentation**: https://fastapi.tiangolo.com/



## 👨‍💻 Author

**Sebastian Toulier Funes**
- AI Engineer with expertise in systems and cloud architecture
- Specialized in RAG systems, LangGraph agent workflows, and Azure cloud solutions
- Email: [sebaas14toulier@gmail.com](sebaas14toulier@gmail.com)
- LinkedIn: [https://www.linkedin.com/in/sebtou08/](https://www.linkedin.com/in/sebtou08/)

### Project Background

This RAG LangGraph Azure system was developed as a demonstration of modern AI-powered product search capabilities, showcasing:

- **Advanced RAG Architecture**: Multi-agent workflow design
- **Production-Ready Code**: Scalable, maintainable, and well-documented
- **Cloud Integration**: Full Azure ecosystem utilization
- **Modern Tech Stack**: Latest frameworks and best practices

---
# tia-zubale-test
