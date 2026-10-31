import { useState, useEffect, useRef } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, Film, Sparkles, Menu, X, Compass, Info } from 'lucide-react';
import { searchMovies } from '../api/cineverseApi';
import type { MovieBrief } from '../types';

export default function Navbar() {
  const [menuOpen, setMenuOpen] = useState(false);
  const [searchOpen, setSearchOpen] = useState(false);
  const [query, setQuery] = useState('');
  const [suggestions, setSuggestions] = useState<MovieBrief[]>([]);
  const [searching, setSearching] = useState(false);
  const navigate = useNavigate();
  const searchRef = useRef<HTMLDivElement | null>(null);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);

  useEffect(() => {
    const handleClick = (e: MouseEvent) => {
      if (searchRef.current && !searchRef.current.contains(e.target as Node)) {
        setSuggestions([]);
      }
    };
    document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, []);

  const handleSearch = (value: string) => {
    setQuery(value);
    clearTimeout(debounceRef.current);
    if (value.length < 2) { setSuggestions([]); return; }
    debounceRef.current = setTimeout(async () => {
      setSearching(true);
      try {
        const res = await searchMovies(value, 6);
        setSuggestions(res.results);
      } catch {
        setSuggestions([]);
      } finally {
        setSearching(false);
      }
    }, 350);
  };

  const handleSelect = (movie: MovieBrief) => {
    setSuggestions([]);
    setSearchOpen(false);
    setQuery('');
    navigate(`/movie/${movie.movie_id}?title=${encodeURIComponent(movie.title)}`);
  };

  const navLinks = [
    { to: '/', label: 'Home', icon: <Film size={16} /> },
    { to: '/discover', label: 'Discover', icon: <Compass size={16} /> },
    { to: '/about-ai', label: 'About AI', icon: <Info size={16} /> },
  ];

  return (
    <motion.nav
      initial={{ y: -80, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.6, ease: 'easeOut' }}
      className="fixed top-0 left-0 right-0 z-50 glass border-b border-white/5"
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2 group">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-gold-400 to-amber-600 flex items-center justify-center shadow-lg shadow-gold-500/30">
              <Sparkles size={16} className="text-black" />
            </div>
            <span className="text-xl font-display font-bold tracking-wide">
              <span className="text-gold-400">CINE</span>
              <span className="text-white">VERSE</span>
            </span>
          </Link>

          {/* Desktop Nav */}
          <div className="hidden md:flex items-center gap-6">
            {navLinks.map(({ to, label, icon }) => (
              <Link
                key={to}
                to={to}
                className="flex items-center gap-1.5 text-sm text-neutral-400 hover:text-gold-400 transition-colors duration-200"
              >
                {icon}
                {label}
              </Link>
            ))}
          </div>

          {/* Search */}
          <div className="flex items-center gap-3">
            <div ref={searchRef} className="relative">
              <AnimatePresence>
                {searchOpen ? (
                  <motion.div
                    initial={{ width: 0, opacity: 0 }}
                    animate={{ width: 280, opacity: 1 }}
                    exit={{ width: 0, opacity: 0 }}
                    transition={{ duration: 0.3 }}
                    className="overflow-hidden"
                  >
                    <input
                      autoFocus
                      value={query}
                      onChange={e => handleSearch(e.target.value)}
                      placeholder="Search movies…"
                      className="w-full bg-white/10 border border-white/20 rounded-xl px-4 py-2 text-sm text-white placeholder:text-neutral-500 outline-none focus:border-gold-400/50"
                    />
                    {/* Suggestions dropdown */}
                    <AnimatePresence>
                      {(suggestions.length > 0 || searching) && (
                        <motion.div
                          initial={{ opacity: 0, y: -8 }}
                          animate={{ opacity: 1, y: 0 }}
                          exit={{ opacity: 0 }}
                          className="absolute top-full mt-2 w-full bg-neutral-900 border border-white/10 rounded-xl overflow-hidden shadow-2xl"
                        >
                          {searching && (
                            <div className="px-4 py-3 text-sm text-neutral-500">Searching…</div>
                          )}
                          {suggestions.map(m => (
                            <button
                              key={m.movie_id}
                              onClick={() => handleSelect(m)}
                              className="w-full text-left px-4 py-3 text-sm text-neutral-200 hover:bg-white/5 hover:text-gold-400 transition-colors border-b border-white/5 last:border-0"
                            >
                              {m.title}
                            </button>
                          ))}
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </motion.div>
                ) : null}
              </AnimatePresence>
              <button
                onClick={() => setSearchOpen(v => !v)}
                className="p-2 rounded-lg text-neutral-400 hover:text-gold-400 hover:bg-white/5 transition-all"
              >
                {searchOpen ? <X size={20} /> : <Search size={20} />}
              </button>
            </div>

            {/* Mobile menu button */}
            <button
              onClick={() => setMenuOpen(v => !v)}
              className="md:hidden p-2 rounded-lg text-neutral-400 hover:text-gold-400 hover:bg-white/5"
            >
              {menuOpen ? <X size={20} /> : <Menu size={20} />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Menu */}
      <AnimatePresence>
        {menuOpen && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="md:hidden border-t border-white/5 overflow-hidden"
          >
            <div className="px-4 py-4 flex flex-col gap-3">
              {navLinks.map(({ to, label, icon }) => (
                <Link
                  key={to}
                  to={to}
                  onClick={() => setMenuOpen(false)}
                  className="flex items-center gap-2 text-neutral-400 hover:text-gold-400 transition-colors py-1"
                >
                  {icon}
                  {label}
                </Link>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.nav>
  );
}
