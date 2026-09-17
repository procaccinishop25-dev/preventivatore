import streamlit as st
from services.theme import apply_custom_theme
from components.technical_drawing import genera_finestra
from components.technical_drawing.geometry import (
    larghezza_disponibile_per_ante,
    calcola_telaio,
    FRAME_THICKNESS_MM,
    MULLION_THICKNESS_MM,
)

st.set_page_config(page_title="Editor Tecnico (Test)", page_icon="📐", layout="wide")
apply_custom_theme()

st.markdown(
    "<div class='page-header'><h1>Editor Tecnico — Prototipo</h1>"
    "<p>Pagina di test isolata per lo sviluppo del motore di disegno tecnico parametrico. "
    "Non collegata al resto dell'applicazione.</p></div>",
    unsafe_allow_html=True
)

col_config, col_anteprima = st.columns([1, 2])

with col_config:
    with st.container(border=True):
        st.markdown("#### Configurazione")

        larghezza_mm = st.number_input("Larghezza infisso (mm)", min_value=400, max_value=4000, value=1200, step=10)
        altezza_mm = st.number_input("Altezza infisso (mm)", min_value=400, max_value=4000, value=1500, step=10)
        numero_ante = st.selectbox("Numero ante", [1, 2, 3, 4], index=1)

        st.markdown("---")
        usa_larghezze_personalizzate = st.checkbox("Aggiungi dimensioni diverse")

        if usa_larghezze_personalizzate:
            telaio = calcola_telaio(larghezza_mm, altezza_mm)
            disponibile = larghezza_disponibile_per_ante(telaio, numero_ante)
            numero_montanti = numero_ante - 1

            st.caption(f"Spazio disponibile da distribuire tra le ante: **{disponibile:.0f} mm** (montanti già esclusi)")

            with st.expander("ℹ️ Esempio di calcolo"):
                righe_sottrazione = f"{larghezza_mm:.0f} mm  (larghezza infisso)\n"
                righe_sottrazione += f"− {FRAME_THICKNESS_MM} mm  (telaio sinistro)\n"
                righe_sottrazione += f"− {FRAME_THICKNESS_MM} mm  (telaio destro)\n"
                if numero_montanti > 0:
                    etichetta_montanti = "montante" if numero_montanti == 1 else "montanti"
                    righe_sottrazione += f"− {numero_montanti * MULLION_THICKNESS_MM} mm  ({numero_montanti} {etichetta_montanti} × {MULLION_THICKNESS_MM}mm)\n"
                righe_sottrazione += f"= {disponibile:.0f} mm disponibili per le ante"

                st.markdown(
                    "**Come vengono calcolate le larghezze?**\n\n"
                    "La misura dell'infisso è la misura totale. Il sistema considera "
                    "automaticamente lo spazio occupato dal telaio e dai montanti prima di "
                    "calcolare lo spazio disponibile per le ante.\n\n"
                    f"Per questo infisso ({larghezza_mm:.0f} × {altezza_mm:.0f} mm, {numero_ante} ant{'a' if numero_ante == 1 else 'e'}):"
                )
                st.code(righe_sottrazione, language=None)
                st.caption("La somma delle larghezze che inserisci per le singole ante deve corrispondere esattamente a questo valore.")

        st.markdown("##### Configurazione ante")

        configurazione_ante = []
        somma_larghezze_inserite = 0

        for i in range(1, numero_ante + 1):
            col_tipo, col_apertura = st.columns(2)
            with col_tipo:
                tipo_label = st.selectbox(
                    f"Anta {i} — Tipo", ["Fissa", "Apribile"],
                    index=1, key=f"tipo_anta_{i}"
                )

            voce_anta = {}
            if tipo_label == "Apribile":
                with col_apertura:
                    apertura_label = st.selectbox(
                        f"Anta {i} — Apertura", ["Sinistra", "Destra"],
                        index=1, key=f"apertura_anta_{i}"
                    )
                voce_anta = {"tipo": "apribile", "apertura": apertura_label.lower()}
            else:
                voce_anta = {"tipo": "fissa"}

            if usa_larghezze_personalizzate:
                larghezza_anta_mm = st.number_input(
                    f"Anta {i} — Larghezza (mm)", min_value=50, max_value=3000,
                    value=300, step=10, key=f"larghezza_anta_{i}"
                )
                voce_anta["larghezza_mm"] = larghezza_anta_mm
                somma_larghezze_inserite += larghezza_anta_mm

            configurazione_ante.append(voce_anta)

        if usa_larghezze_personalizzate:
            st.caption(f"Totale larghezze inserite (senza montanti): **{somma_larghezze_inserite:.0f} mm**")

with col_anteprima:
    with st.container(border=True):
        st.markdown("#### Anteprima disegno tecnico")
        try:
            svg = genera_finestra(larghezza_mm, altezza_mm, configurazione_ante)
            st.markdown(svg, unsafe_allow_html=True)
        except ValueError as errore:
            st.error(str(errore))
