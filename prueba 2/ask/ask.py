from tools.rag_excel import excel_rag_search
from langchain_ollama import ChatOllama
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

# Inicializar LLM local
llm = ChatOllama(model="llama3")

def responder(query: str) -> str:
    """
    RAG + LLM: responde preguntas usando tu Excel.
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


def generar_reporte_pdf(query: str) -> str:
    """
    Genera un reporte profesional en PDF usando RAG + LLM.
    """
    context = excel_rag_search(query)

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

    # Crear carpeta de reportes
    reports_dir = "reports"
    os.makedirs(reports_dir, exist_ok=True)

    # Nombre del archivo PDF
    filename = f"reporte_{query.replace(' ', '_')}.pdf"
    filepath = os.path.join(reports_dir, filename)

    # Generar PDF
    c = canvas.Canvas(filepath, pagesize=letter)
    width, height = letter

    y = height - 50
    for line in reporte_texto.split("\n"):
        c.drawString(50, y, line[:110])
        y -= 15
        if y < 50:
            c.showPage()
            y = height - 50

    c.save()

    return filepath
