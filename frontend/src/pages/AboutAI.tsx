import { motion } from 'framer-motion';
import { Brain, GitBranch, Database, Cpu, Code2, BarChart3, Layers } from 'lucide-react';

export default function AboutAI() {
  return (
    <div className="min-h-screen pt-24 pb-24">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="mb-16">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-12 h-12 rounded-xl bg-gold-400/10 flex items-center justify-center">
              <Brain size={24} className="text-gold-400" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-white font-display">About the AI</h1>
              <p className="text-neutral-500 text-sm">How CINEVERSE recommendations really work</p>
            </div>
          </div>
          <div className="h-px bg-gradient-to-r from-gold-400/30 via-gold-400/10 to-transparent" />
        </motion.div>

        {/* Algorithm overview */}
        <div className="space-y-8">
          {/* Pipeline section */}
          <motion.section
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="rounded-3xl bg-neutral-900/60 border border-white/5 p-8"
          >
            <div className="flex items-center gap-3 mb-6">
              <GitBranch size={18} className="text-gold-400" />
              <h2 className="text-xl font-bold text-white font-display">ML Pipeline</h2>
            </div>
            <div className="grid sm:grid-cols-4 gap-4">
              {[
                { label: 'Data', detail: 'TMDB 5000 Movies + Credits', icon: <Database size={16} /> },
                { label: 'Features', detail: 'Overview + Genres + Keywords + Cast + Director', icon: <Layers size={16} /> },
                { label: 'Vectorization', detail: 'CountVectorizer (5,000 max features)', icon: <BarChart3 size={16} /> },
                { label: 'Similarity', detail: 'Cosine Similarity (4806 × 4806 matrix)', icon: <Cpu size={16} /> },
              ].map(({ label, detail, icon }, i) => (
                <motion.div
                  key={label}
                  initial={{ opacity: 0, y: 10 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: i * 0.1 }}
                  className="p-4 rounded-2xl bg-white/3 border border-white/5 relative overflow-hidden"
                >
                  <div className="absolute top-2 right-2 text-neutral-800 font-bold text-3xl font-display select-none">
                    {String(i + 1).padStart(2, '0')}
                  </div>
                  <div className="text-gold-400 mb-3">{icon}</div>
                  <p className="text-white text-sm font-semibold mb-1">{label}</p>
                  <p className="text-neutral-500 text-xs leading-relaxed">{detail}</p>
                </motion.div>
              ))}
            </div>
          </motion.section>

          {/* Text preprocessing */}
          <motion.section
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="rounded-3xl bg-neutral-900/60 border border-white/5 p-8"
          >
            <div className="flex items-center gap-3 mb-6">
              <Code2 size={18} className="text-gold-400" />
              <h2 className="text-xl font-bold text-white font-display">Text Preprocessing</h2>
            </div>
            <div className="space-y-4">
              {[
                { step: 'Feature Extraction', desc: 'Genres, keywords, and cast are parsed from JSON-like strings in the TMDB dataset.' },
                { step: 'Cast Limiting', desc: 'Only the first 3 cast members are used to prevent popular actors from dominating similarity.' },
                { step: 'Space Removal', desc: 'Multi-word names like "Sam Worthington" become "SamWorthington" so they count as one token.' },
                { step: 'Porter Stemming', desc: 'Words are reduced to their root form. "loving", "lover", "loves" → "love". This links semantically similar films.' },
                { step: 'CountVectorizer', desc: '5,000 most frequent stemmed tokens are kept. Each movie becomes a vector of word frequencies.' },
                { step: 'Cosine Similarity', desc: 'The angle between two movie vectors in 5,000-dimensional space measures how similar they are, regardless of length.' },
              ].map(({ step, desc }, i) => (
                <div key={step} className="flex gap-4">
                  <div className="shrink-0 w-6 h-6 rounded-full bg-gold-400/20 text-gold-400 text-xs font-bold flex items-center justify-center mt-0.5">
                    {i + 1}
                  </div>
                  <div>
                    <span className="text-white text-sm font-semibold">{step}: </span>
                    <span className="text-neutral-500 text-sm">{desc}</span>
                  </div>
                </div>
              ))}
            </div>
          </motion.section>

          {/* Cosine similarity explanation */}
          <motion.section
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="rounded-3xl bg-gradient-to-br from-gold-400/5 to-transparent border border-gold-400/10 p-8"
          >
            <div className="flex items-center gap-3 mb-6">
              <BarChart3 size={18} className="text-gold-400" />
              <h2 className="text-xl font-bold text-white font-display">Cosine Similarity Formula</h2>
            </div>
            <div className="bg-black/40 rounded-2xl p-6 font-mono text-sm text-center mb-6">
              <p className="text-neutral-400 mb-2">similarity( A, B )</p>
              <p className="text-gold-400 text-lg">
                = (A · B) / (‖A‖ × ‖B‖)
              </p>
              <p className="text-neutral-600 text-xs mt-3">
                Range: 0 (completely different) to 1 (identical)
              </p>
            </div>
            <p className="text-neutral-400 text-sm leading-relaxed">
              By pre-computing similarity for all 4,806 × 4,806 movie pairs at training time,
              CINEVERSE can return recommendations in milliseconds at inference time —
              no recomputation needed. The 176 MB <code className="text-gold-400 bg-white/5 px-1 rounded">similarity.pkl</code> matrix
              stores all 23 million pre-computed values.
            </p>
          </motion.section>

          {/* Tech stack */}
          <motion.section
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="rounded-3xl bg-neutral-900/60 border border-white/5 p-8"
          >
            <h2 className="text-xl font-bold text-white font-display mb-6">Tech Stack</h2>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
              {[
                { name: 'Python 3.11', role: 'ML & Backend', color: 'from-blue-500/10' },
                { name: 'scikit-learn', role: 'CountVectorizer + Cosine Sim', color: 'from-orange-500/10' },
                { name: 'NLTK', role: 'Porter Stemmer', color: 'from-green-500/10' },
                { name: 'FastAPI', role: 'REST API Backend', color: 'from-teal-500/10' },
                { name: 'React + TypeScript', role: 'Frontend', color: 'from-cyan-500/10' },
                { name: 'Framer Motion', role: 'Animations', color: 'from-purple-500/10' },
              ].map(({ name, role, color }) => (
                <div key={name} className={`p-4 rounded-2xl bg-gradient-to-br ${color} to-transparent border border-white/5`}>
                  <p className="text-white text-sm font-semibold">{name}</p>
                  <p className="text-neutral-600 text-xs mt-1">{role}</p>
                </div>
              ))}
            </div>
          </motion.section>
        </div>
      </div>
    </div>
  );
}
