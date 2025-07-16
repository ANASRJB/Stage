from typing import List, Dict, Any
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from functools import lru_cache
# Creation of RAG_SERVICE class 
class RAG_SERVICE:
    _embedding_models = {}
    _vectorstores = {}
    # Constructor to initialize the vector store and embedding model
    def __init__(self, vector_store_path:str, embedding_model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",cache_size: int = 100):
        self.vector_store_path = vector_store_path
        self.embedding_model_name = embedding_model_name
        self.vectorstore = None
        self.embedding_model = None
        self._load_vectorstore()
        # Cache the search results to improve performance
        self._cached_search = lru_cache(maxsize=cache_size)(self._internal_search)

    # Load the vector store from the specified path
    def _load_vectorstore(self):
        cache_key = f"{self.vector_store_path}_{self.embedding_model_name}"
        # load emabedding model(cached)
        if self.embedding_model_name not in self._embedding_models:
            self._embedding_models[self.embedding_model_name] = HuggingFaceEmbeddings(
                model_name=self.embedding_model_name
            )
        
        self.embedding_model = self._embedding_models[self.embedding_model_name]
        # Load the vector store
        if cache_key not in self._vectorstores:
            self._vectorstores[cache_key] = FAISS.load_local(
                self.vector_store_path, 
                self.embedding_model,
                allow_dangerous_deserialization=True
            )
        
        self.vectorstore = self._vectorstores[cache_key]       

    # Method to search for similar documents based on a query
    def _internal_search(self, query: str, k: int = 5) -> List[Document]:
        return self.vectorstore.similarity_search(query, k=k)
    # Search similar documents with caching
    def search_documents(self, query: str, k: int = 5) -> List[Document]:
        return self._cached_search(query, k)
    # Context format
    def format_context(self, documents: List[Document],include_metadata: bool = True,max_content_length: int = 500) -> str:
        parts = []
        for i, doc in enumerate(documents,1):
            content = doc.page_content
            if len(content) > max_content_length:
                content = content[:max_content_length] + "..."
            
            if include_metadata:
                title = doc.metadata.get("title", "بدون عنوان")
                administration = doc.metadata.get("administration", "بدون إدارة")
                source = doc.metadata.get("source", "بدون مصدر")
                
                parts.append(f"المستند {i}:\n\n"
                           f"العنوان: {title}\n"
                           f"الإدارة: {administration}\n"
                           f"المصدر: {source}\n\n"
                           f"{content}\n")
            else:
                parts.append(f"المستند {i}:\n{content}\n")
        
        return "\n".join(parts)
    # query method to search and format context
    def query(self, question: str, k: int = 3) -> Dict[str, Any]:
        try:
           docs=self._internal_search(question, k) 
           if not docs:
              return {"Source":[], "context": ""}
           context = self.format_context(docs)
           return {"Retrived_doc": len(docs), "context": context}
        except Exception :
            return {"Retrived_doc": 0, "context": ""}

    def clear_cache(self):
        self._cached_search.cache_clear()
    
    def get_cache_info(self) -> Dict[str, Any]:
        cache_info = self._cached_search.cache_info()
        return {
            "hits": cache_info.hits,
            "misses": cache_info.misses,
            "current_size": cache_info.currsize,
            "max_size": cache_info.maxsize
        }
    
    def add_documents(self, documents: List[Document]):
        self.vectorstore.add_documents(documents)
        self.vectorstore.save_local(self.vector_store_path)
        # Clear cache since new documents were added
        self.clear_cache()
    
    def get_vectorstore_info(self) -> Dict[str, Any]:
        return {
            "vector_store_path": self.vector_store_path,
            "embedding_model": self.embedding_model_name,
            "is_loaded": self.vectorstore is not None
        }