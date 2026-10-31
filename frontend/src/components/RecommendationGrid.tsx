import { motion } from 'framer-motion';
import { Sparkles, AlertCircle } from 'lucide-react';
import MovieCard from './MovieCard';
import type { RecommendationItem } from '../types';

interface RecommendationGridProps {
  queryTitle: string;
  recommendations: RecommendationItem[];
  loading?: boolean;
  error?: string | null;
}

function SkeletonCard() {
  return (
    <div className="rounded-2xl overflow-hidden bg-neutral-900 border border-white/5 animate-pulse">
      <div className="aspect-[2/3] bg-neutral-800" />
      <div className="p-3 space-y-2">
        <div className="h-4 bg-neutral-800 rounded w-3/4" />
        <div className="h-3 bg-neutral-800 rounded w-1/2" />
      </div>
    </div>
  );
}

export default function RecommendationGrid({
  queryTitle,
  recommendations,
  loading = false,
  error = null,
}: RecommendationGridProps) {
  return (
    <div className="w-full">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center gap-3 mb-8"
      >
        <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-gold-400/10 border border-gold-400/20">
          <Sparkles size={16} className="text-gold-400" />
          <span className="text-gold-400 text-sm font-medium">AI Picks</span>
        </div>
        <div>
          <h2 className="text-xl font-bold text-white font-display">
            Because you searched{' '}
            <span className="text-gold-400">&ldquo;{queryTitle}&rdquo;</span>
          </h2>
          <p className="text-neutral-500 text-sm mt-0.5">
            Ranked by cosine similarity score
          </p>
        </div>
      </motion.div>

      {/* Error state */}
      {error && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="flex items-center gap-3 p-6 rounded-2xl bg-red-500/10 border border-red-500/20 text-red-400"
        >
          <AlertCircle size={20} className="shrink-0" />
          <div>
            <p className="font-semibold">Recommendation failed</p>
            <p className="text-sm text-red-400/80 mt-0.5">{error}</p>
          </div>
        </motion.div>
      )}

      {/* Loading skeletons */}
      {loading && !error && (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
          {Array.from({ length: 5 }).map((_, i) => (
            <SkeletonCard key={i} />
          ))}
        </div>
      )}

      {/* Results */}
      {!loading && !error && recommendations.length > 0 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.4 }}
          className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4"
        >
          {recommendations.map((rec, i) => (
            <MovieCard
              key={rec.movie_id}
              movie_id={rec.movie_id}
              title={rec.title}
              poster_path={rec.poster_path}
              release_date={rec.release_date}
              vote_average={rec.vote_average}
              similarity_score={rec.similarity_score}
              rank={rec.rank}
              index={i}
            />
          ))}
        </motion.div>
      )}

      {/* No results */}
      {!loading && !error && recommendations.length === 0 && (
        <div className="text-center py-16 text-neutral-600">
          No recommendations found.
        </div>
      )}
    </div>
  );
}
