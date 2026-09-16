"""Calcoli geometrici puri per il disegno tecnico di infissi parametrici.
Tutte le funzioni lavorano in millimetri (l'unità di misura reale dell'infisso).
Nessuna funzione qui produce grafica: solo numeri e rettangoli logici."""

FRAME_THICKNESS_MM = 60
MULLION_THICKNESS_MM = 40
GLASS_INSET_MM = 20

MARGIN_LEFT_MM = 160
MARGIN_RIGHT_MM = 40
MARGIN_TOP_MM = 40
MARGIN_BOTTOM_MM = 140


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


def calcola_ante(telaio, numero_ante):
    """Divide l'area interna del telaio in `numero_ante` sezioni verticali uguali,
    lasciando spazio per i montanti centrali. Restituisce una lista di rettangoli anta."""
    area_interna_x = telaio["x"] + FRAME_THICKNESS_MM
    area_interna_y = telaio["y"] + FRAME_THICKNESS_MM
    area_interna_larghezza = telaio["larghezza"] - 2 * FRAME_THICKNESS_MM
    area_interna_altezza = telaio["altezza"] - 2 * FRAME_THICKNESS_MM

    numero_montanti = numero_ante - 1
    larghezza_totale_montanti = numero_montanti * MULLION_THICKNESS_MM
    larghezza_anta = (area_interna_larghezza - larghezza_totale_montanti) / numero_ante

    ante = []
    x_corrente = area_interna_x
    for _ in range(numero_ante):
        ante.append({
            "x": x_corrente,
            "y": area_interna_y,
            "larghezza": larghezza_anta,
            "altezza": area_interna_altezza,
        })
        x_corrente += larghezza_anta + MULLION_THICKNESS_MM

    return ante


def calcola_montanti(telaio, ante):
    """Rettangoli pieni dei montanti (divisori centrali) tra ogni coppia di ante adiacenti."""
    montanti = []
    for i in range(len(ante) - 1):
        anta_corrente = ante[i]
        anta_successiva = ante[i + 1]
        x_montante = anta_corrente["x"] + anta_corrente["larghezza"]
        montanti.append({
            "x": x_montante,
            "y": telaio["y"] + FRAME_THICKNESS_MM,
            "larghezza": anta_successiva["x"] - x_montante,
            "altezza": telaio["altezza"] - 2 * FRAME_THICKNESS_MM,
        })
    return montanti


def calcola_vetro(anta):
    """Rettangolo del vetro, inset rispetto al telaio dell'anta."""
    return {
        "x": anta["x"] + GLASS_INSET_MM,
        "y": anta["y"] + GLASS_INSET_MM,
        "larghezza": anta["larghezza"] - 2 * GLASS_INSET_MM,
        "altezza": anta["altezza"] - 2 * GLASS_INSET_MM,
    }
