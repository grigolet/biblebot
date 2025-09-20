from openai import OpenAI
import faiss
import numpy as np
import json

from pypdf import PdfReader
from ebooklib import epub
from bs4 import BeautifulSoup
from tqdm import tqdm

import ebooklib

import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_from_pdf(path):
    reader = PdfReader(path)
    texts = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if text:
            texts.append({"ref": f"Page {i+1}", "text": text})
    return texts

def extract_from_epub(path):
    book = epub.read_epub(path)
    texts = []
    chap_num = 1
    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            soup = BeautifulSoup(item.get_content(), "html.parser")
            text = soup.get_text()
            if text.strip():
                texts.append({"ref": f"Chapter {chap_num}", "text": text})
                chap_num += 1
    return texts

# Set your source file
SOURCE_FILE = "book.epub"  # or "book.epub"

if SOURCE_FILE.endswith(".pdf"):
    raw_chunks = extract_from_pdf(SOURCE_FILE)
elif SOURCE_FILE.endswith(".epub"):
    raw_chunks = extract_from_epub(SOURCE_FILE)
else:
    raise ValueError("Unsupported file format")

# Split into ~1000-character chunks
chunks = []
for entry in raw_chunks:
    ref = entry["ref"]
    text = entry["text"]
    for i in range(0, len(text), 1000):
        chunks.append({
            "ref": ref,
            "text": text[i:i+1000]
        })

print(f"📖 Preparing {len(chunks)} chunks from {SOURCE_FILE}...")

# Embed with progress bar
embeddings = []
for chunk in tqdm(chunks, desc="Embedding chunks"):
    resp = client.embeddings.create(
        model="text-embedding-3-small",
        input=chunk["text"]
    )
    embeddings.append(resp.data[0].embedding)

embeddings = np.array(embeddings).astype("float32")

# Store in FAISS
index = faiss.IndexFlatL2(embeddings.shape[1])
index.add(embeddings)
faiss.write_index(index, "book.index")

# Save chunks with refs
with open("book_chunks.json", "w", encoding="utf-8") as f:
    json.dump(chunks, f, ensure_ascii=False, indent=2)

print("✅ Index built successfully")