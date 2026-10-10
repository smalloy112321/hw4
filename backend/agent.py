"""Campus Customs shop agent: one PydanticAI agent with catalogue tools, used by main.py.

main.py calls run_chat() once per chat message. The agent reads its system prompt from
prompts/prompt.md (fresh on every message), talks to the model through Portkey, looks up products with tools.py, and
returns an AgentReply (text + product ids). Product cards are then rebuilt from the database
so prices on the cards are always real.
"""

from __future__ import annotations

import json
import logging
import re
import os
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

os.environ.setdefault("PYDANTIC_AI_NO_BANNER", "1")

from pydantic_ai import Agent, RunContext, UsageLimitExceeded, UsageLimits, capture_run_messages  # noqa: E402
from pydantic_ai.messages import (  # noqa: E402
    ModelMessage,
    ModelRequest,
    ModelResponse,
    RetryPromptPart,
    TextPart,
    ToolCallPart,
    ToolReturnPart,
    UserPromptPart,
)
from pydantic_ai.models.openai import OpenAIResponsesModel  # noqa: E402
from pydantic_ai.providers.openai import OpenAIProvider  # noqa: E402

import chat_history  # noqa: E402
import tools  # noqa: E402
from models import (  # noqa: E402
    AgentReply,
    AuditEntry,
    ChatResponse,
    ChatResults,
    ChatTurn,
    Customer,
    CustomerProfile,
    LookupMiss,
    PageView,
    ProductInfo,
    ProductResults,
    SearchResults,
    StockReport,
    ToolEvent,
)

log = logging.getLogger("campus_customs.agent")

HERE = Path(__file__).resolve().parent
PROMPT_PATH = HERE / "prompts" / "prompt.md"
AUDIT_PATH = HERE.parent / "output" / "audit_trail.json"
PORTKEY_BASE_URL = "https://api.portkey.ai/v1"
DEFAULT_MODEL = "gpt-6-astra"

MAX_MODEL_REQUESTS = 6
MAX_TOOL_CALLS = 8
MAX_HISTORY_TURNS = 12

FALLBACK_REPLY = "Ruff, I hit a snag on my end! Please try again in a moment. Go Bulldogs!"


def model_name() -> str:
    return os.getenv("OPENAI_MODEL", DEFAULT_MODEL)


_MODEL: OpenAIResponsesModel | None = None


def get_model() -> OpenAIResponsesModel:
    """Build the Portkey-routed model once, on first use (so the API can start without a key)."""
    global _MODEL
    if _MODEL is None:
        api_key = os.getenv("PORTKEY_API_KEY")
        if not api_key:
            raise RuntimeError("PORTKEY_API_KEY not found. Add it to your .env file.")
        _MODEL = OpenAIResponsesModel(model_name(), provider=OpenAIProvider(api_key=api_key, base_url=PORTKEY_BASE_URL))
    return _MODEL


@dataclass
class ChatDeps:
    """Who is chatting and where they are. Built by main.py for every message.

    user_id stays in code (tools use it to look things up); the model only ever sees the
    Customer fields and the checked PageView.
    """

    user_id: int | None = None
    customer: Customer | None = None
    page: PageView | None = None


agent = Agent(
    deps_type=ChatDeps,
    output_type=AgentReply,
    name="handsome_dan",
)


@agent.instructions
def system_prompt() -> str:
    # Read on every run so edits to prompts/prompt.md apply without restarting the server
    # (uvicorn --reload only watches .py files).
    return PROMPT_PATH.read_text(encoding="utf-8")


@agent.instructions
def shopper_context(ctx: RunContext[ChatDeps]) -> str:
    c = ctx.deps.customer
    if c is None:
        return "Shopper: a guest (not logged in). Their chat is not saved."
    returning = (
        f"They've chatted with us before ({c.past_messages} earlier messages)."
        if c.past_messages
        else "This is their first chat with us."
    )
    return (
        f"Shopper: logged in as {c.first_name}, a Campus Customs member since {c.member_since}. {returning} "
        "Their chat is saved, so earlier messages in this conversation may be from a previous visit."
    )


@agent.instructions
def page_context(ctx: RunContext[ChatDeps]) -> str:
    page = ctx.deps.page
    if page is None:
        return "Current page: unknown."
    if page.product:
        return (
            f'Current page: the product page for "{page.product.name}" (product_id: {page.product.product_id}). '
            'If the shopper says "this", "it", or "this one" without naming an item, they mean this product. '
            "Look it up with the tools before answering."
        )
    if page.path.startswith("/products"):
        filters = ", ".join(f for f in [f"category {page.category}" if page.category else "", f'search "{page.search}"' if page.search else ""] if f)
        return f"Current page: the Products listing{f' filtered by {filters}' if filters else ''}."
    return f"Current page: {page.path}."


@agent.tool
def get_shopper_profile(ctx: RunContext[ChatDeps]) -> CustomerProfile:
    """Who is chatting: first name, member-since date, and products shown to them in earlier chats.

    Call this when the shopper refers to an earlier visit ("the hoodie you showed me last time")
    or asks what we know about them. Returns logged_in=false for guests.
    """
    c = ctx.deps.customer
    if c is None or ctx.deps.user_id is None:
        return CustomerProfile(logged_in=False)
    return CustomerProfile(
        logged_in=True,
        first_name=c.first_name,
        last_name=c.last_name,
        member_since=c.member_since,
        past_messages=c.past_messages,
        recently_discussed=chat_history.recently_discussed(ctx.deps.user_id),
    )


@agent.tool_plain
def search_products(
    query: str = "",
    category: str | None = None,
    color: str | None = None,
    size: str | None = None,
    max_price: float | None = None,
) -> SearchResults:
    """Search the Campus Customs catalogue (up to 8 best matches). Returns real prices and in-stock sizes.

    Call this whenever the shopper asks about a type of item or a category; put the best
    matches in `results` so they appear on the page as product cards.

    Args:
        query: Keywords from the shopper, e.g. "navy hoodie", "dad", "baseball", "Boola Boola".
            Leave empty to browse by filters only.
        category: One of "Hoodies", "Crewnecks", "Quarter-Zips", "T-Shirts", "Jackets & Fleece", "Long Sleeves".
        color: A color the item must include, e.g. "navy", "gray", "white".
        size: Only items with this size in stock: "XS", "S", "M", "L", "XL", or "XXL".
        max_price: Highest price in US dollars.
    """
    return tools.search_products(query=query, category=category, color=color, size=size, max_price=max_price)


@agent.tool_plain
def get_product_info(product: str) -> ProductInfo | LookupMiss:
    """Look up one product's description, colors, and price in the catalogue table.

    Call this whenever the shopper asks what an item is like or how much it costs.

    Args:
        product: The product_id (best, e.g. "boola-boola-t-shirt") or the product's name.
    """
    return tools.get_product_info(product)


@agent.tool_plain
def check_stock(product: str, size: str | None = None) -> StockReport | LookupMiss:
    """Look up how many units of one product are in stock, size by size, in the inventory table.

    Call this for any question about availability, sizes, or quantities, and before saying a size
    is available. Pass `size` when the shopper names one; the report then answers it directly.

    Args:
        product: The product_id (best, e.g. "champion-reverse-weave-crewneck") or the product's name.
        size: The size asked about, e.g. "S", "XL", "medium", "extra large". Omit for all sizes.
    """
    return tools.check_stock(product, size)


def _history(turns: list[ChatTurn]) -> list[ModelMessage]:
    """Rebuild earlier turns as PydanticAI messages so follow-ups ("in pink?") make sense."""
    messages: list[ModelMessage] = []
    for turn in turns[-MAX_HISTORY_TURNS:]:
        if turn.role == "user":
            text = turn.content
            if turn.viewing_product_id:  # "this" in an older message meant the page they were on then
                text = f"[Sent from the product page for {turn.viewing_product_id}]\n{text}"
            messages.append(ModelRequest(parts=[UserPromptPart(content=text)]))
        else:
            text = turn.content
            if turn.product_ids:  # remember which cards were shown, for "the second one"
                text += f"\n[Products shown with this reply, in order: {', '.join(turn.product_ids)}]"
            messages.append(ModelResponse(parts=[TextPart(content=text)]))
    return messages


async def run_chat(message: str, history: list[ChatTurn], deps: ChatDeps) -> tuple[ChatResponse, bool]:
    """Answer one chat message. Returns (response, ok); ok is False when the friendly fallback was used.

    Every run, including failed ones, is appended to output/audit_trail.json.
    """
    started = time.perf_counter()
    result = None
    with capture_run_messages() as messages:  # kept even when the run raises
        try:
            result = await agent.run(
                message,
                model=get_model(),
                deps=deps,
                message_history=_history(history),
                usage_limits=UsageLimits(request_limit=MAX_MODEL_REQUESTS, tool_calls_limit=MAX_TOOL_CALLS),
            )
            stop_reason = "final_answer"
        except UsageLimitExceeded as exc:
            log.warning("chat run hit usage limits")
            stop_reason = f"usage_limit: {str(exc)[:160]}"
            response = ChatResponse(
                reply="That one has this bulldog stumped! Could you ask it a little more simply? I'm happy to help."
            )
        except Exception as exc:  # keep the shopper's view friendly; details go to the log and audit trail
            log.exception("chat run failed: %s", type(exc).__name__)
            stop_reason = f"error: {type(exc).__name__}: {str(exc)[:160]}"
            response = ChatResponse(reply=FALLBACK_REPLY)

    events = _tool_events(messages)
    if result is not None:
        output = result.output
        response = ChatResponse(
            reply=output.reply.strip() or FALLBACK_REPLY,
            results=_page_results(output.results),
            tools_used=[e.tool for e in events if not e.result.startswith("retry:")],
        )

    usage = {}
    if result is not None:
        u = result.usage
        usage = {"requests": u.requests, "input_tokens": u.input_tokens, "output_tokens": u.output_tokens}
    append_audit(
        AuditEntry(
            time=datetime.now(timezone.utc).isoformat(timespec="seconds"),
            model=model_name(),
            model_used=sorted({m.model_name for m in messages if isinstance(m, ModelResponse) and m.model_name}),
            shopper=f"user:{deps.user_id}" if deps.user_id else "guest",
            page=deps.page.path if deps.page else None,
            message=_redact(message)[:300],
            tool_calls=events,
            reply=_redact(response.reply)[:300],
            product_ids=[p.product_id for p in response.results.products] if response.results else [],
            stop_reason=stop_reason,
            duration_s=round(time.perf_counter() - started, 2),
            usage=usage,
        )
    )
    return response, result is not None


# --- Audit trail -----------------------------------------------------------------------------

_AUDIT_LOCK = threading.Lock()
OUTPUT_TOOL_PREFIX = "final_result"  # PydanticAI's structured-output tool, not one of ours


_EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
_CARD_OR_ID = re.compile(r"\b\d(?:[ -]?\d){8,18}\b")  # card numbers, SSNs, phone-like digit runs


def _redact(text: str) -> str:
    """Mask emails and long digit runs a shopper may have pasted, so the log never stores them."""
    return _CARD_OR_ID.sub("[number removed]", _EMAIL.sub("[email removed]", text))


def _short(value: object, limit: int = 80) -> object:
    if isinstance(value, str) and len(value) > limit:
        return value[:limit] + "…"
    return value


def _summarize(content: object) -> str:
    """One readable line per tool result, so the audit trail stays small and skimmable."""
    if isinstance(content, SearchResults):
        top = ", ".join(p.product_id for p in content.products[:4])
        return f"{content.total_matches} matches; top: {top}" if content.products else content.note
    if isinstance(content, ProductInfo):
        return f"{content.product_id}: ${content.price:.2f}, colors {content.colors}, in stock {content.sizes_in_stock}"
    if isinstance(content, StockReport):
        sizes = " ".join(f"{s.size}={s.units}" for s in content.sizes)
        asked = f"; asked {content.requested_size} -> {content.requested_size_status}" if content.requested_size else ""
        return f"{content.product_id}: {sizes}{asked}"
    if isinstance(content, LookupMiss):
        return f"miss '{content.query}': {[s.product_id for s in content.suggestions]}"
    if isinstance(content, CustomerProfile):
        return f"logged_in={content.logged_in}, past_messages={content.past_messages}, recent={len(content.recently_discussed)} products"
    return str(content)[:200]


def _tool_events(messages: list[ModelMessage]) -> list[ToolEvent]:
    """Pair each tool call with its result (or retry) from the run's message log."""
    calls: dict[str, ToolCallPart] = {}
    events: list[ToolEvent] = []
    for msg in messages:
        for part in msg.parts:
            if isinstance(part, ToolCallPart) and not part.tool_name.startswith(OUTPUT_TOOL_PREFIX):
                calls[part.tool_call_id] = part
            elif isinstance(part, (ToolReturnPart, RetryPromptPart)) and part.tool_call_id in calls:
                call = calls.pop(part.tool_call_id)
                args = {k: _short(_redact(v) if isinstance(v, str) else v) for k, v in call.args_as_dict().items()}
                result = _summarize(part.content) if isinstance(part, ToolReturnPart) else f"retry: {str(part.content)[:160]}"
                events.append(ToolEvent(tool=call.tool_name, args=args, result=result))
    for call in calls.values():  # called but never answered (run stopped first)
        events.append(ToolEvent(tool=call.tool_name, args=call.args_as_dict(), result="no result (run stopped)"))
    return events


def append_audit(entry: AuditEntry) -> None:
    """Add one entry to output/audit_trail.json without touching earlier entries.

    The file is a JSON list. We read it, add the new entry at the end, and swap the file in
    atomically, so a crash can't leave half a file. If the file is ever unreadable, it is
    renamed (kept, not deleted) and a new list is started.
    """
    with _AUDIT_LOCK:
        AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
        rows: list = []
        if AUDIT_PATH.exists():
            try:
                rows = json.loads(AUDIT_PATH.read_text(encoding="utf-8") or "[]")
                if not isinstance(rows, list):
                    raise ValueError("audit trail is not a list")
            except ValueError:
                stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
                AUDIT_PATH.rename(AUDIT_PATH.with_name(f"audit_trail.corrupt-{stamp}.json"))
                rows = []
        rows.append(entry.model_dump())
        tmp = AUDIT_PATH.with_suffix(".tmp")
        tmp.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
        tmp.replace(AUDIT_PATH)


def _page_results(results: ProductResults | None) -> ChatResults | None:
    """Turn the agent's product ids into cards built from the database (the API contract)."""
    if results is None:
        return None
    cards = tools.product_cards(results.product_ids)
    if not cards:  # every id was unknown: show nothing rather than an empty panel
        return None
    return ChatResults(heading=results.heading.strip(), category=results.category, products=cards)
