import streamlit as st
from services.supabase import supabase
from streamlit_drawable_canvas import st_canvas
from streamlit_image_coordinates import streamlit_image_coordinates
from PIL import Image, ImageDraw, ImageFont
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


def carica_font(dimensione):
    try:
        return ImageFont.load_default(size=dimensione)
    except TypeError:
        return ImageFont.load_default()


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

    canvas_width, canvas_height = 500, 350

    canvas_result = st_canvas(
        fill_color="rgba(255, 255, 255, 0)",
        stroke_width=spessore,
        stroke_color=colore,
        background_color="#FFFFFF",
        height=canvas_height,
        width=canvas_width,
        drawing_mode=modalita,
        display_toolbar=True,
        key=f"canvas_{key_prefix}"
    )

    if canvas_result.image_data is not None:
        disegno_attuale = Image.fromarray(canvas_result.image_data.astype("uint8"), "RGBA")
    else:
        disegno_attuale = Image.new("RGBA", (canvas_width, canvas_height), "white")

    chiave_testi = f"testi_schizzo_{key_prefix}"
    chiave_ultimo_click = f"ultimo_click_{key_prefix}"
    if chiave_testi not in st.session_state:
        st.session_state[chiave_testi] = []
    if chiave_ultimo_click not in st.session_state:
        st.session_state[chiave_ultimo_click] = None

    st.divider()
    st.write("📝 Aggiungi testo: scrivilo qui sotto, poi **clicca sul disegno** nel punto dove vuoi posizionarlo")

    col_testo, col_dim = st.columns([3, 1])
    with col_testo:
        testo_da_inserire = st.text_input("Testo da inserire", key=f"testo_input_{key_prefix}")
    with col_dim:
        dimensione_testo = st.slider("Dimensione", 10, 60, 20, key=f"dim_testo_{key_prefix}")

    # Anteprima: disegno attuale + tutti i testi già posizionati
    anteprima = disegno_attuale.copy()
    draw = ImageDraw.Draw(anteprima)
    for t in st.session_state[chiave_testi]:
        draw.text((t["x"], t["y"]), t["testo"], fill="black", font=carica_font(t["dimensione"]))

    click = streamlit_image_coordinates(anteprima, key=f"click_{key_prefix}")

    if click is not None and click != st.session_state[chiave_ultimo_click]:
        st.session_state[chiave_ultimo_click] = click
        if testo_da_inserire:
            st.session_state[chiave_testi].append({
                "x": click["x"], "y": click["y"],
                "testo": testo_da_inserire, "dimensione": dimensione_testo
            })
            st.rerun()
        else:
            st.warning("Scrivi il testo prima di cliccare sul disegno.")

    if st.session_state[chiave_testi]:
        if st.button("🗑️ Rimuovi ultimo testo aggiunto", key=f"rimuovi_testo_{key_prefix}"):
            st.session_state[chiave_testi].pop()
            st.rerun()

    if st.button("💾 Salva schizzo", key=f"salva_schizzo_{key_prefix}"):
        finale = disegno_attuale.copy()
        draw_finale = ImageDraw.Draw(finale)
        for t in st.session_state[chiave_testi]:
            draw_finale.text((t["x"], t["y"]), t["testo"], fill="black", font=carica_font(t["dimensione"]))

        buffer = io.BytesIO()
        finale.save(buffer, format="PNG")
        buffer.seek(0)
        percorso = f"{cartella}/{slug(nome_file)}.png"
        supabase.storage.from_("schizzi").upload(
            percorso, buffer.getvalue(), {"content-type": "image/png", "upsert": "true"}
        )
        url_pubblico = supabase.storage.from_("schizzi").get_public_url(percorso)
        supabase.table(tabella).update({"schizzo_url": url_pubblico}).eq("id", record_id).execute()

        st.session_state[chiave_testi] = []
        st.session_state[chiave_ultimo_click] = None
        st.success("Schizzo salvato!")
        st.rerun()


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

    st.write("✏️
