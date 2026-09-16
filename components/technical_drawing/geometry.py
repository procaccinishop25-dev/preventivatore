"""Calcoli geometrici puri per il disegno tecnico di infissi parametrici.
Tutte le funzioni lavorano in millimetri (l'unità di misura reale dell'infisso).
Nessuna funzione qui produce grafica: solo numeri e rettangoli logici."""

FRAME_THICKNESS_MM = 60      # spessore della fascia del telaio esterno
SASH_THICKNESS_MM = 50       # spessore della fascia propria dell'anta (profilo mobile)
GLAZING_BEAD_MM = 15         # fermavetro: spazio tra la battuta dell'anta e il vetro visibile
MULLION_THICKNESS_MM = 40

MARGIN_LEFT_MM = 160
MARGIN_RIGHT_MM = 40
MARGIN_TOP_MM = 40
MARGIN_BOTTOM_MM = 140

QUOTA_OFFSET_MM = 60  # distanza tra il disegno e la linea di quota


def _inset(rettangolo, quantita):
    """Restituisce un rettangolo più interno di `quantita` mm su ogni lato."""
    return {
        "x": rettangolo["x"] + quantita,
        "y": rettangolo["y"] + quantita,
        "larghezza": rettangolo["larghezza"] - 2 * quantita,
        "altezza": rettangolo["altezza"] - 2 * quantita,
    }


def calcola_viewbox(larghezza_mm, altezza_mm):
    """Dimensioni totali del 'foglio' di disegno, infisso + margini per le quote."""
    larghezza_totale = larghezza_mm + MARGIN_LEFT_MM + MARGIN_RIGHT_MM
    altezza_totale = altezza_mm + MARGIN_TOP_MM + MARGIN_BOTTOM_MM
    return larghezza_totale, altezza_totale


def calcola_telaio(larghezza_mm, altezza_mm):
    """Rettangolo del telaio esterno, posizionato dentro il foglio tenendo conto dei margini."""
    return {
        "x": MARGIN_LEFT_MM,
        "y": MARGIN_TOP_MM,
        "larghezza": larghezza_mm,
        "altezza": altezza_mm,
    }


def calcola_area_interna_telaio(telaio):
    """Area utile dentro la fascia del telaio, dove vivono le ante."""
    return _inset(telaio, FRAME_THICKNESS_MM)


def calcola_ante(telaio, numero_ante):
    """Divide l'area interna del telaio in `numero_ante` sezioni verticali uguali,
    lasciando spazio per i montanti centrali. Restituisce una lista di rettangoli anta
    (il rettangolo ESTERNO di ogni anta, comprensivo del proprio profilo)."""
    area_interna = calcola_area_interna_telaio(telaio)

    numero_montanti = numero_ante - 1
    larghezza_totale_montanti = numero_montanti * MULLION_THICKNESS_MM
    larghezza_anta = (area_interna["larghezza"] - larghezza_totale_montanti) / numero_ante

    ante = []
    x_corrente = area_interna["x"]
    for _ in range(numero_ante):
        ante.append({
            "x": x_corrente,
            "y": area_interna["y"],
            "larghezza": larghezza_anta,
            "altezza": area_interna["altezza"],
        })
        x_corrente += larghezza_anta + MULLION_THICKNESS_MM

    return ante


def calcola_montanti(telaio, ante):
    """Rettangoli pieni dei montanti (divisori centrali) tra ogni coppia di ante adiacenti."""
    area_interna = calcola_area_interna_telaio(telaio)
    montanti = []
    for i in range(len(ante) - 1):
        anta_corrente = ante[i]
        anta_successiva = ante[i + 1]
        x_montante = anta_corrente["x"] + anta_corrente["larghezza"]
        montanti.append({
            "x": x_montante,
            "y": area_interna["y"],
            "larghezza": anta_successiva["x"] - x_montante,
            "altezza": area_interna["altezza"],
        })
    return montanti


def calcola_battuta_anta(anta):
    """Rettangolo interno dell'anta, dopo il proprio profilo (spessore SASH_THICKNESS_MM)."""
    return _inset(anta, SASH_THICKNESS_MM)


def calcola_vetro(battuta):
    """Rettangolo del vetro visibile, dopo il fermavetro rispetto alla battuta dell'anta."""
    return _inset(battuta, GLAZING_BEAD_MM)


def normalizza_configurazione_ante(numero_ante, apertura_globale):
    """Prepara una configurazione di apertura per singola anta.

    Oggi restituisce semplicemente la stessa apertura ripetuta per ogni anta —
    la UI espone ancora un solo parametro globale. La funzione esiste già con
    questa firma in modo che in futuro possa accettare (o restituire) aperture
    diverse per ciascuna anta senza dover cambiare le funzioni che la consumano."""
    return [apertura_globale] * numero_ante
