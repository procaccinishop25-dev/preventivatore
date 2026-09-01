import streamlit as st
from services.supabase import supabase
from services.pdf import costruisci_contesto_pdf, genera_pdf_preventivo, format_euro, slug
from services.email import invia_email_preventivo
from datetime import datetime, timezone


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
                    if pv.get('email_inviata_a'):
                        st.caption(f"✉️ Inviato a {pv['email_inviata_a']}")
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
                                st.session_state[f"pdf_contesto_{pv['id']}"] = contesto

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

                    if f"pdf_pronto_{pv['id']}" in st.session_state:
                        st.divider()
                        st.write("**✉️ Invia via email**")

                        contesto_pv = st.session_state[f"pdf_contesto_{pv['id']}"]
                        email_default = clienti_info.get('email') or ""
                        destinatario = st.text_input("Email destinatario", value=email_default, key=f"email_dest_{pv['id']}")
                        oggetto = st.text_input("Oggetto", value=f"Preventivo n. {contesto_pv['numero_preventivo']} - {contesto_pv['azienda_nome']}", key=f"email_ogg_{pv['id']}")
                        corpo = st.text_area(
                            "Messaggio",
                            value=(
                                f"Gentile {nome_completo},\n\n"
                                f"In allegato il preventivo n. {contesto_pv['numero_preventivo']} del {contesto_pv['data']} "
                                f"per i lavori presso {indirizzo}, {citta}.\n\n"
                                f"Totale: {contesto_pv['totale_finale']}\n\n"
                                f"Restiamo a disposizione per qualsiasi chiarimento.\n\n"
                                f"Cordiali saluti,\n{contesto_pv['azienda_nome']}"
                            ),
                            height=180,
                            key=f"email_corpo_{pv['id']}"
                        )

                        if st.button("✉️ Invia email", key=f"invia_email_{pv['id']}"):
                            if not destinatario:
                                st.warning("Inserisci l'indirizzo email del destinatario.")
                            else:
                                try:
                                    with st.spinner("Invio email in corso..."):
                                        invia_email_preventivo(
                                            destinatario, oggetto, corpo,
                                            st.session_state[f"pdf_pronto_{pv['id']}"],
                                            f"preventivo_{slug(nome_completo)}.pdf"
                                        )
                                        supabase.table("preventivi").update({
                                            "email_inviata_a": destinatario,
                                            "email_inviata_il": datetime.now(timezone.utc).isoformat(),
                                            "stato": "inviato"
                                        }).eq("id", pv['id']).execute()
                                    st.success(f"Email inviata a {destinatario}!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Errore nell'invio: {e}")

        st.divider()

    if not almeno_uno_mostrato:
        st.info("Nessun preventivo corrisponde alla ricerca.")
