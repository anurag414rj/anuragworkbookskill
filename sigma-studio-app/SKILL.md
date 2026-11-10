---
name: sigma-studio-app
description: 'Builds a branded "studio app" in Sigma: a multi-page workbook that looks and works like the company''s own product, not a BI dashboard. It has a dark app rail, a cinematic hero with live KPIs, frosted glass cards, entity tiles, a custom plugin band, a writeback work queue with a side drawer, and an AI agent page with write actions. Builds through the Sigma MCP connector''s build_workbook (Code Mode) tool. Use this whenever someone wants a "studio", "console", "workspace", "portal", "partner app" or "command app" in Sigma for a named company, team or product line. Also use it for a branded or white-label embedded analytics app, an app that should "look like our website", "glossy", "app-like", "not a boring dashboard", or a demo/POV where users act on the data (triage, assign, approve, plan, escalate) as well as read it. Prefer it over a generic dashboard build whenever a brand and a workflow are both in play.'
---

# Sigma Studio App

A **studio app** is a Sigma workbook built to feel like a product. The reader
lands on a branded home page, sees the one number that matters today, works
a queue, opens a record in a drawer, writes back, and asks an agent to do the
rest. Every studio follows the same skeleton and grammar. Brand, domain and
story change; the structure stays the same. That is what makes them fast to
build and reliably good.

This skill builds studios through the **Sigma MCP connector** (`begin_session`,
`search`, `describe`, `query`, `build_workbook`, `screenshot`, `list_resources`,
`read_resource`). If a tool returns 401/403, ask the user to connect or
re-authorize the Sigma connector, and stop until they have.

## What every studio has

| Layer | What it is | Why |
|---|---|---|
| App shell | Dark left rail (logo, tagline, vertical pill nav, signed-in user) + white top strip (logo, one workbook-wide picker, CTA to the agent). Page tabs hidden. | Reads as an app, not a set of worksheets. One picker re-scopes every page. |
| Home page | Eyebrow + "Welcome back, {first name}" title, a mock/preview chip, a **cinematic dark hero** (original SVG art) whose headline is a live sentence ("**12** cases to move today, **31** staff hours to clear the board"), 2 glass KPIs inside the hero, a row of 4 frosted stat cards with comparisons, a **repeater of dark entity tiles**, then glass chart cards. | The hero answers "what do I do today" in words. KPIs prove it. Tiles make entities feel like objects. |
| Signature view | A **dark plugin band**: a custom HTML visual (the thing the company would build itself) in a dark glass card, plus drill controls and supporting charts below. | The "wow" moment, and the bit no standard chart can do. |
| Work queue | KPI strip → filter bar → **linked input table** (editable status/owner/next step) → a **drawer** that opens one record with buttons that write back and show a toast. | Users act, and the queue updates live. |
| Ledger / planner | A second writeback surface: an escalation or exception ledger, or a month-by-month plan with overrides that flow into KPIs and a chart. | Shows writeback driving the numbers, not just storing notes. |
| Agent page | A named agent (chat) with instructions grounded in the data, 2–3 **write actions** bound to the input tables, a dark KPI tile, and a "Try asking" card. | The agent reads *and* writes the same tables people edit. |
| Data page | Hidden. All seeded input tables and base tables live here. | Keeps visible pages clean; one base per grain. |

Typical page list (rename to the domain): **Overview · <Signature view> ·
Work Queue · <Ledger or Planner> · <Agent name>** (+ hidden **Data**). Five
visible pages is the sweet spot. Fewer is fine for a small story. More than
six dilutes it.

## Flow

Ask what you must, then keep building. A studio with sensible assumptions
named in the report beats a turn that ends in questions.

### 1 · Brief (ask once, up front)

Gather these. Infer from context where possible and ask only for gaps:

1. **Company / product** and its website URL (for the brand).
2. **Who the app is for** (the persona: "a claims-operations team", "a plant manager", "a channel partner"), and the **one job**
   they do in it. The job drives the hero sentence and the queue.
3. **Data mode**:
   - **Real data**: a table or data model already in Sigma. Use `search` /
     `describe`.
   - **Mock data**: seeded input tables. This needs a **write-enabled
     connection** id, so ask which one.
   - **Mixed**: real facts, plus input tables for writeback. This is the usual
     production case.
4. **Asset host** for the logo, glass/hero SVGs and the plugin page: any static
   HTTPS host the user controls (Netlify, Vercel, GitHub Pages, S3 +
   CloudFront, an internal CDN). See `references/look.md` → Hosting. If they
   have none, build without the plugin band and image backgrounds, and say so
   (the flat fallback in `references/look.md`).

Then write a **story sheet** in your head or a scratch file: persona, the one
job, 3 "stories" the data must show (one alarming, one improving, one
surprising), the headline numbers, and the entity the tiles show (suppliers,
lines, sites, partners, accounts). Every page should serve one of those
stories. A studio without stories is just a styled dashboard.

### 2 · Brand

Follow `references/look.md`: pull the site's CSS, lift the palette, type feel,
button shape and hero treatment into a **token block**, and generate the
asset kit with `scripts/make_assets.py`. Use the company's real logo only if
the user owns it or confirms it's OK. Use original artwork for heroes, never
their photography.

### 3 · Data

Follow `references/data.md`. Real data: resolve ids with `describe` and
`query` the literals you will hardcode (status values, categories, date
range). Mock data: write a **seeded, deterministic** generator that makes
the stories true, at a realistic grain. Check the headline numbers *before*
building, because they are the copy.

### 4 · Build: a generator, then 4–5 calls

Studios are too large for one Code Mode program. Write a local Python
**generator** (`build_programs.py`) that emits one program per call, using
`scripts/studio_kit.py` for the repeated chrome (glass cards, titles, KPIs,
tables, conditional pills). Code Mode itself has no `def`, so the helpers run
locally and emit text.

Call plan (each program opens with the same token block):

| Call | Builds | Prints |
|---|---|---|
| A | theme, all pages (created and named), hidden Data page, every input table + seed rows + base tables with calculated columns, delete the starter page | page ids, data element ids |
| B | shell (rail + strip, attached to every page), Overview (title, chip, hero, stat cards, tile repeater, chart cards), Signature view (plugin band, drill bar, charts, scorecard) | element ids later calls need |
| C | Ledger / Planner pages: linked input tables, derived tables on Data, KPIs and charts that read them | linked table + card ids |
| D | Work Queue (linked input table, KPI strip, filter bar, drawer with writeback buttons + toasts, "work a record" picker), Agent page (chat, instructions, sources, write actions, tiles, Try asking) | queue + chat ids |
| E (optional) | seed owners/statuses into linked tables so the app looks lived-in | — |

Between calls, collect the `NAME|id` lines each program prints into
`ids.json`, and fill the next template with `scripts/fill_ids.py` (placeholders
look like `@@NAME@@`). Call A is `target: {type: "new", name, description}`.
**Every later call is `target: {type: "existing", ...}` with the id call A
returned.** A second "new" strands a duplicate workbook.

Page recipes with working code are in `references/pages.md`. Read the
sections for the pages you're building before writing the generator. Read
`references/codemode-traps.md` before the first call, because those traps
cost a round trip each.

If the official `sigma-workbook-quickstart` skill is installed, its
`scripts/check.py` parses a program and folds frames locally. Run it on each
emitted program before submitting. Otherwise rely on typecheck errors, which
are free: a program that fails typecheck runs nothing.

### 5 · Verify

- `screenshot` every visible page (`source: {type: "page", pageId, pixelWidth: 1400}`)
  and walk each one top to bottom. Look for clipped text, blank charts (a
  wrong literal), unreadable text on dark fills, overflowing cards, and empty
  input tables. Page shots omit the sidebar, so that's not a defect.
- `query` the headline numbers the hero and KPIs claim, and confirm they match
  the story sheet.
- Fix everything in one more `existing` call. Re-shoot only the pages whose
  heights changed.
- Agent write actions are often **not exercisable through the API**
  (`call_agent` may report them unavailable). Test the read path with
  `call_agent`, and tell the user to try one write action in the in-workbook
  chat.

### 6 · Report

Give the workbook link, then the pages and what each does, the 3 stories and
their numbers, and what's mock vs real. List what you could not verify (agent
writes, plugin live mode, controls not clicked in a browser), and the one or
two things the user should do in the UI. For example: register the plugin,
or set a date-range default. Keep `build_programs.py`, `ids.json` and the
asset folder together. They are how the next edit happens.

## The look, in one paragraph

Light warm canvas; **ink** rail and hero; one **accent** used sparingly (the
selected nav, the hero eyebrow, the hero's headline KPI, the primary pill
button); white glass cards with a 1px white border, round radius and a faint
gradient + accent glow background image; dark entity tiles with an accent
value line; charts with no title bar, no axis marks, a monotone line, series in
ink + one brand tint; tables in the `presentation` preset with horizontal grid
lines only and **pill-colored status cells**; every number formatted
(`currency_si`, `percent`, sensible decimals). Copy is plain, specific and in
the persona's words: eyebrows in caps, titles that say what to do ("Work the
order that can't wait"), subtitles that say how the number is computed.
Details and exact values are in `references/look.md`.

## Copy rules

- The hero headline is a **live sentence** with `{{formula}}` slots, never a
  static claim.
- Every card has a bold label and a one-line muted subtitle saying what's
  counted, over what window, and what "good" is.
- KPI comparisons name the window ("prior 4 weeks", "last year") and set
  direction (`higher`/`lower` is better).
- Mark mock data visibly (a chip on the home page, a line in the rail) when the
  data is synthetic. Invent people and client names. Never use real
  individuals' names in mock data.
- Nothing is said twice on a page.

## Reference files

| File | Read when |
|---|---|
| `references/look.md` | Step 2: brand extraction, token block, asset kit, hosting, flat fallback |
| `references/data.md` | Step 3: real vs mock data, seeded generators, packing bulk rows, base tables |
| `references/pages.md` | Step 4: code for the shell and each page type |
| `references/plugin.md` | Building the signature-view plugin (snapshot mode → registered plugin) |
| `references/codemode-traps.md` | Before the first `build_workbook` call, and on any confusing error |
| `scripts/studio_kit.py` | Import in your generator: chrome helpers that emit Code Mode text |
| `scripts/make_assets.py` | Generate glass / dark-glass / hero SVGs from your tokens |
| `scripts/fill_ids.py` | Fill `@@NAME@@` placeholders in a template from `ids.json` |
| `assets/plugin-template/` | Starting point for the signature-view plugin page |
