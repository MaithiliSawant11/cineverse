"""
Pydantic response models for CINEVERSE API.
These define the shape of JSON responses sent to the frontend.
"""

from typing import Optional
from pydantic import BaseModel


class MovieBrief(BaseModel):
    """Lightweight movie info used in search results and recommendation lists."""
    movie_id: int
    title: str
    poster_path: Optional[str] = None       # Full TMDB poster URL or None
    release_date: Optional[str] = None
    vote_average: Optional[float] = None


class MovieDetail(BaseModel):
    """Full movie details, enriched from TMDB."""
    movie_id: int
    title: str
    overview: Optional[str] = None
    poster_path: Optional[str] = None
    backdrop_path: Optional[str] = None
    release_date: Optional[str] = None
    vote_average: Optional[float] = None
    vote_count: Optional[int] = None
    genres: list[str] = []
    runtime: Optional[int] = None


class RecommendationItem(BaseModel):
    """One recommended movie, with similarity score and TMDB data."""
    rank: int
    movie_id: int
    title: str
    similarity_score: float
    poster_path: Optional[str] = None
    release_date: Optional[str] = None
    vote_average: Optional[float] = None
    overview: Optional[str] = None


class RecommendationResponse(BaseModel):
    """Full response for /api/recommend/{movie_title}."""
    query_title: str
    query_movie_id: int
    recommendations: list[RecommendationItem]


class SearchResponse(BaseModel):
    """Response for /api/movies/search."""
    query: str
    results: list[MovieBrief]
    total: int


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    movies_loaded: int
    similarity_matrix_shape: list[int]
    message: str
