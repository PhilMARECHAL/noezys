# Zone 1 machine calculation sheets (client deliverable, 2026-08-12)

Thesis-grade calculation document for external design verification
(3 machines: CR.5009, SR.5007, CR.5011 + zone balance + hypothesis
register + references). English, self-contained for a mining-industry
reviewer with no project knowledge.

- Source: WANKOE-Zone1-Machine-Calculation-Sheets.html (KaTeX math,
  Bitstream Charter). Rebuild:
  chromium --headless --no-sandbox --no-pdf-header-footer \
    --virtual-time-budget=10000 --print-to-pdf=out.pdf <html>
  (KaTeX assets: any katex 0.16.x dist/ next to the html as package/dist/)
- Figures: engine commit 3bdc6dc, verified against run_scenario;
  replay via dossiers/DT-001/extract_dt001.py.
