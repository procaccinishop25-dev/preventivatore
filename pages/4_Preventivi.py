import streamlit as st
from services.supabase import supabase
from services.pdf import costruisci_contesto_pdf, genera_pdf_preventivo, format_euro, slug


def formatta_data(data_iso):
    try:
        return "/".join(reversed(data_iso[:10].split("-")))
    except Exception:
        return data_iso


@st.dialog("⚠️ Elimina preventivo")
def conferma_eliminazione_preventivo(preventivo_id, descrizione):
    st.warning(f"Stai per eliminare definitivamente **{descrizione}**. Questa azione non si può annullare.")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Sì, elimina", type="primary", use_container_width=True):
            supabase.table("preventivo_maggiorazioni").delete().eq("preventivo_id", preventivo_id).execute()
            supabase.table("preventivo_prezzi_tipologia").delete().eq("preventivo_id", preventivo_id).execute()
            supabase.table("preventivi").delete().eq("id", preventivo_id).execute()
            st.success("Preventivo eliminato.")
            st.rerun()
    with col2:
        if st.button("Annulla", use_container_width=True):
            st.rerun()


st.set_page_config(page_title="Preventivi", page_icon="📄")

st.title("📄 Preventivi")

preventivi = supabase.table("preventivi").select(
    "*, progetti(indirizzo, citta, data_sopralluogo, operatore, clienti(nome, cognome_azienda, telefono, email))"
).execute()

if not preventivi.data:
    st.info("Nessun preventivo salvato ancora.")
    st.page_link("pages/3_Nuovo_Preventivo.py", label="Crea il primo preventivo →", icon="💰")
else:
    ricerca = st.text_input("🔍 Cerca per cliente o città")

    stati_disponibili = ["bozza", "inviato", "accettato", "rifiutato"]

    # Raggruppa i preventivi per progetto
    gruppi = {}
    for pv in preventivi.data:
        pid = pv['progetto_id']
        gruppi.setdefault(pid, []).append(pv)

    # Ordina ogni gruppo per data crescente, per numerare correttamente in ordine di creazione
    for pid in gruppi:
        gruppi[pid].sort(key=lambda x: x['created_at'])

    # Ordina i progetti mettendo prima quelli con l'attività più recente
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

        st.markdown(f"## 📁 {nome_completo}")
        st.caption(f"📍 {indirizzo}, {citta} — {len(lista_pv)} preventivo/i")

        totale_versioni = len(lista_pv)

        for idx, pv in enumerate(reversed(lista_pv)):
            numero_versione = totale_versioni - idx

            with st.container(border=True):
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.subheader(f"Preventivo #{numero_versione}")
                    st.caption(f"📅 {formatta_data(pv['created_at'])}")
                with col2:
                    st.metric("Totale finale", format_euro(pv.get('totale_finale') or 0))
                with col3:
                    indice_stato = stati_disponibili.index(pv['stato']) if pv.get('stato') in stati_disponibili else 0
                    nuovo_stato = st.selectbox("Stato", stati_disponibili, index=indice_stato, key=f"stato_{pv['id']}")
                    if nuovo_stato != pv['stato']:
                        supabase.table("preventivi").update({"stato": nuovo_stato}).eq("id", pv['id']).execute()
                        st.rerun()

                with st.expander("Vedi dettaglio"):
                    prezzi = supabase.table("preventivo_prezzi_tipologia").select("*").eq("preventivo_id", pv['id']).execute()
                    mappa_prezzi = {p['tipologia']: p['prezzo_mq'] for p in prezzi.data} if prezzi.data else {}
                    if prezzi.data:
                        st.write("**Prezzi per tipologia:**")
                        for p in prezzi.data:
                            st.caption(f"• {p['tipologia']}: {format_euro(p['prezzo_mq'])}/m²")

                    maggiorazioni_pv = supabase.table("preventivo_maggiorazioni").select(
                        "*, maggiorazioni(descrizione, importo, tipo), infissi(nome)"
                    ).eq("preventivo_id", pv['id']).execute()

                    maggiorazioni_righe_pdf = []
                    if maggiorazioni_pv.data:
                        st.write("**Maggiorazioni applicate:**")
                        for mg in maggiorazioni_pv.data:
                            descr = mg.get('maggiorazioni', {}).get('descrizione') if mg.get('maggiorazioni') else mg.get('descrizione_personalizzata')
                            infisso_nome = mg.get('infissi', {}).get('nome') if mg.get('infissi') else None
                            importo_magg = mg.get('maggiorazioni', {}).get('importo') if mg.get('maggiorazioni') else mg.get('importo_personalizzato')
                            riferimento = f"su {infisso_nome}" if infisso_nome else "su tutti gli infissi"
                            st.caption(f"• {descr} ({riferimento})")
                            maggiorazioni_righe_pdf.append({
                                "descrizione": f"{descr} ({riferimento})" if infisso_nome else descr,
                                "importo": format_euro(importo_magg or 0)
                            })

                    st.write(f"**Totale base:** {format_euro(pv.get('totale_base') or 0)}")
                    if pv.get('sconti'):
                        st.write(f"**Sconto:** {format_euro(pv['sconti'])}")
                    st.write(f"**Totale finale:** {format_euro(pv.get('totale_finale') or 0)}")

                    col_pdf, col_elimina = st.columns(2)
                    with col_pdf:
                        if st.button("📄 Genera PDF", key=f"genera_pdf_{pv['id']}"):
                            with st.spinner("Generazione PDF in corso..."):
                                progetto_per_pdf = {**progetto_info, "id": pv['progetto_id']}
                                contesto = costruisci_contesto_pdf(
                                    numero_preventivo=pv['id'][:8].upper(),
                                    data=formatta_data(pv['created_at']),
                                    progetto=progetto_per_pdf,
                                    cliente=clienti_info,
                                    prezzi_tipologia=mappa_prezzi,
                                    maggiorazioni_righe=maggiorazioni_righe_pdf,
                                    totale_base=pv.get('totale_base') or 0,
                                    sconto=pv.get('sconti') or 0,
                                    totale_finale=pv.get('totale_finale') or 0
                                )
                                st.session_state[f"pdf_pronto_{pv['id']}"] = genera_pdf_preventivo(contesto)

                        if f"pdf_pronto_{pv['id']}" in st.session_state:
                            st.download_button(
                                "📥 Scarica PDF",
                                data=st.session_state[f"pdf_pronto_{pv['id']}"],
                                file_name=f"preventivo_{slug(nome_completo)}_v{numero_versione}.pdf",
                                mime="application/pdf",
                                key=f"download_pdf_{pv['id']}"
                            )
                    with col_elimina:
                        if st.button("🗑️ Elimina questo preventivo", key=f"elimina_pv_{pv['id']}"):
                            conferma_eliminazione_preventivo(pv['id'], f"Preventivo #{numero_versione} di {nome_completo}")

        st.divider()

    if not almeno_uno_mostrato:
        st.info("Nessun preventivo corrisponde alla ricerca.")
