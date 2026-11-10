# Data for a studio

## Pick the mode

| Mode | When | Facts come from | Writeback lives in |
|---|---|---|---|
| Real | Production app, or a POV on the customer's own warehouse | `warehouse_table` / data model / workbook element | input tables on a write-enabled connection |
| Mock | Demo before data access exists | seeded input tables | linked input tables over those |
| Mixed | Most production studios | real tables | input tables keyed on the real ids |

Whatever the mode, the Data page holds one **base table per grain** (event
log, open work items, entity roster, plan baseline). Visible elements read
`base.to_source()` so that one strip picker re-scopes everything.

## Real data

1. `begin_session`, then `search` (or `list_documents`) → `describe` each source.
   `get_column_by_name` takes the **friendly label** from `describe`, not the
   warehouse identifier.
2. `query` every literal the program will hardcode: status values, category
   names for color maps, the date range, and the key's distinct count. A
   guessed literal renders an empty chart.
3. Sources in a program:
   ```python
   base = data_page.add_table(sigma.data.source.warehouse_table('<inode id>'))
   # data model: dm = sigma.data.source.data_model('<inode id>'); pick the member from dm.list_tables() by t.name()
   # workbook element: sigma.data.source.element('<element id>')
   ```
4. Join only at the **same grain**. Aggregate the finer side in its own table
   first. A coarse side joined onto a fine one fans out every aggregate,
   silently.

## Mock data

Write `gen_data.py` locally. Rules that make mock data convincing:

- **Seeded and deterministic** (`random.Random(<fixed seed>)`), with a fixed
  `TODAY` and a fixed "last full week". Re-running must give the same numbers,
  because the copy quotes them.
- **Shaped from the company's public facts**: their categories, their claimed
  rates and cycle times, and realistic volumes (a few hundred to ~2,000 event
  rows). Note the source of each assumption in the docstring.
- **Stories engineered in**: one alarming trend (a ramp, a backlog), one
  improvement (the product's effect), one surprise (one entity behaving
  differently). Print the headline numbers at the end and check them before
  building.
- Invented people and client names. Initials or IDs for anything sensitive
  (patients, employees).
- Output one JSON file with a list per table:
  `{"log": [...], "queue": [...], "roster": [...], "plan": [...]}`.

### Seeding input tables

Input tables need a write-enabled connection id (`CONN`). Column types:
`'text' 'number' 'datetime'`. Emit literal rows from the generator:

```python
it = data_page.add_input_table(CONN)
it.set_name('Open items')
it.set_frame(1, 25, 24, 12)
c_id = it.add_editable_column('Item ID', 'text')
c_dt = it.add_editable_column('Opened On', 'datetime')
c_v = it.add_editable_column('Value', 'number')
it.upsert_rows([{c_id: 'A-1001', c_dt: datetime(2026,10,12,12), c_v: 84000}, ...])
base = data_page.add_table(it.to_source())
base.set_name('Open queue')
base.set_frame(1, 37, 24, 12)
```

- Up to ~1,000 rows × 16 columns in one `upsert_rows` works. Larger logs
  make huge programs. Either roll up to a coarser grain (week × category)
  or **pack** rows: emit short lookup lists (`PAY = ['Aetna', ...]`) plus one
  integer per row encoding the indices, and decode in a comprehension with
  `//` and `%`. For a week × entity grid, emit the 26 weeks and 10 entities
  once and index with `W[i // 10]`, `E[i % 10]`. That alone halves a log
  program.
- Strings can't be indexed or sliced in Code Mode, so pack as ints, never as
  strings.
- Dates: `datetime(y, m, d, 12)` (noon avoids timezone day-shifts).
- Use `''`, not `None`, for missing text in a literal list. Mixing `None` and
  `str` in one field fails the typecheck.
- `studio_kit.py` has `S()`, `N()`, `DTS()` and `L()` to emit lists safely
  (apostrophes become `’`).

## Base-table calculations

Add derived columns on the base, not on each chart, so KPIs, charts and the
agent agree:

```python
one = sigma.formula.const_num(1)
zero = sigma.formula.const_num(0)
base.add_column('Item Count', one)
base.add_column('Won', sigma.formula.if_(sigma.formula.eq(base.get_column_by_name('Outcome'), sigma.formula.const_text('Approved')), one, zero))
wback = sigma.formula.date_diff('week', base.get_column_by_name('Week'), sigma.formula.const_date('2026-10-19'))
base.add_column('Period', sigma.formula.if_(sigma.formula.lt(wback, sigma.formula.const_num(4)), sigma.formula.const_text('Last 4 weeks'),
    sigma.formula.if_(sigma.formula.lt(wback, sigma.formula.const_num(8)), sigma.formula.const_text('Prior 4 weeks'), sigma.formula.const_text('Earlier'))))
m = base.add_column('Month', sigma.formula.date_trunc('month', base.get_column_by_name('Week')))
m.set_format_pattern('%b %Y')
```

- A **Period** column with a fixed anchor makes KPI comparisons stable
  ("last 4 weeks vs prior 4"). For real, live data, anchor on `Today()`
  instead.
- 0/1 flag columns (`Won`, `Decided`, `Filed`) make rates simple:
  `sum_if(Won, period) / sum_if(Decided, period)`.
- A calc whose name matches a source column silently becomes `Name (1)`.
  Always pick a distinct name.

## Tables that sit behind visible elements

- **Repeater source**: a table off the roster grouped by the entity, with
  `set_calculation` columns producing ready-to-print text ("$4.2M of revenue
  recovered", "Tough · 71% won"). The repeater binds those.
- **Queue source**: a plain table off the open-items input table. The
  visible queue is a *linked input table* over it (`references/pages.md`).
- **Picker table**: a second table off the queue source, which a "Work an
  item" list control targets. That way the picker never filters the queue
  itself.
- **Derived tables** off linked input tables (`Escalation status`,
  `Capacity plan`), so KPIs and charts react to edits.
