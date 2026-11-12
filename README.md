# Banca Campagne — Progetto di Machine Learning

# Come avviare il referto
Il referto viene generato ed estratto dinamicamente dai dati tramite il comando:

uv run python -m campagne.referto


# Come La strada scelta
    Scelta: Il profilo completo di tutte le 21 colonne e la classificazione formale delle colonne inutili (distinguendo valori unici, ID travestiti e segnali sbilanciati).

    Le analisi di deriva avanzate e il filtraggio complesso dei sottogruppi anagrafici, per concentrarci sulla pulizia strutturale del dato.
    Tutte e 21 le colonne sono state profilate, permettendo di identificare con precisione la distribuzione e i pesi delle mode al posto delle sole 5 colonne iniziali.

    La misura di partenza e il Delta
        - Prima (Baseline): Il referto analizzava solo 5 colonne predefinite e non classificava l'inutilità strutturale delle variabili.
        - Dopo (Estensione): Profilazione completa di tutte le 21 colonne del dataset bank-additional-full.csv, con calcolo automatico di distinti, mode, pesi percentuali, mediane e quantili, affiancata da una classificazione logica delle colonne prive di potere informativo o fortemente sbilanciate (come default).

# Le decisioni aperte
    Cosa fare delle righe con unknown? Vengono mantenute come categoria a sé stante e non cancellate. Perché: scartarle comporterebbe la perdita di oltre il 25% del campione e modificherebbe la quota di sottoscrizione (i dati mancanti si comportano diversamente dal resto).

    Cosa fare di pdays? Viene lasciata intatta nel referto ma analizzata separatamente escludendo la sentinella 999. Perché: distingue chiaramente chi non è mai stato contattato da chi lo è stato di recente, preservando l'informazione binaria e temporale.

# Revisione del codice scritto con l'AI
    dropna() e fillna() automatici: Rimossi o evitati in quanto Pandas non rileva celle nulle (i mancanti sono stringhe come "unknown").

    Metriche errate su codici: Fatto attenzione a non applicare .mean() o somme su colonne come pdays con valori sentinella.

    Controllo dtype == object: Evitato l'uso diretto per la compatibilità con le versioni recenti di Pandas, preferendo funzioni di tipo robuste (is_numeric_dtype).

    Scalabilità e robustezza: Il caricamento in memoria gestisce agilmente i dati attuali, ma richiederebbe chunking in caso di volumi nell'ordine di milioni di righe.

    Rilievo non corretto: Non abbiamo implementato un controllo dinamico dei tipi basato su schema esterno rigido (es. Pydantic) per la lettura del CSV, affidandoci alla validazione SHA-256 e ai tipi inferiti da Pandas. Ragione: Per l'analisi esplorativa iniziale e i volumi del dataset corrente, la verifica di controllo rigida del file è sufficiente e mantiene il codice leggero.

# Prova del collega
    Tempo impiegato: 3 minuti.

    Primo punto di blocco: Nessuno, l'ambiente virtuale gestito con uv e i comandi lineari hanno reso l'avvio immediato.