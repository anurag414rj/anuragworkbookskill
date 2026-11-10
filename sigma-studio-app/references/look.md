# The studio look

## 1 · Pull the brand from the company's site

The goal: the app looks like it came from the company's own product team.
Glossy and app-like, never a generic BI dashboard.

```bash
curl -sL https://<company>.com -o raw/home.html
# linked stylesheets
grep -oE 'href="[^"]+\.css[^"]*"' raw/home.html
curl -sL <css url> -o raw/site.css
# palette: CSS variables first, then the most frequent hex colors
grep -oE -- '--[a-zA-Z0-9-]+:\s*#[0-9a-fA-F]{3,8}' raw/site.css | sort | uniq -c | sort -rn | head -30
grep -oE '#[0-9a-fA-F]{6}\b' raw/site.css raw/home.html | cut -d: -f2 | sort | uniq -c | sort -rn | head -20
grep -oE 'font-family:[^;]+' raw/site.css | sort | uniq -c | sort -rn | head
# logo: inline <svg> in the nav, or an <img> with "logo" in src/alt
grep -oiE '<img[^>]+logo[^>]*>' raw/home.html | head
```

From that, decide:

| Role | How to pick it |
|---|---|
| `INK` | Their near-black (text / dark sections). The rail, hero and tiles use it. |
| `ACCENT` | Their loudest brand color, the one on their primary buttons. Used sparingly. If it's a neon or a pastel that only reads on dark (a lime or yellow), use it **only on dark surfaces** and pick a deeper `DEEP` tone for light ones. |
| `SECOND` / `DEEP` | A secondary brand hue and a darker step of it. Chart series 2, eyebrows on light, pills. |
| `CANVAS` | A light warm or cool grey close to their page background (`#f5f4f2`, `#f2f2f2`, `#f7f5f0`). Never pure white, because the white glass cards need contrast. |
| Font | Their font if it's a standard family Sigma offers. Otherwise **Inter** (safe) or Geist. Call `theme.list_fonts()` if a font call errors. |
| Button shape | Pill if their buttons are rounded, `round` otherwise. |

Write down the source of each color in a comment in the token block, so the
next editor can trust it.

## 2 · The token block

Every program opens with it (`studio_kit.tokens()` emits it from a dict):

```python
CANVAS = '#f5f4f2'     # page background
INK = '#252423'        # text, rail, hero, tiles
BODY = '#45423f'       # body copy
MUTED = '#6f6b67'      # subtitles, KPI titles, axis
DMUTED = '#b3aea8'     # muted text on dark surfaces
HAIRLINE = '#e6e3ef'   # dividers, filter-bar border
FILL = '#f6f5ff'       # lightest tint, heatmap low end
TINT = '#f6f5ff'       # chip / tip-card background
EDGE = '#b9b3e0'       # chip / tip-card border
PRIMARY = '#252423'    # rail + primary buttons (usually = INK)
ACCENT = '#efff92'     # the brand pop — dark surfaces only if light
SECOND = '#b9b3e0'     # series 2
DEEP = '#5b528f'       # eyebrows on light, deep series
SERIES_GREY = '#cfd7df'
RED = '#d0543c'        # bad
AMBER = '#c98a12'      # warning
GOOD = '#2f7d4f'       # good (comparison up)
SITE = 'https://<your-asset-host>'
GLASS_IMG = SITE + '/assets/glass.svg'
DARK_IMG = SITE + '/assets/dark-glass.svg'
```

Theme calls (call A only):

```python
theme = sigma.workbook.theme()
theme.set_canvas_color(CANVAS)
theme.set_surface_color('#8c8c8c')   # control chrome — never white, or inputs lose their borders
theme.set_text_color(INK)
theme.set_title_color(INK)
theme.set_highlight_color(DEEP)
theme.set_text_font('Inter')
theme.set_data_font('Inter')
theme.set_categorical_scheme([INK, DEEP, SECOND, '#…', SERIES_GREY, AMBER, RED])
theme.set_page_width('large')
```

## 3 · Surface grammar

| Surface | Recipe | Used for |
|---|---|---|
| **Glass card** | container, white bg, `border.solid(width=1, color='#ffffff', radius='round')`, `background_image` = `glass.svg` stretched, density high, spacing small | every chart/table card, KPI strips |
| **Dark glass band** | container, `PRIMARY` bg + border, `background_image` = `dark-glass.svg` stretched | plugin band, dark feature cards |
| **Hero** | container `(1,5,24,9)`, `PRIMARY` bg, round border, `background_image` = `hero-dark.svg`, fit `cover` | home page only |
| **Dark tile** | repeater card bg + border `PRIMARY`, round | entity tiles, agent-page KPI tile |
| **Tint chip / tip** | `TINT` bg, `EDGE` 1px round border | "MOCK DATA" chip, "Try asking" card |
| **Filter bar** | white container, `HAIRLINE` 1px round border, height 2–3 | control rows above a queue or chart |

Text on dark surfaces is `#ffffff` (headline), `DMUTED` (body) and `ACCENT`
(eyebrow, headline KPI). Text color comes from inline spans:
`'<p class="p-small"><span style="color: ' + MUTED + '">…</span></p>'`.
Headings use `## `, labels `**bold**`, big tile values `<p class="p-large">`.

KPIs: title 14px not bold in `MUTED` (`DMUTED` on dark); value 28–30px bold
in `INK` (`#ffffff` or `ACCENT` on dark); anchored left/top; no background.
Comparisons: good `GOOD` (or `ACCENT` on dark), bad `#c10007` (or `#f3a08f`
on dark).

Status pills: conditional format, formula `eq(col, 'Value')`, with soft
backgrounds: red `#ffe2e2`/`#c10007`, amber `#fef3c6`/`#bb4d00`, good
(accent tint)/`INK`, info (`TINT`)/`DEEP`. Bold.

## 4 · The asset kit

`python3 scripts/make_assets.py --ink '#252423' --accent '#efff92' --second '#b9b3e0' --out site/assets`
writes:

- `glass.svg`: white → faint tint diagonal gradient, a top sheen and a corner
  accent glow (`preserveAspectRatio="none"`, so it stretches to any card).
- `dark-glass.svg`: the same on ink.
- `hero-dark.svg`: 1600×340 ink gradient, two soft radial glows (accent and
  second), and abstract contour lines. It's original art, safe to ship.
  Edit the generator if the domain deserves a motif (grid lines for
  utilities, a road for logistics), but keep it abstract.

Logo: save `logo.svg` (for the white strip) and `logo-light.svg` (white
version for the dark rail). For an inline-SVG logo, copy the `<svg>` element
into a file and set `fill` to white for the light version. For a PNG logo,
recolor to white per pixel (PIL) for the dark rail, or put it in a white chip.

## 5 · Hosting

Sigma loads images and embeds from a public HTTPS URL. Any static host works.
Requirements:

- Serve with CORS `Access-Control-Allow-Origin: *` and
  `Content-Security-Policy: frame-ancestors *` (or your Sigma domain), so the
  plugin page can be iframed. `assets/plugin-template/_headers` and
  `netlify.toml` carry both.
- Turn off any host overlay or badge injected into pages. Some hosts add a
  floating badge that shows up inside the iframe. On Netlify that's the
  site setting `built_with_badge_enabled: false`
  (`netlify api updateSite --data '{"site_id":"<id>","body":{"built_with_badge_enabled":false}}'`),
  then redeploy.
- If `netlify deploy --prod` fails with `Forbidden`, deploy a draft
  (`netlify deploy --dir site --json`) and promote it with
  `netlify api restoreSiteDeploy --data '{"site_id":"<id>","deploy_id":"<draft id>"}'`.
  A fresh CDN path can 404 for a few seconds after promotion.
- URLs are effectively permanent once a plugin is registered against them
  (a registered plugin's URL can't be edited), so pick a stable path.
- Don't put anything confidential on a public host. The SVGs and a snapshot
  `demo.json` of **mock** data are fine. Real customer data is not; use live
  plugin mode for that (`references/plugin.md`).

## 6 · Flat fallback (no asset host)

Drop every `background_image()` call. Glass card = white bg + `HAIRLINE`
border. Hero = `PRIMARY` bg, no art. The rail shows the company name as
`**bold**` white text instead of a logo. Skip the plugin band and put a
second chart card or a tabbed chart+table in its place. It's still a studio,
just less glossy. Say so in the report.
