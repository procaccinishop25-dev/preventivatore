"""Elementi grafici SVG riutilizzabili per il motore di disegno tecnico.
Ogni funzione restituisce una stringa SVG pronta da concatenare — nessuna
funzione qui fa calcoli geometrici, solo disegno."""

# --- Palette centralizzata: unico punto da modificare per cambiare i colori ---
PALETTE = {
    "telaio": "#20241F",         # struttura fissa, scuro
    "anta": "#8A9089",           # struttura mobile, grigio medio
    "vetro_fill": "#D7EAF5",     # vetro, azzurro chiaro
    "vetro_stroke": "#A9CDE0",
    "quota": "#6B7570",
    "sfondo": "#FFFFFF",
}

SPESSORE_PROFILO_STROKE = 1      # bordo sottile sulle fasce piene di telaio/anta
SPESSORE_VETRO_STROKE = 1
SPESSORE_QUOTA = 1.2
SPESSORE_SIMBOLO_APERTURA = 1.4

LUNGHEZZA_TACCA_MM = 16

# --- Maniglia: dimensioni in mm, coerenti con le altre costanti geometriche del modulo ---
HANDLE_LENGTH_MM = 70
HANDLE_WIDTH_MM = 18
HANDLE_PIVOT_RADIUS_MM = 9


def rettangolo(x, y, larghezza, altezza, stroke, stroke_width, fill="none"):
    return (
        f'<rect x="{x}" y="{y}" width="{larghezza}" height="{altezza}" '
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
    """Disegna un profilo (telaio o anta) come vera fascia piena: rettangolo esterno
    colorato + rettangolo interno 'svuotato' in bianco sopra — rappresentazione
    standard dello spessore di un profilo in vista frontale tecnica."""
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
    """Disegna una maniglia tecnica (leva + perno) sul bordo verticale dell'anta
    indicato da `apertura`. La posizione è calcolata interamente a partire dal
    rettangolo `anta` (x, y, larghezza, altezza) — nessuna coordinata assoluta
    hardcoded — quindi resta corretta al variare di larghezza, altezza, numero
    di ante e apertura. Nessuna maniglia se `apertura` non è "sinistra"/"destra"
    (es. ante fisse, per cui il chiamante comunque non dovrebbe invocarla)."""
    if apertura not in ("sinistra", "destra"):
        return ""

    y_centro = anta["y"] + anta["altezza"] / 2

    if apertura == "sinistra":
        x_bordo = anta["x"]
        x_leva_fine = x_bordo + HANDLE_LENGTH_MM
    else:  # destra
        x_bordo = anta["x"] + anta["larghezza"]
        x_leva_fine = x_bordo - HANDLE_LENGTH_MM

    svg = ""
    # Leva: piccola barra che protrude dal bordo verso l'interno dell'anta
    svg += rettangolo(
        min(x_bordo, x_leva_fine), y_centro - HANDLE_WIDTH_MM / 2,
        HANDLE_LENGTH_MM, HANDLE_WIDTH_MM,
        PALETTE["anta"], SPESSORE_PROFILO_STROKE, fill=PALETTE["anta"]
    )
    # Perno: punto di fissaggio sul bordo dell'anta
    svg += cerchio(
        x_bordo, y_centro, HANDLE_PIVOT_RADIUS_MM,
        PALETTE["anta"], SPESSORE_PROFILO_STROKE, fill=PALETTE["sfondo"]
    )

    return svg
