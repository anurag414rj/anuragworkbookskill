# Page recipes

The code below is Code Mode program text, as your generator emits it. Lines
marked `# kit:` are emitted by a `studio_kit.py` helper. Grid: pages and
containers set to column density `high` are 24 columns wide. The sidebar is
always 6 columns. Rename every label to the domain.

Contents: 1 Call A skeleton · 2 Shell · 3 Overview · 4 Signature view ·
5 Work queue + drawer · 6 Ledger · 7 Planner · 8 Agent page · 9 Re-fetching
in later calls · 10 Seeding linked tables

---

## 1 · Call A: skeleton

```python
# kit: tokens()
# theme calls (references/look.md §2)
old_pages = sigma.workbook.list_pages()
ov = sigma.workbook.add_page('Overview')
sig = sigma.workbook.add_page('<Signature view>')
queue = sigma.workbook.add_page('Work Queue')
ledger = sigma.workbook.add_page('<Ledger or Planner>')
agent_pg = sigma.workbook.add_page('<Agent name>')
data_page = sigma.workbook.add_page('Data')
data_page.set_visibility(False)
# input tables + base tables (references/data.md), stacked 12 rows apart on data_page
for p in old_pages:
    p.delete()          # last: a workbook can't reach zero pages
print('OV|' + ov.id())
print('SIG|' + sig.id())
# ... one print per page and per data element the later calls need
```

## 2 · Shell: dark rail + white strip

Built once on the Overview page and attached to every visible page.

```python
side = ov.add_sidebar()
side.set_background_color(PRIMARY)
side.set_border_style('line')
side.set_scroll_behavior('fixed')
side.set_width('medium')
slogo = side.add_image(SITE + '/assets/logo-light.svg')
slogo.set_frame(1, 1, 6, 2)
slogo.set_fit('contain')
slogo.set_horizontal_align('left')
tagline = side.add_text('<p class="p-small"><span style="color: ' + DMUTED + '"><Org or scope> · <place> · mock data</span></p>')
tagline.set_frame(1, 3, 6, 1)
group = side.add_text('<p class="p-small"><span style="color: ' + DMUTED + '"><CONSOLE NAME IN CAPS></span></p>')
group.set_frame(1, 5, 6, 1)
nav = side.add_navigation()
nav.set_frame(1, 6, 6, 13)            # ~2.5 rows per visible page, rounded up
nav.set_orientation('vertical')
nav.set_style('pill')
nav.set_alignment('left')
nav.set_text_color(DMUTED)
nav.set_selected_color(ACCENT)
foot = side.add_divider()
foot.set_frame(1, 20, 6, 1)
foot.set_color('#3a3836')             # a step lighter than INK
who = side.add_text('<p class="p-small"><span style="color: #ffffff">**{{Who}}**</span><br><span style="color: ' + DMUTED + '">{{Mail}}</span></p>',
    formulas={'Who': sigma.formula.current_user_full_name(), 'Mail': sigma.formula.current_user_email()})
who.set_frame(1, 21, 6, 2)
for pg_ in [sig, queue, ledger, agent_pg]:
    pg_.set_sidebar(side)

strip = ov.add_header()
strip.set_background_color('#ffffff')
strip.set_border_style('line')
strip.set_scroll_behavior('fixed')
hlogo = strip.add_image(SITE + '/assets/logo.svg')
hlogo.set_frame(1, 1, 5, 2)
hlogo.set_fit('contain')
hlogo.set_horizontal_align('left')
hc = strip.add_container()
hc.set_frame(11, 1, 14, 2)
hc.set_column_density('high')
hc.set_padding(False)
hc.set_spacing('small')
hc.set_background_color(None)
hc.set_border(None)
pick = sigma.control.add_list_control(hc, target=[dbase.get_column_by_name('<Category>'), obase.get_column_by_name('<Category>')])
pick.set_name('<Category>')           # one picker that re-scopes the log AND the queue
pick.set_frame(1, 1, 13, 2)
ask = hc.add_button('Ask the <Agent name> →')
ask.set_frame(14, 2, 11, 1)           # row 2: level with the picker's input, not its label
ask.set_appearance('solid')
ask.set_shape('pill')
ask.set_button_size('small')
ask.set_align('right')
ask.set_fill_color(PRIMARY)
ask.set_font_color(ACCENT)
ask.on_click('to agent', [sigma.action.navigateEffect.navigate_to(agent_pg)])
for pg_ in [sig, queue, ledger, agent_pg]:
    pg_.set_header(strip)
sigma.workbook.set_page_tabs_hidden_in_view_mode(True)
```

Every page with the rail also gets the strip. Controls in the strip are
reached later via `sigma.workbook.get_element(id)`, not `page.get_element`.

## 3 · Overview

Band order: title (rows 1–4) + chip → hero (5, h 9) → 4 stat cards (14, h 6)
→ tiles label (20) + repeater (22, h 9) → chart pair 14/10 (31, h 14) →
pivot heatmap (45, h 19) → chart pair 14/10 (64, h 14).

```python
# kit: title('tb', 'ov', 'ORG NAME · LAST 12 MONTHS', 'Welcome back, {{Name}}', '<one sentence on what this app is for>',
#            "{'Name': sigma.formula.current_user_first_name()}")
chip = ov.add_text('<p class="p-small" style="text-align: center"><span style="color: ' + DEEP + '">MOCK DATA · PREVIEW</span></p>')
chip.set_frame(19, 2, 6, 1)
chip.set_vertical_align('middle')
chip.set_padding(False)
chip.set_background_color(TINT)
chip.set_border(sigma.border.solid(width=1, color=EDGE, radius='round'))

hero = ov.add_container()
hero.set_frame(1, 5, 24, 9)
hero.set_column_density('high')
hero.set_spacing('small')
hero.set_background_color(PRIMARY)
hero.set_border(sigma.border.solid(radius='round'))
hbg = hero.background_image()
hbg.set_source(SITE + '/assets/hero-dark.svg')
hbg.set_fit('cover')
urgent = sigma.formula.eq(obase.get_column_by_name('Priority'), sigma.formula.const_text('Do today'))
he = hero.add_text('<p class="p-small"><span style="color: ' + ACCENT + '">WHERE YOUR TEAM’S TIME GOES TODAY</span></p>')
he.set_frame(1, 1, 15, 1)
hs = hero.add_text('## <span style="color: #ffffff">{{N}} items to move today, {{H}} hours to clear the board</span>', formulas={
    'N': sigma.formula.text(sigma.formula.count_if(urgent)),
    'H': sigma.formula.text(sigma.formula.round(sigma.formula.divide(sigma.formula.sum(obase.get_column_by_name('Minutes Left')), sigma.formula.const_num(60)), 1))})
hs.set_frame(1, 2, 15, 4)
hs.set_vertical_align('middle')
hl = hero.add_text('<p class="p-small"><span style="color: ' + DMUTED + '"><two sentences: why these come first></span></p>')
hl.set_frame(1, 6, 15, 2)
hgo = hero.add_button('See the <signature view> →')
hgo.set_frame(1, 8, 5, 2)
hgo.set_appearance('solid')
hgo.set_shape('pill')
hgo.set_button_size('small')
hgo.set_fill_color(ACCENT)
hgo.set_font_color(INK)
hgo.set_align('left')                 # buttons center in their cell by default
hgo.on_click('to sig', [sigma.action.navigateEffect.navigate_to(sig)])
hopt = hero.add_button('Work the queue')
hopt.set_frame(6, 8, 5, 2)
hopt.set_appearance('outline')
hopt.set_shape('pill')
hopt.set_button_size('small')
hopt.set_font_color('#ffffff')
hopt.set_align('left')
hopt.on_click('to queue', [sigma.action.navigateEffect.navigate_to(queue)])
# kit: kpi('hk1', 'hero', 'dsrc', (17,2,4,6), ..., dark=True, size=30, vcolor='ACCENT')   — the headline rate
# kit: kpi('hk2', 'hero', 'dsrc', (21,2,4,6), ..., dark=True, size=30)                   — the cycle time
# kit: stat('c1', 'ov', (1,14,6,6), ...)  stat('c2', 'ov', (7,14,6,6), ...)  stat('c3', ...(13,...))  stat('c4', ...(19,...))
```

The hero's text spans columns 1–15. The two KPIs sit at 17–20 and 21–24.
Stat cards are glass cards with a KPI (comparison to the prior window) and a
one-line muted footnote.

**Entity tiles (repeater):**

```python
pj = data_page.add_table(psrc)                         # off the roster base
pj.set_name('<Entity> tiles')
pj.set_frame(1, 105, 24, 8)
pg = pj.set_groupings([pj.get_column_by_name('<Entity>')])[0]
p_name = pg.set_calculation('<Entity> label', sigma.formula.max(pj.get_column_by_name('<Entity>')))
p_meta = pg.set_calculation('Meta text', sigma.formula.ampersand(sigma.formula.text(sigma.formula.max(pj.get_column_by_name('Status'))),
    sigma.formula.ampersand(sigma.formula.const_text(' · '), sigma.formula.ampersand(sigma.formula.text(sigma.formula.round(
    sigma.formula.multiply(sigma.formula.as_num(sigma.formula.max(pj.get_column_by_name('Win Rate'))), sigma.formula.const_num(100)), 0)), sigma.formula.const_text('% won')))))
p_val = pg.set_calculation('Value text', ...)          # '$4.2M of <value> unlocked'
p_cnt = pg.set_calculation('Detail text', sigma.formula.ampersand(        # '6 open now'
    sigma.formula.text(sigma.formula.round(sigma.formula.sum(pj.get_column_by_name('Open Count')), 0)),  # round, or text() prints 6.0000…
    sigma.formula.const_text(' open now')))
pg.set_calculation('Value sort', sigma.formula.sum(pj.get_column_by_name('<Value>')))
if not (isinstance(p_name, FormulaColumn) and isinstance(p_meta, FormulaColumn) and isinstance(p_val, FormulaColumn) and isinstance(p_cnt, FormulaColumn)):
    raise RuntimeError('calc handles')

cl = ov.add_text('<p class="p-large">**Your <entities>**</p>')
cl.set_frame(1, 20, 24, 2)
cards = ov.add_repeater(pj.to_source())
cards.set_frame(1, 22, 24, 9)
cards.set_grouping(pg)
cards.set_card_layout('grid')
cards.set_card_size('medium')           # small clips text; medium shows ~5 per row
cards.set_scroll_type('vertical')
cards.set_card_background_color(PRIMARY)
cards.set_card_border(sigma.border.solid(width=1, color=PRIMARY, radius='round'))
cards.set_background_color(None)
cards.set_padding(False)
cards.set_spacing('small')
cards.set_card_padding(True)
cards.set_card_spacing('small')
rn = cards.add_text('<span style="color: #ffffff">**{{Name}}**</span>', formulas={'Name': p_name})
rn.set_frame(1, 1, 12, 1)
rm = cards.add_text('<p class="p-small"><span style="color: ' + DMUTED + '">{{Meta}}</span></p>', formulas={'Meta': p_meta})
rm.set_frame(1, 2, 12, 1)
rr = cards.add_divider()
rr.set_frame(1, 3, 12, 1)
rr.set_color('#3a3836')
ra = cards.add_text('<p class="p-large"><span style="color: ' + ACCENT + '">**{{Val}}**</span></p>', formulas={'Val': p_val})
ra.set_frame(1, 4, 12, 1)
rb = cards.add_text('<p class="p-small"><span style="color: ' + DMUTED + '">{{Cnt}}</span></p>', formulas={'Cnt': p_cnt})
rb.set_frame(1, 5, 12, 1)
```

**Chart cards** (`card()` = glass card + bold label + muted subtitle on rows 1–2;
chart at `(1, 3, 24, 12)` inside):

```python
# kit: card('s1', 'ov', (1,31,14,14), 'Items in, items won, each week', '<what is counted>')
tr = s1.add_line_chart(dsrc)
tr.set_frame(1, 3, 24, 12)
wk = tr.add_column('Week of', sigma.formula.date_trunc('week', tr.get_column_by_name('Week')))
wk.set_format_pattern('%b %d')
tr.set_dimension(wk)
tr.dimension_axis().set_scale_type('time')
tr.dimension_axis().set_marks('none')
tr.dimension_axis().set_label_angle(0)
tr.set_series([(sigma.formula.sum(tr.get_column_by_name('Item Count')), 'Items in'),
               (sigma.formula.sum(tr.get_column_by_name('Won')), 'Won')])
pair = tr.list_series()
pair[0].set_format('number', decimals=0)
pair[1].set_format('number', decimals=0)
tr.set_series_color(pair[0], SECOND)
tr.set_series_color(pair[1], INK)
tr.value_axis().set_marks('none')
ls = tr.line_style()
ls.set_interpolation('monotone')
ls.set_show_points(False)
ls.set_stroke_width(2)
ls.set_missing('hide')
# kit: chart_tail('tr', legend=True)
```

Repeater cards come out in the source table's order, not by the
`Value sort` calc. If order matters (worst first), sort the tile source and
check the result in the screenshot.

**KPI on a period** (the stat-card pattern; `sum_if(value, condition)`):

```python
L4 = sigma.formula.eq(c1k.get_column_by_name('Period'), sigma.formula.const_text('Last 4 weeks'))
c1k.set_value((sigma.formula.sum_if(c1k.get_column_by_name('Covered'), L4), 'Moved'))   # label ≠ any source column, case-insensitive
```

**Donut:**

```python
dn = s4.add_donut_chart(src)
dn.set_category(dn.get_column_by_name('Type'))
dn.set_values([(sigma.formula.sum(dn.get_column_by_name('Amount')), 'In dispute')])
dn.set_hole_value((sigma.formula.sum(dn.get_column_by_name('Amount')), 'Total in dispute'))
dn.hole().set_size(0.7)
dn.set_category_color('Damage claim', INK)
dn.legend().set_position('right')
```

Other chart shapes that fit the look:
- **Ranked bar**: `set_orientation('horizontal')`,
  `set_sort_by_series('dimension', s, ascending=False)`,
  `set_color_category(<status col>)` + `set_category_color(value, color)` per
  status, `value_axis().set_show_labels(True)`.
- **Stacked bar by month**: `set_color_category(<category>)`,
  `set_stacking('stacked')`. A two-series bar defaults to stacked, so use
  `set_stacking('none')` for side-by-side.
- **Donut**: `set_category`, `set_values`, `set_hole_value((sum, 'Label'))`,
  `hole().set_size(0.7)`, legend right.
- **Heatmap pivot** in a full-width glass card: `add_pivot_row`,
  `add_pivot_column(Month)`, `add_pivot_value`, `presentation` preset with
  white header/row/column/cell backgrounds,
  `conditionalFormat.color_scale([FILL, SECOND, DEEP])` on the value column
  (`'Sum of <col>'`), totals off.

## 4 · Signature view

```python
# kit: title('rt', 'sig', 'FOR <PERSONA>', '<Imperative headline>', '<how to read the view>')
pl = sig.add_container()
pl.set_frame(1, 5, 24, 27)
pl.set_column_density('high')
pl.set_spacing('small')
pl.set_background_color(PRIMARY)
pl.set_border(sigma.border.solid(width=1, color=PRIMARY, radius='round'))
pl.background_image().set_source(DARK_IMG)
pl.background_image().set_fit('stretch')
pll = pl.add_text('<p class="p-small"><span style="color: ' + ACCENT + '"><COMPANY> PLUGIN · <VIEW NAME></span></p>')
pll.set_frame(1, 1, 24, 1)
pls = pl.add_text('<p class="p-small"><span style="color: ' + DMUTED + '"><what each mark means and how it is sorted></span></p>')
pls.set_frame(1, 2, 24, 1)
emb = pl.add_embed(SITE + '/<view>/?demo&dark')
emb.set_name('<View> plugin')
emb.set_frame(1, 3, 24, 25)
```

Two plugin views in one band: put a tabbed container in `pl`, hide its tab
bar, and switch with two pill buttons in row 1:

```python
tc = pl.add_tabbed_container()
tc.set_frame(1, 3, 24, 24)
tc.set_column_density('high')
tabs = tc.list_tabs()
t_a = tabs[0]
t_a.set_name('<View A>')
t_b = tabs[1]
t_b.set_name('<View B>')
tabs[2].delete()                       # a new tabbed container starts with 3 tabs
tc.set_tab_bar_visible(False)
tc.set_padding(False)
tc.set_gap(False)
tc.set_background_color(None)
e_a = t_a.add_embed(SITE + '/view-a/?demo&dark')
e_a.set_frame(1, 1, 24, 22)
e_b = t_b.add_embed(SITE + '/view-b/?demo&dark')
e_b.set_frame(1, 1, 24, 22)
b_a = pl.add_button('<View A>')
b_a.set_frame(17, 1, 4, 2)
b_a.on_click('show a', [sigma.action.selectTabEffect.select_tab(t_a)])
b_b = pl.add_button('<View B>')
b_b.set_frame(21, 1, 4, 2)
b_b.on_click('show b', [sigma.action.selectTabEffect.select_tab(t_b)])
```

Below the band: a white filter bar `(1,32,24,3)` with a muted label and a
single-select searchable list control ("Drill into one <entity>"), then a
chart pair 14/10 and a full-width **scorecard table** (glass card) with
`set_visible_columns([...])`, `set_sort([sigma.sort.descending(col)])`,
`table_style()`, status pills via `cf_text()`, and
`conditionalFormat.data_bars(DEEP, '#c10007', show_values=True)` on the value
column. Add a text `Playbook` column on the base with `sigma.formula.switch_`
over status. It gives the agent and the reader a next step per entity.

## 5 · Work queue + drawer

```python
qsrc = data_page.add_table(opn.to_source())     # opn = the open-items input table
qsrc.set_name('Queue source')
qpick = data_page.add_table(qsrc.to_source())
qpick.set_name('Item picker')

# kit: title('qt', 'queue', 'WORK QUEUE · WRITEBACK', 'Move every open <item> to a decision', '<who edits what>')
# kit: glass('qcard', 'queue', (1,12,24,22)) + label + subtitle (rows 1-2)
lt = qcard.add_linked_input_table(qsrc.to_source(), lookup_columns={'Item ID': 'Item ID'},
    source_columns={'<Source col>': '<Display name>', ...})   # only the columns the reader decides on
lt.set_name('Work queue')
lt.set_edit_mode('published-all-users')
lt.set_frame(1, 3, 24, 20)
l_status = lt.add_single_select_column('Status', ['<stage 1>', '<stage 2>', '...', '<done>'])
l_owner = lt.add_editable_column('Owner', 'text')
l_note = lt.add_editable_column('Next step', 'text')
lt.add_system_columns(['updated_at', 'updated_by'])
pk = lt.list_primary_key_columns()[0]
lt.set_frozen_column(lt.get_column_by_name('Item ID'))
lt.set_sort([sigma.sort.descending(lt.get_column_by_name('Score'))])
# kit: table_style('lt') ; cf_text pills on Priority ; a red formula format on the urgency column
lt.add_conditional_format(lt.list_columns(), sigma.conditionalFormat.formula(sigma.formula.eq(l_status, sigma.formula.const_text('<done>')), background='<accent tint>'))
```

Above it: a glass KPI strip `(1,5,24,5)` with three 5-row KPIs off
`lt.to_source()` (so they move as people edit) at x = 1, 7, 13 (width 5),
vertical dividers at 6, 12, 18, and a muted guidance sentence at
`(19,1,6,5)`. Then a filter bar `(1,10,24,2)` holding a **segmented control**
on Priority, a list control on the entity, and the **"Work an item"** picker
that opens the drawer:

```python
seg = sigma.control.add_segmented_control(bar, options=['Do today', 'This week', 'Later'], target=lt.get_column_by_name('Priority'))
seg.set_name('Priority')
seg.set_frame(1, 1, 9, 2)
```

```python
drawer = sigma.workbook.add_drawer('Work the <item>')
drawer.set_width('medium')
drawer.set_header(title='Work the <item>', show_close_icon=True)
card = drawer.add_single_row_container(lt.to_source(), key_column=pk, initial_value='@@TOPITEM@@')
card.set_frame(1, 1, 12, 22)          # a drawer is 12 columns
card.set_column_density('medium')
card.set_padding(False)
card.set_gap(False)
dname = card.add_text('<p class="p-large">**{{A}} · {{B}}**</p>', formulas={'A': sigma.formula.max(lt.get_column_by_name('<Name>')), 'B': sigma.formula.max(lt.get_column_by_name('<Thing>'))})
dname.set_frame(1, 1, 12, 2)
facts = card.add_value_list(fields={'<Label>': sigma.formula.max(lt.get_column_by_name('<col>')), 'Status': sigma.formula.max(l_status), 'Owner': sigma.formula.max(l_owner)})
facts.set_layout('grid')
facts.set_label_width(0.5)
facts.set_background_color(None)
facts.set_frame(1, 5, 12, 9)
own = sigma.control.add_text_control(card, placeholder='Who owns it?')
own.set_name('Owner')
own.set_frame(1, 14, 12, 2)
note = sigma.control.add_text_area_control(card, placeholder='What happened, what happens next')
note.set_name('Next step')
note.set_frame(1, 16, 12, 4)
b1 = card.add_button('<Primary action>')
b1.set_frame(1, 20, 4, 2)
b1.set_appearance('solid')
b1.set_shape('pill')
b1.set_fill_color(PRIMARY)
b1.set_font_color(ACCENT)
s1 = b1.on_click('act', [
    sigma.action.inputTableEffects.update_rows(lt, {pk: sigma.formula.text(pk)}, {l_status: '<new status>', l_owner: own, l_note: note}),
    sigma.action.refreshElementEffect.refresh_element(lt),
    sigma.action.overlayEffects.close_overlay()])
s1.set_success_toast(title='<Done>', message='{{r}} moved to <status>', formulas={'r': pk})
# two more buttons at x 5 and 9, width 4
drawer.on_close('reset', [sigma.action.clearControlEffect.clear_control(note), sigma.action.clearControlEffect.clear_control(own)])
ip = sigma.control.add_list_control(bar, target=qpick.get_column_by_name('Item ID'), allows_multi=False, allows_search=True)
ip.set_name('Work an item')
ip.set_frame(18, 1, 7, 2)
ip.on_change('open', [sigma.action.setSingleRowViewEffect.select_row(card, ip), sigma.action.overlayEffects.open_overlay(drawer)])
```

`initial_value` must be a real key (the top item from the generator), or the
drawer opens blank.

## 6 · Ledger (exceptions / escalations)

Same as the queue without the drawer: KPI strip (`(1,5,24,5)`, three KPIs with
dividers + guidance text), then a glass card holding a linked input table with
a single-select **Next step** column, Owner and Note, sorted by the
deadline. Add a red formula format when days left < threshold. Then add a
derived table on Data off `elt.to_source()` with a `Status` calc (Not started
/ In progress / Closed), and a stacked horizontal bar of value by entity
colored by that status. It updates as people pick next steps.

## 7 · Planner (month-by-month plan with overrides)

A baseline input table (Month, Month Label, last-year volume) → base with
`Base case` (e.g. LY × 1.12) and `Base rate` constants. On the page: a glass
card with a linked input table keyed on **Month Label**, plus editable
`Your volume`, `Your rate` and `Why`, tinted when overridden
(`is_not_null` → `TINT`, bold). Derived table on Data:

```python
fp.add_column('Plan Volume', sigma.formula.coalesce(fp.get_column_by_name('Your volume'), fp.get_column_by_name('Base case')))
```

Then plan KPIs (with "vs last year" comparisons) stacked at x 1–6 and a
two-series bar (old way vs with product) at `(8,1,17,14)`. A linked table
keyed on a text label sorts alphabetically. Add the real month as a source
column and sort on it.

## 8 · Agent page

```python
# kit: title('ot', 'agent_pg', '<AGENT NAME> · AGENT', '<Imperative: plan the week with the coach>', '<what it reads and writes>')
# kit: glass('ccard', 'agent_pg', (1,5,16,30)) + label + subtitle
chat = ccard.add_chat('<one-line purpose>')
chat.set_frame(1, 3, 24, 28)
chat.set_agent_name('<Agent name>')
chat.set_agent_description('<one sentence>')
chat.set_instructions('<see below>')
chat.set_sources([lt, elt, flt, scorecard, dbase])
chat.set_background_color(None)
chat.set_padding(False)
ag = sigma.agentAction
chat.add_agent_action('Update <item>', 'Update one open <item> in the work queue with a status, owner and next step.', [
    sigma.action.inputTableEffects.update_rows(lt, {pk: ag.agent_input('<Item> ID, exactly as in the queue, for example A-1001')}, {
        l_status: ag.agent_input('Status: exactly one of <list every allowed value>'),
        l_owner: ag.agent_input('Who owns it'),
        l_note: ag.agent_input('Next step in one sentence')}),
    sigma.action.refreshElementEffect.refresh_element(lt),
])
# insert_row works the same way: sigma.action.inputTableEffects.insert_row(plan, {col: ag.agent_input('...'), col2: 'constant'})
```

Right column `(17, …, 8, …)`: a dark KPI tile (`PRIMARY` bg, round, value in
`ACCENT` 30px, 5 rows), a glass card with the urgent count in `RED`, and a
"Try asking" tip card (`TINT`/`EDGE`, `set_padding(True)` or the text
touches the edge) with 4 prompts. Two prompts read, two
write, and they name real ids from the data.

**Instructions template** (plain sentences joined with `+`):
1. Who you coach and the setting. Say "the data is mock data for a demo" if it is.
2. Each source and its columns, in a sentence each.
3. The domain rules that decide priority, with the actual thresholds and formulas.
4. When to use each action: "Use <Action> only when the user says to <verbs>;
   use the exact <ID>." List allowed enum values verbatim.
5. "Confirm what you wrote. Keep answers to 2–4 sentences, plain text, no
   tables or bullet lists." Plus any domain guardrail (no medical, legal or
   financial advice beyond the workflow).

## 9 · Re-fetching in later calls

Each call after A starts by re-fetching what it touches, from the **host it was
added to**, and narrowing the type:

```python
data_page = sigma.workbook.get_page('@@DATA@@')
queue = sigma.workbook.get_page('@@QUEUE@@')
dbase = data_page.get_element('@@DBASE@@')
if not (isinstance(queue, Page) and isinstance(dbase, LevelTable)):
    raise RuntimeError('re-fetch')
qcard = queue.get_element('@@QCARD@@')         # a card's child comes off the card
if not isinstance(qcard, Container):
    raise RuntimeError('card')
lt = qcard.get_element('@@LT@@')
if not isinstance(lt, LinkedInputTable):
    raise RuntimeError('lt')
l_status = lt.get_column_by_name('Status')
if not isinstance(l_status, SingleSelectEditableColumn):   # LiteralEditableColumn for text/number
    raise RuntimeError('cols')
```

## 10 · Seeding linked tables (optional call E)

```python
lt.update_rows([({k: 'A-1001'}, {st: 'Draft ready for review', ow: 'Dana Ruiz'}), ...])
```

`k`, `st` and `ow` are columns fetched by name and narrowed. Seed 60–80% of
rows with owners and a believable spread of statuses, plus a few ledger
decisions with notes, so the app looks lived-in.
