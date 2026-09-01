import streamlit as st
from services.supabase import supabase
from services.pdf import genera_pdf_preventivo
import re


def slug(testo):
    testo = (testo or "").strip().replace(" ", "_")
    return re.sub(r"[^A-Za-z0-9_-]", "", testo)


def format_euro(x):
    s = f"{x:,.2f}"
    s = s.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{s} €"


def formatta_data(data_iso):
    try:
        return "/".join(reversed(data_iso[:10].split("-")))
    except Exception:
        return data_iso


@st.dialog("⚠️ Elimina preventivo")
def conferma_eliminazione_preventivo(preventivo_id, descrizione):
    st.warning(f"Stai per eliminare definitivamente il preventivo per **{descrizione}**. Questa azione non si può annullare.")
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


def costruisci_contesto_pdf(pv, progetto_info, clienti_info):
    prezzi = supabase.table("preventivo_prezzi_tipologia").select("*").eq("preventivo_id", pv['id']).execute()
    mappa_prezzi = {p['tipologia']: p['prezzo_mq'] for p in prezzi.data} if prezzi.data else {}

    infissi_db = supabase.table("infissi").select("*").eq("progetto_id", pv['progetto_id']).order("numero_infisso").execute()

    infissi_ctx = []
    superficie_totale = 0.0
    for inf in infissi_db.data or []:
        prezzo = mappa_prezzi.get(inf['tipologia'], 0)
        mq_riga = inf['mq'] * inf['quantita']
        subtotale = mq_riga * prezzo
        superficie_totale += mq_riga
        infissi_ctx.append({
            "nome": inf.get('nome') or f"{inf['tipologia']} {inf.get('numero_infisso', '')}",
            "misure": f"{inf['larghezza_cm']}x{inf['altezza_cm']} cm",
            "mq": f"{mq_riga:.2f}",
            "prezzo_mq": format_euro(prezzo),
            "subtotale": format_euro(subtotale),
            "foto_url": inf.get('foto_url'),
            "schizzo_url": inf.get('schizzo_url')
        })

    maggiorazioni_pv = supabase.table("preventivo_maggiorazioni").select(
        "*, maggiorazioni(descrizione, importo, tipo), infissi(nome)"
    ).eq("preventivo_id", pv['id']).execute()

    maggiorazioni_ctx = []
    if maggiorazioni_pv.data:
        for mg in maggiorazioni_pv.data:
            descr = mg.get('maggiorazioni', {}).get('descrizione') if mg.get('maggiorazioni') else mg.get('descrizione_personalizzata')
            infisso_nome = mg.get('infissi', {}).get('nome') if mg.get('infissi') else None
            riferimento = f" (su {infisso_nome})" if infisso_nome else ""
            importo_magg = mg.get('maggiorazioni', {}).get('importo') if mg.get('maggiorazioni') else mg.get('importo_personalizzato')
            maggiorazioni_ctx.append({
                "descrizione": f"{descr}{riferimento}",
                "importo": format_euro(importo_magg or 0)
            })

    return {
        "azienda_nome": "La Tua Azienda Serramenti",
        "azienda_contatti": "Via Esempio 1, 00000 Città — Tel: 000 0000000 — email@esempio.it",
        "numero_preventivo": pv['id'][:8].upper(),
        "data": formatta_data(pv['created_at']),
        "cliente_nome": f"{clienti_info.get('nome', '')} {clienti_info.get('cognome_azienda', '')}",
        "cliente_telefono": clienti_info.get('telefono'),
        "cliente_email": clienti_info.get('email'),
        "progetto_indirizzo": progetto_info.get('indirizzo', ''),
        "progetto_citta": progetto_info.get('citta', ''),
        "data_sopralluogo": progetto_info.get('data_sopralluogo'),
        "operatore": progetto_info.get('operatore'),
        "numero_infissi": len(infissi_ctx),
        "superficie_totale": f"{superficie_totale:.2f}",
        "infissi": infissi_ctx,
        "totale_base": format_euro(pv.get('totale_base') or 0),
        "maggiorazioni": maggiorazioni_ctx,
        "sconto": format_euro(pv.get('sconti') or 0),
        "totale_finale": format_euro(pv.get('totale_finale') or 0),
    }


st.set_page_config(page_title="Preventivi", page_icon="📄")

st.title("📄 Preventivi")

preventivi = supabase.table("preventivi").select(
    "*, progetti(indirizzo, citta, data_sopralluogo, operatore, clienti(nome, cognome_azienda, telefono, email))"
).order("created_at", desc=True).execute()

if not preventivi.data:
    st.info("Nessun preventivo salvato ancora.")
    st.page_link("pages/3_Nuovo_Preventivo.py", label="Crea il primo preventivo →", icon="💰")
else:
    ricerca = st.text_input("🔍 Cerca per cliente o città")

    stati_disponibili = ["bozza", "inviato", "accettato", "rifiutato"]

    for pv in preventivi.data:
        progetto_info = pv.get("progetti") or {}
        clienti_info = progetto_info.get("clienti") or {}
        nome_completo = f"{clienti_info.get('nome', '')} {clienti_info.get('cognome_azienda', '')}".strip() or "Cliente sconosciuto"
        indirizzo = progetto_info.get("indirizzo", "")
        citta = progetto_info.get("citta", "")

        if ricerca and ricerca.lower() not in nome_completo.lower() and ricerca.lower() not in citta.lower():
            continue

        with st.container(border=True):
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.subheader(nome_completo)
                st.caption(f"📍 {indirizzo}, {citta}")
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
                if prezzi.data:
                    st.write("**Prezzi per tipologia:**")
                    for p in prezzi.data:
                        st.caption(f"• {p['tipologia']}: {format_euro(p['prezzo_mq'])}/m²")

                maggiorazioni_pv = supabase.table("preventivo_maggiorazioni").select(
                    "*, maggiorazioni(descrizione, importo, tipo), infissi(nome)"
                ).eq("preventivo_id", pv['id']).execute()

                if maggiorazioni_pv.data:
                    st.write("**Maggiorazioni applicate:**")
                    for mg in maggiorazioni_pv.data:
                        descr = mg.get('maggiorazioni', {}).get('descrizione') if mg.get('maggiorazioni') else mg.get('descrizione_personalizzata')
                        infisso_nome = mg.get('infissi', {}).get('nome') if mg.get('infissi') else None
                        riferimento = f"su {infisso_nome}" if infisso_nome else "su tutti gli infissi"
                        st.caption(f"• {descr} ({riferimento})")

                st.write(f"**Totale base:** {format_euro(pv.get('totale_base') or 0)}")
                if pv.get('sconti'):
                    st.write(f"**Sconto:** {format_euro(pv['sconti'])}")
                st.write(f"**Totale finale:** {format_euro(pv.get('totale_finale') or 0)}")

                col_pdf, col_elimina = st.columns(2)
                with col_pdf:
                    if st.button("📄 Genera PDF", key=f"genera_pdf_{pv['id']}"):
                        with st.spinner("Generazione PDF in corso..."):
                            contesto = costruisci_contesto_pdf(pv, progetto_info, clienti_info)
                            pdf_buffer = genera_pdf_preventivo(contesto)
                            st.session_state[f"pdf_pronto_{pv['id']}"] = pdf_buffer

                    if f"pdf_pronto_{pv['id']}" in st.session_state:
                        st.download_button(
                            "📥 Scarica PDF",
                            data=st.session_state[f"pdf_pronto_{pv['id']}"],
                            file_name=f"preventivo_{slug(nome_completo)}.pdf",
                            mime="application/pdf",
                            key=f"download_pdf_{pv['id']}"
                        )
                with col_elimina:
                    if st.button("🗑️ Elimina questo preventivo", key=f"elimina_pv_{pv['id']}"):
                        conferma_eliminazione_preventivo(pv['id'], nome_completo)
