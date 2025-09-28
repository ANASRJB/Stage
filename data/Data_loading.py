import os, glob, json, pickle
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import faiss
import numpy as np
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
docs = load_documents_from_json_dir("C:\\Users\\MSI\\Documents\\chatbot\\Stage\\data\\readydata")
print(f"Loaded {len(docs)} documents.")
# 2. Split
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = splitter.split_documents(docs)

# 3. Embedding
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

# 4. FAISS indexing - create HNSW index for faster ANN search
# create embeddings for chunks first
chunk_texts = [c.page_content for c in chunks]
chunk_embeddings = embedding_model.embed_documents(chunk_texts)

if not chunk_embeddings:
    print("Error: No embeddings created. Cannot proceed.")
    exit(1)

d = len(chunk_embeddings[0])
# create HNSW index
index = faiss.IndexHNSWFlat(d, 32)  # 32 = M param; tune if needed
# optional: tune efConstruction / efSearch:
index.hnsw.efConstruction = 200

# build index
xb = np.array(chunk_embeddings).astype("float32")
index.add(xb)

# create FAISS vectorstore using from_texts method
vectorstore = FAISS.from_texts(
    texts=chunk_texts,
    embedding=embedding_model,
    metadatas=[c.metadata for c in chunks]
)

# Create vectorstores directory if it doesn't exist
os.makedirs("vectorstores", exist_ok=True)
vectorstore.save_local("vectorstores/procedures_faiss")
# 6. Save documents
os.makedirs("data", exist_ok=True)
with open("data/documents.pkl", "wb") as f:
    pickle.dump(docs, f)

print("JSON loaded, embedded and indexed with FAISS.")
