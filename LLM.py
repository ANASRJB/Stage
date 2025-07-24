from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM
from RAG_Service_Pipeline import RAG_SERVICE

# Instanciation of the RAG pipeline
rag = RAG_SERVICE("vectorstores/procedures_faiss")
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
llm=OllamaLLM(model="llama3.1:8b")
# chaining
chain= prompt_template | llm

rag_question=input("Ask me!")
response=rag.query(rag_question)
context=response["context"]
# Answer generation
answer= chain.invoke({"context":context,"question":rag_question})
print(answer)
