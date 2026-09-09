import streamlit as st


def status_dot(testo, tipo="neutral"):
    """Stato leggero per le liste: bullet colorato + testo, senza sfondo pieno.
    Usa la stessa mappa colori di badge()/stato_badge() in theme.py — nessun colore nuovo introdotto."""
    colori = {
        "success":   "#176B52",
        "warning":   "#B85E2D",
        "danger":    "#B33A3A",
        "info":      "#69746E",
        "bozza":     "#69746E",
        "inviato":   "#B85E2D",
        "accettato": "#176B52",
        "rifiutato": "#B33A3A",
        "neutral":   "#69746E",
    }
    colore = colori.get(tipo, colori["neutral"])
    return (
        f"<span style='display:inline-flex; align-items:center; gap:6px; "
        f"font-size:0.82rem; color:var(--color-text-quiet); font-weight:500; white-space:nowrap;'>"
        f"<span style='width:7px; height:7px; border-radius:50%; background-color:{colore}; flex-shrink:0;'></span>"
        f"{testo}</span>"
    )


def page_toolbar(titolo, descrizione=None, cta_label=None, cta_icon=None, cta_page=None, cta_key=None):
    """Header di pagina condiviso: titolo+descrizione a sinistra, CTA primaria a destra (opzionale)."""
    if cta_label:
        col_titolo, col_cta = st.columns([4, 1.6])
    else:
        col_titolo = st.container()
        col_cta = None

    with col_titolo:
        st.markdown(f"<h1 style='margin-bottom:2px;'>{titolo}</h1>", unsafe_allow_html=True)
        if descrizione:
            st.markdown(
                f"<p style='color:var(--color-text-secondary); font-size:0.86rem; margin-top:0; margin-bottom:0;'>{descrizione}</p>",
                unsafe_allow_html=True
            )

    premuto = False
    if cta_label and col_cta is not None:
        with col_cta:
            st.markdown("<div style='padding-top:4px;'>", unsafe_allow_html=True)
            icona = f":material/{cta_icon}:" if cta_icon else None
            if cta_page:
                st.page_link(cta_page, label=cta_label, icon=icona, use_container_width=True)
            else:
                premuto = st.button(cta_label, icon=icona, type="primary", use_container_width=True, key=cta_key)
            st.markdown("</div>", unsafe_allow_html=True)

    return premuto


def section_link_header(titolo, link_page, link_label="Vedi tutti"):
    """Pattern 'Titolo + Vedi tutti \u2192', per riepiloghi che rimandano a una lista completa."""
    col1, col2 = st.columns([5, 1.4])
    with col1:
        st.markdown(f"<h2 style='margin:0;'>{titolo}</h2>", unsafe_allow_html=True)
    with col2:
        st.page_link(link_page, label=link_label, icon=":material/arrow_forward:")


def list_item(
    titolo, sottotitolo,
    stato_testo=None, stato_tipo="neutral",
    azione_primaria_label=None, key_primaria=None, azione_primaria_icon="arrow_forward",
    azione_secondaria_label=None, azione_secondaria_icon=None, key_secondaria=None,
    azioni_menu=None,
):
    """Riga di lista condivisa e flessibile: Titolo/sottotitolo | Stato (opzionale) | Azioni (tutte opzionali).

    - stato_testo=None → nessuna colonna di stato (per entità senza un vero concetto di stato: infissi, maggiorazioni, prodotti)
    - azione_primaria_label=None → nessuna azione primaria (es. righe con solo un menu overflow)
    - azioni_menu: lista di dict {"label", "icon", "key", "danger": bool (opzionale)}

    Ritorna {"primaria": bool, "secondaria": bool, "menu": key_premuta_o_None}
    """
    risultato = {"primaria": False, "secondaria": False, "menu": None}

    mostra_stato = stato_testo is not None
    if mostra_stato:
        col_info, col_stato, col_azioni = st.columns([3.2, 1.5, 2.8])
    else:
        col_info, col_azioni = st.columns([4.2, 2.8])
        col_stato = None

    with col_info:
        st.markdown(
            f"<div style='font-weight:600; color:var(--color-title); font-size:0.88rem; line-height:1.35;'>{titolo}</div>"
            f"<div style='color:var(--color-text-secondary); font-size:0.8rem; margin-top:1px;'>{sottotitolo}</div>",
            unsafe_allow_html=True
        )

    if mostra_stato and col_stato is not None:
        with col_stato:
            st.markdown(f"<div style='padding-top:5px;'>{status_dot(stato_testo, stato_tipo)}</div>", unsafe_allow_html=True)

    with col_azioni:
        ha_primaria = bool(azione_primaria_label)
        ha_secondaria = bool(azione_secondaria_label)
        ha_menu = bool(azioni_menu)

        if not (ha_primaria or ha_secondaria or ha_menu):
            return risultato

        rapporti = []
        if ha_primaria:
            rapporti.append(3)
        if ha_secondaria:
            rapporti.append(1)
        if ha_menu:
            rapporti.append(1)

        sotto_colonne = st.columns(rapporti)
        indice = 0

        if ha_primaria:
            with sotto_colonne[indice]:
                risultato["primaria"] = st.button(
                    azione_primaria_label,
                    icon=f":material/{azione_primaria_icon}:",
                    type="primary", use_container_width=True, key=key_primaria
                )
            indice += 1

        if ha_secondaria:
            with sotto_colonne[indice]:
                risultato["secondaria"] = st.button(
                    "", icon=f":material/{azione_secondaria_icon}:",
                    use_container_width=True, key=key_secondaria, help=azione_secondaria_label
                )
            indice += 1

        if ha_menu:
            with sotto_colonne[indice]:
                with st.popover("⋯", use_container_width=True):
                    for azione in azioni_menu:
                        classe = "action-danger" if azione.get("danger") else ""
                        if classe:
                            st.markdown(f"<div class='{classe}'>", unsafe_allow_html=True)
                        if st.button(
                            azione["label"], icon=f":material/{azione['icon']}:",
                            key=azione["key"], use_container_width=True
                        ):
                            risultato["menu"] = azione["key"]
                        if classe:
                            st.markdown("</div>", unsafe_allow_html=True)

    return risultato
