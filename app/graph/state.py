from typing import List, Dict, Any, Optional
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    """Agent state containing all RAG flow information"""
    
    original_query: str
    conversation_history: List[Dict[str, str]]
    
    query_plan: List[str]
    
    retrieved_docs: List[Dict[str, Any]]
    
    generated_answer: str
    final_answer: str
    
    evaluation_result: Dict[str, Any]
    confidence_score: float
    
    processing_steps: List[str]
    error_messages: List[str]
    start_time: float
    end_time: Optional[float]
    
    max_retries: int
    current_retry: int 