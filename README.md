# 🎬 CINEVERSE — AI-Powered Movie Recommendation Engine

CINEVERSE is a full-stack, machine learning-powered movie recommendation platform built with **FastAPI**, **React 19**, **TypeScript**, **Tailwind CSS v4**, and **Framer Motion**. It uses **Content-Based Filtering** with **Cosine Similarity** on the TMDB 5,000 movie dataset (4,806 processed movies).

---

## 🌟 Key Highlights

- **Exact ML Engine Preserved**: Uses the pre-computed 4,806 × 4,806 cosine similarity matrix (`similarity.pkl`, 176.2 MB) without retraining or altering recommendation results.
- **Real Theatrical Movie Posters**: Automatically resolves and caches high-definition real movie posters from Wikipedia / Wikimedia Commons REST APIs without requiring an API key.
- **Rich Metadata Out-of-the-Box**: Real ratings (⭐), release years, plot synopses, runtime, and genres are pre-cached for all 4,803 movies.
- **Configurable TMDB Key**: Works seamlessly without any API key, while still providing a configurable `TMDB_API_KEY` slot if you want to use personal TMDB credentials later.
- **Production-Ready Architecture**:
  - **Backend**: FastAPI with lifespan-based singleton ML model loading (loads once on startup into memory).
  - **Frontend**: React 19 + Vite + TypeScript + Tailwind CSS v4 + Framer Motion animated cards & modals.
  - **Git LFS**: Pre-configured and verified for `similarity.pkl` (176.2 MB).
  - **Deployment**: `render.yaml` with `lfsEnabled: true` for Render, and zero-config SPA rewrites for Vercel.

---

## 📁 Repository Structure

```
CINEVERSE/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app, CORS, lifespan & endpoints
│   │   ├── recommender.py       # ML singleton service (loads .pkl artifacts)
│   │   ├── models.py            # Pydantic schemas & response validation
│   │   └── tmdb.py              # Media enrichment & online poster resolver
│   ├── models/
│   │   ├── movie_list.pkl       # 4,806-row DataFrame (movie_id, title, tags)
│   │   ├── similarity.pkl       # 4,806 × 4,806 cosine similarity matrix (176.2 MB, Git LFS)
│   │   ├── count_vectorizer.pkl # CountVectorizer vocabulary
│   │   ├── movie_metadata.json  # Full metadata (overview, rating, year, runtime, genres)
│   │   └── poster_cache.json    # Pre-cached real theatrical poster URLs
│   ├── tests/
│   │   └── test_recommendation_flow.py  # End-to-end automated test suite
│   ├── .env.example             # Backend environment template
│   ├── requirements.txt         # Pinned Python dependencies
│   └── Dockerfile               # Production container definition
│
├── frontend/
│   ├── src/
│   │   ├── api/cineverseApi.ts  # Axios client connecting to backend API
│   │   ├── components/          # Navbar, MovieCard, SearchBar, HeroSection, RecommendationGrid
│   │   ├── pages/               # Home, Discover, MovieDetails, AboutAI
│   │   ├── types/               # TypeScript interfaces
│   │   └── App.tsx              # React router & layout
│   ├── .env.example             # Frontend environment template
│   ├── package.json             # React 19, Tailwind CSS v4, Framer Motion
│   ├── tsconfig.json            # Strict TypeScript configuration
│   ├── vercel.json              # Vercel SPA route rewrite rules
│   └── vite.config.ts           # Vite + Tailwind + React plugin setup
│
├── datasets/                    # Raw TMDB 5,000 CSV datasets
├── scripts/                     # Cache generation utilities
├── .gitattributes               # Git LFS tracking rules for *.pkl
├── render.yaml                  # Render Blueprint deployment definition
└── README.md                    # Project documentation & deployment guide
```

---

## 🧪 Local Testing & Verification

Before deploying, you can run the automated verification test suite locally:

```bash
# Run backend test suite
python backend/tests/test_recommendation_flow.py
```

The test suite validates:
1. `GET /`: Confirms 4,806 movies and `(4806, 4806)` matrix loaded in memory.
2. `GET /api/recommend/Avatar`: Asserts 5 top matches (`Aliens vs Predator: Requiem`, `Aliens`, `Falcon Rising`, `Independence Day`, `Titan A.E.`).
3. Real online poster resolution & metadata fallback check.
4. `GET /api/recommend/NonExistentMovieXYZ`: Asserts clean HTTP 404 response with an informative error message.
5. `GET /api/movies/search?q=Dark%20Knight`: Verifies autocomplete and title substring search.
6. `GET /api/movies/19995`: Verifies movie detail retrieval.
7. `GET /api/genres`: Verifies genre taxonomy.

---

## 🚀 Running Locally

### 1. Backend Setup

```bash
cd backend

# Create and activate a virtual environment
python -m venv venv
# Windows:
.\venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env from template
cp .env.example .env

# Start server
python -m uvicorn app.main:app --reload --port 8000
```

- API Base URL: `http://localhost:8000`
- Interactive Swagger UI: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/`

### 2. Frontend Setup

In a new terminal window:

```bash
cd frontend

# Install dependencies
npm install

# Create .env from template
cp .env.example .env

# Start development server
npm run dev
```

Open your browser at `http://localhost:5173`.

---

## 🌐 Deployment Guide

### Overview
- **Source Code & Git LFS**: GitHub (`https://github.com/MaithiliSawant11/cineverse`)
- **Backend API**: Render (Docker Runtime)
- **Frontend App**: Vercel (Vite SPA)

---

### Part 1: Verify Git LFS on GitHub

The repository already tracks the 176.2 MB `similarity.pkl` using Git LFS. You can verify it with:

```bash
git lfs ls-files -s
```
*Expected output: `backend/models/similarity.pkl (185 MB)` with an asterisk `*` indicating the full LFS object is present.*

---

### Part 2: Backend Deployment on Render

#### Option A: Automatic Blueprint Deployment (Recommended)
1. Sign in to [Render](https://dashboard.render.com/).
2. Click **New +** → **Blueprint**.
3. Select your GitHub repository: `MaithiliSawant11/cineverse`.
4. Render will automatically detect [`render.yaml`](file:///c:/Users/Maithili/Desktop/CINEVERSE/render.yaml) at the repository root.
5. Notice that `lfsEnabled: true` is pre-configured so Render automatically pulls the 176 MB `similarity.pkl` during the Docker build.
6. Click **Apply**.
7. Once deployed, note your Render URL: e.g., `https://cineverse-backend.onrender.com`.

#### Option B: Manual Web Service Deployment
1. Click **New +** → **Web Service**.
2. Connect your GitHub repository: `MaithiliSawant11/cineverse`.
3. Set the following settings:
   - **Name**: `cineverse-backend`
   - **Language / Runtime**: `Docker`
   - **Root Directory**: `backend` (or leave root and set Dockerfile path to `./backend/Dockerfile`)
   - **Dockerfile Path**: `./backend/Dockerfile`
   - **Docker Context**: `./backend`
   - **Plan**: `Starter` (or `Standard` if your instance needs additional RAM)
4. Under **Advanced**:
   - Check **Docker LFS** (or set `lfsEnabled: true`).
5. Under **Environment Variables**:
   - `PORT` = `8000`
   - `ALLOWED_ORIGINS` = `https://cineverse.vercel.app,http://localhost:5173,http://localhost:3000`
   - `TMDB_API_KEY` = *(Optional: leave empty to use built-in poster & metadata enrichment)*
6. Click **Create Web Service**.

---

### Part 3: Frontend Deployment on Vercel

1. Sign in to [Vercel](https://vercel.com/).
2. Click **Add New...** → **Project**.
3. Import your GitHub repository: `MaithiliSawant11/cineverse`.
4. Configure the Project Settings:
   - **Framework Preset**: `Vite`
   - **Root Directory**: Click *Edit* and select `frontend`.
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
5. Under **Environment Variables**, add:
   - **Key**: `VITE_API_URL`
   - **Value**: `https://cineverse-backend.onrender.com` *(your Render backend URL, without trailing slash)*
6. Click **Deploy**.
7. Vercel will build and assign you a URL (e.g., `https://cineverse.vercel.app`).

---

### Part 4: Connecting the Two Services & CORS

1. In your **Render Dashboard** → Select `cineverse-backend` → **Environment**.
2. Update `ALLOWED_ORIGINS` to include your exact Vercel URL:
   ```
   https://cineverse.vercel.app,http://localhost:5173,http://localhost:3000
   ```
   *(Note: The backend also has an automated regex pattern `^https://.*\.vercel\.app$` that auto-authorizes all Vercel production and preview deployment URLs!)*
3. Save changes — Render will redeploy or reload the environment variables automatically.

---

## 📡 API Reference

| Method | Endpoint | Description | Query / Path Params |
|---|---|---|---|
| `GET` | `/` | Health check & model status | None |
| `GET` | `/api/movies/search` | Search movie titles with real posters | `q` (string, required), `limit` (int, default 20) |
| `GET` | `/api/movies/{movie_id}` | Detailed movie information | `movie_id` (int, TMDB ID) |
| `GET` | `/api/recommend/{title}` | Top 5 AI recommendations with posters | `title` (string, movie title) |
| `GET` | `/api/genres` | Available genres list | None |

---

## 🧠 ML Model Architecture

- **Dataset**: TMDB 5,000 Movies & Credits (4,806 deduplicated and cleaned titles).
- **Extracted Metadata**: Overview text, genre keywords, top 3 credited actors, and film director.
- **Preprocessing**: Removal of whitespace within entity names, Porter Stemming on consolidated tags.
- **Vectorization**: `CountVectorizer(max_features=5000, stop_words='english')`.
- **Similarity Metric**: Cosine similarity between 5,000-dimensional tag vectors:
  $$\text{Cosine Similarity}(u, v) = \frac{u \cdot v}{\|u\| \|v\|}$$
- **Inference**: Looks up the row index for a given title, retrieves similarity scores across all 4,806 films, and returns the top 5 highest-scoring movies (excluding itself).
