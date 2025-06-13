from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import sys
from contextlib import asynccontextmanager
from app.api.router import router
from app.core.config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ]
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    logger.info("🚀 Starting RAG LangGraph application...")
    
    try:
        logger.info("✅ Application started successfully")
        yield
    except Exception as e:
        logger.error(f"❌ Error during startup: {e}")
        raise
    finally:
        logger.info("🔥 Closing application...")


app = FastAPI(
    title="RAG LangGraph Azure",
    description="Product Q&A system using LangGraph and Azure",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "path": str(request.url),
            "method": request.method
        }
    )


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "🤖 RAG LangGraph Azure - Product Q&A System",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "ingest": "POST /ingest - Ingest new product",
            "query": "POST /query - Query products",
            "health": "GET /health - Check service status"
        }
    }


app.include_router(router, prefix="", tags=["RAG API"])


if __name__ == "__main__":
    import uvicorn
    
    logger.info("🚀 Starting server in development mode...")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 