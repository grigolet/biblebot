import re
from pathlib import Path

# Mapping superscript digits → normal digits
SUPERSCRIPTS = {
    "⁰": "0",
    "¹": "1",
    "²": "2",
    "³": "3",
    "⁴": "4",
    "⁵": "5",
    "⁶": "6",
    "⁷": "7",
    "⁸": "8",
    "⁹": "9",
}

def normalize_superscripts(text: str) -> str:
    """
    Replace superscript sequences with normal numbers + a dot.
    Example: '²' -> '2.' and '²²' -> '22.'
    """

    def replace_match(match):
        superscripts = match.group(0)
        normal_digits = "".join(SUPERSCRIPTS.get(ch, "") for ch in superscripts)
        return normal_digits + "."

    # Replace sequences of superscripts
    text = re.sub(r"[⁰¹²³⁴⁵⁶⁷⁸⁹]+", replace_match, text)

    # Optional cleanup: avoid double dots like "22.."
    text = re.sub(r"\.\.", ".", text)
    return text


if __name__ == "__main__":
    input_file = Path("book.txt")
    output_file = Path("book_cleaned.txt")

    # Read raw text
    raw_text = input_file.read_text(encoding="utf-8")

    # Normalize superscripts
    clean_text = normalize_superscripts(raw_text)

    # Save cleaned text
    output_file.write_text(clean_text, encoding="utf-8")

    print(f"✅ Cleaned text written to {output_file}")