import { BrowserRouter, Routes, Route, useLocation } from 'react-router-dom';
import { AnimatePresence, motion, type Variants } from 'framer-motion';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import Discover from './pages/Discover';
import MovieDetails from './pages/MovieDetails';
import AboutAI from './pages/AboutAI';

const pageVariants: Variants = {
  initial: { opacity: 0, y: 12 },
  animate: { opacity: 1, y: 0, transition: { duration: 0.35, ease: [0.25, 0.1, 0.25, 1] } },
  exit: { opacity: 0, y: -8, transition: { duration: 0.2 } },
};

function AnimatedRoutes() {
  const location = useLocation();
  return (
    <AnimatePresence mode="wait">
      <Routes location={location} key={location.pathname}>
        <Route path="/" element={
          <motion.div variants={pageVariants} initial="initial" animate="animate" exit="exit">
            <Home />
          </motion.div>
        } />
        <Route path="/discover" element={
          <motion.div variants={pageVariants} initial="initial" animate="animate" exit="exit">
            <Discover />
          </motion.div>
        } />
        <Route path="/movie/:movieId" element={
          <motion.div variants={pageVariants} initial="initial" animate="animate" exit="exit">
            <MovieDetails />
          </motion.div>
        } />
        <Route path="/about-ai" element={
          <motion.div variants={pageVariants} initial="initial" animate="animate" exit="exit">
            <AboutAI />
          </motion.div>
        } />
        {/* 404 fallback */}
        <Route path="*" element={
          <motion.div
            variants={pageVariants} initial="initial" animate="animate" exit="exit"
            className="min-h-screen flex flex-col items-center justify-center text-center pt-24 px-4"
          >
            <p className="text-8xl font-bold text-gold-400 font-display mb-4">404</p>
            <p className="text-neutral-400 mb-6">Page not found</p>
            <a href="/" className="text-gold-400 hover:text-gold-300 transition-colors text-sm">
              ← Return home
            </a>
          </motion.div>
        } />
      </Routes>
    </AnimatePresence>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen" style={{ background: '#060608' }}>
        <Navbar />
        <AnimatedRoutes />
        {/* Footer */}
        <footer className="border-t border-white/5 py-10 mt-8">
          <div className="max-w-7xl mx-auto px-4 text-center">
            <p className="text-neutral-700 text-sm">
              <span className="text-gold-400 font-semibold">CINEVERSE</span>
              {' '}— AI-powered movie recommendations using content-based filtering on TMDB 5000 dataset.
            </p>
            <p className="text-neutral-800 text-xs mt-2">
              Built with Python · FastAPI · scikit-learn · React · TypeScript · Framer Motion
            </p>
          </div>
        </footer>
      </div>
    </BrowserRouter>
  );
}
