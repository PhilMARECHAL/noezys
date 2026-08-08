# Wankoe Python Model

Projet **Wankoe Python Model** — modèle Python développé dans le cadre des projets Noezys.

## Structure du projet

```
wankoe-python-model/
├── README.md               # Ce fichier
├── pyproject.toml          # Configuration du projet et dépendances
├── .gitignore              # Fichiers ignorés par git
├── src/
│   └── wankoe_model/
│       ├── __init__.py     # Point d'entrée du package
│       └── model.py        # Modèle principal
└── tests/
    └── test_model.py       # Tests unitaires
```

## Installation

```bash
cd wankoe-python-model
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
pip install -e ".[dev]"
```

## Utilisation

```python
from wankoe_model import WankoeModel

model = WankoeModel()
result = model.predict([1.0, 2.0, 3.0])
print(result)
```

## Tests

```bash
pytest
```

## Licence

© Noezys — Tous droits réservés.
