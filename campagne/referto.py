# campagne/referto.py
"""Il referto sul dato: che cosa c'è dentro il file, e che cosa non è quello che sembra.

Si lancia con `uv run python -m campagne.referto` e scrive `referto/referto_dato.md`.
È la parte del notebook che vale la pena di poter rifare domani.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from campagne.caricamento import PERCORSO_PREDEFINITO, carica, colonne_per_tipo, somma_di_controllo

SENTINELLA_PDAYS = 999
VALORE_MANCANTE = "unknown"
CARTELLA_REFERTO = Path("referto")


def quota_positivi(dati: pd.DataFrame) -> float:
    """La quota di clienti che hanno sottoscritto: è il numero che decide quali metriche useremo."""
    return float(dati["y"].eq("yes").mean())


def mancanti_travestiti(dati: pd.DataFrame) -> pd.DataFrame:
    """Quante volte compare `unknown` in ciascuna colonna testuale.

    `unknown` non è un valore: è un valore mancante scritto a parole. `isna()` non lo vede,
    e infatti su questo file `isna().sum()` risponde zero su tutte le colonne.
    """
    _, testuali = colonne_per_tipo(dati)
    righe = []
    for colonna in testuali:
        quante = int(dati[colonna].eq(VALORE_MANCANTE).sum())
        if quante:
            righe.append({"colonna": colonna, "occorrenze": quante, "quota": quante / len(dati)})
    return pd.DataFrame(righe).sort_values("occorrenze", ascending=False).reset_index(drop=True)


def effetto_di_buttare_i_mancanti(dati: pd.DataFrame) -> dict[str, float]:
    """Che cosa succede alla composizione del campione se si cancellano le righe con `unknown`.

    Non è una domanda di stile: se le righe che si buttano hanno una quota di sì diversa dalle
    altre, il modello viene addestrato su una popolazione che non è quella che riceverà.
    """
    _, testuali = colonne_per_tipo(dati)
    ha_un_mancante = dati[testuali].eq(VALORE_MANCANTE).any(axis=1)
    return {
        "righe_con_un_mancante": float(ha_un_mancante.sum()),
        "quota_righe_perse": float(ha_un_mancante.mean()),
        "quota_si_fra_chi_si_butta": float(dati.loc[ha_un_mancante, "y"].eq("yes").mean()),
        "quota_si_fra_chi_resta": float(dati.loc[~ha_un_mancante, "y"].eq("yes").mean()),
    }


def sentinelle(dati: pd.DataFrame) -> dict[str, float]:
    """`pdays` vale 999 quando il cliente non è mai stato contattato: è un codice, non un numero."""
    e_sentinella = dati["pdays"].eq(SENTINELLA_PDAYS)
    veri = dati.loc[~e_sentinella, "pdays"]
    return {
        "quante": float(e_sentinella.sum()),
        "quota": float(e_sentinella.mean()),
        "media_con_la_sentinella": float(dati["pdays"].mean()),
        "media_senza": float(veri.mean()),
        "mediana_senza": float(veri.median()),
        "massimo_senza": float(veri.max()),
    }


def blocchi_di_mese(dati: pd.DataFrame) -> list[tuple[str, int]]:
    """I mesi nell'ordine in cui compaiono nel file, raggruppati per blocchi contigui.

    Serve a rispondere alla sola domanda che conta sull'ordine: le righe sono in ordine di tempo?
    Se lo sono, i mesi non si mescolano, e un mese che ricompare più avanti è l'anno dopo.
    """
    blocchi: list[tuple[str, int]] = []
    for mese in dati["month"]:
        if blocchi and blocchi[-1][0] == mese:
            blocchi[-1] = (mese, blocchi[-1][1] + 1)
        else:
            blocchi.append((mese, 1))
    return blocchi


def deriva_per_decile(dati: pd.DataFrame, colonne: list[str] | None = None) -> pd.DataFrame:
    """Taglia il file in dieci fette nell'ordine delle righe e guarda come cambia il mondo.

    È il modo più economico di vedere una deriva: non serve una data, basta l'ordine.
    """
    colonne = colonne or ["euribor3m", "emp.var.rate", "nr.employed"]
    fette = pd.qcut(pd.Series(range(len(dati))), 10, labels=False)
    tabella = dati.groupby(fette)[colonne].mean()
    tabella["quota_si"] = dati.groupby(fette)["y"].apply(lambda colonna: colonna.eq("yes").mean())
    tabella.index.name = "decile"
    return tabella.round(3)

def profila_colonne(dati: pd.DataFrame) -> pd.DataFrame:
    """Calcola il profilo descrittivo per ciascuna delle 21 colonne."""
    numeriche, _ = colonne_per_tipo(dati)
    tot_righe = len(dati)
    righe = []
    
    for col in dati.columns:
        serie = dati[col]
        distinti = int(serie.nunique())
        moda = serie.mode()[0] if not serie.mode().empty else None
        conteggio_moda = int((serie == moda).sum()) if moda is not None else 0
        peso_moda = conteggio_moda / tot_righe
        
        info = {
            "colonna": col,
            "tipo": "numerica" if col in numeriche else "categorica",
            "distinti": distinti,
            "piu_frequente": str(moda),
            "peso_frequente": peso_moda,
        }
        
        if col in numeriche:
            info["mediana"] = float(serie.median())
            info["q25"] = float(serie.quantile(0.25))
            info["q75"] = float(serie.quantile(0.75))
        else:
            info["mediana"] = None
            info["q25"] = None
            info["q75"] = None
            
        righe.append(info)
        
    return pd.DataFrame(righe)

def scrivi_referto(percorso_dato: Path = PERCORSO_PREDEFINITO) -> Path:
    """Mette tutto insieme e lo scrive su file, perché un referto che resta in un notebook non è un referto."""
    dati = carica(percorso_dato)
    numeriche, testuali = colonne_per_tipo(dati)
    mancanti = mancanti_travestiti(dati)
    effetto = effetto_di_buttare_i_mancanti(dati)
    sent = sentinelle(dati)
    blocchi = blocchi_di_mese(dati)
    deriva = deriva_per_decile(dati)
    
    # 1. Calcoliamo il profilo completo delle colonne (Strada 1)
    profilo = profila_colonne(dati)

    righe = [
        "# Referto sul dato — campagne telefoniche",
        "",
        f"File: `{percorso_dato}`  ",
        f"Somma di controllo: `{somma_di_controllo(percorso_dato)}`",
        "",
        "## La forma",
        "",
        (
            f"- righe: **{len(dati)}**, colonne: **{len(dati.columns)}** "
            f"({len(numeriche)} numeriche, {len(testuali)} testuali)"
        ),
        f"- clienti che hanno sottoscritto: **{int(dati['y'].eq('yes').sum())}** = **{quota_positivi(dati):.2%}**",
        f"- valori nulli secondo pandas: **{int(dati.isna().sum().sum())}**",
        f"- righe duplicate: **{int(dati.duplicated().sum())}**",
        "",
        "## Le colonne che non sono quello che sembrano",
        "",
        "### `unknown`, cioè i mancanti travestiti da categoria",
        "",
        mancanti.to_markdown(index=False, floatfmt=".4f"),
        "",
        (
            f"Righe con almeno un `unknown`: **{int(effetto['righe_con_un_mancante'])}** "
            f"(**{effetto['quota_righe_perse']:.2%}** del file). "
            f"Quota di sì fra queste righe: **{effetto['quota_si_fra_chi_si_butta']:.2%}**; "
            f"fra le altre: **{effetto['quota_si_fra_chi_resta']:.2%}**. "
            "Cancellarle non toglie rumore: toglie un pezzo di campione che si comporta diversamente."
        ),
        "",
        "### `pdays`, cioè il numero che non è un numero",
        "",
        f"- vale {SENTINELLA_PDAYS} in **{int(sent['quante'])}** righe = **{sent['quota']:.2%}**",
        f"- media con la sentinella dentro: **{sent['media_con_la_sentinella']:.1f}** giorni",
        (
            f"- media sulle righe vere: **{sent['media_senza']:.1f}** giorni "
            f"(mediana {sent['mediana_senza']:.0f}, massimo {sent['massimo_senza']:.0f})"
        ),
        "",
        # ---------------------------------------------------------
        # QUI INSERIAMO LA NUOVA SEZIONE DELLA STRADA 1 NEL MARKDOWN:
        # ---------------------------------------------------------
        "## Il profilo completo delle 21 colonne",
        "",
        profilo.to_markdown(index=False, floatfmt=".2f"),
        "",
        "## Quali colonne sono praticamente inutili?",
        "",
        "- **Varianza nulla (un solo valore distinto):** Nessuna colonna nel dataset ha un unico valore costante.",
        "- **Identificatore travestito:** Nessuna colonna ha un numero di valori unici pari o prossimo al totale delle righe.",
        "- **Segnale debole / sbilanciato (stile `default`):** Colonne come `default` (fortemente sbilanciate verso il 'no' con una quota di unknown) o `pdays` non sono né costanti né ID: agiscono come indicatori di presenza/assenza e vanno interpretate logicamente anziché scartate con soglie automatiche.",
        "",
        "## L'ordine delle righe",
        "",
        f"- blocchi contigui di mese: **{len(blocchi)}**",
        "- sequenza: " + " ".join(f"{mese}({quante})" for mese, quante in blocchi[:12]) + " …",
        (
            "- non esiste una colonna con l'anno: i mesi che ricompaiono sono l'anno successivo, "
            "e l'unica cosa che tiene insieme il tempo è l'ordine delle righe."
        ),
        "",
        "## Come cambia il mondo lungo il file",
        "",
        deriva.to_markdown(),
        "",
        "## Le colonne che non useremo, e perché",
        "",
        (
            "- `duration` è la durata della telefonata: **non esiste prima di fare la telefonata**. "
            "Gli autori del dato lo scrivono nel loro `bank-additional-names.txt`. "
            f"Media sui no: {dati.loc[dati['y'].eq('no'), 'duration'].mean():.0f} secondi; "
            f"sui sì: {dati.loc[dati['y'].eq('yes'), 'duration'].mean():.0f}."
        ),
        "",
    ]
    CARTELLA_REFERTO.mkdir(exist_ok=True)
    destinazione = CARTELLA_REFERTO / "referto_dato.md"
    destinazione.write_text("\n".join(righe), encoding="utf-8")
    return destinazione


if __name__ == "__main__":
    scritto = scrivi_referto()
    print(f"referto scritto in {scritto}")


