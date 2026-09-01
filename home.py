import streamlit as st
from services.supabase import supabase


def format_euro(x):
    s = f"{x:,.0f}".replace(",", ".")
    return f"{s} €"


progetti = supabase.table("progetti").select(
    "id, indirizzo, citta, clienti(nome, cognome_azienda)"
).order("created_at", desc=True).execute()

preventivi = supabase.table("preventivi").select("id, stato, totale_finale").execute()

num_progetti = len(progetti.data) if progetti.data else 0
num_preventivi = len(preventivi.data) if preventivi.data else 0
valore_attivo = sum((p.get('totale_finale') or 0) for p in (preventivi.data or []) if p.get('stato') in ('bozza', 'inviato'))
valore_accettato = sum((p.get('totale_finale') or 0) for p in (preventivi.data or []) if p.get('stato') == 'accettato')

st.markdown(
    "<div class='page-header'><h1>Panoramica</h1><p>Bentornato — ecco lo stato dei tuoi progetti e preventivi.</p></div>",
    unsafe_allow_html=True
)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Progetti totali", num_progetti)
with col2:
    st.metric("Preventivi totali", num_preventivi)
with col3:
    st.metric("Valore in trattativa", format_euro(valore_attivo))
with col4:
    st.metric("Valore accettato", format_euro(valore_accettato))

st.markdown("<div class='section-spacer'></div>", unsafe_allow_html=True)
st.subheader("Azioni rapide")

col_a, col_b = st.columns(2)
with col_a:
    with st.container(border=True):
        st.markdown("### 📋 Nuovo Progetto")
        st.write("Avvia un nuovo sopralluogo: dati cliente, cantiere e infissi.")
        st.page_link("pages/1_Nuovo_Progetto.py", label="Inizia sopralluogo →", icon="📋")
with col_b:
    with st.container(border=True):
        st.markdown("### 💰 Nuovo Preventivo")
        st.write("Genera un preventivo a partire da un progetto esistente.")
        st.page_link("pages/3_Nuovo_Preventivo.py", label="Crea preventivo →", icon="💰")

st.markdown("<div class='section-spacer'></div>", unsafe_allow_html=True)
st.subheader("Progetti recenti")

if progetti.data:
    for p in progetti.data[:5]:
        nome = f"{p['clienti']['nome']} {p['clienti']['cognome_azienda']}"
        with st.container(border=True):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"**{nome}**")
                st.caption(f"📍 {p['indirizzo']}, {p['citta']}")
            with col2:
                if st.button("Apri →", key=f"apri_home_{p['id']}"):
                    st.session_state["progetto_corrente_id"] = p['id']
                    st.session_state["progetto_corrente_nome"] = nome
                    st.switch_page("pages/5_Gestione_Progetto.py")
else:
    st.info("Nessun progetto ancora. Crea il primo per iniziare.")
    st.page_link("pages/1_Nuovo_Progetto.py", label="Crea il primo progetto →", icon="📋")
