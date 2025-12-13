"""
Level 1: Triage Agent (Linear Graph)

This agent automates the initial investigation of an incident.
It extracts the service name, fetches logs and metrics, and generates a report.
"""
import datetime
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from typing import Literal

from src.config import get_llm
from src.state import AgentState
from src.mocks.devops_tools import mock_get_service_logs, mock_get_service_metrics, reset_simulation



# System prompt for the service extractor and validator
CLASSIFIER_SYSTEM_PROMPT = """Eres un experto en sistemas.
Tu tarea es entender la solicitud y determinar si se refiere a un servicio conocido.
Los servicios válidos son:
- payment-service
- web-service
- storage-service

Devuelve SOLO el nombre del servicio si es válido.
Si la solicitud NO es sobre uno de estos servicios o no es clara, devuelve 'unknown'.
"""

# System prompt for the reporter
REPORTER_SYSTEM_PROMPT = """Eres un SRE (Site Reliability Engineer) experto.
Tu tarea es generar un reporte de incidente breve y conciso en ESPAÑOL.
Basado en los logs y métricas proporcionados, resume la situación.
No sugieras soluciones, solo reporta los hechos.
"""


def create_triage_agent():
    """
    Creates the Triage agent
    Returns:
        Compiled LangGraph StateGraph
    """
    llm = get_llm()
    
    def classify_request(state: AgentState):
        # Helper to get content from object or dict (LangGraph Studio vs CLI compatibility)
        last_msg = state["messages"][-1]
        user_input = last_msg.content if hasattr(last_msg, "content") else last_msg["content"]
        
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        messages = [
            SystemMessage(content=f"{CLASSIFIER_SYSTEM_PROMPT}\nCurrent Time: {current_time}"),
            HumanMessage(content=f"Input: {user_input}")
        ]
        response = llm.invoke(messages)
        service_name = response.content.strip()
        
        return {"service_name": service_name}

    def handle_refusal_node(state: AgentState):
        """Return a refusal message for unknown services."""
        msg = "No puedo ayudarte con eso, solo puedo ayudarte con problemas en los serivicios: payment-service, web-service, storage-service"
        return {"messages": [SystemMessage(content=msg)]}

    def fetch_logs_node(state: AgentState):
        """Fetch logs for the identified service."""
        # Helper to get content from object or dict
        last_msg = state["messages"][-1]
        user_input = last_msg.content if hasattr(last_msg, "content") else last_msg["content"]
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        messages = [
            SystemMessage(content=f"{CLASSIFIER_SYSTEM_PROMPT}\nCurrent Time: {current_time}"),
            HumanMessage(content=f"Input: {user_input}")
        ]
        response = llm.invoke(messages)
        service_name = response.content

        # service_name = state["service_name"] # Already extracted
        logs = mock_get_service_logs.invoke(service_name)
        return {
            "logs": logs,
            "service_name": service_name
        }

    def fetch_metrics_node(state: AgentState):
        """Fetch metrics for the service."""
        service_name = state["service_name"] # Already extracted
        metrics = mock_get_service_metrics.invoke(service_name)
        return {"metrics": metrics}
    
    def generate_report_node(state: AgentState):
        """Generate a summary report."""
        logs = state.get("logs", "")
        metrics = state.get("metrics", "")
        service = state.get("service_name", "")
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        prompt = f"""
        Servicio: {service}
        
        Analiza los siguientes datos del sistema:
        
        LOGS:
        {logs}
        
        METRICS:
        {metrics}
        
        Genera un reporte de incidente en Español.
        """
        
        messages = [
            SystemMessage(content=f"{REPORTER_SYSTEM_PROMPT}\nCurrent Time: {current_time}"),
            HumanMessage(content=prompt)
        ]
        
        response = llm.invoke(messages)
        
        return {"messages": [response]}
    
    def route_request(state: AgentState) -> Literal["fetch_logs", "handle_refusal"]:
        """Decide next step based on service_name."""
        service = state.get("service_name", "unknown")
        if service == "unknown":
            return "handle_refusal"
        return "fetch_logs"

    # Build the graph
    workflow = StateGraph(AgentState)
    
    # workflow.add_node("classify_request", classify_request)
    # workflow.add_node("handle_refusal", handle_refusal_node)
    workflow.add_node("fetch_logs", fetch_logs_node)
    workflow.add_node("fetch_metrics", fetch_metrics_node)
    workflow.add_node("generate_report", generate_report_node)
    
    workflow.set_entry_point("fetch_logs")

    #workflow.set_entry_point("classify_request")
    #workflow.add_conditional_edges(
    #    "classify_request",
    #    route_request
    #)
    
    # workflow.add_edge("handle_refusal", END)
    workflow.add_edge("fetch_logs", "fetch_metrics")
    workflow.add_edge("fetch_metrics", "generate_report")
    workflow.add_edge("generate_report", END)
    
    return workflow.compile()


def run_triage_agent(input_text: str):
    """
    Run the Triage agent.
    """
    agent = create_triage_agent()
    
    initial_state = {
        "messages": [HumanMessage(content=input_text)],
        "logs": "",
        "metrics": "",
        "service_name": ""
    }
    
    result = agent.invoke(initial_state)
    return result["messages"][-1].content
