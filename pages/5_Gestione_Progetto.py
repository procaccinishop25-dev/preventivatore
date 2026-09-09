import streamlit as st
from services.supabase import supabase
from services.theme import apply_custom_theme, card_divider
from services.ui_components import list_item
from services.pdf import genera_preventivo_rapido, trigger_download_automatico, dialog_dopo_generazione_preventivo
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


def crea_infissi_e_foto(progetto_id, cartella_progetto, tipologia, quantita, larghezza, altezza, note_inf, metodo_foto, foto_multiple_da_file):
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

    st.session_state["foto_key_counter"] += 1
    st.session_state["foto_catturate"] = []
    st.session_state["fotocamera_aperta"] = True

    return id_infissi_creati


@st.dialog(":material/add: Aggiungi infisso", width="large")
def dialog_aggiungi_infisso(progetto_id, cartella_progetto):
    if "foto_key_counter" not in st.session_state:
        st.session_state["foto_key_counter"] = 0
    if "foto_catturate" not in st.session_state:
        st.session_state["foto_catturate"] = []
    if "camera_shot_counter" not in st.session_state:
        st.session_state["camera_shot_counter"] = 0
    if "fotocamera_aperta" not in st.session_state:
        st.session_state["fotocamera_aperta"] = True

    contatore = st.session_state["foto_key_counter"]

    prodotti_catalogo = supabase.table("catalogo_prodotti").select(
        "nome, materiale, prezzo_standard_mq, descrizione"
    ).order("nome").execute().data or []

    opzioni_tipologia = [p['nome'] for p in prodotti_catalogo] + ["Altro (personalizzato)"]

    if not prodotti_catalogo:
        st.caption("Il Catalogo è vuoto — aggiungi prodotti da lì, oppure usa \"Altro (personalizzato)\" qui sotto.")

    col_t, col_q = st.columns([2, 1])
    with col_t:
        tipologia_scelta = st.selectbox("Tipologia", opzioni_tipologia, key=f"tip_{contatore}")
    with col_q:
        quantita = st.number_input("Quantità", min_value=1, step=1, value=1, key=f"qta_{contatore}")

    tipologia = tipologia_scelta
    prodotto_selezionato = None
    if tipologia_scelta == "Altro (personalizzato)":
        tipologia = st.text_input("Nome personalizzato", key=f"tip_custom_{contatore}", placeholder="Es. Zanzariera su misura")
    else:
        prodotto_selezionato = next((p for p in prodotti_catalogo if p['nome'] == tipologia_scelta), None)

    if prodotto_selezionato:
        prezzo_val = prodotto_selezionato.get('prezzo_standard_mq')
        prezzo_str = f"{prezzo_val:.2f} €/m²" if prezzo_val is not None else "prezzo non impostato"
        st.markdown(
            f"<div style='background-color:var(--color-primary-light); border-radius:8px; padding:0.5rem 0.8rem; "
            f"margin:0.3rem 0 0.6rem 0; font-size:0.85rem; color:var(--color-text);'>"
            f"<strong>{prezzo_str}</strong>"
            f"</div>",
            unsafe_allow_html=True
        )

    col_l, col_a = st.columns(2)
    with col_l:
        larghezza = st.number_input("Larghezza (cm)", min_value=1.0, step=1.0, key=f"larg_new_{contatore}")
    with col_a:
        altezza = st.number_input("Altezza (cm)", min_value=1.0, step=1.0, key=f"alt_new_{contatore}")

    mq_anteprima = (larghezza / 100) * (altezza / 100)
    st.markdown(
        f"<div style='background-color:var(--color-primary-light); border-radius:8px; padding:0.6rem 0.9rem; "
        f"margin:0.3rem 0 0.8rem 0;'><span style='color:var(--color-text-secondary); font-size:0.85rem;'>Superficie per pezzo</span><br>"
        f"<span style='color:var(--color-primary); font-weight:700; font-size:1.15rem;'>{mq_anteprima:.2f} m²</span></div>",
        unsafe_allow_html=True
    )

    note_inf = st.text_area("Note (opzionale)", height=70, key=f"note_new_{contatore}")

    st.caption("Foto (opzionale) — con più pezzi, assegnate in ordine")
    metodo_foto = st.radio(
        "Come aggiungere la foto?", ["Nessuna", "Carica da file", "Scatta foto"],
        horizontal=True, key=f"metodo_foto_nuovo_{contatore}"
    )

    foto_multiple_da_file = []
    if metodo_foto == "Carica da file":
        foto_multiple_da_file = st.file_uploader(
            "Carica una o più foto", type=["jpg", "jpeg", "png"],
            accept_multiple_files=True, key=f"foto_upload_nuovo_{contatore}"
        ) or []

    elif metodo_foto == "Scatta foto":
        st.caption(f"Scattate finora: **{len(st.session_state['foto_catturate'])}**")
        if st.session_state["foto_catturate"]:
            cols_preview = st.columns(min(len(st.session_state["foto_catturate"]), 6))
            for idx, foto in enumerate(st.session_state["foto_catturate"]):
                with cols_preview[idx % len(cols_preview)]:
                    st.image(foto["bytes"], width=70)

        if st.session_state["fotocamera_aperta"]:
            scatto = st.camera_input("Scatta una foto", key=f"foto_cam_multi_{st.session_state['camera_shot_counter']}")
            col_agg, col_chiudi = st.columns(2)
            with col_agg:
                if scatto is not None:
                    if st.button("Aggiungi alla lista", icon=":material/add:", use_container_width=True):
                        st.session_state["foto_catturate"].append({
                            "bytes": scatto.getvalue(), "type": scatto.type, "name": scatto.name
                        })
                        st.session_state["camera_shot_counter"] += 1
                        st.rerun()
            with col_chiudi:
                if st.button("Chiudi fotocamera", icon=":material/check:", use_container_width=True):
                    st.session_state["fotocamera_aperta"] = False
                    st.rerun()
        else:
            st.info("Fotocamera chiusa.")
            col_riapri, col_svuota = st.columns(2)
            with col_riapri:
                if st.button("Riapri fotocamera", icon=":material/photo_camera:", use_container_width=True):
                    st.session_state["fotocamera_aperta"] = True
                    st.rerun()
            with col_svuota:
                if st.session_state["foto_catturate"]:
                    if st.button("Svuota", icon=":material/delete:", use_container_width=True):
                        st.session_state["foto_catturate"] = []
                        st.rerun()

    st.write("")
    col_normale, col_schizzo = st.columns(2)
    with col_normale:
        premuto_normale = st.button("Aggiungi infisso", icon=":material/check:", type="primary", use_container_width=True, key=f"conferma_add_{contatore}")
    with col_schizzo:
        premuto_con_schizzo = st.button("Aggiungi e disegna schizzo", icon=":material/draw:", use_container_width=True, key=f"conferma_add_schizzo_{contatore}")

    if premuto_normale or premuto_con_schizzo:
        if not tipologia:
            st.warning("Inserisci un nome per la tipologia personalizzata prima di continuare.")
        else:
            id_infissi_creati = crea_infissi_e_foto(
                progetto_id, cartella_progetto, tipologia, quantita, larghezza, altezza,
                note_inf, metodo_foto, foto_multiple_da_file
            )

            if premuto_con_schizzo:
                primo_id, primo_nome = id_infissi_creati[0]
                if int(quantita) > 1:
                    st.info(f"Lo schizzo verrà associato solo al primo infisso: **{primo_nome}**.")
                st.session_state["editor_schizzo_target"] = {
                    "tabella": "infissi",
                    "record_id": primo_id,
                    "cartella": cartella_progetto,
                    "nome_file": primo_nome,
                    "url_esistente": None,
                }
                st.switch_page("pages/8_Editor_Schizzo.py")
            else:
                st.success(f"{int(quantita)} infisso/i aggiunto/i!")
                st.rerun()


@st.dialog("Modifica infisso", width="large")
def dialog_dettagli_infisso(inf, cartella_progetto):
    nome_visualizzato = inf.get('nome') or f"{inf['tipologia']} {inf.get('numero_infisso', '')}"
    st.markdown(f"### {nome_visualizzato}")

    st.markdown("#### Misure")
    col1, col2 = st.columns(2)
    with col1:
        nuova_larghezza = st.number_input("Larghezza (cm)", value=float(inf['larghezza_cm']), key=f"larg_{inf['id']}")
    with col2:
        nuova_altezza = st.number_input("Altezza (cm)", value=float(inf['altezza_cm']), key=f"alt_{inf['id']}")

    mq_live = (nuova_larghezza / 100) * (nuova_altezza / 100)
    st.caption(f"Superficie: **{mq_live:.2f} m²**")

    nuove_note = st.text_area("Note", value=inf['note'] or "", key=f"note_{inf['id']}", height=80)

    col_salva, col_elimina = st.columns(2)
    with col_salva:
        if st.button("Salva modifiche", icon=":material/save:", key=f"salva_{inf['id']}", use_container_width=True, type="primary"):
            supabase.table("infissi").update({
                "larghezza_cm": nuova_larghezza,
                "altezza_cm": nuova_altezza,
                "note": nuove_note
            }).eq("id", inf['id']).execute()
            st.success("Modificato!")
            st.rerun()
    with col_elimina:
        with st.container(key=f"dangerwrap_elimina_{inf['id']}"):
            if st.button("Elimina infisso", icon=":material/delete:", key=f"elimina_{inf['id']}", use_container_width=True):
                supabase.table("infissi").delete().eq("id", inf['id']).execute()
                st.rerun()

    st.divider()
    st.markdown("#### Foto")

    if inf.get('foto_url'):
        st.image(inf['foto_url'], width=220)
    else:
        st.caption("Nessuna foto ancora.")

    metodo_foto_inf = st.radio(
        "Aggiungi/cambia foto", ["Carica da file", "Scatta foto"],
        horizontal=True, key=f"metodo_foto_{inf['id']}"
    )

    if metodo_foto_inf == "Carica da file":
        foto_caricata = st.file_uploader("Carica foto", type=["jpg", "jpeg", "png"], key=f"foto_{inf['id']}")
    else:
        foto_caricata = st.camera_input("Scatta una foto", key=f"foto_cam_{inf['id']}")

    if foto_caricata is not None:
        if st.button("Salva foto", icon=":material/upload:", key=f"salva_foto_{inf['id']}", use_container_width=True, type="primary"):
            carica_foto_bytes(foto_caricata.getvalue(), foto_caricata.type, foto_caricata.name, cartella_progetto, nome_visualizzato, inf['id'])
            st.success("Foto caricata!")
            st.rerun()

    st.divider()
    st.markdown("#### Schizzo")

    def _apri_editor_schizzo():
        st.session_state["editor_schizzo_target"] = {
            "tabella": "infissi",
            "record_id": inf['id'],
            "cartella": cartella_progetto,
            "nome_file": nome_visualizzato,
            "url_esistente": inf.get('schizzo_url'),
        }
        st.switch_page("pages/8_Editor_Schizzo.py")

    if inf.get('schizzo_url'):
        st.image(inf['schizzo_url'], width=220, caption="Schizzo attuale")
        if st.button("Modifica questo schizzo", icon=":material/draw:", key=f"modifica_schizzo_esistente_{inf['id']}", use_container_width=True, type="primary"):
            _apri_editor_schizzo()
    else:
        st.caption("Nessuno schizzo ancora.")
        if st.button("Apri editor schizzo a schermo intero", icon=":material/draw:", key=f"apri_editor_{inf['id']}", use_container_width=True, type="primary"):
            _apri_editor_schizzo()


@st.dialog(":material/payments: Aggiungi maggiorazione")
def dialog_aggiungi_maggiorazione_progetto(progetto_id, lista_infissi):
    descrizione = st.text_input("Nome regola", placeholder="Es. Smontaggio vecchio infisso")

    col1, col2 = st.columns(2)
    with col1:
        importo = st.number_input("Importo", min_value=0.0, step=1.0)
    with col2:
        tipo_label = st.selectbox("Unità di misura", ["€/m²", "€ fisso", "%"])
    tipo_map = {"€/m²": "mq", "€ fisso": "fisso", "%": "percentuale"}

    applicazione = st.radio("Applica a", ["Tutti gli infissi", "Un infisso specifico"])
    infisso_id_scelto = None
    if applicazione == "Un infisso specifico":
        if lista_infissi:
            opzioni = {(inf.get('nome') or inf['tipologia']): inf['id'] for inf in lista_infissi}
            nome_scelto = st.selectbox("Seleziona infisso", list(opzioni.keys()))
            infisso_id_scelto = opzioni[nome_scelto]
        else:
            st.info("Nessun infisso ancora presente in questo progetto.")

    if st.button("Aggiungi", icon=":material/check:", type="primary", use_container_width=True):
        if not descrizione:
            st.warning("Inserisci un nome per la regola.")
        else:
            supabase.table("progetto_maggiorazioni").insert({
                "progetto_id": progetto_id,
                "descrizione": descrizione,
                "importo": importo,
                "tipo": tipo_map[tipo_label],
                "infisso_id": infisso_id_scelto
            }).execute()
            st.success("Maggiorazione aggiunta!")
            st.rerun()


st.set_page_config(page_title="Gestione Progetto", page_icon="🪟", layout="wide")
apply_custom_theme()

if "progetto_corrente_id" not in st.session_state:
    st.markdown("<h1>Gestione Progetto</h1>", unsafe_allow_html=True)
    st.warning("Nessun progetto selezionato.")
    st.page_link("pages/2_Progetti.py", label="Vai a Progetti →", icon=":material/folder:")
    st.page_link("pages/1_Nuovo_Progetto.py", label="Oppure crea un nuovo progetto →", icon=":material/note_add:")
else:
    progetto_id = st.session_state["progetto_corrente_id"]
    nome_cliente = st.session_state["progetto_corrente_nome"]
    cartella_progetto = slug(nome_cliente)

    progetto_row = supabase.table("progetti").select(
        "indirizzo, citta, data_sopralluogo, operatore, schizzo_url, clienti(nome, cognome_azienda, telefono, email)"
    ).eq("id", progetto_id).execute()
    progetto_data = progetto_row.data[0] if progetto_row.data else {}
    cliente_data = progetto_data.get("clienti") or {}

    infissi_esistenti = supabase.table("infissi").select("*").eq("progetto_id", progetto_id).order("numero_infisso").execute()
    lista_infissi = infissi_esistenti.data or []
    num_infissi_tot = len(lista_infissi)
    mq_tot = sum(i['mq'] * i['quantita'] for i in lista_infissi)

    st.markdown(
        f"<div style='font-size:0.72rem; color:var(--color-text-disabled); font-weight:700; letter-spacing:0.06em; text-transform:uppercase; margin-bottom:2px;'>PROGETTO</div>"
        f"<h1 style='margin:0 0 2px 0;'>{nome_cliente}</h1>"
        f"<p style='color:var(--color-text-secondary); margin:0 0 0.8rem 0; font-size:0.87rem;'>"
        f"{progetto_data.get('indirizzo', '')}, {progetto_data.get('citta', '')}</p>",
        unsafe_allow_html=True
    )

    st.markdown(
        f"<div style='display:flex; gap:2.2rem; align-items:center; padding:0.7rem 0; "
        f"border-top:1px solid var(--color-border); border-bottom:1px solid var(--color-border); margin-bottom:1.2rem;'>"
        f"<div><span style='color:var(--color-text-secondary); font-size:0.78rem;'>Infissi &nbsp;</span>"
        f"<span style='color:var(--color-title); font-weight:700; font-size:0.95rem;'>{num_infissi_tot}</span></div>"
        f"<div style='width:1px; height:18px; background-color:var(--color-border);'></div>"
        f"<div><span style='color:var(--color-text-secondary); font-size:0.78rem;'>Superficie totale &nbsp;</span>"
        f"<span class='num-tabular' style='color:var(--color-primary); font-weight:700; font-size:0.95rem;'>{mq_tot:.2f} m²</span></div>"
        f"</div>",
        unsafe_allow_html=True
    )

    col_h1, col_h2 = st.columns([3, 1])
    with col_h1:
        st.markdown(f"### Infissi <span style='color:var(--color-text-secondary); font-weight:400; font-size:0.9rem;'>({num_infissi_tot})</span>", unsafe_allow_html=True)
    with col_h2:
        if st.button("Aggiungi infisso", icon=":material/add:", type="primary", use_container_width=True):
            dialog_aggiungi_infisso(progetto_id, cartella_progetto)

    if lista_infissi:
        with st.expander(f"Inseriti {num_infissi_tot} infissi — clicca per vedere l'elenco", expanded=False):
            with st.container(border=True):
                for idx, inf in enumerate(lista_infissi):
                    nome_visualizzato = inf.get('nome') or f"{inf['tipologia']} {inf.get('numero_infisso', '')}"

                    tag_extra = []
                    if inf.get('foto_url'):
                        tag_extra.append("Foto")
                    if inf.get('schizzo_url'):
                        tag_extra.append("Schizzo")
                    tag_str = f" · {', '.join(tag_extra)}" if tag_extra else ""

                    sottotitolo = f"{inf['larghezza_cm']}×{inf['altezza_cm']} cm · {inf['mq']} m²{tag_str}"

                    risultato = list_item(
                        titolo=nome_visualizzato,
                        sottotitolo=sottotitolo,
                        azione_primaria_label="Modifica",
