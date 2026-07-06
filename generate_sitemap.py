#!/usr/bin/env python3
"""Generate sitemap.xml from temples-directory.json."""

import json
from datetime import date
from pathlib import Path

BASE_URL = "https://pakjai.co"
TODAY = date.today().isoformat()

STATIC_PAGES = [
    ("", "weekly", "1.0"),
    ("places-recommended.html", "weekly", "0.9"),
    ("places-all.html", "weekly", "0.9"),
    ("recommendation.html", "monthly", "0.8"),
    ("report.html", "monthly", "0.4"),
    ("recommend.html", "monthly", "0.4"),
    ("articles/", "weekly", "0.7"),
    ("articles/sathan-thi-phak-phon-chai-nai-krungthep.html", "monthly", "0.6"),
    ("articles/7-meditation-places-for-beginners.html", "monthly", "0.6"),
    ("articles/5-meditation-places-for-foreign-friends.html", "monthly", "0.6"),
    ("articles/sathan-thi-pati-tham-nakhon-ratchasima.html", "monthly", "0.6"),
    ("articles/sathan-thi-pati-tham-chiang-mai.html", "monthly", "0.6"),
]

def main():
    script_dir = Path(__file__).parent
    with open(script_dir / "temples-directory.json", encoding="utf-8") as f:
        temples = json.load(f)

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]

    for path, freq, priority in STATIC_PAGES:
        loc = f"{BASE_URL}/" if not path else f"{BASE_URL}/{path}"
        lines.append(f"  <url>")
        lines.append(f"    <loc>{loc}</loc>")
        lines.append(f"    <lastmod>{TODAY}</lastmod>")
        lines.append(f"    <changefreq>{freq}</changefreq>")
        lines.append(f"    <priority>{priority}</priority>")
        lines.append(f"  </url>")

    for temple in temples:
        temple_id = temple["id"]
        lines.append(f"  <url>")
        lines.append(f"    <loc>{BASE_URL}/detail.html?id={temple_id}</loc>")
        lines.append(f"    <lastmod>{TODAY}</lastmod>")
        lines.append(f"    <changefreq>monthly</changefreq>")
        lines.append(f"    <priority>0.7</priority>")
        lines.append(f"  </url>")

    lines.append("</urlset>")
    lines.append("")

    sitemap_path = script_dir / "sitemap.xml"
    sitemap_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Generated {sitemap_path} with {len(STATIC_PAGES) + len(temples)} URLs")

if __name__ == "__main__":
    main()
