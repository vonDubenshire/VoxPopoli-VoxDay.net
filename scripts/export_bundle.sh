#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
output_dir="$repo_root/exports"

mkdir -p "$output_dir"

python "$repo_root/voxday.net_Scraper/extract_content.py"
python "$repo_root/voxday.net_Scraper/build_jsonl.py"

REPO_ROOT="$repo_root" OUTPUT_DIR="$output_dir" python - <<'PY'
import hashlib
import os
import zipfile

repo_root = os.environ["REPO_ROOT"]
output_dir = os.environ["OUTPUT_DIR"]
corpus_txt = os.path.join(repo_root, "voxday.net_Scraper", "voxday_corpus.txt")
corpus_jsonl = os.path.join(repo_root, "voxday.net_Scraper", "voxday_corpus.jsonl")

zip_path = os.path.join(output_dir, "voxday_corpus_bundle.zip")
sha_path = os.path.join(output_dir, "voxday_corpus_bundle.sha256")

with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
    zf.write(corpus_txt, arcname="voxday_corpus.txt")
    zf.write(corpus_jsonl, arcname="voxday_corpus.jsonl")

sha256 = hashlib.sha256()
with open(zip_path, "rb") as fh:
    for chunk in iter(lambda: fh.read(1024 * 1024), b""):
        sha256.update(chunk)

digest = sha256.hexdigest()
with open(sha_path, "w", encoding="utf-8") as fh:
    fh.write(f"{digest}  {os.path.basename(zip_path)}\n")

print(f"Wrote {zip_path}")
print(f"Wrote {sha_path}")
PY
