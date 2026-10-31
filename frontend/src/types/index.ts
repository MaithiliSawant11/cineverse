// TypeScript types for CINEVERSE API responses

export interface MovieBrief {
  movie_id: number;
  title: string;
  poster_path: string | null;
  release_date: string | null;
  vote_average: number | null;
}

export interface MovieDetail {
  movie_id: number;
  title: string;
  overview: string | null;
  poster_path: string | null;
  backdrop_path: string | null;
  release_date: string | null;
  vote_average: number | null;
  vote_count: number | null;
  genres: string[];
  runtime: number | null;
}

export interface RecommendationItem {
  rank: number;
  movie_id: number;
  title: string;
  similarity_score: number;
  poster_path: string | null;
  release_date: string | null;
  vote_average: number | null;
  overview: string | null;
}

export interface RecommendationResponse {
  query_title: string;
  query_movie_id: number;
  recommendations: RecommendationItem[];
}

export interface SearchResponse {
  query: string;
  results: MovieBrief[];
  total: number;
}

export interface HealthResponse {
  status: string;
  movies_loaded: number;
  similarity_matrix_shape: number[];
  message: string;
}
