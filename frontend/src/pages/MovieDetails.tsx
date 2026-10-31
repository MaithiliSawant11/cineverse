import { useState, useEffect } from 'react';
import { useParams, useSearchParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Star, Calendar, Clock, ChevronLeft, Sparkles, AlertCircle } from 'lucide-react';
import RecommendationGrid from '../components/RecommendationGrid';
import { getMovieDetails, getRecommendations } from '../api/cineverseApi';
import type { MovieDetail, RecommendationItem } from '../types';

export default function MovieDetails() {
  const { movieId } = useParams<{ movieId: string }>();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const titleFromParam = searchParams.get('title') || '';

  const [movie, setMovie] = useState<MovieDetail | null>(null);
  const [movieLoading, setMovieLoading] = useState(true);
  const [movieError, setMovieError] = useState<string | null>(null);

  const [recs, setRecs] = useState<RecommendationItem[]>([]);
  const [recsLoading, setRecsLoading] = useState(false);
  const [recsError, setRecsError] = useState<string | null>(null);

  // Load movie details
  useEffect(() => {
    if (!movieId) return;
    setMovieLoading(true);
    setMovieError(null);
    getMovieDetails(Number(movieId))
      .then(data => {
        setMovie(data);
        // Trigger recommendations using the title
        const title = data.title || titleFromParam;
        if (title) {
          loadRecommendations(title);
        }
      })
      .catch(() => {
        setMovieError('Could not load movie details.');
        // Still try recommendations via the title param
        if (titleFromParam) loadRecommendations(titleFromParam);
      })
      .finally(() => setMovieLoading(false));
  }, [movieId]);

  const loadRecommendations = async (title: string) => {
    setRecsLoading(true);
    setRecsError(null);
    try {
      const res = await getRecommendations(title);
      setRecs(res.recommendations);
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : 'Failed to load recommendations';
      setRecsError(msg);
    } finally {
      setRecsLoading(false);
    }
  };

  const displayTitle = movie?.title || titleFromParam;

  return (
    <div className="min-h-screen pt-16">
      {/* Backdrop */}
      {movie?.backdrop_path && (
        <div className="relative h-[55vh] overflow-hidden">
          <img
            src={movie.backdrop_path}
            alt={displayTitle}
            className="w-full h-full object-cover"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-neutral-950 via-neutral-950/60 to-transparent" />
          <div className="absolute inset-0 bg-gradient-to-r from-neutral-950/80 to-transparent" />
        </div>
      )}

      {!movie?.backdrop_path && (
        <div className="h-32 bg-gradient-to-b from-neutral-900 to-transparent" />
      )}

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 -mt-48 relative z-10 pb-24">
        {/* Back button */}
        <button
          onClick={() => navigate(-1)}
          className="flex items-center gap-2 text-neutral-500 hover:text-gold-400 transition-colors mb-8 text-sm"
        >
          <ChevronLeft size={18} />
          Back
        </button>

        {movieLoading ? (
          <div className="animate-pulse">
            <div className="h-8 bg-neutral-800 rounded w-1/3 mb-4" />
            <div className="h-4 bg-neutral-800 rounded w-1/4 mb-6" />
            <div className="h-20 bg-neutral-800 rounded mb-2" />
          </div>
        ) : movieError && !displayTitle ? (
          <div className="flex items-center gap-3 p-6 rounded-2xl bg-red-500/10 border border-red-500/20 text-red-400 mb-8">
            <AlertCircle size={20} />
            <p>{movieError}</p>
          </div>
        ) : (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex flex-col md:flex-row gap-10 mb-16"
          >
            {/* Poster */}
            <div className="shrink-0">
              <div className="w-48 md:w-64 aspect-[2/3] rounded-2xl overflow-hidden shadow-2xl shadow-black/60 border border-white/10 bg-neutral-900 flex items-center justify-center">
                {movie?.poster_path ? (
                  <img
                    src={movie.poster_path}
                    alt={displayTitle}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div className="w-full h-full p-6 flex flex-col items-center justify-center text-center bg-gradient-to-b from-neutral-800 to-neutral-950">
                    <div className="w-16 h-16 rounded-full bg-gold-400/10 border border-gold-400/20 flex items-center justify-center mb-4 text-gold-400">
                      <Sparkles size={28} />
                    </div>
                    <p className="text-white font-semibold text-sm leading-snug line-clamp-3 font-display">
                      {displayTitle}
                    </p>
                  </div>
                )}
              </div>
            </div>

            {/* Info */}
            <div className="flex-1">
              <h1 className="text-4xl md:text-5xl font-bold text-white font-display leading-tight mb-4">
                {displayTitle}
              </h1>

              {/* Meta row */}
              <div className="flex flex-wrap gap-4 mb-6">
                {movie?.vote_average && (
                  <div className="flex items-center gap-1.5 text-gold-400">
                    <Star size={16} fill="currentColor" />
                    <span className="font-semibold">{movie.vote_average.toFixed(1)}</span>
                    {movie.vote_count && (
                      <span className="text-neutral-600 text-sm">({movie.vote_count.toLocaleString()} votes)</span>
                    )}
                  </div>
                )}
                {movie?.release_date && (
                  <div className="flex items-center gap-1.5 text-neutral-400 text-sm">
                    <Calendar size={14} />
                    {new Date(movie.release_date).getFullYear()}
                  </div>
                )}
                {movie?.runtime && (
                  <div className="flex items-center gap-1.5 text-neutral-400 text-sm">
                    <Clock size={14} />
                    {Math.floor(movie.runtime / 60)}h {movie.runtime % 60}m
                  </div>
                )}
              </div>

              {/* Genres */}
              {movie?.genres && movie.genres.length > 0 && (
                <div className="flex flex-wrap gap-2 mb-6">
                  {movie.genres.map(g => (
                    <span key={g} className="px-3 py-1 rounded-full bg-white/5 border border-white/10 text-neutral-300 text-xs">
                      {g}
                    </span>
                  ))}
                </div>
              )}

              {/* Overview */}
              {movie?.overview && (
                <p className="text-neutral-400 leading-relaxed max-w-2xl text-sm md:text-base">
                  {movie.overview}
                </p>
              )}

              {!movie?.overview && movieError && (
                <p className="text-neutral-600 text-sm italic">
                  Add a TMDB API key in backend/.env to see full movie details, posters, and ratings.
                </p>
              )}

              {/* AI Recommendations CTA */}
              <div className="mt-8 inline-flex items-center gap-2 px-5 py-2.5 rounded-full bg-gold-400/10 border border-gold-400/20 text-gold-400 text-sm font-medium">
                <Sparkles size={14} />
                Scroll down for AI recommendations
              </div>
            </div>
          </motion.div>
        )}

        {/* Recommendations */}
        {(recsLoading || recs.length > 0 || recsError) && (
          <RecommendationGrid
            queryTitle={displayTitle}
            recommendations={recs}
            loading={recsLoading}
            error={recsError}
          />
        )}
      </div>
    </div>
  );
}
