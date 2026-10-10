"""Saved chat history for logged-in shoppers (the chat_messages table).

One row per message. Assistant rows keep the products they showed in products_json as
{"heading", "category", "product_ids"}; cards are rebuilt from the catalogue when history is
loaded, so a reloaded chat always shows today's prices and stock.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import tools
from models import ChatResponse, ChatResults, ChatTurn, Customer, HistoryMessage, ProductSuggestion

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "campus_customs.db"
HISTORY_LIMIT = 50  # messages sent back to the site when a shopper returns


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_index() -> None:
    """History is always read per user, newest first; index that lookup."""
    with connect() as conn:
        conn.execute("CREATE INDEX IF NOT EXISTS idx_chat_messages_user ON chat_messages (user_id, id)")


def _parse_products(products_json: str | None) -> tuple[str | None, str | None, list[str]]:
    """Return (heading, category, product_ids) from either storage format.

    Current rows: {"heading", "category", "product_ids"}. Rows from before Problem 8: a list of
    product objects that each have a product_id.
    """
    if not products_json:
        return None, None, []
    try:
        data = json.loads(products_json)
    except ValueError:
        return None, None, []
    if isinstance(data, dict):
        return data.get("heading"), data.get("category"), [str(i) for i in data.get("product_ids", [])]
    if isinstance(data, list):
        return None, None, [str(p["product_id"]) for p in data if isinstance(p, dict) and "product_id" in p]
    return None, None, []


def save_exchange(user_id: int, message: str, response: ChatResponse, viewing_product_id: str | None = None) -> None:
    """Save the shopper's message and the agent's reply together (both rows or neither).

    On the user row, products_json records the product page they were on ({"viewing_product_id"}),
    so a later "does this come in pink?" in history still points at the right item.
    """
    user_products_json = json.dumps({"viewing_product_id": viewing_product_id}) if viewing_product_id else None
    products_json = None
    if response.results:
        products_json = json.dumps(
            {
                "heading": response.results.heading,
                "category": response.results.category,
                "product_ids": [p.product_id for p in response.results.products],
            }
        )
    with connect() as conn:  # one transaction: committed on success, rolled back on error
        conn.execute(
            "INSERT INTO chat_messages (user_id, role, content, products_json) VALUES (?, 'user', ?, ?)",
            [user_id, message, user_products_json],
        )
        conn.execute(
            "INSERT INTO chat_messages (user_id, role, content, products_json) VALUES (?, 'assistant', ?, ?)",
            [user_id, response.reply, products_json],
        )


def _recent_rows(user_id: int, limit: int) -> list[sqlite3.Row]:
    with connect() as conn:
        rows = conn.execute(
            "SELECT * FROM chat_messages WHERE user_id = ? ORDER BY id DESC LIMIT ?", [user_id, limit]
        ).fetchall()
    return list(reversed(rows))  # oldest first


def recent_turns(user_id: int, limit: int) -> list[ChatTurn]:
    """The last few saved turns, for the agent's memory of this shopper's conversation."""
    turns = []
    for row in _recent_rows(user_id, limit):
        if row["role"] == "user":
            turns.append(ChatTurn(role="user", content=row["content"][:4000], viewing_product_id=_viewing(row["products_json"])))
        else:
            _, _, ids = _parse_products(row["products_json"])
            turns.append(ChatTurn(role="assistant", content=row["content"][:4000], product_ids=ids[:8]))
    return turns


def _viewing(products_json: str | None) -> str | None:
    try:
        data = json.loads(products_json) if products_json else None
    except ValueError:
        return None
    return data.get("viewing_product_id") if isinstance(data, dict) else None


def load_history(user_id: int) -> list[HistoryMessage]:
    """Saved messages for the chat widget, with product cards rebuilt from the database."""
    messages = []
    for row in _recent_rows(user_id, HISTORY_LIMIT):
        heading, category, ids = _parse_products(row["products_json"])
        cards = tools.product_cards(ids[:8]) if ids else []
        results = None
        if cards:
            results = ChatResults(
                heading=heading or "From this chat",
                category=category if category in tools.CATEGORIES else None,
                products=cards,
            )
        messages.append(
            HistoryMessage(role=row["role"], content=row["content"], results=results, created_at=row["created_at"])
        )
    return messages


def clear_history(user_id: int) -> int:
    with connect() as conn:
        return conn.execute("DELETE FROM chat_messages WHERE user_id = ?", [user_id]).rowcount


def message_count(user_id: int) -> int:
    with connect() as conn:
        return conn.execute(
            "SELECT COUNT(*) FROM chat_messages WHERE user_id = ? AND role = 'user'", [user_id]
        ).fetchone()[0]


def recently_discussed(user_id: int, limit: int = 5) -> list[ProductSuggestion]:
    """Products shown to this shopper in earlier chats, most recent first, without repeats."""
    seen: list[str] = []
    for row in reversed(_recent_rows(user_id, HISTORY_LIMIT)):
        for pid in _parse_products(row["products_json"])[2]:
            if pid not in seen:
                seen.append(pid)
        if len(seen) >= limit:
            break
    cards = tools.product_cards(seen[:limit])
    return [ProductSuggestion(product_id=c.product_id, name=c.name) for c in cards]


def customer_for(user_id: int, first_name: str, last_name: str | None, email: str, created_at: str) -> Customer:
    return Customer(
        first_name=first_name,
        last_name=last_name,
        email=email,
        member_since=created_at[:10],
        past_messages=message_count(user_id),
    )
