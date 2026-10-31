"""
CINEVERSE FastAPI Backend — main application entry point.

Architecture:
- The recommender service (ML model) is loaded ONCE at startup via lifespan.
- Every request reuses the in-memory model — no repeated pickle loading.
- TMDB API enriches responses with posters/ratings when a key is available.
- CORS is configured via the ALLOWED_ORIGINS environment variable.
"""

import logging
import os
from contextlib import asynccontextmanager
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from .models import (
    HealthResponse,
    MovieBrief,
    MovieDetail,
    RecommendationItem,
    RecommendationResponse,
    SearchResponse,
)
from .recommender import recommender
from . import tmdb as tmdb_client

# ── Load .env (local dev only; Render injects env vars directly) ───────────
load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(levelname)s │ %(name)s │ %(message)s")
logger = logging.getLogger(__name__)


# ── Lifespan: load model on startup, close HTTP client on shutdown ─────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP
    logger.info("🚀 CINEVERSE backend starting …")
    recommender.load()   # Loads all 3 pickle files; ~1-2 s for the 176 MB similarity matrix
    logger.info("✅ Model ready — %d movies loaded", recommender.movie_count)
    yield
    # SHUTDOWN
    await tmdb_client.close_client()
    logger.info("👋 CINEVERSE backend shut down")


# ── FastAPI app ────────────────────────────────────────────────────────────
app = FastAPI(
    title="CINEVERSE API",
    description="AI-powered movie recommendation backend using content-based filtering.",
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS ───────────────────────────────────────────────────────────────────
_raw_origins = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://localhost:3000,http://localhost:4173,https://cineverse.vercel.app",
)
allowed_origins = [o.strip() for o in _raw_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"^https://.*\.vercel\.app$",  # Automatically allows all Vercel deployments & preview URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ══════════════════════════════════════════════════════════════════════════
#  ENDPOINTS
# ══════════════════════════════════════════════════════════════════════════

@app.get("/", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check — confirms the model is loaded and returns its dimensions.
    Frontend can call this to verify the backend is alive.
    """
    return HealthResponse(
        status="ok",
        movies_loaded=recommender.movie_count,
        similarity_matrix_shape=recommender.similarity_shape,
        message="CINEVERSE recommendation engine is running ✨",
    )


# ── Movie Search ───────────────────────────────────────────────────────────
@app.get("/api/movies/search", response_model=SearchResponse, tags=["Movies"])
async def search_movies(
    q: str = Query(..., min_length=1, description="Search query (movie title substring)"),
    limit: int = Query(20, ge=1, le=50, description="Maximum number of results"),
):
    """
    Search movies by title (case-insensitive substring match).

    Example: GET /api/movies/search?q=iron+man
    Returns movies whose titles contain 'iron man'.
    """
    raw_results = recommender.search(q, max_results=limit)

    # Enrich with TMDB poster data (fire requests concurrently)
    import asyncio

    async def enrich(item: dict) -> MovieBrief:
        brief = await tmdb_client.fetch_movie_brief(item["movie_id"], item["title"])
        return MovieBrief(
            movie_id=item["movie_id"],
            title=item["title"],
            poster_path=brief.get("poster_path") if brief else None,
            release_date=brief.get("release_date") if brief else None,
            vote_average=brief.get("vote_average") if brief else None,
        )

    enriched = await asyncio.gather(*[enrich(r) for r in raw_results])

    return SearchResponse(
        query=q,
        results=list(enriched),
        total=len(enriched),
    )


# ── Movie Detail ───────────────────────────────────────────────────────────
@app.get("/api/movies/{movie_id}", response_model=MovieDetail, tags=["Movies"])
async def get_movie(movie_id: int):
    """
    Return detailed info for a movie by its TMDB movie_id.
    If TMDB API key is set, enriched data (poster, genres, runtime) is returned.
    Otherwise, returns the title from the local dataset.
    """
    # First confirm the movie exists in our dataset
    local = recommender.get_movie_by_id(movie_id)
    if local is None:
        raise HTTPException(status_code=404, detail=f"Movie with id {movie_id} not found in dataset")

    # Try TMDB enrichment
    tmdb_data = await tmdb_client.fetch_movie_details(movie_id, local["title"])
    if tmdb_data:
        return MovieDetail(**tmdb_data)

    # Fallback: return only what we have locally
    return MovieDetail(
        movie_id=local["movie_id"],
        title=local["title"],
    )


# ── Recommendations ────────────────────────────────────────────────────────
@app.get("/api/recommend/{movie_title}", response_model=RecommendationResponse, tags=["Recommendations"])
async def get_recommendations(movie_title: str, top_n: int = Query(5, ge=1, le=20)):
    """
    Get up to `top_n` recommendations for a given movie title.

    This is the core endpoint — it uses the pre-trained cosine similarity matrix
    from similarity.pkl to find the most similar movies.

    Example: GET /api/recommend/Avatar
    Returns: Iron Man, Aliens, Independence Day … (actual ML output, not hardcoded)
    """
    try:
        raw_recs = recommender.recommend(movie_title, top_n=top_n)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    # Find the query movie's id for the response
    query_movie = recommender.search(movie_title, max_results=1)
    query_movie_id = query_movie[0]["movie_id"] if query_movie else -1

    # Enrich recommendations with TMDB data concurrently
    import asyncio

    async def enrich_rec(rec: dict) -> RecommendationItem:
        brief = await tmdb_client.fetch_movie_brief(rec["movie_id"], rec["title"])
        return RecommendationItem(
            rank=rec["rank"],
            movie_id=rec["movie_id"],
            title=rec["title"],
            similarity_score=rec["similarity_score"],
            poster_path=brief.get("poster_path") if brief else None,
            release_date=brief.get("release_date") if brief else None,
            vote_average=brief.get("vote_average") if brief else None,
            overview=None,  # overview fetched on demand via /api/movies/{id}
        )

    enriched_recs = await asyncio.gather(*[enrich_rec(r) for r in raw_recs])

    return RecommendationResponse(
        query_title=movie_title,
        query_movie_id=query_movie_id,
        recommendations=list(enriched_recs),
    )


# ── Genres ─────────────────────────────────────────────────────────────────
@app.get("/api/genres", tags=["Movies"])
async def get_genres():
    """
    Return TMDB genre list (requires TMDB API key).
    Falls back to an empty list if no key is set.
    """
    genres = await tmdb_client.fetch_all_genres()
    return {"genres": genres}


# ── Dev entry point ────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
