# AI Prompts Log — Homework 4 (Campus Customers Website + Chatbot)

A log of the prompts I typed into the vibe coder, with one section for each problem.

---

## Setup — Project background

**Prompt:**
> I am going to be working on Homework 4 for AI FOUNDATIONS. Here's some background before we get started. Let me know when you're ready to go.
>
> Campus Customers needs a real customer website with a helpful chatbot. You will build a React + Vite TypeScript front end and a Python FastAPI backend whose brain is a PydanticAI agent. Shoppers should be able to browse products, create an account, chat about merch, see matching items appear on the page, and get honest answers about price and stock from a local database. We are going to work one problem at a time.
>
> Ready?

**Follow-up:** None needed.

---

## Problem 1 — Create the AI prompts log

**Prompt:**
> Problem 1: I want to create AI_prompts.md and keep it updated as I work. Please put one section for each problem. Each section must include: the problem number and title, at least one typed prompt, one follow-up prompt if needed (and a sentence on what was lacking).
>
> The running site, database writes, and screenshots will be the evidence of my work and no extra proof essay will be needed. Please let me know when you're done.

**Follow-up:** None needed. The first prompt created this file with the required structure.

---

## Problem 2 — Understand the database and start harness.md

**Prompt:**
> Problem 2: I have included a database called data/campus_customs.db. Please ensure you understand the fields of the table. The most important are catalogue, inventory, and users.
>
> Start the file output/harness.md. I want to write down each table and its fields and one short line on why each field matters for the shop or the chatbot. Can you work with me to go through each one so that I can write why each field matters?

**Follow-up prompt:**
> Yes, let's make that change for quantity

**What was lacking after the first prompt:** My first line for `quantity` said what the field holds but not why it matters, so I added that the chatbot uses it to say honestly whether a size is available or sold out.

**Result:** `output/harness.md` lists all four tables (`catalogue`, `inventory`, `users`, `chat_messages`) with every field, its type, and my one-line reason why it matters.

---

## Problem 3 — Scaffold the React + Vite + TypeScript front end and a product API

**Prompt:**
> Okay, let's start Problem 3. I want to scaffold a react + vite + typescript front end for Campus Customs. The nav bar at the top should link to Home, Products, About US, Log In, Create Account.
>
> Please pull wording and tone of voice from the Campus Customs website yalebulldogblue.com for Home and About Us but don't copy the original.
>
> On the products page, show images from the catalogue with basic info about the product (name, price, short description).
>
> Make each product open a single-item page called a PDP (large image on the left, product text on the side in this order: Name, Sizes, Price, Description). Clicking on a card should take the shopper there to the PDP.
>
> Add a chat interface in the bottom right of the site. This agent does not need to talk yet, we will do this in another problem.
>
> I need a small API soon to read the database. It's okay to start a simple FastAPI app in the backend/main.py just to serve products and images, then grow it into the agent backend in Problem 5.

**Follow-up prompts:**
> Let's make a few changes. Here's the Campus Customs logo from their website. Can we make update it so that it feels Yale vintage inspired with the EST. 1975 included and add it to the site. Can you show me a few options?

> I like Option D but can you shrink the CAMPUS CUSTOMS so that it fits inside the pennant without covering the dash marks?

> Can we make the font look more vintage?

> Let's do Option 1. Please add it back to the front end. Put it centered instead of on the left side. Put the nav bar below it.

> Some more changes:
> - change the header to say: "OFFICIAL YALE GEAR FOR THE WHOLE FAMILY"
> - Make the logo 20% larger
> - Make the nav bar smaller
> - Remove the copy that says: Soft hoodies, everyday crewnecks, and game-day tees for students, alumni, parents, and every Bulldog fan in the family.
> - Replace the navy below the nav bar with his picture but crop out the logo that says THE GAME in the right hand corner
> - Remove bulldog favorites carousel

> Remove this section *(screenshot of the "Gear for the whole Bulldog family" section on Home)*

> Let's redo this section. Keep the collections you have now but add an image for each. keep the name and "shop now" but get rid of the description *(screenshot of the "Shop by collection" tiles)*

> Some of the items are cropped out. Can you make sure that none of the apparel items are cropped out of the image? Also, can you pick a crewneck that is not turned to the side so it matches the others?

> When I hover over products in the nav, include a dropdown of the collections. Also, make Create Account in the nav look the same as the other options.

> Can you make the font feel more high-end, ivy league university inspired? I want it to be easy to read but feel very elevated.

> Let's go with option 2. Please do not change the logo.

> Now I am looking at the product pages (PDP).
> - Remove this copy: Select a size. Crossed-out sizes are sold out.
> - Add a button to each page that says "ADD TO CART"

**What was lacking after the first prompt:** The first site used a plain "CC" text badge instead of a real Campus Customs logo, so I asked for vintage Yale-inspired logo options. Then I refined the pennant: the lettering covered the stitch marks, the font wasn't vintage enough, and the logo needed to be centered above the nav bar. Finally, the home page felt plain, so I swapped the navy banner for a game-day crowd photo, tightened the header and nav, and removed extra copy and the favorites row. The new collection tiles cut off parts of some garments and the crewneck photo was angled, so I asked for uncropped, front-facing photos. Last, the default fonts felt generic, so I chose a more elevated Ivy-inspired pairing.

---

## Problem 4 — Create account and log in

**Prompt:**
> Looks great. Let's move on to Problem 4. We are going to build a normal create-account and login flow.
> Create account: first name, last name, email, password, confirm password
> Log in: email and password
>
> New accounts should go into the users table. Please store passwords securely so no human or AI hackers can access them.
>
> The see database already has a test user you can us while building:
> Email: test@campuscustoms.yale.edu
> Password: password
>
> Please confirm that you can log in as that user and that a brand new account you create also works.
>
> Update output/harness.md with how the authorization works, including what you store for a user and how you are protecting all user passwords

**Follow-up:** _None yet._

---

## Problem 5 — The shop chatbot (PydanticAI agent behind FastAPI)

**Prompt:**
> Let's do Problem 5. For this problem we are going to build the shop chatbot as a PydanticAI agent behind FastAPI, plugged into the front end chat widget that we already put on the site. Put the API app in backend/main.py (file run with Uvicorn). Keep the agent as these four files next to it:
> backend/prompts/prompt.md - system prompt
> backend/agent.py - agent entry / wiring
> backend/tools.py - tools the agent can call
> backend/models.py - pydantic / pydanticAI structured types
>
> In main.py expose a chat route so a message from the site returns a reply from the agent. Make sure the agent speaks in the Campus Customs tone of voice (very happy, helpful, cheerful, nice) and safety basics into prompts/prompts.md. Start or update types in models.py for chat replies and product cards as needed.
>
> In output/harness.md, note how the front end talks to FastAPI and how the agent is loaded (prompt file + model).
>
> Make sure the backend runs from the backend/ folder like this:
> uvicorn main:app --reload --port 8000

**Follow-up:** _None yet._

---

## Problem 6 — Database lookup tools for description, price, and stock

**Prompt:**
> Let's move on to Problem 6. Now I want to give the agent tools that look up real information from the website campus_customs.db: product description, price, and how many units are in stock (by size when the customer asks).
>
> The agent must use the database for this. Do not invent any information like price or quantities. If a size is out of stock, please say so.
>
> Expand prompts/prompts.md so that the agent knows to call these tools for price and stock questions. Add or update return types in models.py.
>
> In output/harness.md, list each tool and explain which model fields you choise for lookup results and why.

**Follow-up:** _None yet._

---

## Problem 7 — Show chat search results on the page as product cards

**Prompt:**
> Let's move on to Problem 7. Now, we will add a feature to the site. When a customer asks the chatbot about a type of item or category, the agent should search the catalogue and the website should dynamically show any matching items as product cards with their image, name, price, and short info.
>
> this is an an API contract: the agent returns structured product matches and then the front end renders them on the site.
>
> after the dynamic product cards are loaded, ensure the same single-item behavior built in problem 3 still works to open the detail view (PDP) when clicked.
>
> update prompts/prompts.md and output/harness.md so it's clear how search results reach the page.

**Follow-up:** _None yet._

---

## Problem 8 — Saved chat history, who's chatting, and page context

**Prompt:**
> Let's move on to Problem 8. Now, when a shopper is logged in, I want you to save their chat history in the database in an appropriate table and reload it when that shopper returns. The agent should know who is chatting and put that in the agent deps (or an equivalent clear pattern) and/or tools the agent can call.
>
> Also, pass enough page context so that if someone is on a product page and asks "does this come in pink?" the agent knows which item they mean and can look it up for them.
>
> Guests can still chat but the history only needs to persist for logged in users.
>
> Document this in output/harness.md: how user chat history is stored, what customer fields the agent can see, and how page context is passed.

**Follow-up:** _None yet._

---

## Problem 9 — Usability improvements

**Prompt:**
> Let's move on to Problem 9. Now that the website works properly, I want to make a few more changes. Let's do the following:
>
> Front-end usability improvements:
>
> 1. On the collection pages (like all products) add dropdown filters for color and size
> 2. On the collection pages (like all products) add a sort that allows customers to sort by price (from high to low and low to high)
>
> Back-end usability improvements:
>
> 1. Add an avatar of Yale's mascot Handsome Dan next to the chat button so that customers think they are talking to a cute campus mascot
> 2. Instead of being an anonymous customer service agent, make the ai agent pretend to be Handsome Dan when talking to customers
>
> Write output/usability.md before or as you build. For each improvement, say what was added and why it helps a campus customs shopper or the business. Make sure all improvements actually show up in the running app because graders will read the write-up and look for the features.

**Follow-up:** _None yet._

---

## Problem 10 — Creative design write-up

**Prompt:**
> Let's move on to Problem 10. We are supposed to add creative design so the site feels like a real storefront but we already did this earlier when we made changes to the homepage and product pages. can you help me write output/design.md describing everything we've changed and why it helps customers stick around and buy.

**Follow-up:** _None yet._

---

## Problem 11 — Live app check (output/app_check.html)

**Prompt:**
> Let's move on to Problem 11. Test the live site and document it in output/app_check.html (a page that you can double click open). Include clear screenshots and short captions for:
>
> 1. chat checking the inventory level of an item (honest stock/price)
> 2. The dynamic search-results cards appearing after a category question
> 3. One of the usability features we added in Problem 9

**Follow-up prompt:**
> Make the HTML easy to grade with a heading for each check, screenshot, one or two sentences on what the screenshot proves. Put the screenshot images files in output/app_check_images/ and link them from app_check.html with relative paths (for example: app_check_images/inventory.png)

**What was lacking after the first prompt:** The first prompt didn't say how the page should be laid out for grading or where the screenshot files should live, so I asked for one heading, screenshot, and short proof per check, with images saved as separate files linked by relative paths.

---

## Final — Audit trail, safety rules, and completing harness.md

**Prompt:**
> Keep an append-only output/audit_trail.json of agent loop activity (time, tool name, short args/results, stop reason). Do not wipe between runs.
>
> Also, let's add some safety rules for the agent including:
> -Do not recall information about other customers
> -Do not give away any private information
> -Do not make up any information
> -Do not talk about anything that is not Campus Customs related
>
> Add the safety rules to prompts/prompt.md
>
> Finish out/harness.md so it is clear how the system works. Model fields in models.py and why we chose them, tools and abilities, safety rules, and specs including loop limits, result caps, models, and how to run front and back

**Follow-up:** _None yet._

---

## Problem 13 — Package the code in hw4 and publish to a public GitHub repo

**Prompt:**
> Last problem is Problem 13. For this, we are going to put the code in a folder named hw4 and push it to a public GitHub repository. I will be submitting the repo URL on Canvas myself (the link graders can open and clone). I do not need to upload a zip for this homework.
>
> Please do not put my real .env, campus_customs.db, or product images in the Github repo. Use .gitignore. Include .env.example with placeholders only.
>
> The agent itself is four files under backend/: prompts/prompts.md, agents.py, tools.py, and models.py
>
> READ.me should explain how to run the front end and back end after placing the data pack

**Follow-up (answers to the vibe coder's questions before publishing):** I chose to keep the agent file names `prompts/prompt.md` and `agent.py` (as specified in Problem 5), to name the public repo `hw4`, and to include the game-day crowd photo and the audit trail as-is.

**What was lacking after the first prompt:** The file names in this prompt differed from the ones in Problem 5, and the repo name and a couple of borderline public files weren't specified, so those needed a decision before anything was published.

---
