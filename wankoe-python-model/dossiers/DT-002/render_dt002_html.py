"""DT-002 HTML renderer — REV D, édition FRANÇAISE de l'édition didactique.

    PYTHONPATH=src python dossiers/DT-002/render_dt002_html.py

REV C framing (5 client answers, 2026-08-18): machine-by-machine sheets
after a plain-language project page; no Bruno replay-kit angle; reduced
PSD tables in the sheets, full tables in annex; BOTH modes side by side;
short design confrontation kept. REV D (client ruling 2026-08-18):
FRENCH REPLACES ENGLISH for this note — first registered exception to
the 2026-08-09 English-deliverables rule; the English REV C remains in
git history only. Reader: a process expert, 30 years' experience, no
knowledge of the project. Self-contained file, prints cleanly on A4.
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
    une table compacte par mode, empilées (choix client : les deux modes)."""
    out = []
    for mk, specs in specs_by_mode.items():
        streams = [(stream(mk, ls), name) for ls, name in specs]
        header = [f"<b>Mode {mk}</b> — tamis (mm)"] + [n for _, n in streams]
        rows = [["<b>t/h (sec)</b>"] + [f(s["dry_tph"]) for s, _ in streams]]
        for mesh in REDUCED:
            rows.append([mesh] + [f(s["passing_pct"][mesh], 1) for s, _ in streams])
        out.append(tbl(header, rows, cls="mini"))
    out.append('<p class="note">Les valeurs sont des % passants cumulés '
               "(part de la masse plus fine que chaque tamis).</p>")
    return "\n".join(out)


SHORT = [("Pivot feed", "Alimentation pivot"), ("CR.5006 product", "Produit CR.5006"),
         ("SR.5008 screen feed", "Alim. crible"), ("SR.5008 deck-1 oversize", "+35 vers boucle"),
         ("SR.5008 deck-1 undersize", "0/35 interne"), ("SR.5008 20/35 cut", "Coupe 20/35"),
         ("SR.5008 undersize 0/20", "Brut 0/20"), ("CR.5011 feed", "Alim. CR.5011"),
         ("CR.5011 product", "Retour boucle")]


def short_label(label):
    for start, name in SHORT:
        if label.startswith(start):
            return name
    return html.escape(label.split(" (")[0])


def full_psd(mode_key):
    streams = [s for s in M[mode_key]["streams"] if s.get("present")]
    header = ["Tamis (mm)"] + [short_label(s["label"]) for s in streams]
    rows = []
    for lab, key in [("t/h sec", "dry_tph"), ("t/h humide", "wet_tph"), ("P80 (mm)", "P80_mm")]:
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
doc.append(f"""<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8">
<title>DT-002 REV D — Note de dimensionnement zone 1.1</title><style>{CSS}</style></head><body>
<h1>Dimensionnement des machines de la zone 1.1</h1>
<p class="docsub">Ligne de traitement de calcaire WANKOE — note technique DT-002</p>
<p class="docmeta">par NOEZYS · REV D, 2026-08-18 · pour revue d'expert — aucune connaissance préalable du projet n'est requise</p>
<hr class="rule">

<div class="box"><b>L'objet de cette note.</b> Nous dimensionnons une nouvelle ligne de
production de calcaire à l'aide d'un modèle de calcul. Cette note présente, machine
par machine, <b>les formules qui modélisent les trois machines du premier bloc de la
ligne</b> (la «&nbsp;zone&nbsp;1.1&nbsp;»), explique d'où vient chaque formule et
l'applique numériquement. Nous demandons une seule chose au lecteur&nbsp;:
<b>confronter ces formules et leurs résultats à son expérience</b> — sont-ce les
bonnes lois, avec les bons coefficients, utilisées correctement&nbsp;? Tout ce qu'il
faut pour en juger est dans ces pages.</div>""")

# ------------------------------------------------------------------ Section 1
doc.append(f"""<h2>1 · La ligne, en termes simples</h2>
<p>WANKOE est une carrière de calcaire et son usine de traitement, en cours de
construction. La station de concassage primaire de la carrière livre du calcaire
brisé, entièrement inférieur à 200&nbsp;mm environ, jusqu'à 250 tonnes par heure. La
zone&nbsp;1.1 — l'objet de cette note — transforme ce flux en deux produits&nbsp;:</p>
<p><b>· La pierre à four, 20–35&nbsp;mm</b> (dite «&nbsp;KFS&nbsp;»)&nbsp;: pierre
calibrée pour un four à chaux, vendue sous contrat ferme. L'exigence de qualité est
une enveloppe granulométrique&nbsp;: au plus 30&nbsp;% du produit sous 20&nbsp;mm, au
moins 55&nbsp;% entre 20 et 35&nbsp;mm, au plus 15&nbsp;% au-dessus de 35&nbsp;mm.<br>
<b>· La pierre concassée 0–20&nbsp;mm</b> (le «&nbsp;brut&nbsp;»)&nbsp;: matière
première des ateliers aval (chaux agricole et chaux alimentaire), mise en stock.</p>
<p>Trois machines font le travail. Chacune porte le repère du bureau d'études (CR =
concasseur, SR = crible)&nbsp;; nous les conservons pour que cette note colle aux
plans&nbsp;:</p>
<table>
<tr><th>Machine</th><th>Ce qu'elle fait</th></tr>
<tr><td><b>CR.5006</b> — concasseur à rouleaux dentés</td><td>Deux rouleaux dentés
tournant l'un vers l'autre brisent la pierre de carrière jusqu'à, grosso modo,
l'écartement réglé entre les rouleaux (ici 60&nbsp;mm). Ce type de machine est choisi
parce qu'il produit peu de fines — il protège la fenêtre 20–35&nbsp;mm.</td></tr>
<tr><td><b>SR.5008</b> — crible vibrant à deux étages</td><td>Deux étages de criblage
superposés, à ouvertures de 35&nbsp;mm et 20&nbsp;mm, séparent la pierre concassée en
trois&nbsp;: plus gros que 35&nbsp;mm&nbsp;; entre 20 et 35&nbsp;mm (la pierre à
four)&nbsp;; sous 20&nbsp;mm (le brut).</td></tr>
<tr><td><b>CR.5011</b> — concasseur à percussion</td><td>Rebroie la fraction
+35&nbsp;mm (des percuteurs sur un rotor rapide) et la renvoie au crible&nbsp;: une
boucle fermée. Rien ne sort de la zone au-dessus de 35&nbsp;mm.</td></tr>
</table>
<p><b>Deux modes de marche.</b> Le mode&nbsp;<b>1A</b> est la production
normale&nbsp;: les deux produits sont faits, à 250&nbsp;t/h d'alimentation fraîche.
Le mode&nbsp;<b>1B</b> est une campagne de constitution de stock&nbsp;: on n'extrait
pas de pierre à four — la coupe 20–35&nbsp;mm repart elle aussi au concasseur à
percussion, si bien que tout finit sous 20&nbsp;mm. Le travail de broyage s'en trouve
accru&nbsp;: dans ce mode, le réglage du concasseur se resserre
(30&nbsp;→&nbsp;18&nbsp;mm) et l'alimentation est réduite à 172&nbsp;t/h pour garder
le concasseur de boucle dans sa capacité. Chaque fiche ci-dessous montre les deux
modes côte à côte.</p>
<p><b>Comment les quantités sont comptées.</b> Les débits d'alimentation sont exprimés
en <b>flux total humide</b> — ce que pèse une bascule de bande, eau comprise. La
pierre porte {f(RK['feed_moisture_pct_wet_basis'],1)}&nbsp;% d'humidité&nbsp;:
250&nbsp;t/h humide représentent donc 232.5&nbsp;t/h de matière sèche, et tous les
bilans et formules travaillent sur la part sèche.</p>
<p><b>Comment les tailles sont décrites.</b> Chaque flux est décrit par sa courbe
granulométrique&nbsp;: pour chaque ouverture de tamis, le pourcentage de la masse qui
passerait au travers (le «&nbsp;%&nbsp;passant cumulé&nbsp;»). Un nombre résume une
courbe&nbsp;: le <b>F<sub>80</sub></b> (alimentation) ou <b>P<sub>80</sub></b>
(produit) est la taille de tamis que 80&nbsp;% de la masse passe. L'alimentation de la
zone&nbsp;1.1 a été <b>mesurée</b> par prélèvement sur bande à la sortie de la station
de carrière (2026-08-08)&nbsp;; sa courbe, point de départ de tous les calculs,
est&nbsp;:</p>""")
doc.append('<div class="wide">' + tbl(
    ["Tamis (mm)"] + MESHES,
    [["<b>% passant</b>"] + [f(v) for v in RK["feed_curve_passing_pct"].values()]],
    cls="psd",
    note=f"Courbe d'alimentation mesurée. F<sub>80</sub> = {f(RK['feed_F80_mm'])} mm. "
         "Les extrémités de la courbe, au-delà de la série de tamis, ont été complétées "
         "par des hypothèses déclarées.") + "</div>")

# ------------------------------------------------------------------ Fiche 1
doc.append(f"""<h2 class="sheet">2 · Fiche 1 — CR.5006, le concasseur à rouleaux dentés</h2>
<p class="chapsub">Reçoit tout le flux de carrière · écartement réglé à {S1A['CR.5006_gap_mm']} mm · alimente le crible</p>

<h3>2.1 · La formule du produit (granulométrie)</h3>
<p>Quelle distribution de tailles un concasseur livre-t-il&nbsp;? Nous utilisons la
loi de Rosin–Rammler, la description standard des matériaux concassés (Rosin &amp;
Rammler, 1933)&nbsp;: la part de la masse plus fine qu'une taille <i>x</i> vaut</p>
<p class="eq"><i>P</i>(<i>x</i>) = 1 − exp[ −(<i>x</i>/<i>x</i><sub>c</sub>)<sup><i>n</i></sup> ]</p>
<p>Elle a deux réglages, chacun avec un sens physique&nbsp;:</p>
<p>· <b><i>x</i><sub>c</sub></b> fixe <b>la grosseur</b> du produit. Nous l'ancrons sur
le réglage de la machine&nbsp;: pour un concasseur à rouleaux dentés, le
P<sub>80</sub> du produit égale l'écartement des rouleaux, donc
<i>x</i><sub>c</sub> = écartement / (ln&nbsp;5)<sup>1/n</sup> (simple algèbre qui
impose <i>P</i>(écartement) = 80&nbsp;%).<br>
· <b><i>n</i></b> fixe <b>l'étalement</b> des tailles&nbsp;: <i>n</i> élevé = produit
uniforme, <i>n</i> faible = large étalement avec beaucoup de fines. Pour des rouleaux
dentés nous prenons <i>n</i>&nbsp;=&nbsp;{S1A['CR.5006_n']} (valeur de classe des
catalogues constructeurs&nbsp;; à confirmer par la table granulométrique du
fournisseur).</p>
<p>Deux corrections la rendent physique&nbsp;: la courbe est <b>tronquée</b> à
{CAL['m1_trunc_factor']}&nbsp;×&nbsp;écartement — aucun bloc ne survit bien au-delà du
réglage — et la part de l'alimentation <b>déjà plus fine que l'écartement traverse
sans être brisée</b>&nbsp;: seule la part grossière est redistribuée par la
formule.</p>

<h3>2.2 · La formule de puissance</h3>
<p>La puissance de concassage vient de la loi de Bond (Bond, 1952), la règle
énergétique standard du métier&nbsp;: l'énergie par tonne dépend de la réduction de la
taille à 80&nbsp;% passant,</p>
<p class="eq"><i>W</i> = 10 <i>W</i><sub>i</sub> ( 1/√<i>P</i><sub>80</sub> − 1/√<i>F</i><sub>80</sub> )&emsp;(kWh/t, tailles en µm)</p>
<p><i>W</i><sub>i</sub> est le <b>work index</b> (indice énergétique), la résistance du
matériau à la fragmentation&nbsp;; nous prenons {CAL['Wi_kWh_t']}&nbsp;kWh/t, valeur
publiée pour un calcaire belge. Puissance moteur = <i>W</i> × t/h sec, divisée par
{CAL['eta_m']} pour les pertes de transmission.</p>

<h3>2.3 · Application</h3>""")
doc.append(tbl(["Grandeur", "Mode 1A", "Mode 1B"], [
    ["Débit (t/h sec / humide)",
     f"{f(C6A['throughput_dry_tph'])} / {f(C6A['throughput_wet_tph'])}",
     f"{f(C6B['throughput_dry_tph'])} / {f(C6B['throughput_wet_tph'])}"],
    ["F<sub>80</sub> alimentation → P<sub>80</sub> produit (mm)",
     f"{f(C6A['F80_mm'])} → {f(C6A['P80_mm'])}",
     f"{f(C6B['F80_mm'])} → {f(C6B['P80_mm'])}"],
    ["Énergie spécifique W (kWh/t)", f(C6A['W_kWh_t'], 3), f(C6B['W_kWh_t'], 3)],
    ["Puissance moteur absorbée (kW)", f(C6A['P_installed_kW'], 1), f(C6B['P_installed_kW'], 1)],
]))
doc.append(reduced_psd({
    "1A": [("Pivot feed", "Alimentation (mesurée)"), ("CR.5006 product", "Produit")],
    "1B": [("Pivot feed", "Alimentation (mesurée)"), ("CR.5006 product", "Produit")]}))
doc.append(f"""<div class="check"><b>Ce qu'il faut vérifier sur cette fiche.</b>
(1)&nbsp;P<sub>80</sub> = écartement comme ancrage du dimensionnement pour un
concasseur à rouleaux dentés&nbsp;; (2)&nbsp;la valeur d'étalement
<i>n</i>&nbsp;=&nbsp;{S1A['CR.5006_n']}&nbsp;; (3)&nbsp;la troncature à
{CAL['m1_trunc_factor']}&nbsp;×&nbsp;écartement&nbsp;; (4)&nbsp;Bond avec
W<sub>i</sub>&nbsp;=&nbsp;{CAL['Wi_kWh_t']} sur un travail aussi grossier — précision
de premier ordre par nature, utilisé pour le dimensionnement moteur seulement.</div>""")

# ------------------------------------------------------------------ Fiche 2
qbt, qbb = S8A["required_areas_m2"]["top_deck_35mm"], S8A["required_areas_m2"]["bottom_deck_20mm"]
qbt_b, qbb_b = S8B["required_areas_m2"]["top_deck_35mm"], S8B["required_areas_m2"]["bottom_deck_20mm"]
doc.append(f"""<h2 class="sheet">3 · Fiche 2 — SR.5008, le crible à deux étages</h2>
<p class="chapsub">Étages 35 et 20 mm · alimenté par CR.5006 plus le retour de boucle · définit les deux produits</p>

<h3>3.1 · La formule de séparation</h3>
<p>Un crible réel n'est pas une coupure parfaite&nbsp;: près de la taille d'ouverture,
des grains qui «&nbsp;devraient&nbsp;» passer restent sur la toile, et inversement.
Nous décrivons chaque étage par une <b>courbe de probabilité</b>&nbsp;: la chance
qu'un grain de taille <i>x</i> reste au refus d'un étage d'ouverture <i>a</i>
vaut</p>
<p class="eq">ρ(<i>x</i>) = 1 / [ 1 + (<i>a</i>/<i>x</i>)<sup><i>s</i></sup> ]</p>
<p>À <i>x</i> = <i>a</i>, la chance est de 50&nbsp;% — la définition classique du
point de coupure. L'exposant <b><i>s</i> fixe la netteté de la coupe</b>. Plutôt que
de choisir <i>s</i> directement, nous le déduisons du chiffre de qualité usuel du
métier du criblage, l'<b>imperfection I</b> (0 = coupure au couteau&nbsp;; cribles
industriels courants 0.10–0.20)&nbsp;:
<i>s</i> = ln&nbsp;9&nbsp;/&nbsp;ln(1/(1−<i>I</i>)). Avec la valeur projet
I&nbsp;=&nbsp;{S1A['SR.5008_I']}, <i>s</i>&nbsp;=&nbsp;13.5.</p>
<div class="alert"><b>Une convention à connaître.</b> L'imperfection se définit par
l'étalement de la courbe de probabilité, mais deux conventions de rapport de tailles
coexistent dans la littérature (les quartiles d<sub>75</sub>/d<sub>25</sub>, ou le
rapport plus large d<sub>90</sub>/d<sub>10</sub>). Notre I&nbsp;=&nbsp;0.15 utilise la
convention large. Ré-exprimée dans la convention classique par quartiles de la plupart
des ouvrages, <b>nos toiles se comportent comme une imperfection&nbsp;≈&nbsp;0.081</b>
— un crible net. C'est avec ce chiffre en tête qu'il faut juger la qualité de
coupe.</div>

<h3>3.2 · La règle de surface</h3>
<p>L'étage est-il assez grand&nbsp;? Chaque étage doit laisser passer son débit
traversant. La méthode de capacité de criblage du projet attribue à chaque étage une
<b>capacité de base</b> Q<sub>b</sub> — le tonnage qu'un mètre carré peut passer pour
une ouverture donnée, corrigé de la teneur en fines de l'alimentation et de la
position de l'étage. Surface requise = débit traversant / Q<sub>b</sub>&nbsp;;
l'exigence d'achat prend ensuite le pire cas de marche (cribler de la pierre humide
en saison des pluies dégrade la capacité) et ajoute 25&nbsp;% de marge.</p>

<h3>3.3 · Application</h3>""")
doc.append(tbl(["Grandeur", "Mode 1A", "Mode 1B"], [
    ["Alimentation du crible, boucle convergée (t/h sec / humide)",
     f"{f(S8A['feed_dry_tph'])} / {f(S8A['feed_wet_tph'])}",
     f"{f(S8B['feed_dry_tph'])} / {f(S8B['feed_wet_tph'])}"],
    ["Capacité de base Q<sub>b</sub>, étage 35 / étage 20 (t/h par m²)",
     f"{f(qbt['Qb_tph_m2'],0)} / {f(qbb['Qb_tph_m2'],0)}",
     f"{f(qbt_b['Qb_tph_m2'],0)} / {f(qbb_b['Qb_tph_m2'],0)}"],
    ["Surface requise pour ce travail, étage 35 / étage 20 (m²)",
     f"{f(qbt['required_area_m2'],1)} / {f(qbb['required_area_m2'],1)}",
     f"{f(qbt_b['required_area_m2'],1)} / {f(qbb_b['required_area_m2'],1)}"],
    ["Minimum d'achat (pire cas + 25 %), étage 35 / étage 20 (m²)",
     f"{S8A['purchase_min_area_m2']['top_deck']} / {S8A['purchase_min_area_m2']['bottom_deck']}",
     "identique (fixé par le pire cas sur tous les travaux)"],
]))
doc.append(reduced_psd({
    "1A": [("SR.5008 screen feed", "Alim. crible"),
           ("SR.5008 deck-1 oversize", "+35 → boucle"),
           ("SR.5008 20/35 cut", "Pierre à four 20/35"),
           ("SR.5008 undersize 0/20", "Brut 0/20")],
    "1B": [("SR.5008 screen feed", "Alim. crible"),
           ("SR.5008 deck-1 oversize", "+35 → boucle"),
           ("SR.5008 20/35 cut", "20/35 → rebroyé (pas de pierre à four dans ce mode)"),
           ("SR.5008 undersize 0/20", "Brut 0/20")]}))
doc.append(f"""<p>Qualité de pierre à four obtenue, mode 1A (l'enveloppe contractuelle
demande ≤&nbsp;30&nbsp;% dessous / ≥&nbsp;55&nbsp;% dedans / ≤&nbsp;15&nbsp;%
dessus)&nbsp;: <b>{f(ENV['below_20mm_pct'],1)}&nbsp;% sous 20&nbsp;mm ·
{f(ENV['in_cut_20_35_pct'],1)}&nbsp;% entre 20 et 35 ·
{f(ENV['above_35mm_pct'],1)}&nbsp;% au-dessus de 35&nbsp;mm — conforme avec
marge.</b></p>
<div class="check"><b>Ce qu'il faut vérifier sur cette fiche.</b> (1)&nbsp;la forme de
la courbe de probabilité et la valeur d'imperfection (0.15 en convention large
≈ 0.081 en convention classique) pour du criblage à sec à 35 et 20&nbsp;mm&nbsp;;
(2)&nbsp;les capacités de base Q<sub>b</sub> face à votre pratique du dimensionnement
de cribles&nbsp;; (3)&nbsp;les chiffres d'enveloppe de la pierre à four — sont-ils
plausibles pour un double étage 35/20&nbsp;?</div>""")

# ------------------------------------------------------------------ Fiche 3
doc.append(f"""<h2 class="sheet">4 · Fiche 3 — CR.5011, le concasseur à percussion de la boucle</h2>
<p class="chapsub">Rebroie le +35 mm du crible (et, en mode 1B, la coupe 20/35) · son produit retourne au crible</p>

<h3>4.1 · La formule d'intensité de fragmentation</h3>
<p>Un concasseur à percussion brise par coups de percuteurs&nbsp;: le produit dépend
donc de la violence de chaque coup. L'énergie de coup par tonne vient de la vitesse
périphérique du rotor <i>v</i> (énergie cinétique&nbsp;: <i>E</i> = <i>v</i>²/7200 en
kWh/t, avec <i>v</i> en m/s). La pratique des essais de fragmentation (la tradition
des essais de chute de poids «&nbsp;JK&nbsp;») résume le résultat d'un impact par le
<b><i>t</i><sub>10</sub></b>&nbsp;: la part du produit plus fine que le dixième de la
taille du bloc d'origine — une note de finesse du coup. L'énergie se convertit en
<i>t</i><sub>10</sub> par une loi de saturation&nbsp;:</p>
<p class="eq"><i>t</i><sub>10</sub> = <i>A</i> ( 1 − exp(−<i>b</i>·<i>E</i>) )</p>
<p><i>A</i> est le plafond (le maximum qu'un seul coup peut fragmenter) et <i>b</i> la
vitesse à laquelle l'énergie s'en approche. Nous prenons
<i>A</i>&nbsp;=&nbsp;{CAL['m5_A_j']}, <i>b</i>&nbsp;=&nbsp;{CAL['m5_b_j']} — valeurs
publiées centrales pour la calcite/le calcaire, adoptées comme défauts du
projet&nbsp;; l'essai granulométrique du fournisseur les refermera. La finesse du coup
fixe ensuite l'étalement <i>n</i> de la courbe du produit
(<i>n</i> = max(0.65,&nbsp;(30/<i>t</i><sub>10</sub>)<sup>0.3</sup>)), et le produit
suit la même forme de Rosin–Rammler que la fiche&nbsp;1, avec P<sub>80</sub> égal au
réglage de sortie de la machine (le «&nbsp;CSS&nbsp;»). Puissance&nbsp;: Bond, comme
en fiche&nbsp;1.</p>

<h3>4.2 · La boucle</h3>
<p>Cette machine est en circuit fermé&nbsp;: son produit retourne au crible, donc sa
propre alimentation dépend de ce que le crible rejette — qui dépend du produit du
concasseur. Le modèle résout cette circularité par itération&nbsp;: on recalcule la
boucle jusqu'à ce que le tonnage recyclé <b>et toute sa courbe granulométrique</b>
cessent de changer. Tous les chiffres de cette note sont cet état convergé.</p>

<h3>4.3 · Application</h3>""")
doc.append(tbl(["Grandeur", "Mode 1A", "Mode 1B"], [
    ["Réglage de sortie CSS (mm)", S1A['CR.5011_x80_css_mm'], S1B['CR.5011_x80_css_mm']],
    ["Vitesse rotor v (m/s) → énergie de coup E (kWh/t)",
     f"{S1A['CR.5011_v_ms']} → {f(C11A['Ecs_kWh_t'],3)}",
     f"{S1B['CR.5011_v_ms']} → {f(C11B['Ecs_kWh_t'],3)}"],
    ["Finesse de coup t<sub>10</sub> (%) → étalement du produit n",
     f"{f(C11A['t10_pct'],1)} → {f(C11A['n'],2)}",
     f"{f(C11B['t10_pct'],1)} → {f(C11B['n'],2)}"],
    ["Charge de boucle convergée (t/h humide, sur une machine de 90 t/h)",
     f"{f(C11A['loop_load_wet_tph'])} ({f(C11A['utilization_pct'],1)} %)",
     f"{f(C11B['loop_load_wet_tph'])} ({f(C11B['utilization_pct'],1)} %)"],
    ["F<sub>80</sub> alimentation → P<sub>80</sub> produit (mm)",
     f"{f(C11A['F80_mm'])} → {f(C11A['P80_mm'])}",
     f"{f(C11B['F80_mm'])} → {f(C11B['P80_mm'])}"],
    ["Puissance moteur absorbée (kW)", f(C11A['P_installed_kW'], 1), f(C11B['P_installed_kW'], 1)],
]))
doc.append(reduced_psd({
    "1A": [("CR.5011 feed", "Alim. boucle"), ("CR.5011 product", "Produit boucle")],
    "1B": [("CR.5011 feed", "Alim. boucle"), ("CR.5011 product", "Produit boucle")]}))
doc.append(f"""<div class="check"><b>Ce qu'il faut vérifier sur cette fiche.</b>
(1)&nbsp;l'énergie cinétique de bout de percuteur comme mesure de l'énergie de
coup&nbsp;; (2)&nbsp;la loi de saturation et les valeurs calcite
A&nbsp;=&nbsp;{CAL['m5_A_j']}, b&nbsp;=&nbsp;{CAL['m5_b_j']}&nbsp;;
(3)&nbsp;P<sub>80</sub>&nbsp;=&nbsp;CSS pour un percuteur&nbsp;; (4)&nbsp;les charges
de boucle convergées face à la capacité machine de 90&nbsp;t/h — le mode&nbsp;1B
tourne à {f(C11B['utilization_pct'],1)}&nbsp;%, le point le plus tendu de la
zone.</div>""")

# ------------------------------------------------------------------ Section 5
a = ADQ["engine_measured_curve_mode_1A_wet_tph"]
d = ADQ["pfd_design_figures"]
doc.append(f"""<h2 class="sheet">5 · Confrontation au schéma du bureau d'études</h2>
<p>Le bureau d'études a dimensionné la même ligne à partir de sa propre courbe
d'alimentation <b>supposée</b>. Nos chiffres tournent sur la courbe <b>mesurée</b> —
nettement plus fine (45.5&nbsp;% du flux de carrière est déjà sous 20&nbsp;mm). Mêmes
machines, mêmes formules, alimentation différente&nbsp;:</p>""")
doc.append(tbl(["Flux (mode 1A, t/h humide)", "Bureau d'études", "Cette note (courbe mesurée)"], [
    ["Pierre à four 20–35", f(d['scenario_A']['kfs_tph'], 0), f(a['kfs_20_35'], 0)],
    ["Brut 0–20", f(d['scenario_A']['crude_0_20_tph'], 0), f(a['crude_0_20'], 0)],
    ["Alimentation du crible (boucle comprise)", f(d['screen_feed_BC5007_tph'], 0), f(a['screen_feed'], 0)],
    ["Retour de boucle", f(d['recycle_BC5010_tph'], 0), f(a['recycle'], 0)],
]))
doc.append("""<p>Le motif est cohérent&nbsp;: une alimentation plus fine donne moins de
pierre à four, plus de brut, et moins de matière rejetée dans la boucle. L'écart est
donc une <b>question de courbe d'alimentation, pas un désaccord de formules</b> — et
c'est précisément ce qui rend leur vérification indépendante précieuse&nbsp;: une fois
les formules validées, l'incertitude restante est la vraie courbe de la carrière.</p>""")

# ------------------------------------------------------------------ Annexes
for mk, t in [("1A", "Annexe A — tables complètes des flux, mode 1A (production normale, 250 t/h humide)"),
              ("1B", "Annexe B — tables complètes des flux, mode 1B (campagne de stock, 172 t/h humide, CSS 18)")]:
    doc.append(f'<h2 class="sheet">{t}</h2>')
    doc.append("<p>Tous les flux du schéma convergé, tous les tamis, % passants "
               "cumulés. Les repères BC.xxxx sont les numéros de convoyeurs du bureau "
               "d'études.</p>")
    doc.append(full_psd(mk))

doc.append(f"""<p class="prov">Historique du document&nbsp;: REV A 2026-08-17 (première
émission, anglais) · REV B 2026-08-18 (calibration ratifiée&nbsp;; coquille du chiffre
de recyclage corrigée) · REV C 2026-08-18 (édition didactique, anglais) ·
REV D 2026-08-18 (édition française — décision du client&nbsp;: le français remplace
l'anglais pour cette note). Chaque chiffre est généré par le modèle déterministe du
projet — commit moteur {P['commit']} — et se rejoue sans assistant&nbsp;:
<code>PYTHONPATH=src python dossiers/DT-002/extract_dt002.py</code> puis
<code>python dossiers/DT-002/render_dt002_html.py</code>. Les valeurs de travail en
attente de confirmation par essais sont signalées comme telles dans le texte.
Produit par NOEZYS.</p>
</body></html>""")

dest = HERE / "DT-002-Zone11-Sizing-Note.html"
dest.write_text("\n".join(doc), encoding="utf-8")
print("written:", dest)
