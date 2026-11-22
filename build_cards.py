#!/usr/bin/env python3
"""Build cards.json for couch-tv's `home.custom_cards` from Cinemeta's public Popular feeds.
4 popular movies + 4 popular series, interleaved. Standard library only; no keys."""
import json
import sys
import urllib.request

BASE = "https://v3-cinemeta.strem.io/catalog/{kind}/top.json"
PER_KIND = 4


def fetch(kind):
    req = urllib.request.Request(BASE.format(kind=kind), headers={"User-Agent": "tv-trending-cards"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r).get("metas", [])


def card(meta, label):
    title = (meta.get("name") or "").strip()
    if len(title) > 40:
        title = title[:39].rstrip() + "…"
    if not title:
        return None
    out = {"title": title, "app": "com.nuvio.tv"}
    rating = meta.get("imdbRating")
    if rating:
        out["value"] = ("IMDb " + str(rating))[:24]
    year = str(meta.get("year") or "").split("–")[0][:4]
    out["subtitle"] = (label + (" · " + year if year else ""))[:60]
    poster = meta.get("poster") or ""
    if poster.startswith("https://"):
        out["image"] = poster
    return out


def main():
    movies = [c for c in (card(m, "Trending movie") for m in fetch("movie")) if c][:PER_KIND]
    series = [c for c in (card(m, "Trending series") for m in fetch("series")) if c][:PER_KIND]
    cards = [c for pair in zip(movies, series) for c in pair]
    cards += movies[len(series):] + series[len(movies):]
    if not cards:
        print("no cards built; keeping the old file", file=sys.stderr)
        sys.exit(1)
    with open("cards.json", "w", encoding="utf-8") as f:
        json.dump({"cards": cards[:8]}, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"wrote {len(cards[:8])} cards")


if __name__ == "__main__":
    main()
