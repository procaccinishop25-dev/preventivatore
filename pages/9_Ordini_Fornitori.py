import streamlit as st
from services.theme import apply_custom_theme, material_icon

st.set_page_config(page_title="Ordini fornitori", page_icon="📦")
apply_custom_theme()

st.markdown(
    "<div class='page-header'><h1>Ordini fornitori</h1>"
    "<p>Genera ordini per materiale da inviare ai tuoi fornitori.</p></div>",
    unsafe_allow_html=True
)

st.markdown(
    f"<div class='empty-state'>"
    f"<div class='empty-state-icon'>{material_icon('local_shipping', 36)}</div>"
    f"<div class='empty-state-title'>Funzione in arrivo</div>"
    f"<div class='empty-state-description'>"
    f"Presto potrai selezionare un progetto, filtrare gli infissi per materiale "
    f"(Alluminio, PVC, Ferro) e generare un documento pronto da inviare ai fornitori, "
    f"senza prezzi — direttamente via email o WhatsApp."
    f"</div>"
    f"</div>",
    unsafe_allow_html=True
)
