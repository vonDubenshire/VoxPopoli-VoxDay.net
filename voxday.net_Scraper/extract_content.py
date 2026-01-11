import os
import json
import glob

# Path to the archive directory relative to the repo root
ARCHIVE_DIR = "voxday.net_Scraper/voxday_archive"
OUTPUT_FILE = "voxday_corpus.txt"

def main():
    if not os.path.exists(ARCHIVE_DIR):
        print(f"Error: Archive directory '{ARCHIVE_DIR}' not found from current directory '{os.getcwd()}'.")
        return

    # The directories are YYYY/MM.
    # glob pattern "*/*/*.json" should match YYYY/MM/post.json
    search_pattern = os.path.join(ARCHIVE_DIR, "*", "*", "*.json")
    print(f"Searching for files with pattern: {search_pattern}")
    files = glob.glob(search_pattern)

    # Sort files to try and keep some chronological order (by folder structure)
    files.sort()

    print(f"Found {len(files)} post files.")

    count = 0
    with open(OUTPUT_FILE, "w", encoding="utf-8") as out_f:
        for filepath in files:
            # Skip if it happens to be a system file or not a post
            if not filepath.endswith(".json"):
                continue

            try:
                with open(filepath, "r", encoding="utf-8") as in_f:
                    data = json.load(in_f)

                    title = data.get("title", "No Title")
                    # Try to get ISO date first, then date from URL, then display date
                    date = data.get("date_iso")
                    if not date:
                        date = data.get("date_from_url")
                    if not date:
                         date = data.get("date_display", "Unknown Date")

                    content = data.get("content_text", "")

                    if content is None:
                        content = ""

                    out_f.write(f"Title: {title}\n")
                    out_f.write(f"Date: {date}\n")
                    out_f.write("-" * 20 + "\n")
                    out_f.write(content + "\n")
                    out_f.write("-" * 20 + "\n")
                    out_f.write("=" * 80 + "\n\n")

                    count += 1

            except Exception as e:
                print(f"Error reading {filepath}: {e}")

    print(f"Successfully extracted {count} posts to {OUTPUT_FILE}.")

if __name__ == "__main__":
    main()
