from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM
from RAG_Service_Pipeline import RAG_SERVICE

# Instanciation of the RAG pipeline
rag = RAG_SERVICE(r"C:\Users\MSI\Documents\chatbot\Stage\vectorstores\procedures_faiss")
# prompt template to enhance the response of the LLM
message=""" 
أنت مساعد ذكي ومفيد. استخدم السياق المقدم للإجابة على الأسئلة بدقة.

السياق:
{context}

السؤال: {question}

تعليمات:
- أجب باللغة العربية
- استخدم المعلومات من السياق فقط
- إذا لم تجد الإجابة في السياق، قل "لا توجد معلومات كافية"
- كن مختصراً ومفيداً

الإجابة:
"""
prompt_template= ChatPromptTemplate.from_messages([("human", message)])

#LLM creation 
llm=OllamaLLM(model="llama3.1:8b",temperature=0.0)
# chaining
chain= prompt_template | llm


# Answer generation
def get_bot_answer(question: str) -> str:
    response = rag.query(question)
    context = response["context"]
    return chain.invoke({"context": context, "question": question})

print(get_bot_answer("تجديد بطاقة التعريف الوطنية"))