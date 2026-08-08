# Wankoe Python Model

Modèle de calcul **statique déterministe** de la ligne de traitement calcaire
WANKOE (zones 1.1 / 1.2 / 1.3). Pour un jeu de paramètres (un « scénario »),
il calcule la « photo » synchronisée de toute la ligne : flux, granulométries,
bilans masse et eau, puissances, écarts aux objectifs.

Spécification : `docs/WANKOE-cahier-des-charges-modele-v2026-08-08.docx`
(9 chapitres, modèles M1–M8, fiches machines, flowsheet, cas de référence).

## Principes (règles d'or du cahier des charges)

1. **Données séparées du code** : tout paramètre vit dans `data/*.json` et se
   modifie sans reprogrammation (vérifié par `tests/test_parametrage.py`).
2. Chaque symbole de formule est défini (nom, unité) — voir les docstrings de
   `src/wankoe_model/models.py` et la section `calibration` des données.
3. **Bouclage masse + eau automatique** à chaque scénario (tolérance
   paramétrable), reproduction du cas de référence du chapitre 9, tests livrés.

## Structure

```
wankoe-python-model/
├── data/
│   ├── parametres_defaut.json        # TOUS les paramètres (machines, calibration, produits…)
│   └── courbe_entree_reference.json  # courbe d'entrée CALIBRÉE (hypothèse, → à remplacer par mesure)
├── docs/                             # cahier des charges + classeur de données (originaux)
├── scripts/
│   └── calibrer_courbe_reference.py  # calage de la courbe pivot sur le chapitre 9
├── src/wankoe_model/
│   ├── grid.py                       # grille de mailles, courbes PSD (% passant cumulé)
│   ├── models.py                     # modèles communs M1–M8 (fonctions pures)
│   ├── flowsheet.py                  # zones 1.1/1.2/1.3, boucles fermées, codes machines
│   └── scenario.py                   # chargement paramètres + run_scenario (fonction pure)
└── tests/                            # 31 tests : unités M1–M8, cas de référence, paramétrage
```

## Utilisation

```python
from wankoe_model import charger_parametres, run_scenario

# scénario par défaut (cas de référence chapitre 9)
resultats = run_scenario(charger_parametres())
print(resultats["produits"]["KFS"]["t_h"])      # 59,1 t/h humide
print(resultats["bilans"])                       # bouclage masse + eau
print(resultats["alertes"])                      # goulots, non-conformités, hypothèses

# scénario modifié — AUCUNE modification de code
params = charger_parametres(overrides={
    "machines": {"SR.5007": {"parametres": {"a1": {"defaut": 30}}}},
    "scenario_defaut": {"meteo": "pluie", "debits_th": {"alimentation_zone_1_1": 200}},
})
resultats = run_scenario(params)
```

`run_scenario` est une **fonction pure** (paramètres → résultats, sans état) :
elle est directement utilisable pour des balayages massifs de paramètres et
des recherches d'optimum (phase ultérieure du projet).

## Tests

```bash
pip install -e ".[dev]"
pytest
```

## État de la validation (cas de référence, chapitre 9)

| Grandeur | Attendu | Obtenu | Écart |
|---|---|---|---|
| 9.1 KFS | 59,3 t/h (23,7 %) | 59,1 t/h (23,6 %) | ✅ |
| 9.1 Passant 0/20 | 190,7 t/h | 190,9 t/h | ✅ |
| 9.1 Puissance CR.5009 | ≈ 116 kW | 106 kW | −9 % (documenté) |
| 9.1 Puissance CR.5011 | ≈ 37 kW | 18 kW | ⚠️ écart structurel, signalé |
| 9.2 AgLime | 55,0 t/h | 55,0 t/h | ✅ |
| 9.3 Vapeur | ≈ 2,3 t/h | 2,26 t/h | ✅ |
| 9.3 Grits | 10,1 t/h | 10,1 t/h | ✅ (H-M7 calées) |
| 9.3 UltraFin | ≈ 1,3 t/h | 1,23 t/h | ✅ |
| 9.3 Puissance ML.26 | ≈ 45 kW | 51 kW | +13 % |
| 9.3 Brûleur DY.03 | ≈ 3,8 MW | 3,83 MW | ✅ |

## Hypothèses ouvertes (marquées [H] dans les données)

- **Courbe d'entrée** : calibrée sur le chapitre 9 (aucune mesure réelle) —
  à remplacer par la première coupe de bande.
- **M7 / ML.26** : rôle exact de `comp_lam` non spécifié → hypothèse H-M7-1
  (taux de réduction maximal par passe) ; distribution des fines d'attrition
  → hypothèse H-M7-2. Paramètres calés sur le cas 9.3, à confirmer par essai.
- **Φ(<100 µm)** : non mesuré → UltraFin marqué « NON CERTIFIÉ ».
- **CR.5011** : puissance de référence (37 kW) non reproduite (18 kW) — la
  charge circulante calculée (~36 t/h) est plus faible que celle qu'implique
  le cahier des charges (~94–125 t/h). Point signalé pour arbitrage.

© Noezys — Tous droits réservés.
