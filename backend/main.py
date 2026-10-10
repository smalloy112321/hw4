"""Campus Customs API: serves products, stock, and product photos from the local database.

Run from backend/:  uvicorn main:app --reload --port 8000
Open API docs:      http://127.0.0.1:8000/docs
Frontend (Vite):    http://127.0.0.1:5173

Products (Problem 3), accounts via auth.py (Problem 4), and the shop chatbot via agent.py
(Problem 5): POST /api/chat sends one shopper message to the PydanticAI agent.
"""

from __future__ import annotations

import json
import re
import sqlite3
from pathlib import Path

from dotenv import load_dotenv

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
# .env can sit in this homework folder or a parent folder; the first value found wins.
for folder in (ROOT, *ROOT.parents[:3]):
    load_dotenv(folder / ".env")

from fastapi import Cookie, FastAPI, HTTPException, Query, Request, Response  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from fastapi.staticfiles import StaticFiles  # noqa: E402
from pydantic import BaseModel, Field, field_validator  # noqa: E402

import auth  # noqa: E402  (reads SESSION_SECRET, so it loads after .env)
import tools  # noqa: E402
import chat_history  # noqa: E402
from agent import MAX_HISTORY_TURNS, ChatDeps, run_chat  # noqa: E402
from models import ChatHistory, ChatRequest, ChatResponse, PageContext, PageView, ProductSuggestion  # noqa: E402

DB_PATH = ROOT / "data" / "campus_customs.db"
IMAGES_DIR = ROOT / "data" / "products"

SIZE_ORDER = ["XS", "S", "M", "L", "XL", "XXL"]

app = FastAPI(title="Campus Customs", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Product photos: /images/<file>.jpg
app.mount("/images", StaticFiles(directory=IMAGES_DIR), name="images")


class ProductSummary(BaseModel):
    product_id: str
    name: str
    garment_type: str
    description: str
    colors: list[str]
    price: float
    image_url: str
    in_stock: bool
    color_family: str | None = Field(description='Main garment color group for filtering, e.g. "Navy", "Gray".')
    sizes_in_stock: list[str] = Field(description="Sizes with at least one unit, XS to XXL.")


class SizeStock(BaseModel):
    size: str
    quantity: int
    in_stock: bool


class ProductDetail(ProductSummary):
    search_tags: list[str]
    sizes: list[SizeStock]


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def image_url(image_file_path: str) -> str:
    # The database stores "products/<file>.jpg"; photos are served from /images/<file>.jpg.
    return f"/images/{Path(image_file_path).name}"


def to_summary(row: sqlite3.Row) -> ProductSummary:
    return ProductSummary(
        product_id=row["product_id"],
        name=row["name"],
        garment_type=row["garment_type"],
        description=row["description"],
        colors=json.loads(row["colors"]),
        price=row["price"],
        image_url=image_url(row["image_file_path"]),
        in_stock=row["total_quantity"] > 0,
        color_family=tools.color_family(json.loads(row["colors"])),
        sizes_in_stock=tools.sort_sizes((row["sizes_in_stock"] or "").split(",")) if row["sizes_in_stock"] else [],
    )


PRODUCT_SQL = """
    SELECT c.*, COALESCE(SUM(i.quantity), 0) AS total_quantity,
           GROUP_CONCAT(CASE WHEN i.quantity > 0 THEN i.size END) AS sizes_in_stock
    FROM catalogue c LEFT JOIN inventory i ON i.product_id = c.product_id
"""


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/products", response_model=list[ProductSummary])
def list_products(q: str | None = Query(None, description="Optional text search")) -> list[ProductSummary]:
    sql, params = PRODUCT_SQL, []
    if q:
        like = f"%{q.strip()}%"
        sql += " WHERE c.name LIKE ? OR c.garment_type LIKE ? OR c.description LIKE ? OR c.search_tags LIKE ?"
        params = [like] * 4
    sql += " GROUP BY c.product_id ORDER BY c.name"
    with connect() as conn:
        return [to_summary(r) for r in conn.execute(sql, params)]


@app.get("/api/products/{product_id}", response_model=ProductDetail)
def get_product(product_id: str) -> ProductDetail:
    with connect() as conn:
        row = conn.execute(PRODUCT_SQL + " WHERE c.product_id = ? GROUP BY c.product_id", [product_id]).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Product not found")
        stock = {r["size"]: r["quantity"] for r in conn.execute(
            "SELECT size, quantity FROM inventory WHERE product_id = ?", [product_id]
        )}
    sizes = sorted(stock, key=lambda s: SIZE_ORDER.index(s) if s in SIZE_ORDER else len(SIZE_ORDER))
    return ProductDetail(
        **to_summary(row).model_dump(),
        search_tags=json.loads(row["search_tags"]),
        sizes=[SizeStock(size=s, quantity=stock[s], in_stock=stock[s] > 0) for s in sizes],
    )


# --- Accounts ---------------------------------------------------------------------------

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MIN_PASSWORD = 8
# Upper bound keeps one request from tying up the server hashing a huge string.
MAX_PASSWORD = 128


def normalize_email(value: str) -> str:
    email = value.strip().lower()
    if not EMAIL_RE.match(email) or len(email) > 254:
        raise ValueError("Enter a valid email address.")
    return email


class RegisterRequest(BaseModel):
    first_name: str = Field(min_length=1, max_length=60)
    last_name: str = Field(min_length=1, max_length=60)
    email: str
    password: str = Field(min_length=MIN_PASSWORD, max_length=MAX_PASSWORD)

    @field_validator("first_name", "last_name")
    @classmethod
    def strip_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Name cannot be blank.")
        return v

    @field_validator("email")
    @classmethod
    def check_email(cls, v: str) -> str:
        return normalize_email(v)


class LoginRequest(BaseModel):
    email: str = Field(max_length=254)
    password: str = Field(max_length=MAX_PASSWORD)


class User(BaseModel):
    id: int
    name: str
    first_name: str | None
    last_name: str | None
    email: str
    created_at: str


def to_user(row: sqlite3.Row) -> User:
    return User(
        id=row["id"],
        name=row["name"],
        first_name=row["first_name"],
        last_name=row["last_name"],
        email=row["email"],
        created_at=row["created_at"],
    )


def start_session(response: Response, user_id: int) -> None:
    # HttpOnly: page scripts (and any injected script) cannot read the cookie.
    # SameSite=Lax: other sites cannot make the browser send it on form posts (CSRF).
    response.set_cookie(
        auth.SESSION_COOKIE,
        auth.make_session_token(user_id),
        max_age=auth.SESSION_TTL_SECONDS,
        httponly=True,
        samesite="lax",
        secure=False,  # set True when served over HTTPS
        path="/",
    )


def current_user(token: str | None) -> User | None:
    user_id = auth.read_session_token(token)
    if user_id is None:
        return None
    with connect() as conn:
        row = conn.execute("SELECT * FROM users WHERE id = ?", [user_id]).fetchone()
    return to_user(row) if row else None


@app.post("/api/auth/register", response_model=User, status_code=201)
def register(body: RegisterRequest, response: Response) -> User:
    password_hash = auth.hash_password(body.password)
    try:
        with connect() as conn:
            cur = conn.execute(
                "INSERT INTO users (name, email, password_hash, first_name, last_name) VALUES (?, ?, ?, ?, ?)",
                [f"{body.first_name} {body.last_name}", body.email, password_hash, body.first_name, body.last_name],
            )
            row = conn.execute("SELECT * FROM users WHERE id = ?", [cur.lastrowid]).fetchone()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="An account with that email already exists. Try logging in.")
    start_session(response, row["id"])
    return to_user(row)


LOGIN_FAILED = "That email and password don't match our records."


@app.post("/api/auth/login", response_model=User)
def login(body: LoginRequest, request: Request, response: Response) -> User:
    email = body.email.strip().lower()
    keys = (f"email:{email}", f"ip:{request.client.host if request.client else 'unknown'}")
    if auth.too_many_failures(*keys):
        raise HTTPException(status_code=429, detail="Too many failed attempts. Wait 15 minutes and try again.")
    with connect() as conn:
        row = conn.execute("SELECT * FROM users WHERE email = ?", [email]).fetchone()
    # Always run one hash check so unknown emails are rejected just as slowly as wrong passwords.
    ok = auth.verify_password(body.password, row["password_hash"] if row else auth.DUMMY_HASH)
    if not row or not ok:
        auth.record_failure(*keys)
        raise HTTPException(status_code=401, detail=LOGIN_FAILED)
    auth.clear_failures(*keys)
    start_session(response, row["id"])
    return to_user(row)


@app.post("/api/auth/logout", status_code=204)
def logout(response: Response) -> None:
    response.delete_cookie(auth.SESSION_COOKIE, path="/")


@app.get("/api/auth/me", response_model=User)
def me(cc_session: str | None = Cookie(default=None)) -> User:
    user = current_user(cc_session)
    if user is None:
        raise HTTPException(status_code=401, detail="Not logged in.")
    return user


# --- Chat --------------------------------------------------------------------------------

chat_history.ensure_index()


def page_view(page: PageContext | None) -> PageView | None:
    """Check the page context the browser sent against the database before the agent sees it."""
    if page is None:
        return None
    product = None
    if page.product_id:
        with connect() as conn:
            row = conn.execute("SELECT product_id, name FROM catalogue WHERE product_id = ?", [page.product_id]).fetchone()
        if row:  # unknown ids are ignored rather than trusted
            product = ProductSuggestion(product_id=row["product_id"], name=row["name"])
    category = page.category if page.category in tools.CATEGORIES else None
    return PageView(path=page.path, product=product, category=category, search=(page.search or "").strip() or None)


@app.post("/api/chat", response_model=ChatResponse)
async def chat(body: ChatRequest, cc_session: str | None = Cookie(default=None)) -> ChatResponse:
    """One shopper message in, one agent reply (plus product cards) out.

    Logged in: the conversation is loaded from and saved to chat_messages, and the agent's deps
    carry the customer. Guests: the browser sends recent turns and nothing is saved.
    """
    message = body.message.strip()
    user = current_user(cc_session)
    if user:
        history = chat_history.recent_turns(user.id, MAX_HISTORY_TURNS)
        customer = chat_history.customer_for(
            user.id, user.first_name or user.name.split(" ")[0], user.last_name, user.email, user.created_at
        )
        deps = ChatDeps(user_id=user.id, customer=customer, page=page_view(body.page))
    else:
        history = body.history
        deps = ChatDeps(page=page_view(body.page))

    response, ok = await run_chat(message, history, deps)
    if user and ok:
        viewing = deps.page.product.product_id if deps.page and deps.page.product else None
        chat_history.save_exchange(user.id, message, response, viewing_product_id=viewing)
        response.saved = True
    return response


@app.get("/api/chat/history", response_model=ChatHistory)
def get_chat_history(cc_session: str | None = Cookie(default=None)) -> ChatHistory:
    """The logged-in shopper's saved conversation (most recent 50 messages), oldest first."""
    user = current_user(cc_session)
    if user is None:
        raise HTTPException(status_code=401, detail="Log in to see your saved chat.")
    return ChatHistory(messages=chat_history.load_history(user.id))


@app.delete("/api/chat/history", status_code=204)
def delete_chat_history(cc_session: str | None = Cookie(default=None)) -> None:
    """Let a shopper wipe their own saved chat."""
    user = current_user(cc_session)
    if user is None:
        raise HTTPException(status_code=401, detail="Log in to manage your saved chat.")
    chat_history.clear_history(user.id)
