import streamlit as st
from services.theme import apply_custom_theme
from components.technical_drawing import genera_finestra

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
        apertura = st.selectbox("Apertura", ["Fissa", "Sinistra", "Destra"], index=2)

with col_anteprima:
    with st.container(border=True):
        st.markdown("#### Anteprima disegno tecnico")
        svg = genera_finestra(larghezza_mm, altezza_mm, numero_ante, apertura)
        st.markdown(svg, unsafe_allow_html=True)
