"""
TMDB API helper for CINEVERSE.

Fetches movie posters, ratings, overviews and genres from The Movie Database.
If TMDB_API_KEY is missing or the API call fails, all functions return None
(graceful fallback) — the recommendation engine still works without TMDB data.

TMDB image base URL: https://image.tmdb.org/t/p/w500{poster_path}
"""

import logging
import os
from typing import Optional

import httpx
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

TMDB_API_KEY = os.getenv("TMDB_API_KEY", "")
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500"
TMDB_BACKDROP_BASE = "https://image.tmdb.org/t/p/original"

# Shared async client — reused across requests (connection pooling)
_client: Optional[httpx.AsyncClient] = None


def get_client() -> httpx.AsyncClient:
    global _client
    if _client is None or _client.is_closed:
        _client = httpx.AsyncClient(timeout=8.0)
    return _client


def _has_key() -> bool:
    return bool(TMDB_API_KEY and TMDB_API_KEY != "your_tmdb_api_key_here")


async def fetch_movie_details(tmdb_movie_id: int) -> Optional[dict]:
    """
    Fetch full movie details from TMDB by its numeric movie_id.
    Returns None if TMDB key is missing or the request fails.
    """
    if not _has_key():
        logger.debug("TMDB_API_KEY not set — skipping TMDB fetch for movie %d", tmdb_movie_id)
        return None

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
                "title": data.get("title", ""),
                "overview": data.get("overview", ""),
                "poster_path": f"{TMDB_IMAGE_BASE}{poster}" if poster else None,
                "backdrop_path": f"{TMDB_BACKDROP_BASE}{backdrop}" if backdrop else None,
                "release_date": data.get("release_date", ""),
                "vote_average": data.get("vote_average"),
                "vote_count": data.get("vote_count"),
                "runtime": data.get("runtime"),
                "genres": [g["name"] for g in data.get("genres", [])],
            }
        else:
            logger.warning("TMDB returned %d for movie_id=%d", response.status_code, tmdb_movie_id)
            return None
    except Exception as exc:
        logger.warning("TMDB fetch failed for movie_id=%d: %s", tmdb_movie_id, exc)
        return None


async def fetch_movie_brief(tmdb_movie_id: int) -> Optional[dict]:
    """
    Fetch lightweight movie info (poster + rating) from TMDB.
    Returns None on failure.
    """
    details = await fetch_movie_details(tmdb_movie_id)
    if details is None:
        return None
    return {
        "movie_id": details["movie_id"],
        "title": details["title"],
        "poster_path": details.get("poster_path"),
        "release_date": details.get("release_date"),
        "vote_average": details.get("vote_average"),
    }


async def fetch_all_genres() -> list[dict]:
    """
    Fetch the master genre list from TMDB.
    Returns [] if key is missing or request fails.
    """
    if not _has_key():
        return []

    url = f"{TMDB_BASE_URL}/genre/movie/list"
    params = {"api_key": TMDB_API_KEY, "language": "en-US"}
    try:
        response = await get_client().get(url, params=params)
        if response.status_code == 200:
            return response.json().get("genres", [])
        return []
    except Exception as exc:
        logger.warning("TMDB genre fetch failed: %s", exc)
        return []


async def close_client() -> None:
    """Close the shared httpx client gracefully on app shutdown."""
    global _client
    if _client and not _client.is_closed:
        await _client.aclose()
