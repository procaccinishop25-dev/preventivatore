"""Motore di rendering: assembla gli elementi geometrici in un disegno SVG completo.
Unico punto d'ingresso pubblico: genera_finestra()."""

from . import geometry
from . import elements


def genera_finestra(larghezza_mm, altezza_mm, configurazione_ante, larghezza_display=600):
    """`configurazione_ante` è una lista di dizionari, uno per anta:
    {"tipo": "fissa"} oppure {"tipo": "apribile", "apertura": "sinistra"/"destra"},
    con eventuale chiave opzionale "larghezza_mm" per larghezze asimmetriche.
    Il numero di ante è dedotto dalla lunghezza di questa lista."""
    numero_ante_stimato = len(configurazione_ante) if isinstance(configurazione_ante, list) else 1
    configurazione_ante = geometry.normalizza_configurazione_ante(numero_ante_stimato, configurazione_ante)
    numero_ante = len(configurazione_ante)

    larghezza_totale, altezza_totale = geometry.calcola_viewbox(larghezza_mm, altezza_mm)
    telaio = geometry.calcola_telaio(larghezza_mm, altezza_mm)
    area_interna_telaio = geometry.calcola_area_interna_telaio(telaio)
    ante = geometry.calcola_ante(telaio, configurazione_ante)
    montanti = geometry.calcola_montanti(telaio, ante)

    contenuto_svg = ""

    # 1. Telaio: fascia piena esterna (struttura fissa)
    contenuto_svg += elements.fascia_profilo(telaio, area_interna_telaio, elements.PALETTE["telaio"])

    # 2. Ogni anta: fascia propria, battuta, fermavetro, vetro, simbolo apertura, maniglia
    for anta, configurazione_anta in zip(ante, configurazione_ante):
        battuta = geometry.calcola_battuta_anta(anta)
        zona_fermavetro = geometry.calcola_zona_fermavetro(battuta)
        vetro = geometry.calcola_vetro(zona_fermavetro)

        # 2a. Fascia anta (esterno anta -> confine battuta)
        contenuto_svg += elements.fascia_profilo(anta, battuta, elements.PALETTE["anta"])
        # 2b. Linea di battuta (contorno sottile, nessun riempimento)
        contenuto_svg += elements.linea_battuta(battuta)
        # 2c. Fascia fermavetro (confine battuta -> confine vetro)
        contenuto_svg += elements.fascia_profilo(zona_fermavetro, vetro, elements.PALETTE["fermavetro"])
        # 2d. Vetro
        contenuto_svg += elements.rettangolo(
            vetro["x"], vetro["y"], vetro["larghezza"], vetro["altezza"],
            elements.PALETTE["vetro_stroke"], elements.SPESSORE_VETRO_STROKE,
            fill=elements.PALETTE["vetro_fill"]
        )
        # 2e. Simbolo apertura (sulla battuta, come già in precedenza)
        contenuto_svg += elements.simbolo_apertura(battuta, configurazione_anta)

        # 2f. Maniglia
        if configurazione_anta.get("tipo") == "apribile":
            contenuto_svg += elements.disegna_maniglia(battuta, configurazione_anta.get("apertura", "destra"))

    # 3. Montanti: colore del telaio, per leggerli come elemento strutturale fisso
    for montante in montanti:
        contenuto_svg += elements.rettangolo(
            montante["x"], montante["y"], montante["larghezza"], montante["altezza"],
            elements.PALETTE["telaio"], 0, fill=elements.PALETTE["telaio"]
        )

    # 4. Quote
    y_quota_orizzontale = telaio["y"] + telaio["altezza"] + geometry.QUOTA_OFFSET_MM
    contenuto_svg += elements.quota_orizzontale(
        telaio["x"], telaio["x"] + telaio["larghezza"],
        y_quota_orizzontale, telaio["y"] + telaio["altezza"],
        f"{int(larghezza_mm)} mm"
    )

    x_quota_verticale = telaio["x"] - geometry.QUOTA_OFFSET_MM
    contenuto_svg += elements.quota_verticale(
        telaio["y"], telaio["y"] + telaio["altezza"],
        x_quota_verticale, telaio["x"],
        f"{int(altezza_mm)} mm"
    )

    altezza_display = larghezza_display * (altezza_totale / larghezza_totale)

    return (
        f'<svg viewBox="0 0 {larghezza_totale} {altezza_totale}" '
        f'width="{larghezza_display}" height="{altezza_display:.0f}" '
        f'style="width:100%; max-width:{larghezza_display}px; height:auto;" '
        f'xmlns="http://www.w3.org/2000/svg">'
        f'<rect x="0" y="0" width="{larghezza_totale}" height="{altezza_totale}" fill="{elements.PALETTE["sfondo"]}" />'
        f'{contenuto_svg}'
        f'</svg>'
    )
