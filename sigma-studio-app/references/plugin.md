# The signature-view plugin

The plugin is the one view no standard chart can draw, and the thing the
company would build into its own product. Good ones from past studios:

- a **runway / lane view**: one lane per open item, time elapsed vs time left
  vs expected decision, red when they cross
- a **plan view / map**: sites or segments drawn to scale, colored by risk,
  with click-to-focus showing the factor breakdown
- a **line-flow diagram**: stations in sequence with cycle time vs takt
- a **radar / relationship view**: entities by recency and value, with
  "reconnect" candidates highlighted
- a **defect map** traced over a product silhouette

Pick one that makes the persona's job obvious at a glance. It should sort or
flag by what a day of delay costs. The template sorts by least time left
(overdue first), then by value. Change `SORT` if the persona's order differs,
and make the band caption in Sigma say the same thing. In `&dark` mode the
template hides its own title row, because the Sigma band already carries the
eyebrow and caption.

## Two modes, one page

`assets/plugin-template/index.html` supports both:

| Mode | URL | Data | Use for |
|---|---|---|---|
| Snapshot | `…/view/?demo` (`&dark` for the dark band) | `demo.json` beside the page (mock rows) | demos with mock data. Works as a plain `add_embed`, so no registration is needed |
| Live | `…/view/` registered as a Sigma plugin | `subscribeToElementData` on an element + columns picked in the editor panel | real data, real filters, production |

Snapshot mode is quick and always renders. It does **not** react to the
workbook's filters. Say so in the report, and offer live mode as the next
step.

## Build steps

1. Copy `assets/plugin-template/` to `site/<view>/`. Edit `COLUMNS` (editor
   panel keys = the fields the view needs), `render(rows)` (the drawing) and
   `synth()` (fallback rows).
2. Write `demo.json` from the generator: the same rows the queue/base holds,
   as a list of objects with the `COLUMNS` keys.
3. Open the page locally with `?demo` and `?demo&dark` and check that it fills
   its box at ~1200×700 and ~800×500. It must redraw on resize (the template
   has a `ResizeObserver`, because Sigma sizes the frame after first paint).
4. Deploy with the asset site and confirm `https://…/view/?demo&dark` loads.
5. Embed: `pl.add_embed(SITE + '/view/?demo&dark')` (`references/pages.md` §4).

## Going live (registered plugin)

1. A Sigma admin registers the plugin in the Administration portal's
   **Custom Plugins** section, using the production URL (no `?demo`). A registered URL
   can't be edited later, so register a new plugin if the URL changes.
2. In the workbook, replace the embed with the plugin element (Add element →
   Plugins), choose the data source (the queue source or base table), and map
   each editor-panel field to a column.
3. The template reads data with
   `client.elements.subscribeToElementData(config.source, cb)`. It also calls
   `client.config.get()` once at start, because init can land before the
   first `config.subscribe` callback.
4. Check that page filters now change the plugin.

Load the SDK from a pinned version, e.g.
`https://unpkg.com/@sigmacomputing/plugin@<version>/…`. Pick the version from
Sigma's plugin docs. Different builds expose the client as
`window.sigmaComputing.plugin.client` or via `window.SigmaPlugin`, and the
template checks both. If live mode shows the synthetic fallback inside Sigma,
that global is the first suspect. Live mode hasn't been verified for every
SDK build, so test it once before demoing it.
