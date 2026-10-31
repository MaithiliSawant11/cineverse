# 🎬 CINEVERSE — AI-Powered Movie Recommendation Engine

CINEVERSE is a full-stack, machine learning-powered movie recommendation platform built with **FastAPI**, **React 19**, **TypeScript**, **Tailwind CSS v4**, and **Framer Motion**. It uses **Content-Based Filtering** with **Cosine Similarity** on the TMDB 5,000 movie dataset (4,806 processed movies).

---

## 🌟 Key Features

- **Exact ML Engine Preserved**: Uses the pre-computed 4,806 × 4,806 cosine similarity matrix (`similarity.pkl`) without retraining or altering recommendation accuracy.
- **Configurable TMDB Integration**: Works out-of-the-box **with or without a TMDB API key**. When no key is provided, the platform displays elegant fallback UI states with gradient placeholders for posters, ratings, and overviews.
- **Production-Ready Architecture**:
  - **Backend**: FastAPI with lifespan-based singleton ML model loading (loads once on startup into memory).
  - **Frontend**: React 19 + Vite + TypeScript + Tailwind CSS v4 + Framer Motion animated cards & modals.
  - **Git LFS**: Pre-configured for the 176 MB `similarity.pkl` file.
  - **Deployment**: Dockerfile + `render.yaml` with `lfsEnabled: true` for Render, and zero-config Vercel support.

---

## 📁 Repository Structure

```
CINEVERSE/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application, CORS, lifespan & endpoints
│   │   ├── recommender.py       # ML singleton service (loads .pkl artifacts)
│   │   ├── models.py            # Pydantic schemas & response validation
│   │   └── tmdb.py              # Async TMDB API client with graceful fallback
│   ├── models/
│   │   ├── movie_list.pkl       # 4,806-row DataFrame (movie_id, title, tags)
│   │   ├── similarity.pkl       # 4,806 × 4,806 cosine similarity matrix (176 MB, Git LFS)
│   │   └── count_vectorizer.pkl # CountVectorizer vocabulary
│   ├── tests/
│   │   └── test_recommendation_flow.py  # End-to-end automated test suite
│   ├── .env.example             # Backend environment template
│   ├── requirements.txt         # Pinned Python dependencies
│   ├── Dockerfile               # Container definition for Render / Cloud deploy
│   └── render.yaml              # Render Blueprint specification
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
│   └── vite.config.ts           # Vite + Tailwind + React plugin setup
│
├── datasets/                    # Reference raw datasets (kept intact)
├── .gitattributes               # Git LFS tracking rules for *.pkl
└── README.md                    # Project documentation & deployment guide
```

---

## 🚀 Running Locally

### Prerequisites
- **Python**: 3.10, 3.11, or 3.13
- **Node.js**: v18+ or v20+
- **Git LFS**: [Download Git LFS](https://git-lfs.com/)

---

### 1. Backend Setup

```bash
cd backend

# Create virtual environment (recommended)
python -m venv venv
# Windows:
.\venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
# Copy .env.example to .env
cp .env.example .env
```

Edit `backend/.env` (optional):
```ini
# TMDB API Key (optional): leave as placeholder for graceful fallback mode
TMDB_API_KEY=your_tmdb_api_key_here

# Allowed origins for CORS (default covers Vite standard ports)
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000,http://localhost:4173

# Port
PORT=8000
```

Start the FastAPI server:
```bash
python -m uvicorn app.main:app --reload --port 8000
```

- API Base URL: `http://localhost:8000`
- Interactive Swagger UI: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/`

---

### 2. Frontend Setup

In a new terminal window:

```bash
cd frontend

# Install npm dependencies
npm install

# Create local environment file
cp .env.example .env
```

Ensure `frontend/.env` points to the local backend:
```ini
VITE_API_URL=http://localhost:8000
```

Start the Vite development server:
```bash
npm run dev
```

Open your browser at `http://localhost:5173`.

---

## 🧪 Testing the Recommendation Flow

Run the comprehensive test suite to verify model loading, recommendations, search, TMDB fallbacks, and error handling:

```bash
python backend/tests/test_recommendation_flow.py
```

The test validates:
1. `GET /`: Confirms 4,806 movies and `(4806, 4806)` matrix loaded in memory.
2. `GET /api/recommend/Avatar`: Asserts 5 top matches (`Aliens vs Predator: Requiem`, `Aliens`, `Falcon Rising`, `Independence Day`, `Titan A.E.`).
3. Graceful fallback: Verifies responses remain stable and typed when TMDB metadata is unavailable.
4. `GET /api/recommend/InvalidMovie123`: Asserts clean HTTP 404 response with an informative error message.
5. `GET /api/movies/search?q=Dark%20Knight`: Verifies autocomplete and substring search.
6. `GET /api/movies/19995`: Verifies movie detail retrieval.

---

## 🌐 Deployment Instructions

### Backend Deployment (Render)

The backend includes a pre-configured `Dockerfile` and `backend/render.yaml`. Because `similarity.pkl` is 176 MB, Git LFS must be used.

#### Step 1: Ensure Git LFS is Active in Your Repository
```bash
git lfs install
git add .gitattributes
git add backend/models/*.pkl
git commit -m "Configure Git LFS for model pickle files"
git push origin main
```

#### Step 2: Deploy on Render
1. Log in to [Render](https://render.com/).
2. Click **New +** → **Blueprint** (or **Web Service**).
3. Connect your GitHub repository.
4. Render will read `backend/render.yaml` automatically:
   - **Runtime**: Docker
   - **Docker Context**: `./backend`
   - **Dockerfile Path**: `./backend/Dockerfile`
   - **lfsEnabled**: `true` *(ensures Render pulls the 176 MB file instead of just the pointer)*
5. In the Render Environment Variables settings:
   - `TMDB_API_KEY`: *(Optional)* Paste your key from [TMDB Settings](https://www.themoviedb.org/settings/api). If left empty, graceful fallbacks will automatically be used.
   - `ALLOWED_ORIGINS`: Add your deployed frontend URL (e.g., `https://cineverse.vercel.app`).
6. Deploy! Render will build the Docker container and expose your API (e.g., `https://cineverse-backend.onrender.com`).

---

### Frontend Deployment (Vercel)

1. Push your repository to GitHub.
2. Go to [Vercel](https://vercel.com/) and click **Add New...** → **Project**.
3. Select your repository.
4. Set the **Root Directory** to `frontend`.
5. Set the **Framework Preset** to `Vite`.
6. Under **Environment Variables**, add:
   - `VITE_API_URL` = `https://cineverse-backend.onrender.com` (your Render backend URL)
7. Click **Deploy**.

---

## 📡 API Reference

| Method | Endpoint | Description | Query / Path Params |
|---|---|---|---|
| `GET` | `/` | Health check & model status | None |
| `GET` | `/api/movies/search` | Search movie titles | `q` (string, required), `limit` (int, default 20) |
| `GET` | `/api/movies/{movie_id}` | Detailed movie information | `movie_id` (int, TMDB ID) |
| `GET` | `/api/recommend/{title}` | Top 5 AI recommendations | `title` (string, movie title) |
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
