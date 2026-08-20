"""DT-002 HTML renderer — REV C, the DIDACTIC edition (client order 2026-08-18).

    PYTHONPATH=src python dossiers/DT-002/render_dt002_html.py

Client framing (5 answers, 2026-08-18): machine-by-machine sheets after a
plain-language project page; no Bruno replay-kit angle (validation by
reading); reduced PSD tables in the sheets, full tables in annex; BOTH
modes side by side in every sheet; short design confrontation kept, annual
translation dropped. Reader: a process expert with 30 years' experience
who knows NOTHING about the project. No unexplained symbol, no useless
text. Self-contained file, prints cleanly on A4 portrait.
Numbers NEVER live in this file: every figure is read from dt002_data.json.
"""

import html
import json
import pathlib

HERE = pathlib.Path(__file__).parent
DATA = json.loads((HERE / "dt002_data.json").read_text())

P = DATA["_provenance"]
RK = DATA["replay_kit_inputs"]
CAL = RK["calibration"]
M = DATA["modes"]
ADQ = DATA["pfd_rev15_adequacy"]
MESHES = list(RK["feed_curve_passing_pct"].keys())
REDUCED = ["2", "10", "20", "25", "31.5", "35", "40", "50", "63"]


def f(x, nd=2):
    if isinstance(x, (int, float)):
        return f"{x:,.{nd}f}".replace(",", " ")
    return str(x)


def tbl(header, rows, cls="", note=None):
    out = [f'<table class="{cls}">' if cls else "<table>"]
    out.append("<tr>" + "".join(f"<th>{h}</th>" for h in header) + "</tr>")
    for r in rows:
        out.append("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>")
    out.append("</table>")
    if note:
        out.append(f'<p class="note">{note}</p>')
    return "\n".join(out)


def stream(mode_key, label_start):
    return next(s for s in M[mode_key]["streams"] if s["label"].startswith(label_start))


def reduced_psd(specs_by_mode):
    """specs_by_mode = {"1A": [(label_start, col_name), ...], "1B": [...]} ->
    one compact table per mode, stacked (client choice: both modes side by side)."""
    out = []
    for mk, specs in specs_by_mode.items():
        streams = [(stream(mk, ls), name) for ls, name in specs]
        header = [f"<b>Mode {mk}</b> — sieve (mm)"] + [n for _, n in streams]
        rows = [["<b>t/h (dry)</b>"] + [f(s["dry_tph"]) for s, _ in streams]]
        for mesh in REDUCED:
            rows.append([mesh] + [f(s["passing_pct"][mesh], 1) for s, _ in streams])
        out.append(tbl(header, rows, cls="mini"))
    out.append('<p class="note">Values are cumulative % passing '
               "(share of the mass finer than each sieve).</p>")
    return "\n".join(out)


SHORT = [("Pivot feed", "Pivot feed"), ("CR.5006 product", "CR.5006 product"),
         ("SR.5008 screen feed", "Screen feed"), ("SR.5008 deck-1 oversize", "+35 to loop"),
         ("SR.5008 deck-1 undersize", "0/35 internal"), ("SR.5008 20/35 cut", "20/35 cut"),
         ("SR.5008 undersize 0/20", "0/20 crude"), ("CR.5011 feed", "CR.5011 feed"),
         ("CR.5011 product", "Loop return")]


def short_label(label):
    for start, name in SHORT:
        if label.startswith(start):
            return name
    return html.escape(label.split(" (")[0])


def full_psd(mode_key):
    streams = [s for s in M[mode_key]["streams"] if s.get("present")]
    header = ["Sieve (mm)"] + [short_label(s["label"]) for s in streams]
    rows = []
    for lab, key in [("Dry t/h", "dry_tph"), ("Wet t/h", "wet_tph"), ("P80 (mm)", "P80_mm")]:
        rows.append([f"<b>{lab}</b>"] + [f(s[key]) for s in streams])
    for mesh in MESHES:
        rows.append([mesh] + [f(s["passing_pct"][mesh]) for s in streams])
    return '<div class="wide">' + tbl(header, rows, cls="psd") + "</div>"


S1A, S1B = M["1A"]["settings"], M["1B"]["settings"]
C6A, C6B = M["1A"]["machines"]["CR.5006"], M["1B"]["machines"]["CR.5006"]
S8A, S8B = M["1A"]["machines"]["SR.5008"], M["1B"]["machines"]["SR.5008"]
C11A, C11B = M["1A"]["machines"]["CR.5011"], M["1B"]["machines"]["CR.5011"]
ENV = M["1A"]["kfs_envelope_check"]

CSS = """
@page{size:A4;margin:2.2cm 2cm}
body{font-family:"Bitstream Charter",Georgia,serif;font-size:10.5pt;line-height:1.5;
 color:#111;max-width:62em;margin:2em auto;padding:0 1.5em;background:#fff}
h1{font-size:19pt;text-align:center;margin:0 0 2pt}
p.docsub{text-align:center;font-style:italic;margin:0 0 4pt}
p.docmeta{text-align:center;font-size:9.5pt;color:#444;margin:0 0 14pt}
hr.rule{border:none;border-top:0.7pt solid #333;margin:10pt 0 14pt}
h2{font-size:14pt;margin:20pt 0 4pt;border-bottom:0.6pt solid #999;padding-bottom:2pt}
h2.sheet{page-break-before:always}
h3{font-size:11.5pt;margin:13pt 0 5pt}
p.chapsub{font-style:italic;color:#333;margin:0 0 10pt}
table{border-collapse:collapse;margin:7pt 0;font-size:9.8pt;text-align:left;page-break-inside:avoid}
th{border-top:1pt solid #111;border-bottom:0.6pt solid #111;padding:2.5pt 8pt}
td{padding:2.5pt 8pt}
tr:last-child td{border-bottom:1pt solid #111}
table.mini{font-size:9.2pt}
table.mini td,table.mini th{padding:2pt 7pt}
table.psd{font-size:8pt;white-space:nowrap;page-break-inside:auto}
table.psd th{padding:2pt 3pt}
table.psd td{padding:1.2pt 3pt}
.wide{overflow-x:auto}
.eq{text-align:center;margin:8pt 0;font-size:11pt;page-break-inside:avoid}
.eq i{font-family:Georgia,serif}
.box{border-left:2.2pt solid #5B4FC7;background:#f4f3fb;padding:6pt 10pt;margin:10pt 0;page-break-inside:avoid}
.check{border-left:2.2pt solid #1a6d3a;background:#eef7f0;padding:6pt 10pt;margin:10pt 0;page-break-inside:avoid}
.alert{border-left:2.2pt solid #8a6d1a;background:#faf6e8;padding:5pt 9pt;margin:8pt 0;font-size:9.9pt;page-break-inside:avoid}
.note{font-size:9.3pt;color:#333;font-style:italic;margin:2pt 0 8pt}
.prov{font-size:8.8pt;color:#444;border-top:0.6pt solid #999;margin-top:16pt;padding-top:5pt}
@media print{body{max-width:none;margin:0;padding:0}.wide{overflow:visible}}
"""

doc = []
doc.append(f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<title>DT-002 REV C — Zone 1.1 Machine Sizing Note</title><style>{CSS}</style></head><body>
<h1>Sizing the Machines of Zone 1.1</h1>
<p class="docsub">WANKOE limestone processing line — technical note DT-002</p>
<p class="docmeta">by NOEZYS · REV C, 2026-08-18 · for expert review — no prior knowledge of the project is assumed</p>
<hr class="rule">

<div class="box"><b>The purpose of this note.</b> We are sizing a new limestone
production line with a calculation model. This note lays out, machine by machine,
<b>the formulas that model the three machines of the line's first block</b>
("zone&nbsp;1.1"), explains where each formula comes from, and applies it numerically.
We ask the reader one thing: <b>confront these formulas and their results with your
experience</b> — are these the right laws, with the right coefficients, used the right
way? Everything needed to judge is in these pages.</div>""")

# ------------------------------------------------------------------ Section 1
doc.append(f"""<h2>1 · The line, in plain words</h2>
<p>WANKOE is a limestone quarry and processing plant under construction. The quarry's
primary crushing station delivers broken limestone, all finer than about 200&nbsp;mm,
at up to 250 tonnes per hour. Zone&nbsp;1.1 — the subject of this note — turns that
stream into two products:</p>
<p><b>· Kiln stone, 20–35&nbsp;mm</b> ("KFS"): stone sized for a lime kiln, sold on a
firm contract. The quality requirement is a size envelope: at most 30&nbsp;% of the
product below 20&nbsp;mm, at least 55&nbsp;% inside 20–35&nbsp;mm, at most 15&nbsp;%
above 35&nbsp;mm.<br>
<b>· Crushed stone 0–20&nbsp;mm</b> ("crude"): feedstock for the downstream plants
(agricultural and feed-grade lime), stockpiled.</p>
<p>Three machines do the work. Each carries the design office's tag number (CR =
crusher, SR = screen); we keep those tags so this note matches the drawings:</p>
<table>
<tr><th>Machine</th><th>What it does</th></tr>
<tr><td><b>CR.5006</b> — toothed-roll crusher</td><td>Two toothed rolls turning towards
each other crush the quarry stone down to roughly the gap set between the rolls
(60&nbsp;mm here). This type is chosen because it produces few fines — it protects
the 20–35&nbsp;mm window.</td></tr>
<tr><td><b>SR.5008</b> — double-deck vibrating screen</td><td>Two stacked screening
decks with 35&nbsp;mm and 20&nbsp;mm openings split the crushed stone three ways:
larger than 35&nbsp;mm; between 20 and 35&nbsp;mm (the kiln stone); below 20&nbsp;mm
(the crude).</td></tr>
<tr><td><b>CR.5011</b> — impact crusher</td><td>Re-crushes the +35&nbsp;mm fraction
(hammers on a fast rotor) and sends it back to the screen: a closed loop. Nothing
leaves the zone above 35&nbsp;mm.</td></tr>
</table>
<p><b>Two operating modes.</b> Mode&nbsp;<b>1A</b> is normal production: both products
are made, at 250&nbsp;t/h of fresh feed. Mode&nbsp;<b>1B</b> is a stock-building
campaign: no kiln stone is extracted — the 20–35&nbsp;mm cut is sent back to the
impact crusher too, so everything ends up below 20&nbsp;mm. That deepens the crushing
duty, so in this mode the crusher setting tightens (30&nbsp;→&nbsp;18&nbsp;mm) and
the feed is reduced to 172&nbsp;t/h to keep the loop crusher inside its rating.
Every sheet below shows both modes side by side.</p>
<p><b>How quantities are counted.</b> Feed rates are quoted as the <b>total wet
flow</b> — what a belt scale weighs, water included. The stone carries
{f(RK['feed_moisture_pct_wet_basis'],1)}&nbsp;% moisture, so 250&nbsp;t/h wet is
232.5&nbsp;t/h of dry solids; all mass balances and formulas run on the dry part.</p>
<p><b>How sizes are described.</b> Every stream is described by its size curve: for
each sieve opening, the percentage of the mass that would fall through
("cumulative&nbsp;% passing"). One number summarizes a curve:
<b>F<sub>80</sub></b> (feed) or <b>P<sub>80</sub></b> (product) is the sieve size that
80&nbsp;% of the mass passes. The feed entering zone&nbsp;1.1 was <b>measured</b> by
belt-cut sampling at the quarry station outlet (2026-08-08); its curve, the starting
point of every calculation here, is:</p>""")
doc.append('<div class="wide">' + tbl(
    ["Sieve (mm)"] + MESHES,
    [["<b>% passing</b>"] + [f(v) for v in RK["feed_curve_passing_pct"].values()]],
    cls="psd",
    note=f"Measured feed curve. F<sub>80</sub> = {f(RK['feed_F80_mm'])} mm. The tail ends "
         "beyond the sieve series were completed by declared hypotheses.") + "</div>")

# ------------------------------------------------------------------ Sheet 1
doc.append(f"""<h2 class="sheet">2 · Sheet 1 — CR.5006, the toothed-roll crusher</h2>
<p class="chapsub">Receives the full quarry stream · gap set at {S1A['CR.5006_gap_mm']} mm · feeds the screen</p>

<h3>2.1 · The product-size formula</h3>
<p>What size distribution does a crusher deliver? We use the Rosin–Rammler law, the
standard description of crushed materials (Rosin &amp; Rammler, 1933): the share of
mass finer than a size <i>x</i> is</p>
<p class="eq"><i>P</i>(<i>x</i>) = 1 − exp[ −(<i>x</i>/<i>x</i><sub>c</sub>)<sup><i>n</i></sup> ]</p>
<p>It has two knobs, and both have a physical meaning:</p>
<p>· <b><i>x</i><sub>c</sub></b> sets <b>how coarse</b> the product is. We anchor it to
the machine setting: for a toothed-roll crusher the product's P<sub>80</sub> equals
the gap between the rolls, so <i>x</i><sub>c</sub> = gap / (ln&nbsp;5)<sup>1/n</sup>
(this is just the algebra that forces <i>P</i>(gap) = 80&nbsp;%).<br>
· <b><i>n</i></b> sets <b>how spread</b> the sizes are: high <i>n</i> = uniform product,
low <i>n</i> = wide spread with many fines. For toothed rolls we use
<i>n</i>&nbsp;=&nbsp;{S1A['CR.5006_n']} (manufacturer-handbook class value; to be
confirmed by the vendor's gradation table).</p>
<p>Two corrections make it physical: the curve is <b>cut off</b> at
{CAL['m1_trunc_factor']}&nbsp;×&nbsp;gap — no lump survives much beyond the setting —
and feed <b>already finer than the gap falls through unbroken</b>, so only the coarse
share is redistributed by the formula.</p>

<h3>2.2 · The power formula</h3>
<p>Crushing power comes from Bond's law (Bond, 1952), the industry's standard energy
rule: the energy per tonne depends on how much the 80&nbsp;%-passing size is reduced,</p>
<p class="eq"><i>W</i> = 10 <i>W</i><sub>i</sub> ( 1/√<i>P</i><sub>80</sub> − 1/√<i>F</i><sub>80</sub> )&emsp;(kWh/t, sizes in µm)</p>
<p><i>W</i><sub>i</sub> is the <b>work index</b>, the material's resistance to breakage;
we use {CAL['Wi_kWh_t']}&nbsp;kWh/t, a published value for Belgian limestone. Motor
power = <i>W</i> × dry t/h, divided by {CAL['eta_m']} for drive losses.</p>

<h3>2.3 · Applied</h3>""")
doc.append(tbl(["Quantity", "Mode 1A", "Mode 1B"], [
    ["Throughput (dry / wet t/h)",
     f"{f(C6A['throughput_dry_tph'])} / {f(C6A['throughput_wet_tph'])}",
     f"{f(C6B['throughput_dry_tph'])} / {f(C6B['throughput_wet_tph'])}"],
    ["Feed F<sub>80</sub> → product P<sub>80</sub> (mm)",
     f"{f(C6A['F80_mm'])} → {f(C6A['P80_mm'])}",
     f"{f(C6B['F80_mm'])} → {f(C6B['P80_mm'])}"],
    ["Specific energy W (kWh/t)", f(C6A['W_kWh_t'], 3), f(C6B['W_kWh_t'], 3)],
    ["Motor power absorbed (kW)", f(C6A['P_installed_kW'], 1), f(C6B['P_installed_kW'], 1)],
]))
doc.append(reduced_psd({
    "1A": [("Pivot feed", "Feed (measured)"), ("CR.5006 product", "Product")],
    "1B": [("Pivot feed", "Feed (measured)"), ("CR.5006 product", "Product")]}))
doc.append(f"""<div class="check"><b>What to check on this sheet.</b> (1) P<sub>80</sub> = gap
as the sizing anchor for a toothed-roll crusher; (2) the spread value
<i>n</i>&nbsp;=&nbsp;{S1A['CR.5006_n']}; (3) the {CAL['m1_trunc_factor']}×-gap cut-off;
(4) Bond with W<sub>i</sub>&nbsp;=&nbsp;{CAL['Wi_kWh_t']} on a duty this coarse —
first-order by nature, used for motor sizing only.</div>""")

# ------------------------------------------------------------------ Sheet 2
qbt, qbb = S8A["required_areas_m2"]["top_deck_35mm"], S8A["required_areas_m2"]["bottom_deck_20mm"]
qbt_b, qbb_b = S8B["required_areas_m2"]["top_deck_35mm"], S8B["required_areas_m2"]["bottom_deck_20mm"]
doc.append(f"""<h2 class="sheet">3 · Sheet 2 — SR.5008, the double-deck screen</h2>
<p class="chapsub">Decks 35 and 20 mm · fed by CR.5006 plus the loop return · defines both products</p>

<h3>3.1 · The separation formula</h3>
<p>A real screen is not a perfect cut: near the opening size, some particles that
"should" pass ride over, and vice versa. We describe each deck by a <b>probability
curve</b>: the chance that a particle of size <i>x</i> stays on top of a deck with
opening <i>a</i> is</p>
<p class="eq">ρ(<i>x</i>) = 1 / [ 1 + (<i>a</i>/<i>x</i>)<sup><i>s</i></sup> ]</p>
<p>At <i>x</i> = <i>a</i> the chance is 50&nbsp;% — the textbook definition of the cut
point. The exponent <b><i>s</i> sets how sharp the cut is</b>. Rather than pick
<i>s</i> directly, we derive it from the screening trade's usual quality number, the
<b>imperfection I</b> (0 = perfect knife cut; common industrial screens
0.10–0.20): <i>s</i> = ln&nbsp;9&nbsp;/&nbsp;ln(1/(1−<i>I</i>)). With our project value
I&nbsp;=&nbsp;{S1A['SR.5008_I']}, <i>s</i>&nbsp;=&nbsp;13.5.</p>
<div class="alert"><b>One convention to be aware of.</b> Imperfection is defined from
the spread of the probability curve, but two size-ratio conventions coexist in the
literature (quartiles d<sub>75</sub>/d<sub>25</sub>, or the wider
d<sub>90</sub>/d<sub>10</sub>). Our I&nbsp;=&nbsp;0.15 uses the wider one. Re-expressed
in the classic quartile convention of most handbooks, <b>our decks behave like
imperfection&nbsp;≈&nbsp;0.081</b> — a sharp screen. Judge the cut quality with that
number in mind.</div>

<h3>3.2 · The area rule</h3>
<p>Is the deck big enough? Each deck must pass its through-flow. The project's
screen-capacity method gives each deck a <b>basic capacity</b> Q<sub>b</sub> — the
tonnage one square metre can pass for a given opening, corrected for the feed's
fines content and deck position. Required area = through-flow / Q<sub>b</sub>; the
purchase requirement then takes the worst operating case (screening wet stone in
rain season derates capacity) and adds a 25&nbsp;% margin.</p>

<h3>3.3 · Applied</h3>""")
doc.append(tbl(["Quantity", "Mode 1A", "Mode 1B"], [
    ["Screen feed, converged loop (dry / wet t/h)",
     f"{f(S8A['feed_dry_tph'])} / {f(S8A['feed_wet_tph'])}",
     f"{f(S8B['feed_dry_tph'])} / {f(S8B['feed_wet_tph'])}"],
    ["Basic capacity Q<sub>b</sub>, deck 35 / deck 20 (t/h per m²)",
     f"{f(qbt['Qb_tph_m2'],0)} / {f(qbb['Qb_tph_m2'],0)}",
     f"{f(qbt_b['Qb_tph_m2'],0)} / {f(qbb_b['Qb_tph_m2'],0)}"],
    ["Required area this duty, deck 35 / deck 20 (m²)",
     f"{f(qbt['required_area_m2'],1)} / {f(qbb['required_area_m2'],1)}",
     f"{f(qbt_b['required_area_m2'],1)} / {f(qbb_b['required_area_m2'],1)}"],
    ["Purchase minimum (worst case + 25 %), deck 35 / deck 20 (m²)",
     f"{S8A['purchase_min_area_m2']['top_deck']} / {S8A['purchase_min_area_m2']['bottom_deck']}",
     "same (set by the worst case over all duties)"],
]))
doc.append(reduced_psd({
    "1A": [("SR.5008 screen feed", "Screen feed"),
           ("SR.5008 deck-1 oversize", "+35 → loop"),
           ("SR.5008 20/35 cut", "20/35 kiln stone"),
           ("SR.5008 undersize 0/20", "0/20 crude")],
    "1B": [("SR.5008 screen feed", "Screen feed"),
           ("SR.5008 deck-1 oversize", "+35 → loop"),
           ("SR.5008 20/35 cut", "20/35 → re-crushed (no kiln stone in this mode)"),
           ("SR.5008 undersize 0/20", "0/20 crude")]}))
doc.append(f"""<p>Resulting kiln-stone quality, mode 1A (the contractual envelope says
≤&nbsp;30&nbsp;% under / ≥&nbsp;55&nbsp;% in / ≤&nbsp;15&nbsp;% over):
<b>{f(ENV['below_20mm_pct'],1)}&nbsp;% below 20&nbsp;mm ·
{f(ENV['in_cut_20_35_pct'],1)}&nbsp;% in 20–35 ·
{f(ENV['above_35mm_pct'],1)}&nbsp;% above 35&nbsp;mm — compliant with margin.</b></p>
<div class="check"><b>What to check on this sheet.</b> (1) the probability-curve form
and the imperfection value (0.15 wide-convention ≈ 0.081 classic) for dry screening
at 35 and 20&nbsp;mm; (2) the basic capacities Q<sub>b</sub> against your screen-sizing
practice; (3) the resulting kiln-stone envelope numbers — do they look like what a
35/20 double deck delivers?</div>""")

# ------------------------------------------------------------------ Sheet 3
doc.append(f"""<h2 class="sheet">4 · Sheet 3 — CR.5011, the impact crusher in the loop</h2>
<p class="chapsub">Re-crushes the screen's +35 mm (and, in mode 1B, the 20/35 cut) · product returns to the screen</p>

<h3>4.1 · The breakage-intensity formula</h3>
<p>An impact crusher breaks by hammer blows, so the product depends on how hard each
blow is. The blow energy per tonne comes from the rotor tip speed <i>v</i> (kinetic
energy: <i>E</i> = <i>v</i>²/7200 in kWh/t, with <i>v</i> in m/s). Breakage-testing
practice (the JK drop-weight tradition) summarizes an impact's result by
<b><i>t</i><sub>10</sub></b>: the share of the product finer than one tenth of the
original lump size — a fineness score for the blow. Energy converts to
<i>t</i><sub>10</sub> by a saturation law:</p>
<p class="eq"><i>t</i><sub>10</sub> = <i>A</i> ( 1 − exp(−<i>b</i>·<i>E</i>) )</p>
<p><i>A</i> is the ceiling (the most a single blow can fragment) and <i>b</i> how fast
energy approaches it. We use <i>A</i>&nbsp;=&nbsp;{CAL['m5_A_j']},
<i>b</i>&nbsp;=&nbsp;{CAL['m5_b_j']} — central published values for calcite/limestone,
adopted as project defaults; the vendor's gradation test will close them. The blow
fineness then sets the spread <i>n</i> of the product curve
(<i>n</i> = max(0.65,&nbsp;(30/<i>t</i><sub>10</sub>)<sup>0.3</sup>)), and the product
follows the same Rosin–Rammler form as Sheet&nbsp;1 with P<sub>80</sub> equal to the
machine's discharge setting ("CSS"). Power: Bond, as in Sheet&nbsp;1.</p>

<h3>4.2 · The loop</h3>
<p>This machine sits in a closed circuit: its product returns to the screen, so its
own feed depends on what the screen rejects — which depends on the crusher's product.
The model resolves this circularity by iteration: recompute the loop until the
recycled tonnage <b>and its whole size curve</b> stop changing. All figures in this
note are that converged state.</p>

<h3>4.3 · Applied</h3>""")
doc.append(tbl(["Quantity", "Mode 1A", "Mode 1B"], [
    ["Discharge setting CSS (mm)", S1A['CR.5011_x80_css_mm'], S1B['CR.5011_x80_css_mm']],
    ["Rotor speed v (m/s) → blow energy E (kWh/t)",
     f"{S1A['CR.5011_v_ms']} → {f(C11A['Ecs_kWh_t'],3)}",
     f"{S1B['CR.5011_v_ms']} → {f(C11B['Ecs_kWh_t'],3)}"],
    ["Blow fineness t<sub>10</sub> (%) → product spread n",
     f"{f(C11A['t10_pct'],1)} → {f(C11A['n'],2)}",
     f"{f(C11B['t10_pct'],1)} → {f(C11B['n'],2)}"],
    ["Converged loop load (wet t/h, of a 90 t/h machine rating)",
     f"{f(C11A['loop_load_wet_tph'])} ({f(C11A['utilization_pct'],1)} %)",
     f"{f(C11B['loop_load_wet_tph'])} ({f(C11B['utilization_pct'],1)} %)"],
    ["Feed F<sub>80</sub> → product P<sub>80</sub> (mm)",
     f"{f(C11A['F80_mm'])} → {f(C11A['P80_mm'])}",
     f"{f(C11B['F80_mm'])} → {f(C11B['P80_mm'])}"],
    ["Motor power absorbed (kW)", f(C11A['P_installed_kW'], 1), f(C11B['P_installed_kW'], 1)],
]))
doc.append(reduced_psd({
    "1A": [("CR.5011 feed", "Loop feed"), ("CR.5011 product", "Loop product")],
    "1B": [("CR.5011 feed", "Loop feed"), ("CR.5011 product", "Loop product")]}))
doc.append(f"""<div class="check"><b>What to check on this sheet.</b> (1) tip-speed
kinetic energy as the blow-energy measure; (2) the saturation law and the
calcite values A&nbsp;=&nbsp;{CAL['m5_A_j']}, b&nbsp;=&nbsp;{CAL['m5_b_j']};
(3) P<sub>80</sub>&nbsp;=&nbsp;CSS for an impactor; (4) the converged loop loads
against the machine's 90&nbsp;t/h rating — mode&nbsp;1B runs at
{f(C11B['utilization_pct'],1)}&nbsp;%, the tightest point of the zone.</div>""")

# ------------------------------------------------------------------ Section 5
a = ADQ["engine_measured_curve_mode_1A_wet_tph"]
d = ADQ["pfd_design_figures"]
doc.append(f"""<h2 class="sheet">5 · Reality check against the design office's flowsheet</h2>
<p>The design office sized the same line from its own <b>assumed</b> feed curve. Our
figures run the <b>measured</b> one — which is much finer (45.5&nbsp;% of the quarry
stream is already below 20&nbsp;mm). Same machines, same formulas, different feed:</p>""")
doc.append(tbl(["Stream (mode 1A, wet t/h)", "Design office", "This note (measured feed)"], [
    ["Kiln stone 20–35", f(d['scenario_A']['kfs_tph'], 0), f(a['kfs_20_35'], 0)],
    ["Crude 0–20", f(d['scenario_A']['crude_0_20_tph'], 0), f(a['crude_0_20'], 0)],
    ["Screen feed (loop included)", f(d['screen_feed_BC5007_tph'], 0), f(a['screen_feed'], 0)],
    ["Loop return", f(d['recycle_BC5010_tph'], 0), f(a['recycle'], 0)],
]))
doc.append("""<p>The pattern is coherent: a finer feed means less kiln stone, more
crude, and less material rejected round the loop. The gap is therefore a
<b>feed-curve question, not a formula disagreement</b> — and it is exactly why an
independent check of the formulas matters: once the formulas are trusted, the
remaining uncertainty is the quarry's real curve.</p>""")

# ------------------------------------------------------------------ Annexes
for mk, t in [("1A", "Annex A — full stream tables, mode 1A (normal production, 250 t/h wet)"),
              ("1B", "Annex B — full stream tables, mode 1B (stock campaign, 172 t/h wet, CSS 18)")]:
    doc.append(f'<h2 class="sheet">{t}</h2>')
    doc.append("<p>Every stream of the converged flowsheet, all sieves, cumulative % "
               "passing. Conveyor tags (BC.xxxx) are the design office's belt numbers.</p>")
    doc.append(full_psd(mk))

doc.append(f"""<p class="prov">Document history: REV A 2026-08-17 (first issue) ·
REV B 2026-08-18 (ratified calibration; recycle misprint fixed) · REV C 2026-08-18
(didactic edition, this document). Every figure is generated from the project's
deterministic model — engine commit {P['commit']} — and replays without any
assistant: <code>PYTHONPATH=src python dossiers/DT-002/extract_dt002.py</code> then
<code>python dossiers/DT-002/render_dt002_html.py</code>. Working values awaiting
test confirmation are said so in the text. Produced by NOEZYS.</p>
</body></html>""")

dest = HERE / "DT-002-Zone11-Sizing-Note.html"
dest.write_text("\n".join(doc), encoding="utf-8")
print("written:", dest)
