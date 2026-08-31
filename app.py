import streamlit as st

st.set_page_config(
    page_title="Serramenti Demo",
    page_icon="🏠",
    layout="wide"
)

pagina_home = st.Page("home.py", title="Home", icon="🏠", default=True)
pagina_nuovo_progetto = st.Page("pages/1_Nuovo_Progetto.py", title="Nuovo Progetto", icon="📋")
pagina_progetti = st.Page("pages/2_Progetti.py", title="Progetti", icon="📁")
pagina_nuovo_preventivo = st.Page("pages/3_Nuovo_Preventivo.py", title="Nuovo Preventivo", icon="💰")
pagina_preventivi = st.Page("pages/4_Preventivi.py", title="Preventivi", icon="📄")
pagina_gestione_progetto = st.Page("pages/5_Gestione_Progetto.py", title="Gestione Progetto", icon="🪟")

# Tutte le pagine devono essere elencate qui per essere raggiungibili,
# ma disattiviamo il menu automatico (position="hidden") per costruirne uno su misura
navigazione = st.navigation(
    [pagina_home, pagina_nuovo_progetto, pagina_progetti, pagina_nuovo_preventivo, pagina_preventivi, pagina_gestione_progetto],
    position="hidden"
)

with st.sidebar:
    st.page_link(pagina_home, label="Home", icon="🏠")
    st.page_link(pagina_nuovo_progetto, label="Nuovo Progetto", icon="📋")
    st.page_link(pagina_progetti, label="Progetti", icon="📁")
    st.page_link(pagina_nuovo_preventivo, label="Nuovo Preventivo", icon="💰")
    st.page_link(pagina_preventivi, label="Preventivi", icon="📄")
    # "Gestione Progetto" NON è nel menu: resta raggiungibile solo tramite i pulsanti dell'app

navigazione.run()
