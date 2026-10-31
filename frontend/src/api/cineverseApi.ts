/// <reference types="vite/client" />

/**
 * CINEVERSE API client
 * All backend calls go through this module — makes it easy to swap the base URL.
 * VITE_API_URL is set in .env (local) or Vercel environment (production).
 */

import axios from 'axios';
import type {
  HealthResponse,
  MovieDetail,
  RecommendationResponse,
  SearchResponse,
} from '../types';

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,  // 30s — model loading on cold Render start can be slow
});

/** Health check — verify backend is alive */
export async function checkHealth(): Promise<HealthResponse> {
  const { data } = await api.get<HealthResponse>('/');
  return data;
}

/** Search movies by title substring */
export async function searchMovies(query: string, limit = 20): Promise<SearchResponse> {
  const { data } = await api.get<SearchResponse>('/api/movies/search', {
    params: { q: query, limit },
  });
  return data;
}

/** Get full movie details by TMDB id */
export async function getMovieDetails(movieId: number): Promise<MovieDetail> {
  const { data } = await api.get<MovieDetail>(`/api/movies/${movieId}`);
  return data;
}

/** Get 5 AI recommendations for a movie title */
export async function getRecommendations(movieTitle: string): Promise<RecommendationResponse> {
  const { data } = await api.get<RecommendationResponse>(
    `/api/recommend/${encodeURIComponent(movieTitle)}`
  );
  return data;
}

/** Get genre list (requires TMDB key) */
export async function getGenres(): Promise<{ id: number; name: string }[]> {
  const { data } = await api.get<{ genres: { id: number; name: string }[] }>('/api/genres');
  return data.genres;
}

export { BASE_URL };
