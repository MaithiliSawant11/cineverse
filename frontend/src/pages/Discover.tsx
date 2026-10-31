import { useState } from 'react';
import { motion } from 'framer-motion';
import { Compass, Search } from 'lucide-react';
import SearchBar from '../components/SearchBar';
import RecommendationGrid from '../components/RecommendationGrid';
import { searchMovies, getRecommendations } from '../api/cineverseApi';
import type { MovieBrief, RecommendationItem } from '../types';

export default function Discover() {
  const [searchResults, setSearchResults] = useState<MovieBrief[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchLoading, setSearchLoading] = useState(false);

  const [recommendations, setRecommendations] = useState<RecommendationItem[]>([]);
  const [recQuery, setRecQuery] = useState('');
  const [recLoading, setRecLoading] = useState(false);
  const [recError, setRecError] = useState<string | null>(null);

  const handleSearch = async (query: string) => {
    if (!query.trim()) return;
    setSearchQuery(query);
    setSearchLoading(true);
    try {
      const res = await searchMovies(query, 20);
      setSearchResults(res.results);
    } catch {
      setSearchResults([]);
    } finally {
      setSearchLoading(false);
    }
  };

  const handleGetRecommendations = async (title: string) => {
    setRecQuery(title);
    setRecLoading(true);
    setRecError(null);
    try {
      const res = await getRecommendations(title);
      setRecommendations(res.recommendations);
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : 'Failed to load recommendations';
      setRecError(msg);
    } finally {
      setRecLoading(false);
    }
  };

  return (
    <div className="min-h-screen pt-24 pb-24">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-12"
        >
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 rounded-xl bg-gold-400/10 flex items-center justify-center">
              <Compass size={20} className="text-gold-400" />
            </div>
            <h1 className="text-3xl font-bold text-white font-display">Discover</h1>
          </div>
          <p className="text-neutral-500 max-w-xl">
            Search any movie and get AI-powered recommendations from our content-based model.
          </p>
        </motion.div>

        {/* Search area */}
        <div className="grid lg:grid-cols-3 gap-8">
          {/* Left: search + results */}
          <div className="lg:col-span-1">
            <div className="sticky top-24">
              <div className="mb-6">
                <SearchBar placeholder="Search for a movie…" />
              </div>

              {/* Manual search button approach */}
              <div className="relative">
                <input
                  type="text"
                  placeholder="Or type exact title for AI recommendations…"
                  className="w-full bg-white/5 border border-white/10 rounded-2xl px-4 py-3 text-sm text-white placeholder:text-neutral-600 outline-none focus:border-gold-400/40 mb-3"
                  onKeyDown={e => {
                    if (e.key === 'Enter') {
                      const v = (e.target as HTMLInputElement).value;
                      handleSearch(v);
                    }
                  }}
                />
                <p className="text-xs text-neutral-600 mb-4">Press Enter to search</p>
              </div>

              {/* Search results list */}
              {searchLoading && (
                <div className="space-y-2">
                  {Array.from({ length: 5 }).map((_, i) => (
                    <div key={i} className="h-12 bg-neutral-800 rounded-xl animate-pulse" />
                  ))}
                </div>
              )}
              {!searchLoading && searchResults.length > 0 && (
                <div className="space-y-1">
                  <p className="text-xs text-neutral-600 uppercase tracking-wider mb-3 flex items-center gap-2">
                    <Search size={10} />
                    Results for "{searchQuery}"
                  </p>
                  {searchResults.map(m => (
                    <button
                      key={m.movie_id}
                      onClick={() => handleGetRecommendations(m.title)}
                      className="w-full text-left px-4 py-3 rounded-xl bg-neutral-900 hover:bg-white/5 hover:text-gold-400 text-sm text-neutral-300 transition-colors border border-white/5 hover:border-gold-400/20"
                    >
                      {m.title}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Right: recommendations */}
          <div className="lg:col-span-2">
            {recQuery ? (
              <RecommendationGrid
                queryTitle={recQuery}
                recommendations={recommendations}
                loading={recLoading}
                error={recError}
              />
            ) : (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex flex-col items-center justify-center h-64 text-center"
              >
                <div className="w-16 h-16 rounded-2xl bg-neutral-900 border border-white/5 flex items-center justify-center mb-4">
                  <Compass size={28} className="text-neutral-700" />
                </div>
                <p className="text-neutral-600 text-sm">
                  Search a movie and select it to get AI recommendations
                </p>
              </motion.div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
