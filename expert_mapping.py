"""
expert_mapping.py — Puente entre Streamlit y el servidor MCP de NotebookLM para mapeo de precisión.
"""
import json
import re
import subprocess

# ID del Notebook de Estadísticas HMI (identificado en pasos previos)
HMI_NOTEBOOK_ID = "8e64d715-dca5-4e16-afff-16b62fa04e49"

def consultar_experto_notebook(query_texto):
    """
    Envía una consulta al MCP de NotebookLM para obtener lógica de mapeo experta.
    """
    try:
        # Nota: Aquí usamos una llamada directa si el MCP no está disponible vía import
        # pero como somos un agente, podemos usar la herramienta mcp_notebooklm_notebook_query
        # En el entorno de producción del usuario, este módulo debería invocar el comando MCP
        # Para esta implementación, devolveremos una estructura que app.py procesará.
        
        # Simulamos la integración con el MCP para el flujo del código:
        # En una implementación real fuera del entorno del agente, se usaría la CLI o SDK del MCP
        return {
            "status": "pending_mcp_call",
            "query": query_texto
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

def parse_notebook_response_to_json(notebook_response):
    """
    Intenta extraer bloques JSON de la respuesta en lenguaje natural de NotebookLM.
    """
    if not notebook_response:
        return None
    
    # Buscar bloques JSON entre ```json ... ``` o simplemente { ... }
    match = re.search(r'```json\s*([\s\S]*?)\s*```', notebook_response)
    if not match:
        match = re.search(r'(\{[\s\S]*?\})', notebook_response)
    
    if match:
        try:
            return json.loads(match.group(1))
        except:
            return None
    return None
