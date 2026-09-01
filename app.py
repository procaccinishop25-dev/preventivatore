import streamlit as st
from services.theme import apply_custom_theme

st.set_page_config(
    page_title="Serramenti Pro",
    page_icon="🏠",
    layout="wide"
)

apply_custom_theme()

pagina_home = st.Page("home.py", title="Home", icon="🏠", default=True)
pagina_nuovo_progetto = st.Page("pages/1_Nuovo_Progetto.py", title="Nuovo Progetto", icon="📋")
pagina_progetti = st.Page("pages/2_Progetti.py", title="Progetti", icon="📁")
pagina_nuovo_preventivo = st.Page("pages/3_Nuovo_Preventivo.py", title="Nuovo Preventivo", icon="💰")
pagina_preventivi = st.Page("pages/4_Preventivi.py", title="Preventivi", icon="📄")
pagina_gestione_progetto = st.Page("pages/5_Gestione_Progetto.py", title="Gestione Progetto", icon="🪟")
pagina_maggiorazioni = st.Page("pages/6_Maggiorazioni.py", title="Maggiorazioni", icon="⚙️")

navigazione = st.navigation(
    [pagina_home, pagina_nuovo_progetto, pagina_progetti, pagina_nuovo_preventivo, pagina_preventivi, pagina_gestione_progetto, pagina_maggiorazioni],
    position="hidden"
)

with st.sidebar:
    st.markdown(
        "<div class='sidebar-brand'><span class='sidebar-brand-icon'>🏠</span>"
        "<div><div class='sidebar-brand-title'>Serramenti Pro</div>"
        "<div class='sidebar-brand-subtitle'>Sopralluoghi & Preventivi</div></div></div>",
        unsafe_allow_html=True
    )
    st.page_link(pagina_home, label="Home", icon="🏠")
    st.page_link(pagina_nuovo_progetto, label="Nuovo Progetto", icon="📋")
    st.page_link(pagina_progetti, label="Progetti", icon="📁")
    st.markdown("<div class='sidebar-divider'></div>", unsafe_allow_html=True)
    st.page_link(pagina_nuovo_preventivo, label="Nuovo Preventivo", icon="💰")
    st.page_link(pagina_preventivi, label="Preventivi", icon="📄")
    st.markdown("<div class='sidebar-divider'></div>", unsafe_allow_html=True)
    st.page_link(pagina_maggiorazioni, label="Maggiorazioni", icon="⚙️")

navigazione.run()
