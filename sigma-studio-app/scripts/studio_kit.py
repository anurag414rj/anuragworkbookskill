"""Chrome helpers for a Sigma studio-app generator.

Code Mode programs can't define functions, so these run locally in your
build_programs.py and return program TEXT that you concatenate into each call.

    import sys; sys.path.insert(0, "<skill>/scripts")
    from studio_kit import *
    TOK = tokens(dict(CANVAS='#f5f4f2', INK='#252423', ...), site='https://assets.example.com')
    B = TOK + "..." + card("s1", "ov", (1, 31, 14, 14), "Items each week", "What is counted") + "..."

Every helper assumes the token names from references/look.md exist in the program.
"""

DEFAULT_TOKENS = dict(
    CANVAS='#f5f4f2', INK='#252423', BODY='#45423f', MUTED='#6f6b67', DMUTED='#b3aea8',
    HAIRLINE='#e6e3ef', FILL='#f6f5ff', TINT='#f6f5ff', EDGE='#b9b3e0', PRIMARY='#252423',
    ACCENT='#efff92', SECOND='#b9b3e0', DEEP='#5b528f', SERIES_GREY='#cfd7df',
    RED='#d0543c', AMBER='#c98a12', GOOD='#2f7d4f',
)


def tokens(overrides=None, site='', conn='', comment='tokens'):
    """The token block every program opens with."""
    t = dict(DEFAULT_TOKENS)
    t.update(overrides or {})
    out = [f"# {comment}"] + [f"{k} = '{v}'" for k, v in t.items()]
    out += [f"SITE = '{site}'", "GLASS_IMG = SITE + '/assets/glass.svg'",
            "DARK_IMG = SITE + '/assets/dark-glass.svg'", f"CONN = '{conn}'", ""]
    return "\n".join(out) + "\n"


# ---------------------------------------------------------------- literal emitters
def L(xs): return "[" + ",".join(xs) + "]"
def S(xs): return L(["'" + str(x).replace("'", "’") + "'" for x in xs])
def N(xs): return L([("%g" % x) if isinstance(x, float) else str(x) for x in xs])
def DTS(xs): return L([f"datetime({x[:4]},{int(x[5:7])},{int(x[8:10])},12)" for x in xs])
def DT(x): return DTS([x])[1:-1]
def Q(s): return "'" + str(s).replace("'", "’") + "'"


def muted(text, color='MUTED'):
    """A small muted paragraph (a Code Mode string expression)."""
    return "'<p class=\"p-small\"><span style=\"color: ' + " + color + " + '\">" + text.replace("'", "’") + "</span></p>'"


# ---------------------------------------------------------------- surfaces
def glass(var, host, frame, flat=False):
    """White glass card. flat=True drops the background image (no asset host)."""
    x, y, w, h = frame
    out = f"""{var} = {host}.add_container()
{var}.set_frame({x}, {y}, {w}, {h})
{var}.set_column_density('high')
{var}.set_spacing('small')
{var}.set_background_color('#ffffff')
"""
    if flat:
        out += f"{var}.set_border(sigma.border.solid(width=1, color=HAIRLINE, radius='round'))\n"
    else:
        out += f"""{var}.set_border(sigma.border.solid(width=1, color='#ffffff', radius='round'))
{var}.background_image().set_source(GLASS_IMG)
{var}.background_image().set_fit('stretch')
"""
    return out


def dark(var, host, frame, flat=False):
    """Dark glass band (plugin band, feature card)."""
    x, y, w, h = frame
    out = f"""{var} = {host}.add_container()
{var}.set_frame({x}, {y}, {w}, {h})
{var}.set_column_density('high')
{var}.set_spacing('small')
{var}.set_background_color(PRIMARY)
{var}.set_border(sigma.border.solid(width=1, color=PRIMARY, radius='round'))
"""
    if not flat:
        out += f"""{var}.background_image().set_source(DARK_IMG)
{var}.background_image().set_fit('stretch')
"""
    return out


def card(var, host, frame, label, sub, flat=False):
    """Glass card with a bold label (row 1) and muted subtitle (row 2); content goes at (1, 3, 24, h-2)."""
    out = glass(var, host, frame, flat) + f"""{var}_l = {var}.add_text('**{label.replace("'", chr(8217))}**')
{var}_l.set_frame(1, 1, 24, 1)
"""
    if sub:
        out += f"""{var}_s = {var}.add_text({muted(sub)})
{var}_s.set_frame(1, 2, 24, 1)
"""
    return out


def title(var, page, eyebrow, head, sub, formulas=None, width=16):
    """Eyebrow / heading / subtitle block at rows 1-4 of a page."""
    f = f", formulas={formulas}" if formulas else ""
    return f"""{var} = {page}.add_container()
{var}.set_frame(1, 1, {width}, 4)
{var}.set_column_density('high')
{var}.set_padding(False)
{var}.set_gap(False)
{var}.set_background_color(None)
{var}.set_border(None)
{var}_e = {var}.add_text({muted(eyebrow, 'DEEP')})
{var}_e.set_frame(1, 1, 24, 1)
{var}_t = {var}.add_text('## {head.replace("'", chr(8217))}'{f})
{var}_t.set_frame(1, 2, 24, 2)
{var}_s = {var}.add_text({muted(sub)})
{var}_s.set_frame(1, 4, 24, 1)
"""


# ---------------------------------------------------------------- KPIs
def kpi(var, host, src, frame, name, value, fmt, comp=None, dark=False, size=28, vcolor=None):
    """KPI element.
    value: "(<formula expr>, 'Value label')" — the label must not match a source column name,
           ignoring case ('Fell off' collides with 'Fell Off' and breaks the KPI at runtime).
    fmt:   "'number', decimals=0" | "'percent', decimals=0" | "'currency_si', decimals=1, currency='$'"
    comp:  (<formula expr>, 'prior 4 weeks', 'higher'|'lower') or None.
    In expressions, refer to this KPI's columns as {var}.get_column_by_name(...)."""
    x, y, w, h = frame
    vc = vcolor or ("'#ffffff'" if dark else "INK")
    label = value.split("'")[-2]
    out = f"""{var} = {host}.add_kpi({src})
{var}.set_frame({x}, {y}, {w}, {h})
{var}.set_name('{name.replace("'", chr(8217))}')
{var}.set_value({value})
{var}.get_column_by_name('{label}').set_format({fmt})
{var}.title().set_color({'DMUTED' if dark else 'MUTED'})
{var}.title().set_font_size(14)
{var}.title().set_bold(False)
{var}.value_style().set_color({vc})
{var}.value_style().set_font_size({size})
{var}.value_style().set_bold(True)
{var}.layout().set_anchor('left')
{var}.layout().set_vertical_anchor('top')
{var}.set_background_color(None)
"""
    if not dark:
        out += f"{var}.set_padding(False)\n"
    if comp:
        cf, clabel, direction = comp
        out += f"""{var}.set_comparison(({cf}, '{clabel}'))
{var}.comparison_style().set_direction('{direction}')
{var}.comparison_style().set_good_color({"ACCENT" if dark else "GOOD"})
{var}.comparison_style().set_bad_color({"'#f3a08f'" if dark else "'#c10007'"})
{var}.comparison_style().set_label_color({'DMUTED' if dark else 'MUTED'})
"""
    return out


def stat(var, host, frame, name, value, fmt, comp, footnote, src="dsrc", flat=False):
    """Frosted stat card: glass card + KPI (rows 1-4) + muted footnote (rows 5-6). KPI var is {var}k."""
    out = glass(var, host, frame, flat)
    out += kpi(var + "k", var, src, (1, 1, 24, 4), name, value, fmt, comp)
    out += f"""{var}_t = {var}.add_text({muted(footnote)})
{var}_t.set_frame(1, 5, 24, 2)
"""
    return out


# ---------------------------------------------------------------- charts and tables
def chart_tail(v, legend=False, pos='top-left'):
    return f"""{v}.title_style().set_visible(False)
{v}.legend().{"set_position('" + pos + "')" if legend else "set_visible(False)"}
{v}.set_background_color(None)
{v}.set_padding(False)
"""


def table_style(v):
    return f"""{v}_ts = {v}.table_style()
{v}_ts.set_preset('presentation')
{v}_ts.set_grid_lines('horizontal')
{v}_ts.header_style().set_color(MUTED)
for slot in [{v}_ts.header_style(), {v}_ts.cell_style()]:
    slot.set_background_color('#ffffff')
{v}.title_style().set_visible(False)
{v}.set_summary_bar(False)
{v}.set_background_color(None)
{v}.set_padding(False)
"""


def cf_text(v, col, val, bg, fg):
    """Status pill: color a text cell when it equals val."""
    return (f"{v}.add_conditional_format({v}.get_column_by_name('{col}'), sigma.conditionalFormat.formula("
            f"sigma.formula.eq({v}.get_column_by_name('{col}'), sigma.formula.const_text('{val}')), "
            f"background='{bg}', text_color='{fg}', bold=True))\n")


PILL_RED = ('#ffe2e2', '#c10007')
PILL_AMBER = ('#fef3c6', '#bb4d00')


def pill(v, col, val, kind):
    """kind: 'red' | 'amber' | (bg, fg)."""
    bg, fg = {'red': PILL_RED, 'amber': PILL_AMBER}.get(kind, kind) if isinstance(kind, str) else kind
    return cf_text(v, col, val, bg, fg)


def dividers(host, xs, h, y=1):
    """Vertical hairline dividers inside a KPI strip."""
    return f"""for xx in {list(xs)}:
    dv = {host}.add_divider('vertical')
    dv.set_frame(xx, {y}, 1, {h})
    dv.set_color(HAIRLINE)
"""


def prints(*pairs):
    """Emit 'NAME|id' lines: prints(('OV', 'ov'), ('LT', 'lt'))."""
    return "".join(f"print('{k}|' + {v}.id())\n" for k, v in pairs)


def collect_ids(result_text, path="ids.json"):
    """Merge NAME|id lines from a build_workbook result into ids.json."""
    import json, os, re
    ids = json.load(open(path)) if os.path.exists(path) else {}
    for k, v in re.findall(r"^([A-Z][A-Z0-9_]*)\|(\S+)$", result_text, re.M):
        ids[k] = v
    json.dump(ids, open(path, "w"), indent=1)
    return ids
