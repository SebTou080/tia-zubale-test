import time
from langgraph.graph import StateGraph, END
from app.graph.state import AgentState
from app.graph.nodes import (
    plan_query,
    execute_retrieval,
    generate_answer,
    evaluate_answer,
    finalize_response,
    handle_error,
    should_retry,
    check_response_quality
)
import logging

logger = logging.getLogger(__name__)


def create_rag_graph():
    """Create and configure LangGraph for the RAG flow"""
    workflow = StateGraph(AgentState)
    
    workflow.add_node("plan_query", plan_query)
    workflow.add_node("execute_retrieval", execute_retrieval)
    workflow.add_node("generate_answer", generate_answer)
    workflow.add_node("evaluate_answer", evaluate_answer)
    workflow.add_node("finalize_response", finalize_response)
    workflow.add_node("handle_error", handle_error)
    
    workflow.set_entry_point("plan_query")
    
    workflow.add_edge("plan_query", "execute_retrieval")
    workflow.add_edge("execute_retrieval", "generate_answer")
    
    workflow.add_edge("generate_answer", "evaluate_answer")
    
    workflow.add_conditional_edges(
        "evaluate_answer",
        check_response_quality,
        {
            "finalize": "finalize_response",
            "regenerate": "generate_answer"
        }
    )
    
    workflow.add_edge("finalize_response", END)
    
    workflow.add_conditional_edges(
        "handle_error",
        should_retry,
        {
            "retry": "plan_query",
            "continue": "finalize_response"
        }
    )
    
    app = workflow.compile()
    
    logger.info("RAG graph compiled successfully")
    return app


rag_agent = create_rag_graph() 