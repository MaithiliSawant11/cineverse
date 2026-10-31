import { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, X } from 'lucide-react';
import { searchMovies } from '../api/cineverseApi';
import type { MovieBrief } from '../types';

interface SearchBarProps {
  placeholder?: string;
  autoFocus?: boolean;
  className?: string;
}

export default function SearchBar({
  placeholder = 'Search for a movie…',
  autoFocus = false,
  className = '',
}: SearchBarProps) {
  const [query, setQuery] = useState('');
  const [suggestions, setSuggestions] = useState<MovieBrief[]>([]);
  const [loading, setLoading] = useState(false);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);
  const navigate = useNavigate();

  const handleChange = (value: string) => {
    setQuery(value);
    clearTimeout(debounceRef.current);
    if (value.length < 2) { setSuggestions([]); return; }
    debounceRef.current = setTimeout(async () => {
      setLoading(true);
      try {
        const res = await searchMovies(value, 8);
        setSuggestions(res.results);
      } catch {
        setSuggestions([]);
      } finally {
        setLoading(false);
      }
    }, 300);
  };

  const handleSelect = (movie: MovieBrief) => {
    setSuggestions([]);
    setQuery('');
    navigate(`/movie/${movie.movie_id}?title=${encodeURIComponent(movie.title)}`);
  };

  const clear = () => { setQuery(''); setSuggestions([]); };

  return (
    <div className={`relative ${className}`}>
      <div className="relative flex items-center">
        <Search size={20} className="absolute left-4 text-neutral-500 pointer-events-none" />
        <input
          autoFocus={autoFocus}
          value={query}
          onChange={e => handleChange(e.target.value)}
          placeholder={placeholder}
          className="w-full bg-white/5 border border-white/15 hover:border-white/25 focus:border-gold-400/60 rounded-2xl pl-12 pr-12 py-4 text-white placeholder:text-neutral-600 outline-none transition-all duration-200 text-sm sm:text-base"
        />
        {query && (
          <button onClick={clear} className="absolute right-4 text-neutral-500 hover:text-white transition-colors">
            <X size={18} />
          </button>
        )}
      </div>

      {/* Dropdown */}
      <AnimatePresence>
        {(suggestions.length > 0 || loading) && (
          <motion.div
            initial={{ opacity: 0, y: -8, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -8 }}
            transition={{ duration: 0.15 }}
            className="absolute top-full mt-2 w-full z-50 bg-neutral-900/95 backdrop-blur-xl border border-white/10 rounded-2xl overflow-hidden shadow-2xl shadow-black/50"
          >
            {loading && (
              <div className="px-5 py-4 text-sm text-neutral-500 flex items-center gap-2">
                <div className="w-4 h-4 border-2 border-gold-400/40 border-t-gold-400 rounded-full animate-spin" />
                Searching…
              </div>
            )}
            {suggestions.map((movie, i) => (
              <motion.button
                key={movie.movie_id}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.03 }}
                onClick={() => handleSelect(movie)}
                className="w-full text-left px-5 py-3.5 text-sm text-neutral-200 hover:bg-white/5 hover:text-gold-400 transition-colors border-b border-white/5 last:border-0 flex items-center gap-3"
              >
                <Search size={14} className="text-neutral-600 shrink-0" />
                <span className="truncate">{movie.title}</span>
              </motion.button>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
