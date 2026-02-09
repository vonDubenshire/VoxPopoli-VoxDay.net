# Vox Day corpus exports

This repo already contains a local archive of Vox Popoli posts under `voxday.net_Scraper/voxday_archive/`.
To prepare files for ingestion into an LLM or other tooling, the following exports are generated
from the archive:

- `voxday.net_Scraper/voxday_corpus.txt` — plain-text corpus (title/date/content blocks).
- `voxday.net_Scraper/voxday_corpus.jsonl` — JSONL corpus (one post per line with metadata + content).
- `exports/voxday_corpus_bundle.zip` — ZIP bundle containing both files.
- `exports/voxday_corpus_bundle.sha256` — SHA-256 checksum for the ZIP bundle.

## Generate everything (recommended)

Run the script below to regenerate the corpus files and build a bundled ZIP + checksum:

```bash
./scripts/export_bundle.sh
```

## How to download

From the repo root (`/workspace/VoxPopoli-VoxDay.net`), you can copy the export files to your local
machine using any of the following:

- **Direct file copy** (if you have filesystem access to the container):
  - `voxday.net_Scraper/voxday_corpus.txt`
  - `voxday.net_Scraper/voxday_corpus.jsonl`
  - `exports/voxday_corpus_bundle.zip`
  - `exports/voxday_corpus_bundle.sha256`

- **CLI transfer** (from your own machine):
  - `scp <user>@<host>:/workspace/VoxPopoli-VoxDay.net/voxday.net_Scraper/voxday_corpus.txt .`
  - `scp <user>@<host>:/workspace/VoxPopoli-VoxDay.net/voxday.net_Scraper/voxday_corpus.jsonl .`
  - `scp <user>@<host>:/workspace/VoxPopoli-VoxDay.net/exports/voxday_corpus_bundle.zip .`
  - `scp <user>@<host>:/workspace/VoxPopoli-VoxDay.net/exports/voxday_corpus_bundle.sha256 .`
