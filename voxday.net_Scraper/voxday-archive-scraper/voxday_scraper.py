#!/usr/bin/env python3
"""
Vox Day Blog Archive Scraper
============================
Scrapes the entire voxday.net blog archive using sitemap discovery.

Usage:
    python voxday_scraper.py

Output:
    - Creates ./voxday_archive/ directory
    - Saves posts as JSON files organized by year/month
    - Creates progress.json for resume capability
    - Creates index.json with all post metadata

Requirements:
    pip install requests beautifulsoup4 lxml --break-system-packages

Author: Built for Master Lance
"""

import json
import os
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

# =============================================================================
# CONFIGURATION
# =============================================================================

SITEMAP_INDEX_URL = "https://voxday.net/sitemap_index.xml"
OUTPUT_DIR = Path("./voxday_archive")
PROGRESS_FILE = OUTPUT_DIR / "progress.json"
INDEX_FILE = OUTPUT_DIR / "index.json"

# Rate limiting: seconds between requests
REQUEST_DELAY = 1.0

# Request settings
TIMEOUT = 30
USER_AGENT = "VoxDayArchiver/1.0 (Personal Archive Project)"

HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def setup_directories():
    """Create output directory structure."""
    OUTPUT_DIR.mkdir(exist_ok=True)
    print(f"[+] Output directory: {OUTPUT_DIR.absolute()}")


def load_progress() -> dict:
    """Load progress from checkpoint file."""
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE, "r") as f:
            return json.load(f)
    return {"scraped_urls": [], "failed_urls": [], "last_run": None}


def save_progress(progress: dict):
    """Save progress to checkpoint file."""
    progress["last_run"] = datetime.now().isoformat()
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f, indent=2)


def fetch_url(url: str) -> Optional[str]:
    """Fetch URL content with error handling."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"[!] Error fetching {url}: {e}")
        return None


def extract_date_from_url(url: str) -> Optional[str]:
    """Extract date from URL pattern like /2025/12/13/post-slug/"""
    match = re.search(r'/(\d{4})/(\d{2})/(\d{2})/', url)
    if match:
        return f"{match.group(1)}-{match.group(2)}-{match.group(3)}"
    return None


def get_output_path(url: str) -> Path:
    """Generate output path for a post based on its URL."""
    # Extract year/month from URL
    match = re.search(r'/(\d{4})/(\d{2})/\d{2}/([^/]+)/?', url)
    if match:
        year, month, slug = match.groups()
        # Clean slug for filename
        slug = re.sub(r'[^\w\-]', '_', slug)[:100]
        year_dir = OUTPUT_DIR / year / month
        year_dir.mkdir(parents=True, exist_ok=True)
        return year_dir / f"{slug}.json"
    else:
        # Fallback for non-standard URLs
        misc_dir = OUTPUT_DIR / "misc"
        misc_dir.mkdir(exist_ok=True)
        slug = urlparse(url).path.strip('/').replace('/', '_')[:100]
        return misc_dir / f"{slug}.json"


# =============================================================================
# SITEMAP PARSING
# =============================================================================

def fetch_sitemap_index() -> list[str]:
    """Fetch the sitemap index and extract all post sitemap URLs."""
    print("[*] Fetching sitemap index...")
    content = fetch_url(SITEMAP_INDEX_URL)
    if not content:
        raise RuntimeError("Failed to fetch sitemap index")
    
    soup = BeautifulSoup(content, "lxml-xml")
    sitemap_urls = []
    
    for sitemap in soup.find_all("sitemap"):
        loc = sitemap.find("loc")
        if loc and "post-sitemap" in loc.text:
            sitemap_urls.append(loc.text)
    
    print(f"[+] Found {len(sitemap_urls)} post sitemaps")
    return sorted(sitemap_urls)


def fetch_post_urls_from_sitemap(sitemap_url: str) -> list[dict]:
    """Fetch a single sitemap and extract post URLs with metadata."""
    content = fetch_url(sitemap_url)
    if not content:
        return []
    
    soup = BeautifulSoup(content, "lxml-xml")
    posts = []
    
    for url_entry in soup.find_all("url"):
        loc = url_entry.find("loc")
        lastmod = url_entry.find("lastmod")
        
        if loc:
            post_data = {
                "url": loc.text,
                "lastmod": lastmod.text if lastmod else None,
                "date": extract_date_from_url(loc.text)
            }
            posts.append(post_data)
    
    return posts


def fetch_all_post_urls() -> list[dict]:
    """Fetch all post URLs from all sitemaps."""
    sitemap_urls = fetch_sitemap_index()
    all_posts = []
    
    for i, sitemap_url in enumerate(sitemap_urls, 1):
        print(f"[*] Fetching sitemap {i}/{len(sitemap_urls)}: {sitemap_url}")
        posts = fetch_post_urls_from_sitemap(sitemap_url)
        all_posts.extend(posts)
        print(f"    Found {len(posts)} posts (total: {len(all_posts)})")
        time.sleep(REQUEST_DELAY)
    
    print(f"\n[+] Total posts discovered: {len(all_posts)}")
    return all_posts


# =============================================================================
# POST SCRAPING
# =============================================================================

def scrape_post(url: str) -> Optional[dict]:
    """Scrape a single blog post and extract its content."""
    content = fetch_url(url)
    if not content:
        return None
    
    soup = BeautifulSoup(content, "html.parser")
    post_data = {"url": url, "scraped_at": datetime.now().isoformat()}
    
    # Title
    title_tag = soup.find("h1", class_="entry-title") or soup.find("h1")
    post_data["title"] = title_tag.get_text(strip=True) if title_tag else None
    
    # Date - try multiple selectors
    date_tag = (
        soup.find("time", class_="entry-date") or
        soup.find("time") or
        soup.find(class_="posted-on")
    )
    if date_tag:
        post_data["date_display"] = date_tag.get_text(strip=True)
        if date_tag.get("datetime"):
            post_data["date_iso"] = date_tag["datetime"]
    
    # Extract date from URL as fallback
    post_data["date_from_url"] = extract_date_from_url(url)
    
    # Author
    author_tag = soup.find(class_="author") or soup.find("a", rel="author")
    post_data["author"] = author_tag.get_text(strip=True) if author_tag else "VD"
    
    # Content - look for the main article content
    content_tag = (
        soup.find("div", class_="entry-content") or
        soup.find("article") or
        soup.find(class_="post-content")
    )
    
    if content_tag:
        # Get raw HTML
        post_data["content_html"] = str(content_tag)
        
        # Get clean text
        # Remove script and style elements
        for element in content_tag.find_all(["script", "style"]):
            element.decompose()
        post_data["content_text"] = content_tag.get_text(separator="\n", strip=True)
    
    # Tags
    tags = []
    tag_container = soup.find(class_="tags-links") or soup.find(class_="post-tags")
    if tag_container:
        for tag_link in tag_container.find_all("a"):
            tags.append(tag_link.get_text(strip=True))
    post_data["tags"] = tags
    
    # Categories
    categories = []
    cat_container = soup.find(class_="cat-links") or soup.find(class_="post-categories")
    if cat_container:
        for cat_link in cat_container.find_all("a"):
            categories.append(cat_link.get_text(strip=True))
    post_data["categories"] = categories
    
    # Comments count (if visible)
    comments_tag = soup.find(class_="comments-link")
    if comments_tag:
        comments_text = comments_tag.get_text(strip=True)
        numbers = re.findall(r'\d+', comments_text)
        post_data["comments_count"] = int(numbers[0]) if numbers else 0
    
    return post_data


# =============================================================================
# MAIN SCRAPING LOGIC
# =============================================================================

def scrape_all_posts(post_urls: list[dict], progress: dict) -> dict:
    """Scrape all posts, respecting checkpoints."""
    scraped = set(progress.get("scraped_urls", []))
    failed = set(progress.get("failed_urls", []))
    
    # Filter to only unscraped posts
    to_scrape = [p for p in post_urls if p["url"] not in scraped]
    
    if len(scraped) > 0:
        print(f"[*] Resuming: {len(scraped)} already scraped, {len(to_scrape)} remaining")
    
    total = len(to_scrape)
    success_count = 0
    fail_count = 0
    
    for i, post_info in enumerate(to_scrape, 1):
        url = post_info["url"]
        
        # Progress indicator
        pct = (i / total) * 100
        print(f"[{i}/{total}] ({pct:.1f}%) Scraping: {url[:70]}...")
        
        # Scrape the post
        post_data = scrape_post(url)
        
        if post_data:
            # Add metadata from sitemap
            post_data["sitemap_lastmod"] = post_info.get("lastmod")
            
            # Save to file
            output_path = get_output_path(url)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(post_data, f, indent=2, ensure_ascii=False)
            
            scraped.add(url)
            success_count += 1
        else:
            failed.add(url)
            fail_count += 1
            print(f"    [!] Failed to scrape")
        
        # Update progress every 10 posts
        if i % 10 == 0:
            progress["scraped_urls"] = list(scraped)
            progress["failed_urls"] = list(failed)
            save_progress(progress)
        
        # Rate limit
        time.sleep(REQUEST_DELAY)
    
    # Final progress save
    progress["scraped_urls"] = list(scraped)
    progress["failed_urls"] = list(failed)
    save_progress(progress)
    
    print(f"\n[+] Scraping complete!")
    print(f"    Success: {success_count}")
    print(f"    Failed: {fail_count}")
    print(f"    Total archived: {len(scraped)}")
    
    return progress


def build_index(post_urls: list[dict]):
    """Build an index file with all post metadata."""
    print("[*] Building index...")
    
    index = {
        "generated_at": datetime.now().isoformat(),
        "total_posts": len(post_urls),
        "source": SITEMAP_INDEX_URL,
        "posts": sorted(post_urls, key=lambda x: x.get("date") or "", reverse=True)
    }
    
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2, ensure_ascii=False)
    
    print(f"[+] Index saved to {INDEX_FILE}")


# =============================================================================
# ENTRY POINT
# =============================================================================

def main():
    print("=" * 60)
    print("Vox Day Blog Archive Scraper")
    print("=" * 60)
    print()
    
    # Setup
    setup_directories()
    progress = load_progress()
    
    # Phase 1: Discover all post URLs
    print("\n--- Phase 1: Discovering Posts ---\n")
    post_urls = fetch_all_post_urls()
    
    # Build/update index
    build_index(post_urls)
    
    # Phase 2: Scrape all posts
    print("\n--- Phase 2: Scraping Posts ---\n")
    
    estimated_time = len(post_urls) * REQUEST_DELAY / 3600
    print(f"[*] Estimated time: {estimated_time:.1f} hours at {REQUEST_DELAY}s/request")
    print(f"[*] Progress saved every 10 posts - safe to interrupt with Ctrl+C")
    print()
    
    try:
        scrape_all_posts(post_urls, progress)
    except KeyboardInterrupt:
        print("\n\n[!] Interrupted by user. Progress saved. Run again to resume.")
        return
    
    print("\n" + "=" * 60)
    print("ARCHIVE COMPLETE")
    print("=" * 60)
    print(f"\nOutput directory: {OUTPUT_DIR.absolute()}")
    print(f"Index file: {INDEX_FILE}")
    print(f"\nTo search your archive:")
    print(f"  grep -r 'search term' {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
