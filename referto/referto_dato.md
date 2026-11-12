# Referto sul dato — campagne telefoniche

File: `dati\bank-additional-full.csv`  
Somma di controllo: `74adfc578bf77a7ff4bb1ba4a9f8709d9e3c6907342959c2c8416847e0afb4d8`

## La forma

- righe: **41188**, colonne: **21** (10 numeriche, 11 testuali)
- clienti che hanno sottoscritto: **4640** = **11.27%**
- valori nulli secondo pandas: **0**
- righe duplicate: **12**

## Le colonne che non sono quello che sembrano

### `unknown`, cioè i mancanti travestiti da categoria

| colonna   |   occorrenze |   quota |
|:----------|-------------:|--------:|
| default   |         8597 |  0.2087 |
| education |         1731 |  0.0420 |
| housing   |          990 |  0.0240 |
| loan      |          990 |  0.0240 |
| job       |          330 |  0.0080 |
| marital   |           80 |  0.0019 |

Righe con almeno un `unknown`: **10700** (**25.98%** del file). Quota di sì fra queste righe: **7.30%**; fra le altre: **12.66%**. Cancellarle non toglie rumore: toglie un pezzo di campione che si comporta diversamente.

### `pdays`, cioè il numero che non è un numero

- vale 999 in **39673** righe = **96.32%**
- media con la sentinella dentro: **962.5** giorni
- media sulle righe vere: **6.0** giorni (mediana 6, massimo 27)

## Il profilo completo delle 21 colonne

| colonna        | tipo       |   distinti | piu_frequente     |   peso_frequente |   mediana |     q25 |     q75 |
|:---------------|:-----------|-----------:|:------------------|-----------------:|----------:|--------:|--------:|
| age            | numerica   |         78 | 31                |             0.05 |     38.00 |   32.00 |   47.00 |
| job            | categorica |         12 | admin.            |             0.25 |    nan    |  nan    |  nan    |
| marital        | categorica |          4 | married           |             0.61 |    nan    |  nan    |  nan    |
| education      | categorica |          8 | university.degree |             0.30 |    nan    |  nan    |  nan    |
| default        | categorica |          3 | no                |             0.79 |    nan    |  nan    |  nan    |
| housing        | categorica |          3 | yes               |             0.52 |    nan    |  nan    |  nan    |
| loan           | categorica |          3 | no                |             0.82 |    nan    |  nan    |  nan    |
| contact        | categorica |          2 | cellular          |             0.63 |    nan    |  nan    |  nan    |
| month          | categorica |         10 | may               |             0.33 |    nan    |  nan    |  nan    |
| day_of_week    | categorica |          5 | thu               |             0.21 |    nan    |  nan    |  nan    |
| duration       | numerica   |       1544 | 85                |             0.00 |    180.00 |  102.00 |  319.00 |
| campaign       | numerica   |         42 | 1                 |             0.43 |      2.00 |    1.00 |    3.00 |
| pdays          | numerica   |         27 | 999               |             0.96 |    999.00 |  999.00 |  999.00 |
| previous       | numerica   |          8 | 0                 |             0.86 |      0.00 |    0.00 |    0.00 |
| poutcome       | categorica |          3 | nonexistent       |             0.86 |    nan    |  nan    |  nan    |
| emp.var.rate   | numerica   |         10 | 1.4               |             0.39 |      1.10 |   -1.80 |    1.40 |
| cons.price.idx | numerica   |         26 | 93.994            |             0.19 |     93.75 |   93.08 |   93.99 |
| cons.conf.idx  | numerica   |         26 | -36.4             |             0.19 |    -41.80 |  -42.70 |  -36.40 |
| euribor3m      | numerica   |        316 | 4.857             |             0.07 |      4.86 |    1.34 |    4.96 |
| nr.employed    | numerica   |         11 | 5228.1            |             0.39 |   5191.00 | 5099.10 | 5228.10 |
| y              | categorica |          2 | no                |             0.89 |    nan    |  nan    |  nan    |

## Quali colonne sono praticamente inutili?

- **Varianza nulla (un solo valore distinto):** Nessuna colonna nel dataset ha un unico valore costante.
- **Identificatore travestito:** Nessuna colonna ha un numero di valori unici pari o prossimo al totale delle righe.
- **Segnale debole / sbilanciato (stile `default`):** Colonne come `default` (fortemente sbilanciate verso il 'no' con una quota di unknown) o `pdays` non sono né costanti né ID: agiscono come indicatori di presenza/assenza e vanno interpretate logicamente anziché scartate con soglie automatiche.

## L'ordine delle righe

- blocchi contigui di mese: **26**
- sequenza: may(7763) jun(4374) jul(6685) aug(5175) oct(67) nov(3616) dec(10) mar(282) apr(2458) may(5794) jun(715) jul(178) …
- non esiste una colonna con l'anno: i mesi che ricompaiono sono l'anno successivo, e l'unica cosa che tiene insieme il tempo è l'ordine delle righe.

## Come cambia il mondo lungo il file

|   decile |   euribor3m |   emp.var.rate |   nr.employed |   quota_si |
|---------:|------------:|---------------:|--------------:|-----------:|
|        0 |       4.857 |          1.1   |       5191    |      0.028 |
|        1 |       4.859 |          1.135 |       5195.28 |      0.035 |
|        2 |       4.941 |          1.4   |       5228.1  |      0.042 |
|        3 |       4.961 |          1.4   |       5228.1  |      0.066 |
|        4 |       4.965 |          1.4   |       5228.1  |      0.062 |
|        5 |       4.845 |          1.139 |       5222.48 |      0.055 |
|        6 |       3.37  |         -0.571 |       5168.96 |      0.102 |
|        7 |       1.354 |         -1.8   |       5099.1  |      0.12  |
|        8 |       1.26  |         -2.026 |       5094.4  |      0.157 |
|        9 |       0.802 |         -2.358 |       5014.85 |      0.459 |

## Le colonne che non useremo, e perché

- `duration` è la durata della telefonata: **non esiste prima di fare la telefonata**. Gli autori del dato lo scrivono nel loro `bank-additional-names.txt`. Media sui no: 221 secondi; sui sì: 553.
