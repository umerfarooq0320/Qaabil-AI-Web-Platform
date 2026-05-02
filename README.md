# 🧠 QABIL — AI-Native Assessment & Career Platform

> A multi-agent AI system that dynamically assesses users, builds evolving intelligence profiles, generates adaptive learning paths, and produces verified career passports.

This repository contains the complete QABIL platform, including both the **FastAPI + LangGraph Backend** and the **Streamlit Frontend**.

---

## ⚡ Quick Start Guide

Follow these steps to set up the project on your local machine.

### 1. Prerequisites

Before you begin, ensure you have the following installed:
- **Python 3.11+** — [Download Python](https://python.org)
- **PostgreSQL 15+** — [Download](https://postgresql.org) (or use [Supabase](https://supabase.com) free tier)
- **MongoDB 7+** — [Download](https://mongodb.com) (or use [Atlas](https://cloud.mongodb.com) free tier)
- **Git** — [Download Git](https://git-scm.com/)

### 2. Clone and Setup Environment

Open your terminal or command prompt and run:

```bash
# 1. Clone the repository
git clone https://github.com/AreebaaKhan/GenAi-Hackathon.git
cd GenAi-Hackathon

# 2. Create a virtual environment
python -m venv venv

# 3. Activate the virtual environment
# On Windows:
.\venv\Scripts\activate
# On Mac/Linux:
# source venv/bin/activate

# 4. Install all dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration

You need to set up your environment variables for API keys and databases.

```bash
# Copy the example environment file
copy .env.example .env   # (On Windows)
# cp .env.example .env   # (On Mac/Linux)
```
Open the `.env` file in your code editor and fill in your keys:
- `OPENROUTER_API_KEY` — Get from [openrouter.ai](https://openrouter.ai)
- `POSTGRES_URL` — Your PostgreSQL connection string
- `MONGODB_URL` — Your MongoDB connection string
- `JWT_SECRET` — A random secret string for security

### 4. Database Setup

Ensure your PostgreSQL server is running. Create a new database named `qabil`:

```sql
-- Run this in psql or pgAdmin:
CREATE DATABASE qabil;
```

---

## 🚀 Running the Application

You will need to open **two separate terminal windows** to run the backend and frontend simultaneously. Make sure your virtual environment is activated in both terminals!

### Terminal 1: Run the Backend (FastAPI)
```bash
# Starts the backend server
uvicorn app.main:app --reload --port 8000
```
* **API Documentation:** [http://localhost:8000/docs](http://localhost:8000/docs)

### Terminal 2: Run the Frontend (Streamlit)
```bash
# Starts the interactive UI
cd frontend
streamlit run Home.py
```
* **Web Interface:** The terminal will provide a `Local URL` (usually `http://localhost:8501`) that will open automatically in your browser.

---

## 🏗️ Architecture Overview

```text
Streamlit Frontend ↔ FastAPI Backend ↔ LangGraph Orchestrator ↔ AI Agents
                           ↕                                        ↕
                   PostgreSQL + MongoDB                     OpenRouter LLMs
```

## 🤖 Multi-Agent System

| Agent | Purpose | Trigger |
|-------|---------|---------|
| **Assessor** | Conducts adaptive quizzes & scores | New user / quiz answer |
| **Profiler** | Builds intelligence profiles | Quiz complete |
| **Coach (Rahnuma)**| Voice & communication feedback | Voice upload |
| **Task** | Generates real-world scenario tasks | User request |
| **Supervisor** | Engagement & drop-off monitoring | Daily login / inactivity |
| **Verifier** | Validates trust & fraud detection | Task submission |
| **Career** | Career passport + job matching | Progress update |

## 📡 Key API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/signup` | Create an account |
| POST | `/api/v1/auth/login` | Retrieve JWT token |
| GET | `/api/v1/profile/me` | Fetch user profile |
| POST | `/api/v1/quiz/start` | Start adaptive quiz |
| POST | `/api/v1/tasks/generate`| Generate AI task |
| GET | `/api/v1/career/passport`| View career passport |

## 👥 Contributors
- **Backend & AI System:** FastAPI, LangGraph, PostgreSQL, MongoDB.
- **Frontend & UI:** Streamlit.

