import json
import faiss
import numpy as np
from openai import OpenAI
from tqdm import tqdm
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

with open("book_chunks.json", "r", encoding="utf-8") as f:
    chunks = json.load(f)

texts = [c["text"] for c in chunks]
batch_size = 50
embeddings = []

for i in tqdm(range(0, len(texts), batch_size), desc="Embedding chunks"):
    batch = texts[i:i+batch_size]
    resp = client.embeddings.create(
        model="text-embedding-3-small",
        input=batch
    )
    # extend with all embeddings from this batch
    embeddings.extend([d.embedding for d in resp.data])

emb_array = np.array(embeddings).astype("float32")
index = faiss.IndexFlatL2(emb_array.shape[1])
index.add(emb_array)

faiss.write_index(index, "book.index")

print("✅ Saved FAISS index with", len(chunks), "chunks")