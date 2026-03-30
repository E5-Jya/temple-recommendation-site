#!/usr/bin/env python3
"""
upload_temple_photos.py
Downloads Google Places photos and uploads them to Supabase Storage.

For each temple:
  - Photo 1 @ 400px  -> {slug}/thumbnail.jpg
  - Photo 1 @ 1600px -> {slug}/hero.jpg
  - Photo 2 @ 1200px -> {slug}/gallery_2.jpg
  - Photo 3 @ 1200px -> {slug}/gallery_3.jpg

Saves photo_manifest.json with final public URLs.
"""

import csv
import json
import os
import sys
import time

import requests
from dotenv import load_dotenv

load_dotenv()

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

GOOGLE_API_KEY = os.environ.get("GOOGLE_PLACES_API_KEY")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
BUCKET = "temple-photos"
PLACE_PHOTO_URL = "https://maps.googleapis.com/maps/api/place/photo"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def ensure_bucket_exists():
    """Create the storage bucket if it doesn't exist."""
    headers = {
        "apikey": SUPABASE_SERVICE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
        "Content-Type": "application/json",
    }
    # Check if bucket exists
    resp = requests.get(
        f"{SUPABASE_URL}/storage/v1/bucket/{BUCKET}",
        headers=headers, timeout=15
    )
    if resp.status_code == 200:
        print(f"Bucket '{BUCKET}' already exists")
        return True

    # Create bucket
    payload = {
        "id": BUCKET,
        "name": BUCKET,
        "public": True,
    }
    resp = requests.post(
        f"{SUPABASE_URL}/storage/v1/bucket",
        headers=headers, json=payload, timeout=15
    )
    if resp.status_code in (200, 201):
        print(f"Bucket '{BUCKET}' created successfully")
        return True
    else:
        print(f"Failed to create bucket: {resp.status_code} {resp.text}")
        return False


def download_photo(photo_reference, max_width):
    """Download a photo from Google Places API. Returns bytes or None."""
    url = (
        f"{PLACE_PHOTO_URL}"
        f"?maxwidth={max_width}"
        f"&photo_reference={photo_reference}"
        f"&key={GOOGLE_API_KEY}"
    )
    resp = requests.get(url, timeout=30, allow_redirects=True)
    if resp.status_code == 200 and len(resp.content) > 0:
        return resp.content
    return None


def upload_to_storage(file_path, image_bytes):
    """Upload image bytes to Supabase Storage. Returns public URL or None."""
    headers = {
        "apikey": SUPABASE_SERVICE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
        "Content-Type": "image/jpeg",
        "x-upsert": "true",
    }
    url = f"{SUPABASE_URL}/storage/v1/object/{BUCKET}/{file_path}"
    resp = requests.post(url, headers=headers, data=image_bytes, timeout=30)
    if resp.status_code in (200, 201):
        public_url = f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET}/{file_path}"
        return public_url
    else:
        print(f"      Upload failed ({resp.status_code}): {resp.text[:200]}")
        return None


def main():
    if not GOOGLE_API_KEY:
        print("ERROR: GOOGLE_PLACES_API_KEY not set", file=sys.stderr)
        sys.exit(1)
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        print("ERROR: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY required", file=sys.stderr)
        sys.exit(1)

    # Load lookup data
    lookup_path = os.path.join(SCRIPT_DIR, "temple_photos_lookup.json")
    with open(lookup_path, "r", encoding="utf-8") as f:
        lookup = json.load(f)

    # Load slugs from CSV
    csv_path = os.path.join(SCRIPT_DIR, "..", "temples_database.csv")
    slug_map = {}
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            slug_map[row["temple_id"]] = row["slug"]

    print(f"Loaded {len(lookup)} temples from lookup, {len(slug_map)} slugs from CSV")
    print("=" * 70)

    # Ensure bucket exists
    if not ensure_bucket_exists():
        sys.exit(1)
    print("=" * 70)

    manifest = []
    total_uploaded = 0
    total_failed = 0

    for i, temple in enumerate(lookup, 1):
        temple_id = temple["temple_id"]
        name_en = temple.get("name_en", "")
        slug = slug_map.get(temple_id)
        photos = temple.get("photos", [])

        if not slug:
            print(f"\n[{i}/{len(lookup)}] {temple_id} -- SKIP (no slug)")
            continue

        if not photos:
            print(f"\n[{i}/{len(lookup)}] {temple_id} -- SKIP (no photos)")
            continue

        print(f"\n[{i}/{len(lookup)}] {temple_id} -- {name_en}")
        print(f"  Slug: {slug}")

        entry = {
            "temple_id": temple_id,
            "name_en": name_en,
            "slug": slug,
            "place_id": temple.get("place_id"),
            "rating": temple.get("rating"),
            "total_ratings": temple.get("total_ratings"),
            "photos": {},
        }

        # Define download tasks: (label, photo_index, width, storage_filename)
        tasks = [
            ("thumbnail", 0, 400, "thumbnail.jpg"),
            ("hero", 0, 1600, "hero.jpg"),
        ]
        if len(photos) >= 2:
            tasks.append(("gallery_2", 1, 1200, "gallery_2.jpg"))
        if len(photos) >= 3:
            tasks.append(("gallery_3", 2, 1200, "gallery_3.jpg"))

        for label, photo_idx, width, filename in tasks:
            photo_ref = photos[photo_idx]["photo_reference"]
            storage_path = f"{slug}/{filename}"

            print(f"    {label} ({width}px) -> {storage_path} ... ", end="", flush=True)

            # Download from Google
            image_bytes = download_photo(photo_ref, width)
            if not image_bytes:
                print("DOWNLOAD FAILED")
                total_failed += 1
                continue

            size_kb = len(image_bytes) / 1024
            print(f"{size_kb:.0f}KB ... ", end="", flush=True)

            # Upload to Supabase
            public_url = upload_to_storage(storage_path, image_bytes)
            if public_url:
                print("OK")
                entry["photos"][label] = public_url
                total_uploaded += 1
            else:
                print("UPLOAD FAILED")
                total_failed += 1

            # Rate limit
            time.sleep(0.15)

        manifest.append(entry)

    # Save manifest
    print("\n" + "=" * 70)
    print("SUMMARY")
    print(f"  Temples processed: {len(manifest)}")
    print(f"  Images uploaded:   {total_uploaded}")
    print(f"  Failures:          {total_failed}")
    print("=" * 70)

    manifest_path = os.path.join(SCRIPT_DIR, "photo_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print(f"\nManifest saved to {manifest_path}")


if __name__ == "__main__":
    main()
