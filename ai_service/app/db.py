import chromadb
from app.config import settings

class VectorStore:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=settings.CHROMA_DB_PATH)
        self.collection = self.client.get_or_create_collection(name=settings.COLLECTION_NAME)

    def query_tenant_context(self, prompt: str, tenant_id: str, n_results: int = 3) -> list[str]:
        results = self.collection.query(
            query_texts=[prompt],
            n_results=n_results,
            where={"tenant_id": tenant_id}
        )
        documents = results.get("documents", [[]])
        if documents and len(documents) > 0 and len(documents[0]) > 0:
            return documents[0]
        return []

vector_store = VectorStore()