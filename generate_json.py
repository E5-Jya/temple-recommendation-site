#!/usr/bin/env python3
"""
generate_json.py
Reads temples_database.csv + photo_manifest.json and generates:
  - temples-directory.json
  - temples-recommendation.json
  - temples-detail.json
"""

import csv
import json
import os
import sys
import hashlib

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(SCRIPT_DIR, "..", "temples_database.csv")
MANIFEST_PATH = os.path.join(SCRIPT_DIR, "photo_manifest.json")

GRADIENT_PALETTES = [
    ("#1A3A2A", "#2D5C3E"),
    ("#0B3D2E", "#1A6644"),
    ("#1A2A4A", "#2C4A80"),
    ("#2A1A3A", "#4A2D5C"),
    ("#3A2A1A", "#5C4A2D"),
    ("#1A3A3A", "#2D5C5C"),
    ("#2A3A1A", "#4A5C2D"),
    ("#3A1A2A", "#5C2D4A"),
    ("#1A2A2A", "#2D4A4A"),
    ("#2A2A3A", "#4A4A5C"),
]


def get_gradient(temple_id):
    idx = int(hashlib.md5(temple_id.encode()).hexdigest(), 16) % len(GRADIENT_PALETTES)
    c1, c2 = GRADIENT_PALETTES[idx]
    return "linear-gradient(135deg, %s, %s)" % (c1, c2)


def yn(val):
    return val.strip().upper() == "Y" if val else False


def safe(val, default=""):
    return val.strip() if val and val.strip() else default


def truncate_blurb(text, max_len=200):
    if len(text) <= max_len:
        return text
    cut = text[:max_len]
    space = cut.rfind(" ")
    if space > max_len // 2:
        cut = cut[:space]
    return cut + "..."


def build_chips(row):
    chips = []
    if yn(row.get("act_lay_retreat", "")):
        chips.append("คอร์สปฏิบัติ")
    if yn(row.get("act_monk_ordination", "")):
        chips.append("บวชพระ")
    if yn(row.get("act_online_live", "")):
        chips.append("ออนไลน์")
    if yn(row.get("act_nun_program", "")) or yn(row.get("act_white_robe", "")):
        chips.append("ผู้หญิง/แม่ชี")
    trad = safe(row.get("tradition_th", ""))
    if "ธรรมยุต" in trad:
        chips.append("ธรรมยุต")
    elif "เถรวาท" in trad:
        chips.append("เถรวาท")
    return chips


def build_tags(row):
    tags = []
    province = safe(row.get("province_en", ""))
    is_bkk = province == "Bangkok"
    if is_bkk:
        tags.append("bkk")
    else:
        tags.append("upcountry")
    if yn(row.get("act_lay_retreat", "")):
        tags.append("retreat")
    if yn(row.get("act_monk_ordination", "")):
        tags.append("ordain")
    if yn(row.get("act_online_live", "")):
        tags.append("online")
    if yn(row.get("act_nun_program", "")) or yn(row.get("act_white_robe", "")):
        tags.append("women")
    trad = safe(row.get("tradition_en", "")).lower()
    name = safe(row.get("name_en", "")).lower()
    if "forest" in trad or "forest" in name:
        tags.append("forest")
    return tags


def build_scores(row):
    scores = {}
    province = safe(row.get("province_en", ""))
    is_bkk = province == "Bangkok"

    if is_bkk:
        scores["location_bkk"] = 3
    else:
        scores["location_upcountry"] = 3
    scores["location_any"] = 2

    min_days_str = safe(row.get("retreat_min_days", ""), "0")
    try:
        min_days = float(min_days_str)
    except ValueError:
        min_days = 0

    if min_days <= 0.5:
        scores["duration_halfday"] = 3
        scores["duration_weekend"] = 3
        scores["duration_week"] = 3
    elif min_days <= 1:
        scores["duration_halfday"] = 3
        scores["duration_weekend"] = 3
        scores["duration_week"] = 3
    elif min_days <= 3:
        scores["duration_weekend"] = 3
        scores["duration_week"] = 3
        scores["duration_long"] = 3
    elif min_days <= 7:
        scores["duration_week"] = 3
        scores["duration_long"] = 3
    else:
        scores["duration_long"] = 3

    cost = safe(row.get("retreat_cost", "")).lower()
    if cost in ("free", "ฟรี", "ฟรี (บริจาคตามศรัทธา)"):
        scores["budget_free"] = 3
        scores["budget_any"] = 2
    else:
        scores["budget_mid"] = 2
        scores["budget_any"] = 2

    if yn(row.get("act_daily_meditation", "")):
        scores["activity_meditation"] = 3
    if yn(row.get("act_dhamma_talk", "")):
        scores["activity_dhamma_talk"] = 3
    if yn(row.get("act_monk_ordination", "")):
        scores["activity_ordain"] = 3
    if not is_bkk:
        trad_en = safe(row.get("tradition_en", "")).lower()
        scores["activity_nature"] = 3 if "forest" in trad_en else 2

    scores["profile_beginner"] = 3
    if min_days >= 5:
        scores["profile_intermediate"] = 3
        scores["profile_beginner"] = 2
    if yn(row.get("act_white_robe", "")) or yn(row.get("act_nun_program", "")):
        scores["profile_women"] = 3
    if is_bkk and min_days <= 1:
        scores["profile_family"] = 2

    return scores


def build_whys(row):
    whys = []
    cost = safe(row.get("retreat_cost", ""))
    if cost.lower() in ("free", "ฟรี", "ฟรี (บริจาคตามศรัทธา)"):
        whys.append("ฟรีทุกกิจกรรม บริจาคตามศรัทธา")

    min_days = safe(row.get("retreat_min_days", ""), "0")
    whys.append("เปิดรับผู้ปฏิบัติธรรม ขั้นต่ำ %s วัน" % min_days)

    if yn(row.get("act_monk_ordination", "")):
        whys.append("รับบวชพระ/สามเณร")
    if yn(row.get("act_online_live", "")):
        whys.append("ถ่ายทอดสดออนไลน์")

    province = safe(row.get("province_en", ""))
    if province == "Bangkok":
        whys.append("เดินทางสะดวก ในกรุงเทพฯ")
    else:
        whys.append("สงบ ไกลเมือง เหมาะปฏิบัติจริงจัง")

    if yn(row.get("act_white_robe", "")) or yn(row.get("act_nun_program", "")):
        whys.append("เปิดรับสตรี/แม่ชี")

    return whys[:4]


ACTIVITY_MAP = [
    ("act_daily_meditation", "นั่งสมาธิประจำวัน"),
    ("act_dhamma_talk", "บรรยายธรรม"),
    ("act_lay_retreat", "คอร์สปฏิบัติ"),
    ("act_monk_ordination", "บวชพระ"),
    ("act_novice_ordination", "บวชสามเณร"),
    ("act_white_robe", "บวชชีพราหมณ์"),
    ("act_nun_program", "โครงการแม่ชี"),
    ("act_annual_kathin", "ทอดกฐิน"),
    ("act_special_events", "กิจกรรมพิเศษ"),
    ("act_online_live", "ถ่ายทอดสดออนไลน์"),
    ("act_community_service", "บริการสังคม"),
]


def main():
    temples = []
    with open(CSV_PATH, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            temples.append(row)
    print("Loaded %d temples from CSV" % len(temples))

    manifest = {}
    if os.path.exists(MANIFEST_PATH):
        with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
            for entry in json.load(f):
                manifest[entry["temple_id"]] = entry
        print("Loaded %d entries from photo manifest" % len(manifest))

    directory_data = []
    recommendation_data = []
    detail_data = {}

    for row in temples:
        tid = row["temple_id"]
        slug = safe(row.get("slug", ""))
        province_en = safe(row.get("province_en", ""))
        is_bkk = province_en == "Bangkok"
        cost_raw = safe(row.get("retreat_cost", ""))
        is_free = cost_raw.lower() in ("free", "ฟรี", "ฟรี (บริจาคตามศรัทธา)")

        m = manifest.get(tid, {})
        photos = m.get("photos", {})
        thumbnail_url = photos.get("thumbnail", "")
        hero_url = photos.get("hero", "")
        selected_hero = m.get("selected_hero")

        blurb_th = safe(row.get("blurb_th", ""))

        # ── DIRECTORY ──
        directory_data.append({
            "id": tid,
            "slug": slug,
            "thumbnailUrl": thumbnail_url if selected_hero else "",
            "nameTh": safe(row.get("name_th", "")),
            "nameEn": safe(row.get("name_en", "")),
            "placeType": safe(row.get("place_type_th", "")),
            "province": safe(row.get("province_th", "")),
            "district": safe(row.get("district_th", "")),
            "tradition": "%s – %s" % (safe(row.get("tradition_th", "")), safe(row.get("tradition_en", ""))),
            "cost": "free" if is_free else "paid",
            "tags": build_tags(row),
            "actRetreats": yn(row.get("act_lay_retreat", "")),
            "actOrdain": yn(row.get("act_monk_ordination", "")),
            "actOnline": yn(row.get("act_online_live", "")),
            "actWomen": yn(row.get("act_white_robe", "")) or yn(row.get("act_nun_program", "")),
            "isFree": is_free,
            "isBKK": is_bkk,
            "abbotTh": safe(row.get("abbot_th", "")),
            "blurb": truncate_blurb(blurb_th),
            "costLabel": "ฟรี" if is_free else cost_raw,
            "costClass": "chip-cost" if is_free else "chip-cost-paid",
            "chips": build_chips(row),
            "gradient": get_gradient(tid),
            "link": "temple-detail.html?id=%s" % tid,
        })

        # ── RECOMMENDATION ──
        recommendation_data.append({
            "id": tid,
            "nameTh": safe(row.get("name_th", "")),
            "nameEn": safe(row.get("name_en", "")),
            "province": safe(row.get("province_th", "")),
            "district": safe(row.get("district_th", "")),
            "scores": build_scores(row),
            "whys": build_whys(row),
            "link": "temple-detail.html?id=%s" % tid,
        })

        # ── DETAIL ──
        detail_data[tid] = {
            "slug": slug,
            "heroUrl": hero_url if selected_hero else "",
            "nameTh": safe(row.get("name_th", "")),
            "nameEn": safe(row.get("name_en", "")),
            "province": safe(row.get("province_th", "")),
            "district": safe(row.get("district_th", "")),
            "tradition": safe(row.get("tradition_th", "")),
            "abbot": safe(row.get("abbot_th", "")),
            "blurbTh": blurb_th,
            "blurbEn": safe(row.get("blurb_en", "")),
            "activities": [
                {"name": label, "available": yn(row.get(field, ""))}
                for field, label in ACTIVITY_MAP
            ],
            "retreatInfo": {
                "minDays": safe(row.get("retreat_min_days", ""), "N/A"),
                "cost": safe(row.get("retreat_cost", ""), "N/A"),
                "bookingReq": yn(row.get("retreat_booking_req", "")),
                "bookingChannel": safe(row.get("retreat_booking_channel", ""), "-"),
                "capacity": safe(row.get("retreat_capacity", ""), "ไม่ระบุ"),
            },
            "ordinationInfo": {
                "minDays": safe(row.get("ord_min_days", ""), "N/A"),
                "cost": safe(row.get("ord_cost", ""), "N/A"),
                "prerequisite": safe(row.get("ord_prerequisite", ""), "-"),
            },
            "schedule": {
                "wake": safe(row.get("sched_wake_time", ""), "N/A"),
                "morningChant": safe(row.get("sched_morning_chant", ""), "N/A"),
                "mealCount": safe(row.get("sched_meal_count", ""), "N/A"),
                "mealType": safe(row.get("sched_meal_type", ""), "N/A"),
                "eveningChant": safe(row.get("sched_evening_chant", ""), "N/A"),
            },
            "contact": {
                "website": safe(row.get("website", "")),
                "facebook": safe(row.get("facebook_main", "")),
                "facebookEn": safe(row.get("facebook_en", "")),
                "line": safe(row.get("line_oa", "")),
                "phone": safe(row.get("phone", "")),
                "address": safe(row.get("address_th", "")),
            },
            "gradient": get_gradient(tid),
            "foundedBe": safe(row.get("founded_be", ""), "-"),
            "foundedCe": safe(row.get("founded_ce", ""), "-"),
            "lastUpdated": safe(row.get("last_updated", ""), "-"),
        }

    out_dir = SCRIPT_DIR
    with open(os.path.join(out_dir, "temples-directory.json"), "w", encoding="utf-8") as f:
        json.dump(directory_data, f, ensure_ascii=False, indent=2)
    print("  temples-directory.json: %d temples" % len(directory_data))

    with open(os.path.join(out_dir, "temples-recommendation.json"), "w", encoding="utf-8") as f:
        json.dump(recommendation_data, f, ensure_ascii=False, indent=2)
    print("  temples-recommendation.json: %d temples" % len(recommendation_data))

    with open(os.path.join(out_dir, "temples-detail.json"), "w", encoding="utf-8") as f:
        json.dump(detail_data, f, ensure_ascii=False, indent=2)
    print("  temples-detail.json: %d temples" % len(detail_data))

    print("\nDone!")


if __name__ == "__main__":
    main()
