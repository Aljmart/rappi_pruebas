from mcp.server.fastmcp import FastMCP
from tools.rag_excel import excel_rag_search
import os
from mcp.server.fastmcp import FastMCP
from tools.rag_excel import excel_rag_search
from langchain_ollama import ChatOllama
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Crear servidor MCP moderno
server = FastMCP("excel-rag-server")
llm = ChatOllama(model="llama3")

# Registrar tool RAG
@server.tool()
def buscar_excel(query: str) -> str:
    """
    Busca información en el índice FAISS generado desde Excel.
    """
    return excel_rag_search(query)

# Iniciar servidor
@server.tool()
def generar_reporte_pdf(query: str) -> str:
    """
    Genera un reporte profesional en PDF usando RAG + LLM.
    Devuelve la ruta del archivo PDF generado.
    """
    # 1. Obtener contexto desde FAISS
    context = excel_rag_search(query)

    # 2. Generar reporte con LLM
    prompt = f"""
Genera un reporte profesional basado en el siguiente contexto:

Contexto:
{context}

Instrucciones:
- Crea un reporte claro y bien estructurado.
- Incluye: Resumen, Hallazgos, Datos relevantes, Recomendaciones y Conclusión.
- Usa un tono profesional y directo.
- No inventes datos que no estén en el contexto.

Tema del reporte:
{query}
"""

    response = llm.invoke(prompt)
    reporte_texto = response.content

    # 3. Crear carpeta de reportes
    reports_dir = os.path.join(os.path.dirname(__file__), "reports")
    os.makedirs(reports_dir, exist_ok=True)

    # 4. Nombre del archivo PDF
    filename = f"reporte_{query.replace(' ', '_')}.pdf"
    filepath = os.path.join(reports_dir, filename)

    # 5. Generar PDF
    c = canvas.Canvas(filepath, pagesize=letter)
    width, height = letter

    y = height - 50
    for line in reporte_texto.split("\n"):
        c.drawString(50, y, line[:110])  # evita desbordes
        y -= 15
        if y < 50:
            c.showPage()
            y = height - 50

    c.save()

    return f"Reporte generado: {filepath}"
@server.tool()
def responder(query: str) -> str:
    """
    Usa RAG + LLM para responder preguntas basadas en el Excel.
    """
    context = excel_rag_search(query)

    prompt = f"""
Eres un asistente experto. Usa el siguiente contexto para responder:

Contexto:
{context}

Pregunta:
{query}

Responde de forma clara, precisa y útil.
"""

    response = llm.invoke(prompt)
    return response.content

if __name__ == "__main__":
    server.run()