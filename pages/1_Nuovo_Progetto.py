import streamlit as st
from services.supabase import supabase
from datetime import date
import re


def slug(testo):
    """Rende una stringa sicura per essere usata come nome di cartella/file."""
    testo = (testo or "").strip().replace(" ", "_")
    return re.sub(r"[^A-Za-z0-9_-]", "", testo)


def carica_foto(file_obj, cartella, nome_infisso, infisso_id):
    """Carica un file (da uploader o camera) su Storage e aggiorna l'infisso."""
    nome_file = getattr(file_obj, "name", "foto.jpg")
    tipo_file = getattr(file_obj, "type", "image/jpeg")
    percorso = f"{cartella}/{slug(nome_infisso)}_{nome_file}"

    supabase.storage.from_("foto").upload(
        percorso,
        file_obj.getvalue(),
        {"content-type": tipo_file, "upsert": "true"}
    )
    url_pubblico = supabase.storage.from_("foto").get_public_url(percorso)
    supabase.table("infissi").update({"foto_url": url_pubblico}).eq("id", infisso_id).execute()


st.set_page_config(page_title="Nuovo Progetto", page_icon="📋")

st.title("📋 Nuovo Progetto")

if "progetto_creato_id" not in st.session_state:

    with st.form("nuovo_progetto", clear_on_submit=True):
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

else:
    progetto_id = st.session_state["progetto_creato_id"]
    nome_cliente = st.session_state["progetto_creato_nome"]
    cartella_progetto = slug(nome_cliente)

    st.success(f"✅ Progetto per **{nome_cliente}** salvato!")
    st.subheader("🪟 Ora aggiungi gli infissi")

    with st.form("nuovo_infisso", clear_on_submit=True):
        tipologia = st.selectbox("Tipologia", ["Finestra", "Porta-finestra", "Portoncino", "Scorrevole", "Altro"])
        larghezza = st.number_input("Larghezza (cm)", min_value=1.0, step=1.0)
        altezza = st.number_input("Altezza (cm)", min_value=1.0, step=1.0)
        quantita = st.number_input("Quantità", min_value=1, step=1, value=1)
        note_inf = st.text_area("Note")

        mq_anteprima = (larghezza / 100) * (altezza / 100)
        st.caption(f"Superficie calcolata: **{mq_anteprima:.2f} m²** per pezzo")

        st.write("📷 Foto (opzionale)")
        metodo_foto = st.radio(
            "Come vuoi aggiungere la foto?",
            ["Nessuna", "Carica da file", "Scatta foto"],
            horizontal=True,
            key="metodo_foto_nuovo"
        )
        foto_input = None
        if metodo_foto == "Carica da file":
            foto_input = st.file_uploader("Carica foto", type=["jpg", "jpeg", "png"], key="foto_upload_nuovo")
        elif metodo_foto == "Scatta foto":
            foto_input = st.camera_input("Scatta una foto", key="foto_camera_nuovo")

        submitted_inf = st.form_submit_button("Aggiungi Infisso")

        if submitted_inf:
            esistenti = supabase.table("infissi").select("id").eq("progetto_id", progetto_id).eq("tipologia", tipologia).execute()
            numero_iniziale = len(esistenti.data) + 1

            id_primo_infisso = None
            nome_primo_infisso = None

            for i in range(int(quantita)):
                numero = numero_iniziale + i
                nome_infisso = f"{tipologia.replace('-', ' ')} {numero:02d}"
                nuovo = supabase.table("infissi").insert({
                    "progetto_id": progetto_id,
                    "tipologia": tipologia,
                    "numero_infisso": numero,
                    "nome": nome_infisso,
                    "larghezza_cm": larghezza,
                    "altezza_cm": altezza,
                    "quantita": 1,
                    "note": note_inf
                }).execute()

                if i == 0:
                    id_primo_infisso = nuovo.data[0]["id"]
                    nome_primo_infisso = nome_infisso

            if foto_input is not None and id_primo_infisso:
                carica_foto(foto_input, cartella_progetto, nome_primo_infisso, id_primo_infisso)

            if int(quantita) > 1 and foto_input is not None:
                st.info(f"Foto associata solo a **{nome_primo_infisso}**. Per gli altri, apri il singolo infisso qui sotto e aggiungi la foto.")

            st.success(f"{int(quantita)} infisso/i aggiunto/i: {tipologia}")
            st.rerun()

    st.divider()

    infissi = supabase.table("infissi").select("*").eq("progetto_id", progetto_id).order("numero_infisso").execute()

    if infissi.data:
        totale_mq = sum(i['mq'] * i['quantita'] for i in infissi.data)
        st.caption(f"Infissi inseriti: {len(infissi.data)} — Superficie totale: **{totale_mq:.2f} m²**")

        for inf in infissi.data:
            nome_visualizzato = inf.get('nome') or f"{inf['tipologia']} {inf.get('numero_infisso', '')}"

            with st.expander(f"{nome_visualizzato} — {inf['larghezza_cm']}x{inf['altezza_cm']} cm — {inf['mq']} m²"):
                col1, col2 = st.columns(2)
                with col1:
                    nuova_larghezza = st.number_input("Larghezza (cm)", value=float(inf['larghezza_cm']), key=f"larg_{inf['id']}")
                    nuova_altezza = st.number_input("Altezza (cm)", value=float(inf['altezza_cm']), key=f"alt_{inf['id']}")
                with col2:
                    nuove_note = st.text_area("Note", value=inf['note'] or "", key=f"note_{inf['id']}")

                col_salva, col_elimina = st.columns(2)
                with col_salva:
                    if st.button("💾 Salva modifiche", key=f"salva_{inf['id']}"):
                        supabase.table("infissi").update({
                            "larghezza_cm": nuova_larghezza,
                            "altezza_cm": nuova_altezza,
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

                metodo_foto_inf = st.radio(
                    "Come vuoi aggiungere/cambiare la foto?",
                    ["Carica da file", "Scatta foto"],
                    horizontal=True,
                    key=f"metodo_foto_{inf['id']}"
                )

                if metodo_foto_inf == "Carica da file":
                    foto_caricata = st.file_uploader("Carica foto", type=["jpg", "jpeg", "png"], key=f"foto_{inf['id']}")
                else:
                    foto_caricata = st.camera_input("Scatta una foto", key=f"foto_cam_{inf['id']}")

                if foto_caricata is not None:
                    if st.button("⬆️ Salva foto", key=f"salva_foto_{inf['id']}"):
                        carica_foto(foto_caricata, cartella_progetto, nome_visualizzato, inf['id'])
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
