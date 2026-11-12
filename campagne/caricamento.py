# campagne/caricamento.py
"""Il dato entra da un posto solo, e prima di entrare dice chi è.

Due funzioni e niente altro: una legge il file, l'altra ne calcola la somma di controllo.
Tutto il resto del progetto chiama `carica`, così quando il file cambia cambia un posto solo.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd

# La somma di controllo del file giusto. Sulla pagina di UCI ce ne sono due quasi omonimi:
# bank-full.csv ha 17 colonne e la sentinella -1, bank-additional-full.csv ne ha 21 e la
# sentinella 999. Il nostro è il secondo.
SOMMA_ATTESA = "74adfc578bf77a7ff4bb1ba4a9f8709d9e3c6907342959c2c8416847e0afb4d8"

PERCORSO_PREDEFINITO = Path("dati") / "bank-additional-full.csv"


def somma_di_controllo(percorso: Path) -> str:
    """L'impronta SHA-256 del file, letto a blocchi perché non serve tenerlo tutto in memoria."""
    impronta = hashlib.sha256()
    with percorso.open("rb") as file:
        for blocco in iter(lambda: file.read(1 << 20), b""):
            impronta.update(blocco)
    return impronta.hexdigest()


def carica(percorso: Path = PERCORSO_PREDEFINITO, *, verifica: bool = True) -> pd.DataFrame:
    """Legge il CSV delle campagne e, se glielo chiedi, si rifiuta di leggere il file sbagliato.

    Il separatore è il punto e virgola, non la virgola: aprirlo con il separatore predefinito
    produce un DataFrame da una colonna sola, ed è l'errore che fa perdere il primo quarto d'ora.
    """
    if not percorso.exists():
        raise FileNotFoundError(
            f"Non trovo {percorso}. Scarica bank-additional.zip da UCI e mettilo in dati/ "
            "(le istruzioni sono nella pagina Prima di partire)."
        )
    if verifica:
        trovata = somma_di_controllo(percorso)
        if trovata != SOMMA_ATTESA:
            raise ValueError(
                f"Il file non è quello del corso.\n  attesa:  {SOMMA_ATTESA}\n  trovata: {trovata}\n"
                "Se hai scaricato bank-full.csv invece di bank-additional-full.csv, hai 17 colonne "
                "invece di 21 e metà del materiale non torna."
            )
    return pd.read_csv(percorso, sep=";")


def colonne_per_tipo(dati: pd.DataFrame) -> tuple[list[str], list[str]]:
    """Separa le colonne numeriche da quelle testuali.

    Non si usa `dtype == object`: da pandas 3 le colonne di testo hanno il tipo `str` e quel
    confronto risponde `False` su ogni colonna, in silenzio.
    """
    numeriche = [c for c in dati.columns if pd.api.types.is_numeric_dtype(dati[c])]
    testuali = [c for c in dati.columns if c not in numeriche]
    return numeriche, testuali
