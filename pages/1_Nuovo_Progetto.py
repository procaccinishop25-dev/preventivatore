import streamlit as st
from services.supabase import supabase
from services.theme import apply_custom_theme
from datetime import date

st.set_page_config(page_title="Nuovo Progetto", page_icon="📋")
apply_custom_theme()

st.markdown(
    "<div class='page-header'><h1>📋 Nuovo Progetto</h1>"
    "<p>Registra un nuovo sopralluogo: cliente, cantiere e dettagli del lavoro.</p></div>",
    unsafe_allow_html=True
)

with st.form("nuovo_progetto", clear_on_submit=True):

    with st.container(border=True):
        st.markdown("#### 👤 Dati Cliente")
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome")
        with col2:
            cognome_azienda = st.text_input("Cognome / Azienda")
        col3, col4 = st.columns(2)
        with col3:
            telefono = st.text_input("Telefono")
        with col4:
            email = st.text_input("Email")

    with st.container(border=True):
        st.markdown("#### 📍 Dati Cantiere")
        indirizzo = st.text_input("Indirizzo")
        citta = st.text_input("Città")
        note = st.text_area("Note cantiere", height=80)

    with st.container(border=True):
        st.markdown("#### 🗓️ Sopralluogo")
        col5, col6 = st.columns(2)
        with col5:
            data_sopralluogo = st.date_input("Data", value=date.today())
        with col6:
            operatore = st.text_input("Operatore")
        note_generali = st.text_area("Note generali", height=80)

    submitted = st.form_submit_button(
        "Salva Progetto e continua con gli infissi →",
        use_container_width=True,
        type="primary"
    )

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
