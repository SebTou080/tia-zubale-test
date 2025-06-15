#!/bin/bash
# 🚀 DESPLIEGUE A GOOGLE CLOUD RUN
# Script optimizado y limpio

set -e

echo "🚀 Despliegue a Google Cloud Run"

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# ===== CONFIGURACIÓN =====
REGION="us-central1"
PROJECT_ID=$(gcloud config get-value project 2>/dev/null || echo "")

# Si no hay proyecto configurado, pedirlo
if [ -z "$PROJECT_ID" ]; then
    echo -e "${YELLOW}🔧 Configura tu proyecto de GCP:${NC}"
    read -p "Ingresa tu PROJECT_ID: " PROJECT_ID
    gcloud config set project $PROJECT_ID
fi

echo -e "${BLUE}📦 Proyecto: $PROJECT_ID${NC}"
echo -e "${BLUE}🌍 Región: $REGION${NC}"

# ===== AUTENTICACIÓN =====
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo -e "${YELLOW}🔐 Autenticándote...${NC}"
    gcloud auth login
fi

# ===== HABILITAR APIS =====
echo -e "${YELLOW}🔧 Habilitando APIs...${NC}"
gcloud services enable cloudbuild.googleapis.com run.googleapis.com containerregistry.googleapis.com

# ===== CARGAR VARIABLES DE ENTORNO =====
echo -e "${BLUE}📋 Cargando variables...${NC}"
if [ -f ".env" ]; then
    set -a; source .env; set +a
    echo -e "${GREEN}✅ Variables cargadas desde .env${NC}"
else
    echo -e "${YELLOW}⚠️  No hay .env, usando variables del sistema${NC}"
fi

# ===== VERIFICAR VARIABLES CRÍTICAS =====
required_vars=("AZURE_POSTGRES_HOST" "AZURE_POSTGRES_USER" "AZURE_POSTGRES_PASSWORD" "AZURE_OPENAI_ENDPOINT" "AZURE_OPENAI_API_KEY")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo -e "${RED}❌ Falta variable: $var${NC}"; exit 1
    fi
done
echo -e "${GREEN}✅ Variables verificadas${NC}"

# ===== 1. DESPLEGAR BACKEND =====
echo -e "${BLUE}🏗️  PASO 1: Desplegando Backend...${NC}"

# Build y deploy del backend
docker build --platform linux/amd64 -t gcr.io/$PROJECT_ID/rag-backend .
docker push gcr.io/$PROJECT_ID/rag-backend

gcloud run deploy rag-backend \
    --image gcr.io/$PROJECT_ID/rag-backend \
    --region $REGION \
    --allow-unauthenticated \
    --port 8080 \
    --memory 2Gi \
    --cpu 2 \
    --max-instances 3 \
    --set-env-vars "AZURE_POSTGRES_HOST=$AZURE_POSTGRES_HOST,AZURE_POSTGRES_PORT=${AZURE_POSTGRES_PORT:-5432},AZURE_POSTGRES_DB=${AZURE_POSTGRES_DB:-postgres},AZURE_POSTGRES_USER=$AZURE_POSTGRES_USER,AZURE_POSTGRES_PASSWORD=$AZURE_POSTGRES_PASSWORD,AZURE_OPENAI_ENDPOINT=$AZURE_OPENAI_ENDPOINT,AZURE_OPENAI_API_KEY=$AZURE_OPENAI_API_KEY,AZURE_OPENAI_API_VERSION=${AZURE_OPENAI_API_VERSION:-2023-12-01-preview},AZURE_OPENAI_EMBEDDING_DEPLOYMENT=${AZURE_OPENAI_EMBEDDING_DEPLOYMENT:-text-embedding-ada-002},AZURE_OPENAI_DEPLOYMENT_NAME=${AZURE_OPENAI_DEPLOYMENT_NAME:-gpt-4o-mini-ragia},TOP_K=${TOP_K:-10},RERANK_TOP_K=${RERANK_TOP_K:-5}"

BACKEND_URL=$(gcloud run services describe rag-backend --region=$REGION --format="value(status.url)")
echo -e "${GREEN}✅ Backend: $BACKEND_URL${NC}"

# ===== 2. DESPLEGAR FRONTEND =====
echo -e "${BLUE}🎨 PASO 2: Desplegando Frontend...${NC}"

# Build y deploy del frontend con la URL del backend
cd frontend
docker build --platform linux/amd64 --build-arg NEXT_PUBLIC_API_URL=$BACKEND_URL -t gcr.io/$PROJECT_ID/rag-frontend .
docker push gcr.io/$PROJECT_ID/rag-frontend

gcloud run deploy rag-frontend \
    --image gcr.io/$PROJECT_ID/rag-frontend \
    --region $REGION \
    --allow-unauthenticated \
    --port 8080 \
    --memory 1Gi \
    --cpu 1 \
    --max-instances 2 \
    --set-env-vars "NODE_ENV=production"

cd ..

FRONTEND_URL=$(gcloud run services describe rag-frontend --region=$REGION --format="value(status.url)")

# ===== RESULTADO FINAL =====
echo ""
echo -e "${GREEN}🎉 ¡DESPLIEGUE COMPLETADO!${NC}"
echo ""
echo -e "${BLUE}📱 TUS URLs:${NC}"
echo -e "   🔧 Backend:  $BACKEND_URL"
echo -e "   🎨 Frontend: $FRONTEND_URL"
echo ""
echo -e "${YELLOW}💡 Prueba:${NC}"
echo "   curl $BACKEND_URL/health"
echo ""
echo -e "${GREEN}✨ ¡Listo! 🚀${NC}" 