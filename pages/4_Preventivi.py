import streamlit as st
from services.supabase import supabase


def format_euro(x):
    s = f"{x:,.2f}"
    s = s.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{s} €"


def formatta_data(data_iso):
    try:
        return data_iso[:10][::-1].replace("-", "/", 2)[::-1] if False else "/".join(reversed(data_iso[:10].split("-")))
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


st.set_page_config(page_title="Preventivi", page_icon="📄")

st.title("📄 Preventivi")

preventivi = supabase.table("preventivi").select(
    "*, progetti(indirizzo, citta, clienti(nome, cognome_azienda))"
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

                if st.button("🗑️ Elimina questo preventivo", key=f"elimina_pv_{pv['id']}"):
                    conferma_eliminazione_preventivo(pv['id'], nome_completo)
