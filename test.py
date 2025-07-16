from RAG_Service_Pipeline import RAG_SERVICE


rag = RAG_SERVICE("vectorstores/procedures_faiss")
response = rag.query("covid-19")
print(response["context"])
print(response["Retrived_doc"])
