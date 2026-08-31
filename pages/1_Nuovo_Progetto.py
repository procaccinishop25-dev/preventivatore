import streamlit as st
from services.supabase import supabase
from datetime import date

st.set_page_config(page_title="Nuovo Progetto", page_icon="📋")

st.title("📋 Nuovo Progetto")

# Se non abbiamo ancora un progetto creato in questa sessione, mostra il form iniziale
if "progetto_creato_id" not in st.session_state:

    with st.form("nuovo_progetto"):
        st.subheader("Dati Cliente")
        nome = st.text_input("Nome")
        cognome_azienda = st.text_input("Cognome / Azienda")
        telefono = st.text_input("Telefono")
        email = st.text_input("Email")

        st.subheader("Dati Cantiere")
        indirizzo = st.text_input("Indirizzo")
        citta = st.text_input("Città")
        note = st.text_area("Note cantiere")

        st.subheader("Sopralluogo")
        data_sopralluogo = st.date_input("Data", value=date.today())
        operatore = st.text_input("Operatore")
        note_generali = st.text_area("Note generali")

        submitted = st.form_submit_button("Salva Progetto e continua con gli infissi →")

        if submitted:
            if not nome or not cognome_azienda:
                st.error("Nome e Cognome/Azienda sono obbligatori.")
            else:
                cliente = supabase.table("clienti").insert({
                    "nome": nome,
                    "cognome_azienda": cognome_azienda,
                    "telefono": telefono,
                    "email": email
                }).execute()

                cliente_id = cliente.data[0]["id"]

                progetto = supabase.table("progetti").insert({
                    "cliente_id": cliente_id,
                    "indirizzo": indirizzo,
                    "citta": citta,
                    "note": note,
                    "data_sopralluogo": str(data_sopralluogo),
                    "operatore": operatore,
                    "note_generali": note_generali
                }).execute()

                st.session_state["progetto_creato_id"] = progetto.data[0]["id"]
                st.session_state["progetto_creato_nome"] = f"{nome} {cognome_azienda}"
                st.rerun()

# Se il progetto è stato creato, mostra subito la sezione infissi
else:
    progetto_id = st.session_state["progetto_creato_id"]
    nome_cliente = st.session_state["progetto_creato_nome"]

    st.success(f"✅ Progetto per **{nome_cliente}** salvato!")
    st.subheader("🪟 Ora aggiungi gli infissi")

    with st.form("nuovo_infisso"):
        tipologia = st.selectbox("Tipologia", ["Finestra", "Porta-finestra", "Portoncino", "Scorrevole", "Altro"])
        larghezza = st.number_input("Larghezza (cm)", min_value=1.0, step=1.0)
        altezza = st.number_input("Altezza (cm)", min_value=1.0, step=1.0)
        quantita = st.number_input("Quantità", min_value=1, step=1, value=1)
        note_inf = st.text_area("Note")

        mq_anteprima = (larghezza / 100) * (altezza / 100)
        st.caption(f"Superficie calcolata: **{mq_anteprima:.2f} m²** per pezzo")

        submitted_inf = st.form_submit_button("Aggiungi Infisso")

        if submitted_inf:
            supabase.table("infissi").insert({
                "progetto_id": progetto_id,
                "tipologia": tipologia,
                "larghezza_cm": larghezza,
                "altezza_cm": altezza,
                "quantita": quantita,
                "note": note_inf
            }).execute()
            st.success(f"Infisso aggiunto: {tipologia} {larghezza}x{altezza} cm")
            st.rerun()

    st.divider()

    infissi = supabase.table("infissi").select("*").eq("progetto_id", progetto_id).execute()

    if infissi.data:
        totale_mq = sum(i['mq'] * i['quantita'] for i in infissi.data)
        st.caption(f"Infissi inseriti: {len(infissi.data)} — Superficie totale: **{totale_mq:.2f} m²**")

        for inf in infissi.data:
            with st.expander(f"{inf['tipologia']} — {inf['larghezza_cm']}x{inf['altezza_cm']} cm — {inf['mq']} m² — Qtà: {inf['quantita']}"):
                col1, col2 = st.columns(2)
                with col1:
                    nuova_larghezza = st.number_input("Larghezza (cm)", value=float(inf['larghezza_cm']), key=f"larg_{inf['id']}")
                    nuova_altezza = st.number_input("Altezza (cm)", value=float(inf['altezza_cm']), key=f"alt_{inf['id']}")
                with col2:
                    nuova_quantita = st.number_input("Quantità", value=int(inf['quantita']), min_value=1, key=f"qta_{inf['id']}")
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
                        st.rerun()

                st.divider()
                st.write("📷 Foto")

                if inf.get('foto_url'):
                    st.image(inf['foto_url'], width=200)

                foto_caricata = st.file_uploader("Carica foto", type=["jpg", "jpeg", "png"], key=f"foto_{inf['id']}")

                if foto_caricata is not None:
                    if st.button("⬆️ Salva foto", key=f"salva_foto_{inf['id']}"):
                        percorso = f"{progetto_id}/{inf['id']}_{foto_caricata.name}"
                        supabase.storage.from_("foto").upload(
                            percorso,
                            foto_caricata.getvalue(),
                            {"content-type": foto_caricata.type, "upsert": "true"}
                        )
                        url_pubblico = supabase.storage.from_("foto").get_public_url(percorso)
                        supabase.table("infissi").update({"foto_url": url_pubblico}).eq("id", inf['id']).execute()
                        st.success("Foto caricata!")
                        st.rerun()
    else:
        st.info("Nessun infisso ancora inserito.")

    st.divider()

    col_fine, col_nuovo = st.columns(2)
    with col_fine:
        if st.button("✅ Ho finito, vai a I Miei Progetti"):
            del st.session_state["progetto_creato_id"]
            del st.session_state["progetto_creato_nome"]
            st.switch_page("pages/2_Progetti.py")
    with col_nuovo:
        if st.button("➕ Crea un altro progetto"):
            del st.session_state["progetto_creato_id"]
            del st.session_state["progetto_creato_nome"]
            st.rerun()
