import os, glob, json, pickle
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

def flatten_text(record):
    title = record.get("title", "")
    conditions = "\n".join(record.get("conditions", {}).values())
    steps = "\n".join(record.get("steps", {}).values())
    return f"{title}\n\nالشروط:\n{conditions}\n\nالمراحل:\n{steps}"

def load_documents_from_json_dir(directory_path):
    documents = []
    for file_path in glob.glob(os.path.join(directory_path, "*.json")):
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for item in data:
            doc = Document(
                page_content=flatten_text(item),
                metadata={
                    "title": item.get("title", ""),
                    "administration": item.get("administration", ""),
                    "source": item.get("link", ""),
                    "file": os.path.basename(file_path)
                }
            )
            documents.append(doc)
    return documents

# 1. Load JSON documents
docs = load_documents_from_json_dir("data/ready_data")

# 2. Split
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
chunks = splitter.split_documents(docs)

# 3. Embedding
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

# 4. FAISS indexing
vectorstore = FAISS.from_documents(chunks, embedding_model)

# 5. Save vector index
vectorstore.save_local("vectorstores/procedures_faiss")

# 6. Save documents
with open("stage/documents.pkl", "wb") as f:
    pickle.dump(docs, f)

print("✅ JSON loaded, embedded and indexed with FAISS.")
