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


def build_photo_url(photo_reference, max_width=800):
    """Build a Google Places photo URL from a photo reference."""
    return (
        f"{PLACE_PHOTO_URL}"
        f"?maxwidth={max_width}"
        f"&photo_reference={photo_reference}"
        f"&key={GOOGLE_API_KEY}"
    )


def upload_to_supabase(temple_id, photo_data):
    """Update temple photo data in Supabase."""
    headers = {
        "apikey": SUPABASE_SERVICE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal",
    }
    url = f"{SUPABASE_URL}/rest/v1/temples?temple_id=eq.{temple_id}"
    payload = {"photo_urls": json.dumps(photo_data)}
    resp = requests.patch(url, headers=headers, json=payload, timeout=15)
    return resp.status_code in (200, 204)


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

        photo_count = min(len(photos), args.max_photos)
        photo_data = []
        for j, photo in enumerate(photos[:photo_count]):
            ref = photo.get("photo_reference")
            width = photo.get("width", 0)
            height = photo.get("height", 0)
            attribs = photo.get("html_attributions", [])
            photo_url = build_photo_url(ref)
            photo_data.append({
                "photo_reference": ref,
                "width": width,
                "height": height,
                "url": photo_url,
                "attributions": attribs,
            })

        print(f"  OK {photo_count} photo(s) found (of {len(photos)} total) | rating: {rating} ({total_ratings} reviews)")
        for j, p in enumerate(photo_data):
            print(f"    Photo {j+1}: {p['width']}x{p['height']}")

        found += 1

        # Build manifest entry
        entry = {
            "temple_id": temple_id,
            "name_en": name_en,
            "slug": slug,
            "place_id": place_id,
            "rating": rating,
            "total_ratings": total_ratings,
            "selected_hero": "hero",
            "photos": {
                "thumbnail": f"https://uopxibyowyqirpeuylot.supabase.co/storage/v1/object/public/temple-photos/{slug}/thumbnail.jpg",
                "hero": f"https://uopxibyowyqirpeuylot.supabase.co/storage/v1/object/public/temple-photos/{slug}/hero.jpg",
            },
        }
        # Add gallery photos
        for j, p in enumerate(photo_data):
            key = "hero" if j == 0 else f"gallery_{j+1}"
            entry["photos"][key] = p["url"]

        # Preserve selected_hero if re-processing an existing temple
        if temple_id in manifest and "selected_hero" in manifest[temple_id]:
            entry["selected_hero"] = manifest[temple_id]["selected_hero"]

        manifest[temple_id] = entry

        if args.upload:
            ok = upload_to_supabase(temple_id, photo_data)
            print(f"    Upload: {'OK success' if ok else 'X failed'}")

        # Respect API rate limits
        time.sleep(0.2)

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print(f"  Temples processed: {len(temples)}")
    print(f"  With photos:       {found}")
    print(f"  No photos:         {not_found_count}")
    print(f"  No place ID:       {no_place_id}")
    print(f"  Errors:            {errors}")
    print(f"  Total in manifest: {len(manifest)}")
    print("=" * 70)

    # Save updated manifest
    save_manifest(manifest)

    # Also save raw lookup results for backwards compatibility
    output_file = os.path.join(SCRIPT_DIR, "temple_photos_lookup.json")
    lookup_results = []
    for entry in manifest.values():
        lookup_results.append(entry)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(lookup_results, f, ensure_ascii=False, indent=2)
    print(f"Lookup results also saved to {output_file}")


if __name__ == "__main__":
    main()
