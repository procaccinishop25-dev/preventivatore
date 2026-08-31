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
    if url_esistente:
        st.image(url_esistente, width=250, caption="Schizzo attuale")

    col1, col2 = st.columns(2)
    with col1:
        strumento = st.radio("Strumento", ["Penna", "Gomma"], horizontal=True, key=f"strumento_{key_prefix}")
    with col2:
        spessore = st.slider("Spessore", 1, 25, 3, key=f"spessore_{key_prefix}")

    colore = "#000000" if strumento == "Penna" else "#FFFFFF"

    canvas_result = st_canvas(
        fill_color="rgba(255, 255, 255, 0)",
        stroke_width=spessore,
        stroke_color=colore,
        background_color="#FFFFFF",
        height=350,
        width=500,
        drawing_mode="freedraw",
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

    # --- Schizzo generale del progetto ---
    with st.expander("✏️ Schizzo generale del progetto (es. pianta del cantiere)"):
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
