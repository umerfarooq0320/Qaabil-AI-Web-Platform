# 🧠 QABIL — AI-Native Assessment & Career Platform

> A multi-agent AI system that dynamically assesses users, builds evolving intelligence profiles, generates adaptive learning paths, and produces verified career passports.

## ⚡ Quick Start

### 1. Prerequisites

- **Python 3.11+** — [Download](https://python.org)
- **PostgreSQL 15+** — [Download](https://postgresql.org) (or use [Supabase](https://supabase.com) free tier)
- **MongoDB 7+** — [Download](https://mongodb.com) (or use [Atlas](https://cloud.mongodb.com) free tier)  
- **Redis** — Optional for caching ([Memurai](https://memurai.com) for Windows)

### 2. Setup

```powershell
# Clone into project folder
cd "c:\Users\TS\Desktop\GenAi Hacakthon"

# Create & activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env
# Edit .env with your API keys and database URLs
```

### 3. Database Setup

```sql
-- In PostgreSQL (psql or pgAdmin):
CREATE DATABASE qabil;
```

### 4. Run Server

```powershell
uvicorn app.main:app --reload --port 8000
```

### 5. Open API Docs

Navigate to: **http://localhost:8000/docs**

---

## 🏗️ Architecture

```
Streamlit/Web → FastAPI Backend → LangGraph Orchestrator → AI Agents
                     ↕                                        ↕
              PostgreSQL + MongoDB                     OpenRouter LLMs
```

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/signup` | Create account |
| POST | `/api/v1/auth/login` | Get JWT token |
| GET | `/api/v1/profile/me` | Get user profile |
| PATCH | `/api/v1/profile/me` | Update profile |
| GET | `/api/v1/profile/learning-path` | AI learning path |
| POST | `/api/v1/quiz/start` | Start adaptive quiz |
| POST | `/api/v1/quiz/{id}/answer` | Submit answer |
| GET | `/api/v1/quiz/{id}/report` | Get quiz report |
| POST | `/api/v1/tasks/generate` | Generate AI task |
| POST | `/api/v1/tasks/{id}/submit` | Submit task |
| GET | `/api/v1/tasks/history` | Task history |
| POST | `/api/v1/coach/voice` | Voice analysis |
| POST | `/api/v1/coach/feedback` | Get coaching |
| GET | `/api/v1/career/passport` | Career passport |
| GET | `/api/v1/career/jobs` | Job matches |

## 🤖 AI Agents

| Agent | Purpose | Trigger |
|-------|---------|---------|
| **Assessor** | Adaptive quiz + scoring | New user / quiz answer |
| **Profiler** | Intelligence profile | Quiz complete |
| **Coach (Rahnuma)** | Voice/communication feedback | Voice upload |
| **Task** | Real-world task generation | User request |
| **Supervisor** | Engagement monitoring | Daily login / inactivity |
| **Verifier** | Trust & fraud detection | Task submission |
| **Career** | Passport + job matching | Progress update |

## 🔑 Environment Variables

Edit `.env` with:
- `OPENROUTER_API_KEY` — Get from [openrouter.ai](https://openrouter.ai)
- `POSTGRES_URL` — Your PostgreSQL connection string
- `JWT_SECRET` — Random secret for JWT tokens

## 👥 Team

- **Backend**: FastAPI (this repo)
- **Frontend**: Streamlit (separate repo)
- **AI Agents**: Contributed individually
