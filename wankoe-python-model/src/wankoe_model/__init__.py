"""Wankoe Python Model — modèle de calcul de la ligne de traitement calcaire.

Flowsheet statique déterministe des zones 1.1 / 1.2 / 1.3 : chaque exécution
de ``run_scenario`` calcule la « photo » synchronisée de la ligne pour un jeu
de paramètres. Les données vivent dans data/parametres_defaut.json, séparées
du code.
"""

from wankoe_model.grid import PSD, grille_moteur
from wankoe_model.scenario import charger_parametres, run_scenario, CHEMIN_PARAMETRES_DEFAUT

__all__ = [
    "PSD",
    "grille_moteur",
    "charger_parametres",
    "run_scenario",
    "CHEMIN_PARAMETRES_DEFAUT",
]
__version__ = "0.2.0"
