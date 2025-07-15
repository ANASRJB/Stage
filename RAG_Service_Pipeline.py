from typing import List, Dict, Any
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document

# Creation of RAG_SERVICE class 
class RAG_SERVICE:
    # Constructor to initialize the vector store and embedding model
    def __init__(self, vector_store_path:str):
        self.vector_store_path = vector_store_path
        self.vectorstore = None
        self.embedding_model = None
        self._load_vectorstore()
    # Load the vector store from the specified path
    def _load_vectorstore(self):
        self.embedding_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        )
        self.vectorstore = FAISS.load_local(
            self.vectorstore_path, 
            self.embedding_model,
            allow_dangerous_deserialization=True
        )
    # Method to search for similar documents based on a query
    def search_similar_documents(self, query: str, k: int = 5) -> List[Document]:
        return self.vectorstore.similarity_search(query, k=k)
    # Context format
    def format_context(self, documents: List[Document]) -> str:
        parts = []
        for i, doc in enumerate(documents,1):
            title= doc.metadata.get("title","بدون عنوان")   
            administration= doc.metadata.get("administration","بدون إدارة")
            source= doc.metadata.get("source","بدون مصدر")
            content = doc.page_content
            parts.append(f"المستند {i}:\n\n"
                         f"العنوان: {title}\n"
                         f"الإدارة: {administration}\n"
                         f"المصدر: {source}\n\n"
                         f"{content}\n")
        return "\n".join(parts)
