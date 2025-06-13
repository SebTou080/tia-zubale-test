import time
import logging
import time
from typing import Dict, Any
from app.graph.state import AgentState
from app.services.llm_service import llm_service
from app.services.database import db_service
from app.core.config import settings

logger = logging.getLogger(__name__)


async def plan_query(state: AgentState) -> AgentState:
    """Query Planning node - decompose complex user query into simpler sub-queries"""
    logger.info("Starting query planning")
    
    try:
        query = state["original_query"]
        conversation_history = state.get("conversation_history", [])
        
        if conversation_history:
            context_aware_query = await llm_service.contextualize_query(query, conversation_history)
            sub_queries = await llm_service.plan_query(context_aware_query)
        else:
            sub_queries = await llm_service.plan_query(query)
        
        state["query_plan"] = sub_queries
        state["processing_steps"].append("query_planning_completed")
        
        logger.info(f"Query plan generated: {len(sub_queries)} sub-queries")
        
    except Exception as e:
        error_msg = f"Error in query planning: {str(e)}"
        logger.error(error_msg)
        state["error_messages"].append(error_msg)
        state["query_plan"] = [state["original_query"]]
    
    return state


async def execute_retrieval(state: AgentState) -> AgentState:
    """Hybrid Search & Retrieval node - execute hybrid search"""
    logger.info("Starting search and retrieval")
    
    try:
        original_query = state["original_query"]
        
        # Generate embedding for the query
        query_embedding = await llm_service.generate_embedding(original_query)
        
        # Perform hybrid search
        retrieved_docs = await db_service.hybrid_search(
            query_embedding=query_embedding,
            query_text=original_query,
            top_k=settings.rerank_top_k
        )
        
        state["retrieved_docs"] = retrieved_docs
        state["processing_steps"].append("retrieval_completed")
        
        logger.info(f"Retrieved {len(retrieved_docs)} documents")
        
    except Exception as e:
        error_msg = f"Error in retrieval: {str(e)}"
        logger.error(error_msg)
        state["error_messages"].append(error_msg)
        state["retrieved_docs"] = []
    
    return state


async def generate_answer(state: AgentState) -> AgentState:
    """Response Generation node - synthesize coherent answer based on retrieved documents"""
    logger.info("Starting answer generation")
    
    try:
        original_query = state["original_query"]
        context_docs = state["retrieved_docs"]
        conversation_history = state.get("conversation_history", [])
        
        if not context_docs:
            generated_answer = "Sorry, I couldn't find relevant information to answer your query. Please try rephrasing your question or be more specific."
        else:
            generated_answer = await llm_service.generate_answer_with_memory(
                query=original_query,
                context_docs=context_docs,
                conversation_history=conversation_history
            )
        
        state["generated_answer"] = generated_answer
        state["processing_steps"].append("answer_generation_completed")
        
        logger.info("Answer generated successfully")
        
    except Exception as e:
        error_msg = f"Error generating answer: {str(e)}"
        logger.error(error_msg)
        state["error_messages"].append(error_msg)
        state["generated_answer"] = "Sorry, there was an error generating the answer."
    
    return state


async def evaluate_answer(state: AgentState) -> AgentState:
    """Response Evaluation node - evaluate generated answer"""
    logger.info("Starting answer evaluation")
    
    try:
        original_query = state["original_query"]
        generated_answer = state["generated_answer"]
        context_docs = state["retrieved_docs"]
        
        evaluation = await llm_service.evaluate_answer(
            query=original_query,
            answer=generated_answer,
            context_docs=context_docs
        )
        
        state["evaluation_result"] = evaluation
        state["is_factual"] = evaluation.get("is_factual", True)
        state["confidence_score"] = evaluation.get("confidence_score", 0.5)
        state["processing_steps"].append("evaluation_completed")
        
        logger.info(f"Evaluation completed: confidence={state['confidence_score']}")
        
    except Exception as e:
        error_msg = f"Error in evaluation: {str(e)}"
        logger.error(error_msg)
        state["error_messages"].append(error_msg)
        state["evaluation_result"] = {"is_factual": True, "confidence_score": 0.5}
        state["is_factual"] = True
        state["confidence_score"] = 0.5
    
    return state


async def finalize_response(state: AgentState) -> AgentState:
    """Finalization node - prepare final response and complete processing"""
    logger.info("Finalizing response")
    
    try:
        state["final_answer"] = state["generated_answer"]
        
        if state["confidence_score"] < 0.3:
            disclaimer = "\n\n⚠️ Note: This response might not be completely accurate. We recommend verifying the information."
            state["final_answer"] += disclaimer
        
        state["end_time"] = time.time()
        state["processing_steps"].append("response_finalized")
        
        logger.info("Response finalized successfully")
        
    except Exception as e:
        error_msg = f"Error finalizing response: {str(e)}"
        logger.error(error_msg)
        state["error_messages"].append(error_msg)
        state["final_answer"] = state.get("generated_answer", "Error processing query.")
        state["end_time"] = time.time()
    
    return state


async def handle_error(state: AgentState) -> AgentState:
    """Error handling node - handle errors and decide whether to retry or fail"""
    logger.info("Handling process errors")
    
    current_retry = state.get("current_retry", 0)
    max_retries = state.get("max_retries", 1)
    
    if current_retry < max_retries:
        logger.info(f"Retrying process (attempt {current_retry + 1}/{max_retries})")
        state["current_retry"] = current_retry + 1
        state["processing_steps"].append(f"retry_attempt_{current_retry + 1}")
        return state
    else:
        logger.error("Maximum retry attempts reached")
        state["final_answer"] = "Sorry, there was an error processing your query. Please try again later."
        state["end_time"] = time.time()
        state["processing_steps"].append("max_retries_reached")
        return state


def should_retry(state: AgentState) -> str:
    """Decision function - determine if process should be retried"""
    if state.get("error_messages"):
        last_error = state["error_messages"][-1]
        if "timeout" in last_error.lower() or "connection" in last_error.lower():
            if state.get("current_retry", 0) < state.get("max_retries", 1):
                return "retry"
    
    return "continue"


def check_response_quality(state: AgentState) -> str:
    """Decision function - verify response quality"""
    confidence = state.get("confidence_score", 0)
    
    if confidence < 0.2:
        if state.get("current_retry", 0) < state.get("max_retries", 1):
            return "regenerate"
    
    return "finalize" 