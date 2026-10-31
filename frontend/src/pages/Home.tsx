import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Film, Sparkles, TrendingUp } from 'lucide-react';
import HeroSection from '../components/HeroSection';
import MovieCard from '../components/MovieCard';
import RecommendationGrid from '../components/RecommendationGrid';
import { searchMovies, getRecommendations } from '../api/cineverseApi';
import type { MovieBrief, RecommendationItem } from '../types';

// Featured movies to show on the homepage as "trending"
const FEATURED_MOVIES = [
  'Avatar', 'Iron Man', 'The Dark Knight', 'Inception', 'Interstellar',
  'The Avengers', 'Guardians of the Galaxy', 'Spider-Man 3',
];

export default function Home() {
  const [featured, setFeatured] = useState<MovieBrief[]>([]);
  const [featuredLoading, setFeaturedLoading] = useState(true);
  const [spotlightRecs, setSpotlightRecs] = useState<RecommendationItem[]>([]);
  const [spotlightTitle] = useState('The Dark Knight');
  const [spotlightLoading, setSpotlightLoading] = useState(true);
  const [spotlightError, setSpotlightError] = useState<string | null>(null);

  // Load featured movies for the trending section
  useEffect(() => {
    const loadFeatured = async () => {
      try {
        const results = await Promise.all(
          FEATURED_MOVIES.map(title => searchMovies(title, 1))
        );
        setFeatured(results.flatMap(r => r.results).slice(0, 8));
      } catch {
        setFeatured([]);
      } finally {
        setFeaturedLoading(false);
      }
    };
    loadFeatured();
  }, []);

  // Load spotlight recommendations
  useEffect(() => {
    const loadSpotlight = async () => {
      try {
        const res = await getRecommendations(spotlightTitle);
        setSpotlightRecs(res.recommendations);
      } catch (e: unknown) {
        const msg = e instanceof Error ? e.message : 'Failed to load recommendations';
        setSpotlightError(msg);
      } finally {
        setSpotlightLoading(false);
      }
    };
    loadSpotlight();
  }, [spotlightTitle]);

  return (
    <div className="min-h-screen">
      {/* Hero */}
      <HeroSection />

      {/* Trending section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="flex items-center gap-3 mb-10"
        >
          <TrendingUp size={20} className="text-gold-400" />
          <h2 className="text-2xl font-bold text-white font-display">Popular Titles</h2>
          <div className="flex-1 h-px bg-gradient-to-r from-gold-400/20 to-transparent ml-4" />
        </motion.div>

        {featuredLoading ? (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            {Array.from({ length: 8 }).map((_, i) => (
              <div key={i} className="rounded-2xl overflow-hidden bg-neutral-900 animate-pulse">
                <div className="aspect-[2/3] bg-neutral-800" />
                <div className="p-3 space-y-2">
                  <div className="h-4 bg-neutral-800 rounded w-3/4" />
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            {featured.map((m, i) => (
              <MovieCard
                key={m.movie_id}
                movie_id={m.movie_id}
                title={m.title}
                poster_path={m.poster_path}
                release_date={m.release_date}
                vote_average={m.vote_average}
                index={i}
              />
            ))}
          </div>
        )}
      </section>

      {/* Spotlight AI recommendations */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-24">
        <div className="rounded-3xl bg-gradient-to-br from-neutral-900 to-neutral-950 border border-white/5 p-8 sm:p-12">
          <div className="flex items-center gap-3 mb-2">
            <Sparkles size={20} className="text-gold-400" />
            <span className="text-gold-400 text-sm font-medium uppercase tracking-widest">AI Spotlight</span>
          </div>
          <p className="text-neutral-500 text-sm mb-8">
            Powered by your trained cosine similarity model
          </p>
          <RecommendationGrid
            queryTitle={spotlightTitle}
            recommendations={spotlightRecs}
            loading={spotlightLoading}
            error={spotlightError}
          />
        </div>
      </section>

      {/* How it works */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-32">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-14"
        >
          <h2 className="text-3xl font-bold text-white font-display mb-4">How CINEVERSE Works</h2>
          <p className="text-neutral-500 max-w-xl mx-auto">
            Real machine learning. No fake results.
          </p>
        </motion.div>
        <div className="grid sm:grid-cols-3 gap-6">
          {[
            { icon: <Film size={24} />, step: '01', title: 'Search a Movie', desc: 'Type any movie title from our 4,806 movie database.' },
            { icon: <Sparkles size={24} />, step: '02', title: 'AI Analyses Similarity', desc: 'Our model computes cosine similarity across genre, cast, overview, keywords, and director.' },
            { icon: <TrendingUp size={24} />, step: '03', title: 'Get 5 Real Picks', desc: 'The top-5 most similar movies are returned instantly from the pre-computed similarity matrix.' },
          ].map(({ icon, step, title, desc }, i) => (
            <motion.div
              key={step}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.1 }}
              className="relative p-6 rounded-2xl bg-neutral-900/50 border border-white/5 hover:border-gold-400/20 transition-colors group"
            >
              <div className="absolute top-4 right-4 text-5xl font-bold text-white/[0.03] font-display select-none">
                {step}
              </div>
              <div className="w-12 h-12 rounded-xl bg-gold-400/10 text-gold-400 flex items-center justify-center mb-4 group-hover:bg-gold-400/20 transition-colors">
                {icon}
              </div>
              <h3 className="text-white font-semibold mb-2">{title}</h3>
              <p className="text-neutral-500 text-sm leading-relaxed">{desc}</p>
            </motion.div>
          ))}
        </div>
      </section>
    </div>
  );
}
