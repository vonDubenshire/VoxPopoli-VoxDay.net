import argparse
import glob
import json
import os

DEFAULT_ARCHIVE_DIR = "voxday.net_Scraper/voxday_archive"
DEFAULT_OUTPUT_FILE = "voxday_corpus.jsonl"


def normalize_text(value):
    if value is None:
        return ""
    return str(value).strip()


def parse_args():
    parser = argparse.ArgumentParser(
        description="Build a JSONL corpus from the Vox Day archive."
    )
    parser.add_argument(
        "--archive-dir",
        default=DEFAULT_ARCHIVE_DIR,
        help="Path to the voxday_archive directory.",
    )
    parser.add_argument(
        "--output",
        default=DEFAULT_OUTPUT_FILE,
        help="Output JSONL file path.",
    )
    parser.add_argument(
        "--include-html",
        action="store_true",
        help="Include HTML content in each JSONL record.",
    )
    parser.add_argument(
        "--no-text",
        action="store_true",
        help="Exclude plain-text content from each JSONL record.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    include_html = args.include_html
    include_text = not args.no_text

    if not os.path.exists(args.archive_dir):
        print(
            f"Error: Archive directory '{args.archive_dir}' not found from current directory '{os.getcwd()}'."
        )
        return

    search_pattern = os.path.join(args.archive_dir, "*", "*", "*.json")
    print(f"Searching for files with pattern: {search_pattern}")
    files = glob.glob(search_pattern)
    files.sort()

    print(f"Found {len(files)} post files.")

    count = 0
    with open(args.output, "w", encoding="utf-8") as out_f:
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
                    "sitemap_lastmod": normalize_text(data.get("sitemap_lastmod")),
                    "source": "voxday.net",
                }

                if include_text:
                    record["content_text"] = normalize_text(data.get("content_text"))
                if include_html:
                    record["content_html"] = normalize_text(data.get("content_html"))

                out_f.write(json.dumps(record, ensure_ascii=False) + "\n")
                count += 1
            except Exception as e:
                print(f"Error reading {filepath}: {e}")

    print(f"Successfully extracted {count} posts to {args.output}.")


if __name__ == "__main__":
    main()
