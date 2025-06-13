import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    azure_postgres_host: str = "ragia.postgres.database.azure.com"
    azure_postgres_port: int = 5432
    azure_postgres_db: str = "ragdb"
    azure_postgres_user: str = "postgres"
    azure_postgres_password: str
    
    azure_openai_endpoint: str = "https://ragia-openai.openai.azure.com"
    azure_openai_api_key: str
    azure_openai_api_version: str = "2023-05-15"
    azure_openai_embedding_deployment: str = "text-embedding-ada-002"
    azure_openai_deployment_name: str = "gpt-4o-mini-ragia"
    
    top_k: int = 20
    rerank_top_k: int = 10
    
    @property
    def database_url(self) -> str:
        """Get async database URL with SSL"""
        return f"postgresql+asyncpg://{self.azure_postgres_user}:{self.azure_postgres_password}@{self.azure_postgres_host}:{self.azure_postgres_port}/{self.azure_postgres_db}?sslmode=require"
    
    @property
    def sync_database_url(self) -> str:
        """Get sync database URL with SSL"""
        return f"postgresql://{self.azure_postgres_user}:{self.azure_postgres_password}@{self.azure_postgres_host}:{self.azure_postgres_port}/{self.azure_postgres_db}?sslmode=require"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"


settings = Settings() 