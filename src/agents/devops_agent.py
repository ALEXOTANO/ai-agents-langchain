"""
Level 2: The Fixer Agent (ReAct)

This agent acts as a Senior DevOps Engineer capable of fixing incidents.
It uses a ReAct loop to investigate (Logs/Metrics) and then take action (Scale).
"""
import datetime
from typing import Literal
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from src.config import get_llm
from src.state import AgentState
from src.mocks.devops_tools import DEVOPS_TOOLS, reset_simulation

# System prompt giving the agent its personality
DEVOPS_SYSTEM_PROMPT = """Eres un Senior DevOps Engineer con permisos para arreglar incidentes en producción.
Tu objetivo es restaurar la salud del servicio.

Si te piden ayuda con un servicio que no es conocido, di "No puedo ayudarte con eso".

Tienes acceso a las siguientes herramientas:
- mock_get_service_logs: Para ver logs y diagnosticar errores.
- mock_get_service_metrics: Para ver carga de CPU/Memoria.
- mock_scale_service: Para escalar el servicio (horizontal scaling).
- mock_restart_service: Para reiniciar el servicio.

TUS INSTRUCCIONES:
1. Siempre revisa los logs y métricas primero para confirmar el problema.
2. Si ves uso alto de CPU o problemas de latencia, escala el servicio.
3. Si ves algun otro problema, reinicia el servicio.
4. Verifica que la solución haya funcionado.
5. Siempre vuelve a revisar los logs y métricas para confirmar que el problema ha sido resuelto.
6. Responde en ESPAÑOL.

Sé conciso y profesional.
"""

# System prompt for the service extractor and validator (Copied from triage_chain for independence)
CLASSIFIER_SYSTEM_PROMPT = """Eres un experto en sistemas.
Tu tarea es entender la solicitud y determinar si se refiere a un servicio conocido.
Los servicios válidos son:

- payment-service: todo lo que que tenga que ver con pagos y el carrito de compras
- web-service: todo lo que tenga que ver con la página web y el frontend
- storage-service: todo lo que tenga que ver con el almacenamiento, la base de datos y la carga y descarga de archivos. 

Devuelve SOLO el nombre del servicio si es válido.
Si la solicitud NO es sobre uno de estos servicios o no es clara, devuelve 'unknown'.
"""


def create_devops_agent():
    """
    Creates the DevOps agent graph with ReAct pattern.
    Returns:
        Compiled LangGraph StateGraph
    """
    
    llm = get_llm()
    llm_with_tools = llm.bind_tools(DEVOPS_TOOLS)
    
    def classify_request_node(state: AgentState):
        """Classify the request and extract service name."""
        user_input = state["messages"][-1]['content']
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        messages = [
            SystemMessage(content=f"{CLASSIFIER_SYSTEM_PROMPT}\nCurrent Time: {current_time}"),
            HumanMessage(content=f"Input: {user_input}")
        ]
        response = llm.invoke(messages)
        service_name = response.content.strip()
        
        return {"service_name": service_name}
    
    def agent_node(state: AgentState):
        """Invoke the LLM with the current state."""

        messages = state["messages"]
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        affected_service = state.get("service_name", "unknown")
       
        if not isinstance(messages[0], SystemMessage):
             messages = [SystemMessage(content=f"{DEVOPS_SYSTEM_PROMPT}\nCurrent Time: {current_time} \nAffected Service: {affected_service}")] + messages
        
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}
    
    def should_continue(state: AgentState) -> Literal["tools", END]:
        """Determine if we should continue to tools or end."""

        last_message = state["messages"][-1]
        
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        
        reset_simulation()
        
        return END
    
    workflow = StateGraph(AgentState)
    
    # Nodes
    workflow.add_node("classify_request", classify_request_node)
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", ToolNode(DEVOPS_TOOLS))
    
    # Entry point
    workflow.set_entry_point("classify_request")
    
    # Edges
    workflow.add_edge("classify_request", "agent")
    
    workflow.add_edge("tools", "agent")

    # Add Conditional Edges
    workflow.add_conditional_edges("agent", should_continue)
    
    return workflow.compile()


def run_devops_agent(problem: str, use_local: bool | None = None):
    """
    Run the DevOps agent with a given problem description.
    
    Args:
        problem: Description of the issue to investigate
        use_local: LLM provider selection (passed to config implicitly via env or ignored here as per current setup)
        
    Returns:
        Final response from the agent
    """
    agent = create_devops_agent()
    
    initial_state = {
        "messages": [HumanMessage(content=problem)],
        "logs": "",     # Not explicitly used by this agent's logic but required by state
        "metrics": "",   # Not explicitly used by this agent's logic but required by state
        "service_name": ""
    }
    
    # Run the agent
    result = agent.invoke(initial_state)
    
    # Return the final message content
    return result["messages"][-1].content
