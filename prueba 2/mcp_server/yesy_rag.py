from tools.rag_excel import excel_rag_search

def main():
    query = "Escribe aquí una pregunta que tenga sentido con tu Excel"
    context = excel_rag_search(query)
    print("\n=== CONTEXTO RAG ===\n")
    print(context)

if __name__ == "__main__":
    main()