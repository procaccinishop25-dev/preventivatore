import streamlit as st
from services.supabase import supabase
from datetime import date

st.set_page_config(page_title="Nuovo Progetto", page_icon="📋")

st.title("📋 Nuovo Progetto")

with st.form("nuovo_progetto", clear_on_submit=True):
    st.subheader("Dati Cliente")
    nome = st.text_input("Nome")
    cognome_azienda = st.text_input("Cognome / Azienda")
    telefono = st.text_input("Telefono")
    email = st.text_input("Email")

    st.subheader("Dati Cantiere")
    indirizzo = st.text_input("Indirizzo")
    citta = st.text_input("Città")
    note = st.text_area("Note cantiere")

    st.subheader("Sopralluogo")
    data_sopralluogo = st.date_input("Data", value=date.today())
    operatore = st.text_input("Operatore")
    note_generali = st.text_area("Note generali")

    submitted = st.form_submit_button("Salva Progetto e continua con gli infissi →")

    if submitted:
        if not nome or not cognome_azienda:
            st.error("Nome e Cognome/Azienda sono obbligatori.")
        else:
            cliente = supabase.table("clienti").insert({
                "nome": nome,
                "cognome_azienda": cognome_azienda,
                "telefono": telefono,
                "email": email
            }).execute()

            cliente_id = cliente.data[0]["id"]

            progetto = supabase.table("progetti").insert({
                "cliente_id": cliente_id,
                "indirizzo": indirizzo,
                "citta": citta,
                "note": note,
                "data_sopralluogo": str(data_sopralluogo),
                "operatore": operatore,
                "note_generali": note_generali
            }).execute()

            st.session_state["progetto_corrente_id"] = progetto.data[0]["id"]
            st.session_state["progetto_corrente_nome"] = f"{nome} {cognome_azienda}"
            st.switch_page("pages/5_Gestione_Progetto.py")
