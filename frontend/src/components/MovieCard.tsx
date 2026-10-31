import { useState } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Star, Calendar, Zap, Film } from 'lucide-react';

interface MovieCardProps {
  movie_id: number;
  title: string;
  poster_path: string | null;
  release_date?: string | null;
  vote_average?: number | null;
  similarity_score?: number;
  rank?: number;
  index?: number;
}

export default function MovieCard({
  movie_id,
  title,
  poster_path,
  release_date,
  vote_average,
  similarity_score,
  rank,
  index = 0,
}: MovieCardProps) {
  const navigate = useNavigate();
  const [imgError, setImgError] = useState(false);

  const year = release_date ? new Date(release_date).getFullYear() : null;
  const rating = vote_average ? vote_average.toFixed(1) : null;
  const hasValidImage = Boolean(poster_path && !imgError);

  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: index * 0.08, ease: 'easeOut' }}
      whileHover={{ y: -8, scale: 1.02 }}
      onClick={() => navigate(`/movie/${movie_id}?title=${encodeURIComponent(title)}`)}
      className="relative group cursor-pointer rounded-2xl overflow-hidden bg-neutral-900 border border-white/5 hover:border-gold-400/30 transition-all duration-300 shadow-lg hover:shadow-gold-500/10 flex flex-col justify-between"
    >
      {/* Rank badge */}
      {rank !== undefined && (
        <div className="absolute top-3 left-3 z-20 w-7 h-7 rounded-full bg-gold-400 text-black text-xs font-bold flex items-center justify-center shadow-lg">
          {rank}
        </div>
      )}

      {/* Similarity badge */}
      {similarity_score !== undefined && (
        <div className="absolute top-3 right-3 z-20 flex items-center gap-1 px-2 py-1 rounded-full bg-black/70 backdrop-blur-sm border border-gold-400/30 text-gold-400 text-xs font-medium">
          <Zap size={10} />
          {(similarity_score * 100).toFixed(0)}%
        </div>
      )}

      {/* Poster area */}
      <div className="relative aspect-[2/3] overflow-hidden bg-gradient-to-br from-neutral-900 via-neutral-950 to-black flex items-center justify-center">
        {hasValidImage ? (
          <img
            src={poster_path!}
            alt={title}
            loading="lazy"
            className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
            onError={() => setImgError(true)}
          />
        ) : (
          /* Stylish cinematic placeholder */
          <div className="w-full h-full p-4 flex flex-col items-center justify-center text-center bg-gradient-to-b from-neutral-900 via-neutral-950 to-neutral-900 relative">
            <div className="w-12 h-12 rounded-full bg-gold-400/10 border border-gold-400/20 flex items-center justify-center mb-3 text-gold-400">
              <Film size={22} />
            </div>
            <p className="text-white font-semibold text-xs leading-snug line-clamp-3 px-2 font-display">
              {title}
            </p>
            {year && (
              <span className="text-neutral-500 text-[10px] mt-2 px-2 py-0.5 rounded-full bg-white/5 border border-white/10">
                {year}
              </span>
            )}
            <div className="absolute inset-0 bg-radial-gradient from-gold-400/5 to-transparent pointer-events-none" />
          </div>
        )}

        {/* Gradient overlay */}
        <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
        
        {/* Hover overlay text */}
        <div className="absolute bottom-0 left-0 right-0 p-4 translate-y-full group-hover:translate-y-0 transition-transform duration-300">
          <p className="text-white text-sm font-semibold leading-tight line-clamp-2">{title}</p>
        </div>
      </div>

      {/* Info section */}
      <div className="p-3 bg-neutral-900/90">
        <h3 className="text-white text-sm font-semibold leading-tight line-clamp-2 mb-2">{title}</h3>
        <div className="flex items-center justify-between">
          {year ? (
            <div className="flex items-center gap-1 text-neutral-400 text-xs">
              <Calendar size={11} />
              {year}
            </div>
          ) : (
            <span className="text-neutral-500 text-xs">Featured</span>
          )}
          {rating ? (
            <div className="flex items-center gap-1 text-gold-400 text-xs font-medium">
              <Star size={11} fill="currentColor" />
              {rating}
            </div>
          ) : (
            <span className="text-neutral-500 text-xs">Recommended</span>
          )}
        </div>
      </div>

      {/* Glow effect on hover */}
      <div
        className="absolute inset-0 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none"
        style={{ boxShadow: 'inset 0 0 0 1px rgba(197,156,61,0.3)' }}
      />
    </motion.div>
  );
}
