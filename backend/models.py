"""Structured types for the Campus Customs chat agent.

Tool results (what the agent reads), the agent's own output, and the chat API's request and
response shapes all live here so every layer agrees on the same fields.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

# --- What the tools return to the agent -----------------------------------------------

LOW_STOCK_UNITS = 3

StockStatus = Literal["in_stock", "low_stock", "sold_out"]


def stock_status(units: int) -> StockStatus:
    if units <= 0:
        return "sold_out"
    return "low_stock" if units <= LOW_STOCK_UNITS else "in_stock"


class SizeStock(BaseModel):
    size: str = Field(description="XS, S, M, L, XL, or XXL.")
    units: int = Field(description="Units on hand right now, straight from the inventory table.")
    status: StockStatus = Field(description=f"sold_out at 0 units, low_stock at 1-{LOW_STOCK_UNITS}, else in_stock.")


class ProductMatch(BaseModel):
    """One catalogue item in search results: enough to recommend it honestly."""

    product_id: str
    name: str
    garment_type: str
    price: float = Field(description="Current price in US dollars, from the database.")
    colors: list[str]
    description: str
    sizes_in_stock: list[str] = Field(description="Sizes with at least one unit. Empty means fully sold out.")


class SearchResults(BaseModel):
    total_matches: int
    products: list[ProductMatch]
    note: str = ""


class ProductInfo(BaseModel):
    """Description and price for one product (get_product_info)."""

    product_id: str
    name: str
    garment_type: str
    description: str = Field(description="The catalogue description. Paraphrase it; don't add details it lacks.")
    colors: list[str]
    price: float = Field(description="Price in US dollars from the catalogue table. Quote exactly, e.g. $58.00.")
    in_stock: bool = Field(description="True if at least one size has units on hand.")
    sizes_in_stock: list[str]


class StockReport(BaseModel):
    """Units on hand for one product, by size (check_stock)."""

    product_id: str
    name: str
    price: float
    total_units: int = Field(description="All sizes added together.")
    sizes: list[SizeStock] = Field(description="Every size the product is stocked in, XS to XXL.")
    requested_size: str | None = Field(default=None, description="The size the shopper asked about, if any.")
    requested_size_units: int | None = None
    requested_size_status: StockStatus | Literal["not_offered"] | None = Field(
        default=None, description="not_offered means this product has no inventory row for that size."
    )


class ProductSuggestion(BaseModel):
    product_id: str
    name: str


class Alternatives(BaseModel):
    """Similar items that are in stock in the shopper's size (suggest_alternatives)."""

    for_product: ProductSuggestion = Field(description="The item the shopper wanted.")
    size: str = Field(description="The size they need, as a catalogue code (XS-XXL).")
    original_has_size: bool = Field(description="True if the original item actually has this size in stock.")
    alternatives: list[ProductMatch] = Field(
        description="Up to 4 other items with this size in stock, most similar first (same category, then same color, then closest price)."
    )


class LookupMiss(BaseModel):
    """Returned instead of a result when no single product matches what was asked for."""

    query: str
    message: str
    suggestions: list[ProductSuggestion] = Field(default_factory=list)


# --- What the agent returns -------------------------------------------------------------


Category = Literal["Hoodies", "Crewnecks", "Quarter-Zips", "T-Shirts", "Jackets & Fleece", "Long Sleeves"]


class ProductResults(BaseModel):
    """Structured product matches the site shows as cards. The agent picks the ids; the
    backend fills in name, price, image, and short info from the database."""

    heading: str = Field(
        max_length=60,
        description='Short title for the results panel, e.g. "Navy hoodies" or "Gifts for Dad".',
    )
    category: Category | None = Field(
        default=None,
        description="Set when the shopper asked about a whole category, so the site can link to all of it.",
    )
    product_ids: list[str] = Field(
        min_length=1,
        max_length=8,
        description="product_id values from tool results only, best match first.",
    )


class AgentReply(BaseModel):
    """The agent's final answer for one chat turn: the chat text plus optional product matches."""

    reply: str = Field(
        description="The message to the shopper: warm, cheerful, short (2-5 sentences), plain text with no markdown."
    )
    results: ProductResults | None = Field(
        default=None,
        description="Product matches to show on the page as cards. None when no product fits or none was discussed.",
    )


# --- Chat API shapes ------------------------------------------------------------------------


class ChatTurn(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(max_length=4000)
    product_ids: list[str] = Field(
        default_factory=list, max_length=8, description="Products shown with this assistant turn, so follow-ups like 'the second one' work."
    )
    viewing_product_id: str | None = Field(
        default=None, description="User turns: the product page the shopper was on when they sent it."
    )


class PageContext(BaseModel):
    """Where the shopper is on the site when they send a message (sent by the front end)."""

    path: str = Field(max_length=200, description='The page URL path, e.g. "/products/boola-boola-t-shirt".')
    product_id: str | None = Field(default=None, max_length=120, description="Set on a product page (PDP).")
    category: str | None = Field(default=None, max_length=40, description="Set on Products when a category filter is on.")
    search: str | None = Field(default=None, max_length=100, description="Products page search box text, if any.")


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=1000)
    history: list[ChatTurn] = Field(
        default_factory=list,
        max_length=20,
        description="Guests only: earlier turns, oldest first. Logged-in history is loaded from the database instead.",
    )
    page: PageContext | None = None


# --- Who is chatting and where (agent deps) -------------------------------------------------


class Customer(BaseModel):
    """The logged-in shopper, as the agent sees them. Never the password hash or anyone else's data."""

    first_name: str
    last_name: str | None = None
    email: str = Field(description="The shopper's own login email; may be confirmed back to them, never shared.")
    member_since: str = Field(description="Date the account was created, YYYY-MM-DD.")
    past_messages: int = Field(description="How many chat messages they've sent before this one.")


class PageView(BaseModel):
    """Page context after the backend checks it against the database."""

    path: str
    product: ProductSuggestion | None = Field(default=None, description="The product page they're on, if any.")
    category: str | None = None
    search: str | None = None


class CustomerProfile(BaseModel):
    """Returned by the get_shopper_profile tool."""

    logged_in: bool
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    member_since: str | None = None
    past_messages: int = 0
    recently_discussed: list[ProductSuggestion] = Field(
        default_factory=list, description="Products shown to this shopper in earlier chats, most recent first."
    )


class ProductCard(BaseModel):
    """A product the site shows as a clickable card. Built from the database, never from model text."""

    product_id: str
    name: str
    price: float
    image_url: str
    short_description: str = Field(description="First sentence of the catalogue description.")
    sizes_in_stock: list[str]
    in_stock: bool


class ChatResults(BaseModel):
    """What the site renders: a heading, an optional "view all" category, and the cards."""

    heading: str
    category: Category | None = None
    products: list[ProductCard]


class ChatResponse(BaseModel):
    """API contract for POST /api/chat."""

    reply: str
    results: ChatResults | None = Field(default=None, description="Product cards to show on the page, or null.")
    tools_used: list[str] = Field(
        default_factory=list, description="Tools the agent called this turn, in order (shows the answer came from the database)."
    )
    saved: bool = Field(default=False, description="True when this exchange was saved to the shopper's chat history.")


class HistoryMessage(BaseModel):
    """One saved message, as GET /api/chat/history returns it."""

    role: Literal["user", "assistant"]
    content: str
    results: ChatResults | None = None
    created_at: str


class ChatHistory(BaseModel):
    messages: list[HistoryMessage]


# --- Audit trail (output/audit_trail.json) ---------------------------------------------------


class ToolEvent(BaseModel):
    """One tool call inside an agent run, kept short for the audit trail."""

    tool: str
    args: dict = Field(default_factory=dict, description="Arguments the model passed, long strings shortened.")
    result: str = Field(description="One-line summary of what the tool returned (or the retry message).")


class AuditEntry(BaseModel):
    """One agent run. Appended to output/audit_trail.json and never rewritten or removed."""

    time: str = Field(description="UTC timestamp, ISO 8601.")
    model: str = Field(description="Model name we asked Portkey for (OPENAI_MODEL or gpt-6-astra).")
    model_used: list[str] = Field(
        default_factory=list, description="Model name(s) the responses reported. Portkey may route to a fallback."
    )
    shopper: str = Field(description='"user:<id>" or "guest". No names, emails, or other personal details.')
    page: str | None = Field(default=None, description="Page path the message was sent from.")
    message: str = Field(description="The shopper's message (first 300 characters).")
    tool_calls: list[ToolEvent] = Field(default_factory=list)
    reply: str = Field(description="What the shopper saw (first 300 characters).")
    product_ids: list[str] = Field(default_factory=list, description="Product cards shown with the reply.")
    stop_reason: str = Field(description='"final_answer", "usage_limit: …", or "error: …".')
    duration_s: float
    usage: dict = Field(default_factory=dict, description="Model requests and tokens for the run, when available.")

