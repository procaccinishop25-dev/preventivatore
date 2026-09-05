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
    "📎": "Allega foto",
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

LARGHEZZA_CANVAS = 1400
ALTEZZA_CANVAS = 1500


def slug(testo):
    testo = (testo or "").strip().replace(" ", "_")
    return re.sub(r"[^A-Za-z0-9_-]", "", testo)


def costruisci_sfondo_con_foto(file_bytes, pos_x_pct, pos_y_pct, scala_pct):
    img = Image.open(io.BytesIO(file_bytes)).convert("RGBA")
    scala = scala_pct / 100
    nuova_larghezza = max(1, int(img.width * scala))
    nuova_altezza = max(1, int(img.height * scala))
    img_ridim = img.resize((nuova_larghezza, nuova_altezza), Image.LANCZOS)

    sfondo = Image.new("RGBA", (LARGHEZZA_CANVAS, ALTEZZA_CANVAS), (255, 255, 255, 255))
    x = int((LARGHEZZA_CANVAS - img_ridim.width) * (pos_x_pct / 100))
    y = int((ALTEZZA_CANVAS - img_ridim.height) * (pos_y_pct / 100))
    sfondo.paste(img_ridim, (x, y), img_ridim)
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

    if "editor_foto_bytes" not in st.session_state:
        st.session_state["editor_foto_bytes"] = None

    # --- Barra strumenti compatta, con "Allega foto" come uno degli strumenti ---
    icona_strumento = st.radio("Strumento", list(ICONE_STRUMENTI.keys()), horizontal=True, key="editor_strumento")
    strumento = ICONE_STRUMENTI[icona_strumento]

    immagine_sfondo = None

    if strumento == "Allega foto":
        foto_allegata = st.file_uploader("Scegli foto", type=["jpg", "jpeg", "png"], key="editor_foto_allegata")
        if foto_allegata is not None:
            st.session_state["editor_foto_bytes"] = foto_allegata.getvalue()

        if st.session_state["editor_foto_bytes"]:
            col_px, col_py, col_ps = st.columns(3)
            with col_px:
                pos_x = st.slider("Posizione orizzontale", 0, 100, 0, key="editor_pos_x")
            with col_py:
                pos_y = st.slider("Posizione verticale", 0, 100, 0, key="editor_pos_y")
            with col_ps:
                scala = st.slider("Dimensione (%)", 5, 100, 40, key="editor_scala")
            immagine_sfondo = costruisci_sfondo_con_foto(st.session_state["editor_foto_bytes"], pos_x, pos_y, scala)
            st.caption("Regola gli slider, poi passa a Penna o un altro strumento per disegnare sopra.")
        else:
            st.caption("Carica una foto per posizionarla sul foglio.")

        modalita = "transform"
        spessore = 3
        colore = "#000000"

    else:
        col_colore, col_spessore = st.columns([3, 2])
        with col_colore:
            if strumento != "Gomma":
                icona_colore = st.radio("Colore", list(ICONE_COLORI.keys()), horizontal=True, key="editor_colore")
                colore = ICONE_COLORI[icona_colore]
            else:
                colore = "#FFFFFF"
        with col_spessore:
            spessore = st.slider(
                "Spessore" if strumento != "Gomma" else "Gomma",
                1 if strumento != "Gomma" else 5,
                15 if strumento != "Gomma" else 60,
                3 if strumento != "Gomma" else 25,
                key="editor_spessore"
            )
        modalita = MAPPA_MODALITA[strumento]

        # Se una foto è già stata posizionata in precedenza, resta come sfondo mentre disegni
        if st.session_state["editor_foto_bytes"]:
            pos_x = st.session_state.get("editor_pos_x", 0)
            pos_y = st.session_state.get("editor_pos_y", 0)
            scala = st.session_state.get("editor_scala", 40)
            immagine_sfondo = costruisci_sfondo_con_foto(st.session_state["editor_foto_bytes"], pos_x, pos_y, scala)

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
                st.session_state["editor_foto_bytes"] = None
                st.success("Schizzo salvato!")
                st.switch_page("pages/5_Gestione_Progetto.py")
            else:
                st.warning("Disegna qualcosa prima di salvare.")
    with col_chiudi:
        if st.button("✖️ Chiudi senza salvare", use_container_width=True):
            del st.session_state["editor_schizzo_target"]
            st.session_state["editor_foto_bytes"] = None
            st.switch_page("pages/5_Gestione_Progetto.py")
