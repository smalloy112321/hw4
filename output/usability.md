# Usability improvements — Campus Customs (Problem 9)

Problem 9 asks for **2 front-end** and **2 agent/backend** improvements. All of them are live in the running app. To see them, start both servers (see the README) and open http://127.0.0.1:5173.

| # | Type | Improvement | Where to see it |
|---|---|---|---|
| 1 | Front end | Color and size dropdown filters | **Products** in the nav, or any collection (e.g. Products ▾ → Hoodies) |
| 2 | Front end | Sort by price, low to high or high to low | Same pages, **Sort by** dropdown |
| 3 | Agent / backend | The agent speaks as Handsome Dan (better, friendlier agent output) | Open the chat and say hi |
| 4 | Agent / backend | New agent tool `suggest_alternatives`: when a size is sold out, the agent offers similar items in stock in that size | Ask "Do you have the Champion Reverse Weave Crewneck in large?" |
| + | Front end (bonus) | Handsome Dan avatar beside the chat button, in the header, and on every reply | Bottom-right corner of every page |

---

## Front end

### 1. Color and size dropdown filters on collection pages

**What was added**
- Two dropdowns under the category chips on the Products page: **Color** and **Size in stock**. They work on "Shop all products" and on every collection (Hoodies, Crewnecks, Quarter-Zips, T-Shirts, Jackets & Fleece, Long Sleeves). The page title follows the collection ("Shop Hoodies").
- **Color** filters by the garment's main color, grouped into families shoppers recognize: Navy, Gray, Charcoal, Cream & White, and Coral. The catalogue's `colors` list puts the garment color first and the print colors after it, so we filter on the first color. Otherwise "White" would match almost every navy hoodie with white lettering.
- **Size in stock** shows only items that have at least one unit in that size, read live from the `inventory` table.
- Each option shows how many items it will return (e.g., "Navy (16)", "XL (19)"), and sizes with zero matches are greyed out, so shoppers don't land on an empty page.
- A **Clear filters** link appears when any filter, sort, or search is on. If a combination has no matches, the page says so and offers Clear filters.
- Filters live in the page address (`/products?category=Hoodies&color=Navy&size=XL`), so a filtered view can be bookmarked, shared in a group chat, or restored with the Back button.
- Backend support: `/api/products` now returns `color_family` and `sizes_in_stock` for every product (`backend/main.py`, `color_family()` in `backend/tools.py`).

**Why it helps**
- *Shoppers:* the most common questions in apparel are "Do you have it in my size?" and "Do you have it in navy?" Before, a parent buying an XL had to open each product page to find out it was sold out. Now one dropdown shows only what they can actually buy.
- *Business:* fewer dead ends on sold-out sizes means fewer abandoned visits and fewer "is this in stock?" questions for staff. Shareable filter links also make it easy to promote a view like "navy hoodies in every size" before Family Weekend or The Game.

**Checked in the running app**
- Hoodies → Color: Navy (16), Gray (7), Charcoal (2); Size: XS 20, S 21, M 19, L 18, XL 19, XXL 21.
- Hoodies + Navy + XL → 12 items. An independent database query counted 12 navy hoodies with XL in stock.
- Clear filters returns to all 102 items with every dropdown reset.
- On a 375-px phone screen the dropdowns stack neatly with no sideways scrolling.

**Known data gap:** three catalogue items have no colors recorded (Benjamin Franklin T Shirt, Berkeley Sweater Fleece Jacket, Timothy Dwight College Crewneck). They appear under "All colors" but not under a specific color.

### 2. Sort by price

**What was added**
- A **Sort by** dropdown next to the filters: **Featured** (the default A–Z order), **Price: Low to High**, and **Price: High to Low**. Items with the same price stay in A–Z order. Sorting works together with category, color, size, and search, and it's saved in the address (`&sort=price-asc`).

**Why it helps**
- *Shoppers:* students on a budget can start with the $32 tees, and gift-buyers can start with the $98 fleece jackets, without scrolling through all 102 items.
- *Business:* "High to Low" puts premium pieces (fleece jackets and sweaters at $98) in front of shoppers who are ready to spend, and "Low to High" keeps price-sensitive shoppers browsing instead of leaving.

**Checked in the running app**
- All products, High to Low: starts with $98 fleece sweaters and ends with $32 tees, with every price less than or equal to the one before.
- Low to High: starts at $32, ends at $98, every price greater than or equal to the one before. This matches the catalogue's price range of $32–$98.

---

## Agent / backend

### 3. The chatbot speaks as Handsome Dan (agent output)

**What was added**
- The system prompt (`backend/prompts/prompt.md`) now opens with a "Who you are" section. The agent speaks in the first person as Handsome Dan: a proud, friendly, slightly goofy bulldog who loves Yale and game days. He adds at most one light touch of bulldog flavor per reply ("Woof!", "I'd fetch that for you") so facts, prices, and sizes stay easy to read.
- The site's greetings match: "Woof! I'm Handsome Dan, Yale's bulldog…", and for returning shoppers, "Welcome back, Eli! It's Handsome Dan…". Even the error messages stay in character ("Ruff, I hit a snag…").
- **Every honesty and safety rule still applies in character:** prices and stock still come from the database tools, and he still declines off-topic requests and never asks for card numbers.
- **He's honest about what he is.** If a shopper sincerely asks whether he's a real dog or an AI, he says he's the Campus Customs AI shop helper dressed up as Handsome Dan, and he never claims to be the real Handsome Dan or to speak for Yale.

**Why it helps**
- *Shoppers:* chatting with a cheerful campus mascot is more fun and less intimidating than a faceless support bot, especially for younger fans and families. The playful voice also makes answers like "sold out in large" feel friendly instead of disappointing.
- *Business:* a memorable, on-brand character gives Campus Customs a personality that a big online retailer doesn't have, and it encourages shoppers to come back. Being upfront that he's an AI protects customer trust.

**Checked in the running app** (chat replies)
- "Hi! Who am I talking to?" → "Woof! I'm Handsome Dan, the Campus Customs AI shop helper dressed up as Yale's favorite bulldog mascot…"
- "Is the Champion Reverse Weave Crewneck in stock in large?" → sold out in large; medium and XL in stock. This matches the database (L=0, M=12, XL=12).
- "Are you a real dog or an AI?" → "I'm the Campus Customs AI shop helper dressed up as Handsome Dan, not a real dog…"
- "Write me a poem about Harvard losing" → politely declines in character and offers Yale gear for The Game.
- On the Hoodies page: "Any navy hoodies in XL for my dad?" → "Woof, yes…" plus 7 navy XL hoodie cards on the page.

### 4. Sold-out size → in-stock alternatives (new agent tool)

**What was added**
- A new tool the agent can call, **`suggest_alternatives(product, size)`** (`backend/tools.py`, registered in `backend/agent.py`, result type `Alternatives` in `backend/models.py`).
- It finds up to 4 other items that are **in stock in the shopper's size**, ranked by how similar they are: same collection first (e.g. crewnecks), then the same main color, then the closest price. Every alternative is checked against the `inventory` table, and `original_has_size` tells the agent whether the original item really is sold out, so it never suggests swaps unnecessarily.
- The prompt now tells the agent: when `check_stock` says a size is `sold_out` (or `not_offered`), say so plainly, then call `suggest_alternatives` and show the matches as product cards ("Similar crewnecks in L").
- Calls and results are recorded in `output/audit_trail.json` like every other tool (e.g. `champion-reverse-weave-crewneck has L: False; alternatives: davenport-college-crewneck $58, …`).

**Why it helps**
- *Shoppers:* "sold out in your size" used to be a dead end. Now the very next thing the shopper sees is a short list of similar items they can actually buy in their size, without searching again.
- *Business:* it turns a lost sale into a likely one, at the exact moment a shopper is ready to buy. Because the suggestions come from live inventory, nobody is sent to another out-of-stock item.
- *Accuracy:* before, the agent had to improvise alternatives with general searches, which could include items not available in the shopper's size. Now the matches are guaranteed in stock in that size.

**Checked in the running app**
- "I need the Champion Reverse Weave Crewneck in a large. Do you have it?" → tools `check_stock`, then `suggest_alternatives`. Dan: "…sold out in large right now; medium and XL are in stock. I've fetched some similar crewnecks below that are available in large." The page showed **"Similar crewnecks in L"** with 4 cards: Davenport College, Jonathan Edwards College, Super Heavyweight Arched Yale Crest, and Yale Brother crewnecks, all $58.00 and all with L in stock.
- Database: Champion Reverse Weave Crewneck L = 0, and each of the 4 alternatives has L > 0.

## Bonus (front end)

### Bonus: Handsome Dan avatar next to the chat button (front end)

**What was added**
- An original cartoon of Handsome Dan, Yale's bulldog mascot: a bulldog face with folded "rose" ears, heavy jowls, a little underbite, and a navy sweater with a white Y, on a Yale-blue circle (`frontend/src/components/HandsomeDan.tsx`). It's drawn in code (SVG), so it's sharp on any screen, loads instantly, and uses no copyrighted photo.
- It appears in three places:
  - next to the chat button, which now reads **"Chat with Handsome Dan"** (he gives a small tail-wag wiggle every few seconds, turned off for shoppers who set their device to reduce motion, and clicking him also opens the chat)
  - in the chat header, which now says **Handsome Dan**
  - beside each of his replies and the "typing" dots
- Screen readers announce him as "Handsome Dan, the Yale bulldog."

**Why it helps**
- *Shoppers:* a friendly face is more inviting than a plain "Chat" button. People are more likely to ask a question, and seeing the same face on each reply makes it clear who is talking.
- *Business:* Handsome Dan is the most recognizable symbol of Yale spirit. Putting him on the store's helper makes the shop feel official and on-brand, and a chat that more people open means more questions answered and more sales.

**Checked in the running app**
- The avatar shows next to "Chat with Handsome Dan" on every page, and clicking it opens the chat.
- With the chat open there are 3 avatars (header, greeting, and reply). Confirmed on desktop and phone.
