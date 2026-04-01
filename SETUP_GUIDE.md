# MediBot — Setup Guide

## Quick Start

```bash
pip install flask
python app.py
```

Open `http://localhost:8080` in your browser.

---

## Pages

| URL | Description |
|-----|-------------|
| `/` | Landing page |
| `/chat` | Chat interface |
| `/health` | Health check — returns `{"status":"ok","conditions":<count>}` |
| `/search?q=<query>` | Topic autocomplete — returns matching condition names |
| `/history` | Returns current session chat history as JSON |
| `/clear` | POST — clears session chat history |
| `/get` | POST — send a message, returns bot response |

---

## Features

### Chat
- Session-based history — persists across page refreshes, clears after 2 hours of inactivity
- Autocomplete — suggests matching topics as you type (min 2 chars)
- Follow-up chips — contextual suggestions after each bot reply
- Copy button — copies any bot message to clipboard
- Thumbs up/down feedback per message
- Export chat — downloads full conversation as `.txt`
- Message search — `Ctrl+F` to search within the conversation
- Scroll to top button
- `Ctrl+K` to focus the input from anywhere

### Landing page
- FAQ accordion
- "How it works" section
- Live chat preview
- Topic pills
- Testimonials
- Smooth scroll, scroll-reveal animations, count-up stats
- `Ctrl+K` to jump straight to chat

### PWA
- Installable on mobile via "Add to Home Screen"
- Service worker caches static assets for offline use
- `static/manifest.json`, `static/sw.js`, `static/icon-192.svg`, `static/icon-512.svg`

### Backend
- Rate limiting — max 20 requests/minute per IP
- Input sanitization — HTML-escaped, capped at 500 chars
- Session expiry — 2 hours
- `/health` endpoint for uptime monitoring

---

## Project structure

```
app.py                  # Flask app — all routes and knowledge base
templates/
  index.html            # Landing page
  chat.html             # Chat interface
  404.html              # 404 error page
static/
  style.css             # Print stylesheet + accessibility
  favicon.svg           # Browser tab icon
  manifest.json         # PWA manifest
  sw.js                 # Service worker
  icon-192.svg          # PWA home screen icon
  icon-512.svg          # PWA splash icon
  robots.txt            # Crawler rules
Medical-Chatbot-master/ # Original RAG-based implementation (advanced)
```

---

## Emergency numbers (configured for India)

- Emergency: **102**
- Poison Control: 1-800-222-1222
- Mental health crisis: **988**

Update these in `app.py` response text and `templates/index.html` FAQ if needed.

---

## Notes

- This is a development server. For production use a WSGI server like Gunicorn:
  ```bash
  pip install gunicorn
  gunicorn -w 4 -b 0.0.0.0:8080 app:app
  ```
- All responses are for educational purposes only — not a substitute for professional medical advice.
