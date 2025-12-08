"""
Mock DevOps Tools for Case A: The Junior DevOps on Call

These tools simulate real DevOps operations like checking logs,
restarting services, and verifying health status.
"""
from datetime import datetime, timedelta
from langchain_core.tools import tool


@tool
def mock_get_service_logs(service_name: str) -> str:
    """
    Obtiene los logs recientes de un servicio específico.
    Args:
        service_name: El nombre del servicio (ej: 'payment-service', 'auth-service')
    """
    # Generate dynamic timestamps (current time minus a few minutes)
    now = datetime.now()
    t1 = (now - timedelta(minutes=8)).strftime("%Y-%m-%d %H:%M:%S")
    t2 = (now - timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S")
    t3 = (now - timedelta(minutes=3)).strftime("%Y-%m-%d %H:%M:%S")
    t4 = (now - timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:%S")
    t5 = (now - timedelta(minutes=1)).strftime("%Y-%m-%d %H:%M:%S")
    
    service_name = service_name.lower()
    if "payment" in service_name or "pagos" in service_name:
        return (
            f"{t1} WARN: High latency detected (2500ms).\n"
            f"{t2} ERROR: Connection pool nearing saturation.\n"
            f"{t3} ERROR: Database query timeout."
        )
    if "web" in service_name:
        return (
            f"{t1} ERROR: 502 Bad Gateway.\n"
            f"{t4} WARN: Request queue full.\n"
            f"{t2} ERROR: Worker process terminated unexpectedly."
        )
    if "storage" in service_name:
        return (
            f"{t1} WARN: Slow I/O detected on /data/vol1.\n"
            f"{t5} ERROR: Disk write queue depth > 100.\n"
            f"{t3} WARN: Compaction process taking longer than expected."
        )
    return "INFO: Service healthy. Heartbeat OK."


@tool
def mock_get_service_metrics(service_name: str) -> str:
    """
    Obtiene métricas clave (CPU, Memoria) de un servicio.
    Args:
        service_name: El nombre del servicio.
    """
    service_name = service_name.lower()
    if "payment" in service_name or "pagos" in service_name:
        return "CPU_USAGE: 95% | MEMORY_USAGE: 70% | ACTIVE_CONNECTIONS: 450/500"
    if "web" in service_name:
        return "CPU_USAGE: 80% | MEMORY_USAGE: 90% | ACTIVE_CONNECTIONS: 950/1000 | REQUEST_QUEUE: 150"
    if "storage" in service_name:
        return "CPU_USAGE: 60% | MEMORY_USAGE: 40% | DISK_IOPS: 5000 (Max: 3000) | WRITE_LATENCY: 500ms"
    return "CPU_USAGE: 15% | MEMORY_USAGE: 30% | ACTIVE_CONNECTIONS: 45/500"


@tool
def mock_scale_service(service_name: str) -> str:
    """
    Escala un servicio agregando 10 réplicas.
    Args:
        service_name: El nombre del servicio a escalar.
    """
    return f"Success: Scaled {service_name}, added 10 replicas. Now everything is working fine."


@tool   
def mock_restart_service(service_name: str) -> str:
    """
    Reinicia un servicio.
    Args:
        service_name: El nombre del servicio a reiniciar.
    """
    return f"Success: Restarted {service_name}. Now everything is working fine." 

DEVOPS_TOOLS = [mock_get_service_logs, mock_get_service_metrics, mock_scale_service, mock_restart_service]



