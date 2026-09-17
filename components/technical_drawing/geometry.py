"""Calcoli geometrici puri per il disegno tecnico di infissi parametrici.
Tutte le funzioni lavorano in millimetri (l'unità di misura reale dell'infisso).
Nessuna funzione qui produce grafica: solo numeri e rettangoli logici."""

FRAME_THICKNESS_MM = 60      # spessore della fascia del telaio esterno
SASH_THICKNESS_MM = 50       # spessore della fascia propria dell'anta (profilo mobile)

# --- Battuta: parametro iniziale del modello grafico, non una misura costruttiva
# universale. Rappresenta simbolicamente la zona di tenuta/incastro tra anta e
# fermavetro — pensata per essere ritoccata facilmente in futuro. ---
BATTUTA_MM = 8

GLAZING_BEAD_MM = 15         # spessore della fascia del fermavetro, ora effettivamente disegnata
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


def larghezza_disponibile_per_ante(telaio, numero_ante):
    """Calcola quanto spazio orizzontale è disponibile per distribuire tra le ante,
    al netto dei montanti necessari per il numero di ante indicato. Utile per una
    futura UI che mostri all'utente quanto spazio ha già allocato."""
    area_interna = calcola_area_interna_telaio(telaio)
    numero_montanti = numero_ante - 1
    return area_interna["larghezza"] - numero_montanti * MULLION_THICKNESS_MM


def valida_larghezze_ante(area_interna_larghezza, larghezze_mm, numero_montanti, tolleranza_mm=0.5):
    """Verifica che la somma delle larghezze anta + gli spazi dei montanti
    corrisponda allo spazio orizzontale disponibile dentro il telaio, e che
    ogni anta sia abbastanza larga da contenere profilo/battuta/fermavetro.
    Solleva ValueError con un messaggio preciso se qualcosa non torna."""
    somma_larghezze = sum(larghezze_mm)
    spazio_montanti = numero_montanti * MULLION_THICKNESS_MM
    totale_richiesto = somma_larghezze + spazio_montanti
    differenza = area_interna_larghezza - totale_richiesto

    if abs(differenza) > tolleranza_mm:
        if differenza > 0:
            raise ValueError(
                f"Le larghezze delle ante (totale {somma_larghezze:.0f}mm) più i montanti "
                f"({spazio_montanti:.0f}mm) non riempiono lo spazio disponibile "
                f"({area_interna_larghezza:.0f}mm). Mancano {differenza:.0f}mm."
            )
        raise ValueError(
            f"Le larghezze delle ante (totale {somma_larghezze:.0f}mm) più i montanti "
            f"({spazio_montanti:.0f}mm) superano lo spazio disponibile "
            f"({area_interna_larghezza:.0f}mm) di {abs(differenza):.0f}mm."
        )

    larghezza_minima_anta = 2 * (SASH_THICKNESS_MM + BATTUTA_MM + GLAZING_BEAD_MM) + 1
    for indice, larghezza in enumerate(larghezze_mm, start=1):
        if larghezza < larghezza_minima_anta:
            raise ValueError(
                f"L'anta {indice} ha una larghezza di {larghezza:.0f}mm, troppo stretta per "
                f"contenere profilo, battuta e fermavetro (minimo {larghezza_minima_anta:.0f}mm)."
            )


def calcola_ante(telaio, configurazione_ante):
    """Divide l'area interna del telaio in una sezione per ogni anta, lasciando
    spazio per i montanti centrali. Restituisce una lista di rettangoli anta
    (il rettangolo ESTERNO di ogni anta, comprensivo del proprio profilo).

    `configurazione_ante` è la lista di dizionari normalizzata (una voce per
    anta). Se NESSUNA voce specifica "larghezza_mm", le ante vengono divise in
    parti uguali (comportamento storico, retrocompatibile). Se TUTTE le voci
    specificano "larghezza_mm", vengono usate quelle larghezze esatte, previa
    validazione. Un mix (solo alcune voci con larghezza_mm) è un errore."""
    area_interna = calcola_area_interna_telaio(telaio)
    numero_ante = len(configurazione_ante)
    numero_montanti = numero_ante - 1

    larghezze_specificate = [c.get("larghezza_mm") for c in configurazione_ante]
    numero_specificate = sum(1 for l in larghezze_specificate if l is not None)

    if numero_specificate == 0:
        larghezza_totale_montanti = numero_montanti * MULLION_THICKNESS_MM
        larghezza_anta = (area_interna["larghezza"] - larghezza_totale_montanti) / numero_ante
        larghezze_ante = [larghezza_anta] * numero_ante
    elif numero_specificate == numero_ante:
        larghezze_ante = larghezze_specificate
        valida_larghezze_ante(area_interna["larghezza"], larghezze_ante, numero_montanti)
    else:
        raise ValueError(
            "Specifica la larghezza per tutte le ante, oppure per nessuna. "
            f"Larghezza specificata per {numero_specificate} ante su {numero_ante}."
        )

    ante = []
    x_corrente = area_interna["x"]
    for larghezza_anta in larghezze_ante:
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
    """Rettangolo interno dell'anta, dopo il proprio profilo (spessore SASH_THICKNESS_MM).
    Rappresenta il confine tra la fascia dell'anta e la zona di battuta."""
    return _inset(anta, SASH_THICKNESS_MM)


def calcola_zona_fermavetro(battuta):
    """Rettangolo interno alla battuta, dopo la zona di battuta (spessore BATTUTA_MM).
    Rappresenta il confine dove inizia la fascia del fermavetro."""
    return _inset(battuta, BATTUTA_MM)


def calcola_vetro(zona_fermavetro):
    """Rettangolo del vetro visibile, dopo il fermavetro rispetto alla zona di fermavetro."""
    return _inset(zona_fermavetro, GLAZING_BEAD_MM)


def normalizza_configurazione_ante(numero_ante, configurazione):
    """Restituisce sempre una lista di dizionari, uno per anta, nel formato:
    {"tipo": "fissa"} oppure {"tipo": "apribile", "apertura": "sinistra"/"destra"},
    con eventuale chiave opzionale "larghezza_mm".

    Accetta due formati in ingresso:

    - Nuovo formato (preferito): `configurazione` è già una lista di dizionari
      in questo formato — viene restituita così com'è.
    - Vecchio formato (retrocompatibilità): `configurazione` è una singola
      stringa globale ("Fissa", "Sinistra", "Destra", case-insensitive) —
      viene convertita e ripetuta per `numero_ante` volte, senza "larghezza_mm"
      (quindi il chiamante otterrà sempre la divisione equa storica)."""
    if isinstance(configurazione, list):
        return configurazione

    valore = (configurazione or "").strip().lower()
    if valore in ("", "fissa"):
        singola = {"tipo": "fissa"}
    else:
        singola = {"tipo": "apribile", "apertura": valore}

    return [dict(singola) for _ in range(numero_ante)]
