#!/usr/bin/env python3
"""
upload_temple_photos.py
Downloads Google Places photos and uploads them to Supabase Storage.

For each temple:
  - Photo 1 @ 400px  -> {slug}/thumbnail.jpg
  - Photo 1 @ 1600px -> {slug}/hero.jpg
  - Photo 2 @ 1200px -> {slug}/gallery_2.jpg
  - Photo 3 @ 1200px -> {slug}/gallery_3.jpg

Automatically skips temples that already have photos in photo_manifest.json
(i.e. those with non-empty "photos" containing Supabase public URLs).
Use --only to re-upload specific temples.

Saves/updates photo_manifest.json with final public URLs.
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
MANIFEST_PATH = os.path.join(SCRIPT_DIR, "photo_manifest.json")
SUPABASE_PUBLIC_BASE = f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET}"


def load_manifest():
    """Load existing photo_manifest.json, return dict keyed by temple_id."""
    if not os.path.exists(MANIFEST_PATH):
        return {}
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return {entry["temple_id"]: entry for entry in data}


def save_manifest(manifest_dict):
    """Save manifest dict back to photo_manifest.json (sorted by temple_id)."""
    entries = sorted(manifest_dict.values(), key=lambda x: x["temple_id"])
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)
    print(f"\nManifest saved to {MANIFEST_PATH} ({len(entries)} temples)")


def has_uploaded_photos(entry):
    """Check if a manifest entry already has Supabase public URLs (not Google API URLs)."""
    photos = entry.get("photos", {})
    if not photos:
        return False
    # Check if at least thumbnail and hero point to Supabase storage
    for key in ["thumbnail", "hero"]:
        url = photos.get(key, "")
        if url and SUPABASE_PUBLIC_BASE in url:
            return True
    return False


def ensure_bucket_exists():
    """Create the storage bucket if it doesn't exist."""
    headers = {
        "apikey": SUPABASE_SERVICE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
        "Content-Type": "application/json",
    }
    resp = requests.get(
        f"{SUPABASE_URL}/storage/v1/bucket/{BUCKET}",
        headers=headers, timeout=15
    )
    if resp.status_code == 200:
        print(f"Bucket '{BUCKET}' already exists")
        return True

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
        public_url = f"{SUPABASE_PUBLIC_BASE}/{file_path}"
        return public_url
    else:
        print(f"      Upload failed ({resp.status_code}): {resp.text[:200]}")
        return None


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Upload temple photos to Supabase Storage")
    parser.add_argument("--only", nargs="+", metavar="TEMPLE_ID",
                        help="Re-upload specific temple(s) even if already uploaded")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview which temples would be uploaded")
    args = parser.parse_args()

    if not args.dry_run:
        if not GOOGLE_API_KEY:
            print("ERROR: GOOGLE_PLACES_API_KEY not set", file=sys.stderr)
            sys.exit(1)
        if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
            print("ERROR: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY required", file=sys.stderr)
            sys.exit(1)

    # Load lookup data (from fetch step)
    lookup_path = os.path.join(SCRIPT_DIR, "temple_photos_lookup.json")
    with open(lookup_path, "r", encoding="utf-8") as f:
        lookup = json.load(f)
    lookup_dict = {t["temple_id"]: t for t in lookup}

    # Load slugs from CSV
    csv_path = os.path.join(SCRIPT_DIR, "..", "temples_database.csv")
    slug_map = {}
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            slug_map[row["temple_id"]] = row["slug"]

    # Load existing manifest
    manifest = load_manifest()

    print(f"Loaded {len(lookup)} temples from lookup, {len(slug_map)} slugs from CSV")
    print(f"Existing manifest: {len(manifest)} temples")

    # Determine which temples to process
    if args.only:
        only_set = set(args.only)
        to_process = [t for t in lookup if t["temple_id"] in only_set]
        print(f"Processing {len(to_process)} specified temple(s) (--only override)")
    else:
        to_process = []
        skipped = 0
        for t in lookup:
            tid = t["temple_id"]
            if tid in manifest and has_uploaded_photos(manifest[tid]):
                skipped += 1
            else:
                to_process.append(t)
        print(f"Skipping {skipped} temples (already uploaded), processing {len(to_process)} new temples")

    if not to_process:
        print("\nNo new temples to upload. Use --only TEMPLE_ID to re-upload specific temples.")
        return

    print("=" * 70)

    if args.dry_run:
        print("DRY RUN — would upload photos for:")
        for t in to_process:
            print(f"  {t['temple_id']}: {t.get('name_en', '')}")
        return

    # Ensure bucket exists
    if not ensure_bucket_exists():
        sys.exit(1)
    print("=" * 70)

    total_uploaded = 0
    total_failed = 0

    for i, temple in enumerate(to_process, 1):
        temple_id = temple["temple_id"]
        name_en = temple.get("name_en", "")
        slug = slug_map.get(temple_id)
        photos = temple.get("photos", [])

        if not slug:
            print(f"\n[{i}/{len(to_process)}] {temple_id} -- SKIP (no slug)")
            continue

        if not photos:
            print(f"\n[{i}/{len(to_process)}] {temple_id} -- SKIP (no photos)")
            continue

        print(f"\n[{i}/{len(to_process)}] {temple_id} -- {name_en}")
        print(f"  Slug: {slug}")

        uploaded_photos = {}

        # Extract photo references from either list or dict format
        photo_refs = []
        if isinstance(photos, list):
            # Old format: list of dicts with photo_reference
            photo_refs = [p["photo_reference"] for p in photos]
        elif isinstance(photos, dict):
            # New format: dict with URLs containing photo_reference param
            from urllib.parse import urlparse, parse_qs
            seen_refs = []
            for key in ["hero", "gallery_2", "gallery_3"]:
                url = photos.get(key, "")
                if "photo_reference=" in url:
                    ref = parse_qs(urlparse(url).query).get("photo_reference", [None])[0]
                    if ref and ref not in seen_refs:
                        seen_refs.append(ref)
            photo_refs = seen_refs

        if not photo_refs:
            print(f"  ! No photo references found, skipping")
            continue

        # Define download tasks: (label, photo_ref_index, width, storage_filename)
        tasks = [
            ("thumbnail", 0, 400, "thumbnail.jpg"),
            ("hero", 0, 1600, "hero.jpg"),
        ]
        if len(photo_refs) >= 2:
            tasks.append(("gallery_2", 1, 1200, "gallery_2.jpg"))
        if len(photo_refs) >= 3:
            tasks.append(("gallery_3", 2, 1200, "gallery_3.jpg"))

        for label, photo_idx, width, filename in tasks:
            photo_ref = photo_refs[photo_idx]
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
                uploaded_photos[label] = public_url
                total_uploaded += 1
            else:
                print("UPLOAD FAILED")
                total_failed += 1

            # Rate limit
            time.sleep(0.15)

        # Update manifest entry (preserve existing fields like selected_hero)
        if temple_id in manifest:
            manifest[temple_id]["photos"] = uploaded_photos
            manifest[temple_id]["slug"] = slug
        else:
            manifest[temple_id] = {
                "temple_id": temple_id,
                "name_en": name_en,
                "slug": slug,
                "place_id": temple.get("place_id"),
                "rating": temple.get("rating"),
                "total_ratings": temple.get("total_ratings"),
                "selected_hero": "hero",
                "photos": uploaded_photos,
            }

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print(f"  Temples processed: {len(to_process)}")
    print(f"  Images uploaded:   {total_uploaded}")
    print(f"  Failures:          {total_failed}")
    print(f"  Total in manifest: {len(manifest)}")
    print("=" * 70)

    # Save updated manifest
    save_manifest(manifest)


if __name__ == "__main__":
    main()
