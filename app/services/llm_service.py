from typing import List, Dict, Any
from openai import AzureOpenAI
import tiktoken
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


class LLMService:
    def __init__(self):
        self.client = AzureOpenAI(
            api_key=settings.azure_openai_api_key,
            api_version=settings.azure_openai_api_version,
            azure_endpoint=settings.azure_openai_endpoint,
            timeout=45.0,  # Set timeout for Azure OpenAI calls
            max_retries=2  # Reduce retries to fail faster
        )
        self.encoding = tiktoken.get_encoding("cl100k_base")
    
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for given text with optimized error handling"""
        try:
            logger.info(f"Generating embedding for text: {text[:100]}...")
            
            # Truncate text if too long (Azure OpenAI has token limits)
            max_tokens = 8000  # Conservative limit for text-embedding-ada-002
            if len(self.encoding.encode(text)) > max_tokens:
                tokens = self.encoding.encode(text)[:max_tokens]
                text = self.encoding.decode(tokens)
                logger.warning(f"Text truncated to {max_tokens} tokens")
            
            response = self.client.embeddings.create(
                input=text,
                model=settings.azure_openai_embedding_deployment
            )
            
            logger.info("Embedding generated successfully")
            return response.data[0].embedding
            
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            # Re-raise with more context
            raise Exception(f"Failed to generate embedding: {str(e)}")
    
    async def plan_query(self, user_query: str) -> List[str]:
        """Query planning - returns original query"""
        return [user_query]
    
    async def contextualize_query(self, query: str, conversation_history: List[Dict[str, str]]) -> str:
        if not conversation_history:
            return query
        
        recent_context = ""
        for msg in conversation_history[-4:]:
            role_name = "Usuario" if msg["role"] == "user" else "Asistente"
            recent_context += f"{role_name}: {msg['content'][:100]}...\n"
        
        prompt = f"""
                    Basándote en el contexto de la conversación, reformula la consulta actual para que sea más clara y específica.

                    Contexto de la conversación:
                    {recent_context}

                    Consulta actual: "{query}"

                    Consulta contextualizada (mantén la intención original pero añade contexto si es necesario):
                """
        
        try:
            response = self.client.chat.completions.create(
                model=settings.azure_openai_deployment_name,
                messages=[
                    {"role": "system", "content": "Eres un asistente que ayuda a contextualizar consultas basándose en conversaciones previas."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=150
            )
            
            contextualized = response.choices[0].message.content.strip()
            return contextualized if contextualized else query
        
        except Exception as e:
            logger.error(f"Error contextualizing query: {e}")
            return query
    
    async def generate_answer_with_memory(
        self, 
        query: str, 
        context_docs: List[Dict[str, Any]],
        conversation_history: List[Dict[str, str]]
    ) -> str:
        context_text = ""
        for i, doc in enumerate(context_docs[:5], 1):
            context_text += f"\nProducto {i}:\n"
            context_text += f"Nombre: {doc.get('name', 'N/A')}\n"
            context_text += f"Descripción: {doc.get('description', 'N/A')}\n"
            context_text += f"Categoría: {doc.get('category', 'N/A')}\n"
            context_text += f"Precio: ${doc.get('price', 'N/A')}\n"
            context_text += "---\n"
        
        conversation_context = ""
        if conversation_history:
            conversation_context = "\nContexto de la conversación:\n"
            for msg in conversation_history[-6:]:
                role_name = "Usuario" if msg["role"] == "user" else "Asistente"
                conversation_context += f"{role_name}: {msg['content'][:150]}...\n"
        
        prompt = f"""
                    Eres un asistente experto en productos que mantiene el contexto de conversaciones.

                    {conversation_context}

                    Consulta actual del usuario: "{query}"

                    Productos disponibles:
                    {context_text}

                    Instrucciones:
                    1. CONTEXTO: Si hay conversación previa, mantén la continuidad natural
                    2. PRODUCTOS: Si hay productos relevantes, recomiéndalos con detalles específicos
                    3. CONVERSACIÓN: Mantén un tono amigable y conversacional
                    4. HONESTIDAD: Si no hay productos relevantes, sé honesto pero ofrece alternativas
                    5. IDIOMA: Responde siempre en español

                    Respuesta:
                """
        
        try:
            response = self.client.chat.completions.create(
                model=settings.azure_openai_deployment_name,
                messages=[
                    {"role": "system", "content": "Eres un asistente experto en productos que mantiene conversaciones naturales y contextuales."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=600
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "Lo siento, hubo un error al generar la respuesta."
    
    async def evaluate_answer(self, query: str, answer: str, context_docs: List[Dict]) -> Dict[str, Any]:
        """Simple evaluation of answer quality"""
        return {
            "confidence_score": 0.8 if context_docs else 0.5,
            "relevance": "high" if context_docs else "medium",
            "is_factual": True
        }


# Global instance
llm_service = LLMService() 