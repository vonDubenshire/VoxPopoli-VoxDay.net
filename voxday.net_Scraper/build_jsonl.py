import os
import json
import glob

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARCHIVE_DIR = os.path.join(BASE_DIR, "voxday_archive")
OUTPUT_FILE = os.path.join(BASE_DIR, "voxday_corpus.jsonl")


def normalize_text(value):
    if value is None:
        return ""
    return str(value).strip()


def main():
    if not os.path.exists(ARCHIVE_DIR):
        print(
            f"Error: Archive directory '{ARCHIVE_DIR}' not found."
        )
        return

    search_pattern = os.path.join(ARCHIVE_DIR, "*", "*", "*.json")
    print(f"Searching for files with pattern: {search_pattern}")
    files = glob.glob(search_pattern)
    files.sort()

    print(f"Found {len(files)} post files.")

    count = 0
    with open(OUTPUT_FILE, "w", encoding="utf-8") as out_f:
        for filepath in files:
            if not filepath.endswith(".json"):
                continue

            try:
                with open(filepath, "r", encoding="utf-8") as in_f:
                    data = json.load(in_f)

                date = data.get("date_iso") or data.get("date_from_url") or data.get(
                    "date_display", "Unknown Date"
                )

                record = {
                    "title": normalize_text(data.get("title", "No Title")),
                    "date": normalize_text(date),
                    "url": normalize_text(data.get("url")),
                    "author": normalize_text(data.get("author")),
                    "tags": data.get("tags") or [],
                    "categories": data.get("categories") or [],
                    "content": normalize_text(data.get("content_text")),
                }

                out_f.write(json.dumps(record, ensure_ascii=False) + "\n")
                count += 1
            except Exception as e:
                print(f"Error reading {filepath}: {e}")

    print(f"Successfully extracted {count} posts to {OUTPUT_FILE}.")


if __name__ == "__main__":
    main()
