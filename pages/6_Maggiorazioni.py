import streamlit as st
from services.supabase import supabase

st.set_page_config(page_title="Aggiungi regole personalizzate", page_icon="⚙️")

st.title("⚙️ Aggiungi regole personalizzate")
st.caption("Gestisci qui le maggiorazioni standard selezionabili in ogni preventivo (es. Smontaggio, Piano alto...).")

st.subheader("➕ Aggiungi nuova maggiorazione")

with st.form("nuova_maggiorazione", clear_on_submit=True):
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        descrizione = st.text_input("Descrizione")
    with col2:
        importo = st.number_input("Importo", min_value=0.0, step=1.0)
    with col3:
        tipo = st.selectbox("Tipo", ["€ fisso", "€/m²", "%"])

    submitted = st.form_submit_button("Aggiungi")
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

st.divider()
st.subheader("📋 Maggiorazioni esistenti")

maggiorazioni = supabase.table("maggiorazioni").select("*").order("descrizione").execute()

if not maggiorazioni.data:
    st.info("Nessuna maggiorazione predefinita ancora.")
else:
    tipo_map = {"€ fisso": "fisso", "€/m²": "mq", "%": "percentuale"}
    tipo_ordine = ["fisso", "mq", "percentuale"]
    tipo_label = ["€ fisso", "€/m²", "%"]

    for m in maggiorazioni.data:
        with st.container(border=True):
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
                    if st.button("💾", key=f"salva_magg_{m['id']}"):
                        supabase.table("maggiorazioni").update({
                            "descrizione": nuova_descr,
                            "importo": nuovo_importo,
                            "tipo": tipo_map[nuovo_tipo_label]
                        }).eq("id", m['id']).execute()
                        st.success("Aggiornata!")
                        st.rerun()
                with col_elimina:
                    if
