# bot.py
import json
import faiss
import numpy as np
from openai import OpenAI
from telegram import Update
from telegram.constants import ChatAction
from telegram import InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import InlineQueryHandler
import uuid
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from dotenv import load_dotenv
import os
# from rank_bm25 import BM25Okapi


load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

index = faiss.read_index("book.index")
with open("book_chunks.json", "r", encoding="utf-8") as f:
    chunks = json.load(f)


def get_matching_results(query, top_n=3):
    """Given a user query, retrieve relevant book chunks."""
    resp = client.embeddings.create(model="text-embedding-3-small", input=query)
    q_emb = np.array(resp.data[0].embedding).astype("float32").reshape(1, -1)

    D, I = index.search(q_emb, k=top_n)
    retrieved = [chunks[i] for i in I[0]]
    distances = [distance for distance in D[0]]

    context_text = "\n\n".join(
        [
            f"{distances[i]} - {c['book']} {c['chapter']}:{c['verse']} → {c['text']}"
            for i, c in enumerate(retrieved)
        ]
    )

    return context_text, retrieved, distances


def get_reply(query):
    """Given a user query, retrieve relevant book chunks and generate a response."""
    context_text, retrieved, distances = get_matching_results(query)
    prompt = f"""Sei un assistente che risponde usando brevi citazioni (massimo 1-2 frasi)
dal libro fornito. Per ogni input fornito, rispondi con la citazione più pertinente dagli estratti del libro.
Rispondi con il versetto intero.

Estratti del libro:
{context_text}

Input fornito: {query}

Formato della risposta:
versetto intero (referenza)
"""

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt},
        ],
        temperature=0,
    )

    reply = completion.choices[0].message.content
    return reply


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! Ask me something about the book 📖")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.message.text

        # Show typing indicator
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id, action=ChatAction.TYPING
        )

        reply = get_reply(query)

        # reply = best_result
        await update.message.reply_text(reply)
    except Exception as e:
        await update.message.reply_text(
            "⚠️ Sorry, something went wrong. Please try again."
        )
        print("Error:", e)


async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.inline_query.query
        if not query:
            return

        context_text, retrieved, distances = get_matching_results(query, top_n=5)
        results = [
            InlineQueryResultArticle(
                id=str(uuid.uuid4()),
                title=f"{reply['book']} {reply['chapter']}:{reply['verse']}",
                description=reply['text'][:50] + "...",
                input_message_content=InputTextMessageContent(
                    message_text=f"{reply['text']} ({reply['book']} {reply['chapter']}:{reply['verse']})"
                ),
            )
            for reply in retrieved
        ]

        await update.inline_query.answer(results, cache_time=1)

    except Exception as e:
        await update.inline_query.answer([], cache_time=1)
        print("Error:", e)


def main():
    app = Application.builder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & ~filters.VIA_BOT, handle_message))
    app.add_handler(InlineQueryHandler(inline_query))
    app.run_polling()


if __name__ == "__main__":
    main()
