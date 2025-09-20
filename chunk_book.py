import re
import json
from pathlib import Path

def preprocess_text(text: str):
    """
    Preprocess structured Bible-like text into chunks for embeddings.
    """
    chunks = []
    current_book = None
    current_chapter = None

    lines = text.splitlines()

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Detect a Book title (heuristic: single word, capitalized, no dot at end)
        if re.match(r"^[A-Z][a-zàèéìòùA-Z\s]+$", line) and len(line.split()) <= 3:
            current_book = line.strip()
            continue

        # Detect chapter + text (e.g. "49 Giacobbe...")
        chapter_match = re.match(r"^(\d+)\s+(.*)", line)
        if chapter_match:
            current_chapter = int(chapter_match.group(1))
            rest_text = chapter_match.group(2)
            # Append as a temporary text with chapter header
            if rest_text:
                chunks.append({
                    "book": current_book,
                    "chapter": current_chapter,
                    "verse": None,
                    "text": rest_text.strip()
                })
            continue

        # Detect verse/subparagraph (e.g. "2. Radunatevi...")
        verse_match = re.match(r"^(\d+)\.\s+(.*)", line)
        if verse_match:
            verse_num = int(verse_match.group(1))
            verse_text = verse_match.group(2)
            chunks.append({
                "book": current_book,
                "chapter": current_chapter,
                "verse": verse_num,
                "text": verse_text.strip()
            })
            continue

        # If none matched, it’s a continuation of previous chunk → append text
        if chunks:
            chunks[-1]["text"] += " " + line.strip()

    return chunks


if __name__ == "__main__":
    input_file = Path("book_cleaned.txt")
    output_file = Path("book_chunks.json")

    raw_text = input_file.read_text(encoding="utf-8")
    chunks = preprocess_text(raw_text)

    # Save as JSON
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)

    print(f"✅ Extracted {len(chunks)} chunks into {output_file}")