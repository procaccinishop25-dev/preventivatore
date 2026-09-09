import streamlit as st
from services.supabase import supabase
from services.theme import apply_custom_theme, card_divider
from services.ui_components import page_toolbar

st.set_page_config(page_title="Regole prezzo personalizzate", page_icon="⚙️")
apply_custom_theme()

page_toolbar(
    "Regole prezzo personalizzate",
    "Gestisci qui le maggiorazioni standard selezionabili in ogni preventivo (es. Smontaggio, Piano alto...)."
)

with st.container(border=True):
    st.markdown("#### Aggiungi nuova regola")

    with st.form("nuova_maggiorazione", clear_on_submit=True):
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            descrizione = st.text_input("Descrizione")
        with col2:
            importo = st.number_input("Importo", min_value=0.0, step=1.0)
        with col3:
            tipo = st.selectbox("Tipo", ["€ fisso", "€/m²", "%"])

        submitted = st.form_submit_button("Aggiungi", icon=":material/check:", type="primary")
        if submitted:
            if descrizione:
                tipo_map = {"€ fisso": "fisso", "€/m²": "mq", "%": "percentuale"}
                supabase.table("maggiorazioni").insert({
                    "descrizione": descrizione,
                    "importo": importo,
                    "tipo": tipo_map[tipo]
                }).execute()
                st.success("Maggiorazione aggiunta!")
                st.rerun()
            else:
                st.warning("Inserisci una descrizione.")

st.markdown("<div class='section-spacer'></div>", unsafe_allow_html=True)
st.markdown("### Regole esistenti")

maggiorazioni = supabase.table("maggiorazioni").select("*").order("descrizione").execute()

if not maggiorazioni.data:
    st.markdown(
        "<div class='empty-state'>"
        "<div class='empty-state-title'>Nessuna regola ancora</div>"
        "<div class='empty-state-description'>Aggiungi la prima maggiorazione predefinita qui sopra.</div>"
        "</div>",
        unsafe_allow_html=True
    )
else:
    tipo_map = {"€ fisso": "fisso", "€/m²": "mq", "%": "percentuale"}
    tipo_ordine = ["fisso", "mq", "percentuale"]
    tipo_label = ["€ fisso", "€/m²", "%"]

    with st.container(border=True):
        for idx, m in enumerate(maggiorazioni.data):
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            with col1:
                nuova_descr = st.text_input("Descrizione", value=m['descrizione'], key=f"descr_{m['id']}")
            with col2:
                nuovo_importo = st.number_input("Importo", value=float(m['importo']), min_value=0.0, step=1.0, key=f"importo_{m['id']}")
            with col3:
                indice_tipo = tipo_ordine.index(m['tipo']) if m['tipo'] in tipo_ordine else 0
                nuovo_tipo_label = st.selectbox("Tipo", tipo_label, index=indice_tipo, key=f"tipo_{m['id']}")
            with col4:
                st.write("")
                col_salva, col_elimina = st.columns(2)
                with col_salva:
                    if st.button("", icon=":material/save:", key=f"salva_magg_{m['id']}", help="Salva", use_container_width=True):
                        supabase.table("maggiorazioni").update({
                            "descrizione": nuova_descr,
                            "importo": nuovo_importo,
                            "tipo": tipo_map[nuovo_tipo_label]
                        }).eq("id", m['id']).execute()
                        st.success("Aggiornata!")
                        st.rerun()
                with col_elimina:
                    st.markdown("<div class='action-danger'>", unsafe_allow_html=True)
                    if st.button("", icon=":material/delete:", key=f"elimina_magg_{m['id']}", help="Elimina", use_container_width=True):
                        supabase.table("maggiorazioni").delete().eq("id", m['id']).execute()
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)

            if idx < len(maggiorazioni.data) - 1:
                st.markdown(card_divider(), unsafe_allow_html=True)
