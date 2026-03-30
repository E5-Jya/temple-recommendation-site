#!/usr/bin/env python3
"""
fetch_temple_photos.py
Looks up Google Places photo metadata for temples in the CSV,
and optionally uploads photo URLs to Supabase.

Usage:
  python fetch_temple_photos.py --csv temples_database.csv --lookup-only
  python fetch_temple_photos.py --csv temples_database.csv --upload
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


def find_place_id(name_th, name_en, province_en=""):
    """Search for a place by name to get a proper Places API place_id."""
    # Try Thai name first (more specific), then English
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
    parser.add_argument("--csv", required=True, help="Path to temples_database.csv")
    parser.add_argument("--lookup-only", action="store_true",
                        help="Only look up photo metadata, don't upload")
    parser.add_argument("--upload", action="store_true",
                        help="Upload photo URLs to Supabase")
    parser.add_argument("--max-photos", type=int, default=3,
                        help="Max photos per temple (default: 3)")
    parser.add_argument("--limit", type=int, default=0,
                        help="Limit number of temples to process (0 = all)")
    args = parser.parse_args()

    if not GOOGLE_API_KEY:
        print("ERROR: GOOGLE_PLACES_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    if args.upload and (not SUPABASE_URL or not SUPABASE_SERVICE_KEY):
        print("ERROR: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY required for upload", file=sys.stderr)
        sys.exit(1)

    # Read CSV
    csv_path = args.csv
    if not os.path.isabs(csv_path):
        if not os.path.exists(csv_path):
            parent = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", csv_path)
            if os.path.exists(parent):
                csv_path = parent

    if not os.path.exists(csv_path):
        print(f"ERROR: CSV file not found: {csv_path}", file=sys.stderr)
        sys.exit(1)

    temples = []
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            temples.append(row)

    print(f"Loaded {len(temples)} temples from CSV")
    print("=" * 70)

    if args.limit > 0:
        temples = temples[:args.limit]
        print(f"Processing first {args.limit} temples only")

    found = 0
    not_found = 0
    no_place_id = 0
    errors = 0
    results = []

    for i, temple in enumerate(temples, 1):
        temple_id = temple.get("temple_id", "?")
        name_en = temple.get("name_en", "")
        name_th = temple.get("name_th", "")
        province_en = temple.get("province_en", "")
        hex_cid = temple.get("gmaps_place_id", "").strip()

        display_name = name_en or name_th
        print(f"\n[{i}/{len(temples)}] {temple_id} -- {display_name}")

        # The CSV has hex CIDs, not Places API IDs — search by name instead
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
            not_found += 1
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

        entry = {
            "temple_id": temple_id,
            "name_en": name_en,
            "name_th": name_th,
            "hex_cid": hex_cid,
            "place_id": place_id,
            "matched_name": matched_name,
            "rating": rating,
            "total_ratings": total_ratings,
            "photos": photo_data,
        }
        results.append(entry)

        if args.upload:
            ok = upload_to_supabase(temple_id, photo_data)
            print(f"    Upload: {'OK success' if ok else 'X failed'}")

        # Respect API rate limits
        time.sleep(0.2)

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print(f"  Total temples:    {len(temples)}")
    print(f"  With photos:      {found}")
    print(f"  No photos:        {not_found}")
    print(f"  No place ID:      {no_place_id}")
    print(f"  Errors:           {errors}")
    print("=" * 70)

    # Save results to JSON
    output_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temple_photos_lookup.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\nResults saved to {output_file}")


if __name__ == "__main__":
    main()
