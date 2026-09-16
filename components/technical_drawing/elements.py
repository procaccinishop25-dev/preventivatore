"""Elementi grafici SVG riutilizzabili per il motore di disegno tecnico.
Ogni funzione restituisce una stringa SVG pronta da concatenare — nessuna
funzione qui fa calcoli geometrici, solo disegno."""

COLORE_TELAIO = "#1A1D1B"
COLORE_ANTA = "#3D453F"
COLORE_VETRO_FILL = "#D6EAF8"
COLORE_VETRO_STROKE = "#A9CCE3"
COLORE_QUOTA = "#69746E"

SPESSORE_TELAIO = 4
SPESSORE_ANTA = 2
SPESSORE_QUOTA = 1


def rettangolo(x, y, larghezza, altezza, stroke, stroke_width, fill="none"):
    return (
        f'<rect x="{x}" y="{y}" width="{larghezza}" height="{altezza}" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}" />'
    )


def linea(x1, y1, x2, y2, stroke, stroke_width):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" stroke-width="{stroke_width}" />'


def testo(x, y, contenuto, dimensione=28, ancoraggio="middle", rotazione=0):
    trasformazione = f' transform="rotate({rotazione} {x} {y})"' if rotazione else ""
    return (
        f'<text x="{x}" y="{y}" font-size="{dimensione}" fill="{COLORE_QUOTA}" '
        f'text-anchor="{ancoraggio}" font-family="Inter, sans-serif"{trasformazione}>{contenuto}</text>'
    )


def quota_orizzontale(x_inizio, x_fine, y_quota, y_oggetto, etichetta):
    """Linea di quota orizzontale con tratti di richiamo dall'oggetto e testo centrato."""
    svg = ""
    svg += linea(x_inizio, y_oggetto, x_inizio, y_quota + 15, COLORE_QUOTA, SPESSORE_QUOTA)
    svg += linea(x_fine, y_oggetto, x_fine, y_quota + 15, COLORE_QUOTA, SPESSORE_QUOTA)
    svg += linea(x_inizio, y_quota, x_fine, y_quota, COLORE_QUOTA, SPESSORE_QUOTA)
    svg += linea(x_inizio, y_quota - 8, x_inizio, y_quota + 8, COLORE_QUOTA, SPESSORE_QUOTA)
    svg += linea(x_fine, y_quota - 8, x_fine, y_quota + 8, COLORE_QUOTA, SPESSORE_QUOTA)
    x_centro = (x_inizio + x_fine) / 2
    svg += testo(x_centro, y_quota + 32, etichetta)
    return svg


def quota_verticale(y_inizio, y_fine, x_quota, x_oggetto, etichetta):
    """Linea di quota verticale con tratti di richiamo dall'oggetto e testo ruotato."""
    svg = ""
    svg += linea(x_oggetto, y_inizio, x_quota - 15, y_inizio, COLORE_QUOTA, SPESSORE_QUOTA)
    svg += linea(x_oggetto, y_fine, x_quota - 15, y_fine, COLORE_QUOTA, SPESSORE_QUOTA)
    svg += linea(x_quota, y_inizio, x_quota, y_fine, COLORE_QUOTA, SPESSORE_QUOTA)
    svg += linea(x_quota - 8, y_inizio, x_quota + 8, y_inizio, COLORE_QUOTA, SPESSORE_QUOTA)
    svg += linea(x_quota - 8, y_fine, x_quota + 8, y_fine, COLORE_QUOTA, SPESSORE_QUOTA)
    y_centro = (y_inizio + y_fine) / 2
    svg += testo(x_quota - 30, y_centro, etichetta, rotazione=-90)
    return svg


def simbolo_apertura(anta, direzione):
    """Simbolo standard di apertura: due linee convergenti verso il lato della cerniera.
    Nessun simbolo se l'apertura è 'Fissa'."""
    if direzione == "Fissa":
        return ""

    x, y = anta["x"], anta["y"]
    larghezza, altezza = anta["larghezza"], anta["altezza"]

    if direzione == "Destra":
        apice = (x + larghezza, y + altezza / 2)
        angolo1 = (x, y)
        angolo2 = (x, y + altezza)
    else:  # Sinistra
        apice = (x, y + altezza / 2)
        angolo1 = (x + larghezza, y)
        angolo2 = (x + larghezza, y + altezza)

    svg = ""
    svg += linea(angolo1[0], angolo1[1], apice[0], apice[1], COLORE_ANTA, SPESSORE_ANTA)
    svg += linea(angolo2[0], angolo2[1], apice[0], apice[1], COLORE_ANTA, SPESSORE_ANTA)
    return svg
