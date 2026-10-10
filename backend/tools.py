"""Tools the Campus Customs agent can call. Every answer about price or stock comes from here.

Plain functions over the local SQLite database; agent.py registers them with the agent.
"""

from __future__ import annotations

import json
import re
import sqlite3
from pathlib import Path

from models import (
    LookupMiss,
    ProductCard,
    ProductInfo,
    ProductMatch,
    ProductSuggestion,
    SearchResults,
    SizeStock,
    StockReport,
    stock_status,
)

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "campus_customs.db"
SIZE_ORDER = ["XS", "S", "M", "L", "XL", "XXL"]
MAX_RESULTS = 12

# Same six shopper-facing groups the website uses (categoryOf in frontend/src/api.ts).
CATEGORIES = ["Hoodies", "Crewnecks", "Quarter-Zips", "T-Shirts", "Jackets & Fleece", "Long Sleeves"]

# Shoppers say "tee" or "quarter zip"; the catalogue says "t-shirt" or "1-4-zip".
SYNONYMS = {
    "tee": ["t-shirt", "tshirt", "shirt"],
    "tees": ["t-shirt", "tshirt", "shirt"],
    "tshirt": ["t-shirt"],
    "hoody": ["hoodie", "hooded"],
    "hoodies": ["hoodie", "hooded"],
    "sweatshirt": ["crewneck", "hoodie", "sweatshirt"],
    "sweatshirts": ["crewneck", "hoodie", "sweatshirt"],
    "crew": ["crewneck"],
    "crewnecks": ["crewneck"],
    "quarter": ["quarter-zip", "1-4"],
    "zip": ["zip"],
    "jacket": ["jacket", "fleece"],
    "jackets": ["jacket", "fleece"],
    "grey": ["gray"],
    "navy": ["navy"],
    "dad": ["dad"],
    "mom": ["mom"],
}
STOPWORDS = {
    "a", "an", "and", "any", "are", "do", "for", "have", "i", "in", "is", "it", "me", "my", "of",
    "on", "or", "please", "show", "some", "something", "that", "the", "this", "to", "want", "with",
    "you", "your", "what", "which", "looking", "need", "got", "get",
}


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)  # tools only ever read
    conn.row_factory = sqlite3.Row
    return conn


def category_of(garment_type: str) -> str:
    t = garment_type.lower()
    if "quarter-zip" in t or "1/4" in t:
        return "Quarter-Zips"
    if "jacket" in t or "fleece" in t or "full-zip" in t:
        return "Jackets & Fleece"
    if "hood" in t:
        return "Hoodies"
    if "crewneck" in t or "mockneck" in t:
        return "Crewnecks"
    if "long-sleeve" in t:
        return "Long Sleeves"
    return "T-Shirts"


SIZE_WORDS = {
    "XS": "XS", "XSMALL": "XS", "EXTRASMALL": "XS",
    "S": "S", "SM": "S", "SMALL": "S",
    "M": "M", "MED": "M", "MEDIUM": "M",
    "L": "L", "LG": "L", "LARGE": "L",
    "XL": "XL", "XLARGE": "XL", "EXTRALARGE": "XL",
    "XXL": "XXL", "2XL": "XXL", "XXLARGE": "XXL", "2XLARGE": "XXL",
}


def normalize_size(size: str) -> str:
    """"extra large", "x-small", "2XL" -> catalogue codes (XL, XS, XXL). Unknown text passes through."""
    key = re.sub(r"[^A-Z0-9]", "", size.upper())
    return SIZE_WORDS.get(key, key)


# The first color in catalogue.colors is the garment itself; the rest are print colors.
# Shopper-facing families for the Products page color filter.
COLOR_FAMILIES = [
    ("Navy", ("navy",)),
    ("Charcoal", ("charcoal", "dark heather")),
    ("Gray", ("gray", "grey")),
    ("Cream & White", ("cream", "ivory", "white")),
    ("Coral", ("coral",)),
]


def color_family(colors: list[str]) -> str | None:
    """Main garment color as a family ("heather gray" -> "Gray"); None when the catalogue has no colors."""
    if not colors:
        return None
    main = colors[0].lower()
    return next((family for family, words in COLOR_FAMILIES if any(w in main for w in words)), main.title())


def sort_sizes(sizes: list[str]) -> list[str]:
    return sorted(sizes, key=lambda s: SIZE_ORDER.index(s) if s in SIZE_ORDER else len(SIZE_ORDER))


def _load_catalogue() -> list[dict]:
    with connect() as conn:
        rows = conn.execute("SELECT * FROM catalogue").fetchall()
        stock: dict[str, dict[str, int]] = {}
        for r in conn.execute("SELECT product_id, size, quantity FROM inventory"):
            stock.setdefault(r["product_id"], {})[r["size"]] = r["quantity"]
    items = []
    for r in rows:
        item = dict(r)
        item["colors"] = json.loads(r["colors"])
        item["search_tags"] = json.loads(r["search_tags"])
        item["stock"] = stock.get(r["product_id"], {})
        items.append(item)
    return items


def _terms(query: str) -> list[list[str]]:
    """Each query word plus its synonyms, e.g. "navy tee" -> [["navy"], ["tee", "t-shirt", ...]]."""
    words = [w for w in re.findall(r"[a-z0-9/-]+", query.lower()) if w not in STOPWORDS]
    return [[w, *SYNONYMS.get(w, [])] for w in words]


def _score(item: dict, terms: list[list[str]]) -> int:
    fields = [
        (item["name"].lower(), 3),
        (" ".join(item["search_tags"]).lower(), 2),
        (item["garment_type"].lower(), 2),
        (" ".join(item["colors"]).lower(), 2),
        (item["product_id"].lower(), 1),
        (item["description"].lower(), 1),
    ]
    score = 0
    for options in terms:
        best = max((weight for text, weight in fields for opt in options if opt in text), default=0)
        if best == 0:
            return 0  # every meaningful word must match somewhere
        score += best
    return score


def _to_match(item: dict) -> ProductMatch:
    return ProductMatch(
        product_id=item["product_id"],
        name=item["name"],
        garment_type=item["garment_type"],
        price=item["price"],
        colors=item["colors"],
        description=item["description"],
        sizes_in_stock=sort_sizes([s for s, q in item["stock"].items() if q > 0]),
    )


def search_products(
    query: str = "",
    category: str | None = None,
    color: str | None = None,
    size: str | None = None,
    max_price: float | None = None,
    limit: int = 8,
) -> SearchResults:
    """Find catalogue items by keywords and optional filters, best matches first."""
    items = _load_catalogue()
    if category:
        wanted = category.strip().lower()
        items = [i for i in items if category_of(i["garment_type"]).lower() == wanted]
    if color:
        c = color.strip().lower().replace("grey", "gray")
        items = [i for i in items if any(c in col.lower() for col in i["colors"])]
    if size:
        s = normalize_size(size)
        items = [i for i in items if i["stock"].get(s, 0) > 0]
    if max_price is not None:
        items = [i for i in items if i["price"] <= max_price]

    terms = _terms(query)
    if terms:
        scored = [(s, i) for i in items if (s := _score(i, terms)) > 0]
        scored.sort(key=lambda pair: (-pair[0], pair[1]["name"]))
        items = [i for _, i in scored]
    else:
        items.sort(key=lambda i: i["name"])

    limit = max(1, min(limit, MAX_RESULTS))
    if not items:
        note = "No products match. Say so honestly and suggest the closest alternatives."
    elif size:
        note = f"Every product listed has size {normalize_size(size)} in stock right now (checked in the inventory table)."
    else:
        note = ""
    return SearchResults(total_matches=len(items), products=[_to_match(i) for i in items[:limit]], note=note)


def resolve_product(ref: str) -> str | LookupMiss:
    """Turn a product_id or a product name ("the Boola Boola tee") into one product_id.

    Exact id, then exact name, then the single best keyword match. If the words match
    several products equally well, return a LookupMiss with suggestions instead of guessing.
    """
    text = ref.strip()
    with connect() as conn:
        row = conn.execute(
            "SELECT product_id FROM catalogue WHERE product_id = ? OR lower(name) = lower(?)", [text, text]
        ).fetchone()
    if row:
        return row["product_id"]
    terms = _terms(text.replace("-", " "))
    scored = sorted(
        ((sc, i) for i in _load_catalogue() if terms and (sc := _score(i, terms)) > 0),
        key=lambda pair: (-pair[0], pair[1]["name"]),
    )
    if scored and (len(scored) == 1 or scored[0][0] > scored[1][0]):
        return scored[0][1]["product_id"]
    suggestions = [ProductSuggestion(product_id=i["product_id"], name=i["name"]) for _, i in scored[:5]]
    message = (
        "Several products match. Ask the shopper which one they mean."
        if suggestions
        else "No product matches that name. Use search_products to find the right item."
    )
    return LookupMiss(query=text, message=message, suggestions=suggestions)


def _stock(conn: sqlite3.Connection, product_id: str) -> list[SizeStock]:
    rows = conn.execute("SELECT size, quantity FROM inventory WHERE product_id = ?", [product_id]).fetchall()
    units = {r["size"]: r["quantity"] for r in rows}
    return [SizeStock(size=s, units=units[s], status=stock_status(units[s])) for s in sort_sizes(list(units))]


def get_product_info(product: str) -> ProductInfo | LookupMiss:
    """Description, colors, and price for one product, read from the catalogue table."""
    pid = resolve_product(product)
    if isinstance(pid, LookupMiss):
        return pid
    with connect() as conn:
        row = conn.execute("SELECT * FROM catalogue WHERE product_id = ?", [pid]).fetchone()
        sizes = _stock(conn, pid)
    in_stock = [s.size for s in sizes if s.units > 0]
    return ProductInfo(
        product_id=row["product_id"],
        name=row["name"],
        garment_type=row["garment_type"],
        description=row["description"],
        colors=json.loads(row["colors"]),
        price=row["price"],
        in_stock=bool(in_stock),
        sizes_in_stock=in_stock,
    )


def check_stock(product: str, size: str | None = None) -> StockReport | LookupMiss:
    """Units on hand for one product in every size, plus a direct answer for one size if asked."""
    pid = resolve_product(product)
    if isinstance(pid, LookupMiss):
        return pid
    with connect() as conn:
        row = conn.execute("SELECT product_id, name, price FROM catalogue WHERE product_id = ?", [pid]).fetchone()
        sizes = _stock(conn, pid)
    report = StockReport(
        product_id=row["product_id"],
        name=row["name"],
        price=row["price"],
        total_units=sum(s.units for s in sizes),
        sizes=sizes,
    )
    if size:
        wanted = normalize_size(size)
        match = next((s for s in sizes if s.size == wanted), None)
        report.requested_size = wanted
        report.requested_size_units = match.units if match else None
        report.requested_size_status = match.status if match else "not_offered"
    return report


def short_description(text: str, limit: int = 120) -> str:
    """First sentence of a catalogue description, cut at a word boundary if it's long."""
    first = re.split(r"(?<=\.)\s", text.strip(), maxsplit=1)[0]
    if len(first) <= limit:
        return first
    return first[: first.rfind(" ", 0, limit)].rstrip(",;") + "…"


def product_cards(product_ids: list[str]) -> list[ProductCard]:
    """Cards for the site, read fresh from the database in the order given. Unknown ids are dropped."""
    ids = list(dict.fromkeys(product_ids))  # keep order, drop repeats
    if not ids:
        return []
    marks = ",".join("?" * len(ids))
    with connect() as conn:
        rows = {r["product_id"]: r for r in conn.execute(f"SELECT * FROM catalogue WHERE product_id IN ({marks})", ids)}
        stock: dict[str, dict[str, int]] = {}
        for r in conn.execute(f"SELECT product_id, size, quantity FROM inventory WHERE product_id IN ({marks})", ids):
            stock.setdefault(r["product_id"], {})[r["size"]] = r["quantity"]
    cards = []
    for pid in ids:
        row = rows.get(pid)
        if row is None:
            continue
        in_stock = sort_sizes([s for s, q in stock.get(pid, {}).items() if q > 0])
        cards.append(
            ProductCard(
                product_id=pid,
                name=row["name"],
                price=row["price"],
                image_url=f"/images/{Path(row['image_file_path']).name}",
                short_description=short_description(row["description"]),
                sizes_in_stock=in_stock,
                in_stock=bool(in_stock),
            )
        )
    return cards
