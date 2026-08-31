import streamlit as st
from services.supabase import supabase
from streamlit_drawable_canvas import st_canvas
from PIL import Image
import io
import re


def slug(testo):
    testo = (testo or "").strip().replace(" ", "_")
    return re.sub(r"[^A-Za-z0-9_-]", "", testo)


def carica_foto_bytes(bytes_data, tipo, nome_file_originale, cartella, nome_infisso, infisso_id):
    percorso = f"{cartella}/{slug(nome_infisso)}_{nome_file_originale}"
    supabase.storage.from_("foto").upload(
        percorso,
        bytes_data,
        {"content-type": tipo, "upsert": "true"}
    )
    url_pubblico = supabase.storage.from_("foto").get_public_url(percorso)
    supabase.table("infissi").update({"foto_url": url_pubblico}).eq("id", infisso_id).execute()


def salva_schizzo(image_data, cartella, nome_file, tabella, record_id):
    img = Image.fromarray(image_data.astype("uint8"), "RGBA")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    percorso = f"{cartella}/{slug(nome_file)}.png"
    supabase.storage.from_("schizzi").upload(
        percorso,
        buffer.getvalue(),
        {"content-type": "image/png", "upsert": "true"}
    )
    url_pubblico = supabase.storage.from_("schizzi").get_public_url(percorso)
    supabase.table(tabella).update({"schizzo_url": url_pubblico}).eq("id", record_id).execute()


def pannello_schizzo(key_prefix, cartella, nome_file, tabella, record_id, url_esistente):
    if isinstance(url_esistente, str) and url_esistente.startswith("http"):
        st.image(url_esistente, width=250, caption="Schizzo attuale")

    strumento = st.radio(
        "Strumento",
        ["Penna", "Gomma", "Linea dritta"],
        horizontal=True,
        key=f"strumento_{key_prefix}"
    )

    if strumento == "Penna":
        spessore = st.slider("Spessore tratto", 1, 15, 3, key=f"spessore_penna_{key_prefix}")
        colore = "#000000"
        modalita = "freedraw"
    elif strumento == "Gomma":
        spessore = st.slider("Spessore gomma", 5, 60, 25, key=f"spessore_gomma_{key_prefix}")
        colore = "#FFFFFF"
        modalita = "freedraw"
    else:
        spessore = st.slider("Spessore linea", 1, 15, 3, key=f"spessore_linea_{key_prefix}")
        colore = "#000000"
        modalita = "line"

    if strumento == "Linea dritta":
        st.caption("Trascina da un punto all'altro: la linea uscirà sempre perfettamente dritta.")

    canvas_result = st_canvas(
        fill_color="rgba(255, 255, 255, 0)",
        stroke_width=spessore,
        stroke_color=colore,
        background_color="#FFFFFF",
        height=350,
        width=500,
        drawing_mode=modalita,
        display_toolbar=True,
        key=f"canvas_{key_prefix}"
    )

    if st.button("💾 Salva schizzo", key=f"salva_schizzo_{key_prefix}"):
        if canvas_result.image_data is not None:
            salva_schizzo(canvas_result.image_data, cartella, nome_file, tabella, record_id)
            st.success("Schizzo salvato!")
            st.rerun()
        else:
            st.warning("Disegna qualcosa prima di salvare.")


st.set_page_config(page_title="Gestione Progetto", page_icon="🪟", layout="wide")

st.title("🪟 Gestione Progetto")

if "progetto_corrente_id" not in st.session_state:
    st.warning("Nessun progetto selezionato.")
    st.page_link("pages/2_Progetti.py", label="Vai a I Miei Progetti →", icon="📁")
    st.page_link("pages/1_Nuovo_Progetto.py", label="Oppure crea un nuovo progetto →", icon="📋")
else:
    progetto_id = st.session_state["progetto_corrente_id"]
    nome_cliente = st.session_state["progetto_corrente_nome"]
    cartella_progetto = slug(nome_cliente)

    if "foto_key_counter" not in st.session_state:
        st.session_state["foto_key_counter"] = 0
    if "foto_catturate" not in st.session_state:
        st.session_state["foto_catturate"] = []
    if "camera_shot_counter" not in st.session_state:
        st.session_state["camera_shot_counter"] = 0
    if "fotocamera_aperta" not in st.session_state:
        st.session_state["fotocamera_aperta"] = True

    st.success(f"✅ Progetto: **{nome_cliente}**")

    # --- Schizzo generale del progetto (checkbox invece di expander, per evitare il bug del canvas a larghezza 0) ---
    st.write("✏️ Schizzo generale del progetto (es. pianta del cantiere)")
    mostra_schizzo_generale = st.checkbox("Mostra/Modifica schizzo generale", key="mostra_schizzo_generale")
    if mostra_schizzo_generale:
        progetto_info = supabase.table("progetti").select("schizzo_url").eq("id", progetto_id).execute()
        schizzo_esistente = progetto_info.data[0].get("schizzo_url") if progetto_info.data else None
        pannello_schizzo("progetto", cartella_progetto, "schizzo_generale", "progetti", progetto_id, schizzo_esistente)

    st.divider()
    st.subheader("Aggiungi infissi")

    contatore = st.session_state["foto_key_counter"]

    st.write("📷 Foto (opzionale) — se aggiungi più finestre uguali, carica/scatta una foto per ciascuna: verranno assegnate in ordine")
    metodo_foto = st.radio(
        "Come vuoi aggiungere le foto?",
        ["Nessuna", "Carica da file", "Scatta foto"],
        horizontal=True,
        key=f"metodo_foto_nuovo_{contatore}"
    )

    foto_multiple_da_file = []
    if metodo_foto == "Carica da file":
        foto_multiple_da_file = st.file_uploader(
            "Carica una o più foto (in ordine: 1ª foto → 1° infisso, 2ª foto → 2° infisso, ecc.)",
            type=["jpg", "jpeg", "png"],
            accept_multiple_files=True,
            key=f"foto_upload_nuovo_{contatore}"
        ) or []

    elif metodo_foto == "Scatta foto":
        st.caption(f"📸 Foto scattate finora: **{len(st.session_state['foto_catturate'])}**")
        if st.session_state["foto_catturate"]:
            cols_preview = st.columns(min(len(st.session_state["foto_catturate"]), 6))
            for idx, foto in enumerate(st.session_state["foto_catturate"]):
                with cols_preview[idx % len(cols_preview)]:
                    st.image(foto["bytes"], width=80)

        if st.session_state["fotocamera_aperta"]:
            scatto = st.camera_input("Scatta una foto", key=f"foto_cam_multi_{st.session_state['camera_shot_counter']}")

            col_agg, col_chiudi = st.columns(2)
            with col_agg:
                if scatto is not None:
                    if st.button("➕ Aggiungi questa foto alla lista"):
                        st.session_state["foto_catturate"].append({
                            "bytes": scatto.getvalue(),
                            "type": scatto.type,
                            "name": scatto.name
                        })
                        st.session_state["camera_shot_counter"] += 1
                        st.rerun()
            with col_chiudi:
                if st.button("✅ Ho finito, chiudi fotocamera"):
                    st.session_state["fotocamera_aperta"] = False
                    st.rerun()
        else:
            st.info("Fotocamera chiusa.")
            col_riapri, col_svuota = st.columns(2)
            with col_riapri:
                if st.button("📷 Riapri fotocamera"):
                    st.session_state["fotocamera_aperta"] = True
                    st.rerun()
            with col_svuota:
                if st.session_state["foto_catturate"]:
                    if st.button("🗑️ Svuota foto scattate"):
                        st.session_state["foto_catturate"] = []
                        st.rerun()

    with st.form("nuovo_infisso", clear_on_submit=True):
        tipologia = st.selectbox("Tipologia", ["Finestra", "Porta-finestra", "Portoncino", "Scorrevole", "Altro"])
        larghezza = st.number_input("Larghezza (cm)", min_value=1.0, step=1.0)
        altezza = st.number_input("Altezza (cm)", min_value=1.0, step=1.0)
        quantita = st.number_input("Quantità", min_value=1, step=1, value=1)
        note_inf = st.text_area("Note")

        mq_anteprima = (larghezza / 100) * (altezza / 100)
        st.caption(f"Superficie calcolata: **{mq_anteprima:.2f} m²** per pezzo")

        submitted_inf = st.form_submit_button("Aggiungi Infisso")

        if submitted_inf:
            lista_foto = []
            if metodo_foto == "Carica da file" and foto_multiple_da_file:
                for f in foto_multiple_da_file:
                    lista_foto.append({"bytes": f.getvalue(), "type": f.type, "name": f.name})
            elif metodo_foto == "Scatta foto" and st.session_state["foto_catturate"]:
                lista_foto = st.session_state["foto_catturate"]

            esistenti = supabase.table("infissi").select("id").eq("progetto_id", progetto_id).eq("tipologia", tipologia).execute()
            numero_iniziale = len(esistenti.data) + 1

            id_infissi_creati = []

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
                id_infissi_creati.append((nuovo.data[0]["id"], nome_infisso))

            for idx, (infisso_id, nome_infisso) in enumerate(id_infissi_creati):
                if idx < len(lista_foto):
                    foto = lista_foto[idx]
                    carica_foto_bytes(foto["bytes"], foto["type"], foto["name"], cartella_progetto, nome_infisso, infisso_id)

            if lista_foto and len(lista_foto) < int(quantita):
                st.info(f"Assegnate {len(lista_foto)} foto su {int(quantita)} infissi. Le restanti finestre sono senza foto, aggiungile singolarmente qui sotto.")
            elif lista_foto and len(lista_foto) > int(quantita):
                st.info(f"Hai caricato {len(lista_foto)} foto ma creato solo {int(quantita)} infissi: le foto in eccesso sono state ignorate.")

            st.session_state["foto_key_counter"] += 1
            st.session_state["foto_catturate"] = []
            st.session_state["fotocamera_aperta"] = True

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
                        carica_foto_bytes(foto_caricata.getvalue(), foto_caricata.type, foto_caricata.name, cartella_progetto, nome_visualizzato, inf['id'])
                        st.success("Foto caricata!")
                        st.rerun()

                st.divider()
                st.write("✏️ Schizzo")

                mostra_schizzo = st.checkbox("Aggiungi/modifica schizzo", key=f"mostra_schizzo_{inf['id']}")
                if mostra_schizzo:
                    pannello_schizzo(
                        f"infisso_{inf['id']}",
                        cartella_progetto,
                        nome_visualizzato,
                        "infissi",
                        inf['id'],
                        inf.get('schizzo_url')
                    )
    else:
        st.info("Nessun infisso ancora inserito.")

    st.divider()

    col_fine, col_nuovo = st.columns(2)
    with col_fine:
        if st.button("✅ Ho finito, vai a I Miei Progetti"):
            del st.session_state["progetto_corrente_id"]
            del st.session_state["progetto_corrente_nome"]
            st.switch_page("pages/2_Progetti.py")
    with col_nuovo:
        if st.button("➕ Crea un altro progetto"):
            del st.session_state["progetto_corrente_id"]
            del st.session_state["progetto_corrente_nome"]
            st.switch_page("pages/1_Nuovo_Progetto.py")
