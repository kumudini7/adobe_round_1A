import os
import json
import pdfplumber
from collections import defaultdict

INPUT_DIR = "/app/input"
OUTPUT_DIR = "/app/output"

def extract_outline(pdf_path):
    headings = []
    title = ""
    font_sizes = defaultdict(int)

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            try:
                words = page.extract_words(extra_attrs=["size"])
                for word in words:
                    text = word["text"].strip()
                    if not text or len(text.split()) > 12:
                        continue
                    size = round(word["size"], 1)
                    font_sizes[size] += 1
                    headings.append({
                        "text": text,
                        "size": size,
                        "page": page_num
                    })
            except Exception as e:
                continue  # skip malformed page

    # Determine font sizes by frequency (largest = title, next = H1, ...)
    sorted_sizes = sorted(font_sizes.items(), key=lambda x: (-x[0], -x[1]))
    size_to_level = {}
    if sorted_sizes:
        size_to_level[sorted_sizes[0][0]] = "title"
        if len(sorted_sizes) > 1:
            size_to_level[sorted_sizes[1][0]] = "H1"
        if len(sorted_sizes) > 2:
            size_to_level[sorted_sizes[2][0]] = "H2"
        if len(sorted_sizes) > 3:
            size_to_level[sorted_sizes[3][0]] = "H3"

    outline = []
    used_titles = set()
    for h in headings:
        level = size_to_level.get(h["size"])
        if level == "title" and not title:
            title = h["text"]
            used_titles.add(h["text"])
        elif level in {"H1", "H2", "H3"}:
            if h["text"] not in used_titles:
                outline.append({
                    "level": level,
                    "text": h["text"],
                    "page": h["page"]
                })
                used_titles.add(h["text"])

    return {
        "title": title,
        "outline": outline
    }

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for filename in os.listdir(INPUT_DIR):
        if filename.lower().endswith(".pdf"):
            input_path = os.path.join(INPUT_DIR, filename)
            output_path = os.path.join(OUTPUT_DIR, filename.replace(".pdf", ".json"))
            try:
                result = extract_outline(input_path)
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
            except Exception as e:
                print(f"Failed to process {filename}: {e}")

if __name__ == "__main__":
    main()
