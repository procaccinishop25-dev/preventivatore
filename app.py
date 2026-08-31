import streamlit as st
from services.supabase import supabase

st.title("Serramenti Demo")

st.write("Test connessione a Supabase...")

try:
    response = supabase.table("clienti").select("*").execute()
    st.success("Connessione riuscita! ✅")
    st.write(f"Clienti trovati: {len(response.data)}")
except Exception as e:
    st.error(f"Errore di connessione: {e}")

st.divider()
st.subheader("Test inserimento cliente")

if st.button("Aggiungi cliente di prova"):
    nuovo = supabase.table("clienti").insert({
        "nome": "Mario",
        "cognome_azienda": "Rossi",
        "telefono": "3331234567",
        "email": "mario.rossi@test.it"
    }).execute()
    st.success("Cliente inserito!")

st.divider()
st.subheader("Lista clienti")
clienti = supabase.table("clienti").select("*").execute()
st.dataframe(clienti.data)
