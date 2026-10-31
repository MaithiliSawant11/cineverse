"""
Fast Async Poster Cache Builder using httpx and asyncio.
Fetches Wikipedia/Wikimedia poster URLs concurrently with rate limiting.
"""

import asyncio
import json
import os
import urllib.parse
import httpx
import pandas as pd

HEADERS = {
    "User-Agent": "CineverseApp/1.0 (https://github.com/MaithiliSawant11/cineverse; contact: maithilis350@gmail.com)"
}

async def fetch_poster_async(client: httpx.AsyncClient, title: str, year: str) -> str | None:
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
    
    # 1. Direct summary
    for cand in candidates:
        try:
            slug = urllib.parse.quote(cand.replace(" ", "_"))
            url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{slug}"
            resp = await client.get(url, headers=HEADERS, timeout=4.0)
            if resp.status_code == 200:
                data = resp.json()
                img = data.get("thumbnail", {}).get("source") or data.get("originalimage", {}).get("source")
                if img and ("poster" in img.lower() or "sheet" in img.lower() or "cover" in img.lower() or "film" in cand.lower()):
                    return img
        except Exception:
            pass
            
    # 2. Search
    try:
        search_query = f"{title} film {year}".strip()
        search_url = (
            "https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch="
            + urllib.parse.quote(search_query)
            + "&format=json"
        )
        resp = await client.get(search_url, headers=HEADERS, timeout=4.0)
        if resp.status_code == 200:
            hits = resp.json().get("query", {}).get("search", [])
            for hit in hits[:2]:
                slug = urllib.parse.quote(hit["title"].replace(" ", "_"))
                url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{slug}"
                resp2 = await client.get(url, headers=HEADERS, timeout=4.0)
                if resp2.status_code == 200:
                    data2 = resp2.json()
                    img = data2.get("thumbnail", {}).get("source") or data2.get("originalimage", {}).get("source")
                    if img:
                        return img
    except Exception:
        pass
        
    return None

async def main():
    print("Reading movies dataset...", flush=True)
    df = pd.read_csv("datasets/tmdb_5000_movies.csv")
    
    cache_path = os.path.join("backend", "models", "poster_cache.json")
    cache = {}
    if os.path.exists(cache_path):
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                cache = json.load(f)
        except Exception:
            cache = {}
            
    popular_df = df.sort_values(by="popularity", ascending=False).head(160)
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
        "Harry Potter and the Philosopher's Stone", "Back to the Future",
        "Toy Story", "WALL·E", "Up"
    ]
    featured_rows = df[df["title"].isin(featured_titles)]
    targets = pd.concat([popular_df, featured_rows]).drop_duplicates(subset=["id"])
    print(f"Targeting {len(targets)} movies for real poster fetch...", flush=True)
    
    sem = asyncio.Semaphore(5) # max 5 concurrent requests
    
    async with httpx.AsyncClient() as client:
        async def process_movie(row):
            async with sem:
                mid = str(int(row["id"]))
                title = str(row["title"])
                year = str(row["release_date"])[:4] if pd.notna(row["release_date"]) else ""
                
                if mid in cache and cache[mid]:
                    return mid, title, cache[mid]
                    
                poster = await fetch_poster_async(client, title, year)
                await asyncio.sleep(0.05)
                return mid, title, poster
                
        tasks = [process_movie(row) for _, row in targets.iterrows()]
        results = await asyncio.gather(*tasks)
        
        found = 0
        for mid, title, poster in results:
            if poster:
                cache[mid] = poster
                cache[title.lower()] = poster
                found += 1
                
        print(f"Successfully resolved and cached {found} posters!", flush=True)
        
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)
        
    print(f"Saved cache with {len(cache)} entries to {cache_path}", flush=True)

if __name__ == "__main__":
    asyncio.run(main())
