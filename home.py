import streamlit as st
from services.supabase import supabase
from services.theme import apply_custom_theme, card_divider
from services.ui_components import page_toolbar, section_link_header, list_item


def format_euro(x):
    s = f"{x:,.0f}".replace(",", ".")
    return f"{s} €"


st.set_page_config(page_title="Panoramica", page_icon="🏠")
apply_custom_theme()

progetti = supabase.table("progetti").select(
    "id, indirizzo, citta, stato, created_at, clienti(nome, cognome_azienda)"
).order("created_at", desc=True).execute()

preventivi = supabase.table("preventivi").select("id, progetto_id, stato, totale_finale, created_at").execute()

num_progetti = len(progetti.data) if progetti.data else 0
num_preventivi = len(preventivi.data) if preventivi.data else 0
valore_attivo = sum((p.get('totale_finale') or 0) for p in (preventivi.data or []) if p.get('stato') in ('bozza', 'inviato'))
valore_accettato = sum((p.get('totale_finale') or 0) for p in (preventivi.data or []) if p.get('stato') == 'accettato')

ultimo_preventivo_per_progetto = {}
for pv in (preventivi.data or []):
    pid = pv['progetto_id']
    esistente = ultimo_preventivo_per_progetto.get(pid)
    if esistente is None or pv['created_at'] > esistente['created_at']:
        ultimo_preventivo_per_progetto[pid] = pv

page_toolbar("Panoramica", "Bentornato — ecco lo stato dei tuoi progetti e preventivi.")

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
    st.page_link("pages/1_Nuovo_Progetto.py", label="Nuovo progetto", icon=":material/note_add:", use_container_width=True)
with col_b:
    st.page_link("pages/3_Nuovo_Preventivo.py", label="Nuovo preventivo", icon=":material/payments:", use_container_width=True)

st.markdown("<div class='section-spacer'></div>", unsafe_allow_html=True)

section_link_header("Progetti recenti", "pages/2_Progetti.py")

if progetti.data:
    with st.container(border=True):
        recenti = progetti.data[:5]
        for idx, p in enumerate(recenti):
            nome = f"{p['clienti']['nome']} {p['clienti']['cognome_azienda']}"
            pv_recente = ultimo_preventivo_per_progetto.get(p['id'])

            sottotitolo = p['citta'] or ""
            if pv_recente:
                sottotitolo += f" · {format_euro(pv_recente.get('totale_finale') or 0)}"

            risultato = list_item(
                titolo=nome,
                sottotitolo=sottotitolo,
                stato_testo=(p.get('stato') or "—").capitalize(),
                stato_tipo="neutral",
                azione_primaria_label="Apri",
                azione_primaria_icon="arrow_forward",
                key_primaria=f"apri_home_{p['id']}",
            )

            if risultato["primaria"]:
                st.session_state["progetto_corrente_id"] = p['id']
                st.session_state["progetto_corrente_nome"] = nome
                st.switch_page("pages/5_Gestione_Progetto.py")

            if idx < len(recenti) - 1:
                st.markdown(card_divider(), unsafe_allow_html=True)
else:
    st.markdown(
        "<div class='empty-state'>"
        "<div class='empty-state-title'>Nessun progetto ancora</div>"
        "<div class='empty-state-description'>Crea il tuo primo progetto per iniziare a generare preventivi.</div>"
        "</div>",
        unsafe_allow_html=True
    )
    st.page_link("pages/1_Nuovo_Progetto.py", label="Nuovo progetto", icon=":material/note_add:")
