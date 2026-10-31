"""
Build poster cache from online sources (Wikipedia / Wikimedia REST API).
Caches real theatrical posters by movie_id and title.
"""

import json
import os
import sys
import time
import urllib.parse
import urllib.request
import pandas as pd

HEADERS = {
    "User-Agent": "CineverseApp/1.0 (https://github.com/MaithiliSawant11/cineverse; contact: maithilis350@gmail.com)"
}

def get_online_poster(title: str, year: str = "") -> str | None:
    """Fetch real movie poster image URL from Wikipedia / Wikimedia."""
    # List of page title candidates to try directly
    clean_title = title.replace("&", "and").strip()
    candidates = []
    
    if year:
        candidates.append(f"{clean_title} ({year} film)")
    candidates.extend([
        f"{clean_title} (film)",
        f"{clean_title} (2009 film)",
        f"{clean_title} (2008 film)",
        f"{clean_title} (1996 film)",
        f"{clean_title} (2012 film)",
        clean_title,
    ])
    
    # 1. Try direct page summary
    for cand in candidates:
        try:
            slug = urllib.parse.quote(cand.replace(" ", "_"))
            url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{slug}"
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=3.0) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                img = data.get("thumbnail", {}).get("source") or data.get("originalimage", {}).get("source")
                # Make sure it's not a generic disambiguation or tiny icon
                if img and ("poster" in img.lower() or "sheet" in img.lower() or "cover" in img.lower() or "film" in cand.lower()):
                    return img
        except Exception:
            pass

    # 2. Search Wikipedia API
    try:
        search_query = f"{title} film {year}".strip()
        search_url = (
            "https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch="
            + urllib.parse.quote(search_query)
            + "&format=json"
        )
        req = urllib.request.Request(search_url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=3.5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            hits = data.get("query", {}).get("search", [])
            for hit in hits[:2]:
                hit_title = hit["title"]
                slug = urllib.parse.quote(hit_title.replace(" ", "_"))
                url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{slug}"
                req2 = urllib.request.Request(url, headers=HEADERS)
                with urllib.request.urlopen(req2, timeout=3.0) as resp2:
                    data2 = json.loads(resp2.read().decode("utf-8"))
                    img = data2.get("thumbnail", {}).get("source") or data2.get("originalimage", {}).get("source")
                    if img:
                        return img
    except Exception:
        pass

    return None

def main():
    print("Loading dataset...")
    df = pd.read_csv("datasets/tmdb_5000_movies.csv")
    
    # Cache path
    cache_path = os.path.join("backend", "models", "poster_cache.json")
    cache = {}
    if os.path.exists(cache_path):
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                cache = json.load(f)
            print(f"Loaded existing cache with {len(cache)} posters.")
        except Exception:
            cache = {}

    # Target movies to pre-populate:
    # 1. Top 150 most popular movies
    popular_df = df.sort_values(by="popularity", ascending=False).head(150)
    
    # 2. Must-have featured and demo movies
    featured_titles = [
        "Avatar", "Iron Man", "Iron Man 2", "Iron Man 3", "The Dark Knight",
        "The Dark Knight Rises", "Inception", "Interstellar", "The Avengers",
        "Guardians of the Galaxy", "Spider-Man 3", "Spider-Man", "Spider-Man 2",
        "Titanic", "The Matrix", "Jurassic Park", "Deadpool", "Whiplash",
        "Frozen", "Mad Max: Fury Road", "The Martian", "Minions",
        "Aliens vs Predator: Requiem", "Aliens", "Falcon Rising",
        "Independence Day", "Titan A.E.", "Batman Begins", "Fight Club",
        "Pulp Fiction", "The Shawshank Redemption", "Forrest Gump",
        "Gladiator", "The Lion King", "Monsters, Inc.", "Finding Nemo",
        "Pirates of the Caribbean: The Curse of the Black Pearl",
        "The Lord of the Rings: The Fellowship of the Ring",
        "The Lord of the Rings: The Two Towers",
        "The Lord of the Rings: The Return of the King",
        "Harry Potter and the Philosopher's Stone",
        "Star Wars", "The Empire Strikes Back", "Return of the Jedi",
        "Back to the Future", "Toy Story", "WALL·E", "Up"
    ]
    
    featured_rows = df[df["title"].isin(featured_titles)]
    all_targets = pd.concat([popular_df, featured_rows]).drop_duplicates(subset=["id"])
    
    print(f"Targeting {len(all_targets)} key movies for real poster caching...")
    
    count = 0
    success = 0
    for _, row in all_targets.iterrows():
        mid = str(int(row["id"]))
        title = str(row["title"])
        year = str(row["release_date"])[:4] if pd.notna(row["release_date"]) else ""
        
        if mid in cache and cache[mid]:
            success += 1
            continue
            
        poster = get_online_poster(title, year)
        if poster:
            cache[mid] = poster
            # Also store title-keyed for fast fallback
            cache[title.lower()] = poster
            success += 1
            print(f"[{success}] {title} ({year}) -> {poster[:75]}...")
        else:
            print(f"[-] Could not find poster for {title}")
            
        count += 1
        # Save every 15 items
        if count % 15 == 0:
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(cache, f, ensure_ascii=False, indent=2)
                
        time.sleep(0.08) # Respectful delay
        
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)
        
    print(f"\nDone! Cached {len(cache)} posters successfully in {cache_path}")

if __name__ == "__main__":
    main()
