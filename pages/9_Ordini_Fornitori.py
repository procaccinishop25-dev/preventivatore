import streamlit as st
from services.theme import apply_custom_theme

st.set_page_config(page_title="Ordini fornitori", page_icon="📦")
apply_custom_theme()

st.markdown(
    "<div class='page-header'><h1>📦 Ordini fornitori</h1>"
    "<p>Genera ordini per materiale da inviare ai tuoi fornitori.</p></div>",
    unsafe_allow_html=True
)

st.markdown(
    "<div class='empty-state'>"
    "<div class='empty-state-icon'>📦</div>"
    "<div class='empty-state-title'>Funzione in arrivo</div>"
    "<div class='empty-state-description'>"
    "Presto potrai selezionare un progetto, filtrare gli infissi per materiale "
    "(Alluminio, PVC, Ferro) e generare un documento pronto da inviare ai fornitori, "
    "senza prezzi — direttamente via email o WhatsApp."
    "</div>"
    "</div>",
    unsafe_allow_html=True
)
