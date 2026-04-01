from mcp_client import MCPClient

def main():
    client = MCPClient(host="localhost", port=8765)

    query = "¿Qué dice la base sobre el producto X?"

    response = client.call_tool(
        "excel_rag_search",
        {"query": query}
    )

    print("\n=== CONTEXTO RAG ===\n")
    print(response.get("result", "Sin resultados"))

if __name__ == "__main__":
    main()