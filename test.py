# benchmark_rag.py
import time
from RAG_Service_Pipeline import RAG_SERVICE
from LLM import get_bot_answer, rag

queries = [
    "كيف أطلب وثيقة تسجيل الشركة؟",
    "ما هي شروط الحصول على تصريح؟",
]

r = rag  # using the same instance from your LLM.py if imported

for q in queries:
    t0 = time.perf_counter()
    docs = r.search_documents(q, k=3)
    t1 = time.perf_counter()
    print(f"Query: {q[:60]} | retrieval_time={t1-t0:.3f}s | docs={len(docs)}")
    t2 = time.perf_counter()
    ans = get_bot_answer(q)
    t3 = time.perf_counter()
    print(f"Total pipeline time={t3-t0:.3f}s | generation_time={t3-t2:.3f}s")
    print("Answer:", ans)
    print("-" * 60)
