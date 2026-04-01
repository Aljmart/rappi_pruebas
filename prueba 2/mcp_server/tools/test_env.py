from langchain_community.embeddings import OllamaEmbeddings

emb = OllamaEmbeddings(model="nomic-embed-text")
vec = emb.embed_query("hola mundo")

print(len(vec))
print(vec[:10])
