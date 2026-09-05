import streamlit as st
from services.supabase import supabase
from services.theme import apply_custom_theme
from components.drawing_editor import drawing_editor
import base64
import json
import re
import urllib.request


def slug(testo):
    testo = (testo or "").strip().replace(" ", "_")
    return re.sub(r"[^A-Za-z0-9_-]", "", testo)


def scarica_json(url):
    try:
        with urllib.request.urlopen(url, timeout=10) as risposta:
            return json.loads(risposta.read().decode("utf-8"))
    except Exception:
        return None


def salva_png_e_stato(png_base64, state_json_str, cartella, nome_file, tabella, record_id):
    _, dati_b64 = png_base64.split(",", 1)
    png_bytes = base64.b64decode(dati_b64)

    percorso_png = f"{cartella}/{slug(nome_file)}.png"
    supabase.storage.from_("schizzi").upload(
        percorso_png, png_bytes, {"content-type": "image/png", "upsert": "true"}
    )
    url_png = supabase.storage.from_("schizzi").get_public_url(percorso_png)

    percorso_json = f"{cartella}/{slug(nome_file)}.json"
    supabase.storage.from_("schizzi").upload(
        percorso_json, state_json_str.encode("utf-8"), {"content-type": "application/json", "upsert": "true"}
    )
    url_json = supabase.storage.from_("schizzi").get_public_url(percorso_json)

    supabase.table(tabella).update({
        "schizzo_url": url_png,
        "schizzo_stato_url": url_json
    }).eq("id", record_id).execute()


st.set_page_config(page_title="Editor Schizzo", page_icon="✏️", layout="wide")
apply_custom_theme()

target = st.session_state.get("editor_schizzo_target")

if not target:
    st.warning("Nessuno schizzo da modificare selezionato.")
    if st.button("← Torna a Gestione Progetto"):
        st.switch_page("pages/5_Gestione_Progetto.py")
else:
    record = supabase.table(target['tabella']).select("schizzo_stato_url").eq("id", target['record_id']).execute()
    schizzo_stato_url = record.data[0].get('schizzo_stato_url') if record.data else None

    stato_iniziale = None
    if schizzo_stato_url:
        stato_iniziale = scarica_json(schizzo_stato_url)

    if "editor_ultimo_save_id" not in st.session_state:
        st.session_state["editor_ultimo_save_id"] = None

    risultato = drawing_editor(
        title=target['nome_file'],
        background_image_url=target.get('url_esistente') if not stato_iniziale else None,
        initial_state=stato_iniziale,
        key=f"drawing_editor_{target['record_id']}"
    )

    if risultato is not None and risultato.get("save_id") != st.session_state["editor_ultimo_save_id"]:
        st.session_state["editor_ultimo_save_id"] = risultato.get("save_id")

        if risultato.get("event") == "save":
            with st.spinner("Salvataggio in corso..."):
                salva_png_e_stato(
                    risultato["png_base64"], risultato["state_json"],
                    target['cartella'], target['nome_file'], target['tabella'], target['record_id']
                )
            del st.session_state["editor_schizzo_target"]
            st.session_state["editor_ultimo_save_id"] = None
            st.success("Schizzo salvato!")
            st.switch_page("pages/5_Gestione_Progetto.py")

        elif risultato.get("event") == "cancel":
            del st.session_state["editor_schizzo_target"]
            st.session_state["editor_ultimo_save_id"] = None
            st.switch_page("pages/5_Gestione_Progetto.py")
