"""
Core recommendation service for CINEVERSE.

This module loads the three pre-trained pickle files ONCE at startup and
exposes a recommend() function. The model is NEVER retrained here — we only
read from the saved artifacts.

Pickle files loaded:
  - movie_list.pkl     : Pandas DataFrame (4806 rows) with movie_id, title, tags
  - similarity.pkl     : NumPy ndarray (4806 x 4806) cosine similarity matrix
  - count_vectorizer.pkl : Fitted sklearn CountVectorizer (not used for inference,
                           kept loaded for compatibility checks)
"""

import os
import pickle
import logging
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# ── Resolve model directory relative to this file ──────────────────────────
# Works both locally and on Render/Docker where the cwd may differ.
_HERE = Path(__file__).resolve().parent          # backend/app/
_MODELS_DIR = _HERE.parent / "models"            # backend/models/


class RecommenderService:
    """
    Singleton-style service that holds loaded model artifacts in memory.

    Why singleton? Loading similarity.pkl (176 MB numpy array) takes ~1-2 seconds.
    We do it once when FastAPI starts, then every request reuses the same object.
    """

    def __init__(self) -> None:
        self.movie_df: Optional[pd.DataFrame] = None   # columns: movie_id, title, tags
        self.similarity: Optional[np.ndarray] = None   # shape (4806, 4806)
        self.vectorizer = None                          # sklearn CountVectorizer
        self._loaded = False

    # ── Public API ──────────────────────────────────────────────────────────

    def load(self) -> None:
        """Load all three pickle files. Called once on app startup."""
        logger.info("Loading CINEVERSE model artifacts from %s …", _MODELS_DIR)

        self.movie_df = self._load_pickle("movie_list.pkl")
        self.similarity = self._load_pickle("similarity.pkl")
        self.vectorizer = self._load_pickle("count_vectorizer.pkl")

        # Sanity checks — surface problems immediately rather than at request time
        assert isinstance(self.movie_df, pd.DataFrame), "movie_list.pkl must be a DataFrame"
        assert isinstance(self.similarity, np.ndarray), "similarity.pkl must be a numpy array"
        assert self.similarity.shape == (len(self.movie_df), len(self.movie_df)), (
            f"Mismatch: similarity shape {self.similarity.shape} vs "
            f"movie_df length {len(self.movie_df)}"
        )

        self._loaded = True
        logger.info(
            "Model loaded ✓  movies=%d  similarity=%s",
            len(self.movie_df),
            self.similarity.shape,
        )

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    @property
    def movie_count(self) -> int:
        return len(self.movie_df) if self.movie_df is not None else 0

    @property
    def similarity_shape(self) -> list[int]:
        if self.similarity is not None:
            return list(self.similarity.shape)
        return []

    def recommend(self, movie_title: str, top_n: int = 5) -> list[dict]:
        """
        Return up to `top_n` movie recommendations for the given title.

        Uses the pre-computed cosine similarity matrix — no re-computation.
        Index alignment between movie_df rows and similarity matrix rows
        is guaranteed by the original training code that saved both files.

        Returns a list of dicts:
            [{movie_id, title, similarity_score}, ...]
        Raises ValueError if the movie is not found in the dataset.
        """
        self._assert_loaded()

        # Case-insensitive exact-title match (same as original notebook logic)
        matches = self.movie_df.index[
            self.movie_df["title"].str.casefold() == movie_title.casefold()
        ].tolist()

        if not matches:
            raise ValueError(
                f"Movie '{movie_title}' not found in the dataset. "
                "Check the spelling or use /api/movies/search to find valid titles."
            )

        movie_index = matches[0]
        distance_row = self.similarity[movie_index]  # shape: (4806,)

        # Sort by similarity descending; skip index 0 (the movie itself)
        sorted_pairs = sorted(
            enumerate(distance_row),
            key=lambda x: x[1],
            reverse=True,
        )[1 : top_n + 1]

        results = []
        for rank, (idx, score) in enumerate(sorted_pairs, start=1):
            row = self.movie_df.iloc[idx]
            results.append(
                {
                    "rank": rank,
                    "movie_id": int(row["movie_id"]),
                    "title": str(row["title"]),
                    "similarity_score": round(float(score), 4),
                }
            )

        return results

    def search(self, query: str, max_results: int = 20) -> list[dict]:
        """
        Search movie titles by substring match (case-insensitive).
        Returns a list of {movie_id, title} dicts.
        """
        self._assert_loaded()

        if not query or not query.strip():
            return []

        mask = self.movie_df["title"].str.contains(
            query.strip(), case=False, na=False, regex=False
        )
        results_df = self.movie_df[mask].head(max_results)

        return [
            {"movie_id": int(row["movie_id"]), "title": str(row["title"])}
            for _, row in results_df.iterrows()
        ]

    def get_movie_by_id(self, movie_id: int) -> Optional[dict]:
        """Return basic movie info by TMDB movie_id, or None if not found."""
        self._assert_loaded()
        rows = self.movie_df[self.movie_df["movie_id"] == movie_id]
        if rows.empty:
            return None
        row = rows.iloc[0]
        return {"movie_id": int(row["movie_id"]), "title": str(row["title"])}

    def all_titles(self) -> list[str]:
        """Return sorted list of all movie titles (used for the genres endpoint workaround)."""
        self._assert_loaded()
        return sorted(self.movie_df["title"].tolist())

    # ── Private helpers ─────────────────────────────────────────────────────

    def _load_pickle(self, filename: str):
        path = _MODELS_DIR / filename
        if not path.exists():
            raise FileNotFoundError(
                f"Model file not found: {path}\n"
                "Make sure movie_list.pkl, similarity.pkl, and count_vectorizer.pkl "
                "are present in backend/models/"
            )
        logger.info("Loading %s (%.1f MB) …", filename, path.stat().st_size / 1_048_576)
        with open(path, "rb") as f:
            return pickle.load(f)

    def _assert_loaded(self) -> None:
        if not self._loaded:
            raise RuntimeError("RecommenderService.load() has not been called yet.")


# ── Module-level singleton instance ─────────────────────────────────────────
# Imported and used by main.py via FastAPI's app.state
recommender = RecommenderService()
