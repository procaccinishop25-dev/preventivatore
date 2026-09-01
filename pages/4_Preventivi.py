import streamlit as st
from services.supabase import supabase
from services.theme import apply_custom_theme, stato_badge
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
    if st.button("Salva", type="primary", use_container_width=True):
        supabase.table("preventivi").update({"stato": nuovo_stato}).eq("id", preventivo_id).execute()
        st.rerun()


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


st.set_page_config(page_title="I Miei Preventivi", page_icon="📄")
apply_custom_theme()

st.markdown(
    "<div class='page-header'><h1>📄 I Miei Preventivi</h1>"
    "<p>Raggruppati per progetto, con lo storico delle versioni.</p></div>",
    unsafe_allow_html=True
)

preventivi = supabase.table("preventivi").select(
    "*, progetti(indirizzo, citta, data_sopralluogo, operatore, clienti(nome, cognome_azienda, telefono, email))"
).execute()

if not preventivi.data:
    st.info("Nessun preventivo salvato ancora.")
    st.page_link("pages/3_Nuovo_Preventivo.py", label="Crea il primo preventivo →", icon="💰")
else:
    ricerca = st.text_input("🔍 Cerca per cliente o città")

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

        st.markdown(f"### 📁 {nome_completo}")
        st.caption(f"📍 {indirizzo}, {citta} — {len(lista_pv)} preventivo/i")

        totale_versioni = len(lista_pv)

        for idx, pv in enumerate(reversed(lista_pv)):
            numero_versione = totale_versioni - idx

            with st.container(border=True):
                col1, col2, col3 = st.columns([3, 1.4, 1.6])
                with col1:
                    st.markdown(
                        f"<div style='font-weight:600; color:var(--color-title); font-size:0.98rem;'>Preventivo #{numero_versione}</div>"
                        f"<div style='color:var(--color-text-secondary); font-size:0.85rem;'>📅 {formatta_data(pv['created_at'])}</div>",
                        unsafe_allow_html=True
                    )
                    if pv.get('email_inviata_a'):
                        st.caption(f"✉️ Inviato a {pv['email_inviata_a']}")
                with col2:
                    st.markdown(
                        f"<div style='color:var(--color-text-secondary); font-size:0.82rem;'>Totale</div>"
                        f"<div style='color:var(--color-primary); font-weight:700; font-size:1.1rem;'>{format_euro(pv.get('totale_finale') or 0)}</div>",
                        unsafe_allow_html=True
                    )
                with col3:
                    st.markdown(stato_badge(pv['stato']), unsafe_allow_html=True)
                    if st.button("Cambia stato", key=f"stato_{pv['id']}", use_container_width=True):
                        dialog_cambia_stato(pv['id'], pv['stato'])

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
                        if st.button("📄 Genera PDF", key=f"genera_pdf_{pv['id']}", use_container_width=True, type="primary"):
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
                                pdf_buffer = genera_pdf_preventivo(contesto)
                            trigger_download_automatico(pdf_buffer.getvalue(), f"preventivo_{slug(nome_completo)}_v{numero_versione}.pdf")
                            dialog_dopo_generazione_preventivo(
                                pv['id'], pdf_buffer, contesto, clienti_info, nome_completo, indirizzo, citta
                            )
                    with col_elimina:
                        if st.button("🗑️ Elimina questo preventivo", key=f"elimina_pv_{pv['id']}", use_container_width=True):
                            conferma_eliminazione_preventivo(pv['id'], f"Preventivo #{numero_versione} di {nome_completo}")

        st.divider()

    if not almeno_uno_mostrato:
        st.info("Nessun preventivo corrisponde alla ricerca.")
