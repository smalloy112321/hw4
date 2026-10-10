# Campus Customs — Homework 4

A customer website for Campus Customs (officially licensed Yale Bulldog apparel) with a helpful chatbot.

- **Front end:** React + Vite + TypeScript. Shoppers browse products, filter by color and size, sort by price, open product pages, and create an account or log in.
- **Back end:** Python FastAPI. The chatbot's brain is a PydanticAI agent ("Handsome Dan") that answers honestly about price and stock from the local SQLite database, shows matching products on the page as cards, and remembers logged-in shoppers' chats.

> **The data pack, real `.env`, and product photos are not in this repo.** Follow step 1 below to add them.

---

## Requirements

- Python 3.11+ (built and tested with 3.14)
- Node.js 20+ and npm (built and tested with Node 24)
- A Portkey API key for the chatbot

## 1. Place the data pack

Copy the course data pack into `data/`:

```
hw4/
  data/
    campus_customs.db      ← the SQLite database
    products/              ← the 102 product photos (*.jpg)
    README.md
```

## 2. One-time setup

From the `hw4` folder:

```bash
# Python environment for the back end (kept outside backend/ so uvicorn --reload ignores it)
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

# Secrets: copy the example, then fill in PORTKEY_API_KEY and SESSION_SECRET
cp .env.example .env

# Home-page collection tiles, built from the product photos (optional but recommended)
.venv/bin/python scripts/build_collection_tiles.py

# Front-end packages
cd frontend
npm install
```

`.env` settings:
- `PORTKEY_API_KEY` is used for all model calls, which go through Portkey.
- `SESSION_SECRET` is any long random string. It signs login cookies.

## 3. Run the back end (terminal 1)

```bash
cd backend
source ../.venv/bin/activate
uvicorn main:app --reload --port 8000
```

- API: http://127.0.0.1:8000. Interactive docs: http://127.0.0.1:8000/docs.
- `--reload` restarts the server when a `.py` file in `backend/` changes. Edits to the system prompt (`backend/prompts/prompt.md`) apply on the next chat message.

## 4. Run the front end (terminal 2)

```bash
cd frontend
npm run dev
```

Open **http://127.0.0.1:5173**. Start the back end first: Vite forwards `/api/*` and `/images/*` to it on port 8000.

## 5. Try it

- **Log in** with the seeded test user from the data pack (`test@campuscustoms.yale.edu`), or **Create Account**. New accounts are written to the `users` table.
- **Shop:** Products → Color / Size in stock / Sort by price, or Products ▾ → a collection. Click any card for its product page.
- **Chat:** click **Chat with Handsome Dan** (bottom right). For example:
  - "Show me your hoodies." Matching product cards appear at the top of the page.
  - "How many XL Boola Boola tees are left?" The answer is an exact count from the database.
  - On a product page: "Does this come in pink?"
  - Log in, chat, and come back later. Your conversation reloads.

## Stopping cleanly

Press Ctrl+C in each terminal. `uvicorn --reload` runs a parent and a worker process, so confirm both ports are free before restarting:

```bash
lsof -i :8000
```

```bash
lsof -i :5173
```

If anything is still listed, stop it with `kill <pid>`.

---

## What's where

```
hw4/
  README.md                 this file
  AI_prompts.md             prompt log, one section per problem
  requirements.txt          Python packages for the back end (and the tile script)
  .env.example              variable names with placeholders only (copy to .env)
  data/README.md            where the data pack goes (the pack itself is git-ignored)
  scripts/
    build_collection_tiles.py   builds Home-page tiles from data/products (Pillow)
  backend/                  FastAPI app — run from here with uvicorn
    main.py                 API: products, images, accounts, chat, chat history
    auth.py                 password hashing (PBKDF2), signed session cookies, login lockout
    chat_history.py         saves and reloads logged-in shoppers' chats (chat_messages table)
    agent.py                ┐
    tools.py                │ the agent (four files)
    models.py               │
    prompts/prompt.md       ┘
  frontend/                 React + Vite + TypeScript
    src/pages/              Home, Products, ProductPage (PDP), About, Login, CreateAccount, NotFound
    src/components/         NavBar, Logo, ProductCard, ChatWidget, ChatResultsPanel, HandsomeDan, …
    src/api.ts              typed client for the FastAPI routes
  output/
    harness.md              how the system works: specs and limits, models, tools, safety, audit
    usability.md            Problem 9 usability improvements and why they help
    design.md               Problem 10 storefront design choices
    app_check.html          Problem 11 live-site test page (open it directly in a browser)
    app_check_images/       screenshots used by app_check.html
    audit_trail.json        append-only log of every agent run (tools, args, results, stop reason)
```

### The agent (four files in `backend/`)

| File | Role |
|---|---|
| `prompts/prompt.md` | System prompt: Handsome Dan's voice, honesty rules for price and stock, page and customer context, and safety rules. |
| `agent.py` | Builds the Portkey-routed model (`gpt-6-astra`), the agent, its deps (who's chatting and which page they're on), loop limits, and the audit trail. |
| `tools.py` | Read-only database tools: `search_products`, `get_product_info`, `check_stock`, `suggest_alternatives` (plus `get_shopper_profile`, registered in `agent.py`). |
| `models.py` | Pydantic types for tool results, the agent's structured output, the chat API, and audit entries. |

See `output/harness.md` for the full reference: architecture, specs and limits, every model field and why it was chosen, tools, safety rules, and the audit trail.

## Dependencies

- **Back end:** `fastapi`, `uvicorn`, `python-dotenv`, `pydantic-ai-slim[openai]`, and `pillow`, which is used only by the tile script. SQLite, password hashing, and cookie signing use Python's standard library.
- **Front end:** the Vite React template plus three deliberate additions:
  - `react-router-dom` for real page URLs and the Back button
  - `@fontsource/graduate`, `@fontsource/cormorant-garamond`, and `@fontsource/lato`, the logo, heading, and body fonts, bundled locally so the site makes no Google Fonts calls

## Security notes

- Secrets come only from `.env`, which is git-ignored. `.env.example` holds placeholders.
- Passwords are stored only as salted PBKDF2-HMAC-SHA256 hashes (120,000 rounds, `pbkdf2_sha256$salt$hash`, as the assignment specifies).
- Sessions use a signed, HttpOnly, SameSite=Lax cookie.
- Login is locked after 5 failed attempts in 15 minutes.
- The agent's tools open the database read-only. The agent sees only the current shopper's name, own email, join date, and chat, never password hashes or other customers' data.
