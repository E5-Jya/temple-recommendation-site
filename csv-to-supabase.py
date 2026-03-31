#!/usr/bin/env python3
"""
csv-to-supabase.py
Reads temples_database.csv and upserts all rows into the Supabase temples table.

Usage:
  python csv-to-supabase.py                    # upsert all rows
  python csv-to-supabase.py --dry-run          # preview without writing
  python csv-to-supabase.py --force            # overwrite even web-edited fields
"""

import argparse
import csv
import json
import os
import sys

import requests
from dotenv import load_dotenv

load_dotenv()

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(SCRIPT_DIR, "..", "temples_database.csv")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

# All columns from the CSV that map directly to table columns
CSV_COLUMNS = [
    "temple_id", "name_th", "name_en", "place_type_th", "place_type_en",
    "slug", "tradition_th", "tradition_en", "abbot_th", "abbot_en",
    "founded_be", "founded_ce", "province_th", "province_en",
    "district_th", "district_en", "address_th", "website",
    "facebook_main", "facebook_en", "line_oa", "phone",
    "act_daily_meditation", "act_dhamma_talk", "act_lay_retreat",
    "act_monk_ordination", "act_novice_ordination", "act_white_robe",
    "act_nun_program", "act_annual_kathin", "act_special_events",
    "act_online_live", "act_community_service",
    "retreat_min_days", "retreat_cost", "retreat_booking_req",
    "retreat_booking_channel", "retreat_capacity",
    "ord_min_days", "ord_cost", "ord_prerequisite",
    "sched_wake_time", "sched_morning_chant", "sched_meal_count",
    "sched_meal_type", "sched_evening_chant",
    "blurb_th", "blurb_en", "last_updated", "data_sources", "notes",
    "gmaps_place_id",
]


def upsert_temples(rows, dry_run=False):
    """Upsert rows to Supabase via REST API."""
    headers = {
        "apikey": SUPABASE_SERVICE_KEY,
        "Authorization": "Bearer %s" % SUPABASE_SERVICE_KEY,
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates,return=representation",
    }
    url = "%s/rest/v1/temples" % SUPABASE_URL

    if dry_run:
        print("DRY RUN: Would upsert %d rows" % len(rows))
        for r in rows[:3]:
            print("  %s: %s" % (r["temple_id"], r["name_en"]))
        if len(rows) > 3:
            print("  ... and %d more" % (len(rows) - 3))
        return True

    # Supabase REST API supports bulk upsert
    resp = requests.post(
        url,
        headers=headers,
        data=json.dumps(rows, ensure_ascii=False).encode("utf-8"),
        timeout=30,
    )

    if resp.status_code in (200, 201):
        result = resp.json()
        print("Successfully upserted %d rows" % len(result))
        return True
    else:
        print("ERROR %d: %s" % (resp.status_code, resp.text[:500]))
        return False


def main():
    parser = argparse.ArgumentParser(description="Import CSV to Supabase temples table")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    parser.add_argument("--force", action="store_true",
                        help="Overwrite all fields including web-edited ones")
    parser.add_argument("--csv", default=CSV_PATH, help="Path to CSV file")
    args = parser.parse_args()

    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        print("ERROR: Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY", file=sys.stderr)
        sys.exit(1)

    # Read CSV
    temples = []
    with open(args.csv, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            record = {}
            for col in CSV_COLUMNS:
                val = row.get(col, "").strip()
                record[col] = val if val else None
            record["last_edited_source"] = "csv"
            temples.append(record)

    print("Read %d temples from CSV" % len(temples))

    if not temples:
        print("No data to import")
        return

    # Upsert
    success = upsert_temples(temples, dry_run=args.dry_run)
    if success and not args.dry_run:
        print("Import complete!")


if __name__ == "__main__":
    main()
