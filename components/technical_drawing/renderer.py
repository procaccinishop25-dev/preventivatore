"""Motore di rendering: assembla gli elementi geometrici in un disegno SVG completo.
Unico punto d'ingresso pubblico: genera_finestra()."""

from . import geometry
from . import elements


def genera_finestra(larghezza_mm, altezza_mm, numero_ante, apertura, larghezza_display=600):
    larghezza_totale, altezza_totale = geometry.calcola_viewbox(larghezza_mm, altezza_mm)
    telaio = geometry.calcola_telaio(larghezza_mm, altezza_mm)
    ante = geometry.calcola_ante(telaio, numero_ante)
    montanti = geometry.calcola_montanti(telaio, ante)

    contenuto_svg = ""

    # Telaio esterno
    contenuto_svg += elements.rettangolo(
        telaio["x"], telaio["y"], telaio["larghezza"], telaio["altezza"],
        elements.COLORE_TELAIO, elements.SPESSORE_TELAIO
    )

    # Ogni anta: vetro, telaio dell'anta, simbolo apertura
    for anta in ante:
        vetro = geometry.calcola_vetro(anta)
        contenuto_svg += elements.rettangolo(
            vetro["x"], vetro["y"], vetro["larghezza"], vetro["altezza"],
            elements.COLORE_VETRO_STROKE, 1, fill=elements.COLORE_VETRO_FILL
        )
        contenuto_svg += elements.rettangolo(
            anta["x"], anta["y"], anta["larghezza"], anta["altezza"],
            elements.COLORE_ANTA, elements.SPESSORE_ANTA
        )
        contenuto_svg += elements.simbolo_apertura(anta, apertura)

    # Montanti (divisori centrali), pieni
    for montante in montanti:
        contenuto_svg += elements.rettangolo(
            montante["x"], montante["y"], montante["larghezza"], montante["altezza"],
            elements.COLORE_ANTA, 1, fill=elements.COLORE_ANTA
        )

    # Quote
    contenuto_svg += elements.quota_orizzontale(
        telaio["x"], telaio["x"] + telaio["larghezza"],
        telaio["y"] + telaio["altezza"] + 60, telaio["y"] + telaio["altezza"],
        f"{int(larghezza_mm)} mm"
    )
    contenuto_svg += elements.quota_verticale(
        telaio["y"], telaio["y"] + telaio["altezza"],
        telaio["x"] - 60, telaio["x"],
        f"{int(altezza_mm)} mm"
    )

    altezza_display = larghezza_display * (altezza_totale / larghezza_totale)

    return (
        f'<svg viewBox="0 0 {larghezza_totale} {altezza_totale}" '
        f'width="{larghezza_display}" height="{altezza_display:.0f}" '
        f'style="width:100%; max-width:{larghezza_display}px; height:auto;" '
        f'xmlns="http://www.w3.org/2000/svg">'
        f'<rect x="0" y="0" width="{larghezza_totale}" height="{altezza_totale}" fill="#FFFFFF" />'
        f'{contenuto_svg}'
        f'</svg>'
    )
