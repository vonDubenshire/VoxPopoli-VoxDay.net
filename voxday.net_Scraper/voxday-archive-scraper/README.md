# Vox Day Blog Archive Scraper

A Python scraper to create a complete local archive of [voxday.net](https://voxday.net) (Vox Popoli).

## Features

- **Sitemap-based discovery**: Uses WordPress sitemaps to find all ~30,000 posts
- **Resume capability**: Safe to interrupt and resume anytime
- **Organized output**: Posts saved as JSON files organized by year/month
- **Complete extraction**: Title, date, author, content (HTML + text), tags, categories
- **Rate limiting**: Polite 1 request/second to avoid overloading the server
- **Progress tracking**: Saves checkpoint every 10 posts

## Requirements

- Python 3.8+
- `requests`
- `beautifulsoup4`
- `lxml`

## Installation

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/voxday-archive.git
cd voxday-archive

# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
python voxday_scraper.py
```

The scraper will:
1. Fetch the sitemap index from voxday.net
2. Discover all ~30,000 post URLs
3. Scrape each post and save as JSON
4. Create an index file with all post metadata

**Estimated runtime**: 8-10 hours for the full archive.

You can safely interrupt with `Ctrl+C` at any time. Progress is saved, and running the script again will resume from where it left off.

## Output Structure

```
voxday_archive/
├── index.json           # Master index of all posts
├── progress.json        # Checkpoint file for resume
├── 2003/
│   ├── 10/
│   │   ├── post-slug.json
│   │   └── ...
│   └── 11/
├── 2004/
│   └── ...
└── 2025/
    └── 12/
        └── latest-post.json
```

## Post JSON Format

Each post is saved as a JSON file with this structure:

```json
{
  "url": "https://voxday.net/2025/12/13/post-title/",
  "title": "Post Title",
  "author": "VD",
  "date_from_url": "2025-12-13",
  "date_iso": "2025-12-13T10:53:27+00:00",
  "content_html": "<div class=\"entry-content\">...</div>",
  "content_text": "Plain text content...",
  "tags": ["politics", "economics"],
  "categories": ["Decline and Fall"],
  "sitemap_lastmod": "2025-12-13T10:53:27+00:00",
  "scraped_at": "2025-12-13T15:30:00.000000"
}
```

## Searching the Archive

Once scraped, you can search with grep:

```bash
# Find all posts mentioning "free trade"
grep -rl "free trade" voxday_archive/

# Search with context
grep -r "free trade" voxday_archive/ -l | head -20

# Count posts per year
ls voxday_archive/20*/  | wc -l
```

Or load into a database/search tool of your choice.

## Configuration

Edit these variables at the top of `voxday_scraper.py`:

| Variable | Default | Description |
|----------|---------|-------------|
| `REQUEST_DELAY` | `1.0` | Seconds between requests |
| `OUTPUT_DIR` | `./voxday_archive` | Where to save files |
| `TIMEOUT` | `30` | Request timeout in seconds |

## License

This tool is for personal archival purposes. Respect the original content's copyright.

## Credits

Built for personal archival use.
