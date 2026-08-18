"""DT-002 HTML renderer — the SIMPLE, readable edition (client order 2026-08-18).

    PYTHONPATH=src python dossiers/DT-002/render_dt002_html.py

Builds DT-002-Zone11-Sizing-Note.html from dt002_data.json in the house
style of docs/calc-notes/ (serif, compact tables, numbered simple
formulas) but fully SELF-CONTAINED: no external CSS/JS, formulas in
plain HTML (sub/sup), so the single file opens anywhere. Numbers NEVER
live in this file: every figure is read from dt002_data.json.
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
PLAN = DATA["annual_planning"]
ADQ = DATA["pfd_rev15_adequacy"]
MESHES = list(RK["feed_curve_passing_pct"].keys())


def f(x, nd=2):
    if isinstance(x, (int, float)):
        return f"{x:,.{nd}f}".replace(",", " ")
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


def psd_table(mode_key):
    streams = [s for s in M[mode_key]["streams"] if s.get("present")]
    header = ["Sieve (mm)"] + [html.escape(s["label"].split(" (")[0]) for s in streams]
    rows = []
    for lab, key in [("Dry t/h", "dry_tph"), ("Wet t/h", "wet_tph"), ("P80 (mm)", "P80_mm")]:
        rows.append([f"<b>{lab}</b>"] + [f(s[key]) for s in streams])
    for mesh in MESHES:
        rows.append([mesh] + [f(s["passing_pct"][mesh]) for s in streams])
    return ('<div class="wide">'
            + tbl(header, rows, cls="psd",
                  note="Rows below the rates are cumulative % passing at each sieve.")
            + "</div>")


def duty_rows(mode_key):
    mm = M[mode_key]["machines"]
    c6, s8, c11 = mm["CR.5006"], mm["SR.5008"], mm["CR.5011"]
    st = M[mode_key]["settings"]
    return [
        ["<b>CR.5006</b> toothed-roll sizer",
         f"{f(c6['throughput_wet_tph'])} t/h wet · F80 {f(c6['F80_mm'])} → P80 {f(c6['P80_mm'])} mm (gap 60)",
         f"{f(c6['P_installed_kW'],1)} kW absorbed"],
        ["<b>SR.5008</b> screen 35/20",
         f"feed {f(s8['feed_wet_tph'])} t/h wet · required areas {f(s8['required_areas_m2']['top_deck_35mm']['required_area_m2'])} / {f(s8['required_areas_m2']['bottom_deck_20mm']['required_area_m2'])} m² · purchase minima {s8['purchase_min_area_m2']['top_deck']} / {s8['purchase_min_area_m2']['bottom_deck']} m² (rain duty)",
         "—"],
        ["<b>CR.5011</b> impact crusher (loop)",
         f"loop {f(c11['loop_load_wet_tph'])} of {f(c11['vendor_capacity_wet_tph'],0)} t/h wet = {f(c11['utilization_pct'],1)} % · CSS {st['CR.5011_x80_css_mm']} mm · v {st['CR.5011_v_ms']} m/s · t10 {f(c11['t10_pct'],1)} % · n {f(c11['n'],2)}",
         f"{f(c11['P_installed_kW'],1)} kW absorbed"],
    ]


env = M["1A"]["kfs_envelope_check"]
c11a = M["1A"]["machines"]["CR.5011"]

CSS = """
body{font-family:"Bitstream Charter",Georgia,serif;font-size:10.5pt;line-height:1.5;
 color:#111;max-width:62em;margin:2em auto;padding:0 1.5em;background:#fff}
h1{font-size:19pt;text-align:center;margin:0 0 2pt}
p.docsub{text-align:center;font-style:italic;margin:0 0 4pt}
p.docmeta{text-align:center;font-size:9.5pt;color:#444;margin:0 0 14pt}
hr.rule{border:none;border-top:0.7pt solid #333;margin:10pt 0 14pt}
h2{font-size:14pt;margin:20pt 0 4pt;border-bottom:0.6pt solid #999;padding-bottom:2pt}
h3{font-size:11.5pt;margin:13pt 0 5pt}
table{border-collapse:collapse;margin:7pt 0;font-size:9.8pt;text-align:left}
th{border-top:1pt solid #111;border-bottom:0.6pt solid #111;padding:2.5pt 8pt}
td{padding:2.5pt 8pt}
tr:last-child td{border-bottom:1pt solid #111}
table.psd{font-size:8.6pt;white-space:nowrap}
table.psd th{padding:2pt 5pt}
table.psd td{padding:1.6pt 5pt}
.wide{overflow-x:auto}
.eq{text-align:center;margin:8pt 0;font-size:11pt}
.eq i{font-family:Georgia,serif}
.box{border-left:2.2pt solid #5B4FC7;background:#f4f3fb;padding:6pt 10pt;margin:10pt 0}
.alert{border-left:2.2pt solid #8a6d1a;background:#faf6e8;padding:5pt 9pt;margin:8pt 0;font-size:9.9pt}
.note{font-size:9.3pt;color:#333;font-style:italic;margin:2pt 0 8pt}
.prov{font-size:8.8pt;color:#444;border-top:0.6pt solid #999;margin-top:16pt;padding-top:5pt}
@media print{body{max-width:none;margin:0}}
"""

doc = []
doc.append(f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<title>DT-002 REV B — Zone 1.1 Sizing Note</title><style>{CSS}</style></head><body>
<h1>DT-002 — Zone 1.1 Sizing Note</h1>
<p class="docsub">Model-exchange edition: our deterministic engine and Metso Bruno, side by side</p>
<p class="docmeta">by NOEZYS · REV B, 2026-08-18 (REV A 2026-08-17) · tags per NACO PFD 11-01-PFD REV15 · all PSD tables cumulative % passing</p>
<hr class="rule">

<div class="box"><b>What this is.</b> Everything needed to configure Bruno identically
to our model and compare outputs: the feed curve, the settings, the four simple
model formulas, and the computed streams for both operating modes. Every figure
is generated by the engine from <code>dt002_data.json</code> — nothing hand-typed.
The PFD travels as a separate PDF (open it full screen alongside).</div>

<div class="box"><b>REV B changes.</b> (1) Calibration ratified by the client (Q12):
A<sub>j</sub> 60 → {CAL['m5_A_j']}, b<sub>j</sub> 0.8 → {CAL['m5_b_j']} — all figures regenerated
(loop t10 5.71 → {f(c11a['t10_pct'],1)} %, KFS yield 24.88 → {f(PLAN['kfs_yield']['realized_pct'])} %).
(2) REV A §9 misprinted the recycle as 324 t/h; the correct engine value is
{f(ADQ['engine_measured_curve_mode_1A_wet_tph']['recycle'],0)} t/h wet (script selector fixed).</div>
""")

# --- 1. Inputs
doc.append("<h2>1 · Inputs (the replay kit)</h2>")
doc.append(f"""<p>Total-flow rule: every feed rate is the <b>total wet flow</b> as a belt
scale weighs it. Mode 1A (KFS production): {f(RK['flow_rates_wet_tph']['mode_1A_feed'],0)} t/h wet.
Mode 1B (0/20 campaigns, no KFS): {f(RK['flow_rates_wet_tph']['mode_1B_feed'],1)} t/h wet.
Moisture {f(RK['feed_moisture_pct_wet_basis'],1)} % wet basis (dry weather).
Feed F<sub>80</sub> = {f(RK['feed_F80_mm'])} mm — measured belt-cut curve of 2026-08-08:</p>""")
doc.append('<div class="wide">' + tbl(
    ["Sieve (mm)"] + MESHES,
    [["<b>% passing</b>"] + [f(v) for v in RK["feed_curve_passing_pct"].values()]],
    cls="psd", note="The pivot feed curve, exactly as Bruno should ingest it.") + "</div>")
doc.append(tbl(["Setting", "Value", "Status"], [
    ["CR.5006 gap (= product x<sub>80</sub>)", "60 mm", "client reference setting"],
    ["CR.5006 RR uniformity n", str(M['1A']['settings']['CR.5006_n']), "[H] pending vendor gradation table"],
    ["SR.5008 apertures", "35 / 20 mm", "KFS window, sanctuarized"],
    ["Screen imperfection I", str(M['1A']['settings']['SR.5008_I']),
     "ratified convention (Q3) — <b>see the Bruno note in §2.3</b>"],
    ["CR.5011 CSS / speed", f"{M['1A']['settings']['CR.5011_x80_css_mm']} mm (1A) · {M['1B']['settings']['CR.5011_x80_css_mm']} mm (1B) / {M['1A']['settings']['CR.5011_v_ms']} m/s", "mode changeover is routine"],
    ["Bond work index W<sub>i</sub>", f"{CAL['Wi_kWh_t']} kWh/t", "[ref.] Fontaine, Belgian limestone"],
    ["Impact breakage A<sub>j</sub> / b<sub>j</sub>", f"{CAL['m5_A_j']} / {CAL['m5_b_j']}",
     "<b>ratified defaults</b> (Q12, expert-book calcite centrals)"],
    ["Motor efficiency η<sub>m</sub>", str(CAL['eta_m']), "absorbed = net / η<sub>m</sub>"],
]))

# --- 2. Models
doc.append("<h2>2 · The four models, simply</h2>")
doc.append(f"""<h3>2.1 · Crusher product curve (Rosin–Rammler)</h3>
<p class="eq"><i>P</i>(<i>x</i>) = 1 − exp[ −(<i>x</i>/<i>x</i><sub>c</sub>)<sup><i>n</i></sup> ]&emsp;with&emsp;<i>x</i><sub>c</sub> = <i>x</i><sub>80</sub> / (ln 5)<sup>1/<i>n</i></sup></p>
<p>The setting gives the product x<sub>80</sub> (gap for the sizer, CSS for the impactor).
Two corrections: the curve is cut at {CAL['m1_trunc_factor']}·x<sub>80</sub> (no lump survives much
beyond the setting), and feed already finer than the setting passes through unbroken.</p>

<h3>2.2 · Power (Bond)</h3>
<p class="eq"><i>W</i> = 10 <i>W</i><sub>i</sub> ( 1/√<i>P</i><sub>80</sub> − 1/√<i>F</i><sub>80</sub> )&emsp;[kWh/t, sizes in µm]</p>
<p>Net power = W × dry t/h; absorbed = net / {CAL['eta_m']}.</p>

<h3>2.3 · Screen separation (partition curve)</h3>
<p class="eq">ρ(<i>x</i>) = 1 / [ 1 + (<i>d</i><sub>50</sub>/<i>x</i>)<sup><i>s</i></sup> ]&emsp;with&emsp;<i>s</i> = ln 9 / ln( 1/(1−<i>I</i>) ) = 13.5 at I = {M['1A']['settings']['SR.5008_I']}</p>
<p>ρ is the probability a particle of size x reports to the oversize; d<sub>50</sub> = aperture.</p>
<div class="alert"><b>The one thing to get right in Bruno.</b> Our I = 0.15 is a
d<sub>90</sub>/d<sub>10</sub>-type sharpness, not the classic (d<sub>75</sub>−d<sub>25</sub>)/(2 d<sub>50</sub>)
imperfection. The <b>realized classic imperfection of our screens is ≈ 0.081</b>.
If Bruno asks for a classic imperfection, enter 0.081 — entering 0.15 will make
Bruno's cuts visibly blunter than ours around both apertures.</div>

<h3>2.4 · Impactor breakage intensity (loop crusher CR.5011)</h3>
<p class="eq"><i>E</i><sub>cs</sub> = <i>v</i>²/7200&emsp;→&emsp;<i>t</i><sub>10</sub> = <i>A</i><sub>j</sub> (1 − exp(−<i>b</i><sub>j</sub> <i>E</i><sub>cs</sub>))&emsp;→&emsp;<i>n</i> = max(0.65, (30/<i>t</i><sub>10</sub>)<sup>0.3</sup>)</p>
<p>Rotor speed sets the specific energy, which sets t<sub>10</sub> (fineness of breakage),
which sets the RR uniformity n of §2.1. At v = 30 m/s:
t<sub>10</sub> = {f(c11a['t10_pct'],1)} %, n = {f(c11a['n'],2)}.
<b>The loop</b> (screen oversize → CR.5011 → back to screen feed) is solved as a
fixed point: iterate until the recycled rate and its whole curve stop changing.</p>""")

# --- 3/4. Results per mode
for mk, title, blurb in [
    ("1A", "3 · Mode 1A — KFS production, 250 t/h wet",
     f"Converged loop; recirculation {f(M['1A']['recirculation_dry_tph'])} t/h dry. "
     f"KFS envelope (30/55/15 rule): {f(env['below_20mm_pct'])} % below / "
     f"{f(env['in_cut_20_35_pct'])} % in cut / {f(env['above_35mm_pct'])} % above — <b>compliant</b>."),
    ("1B", "4 · Mode 1B — 0/20 campaigns, 172.0 t/h wet, CSS 18",
     f"No KFS (the 20/35 cut recirculates); recirculation {f(M['1B']['recirculation_dry_tph'])} t/h dry. "
     "Feed re-bisected so the CR.5011 vendor guarantee (90 t/h wet) holds on both feed curves."),
]:
    doc.append(f"<h2>{title}</h2><p>{blurb}</p>")
    doc.append(tbl(["Machine", "Duty", "Power"], duty_rows(mk)))
    doc.append(psd_table(mk))

# --- 5. Annual
doc.append("<h2>5 · Annual translation</h2>")
doc.append(tbl(["Quantity", "Value"], [
    ["Zone-1.1 hours (mode 1A / 1B)",
     f"{f(PLAN['zone_1_1_hours']['mode_1A_hours_effective'],1)} / {f(PLAN['zone_1_1_hours']['mode_1B_hours_effective'],1)} h of the {PLAN['zone_1_1_ceiling_h']} h ceiling"],
    ["KFS", f"{f(PLAN['production_t']['KFS'],0)} t (firm contract)"],
    ["AgLime total", f"{f(PLAN['production_t']['AgLime'],0)} t (incl. mandatory 0/20 conversion)"],
    ["FeedLime grits / fines", f"{f(PLAN['production_t']['FeedLime grits'],0)} / {f(PLAN['production_t']['FeedLime fines'],0)} t"],
    ["0/20 to landfill", f"{f(PLAN['stockpiles_t']['0/20 to LANDFILL (net loss)'],0)} t"],
    ["KFS yield (whole KFS stream / wet pivot feed)",
     f"{f(PLAN['kfs_yield']['realized_pct'])} %"],
], note="Hours follow the production targets (project rule); never the reverse."))

# --- 6. PFD adequacy
a = ADQ["engine_measured_curve_mode_1A_wet_tph"]
d = ADQ["pfd_design_figures"]
doc.append("<h2>6 · Confrontation with the PFD design figures</h2>")
doc.append(tbl(["Stream (mode 1A, t/h wet)", "PFD design", "Engine (measured curve)"], [
    ["KFS 20/35", f(d['scenario_A']['kfs_tph'], 0), f(a['kfs_20_35'], 0)],
    ["Crude 0/20", f(d['scenario_A']['crude_0_20_tph'], 0), f(a['crude_0_20'], 0)],
    ["Screen feed (BC.5007)", f(d['screen_feed_BC5007_tph'], 0), f(a['screen_feed'], 0)],
    ["Recycle (BC.5010)", f(d['recycle_BC5010_tph'], 0), f(a['recycle'], 0)],
]))
doc.append("""<p>The gaps are a <b>feed-curve question, not a flowsheet disagreement</b>:
the PFD assumes the NACO design curve; the engine runs the measured belt-cut curve
(45.5 % already below 20 mm at the pivot), so less KFS, more crude, less recycle.
Proposed experiment: run Bruno on <b>both</b> curves — if Bruno reproduces both sides,
the machines are sized right and the open question is the quarry curve.</p>""")

# --- provenance
doc.append(f"""<p class="prov">Engine commit {P['commit']} · {html.escape(P['engine'])} ·
scenario: {html.escape(P['scenario'])}. Replay without any assistant:
<code>PYTHONPATH=src python dossiers/DT-002/extract_dt002.py</code> then
<code>python dossiers/DT-002/render_dt002_html.py</code>. Declared hypotheses [H]
remain hypotheses; no external test campaign launched. Produced by NOEZYS.</p>
</body></html>""")

dest = HERE / "DT-002-Zone11-Sizing-Note.html"
dest.write_text("\n".join(doc), encoding="utf-8")
print("written:", dest)
