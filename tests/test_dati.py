# tests/test_dati.py
"""Le prove sul dato. Non provano il codice: provano i fatti su cui si regge la giornata."""

from __future__ import annotations

from pathlib import Path

import pytest

from campagne.caricamento import SOMMA_ATTESA, carica, colonne_per_tipo, somma_di_controllo
from campagne.referto import blocchi_di_mese, effetto_di_buttare_i_mancanti, mancanti_travestiti, sentinelle

PERCORSO = Path("dati") / "bank-additional-full.csv"


def test_il_file_e_quello_del_corso() -> None:
    assert somma_di_controllo(PERCORSO) == SOMMA_ATTESA


def test_il_file_sbagliato_viene_rifiutato(tmp_path: Path) -> None:
    finto = tmp_path / "bank-additional-full.csv"
    finto.write_text("age;y\n30;no\n", encoding="utf-8")
    with pytest.raises(ValueError, match="non è quello del corso"):
        carica(finto)


def test_la_forma_del_file() -> None:
    dati = carica(PERCORSO)
    assert dati.shape == (41188, 21)
    assert dati["y"].eq("yes").sum() == 4640


def test_le_colonne_testuali_si_riconoscono() -> None:
    numeriche, testuali = colonne_per_tipo(carica(PERCORSO))
    assert "age" in numeriche and "job" in testuali
    assert len(testuali) == 11


def test_unknown_non_e_un_valore_nullo() -> None:
    dati = carica(PERCORSO)
    assert dati.isna().sum().sum() == 0, "pandas non vede nessun nullo: i mancanti sono travestiti"
    assert mancanti_travestiti(dati)["occorrenze"].sum() == 12718


def test_buttare_i_mancanti_sposta_la_quota_di_si() -> None:
    effetto = effetto_di_buttare_i_mancanti(carica(PERCORSO))
    assert effetto["quota_righe_perse"] > 0.25
    assert effetto["quota_si_fra_chi_si_butta"] < effetto["quota_si_fra_chi_resta"]


def test_la_sentinella_sposta_la_media_di_due_ordini_di_grandezza() -> None:
    misure = sentinelle(carica(PERCORSO))
    assert misure["media_con_la_sentinella"] > 900
    assert misure["media_senza"] < 10


def test_l_ordine_delle_righe_e_cronologico() -> None:
    """I mesi non si mescolano: se lo facessero, da domani non potremmo dividere per tempo."""
    blocchi = blocchi_di_mese(carica(PERCORSO))
    assert len(blocchi) == 26
    assert blocchi[0][0] == "may"

from campagne.referto import profila_colonne

def test_profilo_copre_tutte_le_21_colonne() -> None:
    dati = carica(PERCORSO)
    profilo = profila_colonne(dati)
    assert len(profilo) == 21, "Il profilo deve coprire tutte le colonne del dataset"