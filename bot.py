# bot.py
import json
import faiss
import numpy as np
from openai import OpenAI
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

index = faiss.read_index("book.index")
with open("book_chunks.json", "r", encoding="utf-8") as f:
    chunks = json.load(f)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! Ask me something about the book 📖")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text
    
    # Show typing indicator
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)

    resp = client.embeddings.create(
        model="text-embedding-3-small",
        input=query
    )
    q_emb = np.array(resp.data[0].embedding).astype("float32").reshape(1, -1)

    D, I = index.search(q_emb, k=10)
    retrieved = [chunks[i] for i in I[0]]
    distances = [distance for distance in D[0]]

    context_text = "\n\n".join(
        [f"{distances[i]} - {c['book']} {c['chapter']}:{c['verse']} → {c['text']}" for i, c in enumerate(retrieved)]
    )

    prompt = f"""Sei un assistente che risponde usando brevi citazioni (massimo 1-2 frasi)
dal libro fornito. Per ogni input fornito, rispondi con la citazione più pertinente dagli estratti del libro.

Estratti del libro:
{context_text}

Input fornito: {query}

Formato della risposta:
citazione breve (referenza)
"""

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {'role': 'system', 'content': 'Rispondi con il versetto del libro più pertinente alla domanda. Rispondi con il versetto per intero. '},
            {'role': 'user', 'content': prompt},
        ],
        temperature=0,
    )

    reply = completion.choices[0].message.content
    # reply = best_result
    await update.message.reply_text(reply)
    
async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.inline_query.query
    if not query:
        return
    
    

    # Perform the same FAISS + LLM retrieval
    result_text = f"Result for: {query}"  # (Replace with actual retrieval)

    results = [
        InlineQueryResultArticle(
            id=str(uuid.uuid4()),
            title="Book answer",
            input_message_content=InputTextMessageContent(result_text)
        )
    ]

    await update.inline_query.answer(results, cache_time=1)
    


def main():
    app = Application.builder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()