# ⚽ FIONAH ENGINE v1.0
**Football Intelligence & Odds Normalization Heuristic Architecture**

A production-grade, 10-pillar quantitative soccer prediction syndicate engine. Built with strict mathematical guardrails: Zero LLM math, RapidFuzz entity resolution, Dixon-Coles bivariate Poisson, Shin de-vigging, and orthogonal disjoint accumulator building with Fractional Kelly staking.

## 🏗️ Architecture
- **Backend**: Python, FastAPI, Uvicorn, RapidFuzz, SciPy, NumPy
- **Frontend**: Vanilla HTML/JS/CSS (Zero dependencies, ultra-fast)
- **Deployment**: Render (Backend API) + Vercel (Frontend UI)

## 🛡️ Strict Guardrails Enforced
1. **No LLM Mathematical Calculations**: All probabilities, EV, and odds are computed via deterministic Python (`scipy`/`math`).
2. **No Hardcoded Multipliers**: Uses Shin (1993) de-biasing and Elo-derived Poisson lambdas.
3. **No Invented Entities**: RapidFuzz gatekeeper hard-rejects any team name with <85% canonical match confidence.
4. **Disjoint Acca Sets**: Accumulator builder enforces `Slip A ∩ Slip B = ∅` to prevent overlapping match risk.

## 🚀 Deployment Instructions

### Step 1: GitHub
1. Create a new repository on GitHub named `fionah-engine`.
2. Push all the files above into the root of the repository.

### Step 2: Render (Backend)
1. Go to [render.com](https://render.com) and create a new **Web Service**.
2. Connect your GitHub repository.
3. Configure the service:
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT`
4. Click **Create Web Service**. Note the generated URL (e.g., `https://fionah-engine.onrender.com`).

### Step 3: Vercel (Frontend)
1. Go to [vercel.com](https://vercel.com) and click **Add New Project**.
2. Import your `fionah-engine` GitHub repository.
3. Configure the project:
   - **Framework Preset**: Other
   - **Root Directory**: `frontend`
   - **Build Command**: Leave blank
   - **Output Directory**: Leave blank
4. Click **Deploy**.

### Step 4: Connect Frontend to Backend
1. Open `frontend/index.html` in your code editor.
2. Find line ~185: `const API_BASE = ...`
3. Replace `"https://YOUR-RENDER-URL.onrender.com"` with your actual Render backend URL.
4. Commit and push the change to GitHub. Vercel will auto-redeploy.

## 📊 Usage
1. Open your Vercel frontend URL.
2. Paste raw bookmaker text (e.g., `Arsenal vs Chelsea 1.95 3.60 4.20`).
3. Click **Run Quantitative Evaluation**.
4. The engine will strip UI chrome, verify entities via RapidFuzz, compute Dixon-Coles probabilities, de-vig via Shin, and output verified predictions + orthogonal accumulators. Unverified fixtures are explicitly rejected and displayed separately.
