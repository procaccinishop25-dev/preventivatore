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
pagina_maggiorazioni = st.Page("pages/6_Maggiorazioni.py", title="Regole prezzo personalizzate", icon="⚙️")
pagina_catalogo = st.Page("pages/7_Catalogo.py", title="Catalogo", icon="🛒")
pagina_editor_schizzo = st.Page("pages/8_Editor_Schizzo.py", title="Editor Schizzo", icon="✏️")
pagina_ordini_fornitori = st.Page("pages/9_Ordini_Fornitori.py", title="Ordini fornitori", icon="📦")

navigazione = st.navigation(
    [pagina_home, pagina_nuovo_progetto, pagina_progetti, pagina_nuovo_preventivo, pagina_preventivi,
     pagina_gestione_progetto, pagina_maggiorazioni, pagina_catalogo, pagina_editor_schizzo, pagina_ordini_fornitori],
    position="hidden"
)


def sidebar_section_label(testo):
    st.markdown(f"<div class='sidebar-section-label'>{testo}</div>", unsafe_allow_html=True)


with st.sidebar:
    st.markdown(
        "<div class='sidebar-brand'>"
        "<span class='sidebar-brand-icon'>S</span>"
        "<div><div class='sidebar-brand-title'>Serramenti Pro</div></div>"
        "</div>",
        unsafe_allow_html=True
    )

    st.page_link(pagina_home, label="Home", icon="🏠")

    # "Nuovo Progetto" è l'azione primaria dell'app: resa visivamente evidente
    st.markdown("<div class='sidebar-cta-primary'>", unsafe_allow_html=True)
    st.page_link(pagina_nuovo_progetto, label="Nuovo progetto", icon="➕")
    st.markdown("</div>", unsafe_allow_html=True)

    st.page_link(pagina_progetti, label="Progetti", icon="📁")
    st.page_link(pagina_preventivi, label="Preventivi", icon="📄")
    st.page_link(pagina_ordini_fornitori, label="Ordini fornitori", icon="📦")

    st.markdown("<div class='sidebar-divider'></div>", unsafe_allow_html=True)

    sidebar_section_label("Impostazioni")
    st.page_link(pagina_catalogo, label="Catalogo", icon="🛒")
    st.page_link(pagina_maggiorazioni, label="Regole prezzo personalizzate", icon="⚙️")

    # "Gestione Progetto", "Nuovo Preventivo" ed "Editor Schizzo" restano raggiungibili
    # solo tramite i pulsanti dell'app, non compaiono nel menu.

    st.markdown(
        "<div class='sidebar-user'>"
        "<span class='sidebar-user-avatar'>MI</span>"
        "<span>Martino Infissi</span>"
        "</div>",
        unsafe_allow_html=True
    )

navigazione.run()
