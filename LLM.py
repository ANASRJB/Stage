from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM
from RAG_Service_Pipeline import RAG_SERVICE
from langchain.chains import LLMChain
import time
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
# Instanciation of the RAG pipeline
rag = RAG_SERVICE(r"C:\Users\MSI\Documents\chatbot\Stage\vectorstores\procedures_faiss")
# prompt template to enhance the response of the LLM
message = """ 
أنت مساعد ذكي ومفيد. لديك عدة مستندات قد تحتوي على معلومات للإجابة على السؤال.

السياق:
{context}

السؤال: {question}

تعليمات:
- استخدم المعلومات من كل المستندات للإجابة
- حتى إذا لم يتم ذكر السؤال بالكلمات نفسها، أعط أفضل إجابة ممكنة
- كن مختصراً ومفيداً
- إذا لم يكن بالإمكان تقديم أي معلومات، قل "لا توجد معلومات كافية"

الإجابة:
"""

prompt_template= ChatPromptTemplate.from_messages([("human", message)])

#LLM creation 
llm = OllamaLLM(model="llama3.1:8b", temperature=0, max_tokens=512)
# chaining
chain = LLMChain(prompt=prompt_template, llm=llm)



# Answer generation
def get_bot_answer(question: str) -> str:
    t0 = time.perf_counter()
    retrieval = rag.query(question, k=3)
    t1 = time.perf_counter()
    logger.info("Retrieval time: %.3f s, docs=%s", t1 - t0, retrieval.get("Retrived_doc", 0))

    context = retrieval.get("context", "")
    if not context:
        logger.warning("No context retrieved for question: %s", question)
        return "لا توجد معلومات كافية"

    # Log the retrieved context and question for debugging
    logger.info("Question: %s", question)
    logger.info("Retrieved context length: %d characters", len(context))
    logger.info("Retrieved context preview: %s...", context[:200])

    # invoke LLM (blocking path). If OllamaLLM supports streaming, prefer streaming in UI to show tokens early.
    t2 = time.perf_counter()
    out = chain.run({"context": context, "question": question})
    t3 = time.perf_counter()
    logger.info("Generation time: %.3f s", t3 - t2)
    logger.info("LLM output: %s", out[:200] + "..." if len(out) > 200 else out)
    return out 