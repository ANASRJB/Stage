from langchain_core.documents import Document # type: ignore

import os
import glob
import json

def flatten_text(record):
    """Assemble title, conditions et steps en un seul bloc de texte."""
    title = record.get("title", "")
    conditions = "\n".join(record.get("conditions", {}).values())
    steps = "\n".join(record.get("steps", {}).values())
    return f"{title}\n\nالشروط:\n{conditions}\n\nالمراحل:\n{steps}"

def load_documents_from_json_dir(directory_path):
    """Charge tous les fichiers JSON depuis un répertoire."""
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
docs = load_documents_from_json_dir("data/procedures")