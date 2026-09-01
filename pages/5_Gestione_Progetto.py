import streamlit as st
from services.supabase import supabase
from services.theme import apply_custom_theme, badge
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
        st.image(url_esistente, width=250, caption="Schizzo attuale")

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
        height=350,
        width=500,
        drawing_mode=modalita,
        display_toolbar=True,
        key=f"canvas_{key_prefix}"
    )

    if st.button("💾 Salva schizzo", key=f"salva_schizzo_{key_prefix}", use_container_width=True):
        if canvas_result.image_data is not None:
            salva_schizzo(canvas_result.image_data, cartella, nome_file, tabella, record_id)
            st.success("Schizzo salvato!")
            st.rerun()
        else:
            st.warning("Disegna qualcosa prima di salvare.")


st.set_page_config(page_title="Gestione Progetto", page_icon="🪟", layout="wide")
apply_custom_theme()

if "progetto_corrente_id" not in st.session_state:
    st.markdown("<div class='page-header'><h1>🪟 Gestione Progetto</h1></div>", unsafe_allow_html=True)
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

    infissi_esistenti = supabase.table("infissi").select("*").eq("progetto_id", progetto_id).order("numero_infisso").execute()
    num_infissi_tot = len(infissi_esistenti.data) if infissi_esistenti.data else 0
    mq_tot = sum(i['mq'] * i['quantita'] for i in infissi_esistenti.data) if infissi_esistenti.data else 0.0

    st.markdown(
        f"<div class='page-header'><h1>🪟 {nome_cliente}</h1>"
        f"<p>Gestisci infissi, foto e schizzi di questo progetto.</p></div>",
        unsafe_allow_html=True
    )

    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.metric("Infissi inseriti", num_infissi_tot)
    with col_m2:
        st.metric("Superficie totale", f"{mq_tot:.2f} m²")

    st.markdown("<div class='section-spacer'></div>", unsafe_allow_html=True)

    # --- Schizzo generale del progetto ---
    with st.container(border=True):
        st.markdown("#### ✏️ Schizzo generale del progetto")
        st.caption("Es. pianta del cantiere")
        mostra_schizzo_generale = st.checkbox("Mostra/Modifica schizzo generale", key="mostra_schizzo_generale")
        if mostra_schizzo_generale:
            progetto_info = supabase.table("progetti").select("schizzo_url").eq("id", progetto_id).execute()
            schizzo_esistente = progetto_info.data[0].get("schizzo_url") if progetto_info.data else None
            pannello_schizzo("progetto", cartella_progetto, "schizzo_generale", "progetti", progetto_id, schizzo_esistente)

    # --- Foto generali del progetto ---
    with st.container(border=True):
        st.markdown("#### 📷 Foto generali del progetto")
        st.caption("Es. schizzi su carta fotografati, foto d'insieme del cantiere")
        mostra_foto_generali = st.checkbox("Mostra/Aggiungi foto generali", key="mostra_foto_generali")
        if mostra_foto_generali:
            if "foto_generali_key_counter" not in st.session_state:
                st.session_state["foto_generali_key_counter"] = 0
            if "foto_generali_catturate" not in st.session_state:
                st.session_state["foto_generali_catturate"] = []
            if "camera_generali_shot_counter" not in st.session_state:
                st.session_state["camera_generali_shot_counter"] = 0
            if "fotocamera_generali_aperta" not in st.session_state:
                st.session_state["fotocamera_generali_aperta"] = True

            foto_esistenti = elenco_foto_generali(cartella_progetto)
            if foto_esistenti:
                st.caption(f"Foto già caricate: {len(foto_esistenti)}")
                cols = st.columns(4)
                for idx, foto in enumerate(foto_esistenti):
                    with cols[idx % 4]:
