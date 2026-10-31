"""
TMDB & Online Media Enrichment Service for CINEVERSE.

Features:
1. High-Performance Poster Caching:
   - Uses pre-built poster_cache.json for top popular and featured movies.
   - Automatically resolves real movie posters from Wikipedia / Wikimedia REST API on-demand.
   - Saves new poster resolutions to poster_cache.json.
2. Rich Metadata Enrichment:
   - Uses movie_metadata.json (overview, release_date, vote_average, runtime, genres) extracted
     directly from the TMDB 5,000 dataset so no movie is missing ratings or overviews.
3. Configurable TMDB API:
   - If TMDB_API_KEY is configured, queries TMDB v3 API.
   - If not set or on network failure, falls back seamlessly to real online posters and dataset metadata.
"""

import asyncio
import json
import logging
import os
import urllib.parse
from pathlib import Path
from typing import Optional

import httpx
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

TMDB_API_KEY = os.getenv("TMDB_API_KEY", "")
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500"
TMDB_BACKDROP_BASE = "https://image.tmdb.org/t/p/original"

# User-Agent for Wikimedia / Wikipedia API compliance
WIKI_HEADERS = {
    "User-Agent": "CineverseApp/1.0 (https://github.com/MaithiliSawant11/cineverse; contact: maithilis350@gmail.com)"
}

# Resolve model and data paths
_MODELS_DIR = Path(__file__).resolve().parent.parent / "models"
_METADATA_FILE = _MODELS_DIR / "movie_metadata.json"
_POSTER_CACHE_FILE = _MODELS_DIR / "poster_cache.json"

# In-memory caches
_metadata: dict[int, dict] = {}
_poster_cache: dict[str, str] = {}
_client: Optional[httpx.AsyncClient] = None


def _load_caches() -> None:
    global _metadata, _poster_cache
    if _METADATA_FILE.exists():
        try:
            with open(_METADATA_FILE, "r", encoding="utf-8") as f:
                raw = json.load(f)
                _metadata = {int(k): v for k, v in raw.items()}
            logger.info("Loaded movie metadata for %d movies", len(_metadata))
        except Exception as e:
            logger.warning("Failed to load movie_metadata.json: %s", e)

    if _POSTER_CACHE_FILE.exists():
        try:
            with open(_POSTER_CACHE_FILE, "r", encoding="utf-8") as f:
                _poster_cache = json.load(f)
            logger.info("Loaded poster cache with %d entries", len(_poster_cache))
        except Exception as e:
            logger.warning("Failed to load poster_cache.json: %s", e)


# Initialize caches on import
_load_caches()


def get_client() -> httpx.AsyncClient:
    global _client
    if _client is None or _client.is_closed:
        _client = httpx.AsyncClient(timeout=6.0)
    return _client


def _has_key() -> bool:
    return bool(TMDB_API_KEY and TMDB_API_KEY != "your_tmdb_api_key_here")


async def _resolve_online_poster(title: str, year: str = "") -> Optional[str]:
    """Dynamically fetch real movie poster from Wikipedia / Wikimedia REST API."""
    if not title:
        return None

    clean_title = title.replace("&", "and").strip()
    candidates = []
    if year:
        candidates.append(f"{clean_title} ({year} film)")
    candidates.extend([
        f"{clean_title} (film)",
        clean_title,
    ])

    client = get_client()
    for cand in candidates:
        try:
            slug = urllib.parse.quote(cand.replace(" ", "_"))
            url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{slug}"
            resp = await client.get(url, headers=WIKI_HEADERS, timeout=3.5)
            if resp.status_code == 200:
                data = resp.json()
                img = data.get("thumbnail", {}).get("source") or data.get("originalimage", {}).get("source")
                if img:
                    return img
        except Exception:
            pass

    # Search fallback
    try:
        search_query = f"{title} film {year}".strip()
        search_url = (
            "https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch="
            + urllib.parse.quote(search_query)
            + "&format=json"
        )
        resp = await client.get(search_url, headers=WIKI_HEADERS, timeout=3.5)
        if resp.status_code == 200:
            hits = resp.json().get("query", {}).get("search", [])
            for hit in hits[:2]:
                slug = urllib.parse.quote(hit["title"].replace(" ", "_"))
                url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{slug}"
                resp2 = await client.get(url, headers=WIKI_HEADERS, timeout=3.5)
                if resp2.status_code == 200:
                    data2 = resp2.json()
                    img = data2.get("thumbnail", {}).get("source") or data2.get("originalimage", {}).get("source")
                    if img:
                        return img
    except Exception:
        pass

    return None


async def get_poster_for_movie(movie_id: int, title: str = "", year: str = "") -> Optional[str]:
    """Retrieve poster URL from cache, online Wikimedia, or None."""
    # 1. Check by movie_id string in cache
    s_id = str(movie_id)
    if s_id in _poster_cache and _poster_cache[s_id]:
        return _poster_cache[s_id]

    # 2. Check by lower-cased title
    if title:
        lower_t = title.lower().strip()
        if lower_t in _poster_cache and _poster_cache[lower_t]:
            return _poster_cache[lower_t]

    # 3. Fetch dynamically from online
    if title:
        poster = await _resolve_online_poster(title, year)
        if poster:
            _poster_cache[s_id] = poster
            _poster_cache[title.lower().strip()] = poster
            return poster

    return None


async def fetch_movie_details(tmdb_movie_id: int, title: str = "") -> Optional[dict]:
    """
    Fetch full movie details.
    Uses TMDB if key configured, otherwise enriches with local metadata and online poster.
    """
    meta = _metadata.get(tmdb_movie_id, {})
    resolved_title = title or meta.get("title", "")
    release_date = meta.get("release_date", "")
    year = release_date[:4] if release_date else ""

    if _has_key():
        url = f"{TMDB_BASE_URL}/movie/{tmdb_movie_id}"
        params = {"api_key": TMDB_API_KEY, "language": "en-US"}
        try:
            response = await get_client().get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                poster = data.get("poster_path")
                backdrop = data.get("backdrop_path")
                return {
                    "movie_id": tmdb_movie_id,
                    "title": data.get("title", resolved_title),
                    "overview": data.get("overview") or meta.get("overview", ""),
                    "poster_path": f"{TMDB_IMAGE_BASE}{poster}" if poster else await get_poster_for_movie(tmdb_movie_id, resolved_title, year),
                    "backdrop_path": f"{TMDB_BACKDROP_BASE}{backdrop}" if backdrop else None,
                    "release_date": data.get("release_date") or release_date,
                    "vote_average": data.get("vote_average") or meta.get("vote_average"),
                    "vote_count": data.get("vote_count") or meta.get("vote_count"),
                    "runtime": data.get("runtime") or meta.get("runtime"),
                    "genres": [g["name"] for g in data.get("genres", [])] or meta.get("genres", []),
                }
        except Exception as exc:
            logger.warning("TMDB request failed for movie %d: %s", tmdb_movie_id, exc)

    # Online / Local enrichment
    poster_url = await get_poster_for_movie(tmdb_movie_id, resolved_title, year)
    return {
        "movie_id": tmdb_movie_id,
        "title": resolved_title,
        "overview": meta.get("overview", ""),
        "poster_path": poster_url,
        "backdrop_path": None,
        "release_date": release_date,
        "vote_average": meta.get("vote_average"),
        "vote_count": meta.get("vote_count"),
        "runtime": meta.get("runtime"),
        "genres": meta.get("genres", []),
    }


async def fetch_movie_brief(tmdb_movie_id: int, title: str = "") -> Optional[dict]:
    """Fetch lightweight movie info (poster, release date, rating)."""
    meta = _metadata.get(tmdb_movie_id, {})
    resolved_title = title or meta.get("title", "")
    release_date = meta.get("release_date", "")
    year = release_date[:4] if release_date else ""

    poster_url = await get_poster_for_movie(tmdb_movie_id, resolved_title, year)
    return {
        "movie_id": tmdb_movie_id,
        "title": resolved_title,
        "poster_path": poster_url,
        "release_date": release_date,
        "vote_average": meta.get("vote_average"),
    }


async def fetch_all_genres() -> list[dict]:
    """Fetch genres list from TMDB or return standard genres from dataset."""
    if _has_key():
        url = f"{TMDB_BASE_URL}/genre/movie/list"
        params = {"api_key": TMDB_API_KEY, "language": "en-US"}
        try:
            response = await get_client().get(url, params=params)
            if response.status_code == 200:
                return response.json().get("genres", [])
        except Exception:
            pass

    # Extract distinct genres from local metadata
    all_genres = set()
    for m in _metadata.values():
        for g in m.get("genres", []):
            if g:
                all_genres.add(g)
    return [{"id": idx + 1, "name": name} for idx, name in enumerate(sorted(all_genres))]


async def close_client() -> None:
    """Close the shared httpx client gracefully on app shutdown."""
    global _client
    if _client and not _client.is_closed:
        await _client.aclose()
