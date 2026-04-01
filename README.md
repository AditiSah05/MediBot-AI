# MediBot

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-latest-green.svg)](https://flask.palletsprojects.com/)
[![Deployed on Render](https://img.shields.io/badge/Render-deployed-46E3B7.svg)](https://medibot-ai-5e3j.onrender.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An AI health information assistant built with Flask. Ask about symptoms, conditions, medications, vaccines, and more — instantly, for free.

**Live:** [https://medibot-ai-5e3j.onrender.com](https://medibot-ai-5e3j.onrender.com/)

---

## Quick start

```bash
pip install -r requirements.txt
python app.py
```

Open `http://localhost:8080`.

---

## Pages

| URL | Description |
|-----|-------------|
| `/` | Landing page |
| `/chat` | Chat interface |
| `/health` | Health check JSON |
| `/search?q=` | Topic autocomplete |
| `/history` | Session chat history |
| `/clear` | Clear session history |
| `/get` | POST — send a message |

---

## Features

**Chat**
- 100+ medical conditions in the knowledge base
- Session history — persists on refresh, expires after 2 hours
- Autocomplete — topic suggestions as you type
- Follow-up chips — contextual questions after each reply
- Message search (`Ctrl+F`), copy, thumbs feedback
- Export chat as `.txt`
- `Ctrl+K` to focus input

**Landing page**
- How it works, topic pills, FAQ accordion, testimonials
- Scroll-reveal animations, count-up stats
- `Ctrl+K` to jump to chat

**PWA**
- Installable on mobile via "Add to Home Screen"
- Service worker for offline static asset caching

**Backend**
- Rate limiting — 20 req/min per IP
- Input sanitization — HTML-escaped, 500 char limit
- `/health` endpoint for uptime monitoring

---

## Project structure

```
app.py                  # Flask app — routes + knowledge base
requirements.txt        # Python dependencies
Dockerfile              # Docker image definition
render.yaml             # Render deployment blueprint
docker-compose.yml      # Local Docker Compose config
templates/
  index.html            # Landing page
  chat.html             # Chat interface
  404.html              # 404 page
static/
  style.css             # Print stylesheet + accessibility
  favicon.svg           # Browser tab icon
  manifest.json         # PWA manifest
  sw.js                 # Service worker
  icon-192.svg          # PWA icon
  icon-512.svg          # PWA splash icon
  robots.txt            # Crawler rules
```

---

## Deploy to Render

1. Push your code to GitHub
2. Go to [render.com](https://render.com) → **New +** → **Web Service**
3. Connect your repo (settings auto-detected from `render.yaml`)
4. Leave **Root Directory** empty
5. Click **Create Web Service**

The app will be live at `https://<your-service>.onrender.com`.

---

## Deploy with Docker

```bash
docker build -t medibot .
docker run -p 8080:8080 medibot
```

Or via Docker Compose:

```bash
docker-compose up --build
```

---

## Production

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8080 app:app
```

---

## Medical categories covered

Respiratory · Cardiovascular · Endocrine · Gastrointestinal · Mental Health · Musculoskeletal · Skin · Infectious Diseases · Neurological · Eye & Ear · Kidney & Urological · Women's Health · Men's Health · Pediatrics · Nutrition · Sleep · Emergency · Vaccines

---

## Emergency numbers

- Emergency: **102**
- Poison Control: 1-800-222-1222
- Mental health crisis: **988**

---

## Disclaimer

MediBot provides general health information for educational purposes only. It is not a substitute for professional medical advice, diagnosis, or treatment. Always consult a qualified healthcare provider.

---

**Author: Aditi Sah** · Licensed under MIT
