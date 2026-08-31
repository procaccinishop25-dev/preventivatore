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
