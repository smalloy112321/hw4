# Creative design — Campus Customs storefront (Problem 10)

The goal was a site that feels like a real Yale shop in New Haven, not a class demo: something a parent, student, or alum trusts enough to browse and buy from. Most of the design work happened while building Problems 3 and 9. This file collects every design choice in one place, explains why each one helps shoppers stay and buy, and says where to see it in the running app (http://127.0.0.1:5173).

## At a glance (the short version)

| Area | What we changed | Why it helps shoppers stay and buy |
|---|---|---|
| **Brand** | Vintage felt-pennant logo with "EST. 1975", centered on a cream band; "OFFICIAL YALE GEAR FOR THE WHOLE FAMILY" strip | Instant heritage and trust; says "official" and "for everyone" before any scrolling |
| **Fonts and color** | Cormorant Garamond headlines, Lato body, spaced capitals for nav and buttons; Yale blue, navy, and cream only | Feels premium and Ivy League but stays easy to read; product photos and ADD TO CART stand out |
| **Home** | Game-day crowd photo hero, one-line headline, two buttons; photo tiles for 4 collections; clutter removed | Sells the feeling of being part of the crowd, then gives one obvious next click |
| **Navigation** | Sticky slim nav, Products ▾ dropdown, plain Create Account, "Hi, Eli" when logged in | Always one click from shopping; feels personal for returning customers |
| **Browsing** | Uniform cards, color, size, and price filters with counts, friendly empty states | Shoppers reach "in my size, in my budget" fast and never hit a dead end |
| **Product page** | Big photo; Name → Sizes → Price → ADD TO CART → Description; sold-out sizes crossed out; "Only 2 left" | Answers "can I get it?" first; honest urgency; one clear call to action |
| **Chat** | Handsome Dan mascot avatar and voice; chat results become cards on the page; saved chats | A friendly helper that shows the merchandise turns questions into sales and gives people a reason to come back |
| **Motion and polish** | Cards lift on hover, Dan's tail-wag wiggle (off for reduced-motion users), typing dots, phone layouts, accessible focus outlines | Feels alive and finished on every device, which builds trust |

The sections below give the details and where to see each change in the running app.

## The design idea in one line

**Vintage Ivy spirit, modern store.** Heritage cues (a felt pennant, "EST. 1975", Garamond headlines, Yale blue and cream) make the brand feel official and established. Modern store patterns (big photos, clear prices, filters, a sticky nav, a helpful chat) make it easy to buy.

---

## 1. First impression: header, logo, and brand

| What we designed | Why it helps shoppers stay and buy | Where to see it |
|---|---|---|
| **A felt-pennant logo with "EST. 1975"**, adapted from the Campus Customs logo. A navy pennant with stitched edges, varsity lettering (Graduate font) with a light-blue offset like a screen print, and "EST. 1975" on the cream band. Drawn as SVG so it's crisp on every screen. | A pennant is instantly "college," and "EST. 1975" signals a long-standing local business. That heritage builds trust in the first second, before a shopper has read anything. We shrank the lettering so it never covers the stitching; small craft details like that read as quality. | Top of every page |
| **Centered logo on a cream band, 20% larger**, with the nav below it. | A centered crest reads as a confident, established brand (like a university seal) rather than a generic web template. Cream adds warmth and a vintage-paper feel next to Yale blue. | Every page |
| **A navy announcement strip: "OFFICIAL YALE GEAR FOR THE WHOLE FAMILY."** | It states the two biggest reasons to buy here (official, and something for everyone) before the shopper scrolls. "Whole family" invites parents and grandparents, not just students. | Very top of every page |
| **A pennant favicon** in the browser tab. | Shoppers with many tabs open can find the store again at a glance, and it looks finished and professional. | Browser tab |

## 2. Type and color: elevated but easy to read

| What we designed | Why it helps | Where to see it |
|---|---|---|
| **Cormorant Garamond for headlines and product names**, an engraved-style serif with an Ivy League feel. | Classic serif headlines make the clothing feel premium and collegiate, which supports $58–$98 price points. We made the headings slightly larger because this font runs small. | Page titles, product names, "Shop by collection" |
| **Lato for body text, prices, forms, and chat.** | A clean sans-serif keeps descriptions, prices, and sizes effortless to read. Elegant headlines plus easy reading is the combination shoppers trust. | Everywhere below the headlines |
| **Small spaced capitals for the nav, buttons, and labels** (HOME, SHOP ALL PRODUCTS, SIZES, ADD TO CART). | This is the look of high-end apparel brands. It also makes every clickable thing and every section label easy to spot. | Nav, buttons, product-page labels |
| **A tight palette:** Yale blue `#00356B`, deep navy `#00254A`, cream `#F6F1E6`, white, and soft grays. | Few colors make the site feel calm and on-brand, so the product photos and the navy "ADD TO CART" button stand out as the things to look at and click. | Site-wide |
| **The logo keeps its own varsity font**, separate from the site fonts. | A distinct logo typeface keeps the brand mark recognizable while the rest of the site feels refined. | Header |
| All fonts are bundled with the site (not loaded from Google). | Pages render consistently and quickly, with no flash of the wrong font and no third-party request. | — |

## 3. The home page: a storefront window

| What we designed | Why it helps | Where to see it |
|---|---|---|
| **A full-width game-day crowd photo as the hero**: Yale fans with "LET'S GO YALE" and "BOOLA BOOLA" signs, cropped to remove another event's logo. | People buy school gear to feel part of the crowd, and this photo sells that feeling better than any sentence. It shows real people in Yale blue, which is aspirational and social proof at once. | Home, below the nav |
| **The headline sits at the bottom of the photo over a soft navy fade**, so both signs stay visible. Copy: "Wear your Bulldog pride every day." on one line, with SHOP ALL PRODUCTS and OUR STORY buttons. | Text never covers the most emotional part of the photo, and the fade keeps the headline readable. Two clear buttons give shoppers an obvious next step: buy, or learn about us. | Home hero |
| **"Shop by collection" tiles with real product photos**: Hoodies (vintage bulldog hoodie), Crewnecks ("YALE EST. 1701"), T-Shirts (vintage Y shield), Quarter-Zips. Each photo is trimmed and centered on white so the whole garment shows, all facing forward. | Pictures let shoppers recognize what they want in a glance, faster than reading a list. Uniform, uncropped, front-facing photos look like a curated store display, not a database dump. | Home, below the hero |
| **Decluttered home page.** We removed an extra paragraph in the hero, a "Bulldog favorites" row, and a "Gear for the whole family" text block. | Fewer choices on the first screen means less effort and a faster path into the collections. Every remaining element has one job. | Home |
| **Original copy in the Campus Customs voice** (friendly, family-focused, Bulldog pride), inspired by yalebulldogblue.com but not copied. | A warm, consistent voice makes a small shop feel personal, which is something a big online retailer can't offer. | Home and About Us |

## 4. Navigation: always one click from shopping

| What we designed | Why it helps | Where to see it |
|---|---|---|
| **A slim nav that sticks to the top while scrolling.** | Shoppers can jump to Products or the account pages from anywhere on a long page, so they never get stuck. | Every page |
| **Products ▾ dropdown** with All products and the six collections. | One hover reaches any collection, the same pattern shoppers know from big retailers. | Hover Products |
| **Create Account styled like the other links** (not a loud button). | A calmer nav keeps attention on the merchandise. Signing up is easy to find without pushing. | Nav |
| **Logged-in greeting, "Hi, Eli,"** in italic Garamond. | A personal touch that makes returning customers feel recognized. | Nav, after logging in |

## 5. Browsing: product cards and collection pages

| What we designed | Why it helps | Where to see it |
|---|---|---|
| **Consistent product cards**: large photo, Garamond name, blue price, one-line description, and "Sold out" badges. Cards lift slightly on hover. | Shoppers compare items fast when every card has the same layout. Showing the price up front builds trust, and the hover lift signals "this is clickable." | Products, chat results |
| **Collection titles that follow the filter** ("Shop Hoodies"). | Shoppers always know where they are, like department signs in a store. | Products pages |
| **Color, Size-in-stock, and Sort-by-price dropdowns** (Problem 9), with live counts like "Navy (16)" and a Clear filters link. | Shoppers reach "navy, in my size, in my budget" in three clicks, and the counts stop them from landing on an empty page. Finding something you can actually buy keeps you on the site. See `usability.md`. | Products pages |
| **Friendly empty and error states** ("Nothing matches those filters right now. Clear filters to see more."; "Could not reach the store server… Try again"). | A dead end with no way forward makes people leave. A clear next step keeps them shopping. | Products, any page while loading |

## 6. The product page: built to convert

| What we designed | Why it helps | Where to see it |
|---|---|---|
| **Big photo on the left, and on the right the order shoppers decide in: Name → Sizes → Price → ADD TO CART → Description.** | The large photo does the selling. Putting sizes before price answers "can I get it?" first, so shoppers don't fall for something that's sold out in their size. | Any product page |
| **Size buttons that show real stock**: sold-out sizes are crossed out and can't be clicked, and picking a size with 1–3 left shows "Only 2 left in L." | Honest stock prevents disappointment at checkout, and a truthful low-stock note gives a gentle, real reason to buy now. | Product page sizes |
| **A full-width navy ADD TO CART button** that asks for a size first ("Choose a size first.") and then confirms ("Added … (size M) to your cart."). | One unmistakable call to action, with clear feedback, so the shopper is never unsure whether it worked. (Checkout itself isn't part of this project.) | Product page |
| **← Back to products** and a "Show matches" bar for chat results. | Shoppers can step into a product and back out without losing their place, which keeps them browsing longer. | Product page |

## 7. The chat: a mascot concierge

| What we designed | Why it helps | Where to see it |
|---|---|---|
| **Handsome Dan**, an original cartoon of Yale's bulldog, beside "Chat with Handsome Dan," in the chat header, and next to every reply. He gives a small tail-wag wiggle (turned off for people who prefer reduced motion). | A friendly mascot face invites people to ask for help, and help is what turns browsers into buyers. It's also a memorable piece of brand personality. | Bottom-right of every page |
| **Dan's voice**: cheerful, short, one light bulldog touch per reply ("Woof!"), and always honest about prices and stock. | Fun but useful. Shoppers get real answers in a voice that matches the brand, and he's honest that he's an AI if sincerely asked, which protects trust. | Open the chat |
| **Search results appear as product cards on the page** ("From your chat: Navy hoodies in XL (7)"), with a 3-item preview in the chat bubble. | The chat doesn't just talk; it shows the merchandise, one click from each product page. Asking "any navy hoodies in XL?" turns into a mini shopping aisle. | Ask Dan about any item type |
| **Saved conversations for logged-in shoppers** ("Welcome back, Eli!"), and page-aware answers ("does this come in pink?" on a product page). | Remembering past chats and knowing which product you're looking at is what a good salesperson does. It gives shoppers a reason to come back and log in. | Log in, then open the chat |
| **Chat bubbles in brand colors**, a typing indicator, and product mini-cards. | It looks and feels like a polished messaging app, so shoppers trust it enough to use it. | Chat panel |

## 8. Polish that builds trust

| What we designed | Why it helps |
|---|---|
| **Responsive on phones**: the logo resizes, nav links wrap, the product page stacks the photo above the details, the filter dropdowns stack, and the chat panel fits the screen. No sideways scrolling. | Many students and parents shop on their phones. A broken mobile layout is the fastest way to lose a sale. |
| **Accessible by design**: real labels on every input, visible gold focus outlines for keyboard users, a "Skip to content" link, alt text on photos, screen-reader names for the avatar and chat messages, and strong text contrast. | Everyone in the Bulldog family can shop, including grandparents with low vision and keyboard users. It's also simply what a professional site does. |
| **Honest data everywhere**: prices, sizes, and "Only N left" all come live from the store database, including in chat. | Nothing erodes trust like a price or size that turns out to be wrong. Accuracy is a design choice. |
| **Consistent loading states** (a spinner with "Loading products…") and friendly error messages. | Shoppers know the site is working, so they wait instead of leaving. |

---

## How the pieces work together to keep shoppers and lead to a sale

1. **Trust in the first second:** pennant logo, EST. 1975, "Official Yale gear," and Ivy typography.
2. **Emotion:** a game-day crowd photo and "Wear your Bulldog pride every day."
3. **An easy path in:** collection tiles with photos, a sticky nav, and the Products ▾ dropdown.
4. **Find something you can actually buy:** consistent cards plus color, size, and price filters.
5. **Confidence to buy:** a big photo, honest sizes and low-stock notes, and one clear ADD TO CART.
6. **Help when you hesitate:** Handsome Dan answers questions and lays out matching products on the page.
7. **A reason to come back:** a saved chat and "Welcome back."
