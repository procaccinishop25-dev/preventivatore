import streamlit as st
from services.supabase import supabase
from services.theme import apply_custom_theme
from services.pdf import genera_preventivo_rapido, trigger_download_automatico, dialog_dopo_generazione_preventivo
import re


def slug(testo):
    testo = (testo or "").strip().replace(" ", "_")
    return re.sub(r"[^A-Za-z0-9_-]", "", testo)


@st.dialog("⚠️ Elimina progetto")
def conferma_eliminazione(progetto_id, nome_completo):
    st.warning(
        f"Stai per eliminare definitivamente il progetto di **{nome_completo}**, "
        f"con tutti i suoi infissi e le foto caricate. Questa azione non si può annullare."
    )
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Sì, elimina", type="primary", use_container_width=True):
            cartella_progetto = slug(nome_completo)

            file_esistenti = supabase.storage.from_("foto").list(cartella_progetto)
            if file_esistenti:
                percorsi = [f"{cartella_progetto}/{f['name']}" for f in file_esistenti]
                supabase.storage.from_("foto").remove(percorsi)

            supabase.table("infissi").delete().eq("progetto_id", progetto_id).execute()

            preventivi_collegati = supabase.table("preventivi").select("id").eq("progetto_id", progetto_id).execute()
            for prev in preventivi_collegati.data:
                supabase.table("preventivo_maggiorazioni").delete().eq("preventivo_id", prev["id"]).execute()
            supabase.table("preventivi").delete().eq("progetto_id", progetto_id).execute()

            supabase.table("progetti").delete().eq("id", progetto_id).execute()

            st.success("Progetto eliminato completamente.")
            st.rerun()
    with col2:
        if st.button("Annulla", use_container_width=True):
            st.rerun()


st.set_page_config(page_title="I Miei Progetti", page_icon="📁")
apply_custom_theme()

st.markdown(
    "<div class='page-header'><h1>📁 I Miei Progetti</h1>"
    "<p>Riprendi un progetto o generane subito il preventivo.</p></div>",
    unsafe_allow_html=True
)

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
            col1, col2, col3, col4 = st.columns([3, 1.3, 1.5, 1])
            with col1:
                st.subheader(nome_completo)
                st.caption(f"📍 {p['indirizzo']}, {p['citta']}")
                st.caption(f"🪟 {num_infissi} infissi — {mq_totali:.2f} m² totali — Stato: {p['stato']}")
            with col2:
                if st.button("Apri →", key=f"apri_{p['id']}", use_container_width=True):
                    st.session_state["progetto_corrente_id"] = p['id']
                    st.session_state["progetto_corrente_nome"] = nome_completo
                    st.switch_page("pages/5_Gestione_Progetto.py")
            with col3:
                if st.button("💰 Preventivo", key=f"genera_{p['id']}", use_container_width=True):
                    if num_infissi == 0:
                        st.warning("Aggiungi almeno un infisso prima di generare il preventivo.")
                    else:
                        with st.spinner("Generazione preventivo e PDF in corso..."):
                            preventivo_id, pdf_buffer, contesto = genera_preventivo_rapido(p['id'], p, p['clienti'])
                        trigger_download_automatico(pdf_buffer.getvalue(), f"preventivo_{slug(nome_completo)}.pdf")
                        dialog_dopo_generazione_preventivo(
                            preventivo_id, pdf_buffer, contesto, p['clienti'], nome_completo,
                            p['indirizzo'], p['citta']
                        )
            with col4:
                if st.button("🗑️", key=f"elimina_{p['id']}", use_container_width=True, help="Elimina"):
                    conferma_eliminazione(p['id'], nome_completo)
