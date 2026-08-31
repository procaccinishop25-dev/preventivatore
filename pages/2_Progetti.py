import streamlit as st
from services.supabase import supabase


def slug(testo):
    import re
    testo = (testo or "").strip().replace(" ", "_")
    return re.sub(r"[^A-Za-z0-9_-]", "", testo)


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
                    st.session_state["progetto_creato_id"] = p['id']
                    st.session_state["progetto_creato_nome"] = nome_completo
                    st.switch_page("pages/1_Nuovo_Progetto.py")
            with col3:
                conferma_key = f"conferma_del_{p['id']}"
                if st.session_state.get(conferma_key):
                    if st.button("Conferma 🗑️", key=f"conferma_btn_{p['id']}", type="primary"):
                        cartella_progetto = slug(nome_completo)
                        file_esistenti = supabase.storage.from_("foto").list(cartella_progetto)
                        if file_esistenti:
                            percorsi = [f"{cartella_progetto}/{f['name']}" for f in file_esistenti]
                            supabase.storage.from_("foto").remove(percorsi)
                        supabase.table("progetti").delete().eq("id", p['id']).execute()
                        st.success("Progetto eliminato.")
                        st.rerun()
                    if st.button("Annulla", key=f"annulla_{p['id']}"):
                        st.session_state[conferma_key] = False
                        st.rerun()
                else:
                    if st.button("🗑️ Elimina", key=f"elimina_{p['id']}"):
                        st.session_state[conferma_key] = True
                        st.rerun()
