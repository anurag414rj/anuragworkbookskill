# Code Mode traps

Hit in real studio builds. Each one costs a round trip if you learn it live.
When something here disagrees with the connector's own SDK docs
(`list_resources` / `read_resource`), trust the docs for your server version
and note the drift.

## Dialect

- Not full Python: no `def`, `class`, `lambda` or `while`, no f-strings or
  `.format` (they collapse `{{placeholder}}`), no tuple unpacking in
  comprehensions (`for a, b in zip(...)` is a parse error, so index with
  `range(n)` instead), no slicing, and strings can't be indexed. Join string
  pieces with `+`.
- Builtins are a short list (`print len any enumerate zip range list reversed
  sorted min max str isinstance datetime RuntimeError`). Aggregation is
  `sigma.formula.sum`, never `sum()`.
- A literal list must be one type per field: `''` not `None` for missing text.
- No imports, no `commands.*`, no in-program SQL.

## Errors

- **Typecheck errors run nothing**, so iterate on them freely.
- **Runtime errors leave partial edits**: everything before the failing line
  persisted, everything after didn't (series, styling, prints). Put risky ops
  (deletes, moves) last, and after a runtime error re-check what exists
  before resubmitting. Don't re-add what is already there.
- A result with `persisted: false` built nothing and spent nothing. The next
  call can still be `new`. Once an id comes back, every call is `existing`.

## Formulas and columns

- `max`, `count_distinct` and `lookup` return an untyped `Formula`. Wrap them in
  `sigma.formula.as_num(...)` (or `sigma.formula.number(...)`) before
  `multiply`, `divide` or `round`.
- `add_column` takes a Formula, not a column. Wrap a bare column with
  `sigma.formula.text(col)` / `number(col)` / `date(col)`.
- A calc named like an existing column silently becomes `Name (1)`. Never
  reuse a source column's name (`'Total revenue'`, not `'Revenue'`).
- A KPI **value label** or **chart series name** that matches a source column
  name, **ignoring case** (`'Fell off'` vs `Fell Off`), shadows it. The source
  column becomes `Fell Off (1)` inside that element, and the next
  `get_column_by_name('Fell Off')` fails at runtime, after the element
  has already been created. Give value labels and series names their own words
  (`'Fall-off share'`, `'Fall-offs'`).
- Comparisons with a blank cell are blank, not false:
  `not_(eq(Status, 'Closed'))` silently drops every row with no status yet.
  Count "not X" as `subtract(total, sum_if(..., eq(col, 'X')))`, or wrap the
  column in `coalesce` first.
- `text(sum(col))` prints the raw float (`7.0000000000000000`). Wrap counts in
  `round(..., 0)` before `text()`.
- `set_calculation()` returns `FormulaColumn | ColumnFolder`. Narrow with
  `isinstance(x, FormulaColumn)` before using it in `formulas={}`.
- `date_parse` needs a day: `'01 Nov 2026'` with `'%d %b %Y'`.
- Formulas reference workbook columns only, never raw warehouse columns.

## Linked input tables

- Pull parent columns in with `source_columns={...}` (or
  `add_source_column(name, display)`), **not** `add_formula_column`, which
  shows "multiple values".
- A source column with the same name as the lookup key is silently dropped.
- Hidden linked columns don't flow to tables derived from the linked table.
- Columns fetched back by name must be narrowed to `LiteralEditableColumn` /
  `SingleSelectEditableColumn` before `update_rows` or agent actions accept
  them.
- Keyed on a text label → sorted alphabetically. Add the real date as a source
  column and `set_sort` on it.
- To edit seeded rows of a plain input table: `add_system_columns(['row_id'])`,
  `query` the ids, then `update_rows([(id, {col: val})])`.

## Layout

- Frames are on the **host's** grid: page and containers 24 columns (density
  high), sidebar 6, drawer 12. Child coordinates restart at 1 inside every
  container.
- An element added later can push earlier ones down. Place bands top-down,
  with each y = previous y + previous height.
- A two-series bar chart defaults to stacked. Use `set_stacking('none')` for
  side-by-side.
- KPIs don't stretch to fill their frame. Size a KPI strip at 5 rows with
  5-row KPIs, dividers and guidance text; a 7-row strip leaves a visible empty
  band.
- Codemode classes expose methods, not attributes: `frame().x` doesn't
  typecheck. Re-state the full frame you want instead of reading it back.
- `set_page_order` must list overlays too.

## Shell and controls

- Controls placed in the header strip are fetched with
  `sigma.workbook.get_element(id)`, not `page.get_element`.
- `list_pages()` / `get_page()` return `PageBase`. Narrow with `isinstance(p, Page)`
  before `set_sidebar` or `set_header`.
- A list control with `target=[...]` filters those elements **everywhere they
  are used**. For a picker that should only select (e.g. "work an item"),
  target a separate picker table, never the queue itself.
- Drill controls can't be edited once made. Delete and re-add them.

## Agents

- Agent actions created with `add_agent_action` exist (`list_actions` shows
  them), but `call_agent` through the API may report them unavailable.
  Verify write actions in the in-workbook chat while signed in.
- Deleting a chat leaves its agent behind, and there is no agent delete. Rename
  an orphan "Unused" rather than creating duplicates.

## Workbook management

- There is no copy/duplicate through Code Mode. To work on a copy, ask the user
  to File → Duplicate in Sigma, then `search` for it and edit it as
  `existing`.
- The SDK can't rename a workbook after creation. Pick the name in call A.
- Column renames propagate by id to every child, so a test rename persists.
  Rename it back.

## Verification

- `screenshot` page shots omit the sidebar. Element shots sometimes land on the
  wrong page, and embeds can't be shot as elements ("Not a visualization"),
  so shoot the page. Use `query` to confirm numbers.
- A workbook element is queryable only while it sits on a **visible** page, so
  hidden Data-page tables aren't. Query the visible element built on them.
