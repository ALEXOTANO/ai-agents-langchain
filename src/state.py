"""
Shared State Definitions for LangGraph Agents
"""
from typing import TypedDict, Annotated, List
import operator
from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    """
    Shared state for all agents in the system.
    
    Attributes:
        messages: Accumulated message history (uses operator.add for appending)
        prospect_info: Company/prospect data for outreach pipeline (Case B)
    """
  
    # 'add' ensures messages accumulate in the history
    messages: Annotated[List[BaseMessage], operator.add]
  
    logs: str
    metrics: str
    service_name: str




