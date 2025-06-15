# 🚀 DESPLIEGUE ULTRA-SENCILLO EN GOOGLE CLOUD RUN

**Más fácil que Azure Container Instances - TODO EN UN SCRIPT!**

## ⚡ Pasos Súper Rápidos

### 1. **Prerequisitos** (Solo una vez)
```bash
# Instalar Google Cloud CLI
curl https://sdk.cloud.google.com | bash
exec -l $SHELL  # Reiniciar terminal

# Instalar Docker (si no lo tienes)
# Mac: brew install docker
# Windows/Linux: https://docs.docker.com/get-docker/
```

### 2. **Preparar tu archivo .env**
Copia tu `.env` actual (el mismo que usas con Docker Compose) - **¡usa las mismas variables!**

### 3. **¡DESPLEGAR! (Un solo comando)**
```bash
cd rag-langgraph-azure
./deploy-gcp.sh
```

**¡Y YA!** El script hace TODO automáticamente:
- ✅ Te autentica con Google Cloud
- ✅ Habilita las APIs necesarias  
- ✅ Construye las imágenes Docker
- ✅ Las sube al registry
- ✅ Despliega backend y frontend
- ✅ Te da las URLs finales

## 🎯 ¿Qué hace cada paso?

### **Paso 1: Backend (FastAPI)**
- Crea un Dockerfile optimizado para Cloud Run
- Construye la imagen con tu código
- La despliega con todas tus variables de entorno
- Configura 2GB RAM, 2 CPUs, hasta 10 instancias

### **Paso 2: Frontend (Next.js)**  
- Conecta automáticamente con la URL del backend
- Optimiza el build para Cloud Run
- Lo despliega con 1GB RAM, 1 CPU, hasta 5 instancias

## 💰 **Ventajas vs Azure Container Instances**

| Característica | Azure Container Instances | Google Cloud Run |
|---|---|---|
| **Complejidad** | Sencillo | **MÁS SENCILLO** |
| **Pago** | Siempre corriendo | **Solo cuando hay tráfico** |
| **HTTPS** | Manual | **Automático** |
| **Escalado** | Manual | **Automático a cero** |
| **Logs** | Básicos | **Avanzados con Cloud Logging** |
| **Setup** | Portal + CLI | **Un solo script** |

## 🔧 **Configuración Avanzada** (Opcional)

Si quieres cambiar algo, edita estas variables en `deploy-gcp.sh`:
```bash
REGION="us-central1"      # Cambia la región
--memory 2Gi             # Memoria del backend  
--cpu 2                  # CPUs del backend
--max-instances 10       # Límite de escalado
```

## 🐛 **Solución de Problemas**

### Error: "gcloud not found"
```bash
curl https://sdk.cloud.google.com | bash
```

### Error: "Docker not running"  
```bash
# Mac
open -a Docker

# Linux
sudo systemctl start docker
```

### Error: "Variables de entorno faltantes"
Verifica que tu `.env` tenga:
```
AZURE_POSTGRES_HOST=...
AZURE_POSTGRES_USER=...
AZURE_POSTGRES_PASSWORD=...
AZURE_OPENAI_ENDPOINT=...
AZURE_OPENAI_API_KEY=...
```

## 🎉 **Resultado Final**

Después del despliegue obtienes:
- 🔧 **Backend URL**: `https://rag-backend-xxx-uc.a.run.app`
- 🎨 **Frontend URL**: `https://rag-frontend-xxx-uc.a.run.app`
- 💰 **Costo**: $0 cuando no hay tráfico
- 🚀 **Escalado**: Automático según demanda
- 🔒 **HTTPS**: Automático con certificados SSL

## 📱 **Usar tu aplicación**

```bash
# Probar la API
curl https://rag-backend-xxx-uc.a.run.app/health

# Query de ejemplo
curl -X POST "https://rag-backend-xxx-uc.a.run.app/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What products do you have?", "conversation_history": []}'
```

---

**¡Es realmente MÁS SENCILLO que Azure Container Instances!** 🎯 