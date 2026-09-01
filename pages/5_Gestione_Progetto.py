import streamlit as st
from services.supabase import supabase
from services.theme import apply_custom_theme, badge
from services.pdf import genera_preventivo_rapido, trigger_download_automatico, dialog_dopo_generazione_preventivo
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
        percorso, bytes_data, {"content-type": tipo, "upsert": "true"}
    )
    url_pubblico = supabase.storage.from_("foto").get_public_url(percorso)
    supabase.table("infissi").update({"foto_url": url_pubblico}).eq("id", infisso_id).execute()


def elenco_foto_generali(cartella_progetto):
    file_esistenti = supabase.storage.from_("foto").list(cartella_progetto) or []
    generali = [f for f in file_esistenti if f["name"].startswith("generale_")]
    risultato = []
    for f in generali:
        url = supabase.storage.from_("foto").get_public_url(f"{cartella_progetto}/{f['name']}")
        risultato.append({"name": f["name"], "url": url})
    return risultato


def carica_foto_generale(bytes_data, tipo, nome_originale, cartella_progetto):
    import uuid
    nome_unico = f"generale_{uuid.uuid4().hex[:8]}_{nome_originale}"
    percorso = f"{cartella_progetto}/{nome_unico}"
    supabase.storage.from_("foto").upload(
        percorso, bytes_data, {"content-type": tipo, "upsert": "true"}
    )


def elimina_foto_generale(cartella_progetto, nome_file):
    supabase.storage.from_("foto").remove([f"{cartella_progetto}/{nome_file}"])


def salva_schizzo(image_data, cartella, nome_file, tabella, record_id):
    img = Image.fromarray(image_data.astype("uint8"), "RGBA")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    percorso = f"{cartella}/{slug(nome_file)}.png"
    supabase.storage.from_("schizzi").upload(
        percorso, buffer.getvalue(), {"content-type": "image/png", "upsert": "true"}
    )
    url_pubblico = supabase.storage.from_("schizzi").get_public_url(percorso)
    supabase.table(tabella).update({"schizzo_url": url_pubblico}).eq("id", record_id).execute()


def pannello_schizzo(key_prefix, cartella, nome_file, tabella, record_id, url_esistente):
    if isinstance(url_esistente, str) and url_esistente.startswith("http"):
        st.image(url_esistente, width=220, caption="Schizzo attuale")

    strumento = st.radio("Strumento", ["Penna", "Gomma", "Linea dritta"], horizontal=True, key=f"strumento_{key_prefix}")

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
        height=320,
        width=460,
        drawing_mode=modalita,
        display_toolbar=True,
        key=f"canvas_{key_prefix}"
    )

    if st.button("💾 Salva schizzo", key=f"salva_schizzo_{key_prefix}", use_container_width=True, type="primary"):
        if canvas_result.image_data is not None:
            salva_schizzo(canvas_result.image_data, cartella, nome_file, tabella, record_id)
            st.success("Schizzo salvato!")
            st.rerun()
        else:
            st.warning("Disegna qualcosa prima di salvare.")


@st.dialog("✏️ Schizzo generale del progetto", width="large")
def dialog_schizzo_generale(progetto_id, cartella_progetto, schizzo_url_esistente):
    st.caption("Es. pianta del cantiere — utile per orientarsi tra gli infissi.")
