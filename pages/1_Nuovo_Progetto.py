import streamlit as st
from services.supabase import supabase

st.set_page_config(page_title="Infissi", page_icon="🪟")

st.title("🪟 Gestione Infissi")

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
    st.subheader(f"Infissi di questo progetto ({opzioni_count if False else ''})")

    infissi = supabase.table("infissi").select("*").eq("progetto_id", progetto_id).order("numero_infisso").execute()

    if infissi.data:
        totale_mq = sum(i['mq'] * i['quantita'] for i in infissi.data)
        st.caption(f"Totale infissi: {len(infissi.data)} — Superficie totale: **{totale_mq:.2f} m²**")

        for inf in infissi.data:
            with st.expander(f"{inf['tipologia']} — {inf['larghezza_cm']}x{inf['altezza_cm']} cm — {inf['mq']} m² — Qtà: {inf['quantita']}"):
                col1, col2 = st.columns(2)

                with col1:
                    nuova_larghezza = st.number_input("Larghezza (cm)", value=float(inf['larghezza_cm']), key=f"larg_{inf['id']}")
                    nuova_altezza = st.number_input("Altezza (cm)", value=float(inf['altezza_cm']), key=f"alt_{inf['id']}")
                    nuova_quantita = st.number_input("Quantità", value=int(inf['quantita']), min_value=1, key=f"qta_{inf['id']}")

                with col2:
                    nuove_note = st.text_area("Note", value=inf['note'] or "", key=f"note_{inf['id']}")

                col_salva, col_elimina = st.columns(2)

                with col_salva:
                    if st.button("💾 Salva modifiche", key=f"salva_{inf['id']}"):
                        supabase.table("infissi").update({
                            "larghezza_cm": nuova_larghezza,
                            "altezza_cm": nuova_altezza,
                            "quantita": nuova_quantita,
                            "note": nuove_note
                        }).eq("id", inf['id']).execute()
                        st.success("Modificato!")
                        st.rerun()

                with col_elimina:
                    if st.button("🗑️ Elimina infisso", key=f"elimina_{inf['id']}"):
                        supabase.table("infissi").delete().eq("id", inf['id']).execute()
                        st.warning("Infisso eliminato.")
                        st.rerun()
    else:
        st.info("Nessun infisso ancora inserito per questo progetto.")
