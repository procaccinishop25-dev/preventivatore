import streamlit as st
from services.supabase import supabase
from services.theme import apply_custom_theme, stato_badge, material_icon
from services.pdf import costruisci_contesto_pdf, genera_pdf_preventivo, trigger_download_automatico, dialog_dopo_generazione_preventivo, format_euro, slug


def formatta_data(data_iso):
    try:
        return "/".join(reversed(data_iso[:10].split("-")))
    except Exception:
        return data_iso


@st.dialog("Cambia stato")
def dialog_cambia_stato(preventivo_id, stato_attuale):
    stati_disponibili = ["bozza", "inviato", "accettato", "rifiutato"]
    indice = stati_disponibili.index(stato_attuale) if stato_attuale in stati_disponibili else 0
    nuovo_stato = st.radio("Nuovo stato", stati_disponibili, index=indice, format_func=lambda s: s.capitalize())
    if st.button("Salva", icon=":material/save:", type="primary", use_container_width=True):
        supabase.table("preventivi").update({"stato": nuovo_stato}).eq("id", preventivo_id).execute()
        st.rerun()


@st.dialog(":material/warning: Elimina preventivo")
def conferma_eliminazione_preventivo(preventivo_id, descrizione):
    st.warning(f"Stai per eliminare definitivamente **{descrizione}**. Questa azione non si può annullare.")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Sì, elimina", icon=":material/delete:", type="primary", use_container_width=True):
            supabase.table("preventivo_maggiorazioni").delete().eq("preventivo_id", preventivo_id).execute()
            supabase.table("preventivo_prezzi_tipologia").delete().eq("preventivo_id", preventivo_id).execute()
            supabase.table("preventivi").delete().eq("id", preventivo_id).execute()
            st.success("Preventivo eliminato.")
            st.rerun()
    with col2:
        if st.button("Annulla", use_container_width=True):
            st.rerun()


st.set_page_config(page_title="Preventivi", page_icon="📄")
apply_custom_theme()

st.markdown(
    f"<div class='page-header'><h1>{material_icon('description')} Preventivi</h1>"
    "<p>Raggruppati per progetto, con lo storico delle versioni.</p></div>",
    unsafe_allow_html=True
)

preventivi = supabase.table("preventivi").select(
    "*, progetti(indirizzo, citta, data_sopralluogo, operatore, clienti(nome, cognome_azienda, telefono, email))"
).execute()

if not preventivi.data:
    st.info("Nessun preventivo salvato ancora.")
    st.page_link("pages/3_Nuovo_Preventivo.py", label="Crea il primo preventivo →", icon=":material/payments:")
else:
    ricerca = st.text_input(":material/search: Cerca per cliente o città")

    gruppi = {}
    for pv in preventivi.data:
        pid = pv['progetto_id']
        gruppi.setdefault(pid, []).append(pv)

    for pid in gruppi:
        gruppi[pid].sort(key=lambda x: x['created_at'])

    gruppi_ordinati = sorted(gruppi.items(), key=lambda item: item[1][-1]['created_at'], reverse=True)

    almeno_uno_mostrato = False

    for progetto_id_gruppo, lista_pv in gruppi_ordinati:
        primo_pv = lista_pv[0]
        progetto_info = primo_pv.get("progetti") or {}
        clienti_info = progetto_info.get("clienti") or {}
        nome_completo = f"{clienti_info.get('nome', '')} {clienti_info.get('cognome_azienda', '')}".strip() or "Cliente sconosciuto"
        indirizzo = progetto_info.get("indirizzo", "")
        citta = progetto_info.get("citta", "")

        if ricerca and ricerca.lower() not in nome_completo.lower() and ricerca.lower() not in citta.lower():
            continue

        almeno_uno_mostrato = True

        st.markdown(f"### :material/folder: {nome_completo}")
        st.caption(f":material/location_on: {indirizzo}, {citta}
