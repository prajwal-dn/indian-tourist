---
title: Indian Tourist
emoji: 🕌
colorFrom: yellow
colorTo: green
sdk: docker
pinned: false
---

<div align="center">

# 🏛️ Discover India
### AI-Powered Travel Concierge for the Indian Subcontinent

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.x-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![OpenRouter](https://img.shields.io/badge/OpenRouter-AI-6C47FF?style=for-the-badge&logo=openai&logoColor=white)](https://openrouter.ai)
[![Docker](https://img.shields.io/badge/Docker-Deployed-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://huggingface.co/spaces/praj-9035/indian-tourist)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

**[🚀 Live Demo →](https://huggingface.co/spaces/praj-9035/indian-tourist)**

*Discover India's hidden gems with the power of generative AI — personalized travel recommendations, real-time imagery, and a premium glassmorphism UI, all in one place.*

</div>

---

## 📸 Preview

> A sleek, dark-mode travel interface — select your state, choose your travel style, and get AI-curated destinations with live photography in seconds.

---

## 🎯 What This Project Does

**Discover India** is a full-stack AI web application that generates **personalized travel recommendations** across India's 28 states. Users pick a state and an interest (beaches, history, adventure, spirituality, etc.) and receive 4 tailored destination cards — each with a description, best travel time, local tips, and a live photo pulled from Pexels.

This project demonstrates a real-world integration of **LLM inference**, **third-party REST APIs**, **resilient backend design**, and **premium UI/UX** — all shipped via Docker on Hugging Face Spaces.

---

## ✨ Key Features

| Feature | Detail |
|---|---|
| 🧠 **AI-Powered Recommendations** | Uses OpenRouter to route prompts to top LLMs (Google Gemma 4, NVIDIA Nemotron) for nuanced, contextual travel curation |
| 🔄 **Multi-Model Fallback** | Automatic retry logic across multiple free LLMs with exponential backoff — zero single point of failure |
| 🖼️ **Live Travel Photography** | Pexels API integration fetches real, high-res destination photos dynamically per result |
| 💎 **Premium Glassmorphism UI** | Custom CSS design system — dark mode, gold accents, blur effects, and fluid micro-animations |
| 📱 **Fully Responsive** | Mobile-first layout that scales beautifully across all screen sizes |
| ☁️ **Dockerized & Cloud-Deployed** | Runs as a containerized app on Hugging Face Spaces — zero infrastructure management |
| ⚡ **Fast & Lightweight** | No heavy JS frameworks — vanilla HTML/CSS/JS frontend keeps the bundle tiny and load time minimal |

---

## 🛠️ Tech Stack

```
┌─────────────────────────────────────────────────────┐
│                   DISCOVER INDIA                    │
├─────────────────┬───────────────────────────────────┤
│   FRONTEND      │   HTML5 · CSS3 · Vanilla JS ES6+  │
│   BACKEND       │   Python 3.9+ · Flask · Flask-CORS │
│   AI ENGINE     │   OpenRouter API (multi-model)     │
│                 │   → Google Gemma 4 27B             │
│                 │   → NVIDIA Nemotron 3.5            │
│                 │   → Google Gemma 4 31B             │
│   IMAGERY       │   Pexels REST API                  │
│   CONFIG        │   python-dotenv                    │
│   DEPLOYMENT    │   Docker · Hugging Face Spaces     │
└─────────────────┴───────────────────────────────────┘
```

---

## 🏗️ Architecture

```
User Request
    │
    ▼
┌─────────────┐       ┌──────────────────────┐
│  Flask App  │──────▶│  OpenRouter API       │
│  (app.py)   │       │  Multi-model fallback │
│             │◀──────│  Gemma / Nemotron     │
└──────┬──────┘       └──────────────────────┘
       │
       ▼
┌─────────────┐       ┌──────────────────────┐
│  Pexels API │◀──────│  image_keyword        │
│  (photos)   │──────▶│  from AI response     │
└──────┬──────┘       └──────────────────────┘
       │
       ▼
┌─────────────┐
│  index.html │  ← Rendered destination cards
│  (Jinja2)   │    with glassmorphism UI
└─────────────┘
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- [OpenRouter API Key](https://openrouter.ai/settings/keys) *(free tier available)*
- [Pexels API Key](https://www.pexels.com/api/) *(free)*

### Local Setup

```bash
# 1. Clone the repository
git clone https://github.com/yes999praj-max/indian-tourist.git
cd indian-tourist

# 2. Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.example .env
# Edit .env and add your API keys

# 5. Run the application
python app.py
# → Open http://127.0.0.1:7860
```

### Environment Variables

```env
OPENROUTER_API_KEY=sk-or-v1-your_key_here
PEXELS_API_KEY=your_pexels_key_here
```

---

## 🐳 Docker

```bash
# Build the image
docker build -t discover-india .

# Run the container
docker run -p 7860:7860 \
  -e OPENROUTER_API_KEY=your_key \
  -e PEXELS_API_KEY=your_key \
  discover-india
```

---

## 📁 Project Structure

```
indian-tourist/
├── app.py              # Flask backend — routes, AI calls, image fetching
├── requirements.txt    # Python dependencies
├── Dockerfile          # Container config for Hugging Face Spaces
├── .env                # Local secrets (not committed)
├── templates/
│   └── index.html      # Single-page frontend (HTML + CSS + JS)
└── static/
    └── hero.png        # Fallback hero image
```

---

## 💡 Engineering Highlights

- **Resilient LLM Integration**: Implemented a custom retry engine that cycles through multiple LLM models with exponential backoff — ensuring near-100% uptime even when individual models are rate-limited or unavailable.
- **Dynamic Model Discovery**: Model list is kept current by querying the OpenRouter `/models` endpoint to filter only the models with free pricing.
- **Clean JSON Parsing**: Used regex extraction + `json.loads` with graceful error handling to reliably parse structured AI output, even when models include extra markdown or prose.
- **Zero-dependency Frontend**: The entire UI is built in vanilla HTML/CSS/JS — no React, no Vue, no build step. Fast, maintainable, and dependency-free.

---

## 🔒 Security

- All API keys are stored as **environment variables** — never hardcoded.
- For Hugging Face deployment, keys are stored as **Repository Secrets** in Space settings.
- `.env` is listed in `.gitignore` to prevent accidental commits.

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you'd like to change.

---

<div align="center">

Made with ♥ by **[Prajwal DN](https://github.com/yes999praj-max)**

*If you found this useful, consider giving it a ⭐ on GitHub!*

</div>
