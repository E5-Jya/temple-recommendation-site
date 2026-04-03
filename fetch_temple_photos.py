#!/usr/bin/env python3
"""
fetch_temple_photos.py
Looks up Google Places photo metadata for temples in the CSV,
and optionally uploads photo URLs to Supabase.

Automatically skips temples already in photo_manifest.json unless
--only is used to re-process specific temples.

Usage:
  python fetch_temple_photos.py                          # process new temples only
  python fetch_temple_photos.py --only TH-BKK-001       # re-process specific temple(s)
  python fetch_temple_photos.py --upload                 # also upload to Supabase
  python fetch_temple_photos.py --dry-run                # preview without fetching
"""

import argparse
import csv
import json
import os
import sys
import time

import requests
from dotenv import load_dotenv

load_dotenv()

# Fix Windows console encoding for Thai text
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

GOOGLE_API_KEY = os.environ.get("GOOGLE_PLACES_API_KEY")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

PLACE_DETAILS_URL = "https://maps.googleapis.com/maps/api/place/details/json"
PLACE_PHOTO_URL = "https://maps.googleapis.com/maps/api/place/photo"
TEXT_SEARCH_URL = "https://maps.googleapis.com/maps/api/place/textsearch/json"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MANIFEST_PATH = os.path.join(SCRIPT_DIR, "photo_manifest.json")
DEFAULT_CSV = os.path.join(SCRIPT_DIR, "..", "temples_database.csv")


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


def find_place_id(name_th, name_en, province_en=""):
    """Search for a place by name to get a proper Places API place_id."""
    for query in [name_th, name_en]:
        if not query:
            continue
        search_query = f"{query} {province_en} Thailand" if province_en else f"{query} Thailand"
        params = {
            "query": search_query,
            "key": GOOGLE_API_KEY,
        }
        resp = requests.get(TEXT_SEARCH_URL, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        if data.get("status") == "OK" and data.get("results"):
            result = data["results"][0]
            return result.get("place_id"), result.get("name")
    return None, None


def get_place_details(place_id):
    """Fetch place details including photos from Google Places API."""
    params = {
        "place_id": place_id,
        "fields": "name,formatted_address,photos,rating,user_ratings_total,geometry",
        "key": GOOGLE_API_KEY,
    }
    resp = requests.get(PLACE_DETAILS_URL, params=params, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    if data.get("status") != "OK":
        return None, data.get("status"), data.get("error_message", "")
    return data.get("result"), "OK", ""


SUPABASE_STORAGE_BASE = "https://uopxibyowyqirpeuylot.supabase.co/storage/v1/object/public/temple-photos"

# Photo sizes: key -> (max_width, filename)
PHOTO_SIZES = {
    "thumbnail": (400, "thumbnail.jpg"),
    "hero": (1600, "hero.jpg"),
    "gallery": (1200, None),  # gallery_2.jpg, gallery_3.jpg etc.
}


def download_photo(photo_reference, max_width=800):
    """Download a photo from Google Places API, return bytes."""
    url = (
        f"{PLACE_PHOTO_URL}"
        f"?maxwidth={max_width}"
        f"&photo_reference={photo_reference}"
        f"&key={GOOGLE_API_KEY}"
    )
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    if resp.headers.get("content-type", "").startswith("image"):
        return resp.content
    return None


def upload_to_supabase_storage(slug, filename, image_bytes):
    """Upload image bytes to Supabase Storage bucket 'temple-photos'.
    Returns the public URL on success, None on failure."""
    storage_path = f"{slug}/{filename}"
    upload_url = f"{SUPABASE_URL}/storage/v1/object/temple-photos/{storage_path}"
    headers = {
        "apikey": SUPABASE_SERVICE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
        "Content-Type": "image/jpeg",
        "x-upsert": "true",  # overwrite if exists
    }
    resp = requests.post(upload_url, headers=headers, data=image_bytes, timeout=30)
    if resp.status_code in (200, 201):
        return f"{SUPABASE_STORAGE_BASE}/{storage_path}"
    else:
        print(f"    ! Upload failed for {storage_path}: {resp.status_code} {resp.text[:200]}")
        return None


def validate_manifest_urls(entry):
    """Safety check: ensure no Google API URLs (with exposed keys) in manifest.
    Returns True if all URLs are clean Supabase URLs."""
    photos = entry.get("photos", {})
    for key, url in photos.items():
        if "googleapis.com" in url or "key=" in url:
            print(f"  WARNING: {key} still has a Google API URL — skipping manifest save for this temple")
            return False
    return True


def main():
    parser = argparse.ArgumentParser(description="Fetch Google Places photos for temples")
    parser.add_argument("--csv", default=DEFAULT_CSV, help="Path to temples_database.csv")
    parser.add_argument("--only", nargs="+", metavar="TEMPLE_ID",
                        help="Re-process specific temple(s) even if already in manifest")
    parser.add_argument("--upload", action="store_true",
                        help="Upload photo URLs to Supabase")
    parser.add_argument("--max-photos", type=int, default=3,
                        help="Max photos per temple (default: 3)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview which temples would be processed")
    args = parser.parse_args()

    if not args.dry_run and not GOOGLE_API_KEY:
        print("ERROR: GOOGLE_PLACES_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    if args.upload and (not SUPABASE_URL or not SUPABASE_SERVICE_KEY):
        print("ERROR: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY required for upload", file=sys.stderr)
        sys.exit(1)

    # Read CSV
    csv_path = args.csv
    if not os.path.isabs(csv_path):
        if not os.path.exists(csv_path):
            parent = os.path.join(SCRIPT_DIR, "..", csv_path)
            if os.path.exists(parent):
                csv_path = parent

    if not os.path.exists(csv_path):
        print(f"ERROR: CSV file not found: {csv_path}", file=sys.stderr)
        sys.exit(1)

    all_temples = []
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            all_temples.append(row)

    print(f"Loaded {len(all_temples)} temples from CSV")

    # Load existing manifest
    manifest = load_manifest()
    existing_ids = set(manifest.keys())

    # Determine which temples to process
    if args.only:
        # --only override: process specified temples regardless of manifest
        only_set = set(args.only)
        temples = [t for t in all_temples if t.get("temple_id") in only_set]
        not_found = only_set - {t.get("temple_id") for t in temples}
        if not_found:
            print(f"WARNING: temple IDs not found in CSV: {', '.join(not_found)}")
        print(f"Processing {len(temples)} specified temple(s) (--only override)")
    else:
        # Auto-skip temples already in manifest
        temples = [t for t in all_temples if t.get("temple_id") not in existing_ids]
        skipped = len(all_temples) - len(temples)
        print(f"Skipping {skipped} temples (already have photos), processing {len(temples)} new temples")

    if not temples:
        print("\nNo new temples to process. Use --only TEMPLE_ID to re-process specific temples.")
        return

    print("=" * 70)

    if args.dry_run:
        print("DRY RUN — would process these temples:")
        for t in temples:
            print(f"  {t.get('temple_id')}: {t.get('name_en', '')}")
        return

    found = 0
    not_found_count = 0
    no_place_id = 0
    errors = 0

    for i, temple in enumerate(temples, 1):
        temple_id = temple.get("temple_id", "?")
        name_en = temple.get("name_en", "")
        name_th = temple.get("name_th", "")
        province_en = temple.get("province_en", "")
        slug = temple.get("slug", "")

        display_name = name_en or name_th
        print(f"\n[{i}/{len(temples)}] {temple_id} -- {display_name}")

        try:
            place_id, matched_name = find_place_id(name_th, name_en, province_en)
        except Exception as e:
            print(f"  X Search error: {e}")
            errors += 1
            continue

        if not place_id:
            print("  ! Could not find place via text search")
            no_place_id += 1
            continue

        print(f"  Found: {matched_name} (place_id: {place_id})")

        try:
            result, status, err_msg = get_place_details(place_id)
        except Exception as e:
            print(f"  X Request error: {e}")
            errors += 1
            continue

        if not result:
            print(f"  X API status: {status} -- {err_msg}")
            errors += 1
            continue

        photos = result.get("photos", [])
        rating = result.get("rating", "N/A")
        total_ratings = result.get("user_ratings_total", 0)

        if not photos:
            print(f"  ! No photos available (rating: {rating}, reviews: {total_ratings})")
            not_found_count += 1
            continue

        print(f"  Rating: {rating} ({total_ratings} reviews), {len(photos)} photos available")

        # Take up to max_photos photo references
        selected_refs = [p["photo_reference"] for p in photos[:args.max_photos]]

        # Download and upload each photo
        photo_urls = {}
        all_uploaded = True

        for idx, ref in enumerate(selected_refs):
            if idx == 0:
                # First photo -> thumbnail + hero
                for size_key, max_w in [("thumbnail", 400), ("hero", 1600)]:
                    print(f"  Downloading {size_key} ({max_w}px)...")
                    img_bytes = download_photo(ref, max_width=max_w)
                    if not img_bytes:
                        print(f"    ! Failed to download {size_key}")
                        all_uploaded = False
                        continue
                    supabase_url = upload_to_supabase_storage(slug, f"{size_key}.jpg", img_bytes)
                    if supabase_url:
                        photo_urls[size_key] = supabase_url
                        print(f"    Uploaded {size_key}")
                    else:
                        all_uploaded = False
            else:
                # Additional photos -> gallery_2, gallery_3, etc.
                gallery_key = f"gallery_{idx + 1}"
                print(f"  Downloading {gallery_key} (1200px)...")
                img_bytes = download_photo(ref, max_width=1200)
                if not img_bytes:
                    print(f"    ! Failed to download {gallery_key}")
                    all_uploaded = False
                    continue
                supabase_url = upload_to_supabase_storage(slug, f"{gallery_key}.jpg", img_bytes)
                if supabase_url:
                    photo_urls[gallery_key] = supabase_url
                    print(f"    Uploaded {gallery_key}")
                else:
                    all_uploaded = False

            time.sleep(0.3)  # rate limit

        if not photo_urls:
            print("  ! No photos could be uploaded")
            errors += 1
            continue

        # Build manifest entry
        entry = {
            "temple_id": temple_id,
            "name_en": name_en,
            "slug": slug,
            "place_id": place_id,
            "rating": rating,
            "total_ratings": total_ratings,
            "photos": photo_urls,
        }

        # Preserve existing selected_hero if re-processing
        if temple_id in manifest and "selected_hero" in manifest[temple_id]:
            entry["selected_hero"] = manifest[temple_id]["selected_hero"]

        # SAFETY: never save Google API URLs to manifest
        if not validate_manifest_urls(entry):
            print(f"  BLOCKED: refusing to save Google API URLs for {temple_id}")
            errors += 1
            continue

        manifest[temple_id] = entry
        found += 1

        # Save manifest after each successful temple (in case of crash)
        save_manifest(manifest)

        if not all_uploaded:
            print(f"  Partial upload for {temple_id} — some photos may be missing")

    # Final summary
    print("\n" + "=" * 70)
    print(f"DONE: {found} temples processed, {not_found_count} not found, {errors} errors")
    print(f"Manifest: {MANIFEST_PATH} ({len(manifest)} total temples)")


if __name__ == "__main__":
    main()