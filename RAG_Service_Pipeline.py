# RAG_Service_Pipeline.py
from typing import List, Dict, Any
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from functools import lru_cache
import time
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class RAG_SERVICE:
    _embedding_models = {}
    _vectorstores = {}

    def __init__(self, vector_store_path: str,
                 embedding_model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
                 cache_size: int = 256, llm_service=None):
        self.vector_store_path = vector_store_path
        self.embedding_model_name = embedding_model_name
        self.vectorstore = None
        self.embedding_model = None
        self._load_vectorstore()
        # decorate a helper that will be used for caching searches
        self._cached_search = lru_cache(maxsize=cache_size)(self._cached_search_impl)
        self.llm_service = llm_service

    def _load_vectorstore(self):
        cache_key = f"{self.vector_store_path}_{self.embedding_model_name}"
        # load embedding model (cached per class)
        if self.embedding_model_name not in self._embedding_models:
            self._embedding_models[self.embedding_model_name] = HuggingFaceEmbeddings(
                model_name=self.embedding_model_name
            )

        self.embedding_model = self._embedding_models[self.embedding_model_name]

        # Load the vector store once
        if cache_key not in self._vectorstores:
            logger.info("Loading FAISS vectorstore from %s", self.vector_store_path)
            self._vectorstores[cache_key] = FAISS.load_local(
                self.vector_store_path,
                self.embedding_model,
                allow_dangerous_deserialization=True
            )

        self.vectorstore = self._vectorstores[cache_key]

    # internal (non-cached) search impl — expects an already computed query embedding
    def _internal_search_by_vector(self, query_embedding: List[float], k: int = 5) -> List[Document]:
        # FAISS object provides similarity_search_by_vector
        return self.vectorstore.similarity_search_by_vector(query_embedding, k=k)

    # lru_cache friendly wrapper: note cache key depends only on textual query and k
    def _cached_search_impl(self, query: str, k: int = 5):
        # compute embedding once per query and call vector search
        t0 = time.perf_counter()
        query_embedding = self.embedding_model.embed_query(query)
        docs = self._internal_search_by_vector(query_embedding, k=k)
        t1 = time.perf_counter()
        logger.info("Search: query='%s' k=%d results=%d time=%.3fs", query[:80], k, len(docs), t1 - t0)
        return docs

    # public search method (uses cached wrapper)
    def search_documents(self, query: str, k: int = 5) -> List[Document]:
        # call the cached wrapper
        return self._cached_search(query, k)

    def format_context(self, documents: List[Document], include_metadata: bool = True, max_content_length: int = 500) -> str:
        parts = []
        for i, doc in enumerate(documents, 1):
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

    def query(self, question: str, k: int = 3) -> Dict[str, Any]:
        try:
            docs = self._cached_search(question, k)  # <--- use cached path
            if not docs:
                return {"Source": [], "context": ""}
            context = self.format_context(docs)
            return {"Retrived_doc": len(docs), "context": context}
        except Exception as e:
            logger.exception("Error during query: %s", e)
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
        self.clear_cache()

    def get_vectorstore_info(self) -> Dict[str, Any]:
        return {
            "vector_store_path": self.vector_store_path,
            "embedding_model": self.embedding_model_name,
            "is_loaded": self.vectorstore is not None
        }

    def answer_question(self, question: str, k: int = 3) -> Dict[str, Any]:
        retrieval_result = self.query(question, k)
        if not retrieval_result["context"] or not self.llm_service:
            return {"answer": "لا توجد معلومات كافية", **retrieval_result}

        answer = self.llm_service.generate_response(question, retrieval_result["context"])
        return {
            "answer": answer,
            "retrieved_docs": retrieval_result["Retrived_doc"],
            "context": retrieval_result["context"]
        }
