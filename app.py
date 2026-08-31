import streamlit as st

st.set_page_config(
    page_title="Serramenti Demo",
    page_icon="🏠",
    layout="wide"
)

st.title("🏠 Gestionale Sopralluoghi e Preventivi")
st.write("Benvenuto! Da qui puoi gestire progetti e preventivi in pochi click.")

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.subheader("📋 Progetti")
    st.write("Crea un nuovo sopralluogo o consulta quelli salvati.")

with col2:
    st.subheader("💰 Preventivi")
    st.write("Genera un preventivo automatico partendo da un progetto.")
