# AI Agents using LangChain and LangGraph

A two-tier incident response system demonstrating different LangGraph patterns: sequential pipelines and cyclic (ReAct) agents.

## System Overview

This demo implements an automated incident response workflow with two levels:

### Level 1: Triage Agent (Sequential Pipeline)
A deterministic pipeline that performs initial investigation of incidents. It identifies the affected service, fetches logs and metrics, and generates a diagnostic report.

**Flow:** Alert → Classify Service → Fetch Logs → Fetch Metrics → Generate Report

### Level 2: Fixer Agent (ReAct Loop)
A Senior DevOps agent with permissions to fix production incidents. It uses a ReAct pattern to investigate issues and take corrective actions in a loop until the problem is resolved.

**Flow:** Alert → Classify Service → Agent ↔ Tools (Logs/Metrics/Scale/Restart) → Resolution

## Supported Services

The system can handle incidents for the following services:
- `payment-service` - Payment processing service
- `web-service` - Web application service
- `storage-service` - Data storage service

## Setup

### 1. Install uv (if not installed)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Install Dependencies

```bash
uv sync
```

### 3. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your settings:
- `OPENAI_API_KEY`: Your OpenAI API key (required for cloud mode)
- `USE_LOCAL_LLM`: Set to `true` to use Ollama locally

### 4. (Optional) Setup Ollama for Local LLM

```bash
# Install Ollama from https://ollama.ai
# Then pull the Mistral model:
ollama pull mistral-3:3b
```

## Usage

### Triage Agent (Level 1)

Performs initial investigation and generates a diagnostic report:

```bash
# Using OpenAI
uv run python -m src.main triage "El servicio de pagos está lento"

# Using Ollama locally
uv run python -m src.main triage "El servicio de pagos está lento" --local
```

### Fixer Agent (Level 2)

Investigates and fixes the incident:

```bash
# Using OpenAI
uv run python -m src.main fixer "Hay alta latencia en el servicio de pagos, soluciónalo"

# Using Ollama locally
uv run python -m src.main fixer "Hay alta latencia en el servicio de pagos, soluciónalo" --local
```

### Using LangGraph Studio

```bash
# Start the LangGraph development server
uv run langgraph dev
```

Then open LangGraph Studio in your browser to visualize and interact with the agent graphs.

## Project Structure

```
├── .env.example           # Environment template
├── pyproject.toml         # Python dependencies (uv)
├── langgraph.json         # LangGraph configuration
├── src/
│   ├── config.py          # LLM factory (OpenAI/Ollama)
│   ├── state.py           # Shared AgentState
│   ├── main.py            # CLI entry point
│   ├── mocks/
│   │   └── devops_tools.py    # Mock DevOps tools
│   └── agents/
│       ├── triage_chain.py    # Level 1: Triage Agent
│       └── devops_agent.py    # Level 2: Fixer Agent
```

## Available Mock Tools

The Fixer Agent has access to the following DevOps tools:

- `mock_get_service_logs(service_name)`: Returns simulated service logs with dynamic timestamps
- `mock_get_service_metrics(service_name)`: Returns CPU, memory, and connection metrics
- `mock_scale_service(service_name)`: Simulates horizontal scaling (adds 10 replicas)
- `mock_restart_service(service_name)`: Simulates service restart

## Agent Behavior

### Triage Agent
1. Classifies the request to identify the affected service
2. Fetches recent logs for the service
3. Fetches current metrics (CPU, memory, connections)
4. Generates a concise incident report in Spanish

### Fixer Agent
1. Classifies the request to identify the affected service
2. Reviews logs and metrics to diagnose the issue
3. Takes appropriate action:
   - Scales the service if CPU usage is high or latency issues are detected
   - Restarts the service if there are latency problems
4. Verifies the fix was successful
5. Responds in Spanish with a professional summary

## Requirements

- Python 3.11+
- uv package manager
- OpenAI API key (for cloud mode) OR Ollama installed (for local mode)
