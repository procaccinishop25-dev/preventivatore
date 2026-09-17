"""Elementi grafici SVG riutilizzabili per il motore di disegno tecnico.
Ogni funzione restituisce una stringa SVG pronta da concatenare — nessuna
funzione qui fa calcoli geometrici, solo disegno."""

# --- Palette centralizzata: unico punto da modificare per cambiare i colori ---
PALETTE = {
    "telaio": "#20241F",         # struttura fissa, scuro
    "anta": "#8A9089",           # struttura mobile, grigio medio
    "battuta": "#C7CBC5",        # linea sottile di battuta, tono neutro discreto
    "fermavetro": "#AEB4A9",     # fascia fermavetro, variante più chiara del colore anta
    "vetro_fill": "#D7EAF5",     # vetro, azzurro chiaro
    "vetro_stroke": "#A9CDE0",
    "quota": "#6B7570",
    "maniglia": "#494D49",       # ferramenta, grigio scuro neutro, distinto dal colore anta
    "sfondo": "#FFFFFF",
}

SPESSORE_PROFILO_STROKE = 1      # bordo sottile sulle fasce piene di telaio/anta/fermavetro
SPESSORE_BATTUTA_STROKE = 1      # spessore della linea sottile di battuta
SPESSORE_VETRO_STROKE = 1
SPESSORE_QUOTA = 1.2
SPESSORE_SIMBOLO_APERTURA = 1.4

LUNGHEZZA_TACCA_MM = 16

# --- Maniglia tecnica: piastra + collo/perno + impugnatura verticale, dimensioni in mm ---
HANDLE_PLATE_WIDTH_MM = 22
HANDLE_PLATE_HEIGHT_MM = 110
HANDLE_PLATE_RADIUS_MM = 5
HANDLE_NECK_LENGTH_MM = 16
HANDLE_NECK_WIDTH_MM = 10
HANDLE_GRIP_LENGTH_MM = 80
HANDLE_GRIP_WIDTH_MM = 13
HANDLE_GRIP_RADIUS_MM = 6.5
HANDLE_PIVOT_RADIUS_MM = 7


def rettangolo(x, y, larghezza, altezza, stroke, stroke_width, fill="none"):
    return (
        f'<rect x="{x}" y="{y}" width="{larghezza}" height="{altezza}" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}" />'
    )


def rettangolo_arrotondato(x, y, larghezza, altezza, raggio, stroke, stroke_width, fill="none"):
    """Come rettangolo(), ma con angoli arrotondati — usato per elementi che
    devono leggersi come componenti fisici (es. maniglia) invece che come
    profili tecnici a spigolo vivo."""
    return (
        f'<rect x="{x}" y="{y}" width="{larghezza}" height="{altezza}" rx="{raggio}" ry="{raggio}" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}" />'
    )


def cerchio(cx, cy, raggio, stroke, stroke_width, fill="none"):
    return f'<circle cx="{cx}" cy="{cy}" r="{raggio}" fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}" />'


def linea(x1, y1, x2, y2, stroke, stroke_width, tratteggiata=False):
    dash = ' stroke-dasharray="7,6"' if tratteggiata else ""
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" stroke-width="{stroke_width}"{dash} />'


def testo(x, y, contenuto, dimensione=28, ancoraggio="middle", rotazione=0, colore=None):
    colore = colore or PALETTE["quota"]
    trasformazione = f' transform="rotate({rotazione} {x} {y})"' if rotazione else ""
    return (
        f'<text x="{x}" y="{y}" font-size="{dimensione}" fill="{colore}" '
        f'text-anchor="{ancoraggio}" font-family="Inter, sans-serif"{trasformazione}>{contenuto}</text>'
    )


def fascia_profilo(rettangolo_esterno, rettangolo_interno, colore):
    """Disegna un profilo (telaio, anta o fermavetro) come vera fascia piena:
    rettangolo esterno colorato + rettangolo interno 'svuotato' in bianco sopra —
    rappresentazione standard dello spessore di un profilo in vista frontale tecnica."""
    svg = rettangolo(
        rettangolo_esterno["x"], rettangolo_esterno["y"],
        rettangolo_esterno["larghezza"], rettangolo_esterno["altezza"],
        colore, SPESSORE_PROFILO_STROKE, fill=colore
    )
    svg += rettangolo(
        rettangolo_interno["x"], rettangolo_interno["y"],
        rettangolo_interno["larghezza"], rettangolo_interno["altezza"],
        colore, SPESSORE_PROFILO_STROKE, fill=PALETTE["sfondo"]
    )
    return svg


def linea_battuta(rettangolo_battuta):
    """Disegna la zona di battuta come sottile contorno (nessun riempimento) —
    si legge come una linea di giunzione/fessura, distinta dalle fasce piene
    di anta e fermavetro che la circondano."""
    return rettangolo(
        rettangolo_battuta["x"], rettangolo_battuta["y"],
        rettangolo_battuta["larghezza"], rettangolo_battuta["altezza"],
        PALETTE["battuta"], SPESSORE_BATTUTA_STROKE, fill="none"
    )


def _tacca_45(x, y, verso_x=1, verso_y=-1):
    """Piccola tacca inclinata a 45° centrata su (x, y) — convenzione tecnica
    per l'estremità di una linea di quota, al posto di un trattino perpendicolare."""
    meta = LUNGHEZZA_TACCA_MM / 2 * 0.7071
    return linea(
        x - meta * verso_x, y - meta * verso_y,
        x + meta * verso_x, y + meta * verso_y,
        PALETTE["quota"], SPESSORE_QUOTA
    )


def quota_orizzontale(x_inizio, x_fine, y_quota, y_oggetto, etichetta):
    """Linea di quota orizzontale, separata dal disegno, con tacche a 45° e testo centrato."""
    svg = ""
    svg += linea(x_inizio, y_oggetto, x_inizio, y_quota, PALETTE["quota"], SPESSORE_QUOTA)
    svg += linea(x_fine, y_oggetto, x_fine, y_quota, PALETTE["quota"], SPESSORE_QUOTA)
    svg += linea(x_inizio, y_quota, x_fine, y_quota, PALETTE["quota"], SPESSORE_QUOTA)
    svg += _tacca_45(x_inizio, y_quota)
    svg += _tacca_45(x_fine, y_quota)
    x_centro = (x_inizio + x_fine) / 2
    larghezza_etichetta = 8 * len(etichetta) + 16
    svg += rettangolo(x_centro - larghezza_etichetta / 2, y_quota - 20, larghezza_etichetta, 30, "none", 0, fill=PALETTE["sfondo"])
    svg += testo(x_centro, y_quota + 3, etichetta)
    return svg


def quota_verticale(y_inizio, y_fine, x_quota, x_oggetto, etichetta):
    """Linea di quota verticale, separata dal disegno, con tacche a 45° e testo ruotato centrato."""
    svg = ""
    svg += linea(x_oggetto, y_inizio, x_quota, y_inizio, PALETTE["quota"], SPESSORE_QUOTA)
    svg += linea(x_oggetto, y_fine, x_quota, y_fine, PALETTE["quota"], SPESSORE_QUOTA)
    svg += linea(x_quota, y_inizio, x_quota, y_fine, PALETTE["quota"], SPESSORE_QUOTA)
    svg += _tacca_45(x_quota, y_inizio)
    svg += _tacca_45(x_quota, y_fine)
    y_centro = (y_inizio + y_fine) / 2
    larghezza_etichetta = 8 * len(etichetta) + 16
    svg += rettangolo(x_quota - 15, y_centro - larghezza_etichetta / 2, 30, larghezza_etichetta, "none", 0, fill=PALETTE["sfondo"])
    svg += testo(x_quota, y_centro, etichetta, rotazione=-90)
    return svg


def simbolo_apertura(rettangolo_riferimento, configurazione_anta):
    """Simbolo tecnico di apertura, letto da una configurazione per singola anta:
    {"tipo": "fissa"} oppure {"tipo": "apribile", "apertura": "sinistra"/"destra"}.
    Linee sottili tratteggiate convergenti verso il lato della cerniera — solo
    indicativo, non una linea costruttiva reale. Nessun simbolo se tipo è "fissa"."""
    if configurazione_anta.get("tipo") != "apribile":
        return ""

    direzione = configurazione_anta.get("apertura", "destra")

    x, y = rettangolo_riferimento["x"], rettangolo_riferimento["y"]
    larghezza, altezza = rettangolo_riferimento["larghezza"], rettangolo_riferimento["altezza"]

    if direzione == "destra":
        apice = (x + larghezza, y + altezza / 2)
        angolo1 = (x, y)
        angolo2 = (x, y + altezza)
    else:  # sinistra
        apice = (x, y + altezza / 2)
        angolo1 = (x + larghezza, y)
        angolo2 = (x + larghezza, y + altezza)

    svg = ""
    svg += linea(angolo1[0], angolo1[1], apice[0], apice[1], PALETTE["anta"], SPESSORE_SIMBOLO_APERTURA, tratteggiata=True)
    svg += linea(angolo2[0], angolo2[1], apice[0], apice[1], PALETTE["anta"], SPESSORE_SIMBOLO_APERTURA, tratteggiata=True)
    return svg


def disegna_maniglia(anta, apertura):
    """Disegna una maniglia tecnica realistica — piastra verticale, collo/perno,
    impugnatura verticale con estremità arrotondate — sul bordo dell'anta
    indicato da `apertura`. Tutte le coordinate derivano dal rettangolo `anta`
    (x, y, larghezza, altezza) e dalla direzione di apertura — nessuna
    coordinata assoluta hardcoded — quindi resta corretta al variare di
    larghezza, altezza, numero di ante e apertura. Nessuna maniglia se
    `apertura` non è "sinistra"/"destra" (es. ante fisse, per cui il chiamante
    comunque non dovrebbe invocarla). Stessa firma pubblica di prima."""
    if apertura not in ("sinistra", "destra"):
        return ""

    y_centro = anta["y"] + anta["altezza"] / 2
    colore = PALETTE["maniglia"]

    if apertura == "sinistra":
        x_bordo = anta["x"]
        verso_interno = 1   # l'interno dell'anta è verso destra
    else:  # destra
        x_bordo = anta["x"] + anta["larghezza"]
        verso_interno = -1  # l'interno dell'anta è verso sinistra

    # 1. Piastra: rettangolo verticale arrotondato, appoggiata sul bordo dell'anta
    if verso_interno == 1:
        piastra_x = x_bordo
    else:
        piastra_x = x_bordo - HANDLE_PLATE_WIDTH_MM
    piastra_y = y_centro - HANDLE_PLATE_HEIGHT_MM / 2

    svg = rettangolo_arrotondato(
        piastra_x, piastra_y, HANDLE_PLATE_WIDTH_MM, HANDLE_PLATE_HEIGHT_MM,
        HANDLE_PLATE_RADIUS_MM, colore, SPESSORE_PROFILO_STROKE, fill=colore
    )

    # 2. Collo: piccolo profilo che protrude dalla piastra verso l'interno dell'anta
    if verso_interno == 1:
        collo_x = piastra_x + HANDLE_PLATE_WIDTH_MM
    else:
        collo_x = piastra_x - HANDLE_NECK_LENGTH_MM
    collo_y = y_centro - HANDLE_NECK_WIDTH_MM / 2

    svg += rettangolo(
        collo_x, collo_y, HANDLE_NECK_LENGTH_MM, HANDLE_NECK_WIDTH_MM,
        colore, SPESSORE_PROFILO_STROKE, fill=colore
    )

    # 3. Impugnatura: leva verticale sottile con estremità arrotondate, centrata sul perno
    perno_x = collo_x + HANDLE_NECK_LENGTH_MM if verso_interno == 1 else collo_x
    impugnatura_x = perno_x - HANDLE_GRIP_WIDTH_MM / 2
    impugnatura_y = y_centro - HANDLE_GRIP_LENGTH_MM / 2
    svg += rettangolo_arrotondato(
        impugnatura_x, impugnatura_y, HANDLE_GRIP_WIDTH_MM, HANDLE_GRIP_LENGTH_MM,
        HANDLE_GRIP_RADIUS_MM, colore, SPESSORE_PROFILO_STROKE, fill=colore
    )

    # 4. Perno: disegnato per ultimo, sopra l'impugnatura, per restare visibile
    # come piccolo dettaglio della vite invece di finire coperto dalla leva.
    svg += cerchio(perno_x, y_centro, HANDLE_PIVOT_RADIUS_MM * 0.6, colore, SPESSORE_PROFILO_STROKE, fill=PALETTE["sfondo"])

    return svg
