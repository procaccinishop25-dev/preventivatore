import streamlit as st
from services.supabase import supabase

st.set_page_config(page_title="Infissi", page_icon="🪟")

st.title("🪟 Gestione Infissi")

# Seleziona il progetto
progetti = supabase.table("progetti").select("id, indirizzo, citta, clienti(nome, cognome_azienda)").execute()

if not progetti.data:
    st.warning("Nessun progetto trovato. Crea prima un progetto.")
    st.page_link("pages/1_Nuovo_Progetto.py", label="Vai a Nuovo Progetto →", icon="📋")
else:
    opzioni = {
        f"{p['clienti']['nome']} {p['clienti']['cognome_azienda']} - {p['indirizzo']}, {p['citta']}": p['id']
        for p in progetti.data
    }
    scelta = st.selectbox("Seleziona progetto", list(opzioni.keys()))
    progetto_id = opzioni[scelta]

    st.divider()
    st.subheader("Aggiungi nuovo infisso")

    with st.form("nuovo_infisso"):
        tipologia = st.selectbox("Tipologia", ["Finestra", "Porta-finestra", "Portoncino", "Scorrevole", "Altro"])
        larghezza = st.number_input("Larghezza (cm)", min_value=1.0, step=1.0)
        altezza = st.number_input("Altezza (cm)", min_value=1.0, step=1.0)
        quantita = st.number_input("Quantità", min_value=1, step=1, value=1)
        note = st.text_area("Note")

        mq_anteprima = (larghezza / 100) * (altezza / 100)
        st.caption(f"Superficie calcolata: **{mq_anteprima:.2f} m²** per pezzo")

        submitted = st.form_submit_button("Aggiungi Infisso")

        if submitted:
            supabase.table("infissi").insert({
                "progetto_id": progetto_id,
                "tipologia": tipologia,
                "larghezza_cm": larghezza,
                "altezza_cm": altezza,
                "quantita": quantita,
                "note": note
            }).execute()
            st.success(f"Infisso aggiunto: {tipologia} {larghezza}x{altezza} cm")
            st.rerun()

    st.divider()
    st.subheader("Infissi di questo progetto")

    infissi = supabase.table("infissi").select("*").eq("progetto_id", progetto_id).execute()

    if infissi.data:
        for inf in infissi.data:
            st.write(f"**{inf['tipologia']}** — {inf['larghezza_cm']}x{inf['altezza_cm']} cm — {inf['mq']} m² — Qtà: {inf['quantita']}")
    else:
        st.info("Nessun infisso ancora inserito per questo progetto.")
