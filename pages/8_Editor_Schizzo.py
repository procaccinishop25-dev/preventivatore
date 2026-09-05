import streamlit as st
from services.supabase import supabase
from services.theme import apply_custom_theme
from streamlit_drawable_canvas import st_canvas
from PIL import Image
import io
import re


ICONE_STRUMENTI = {
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
    "Penna": "freedraw",
    "Gomma": "freedraw",
    "Linea dritta": "line",
    "Rettangolo": "rect",
    "Cerchio": "circle",
}

LARGHEZZA_CANVAS = 1000
ALTEZZA_CANVAS = 620


def slug(testo):
    testo = (testo or "").strip().replace(" ", "_")
    return re.sub(r"[^A-Za-z0-9_-]", "", testo)


def prepara_immagine_sfondo(file_bytes):
    img = Image.open(io.BytesIO(file_bytes)).convert("RGBA")
    img.thumbnail((LARGHEZZA_CANVAS, ALTEZZA_CANVAS), Image.LANCZOS)
    sfondo = Image.new("RGBA", (LARGHEZZA_CANVAS, ALTEZZA_CANVAS), (255, 255, 255, 255))
    x = (LARGHEZZA_CANVAS - img.width) // 2
    y = (ALTEZZA_CANVAS - img.height) // 2
    sfondo.paste(img, (x, y), img)
    return sfondo


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

    col_strumento, col_colore = st.columns([2, 2])
    with col_strumento:
        icona_strumento = st.radio("Strumento", list(ICONE_STRUMENTI.keys()), horizontal=True, key="editor_strumento")
        strumento = ICONE_STRUMENTI[icona_strumento]
    with col_colore:
        if strumento != "Gomma":
            icona_colore = st.radio("Colore", list(ICONE_COLORI.keys()), horizontal=True, key="editor_colore")
            colore = ICONE_COLORI[icona_colore]
        else:
            colore = "#FFFFFF"

    modalita = MAPPA_MODALITA[strumento]
    spessore = st.slider(
        "Spessore" if strumento != "Gomma" else "Spessore gomma",
        1 if strumento != "Gomma" else 5,
        15 if strumento != "Gomma" else 60,
        3 if strumento != "Gomma" else 25,
        key="editor_spessore"
    )

    with st.expander("📷 Usa una foto come sfondo (opzionale)"):
        foto_sfondo = st.file_uploader("Carica una foto per disegnarci sopra", type=["jpg", "jpeg", "png"], key="editor_foto_sfondo")

    immagine_sfondo = None
    if foto_sfondo is not None:
        immagine_sfondo = prepara_immagine_sfondo(foto_sfondo.getvalue())

    canvas_result = st_canvas(
        fill_color="rgba(255, 255, 255, 0)",
        stroke_width=spessore,
        stroke_color=colore,
        background_color="#FFFFFF",
        background_image=immagine_sfondo,
        height=ALTEZZA_CANVAS,
        width=LARGHEZZA_CANVAS,
        drawing_mode=modalita,
        display_toolbar=True,
        key="editor_canvas"
    )

    st.write("")
    col_salva, col_chiudi = st.columns(2)
    with col_salva:
        if st.button("💾 Salva schizzo ed esci", type="primary", use_container_width=True):
            if canvas_result.image_data is not None:
                salva_schizzo(canvas_result.image_data, target['cartella'], target['nome_file'], target['tabella'], target['record_id'])
                del st.session_state["editor_schizzo_target"]
                st.success("Schizzo salvato!")
                st.switch_page("pages/5_Gestione_Progetto.py")
            else:
                st.warning("Disegna qualcosa prima di salvare.")
    with col_chiudi:
        if st.button("✖️ Chiudi senza salvare", use_container_width=True):
            del st.session_state["editor_schizzo_target"]
            st.switch_page("pages/5_Gestione_Progetto.py")
