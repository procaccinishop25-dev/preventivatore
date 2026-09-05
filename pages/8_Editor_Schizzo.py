import streamlit as st
from services.supabase import supabase
from services.theme import apply_custom_theme
from streamlit_drawable_canvas import st_canvas
from PIL import Image
import io
import re
import base64


ICONE_STRUMENTI = {
    "🖐️": "Sposta",
    "✏️": "Penna",
    "🧽": "Gomma",
    "➖": "Linea dritta",
    "▭": "Rettangolo",
    "⚪": "Cerchio",
}

ICONE_COLORI = {
    "⚫": "#000000",
    "🔴": "#DC2626",
    "🔵": "#2563EB",
    "🟢": "#16A34A",
    "🟡": "#F59E0B",
    "🟣": "#7C3AED",
}

MAPPA_MODALITA = {
    "Sposta": "transform",
    "Penna": "freedraw",
    "Gomma": "freedraw",
    "Linea dritta": "line",
    "Rettangolo": "rect",
    "Cerchio": "circle",
}

LARGHEZZA_CANVAS = 1100
ALTEZZA_CANVAS = 650


def slug(testo):
    testo = (testo or "").strip().replace(" ", "_")
    return re.sub(r"[^A-Za-z0-9_-]", "", testo)


def costruisci_json_immagine(file_bytes, max_dim=350):
    img = Image.open(io.BytesIO(file_bytes)).convert("RGBA")
    w, h = img.size
    scala = min(1.0, max_dim / max(w, h))

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    b64_png = base64.b64encode(buffer.getvalue()).decode()

    return {
        "version": "4.4.0",
        "objects": [
            {
                "type": "image",
                "version": "4.4.0",
                "left": 30,
                "top": 30,
                "width": w,
                "height": h,
                "scaleX": scala,
                "scaleY": scala,
                "src": f"data:image/png;base64,{b64_png}",
                "crossOrigin": "anonymous",
                "selectable": True
            }
        ]
    }


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


st.set_page_config(page_title="Editor Schizzo", page_icon="✏️", layout="wide")
apply_custom_theme()

target = st.session_state.get("editor_schizzo_target")

if not target:
    st.warning("Nessuno schizzo da modificare selezionato.")
    if st.button("← Torna a Gestione Progetto"):
        st.switch_page("pages/5_Gestione_Progetto.py")
else:
    st.markdown(f"### ✏️ Schizzo — {target['nome_file']}")

    if target.get('url_esistente'):
        with st.expander("Vedi schizzo salvato in precedenza"):
            st.image(target['url_esistente'], width=300)

    if "editor_ultima_foto_fingerprint" not in st.session_state:
        st.session_state["editor_ultima_foto_fingerprint"] = None
    if "editor_immagine_da_inserire" not in st.session_state:
        st.session_state["editor_immagine_da_inserire"] = None

    with st.expander("📎 Allega una foto (poi usa \"🖐️ Sposta\" per posizionarla)"):
        st.caption("Attenzione: allega la foto prima di iniziare a disegnare, per evitare di perdere il disegno.")
        foto_allegata = st.file_uploader("Scegli foto", type=["jpg", "jpeg", "png"], key="editor_foto_allegata")

        if foto_allegata is not None:
            fingerprint = f"{foto_allegata.name}_{foto_allegata.size}"
            if fingerprint != st.session_state["editor_ultima_foto_fingerprint"]:
                st.session_state["editor_ultima_foto_fingerprint"] = fingerprint
                st.session_state["editor_immagine_da_inserire"] = costruisci_json_immagine(foto_allegata.getvalue())
                st.rerun()

    col_strumento, col_colore = st.columns([3, 2])
    with col_strumento:
        icona_strumento = st.radio("Strumento", list(ICONE_STRUMENTI.keys()), horizontal=True, key="editor_strumento")
        strumento = ICONE_STRUMENTI[icona_strumento]
    with col_colore:
        if strumento not in ("Gomma", "Sposta"):
            icona_colore = st.radio("Colore", list(ICONE_COLORI.keys()), horizontal=True, key="editor_colore")
            colore = ICONE_COLORI[icona_colore]
        else:
            colore = "#FFFFFF" if strumento == "Gomma" else "#000000"

    modalita = MAPPA_MODALITA[strumento]

    if strumento not in ("Sposta",):
        spessore = st.slider(
            "Spessore" if strumento != "Gomma" else "Spessore gomma",
            1 if strumento != "Gomma" else 5,
            15 if strumento != "Gomma" else 60,
            3 if strumento != "Gomma" else 25,
            key="editor_spessore"
        )
    else:
        spessore = 3
        st.caption("Trascina la foto per spostarla, tira gli angoli per ridimensionarla.")

    immagine_da_inserire = st.session_state["editor_immagine_da_inserire"]

    canvas_result = st_canvas(
        fill_color="rgba(255, 255, 255, 0)",
        stroke_width=spessore,
        stroke_color=colore,
        background_color="#FFFFFF",
        initial_drawing=immagine_da_inserire,
        height=ALTEZZA_CANVAS,
        width=LARGHEZZA_CANVAS,
        drawing_mode=modalita,
        display_toolbar=True,
        key="editor_canvas"
    )

    # L'immagine va iniettata una sola volta: la puliamo subito dopo averla passata al canvas
    if immagine_da_inserire is not None:
        st.session_state["editor_immagine_da_inserire"] = None

    st.write("")
    col_salva, col_chiudi = st.columns(2)
    with col_salva:
        if st.button("💾 Salva schizzo ed esci", type="primary", use_container_width=True):
            if canvas_result.image_data is not None:
                salva_schizzo(canvas_result.image_data, target['cartella'], target['nome_file'], target['tabella'], target['record_id'])
                del st.session_state["editor_schizzo_target"]
                st.session_state["editor_ultima_foto_fingerprint"] = None
                st.success("Schizzo salvato!")
                st.switch_page("pages/5_Gestione_Progetto.py")
            else:
                st.warning("Disegna qualcosa prima di salvare.")
    with col_chiudi:
        if st.button("✖️ Chiudi senza salvare", use_container_width=True):
            del st.session_state["editor_schizzo_target"]
            st.session_state["editor_ultima_foto_fingerprint"] = None
            st.switch_page("pages/5_Gestione_Progetto.py")
