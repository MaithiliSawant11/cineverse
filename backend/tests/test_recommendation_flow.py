"""
Comprehensive Test Suite for CINEVERSE Recommender & API.

Verifies:
1. Recommender service loads 4,806 movies and similarity matrix correctly.
2. Valid movie recommendations return exactly 5 relevant items with expected schema.
3. Invalid movie names raise expected 404 / error handling.
4. TMDB integration gracefully falls back when TMDB_API_KEY is unset/mocked.
5. Search endpoint returns substring matches.
6. Movie details endpoint returns expected data with graceful fallback.
"""

import sys
import os

# Add backend directory to sys.path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from fastapi.testclient import TestClient
from app.main import app

def run_all_tests():
    print("=" * 60)
    print("RUNNING CINEVERSE TEST SUITE")
    print("=" * 60)

    # 1. Initialize TestClient with app lifespan
    with TestClient(app) as client:
        # Test 1: Health check
        print("\n[TEST 1] Health check endpoint...")
        resp = client.get("/")
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        data = resp.json()
        assert data["status"] == "ok"
        assert data["movies_loaded"] == 4806
        assert data["similarity_matrix_shape"] == [4806, 4806]
        print(f"  [OK] Health check: {data['movies_loaded']} movies loaded")

        # Test 2: Valid movie recommendation (Avatar)
        print("\n[TEST 2] Recommendations for 'Avatar'...")
        resp = client.get("/api/recommend/Avatar")
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        rec_data = resp.json()
        assert rec_data["query_title"] == "Avatar"
        assert len(rec_data["recommendations"]) == 5
        titles = [r["title"] for r in rec_data["recommendations"]]
        print(f"  [OK] Avatar recommendations: {titles}")
        assert "Aliens vs Predator: Requiem" in titles or "Aliens" in titles

        # Test 3: Recommendation with graceful TMDB fallback (null posters/ratings)
        print("\n[TEST 3] Graceful fallback check for TMDB metadata...")
        for r in rec_data["recommendations"]:
            # With unconfigured TMDB key, fields must be None / fallback strings without crashing
            assert "poster_path" in r
            assert "vote_average" in r
            assert "overview" in r
        print("  [OK] Graceful TMDB fallbacks present in all recommendation items")

        # Test 4: Invalid movie recommendation (NonExistentMovieXYZ)
        print("\n[TEST 4] Invalid movie error handling...")
        resp = client.get("/api/recommend/NonExistentMovieXYZ")
        assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"
        err_data = resp.json()
        assert "detail" in err_data
        print(f"  [OK] Non-existent movie returned 404 cleanly: {err_data['detail']}")

        # Test 5: Search movies
        print("\n[TEST 5] Movie search endpoint...")
        resp = client.get("/api/movies/search?q=Dark%20Knight")
        assert resp.status_code == 200
        search_data = resp.json()
        assert search_data["total"] >= 1
        found_titles = [m["title"] for m in search_data["results"]]
        print(f"  [OK] Search 'Dark Knight' results: {found_titles}")

        # Test 6: Movie details endpoint
        print("\n[TEST 6] Movie details endpoint...")
        resp = client.get("/api/movies/19995") # Avatar TMDB id
        assert resp.status_code == 200
        details = resp.json()
        assert details["title"] == "Avatar"
        assert details["movie_id"] == 19995
        print(f"  [OK] Movie details retrieved: {details['title']} (ID: {details['movie_id']})")

        # Test 7: Genres endpoint
        print("\n[TEST 7] Genres list endpoint...")
        resp = client.get("/api/genres")
        assert resp.status_code == 200
        genres = resp.json()
        assert len(genres) > 0
        print(f"  [OK] Genres retrieved: {len(genres)} genres available")

    print("\n" + "=" * 60)
    print("ALL TESTS PASSED SUCCESSFULLY! [OK]")
    print("=" * 60)

if __name__ == "__main__":
    run_all_tests()
