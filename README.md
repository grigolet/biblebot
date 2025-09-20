# BibleBot

A Telegram bot that answers questions about a book using OpenAI and FAISS for semantic search.

## Run with Docker

1. Build the Docker image:
   ```bash
   docker build -t biblebot .
   ```
2. Run the container (set your API keys):
   ```bash
   docker run --env OPENAI_API_KEY=your_openai_key --env TELEGRAM_BOT_TOKEN=your_telegram_token biblebot
   ```

## Push to GitHub

1. Create a new repo on GitHub.
2. Add the remote and push:
   ```bash
   git remote add origin https://github.com/yourusername/biblebot.git
   git branch -M main
   git push -u origin main
   ```

## Notes
- Make sure `book.index` and `book_chunks.json` are present in the container.
- Edit `.env` or pass environment variables for API keys.
