import streamlit as st
from services.supabase import supabase
import re


def slug(testo):
    testo = (testo or "").strip().replace(" ", "_")
    return re.sub(r"[^A-Za-z0-9_-]", "", testo)


@st.dialog("⚠️ Elimina progetto")
def conferma_eliminazione(progetto_id, cliente_id, nome_completo):
    st.warning(
        f"Stai per eliminare definitivamente il progetto di **{nome_completo}**, "
        f"con tutti i suoi infissi, foto e i dati del cliente. Questa azione non si può annullare."
    )
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Sì, elimina", type="primary", use_container_width=True):
            cartella_progetto = slug(nome_completo)

            # 1. Elimina le foto dallo Storage
            file_esistenti = supabase.storage.from_("foto").list(cartella_progetto)
            if file_esistenti:
                percorsi = [f"{cartella_progetto}/{f['name']}" for f in file_esistenti]
                supabase.storage.from_("foto").remove(percorsi)

            # 2. Elimina esplicitamente gli infissi collegati
            supabase.table("infissi").delete().eq("progetto_id", progetto_id).execute()

            # 3. Elimina eventuali preventivi collegati
            preventivi_collegati = supabase.table("preventivi").select("id").eq("progetto_id", progetto_id).execute()
            for prev in preventivi_collegati.data:
                supabase.table("preventivo_maggiorazioni").delete().eq("preventivo_id", prev["id"]).execute()
            supabase.table("preventivi").delete().eq("progetto_id", progetto_id).execute()

            # 4. Elimina il progetto
            supabase.table("progetti").delete().eq("id", progetto_id).execute()

            # 5. Elimina il cliente collegato (creato apposta per questo progetto)
            if cliente_id:
                supabase.table("clienti").delete().eq("id", cliente_id).execute()

            st.success("Progetto eliminato completamente.")
            st.rerun()
    with col2:
        if st.button("Annulla", use_container_width=True):
            st.rerun()


st.set_page_config(page_title="I Miei Progetti", page_icon="📁")

st.title("📁 I Miei Progetti")

progetti = supabase.table("progetti").select("*, clienti(nome, cognome_azienda, telefono, email)").order("created_at", desc=True).execute()

if not progetti.data:
    st.info("Nessun progetto salvato ancora.")
    st.page_link("pages/1_Nuovo_Progetto.py", label="Crea il primo progetto →", icon="📋")
else:
    ricerca = st.text_input("🔍 Cerca per cliente o città")

    for p in progetti.data:
        nome_completo = f"{p['clienti']['nome']} {p['clienti']['cognome_azienda']}"

        if ricerca and ricerca.lower() not in nome_completo.lower() and ricerca.lower() not in (p['citta'] or "").lower():
            continue

        infissi = supabase.table("infissi").select("id, mq, quantita").eq("progetto_id", p['id']).execute()
        num_infissi = len(infissi.data)
        mq_totali = sum(i['mq'] * i['quantita'] for i in infissi.data) if infissi.data else 0

        with st.container(border=True):
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.subheader(nome_completo)
                st.caption(f"📍 {p['indirizzo']}, {p['citta']}")
                st.caption(f"🪟 {num_infissi} infissi — {mq_totali:.2f} m² totali — Stato: {p['stato']}")
            with col2:
                if st.button("Apri →", key=f"apri_{p['id']}"):
                    st.session_state["progetto_corrente_id"] = p['id']
                    st.session_state["progetto_corrente_nome"] = nome_completo
                    st.switch_page("pages/5_Gestione_Progetto.py")
            with col3:
                if st.button("🗑️ Elimina", key=f"elimina_{p['id']}"):
                    conferma_eliminazione(p['id'], p['cliente_id'], nome_completo)
