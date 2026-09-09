import streamlit as st
from services.supabase import supabase
from services.theme import apply_custom_theme, card_divider
from services.ui_components import page_toolbar
import uuid


MATERIALI = ["Alluminio", "PVC", "Ferro"]


def carica_foto_prodotto(bytes_data, tipo, nome_file):
    nome_unico = f"catalogo/{uuid.uuid4().hex[:8]}_{nome_file}"
    supabase.storage.from_("foto").upload(nome_unico, bytes_data, {"content-type": tipo, "upsert": "true"})
    return supabase.storage.from_("foto").get_public_url(nome_unico)


st.set_page_config(page_title="Catalogo", page_icon="🛒")
apply_custom_theme()

page_toolbar(
    "Catalogo",
    "I prodotti selezionabili quando aggiungi un infisso a un progetto."
)

if "catalogo_form_counter" not in st.session_state:
    st.session_state["catalogo_form_counter"] = 0

contatore_form = st.session_state["catalogo_form_counter"]

with st.container(border=True):
    st.markdown("#### Aggiungi nuovo prodotto")
    st.caption("Suggerimento: includi il materiale nel nome, es. \"Finestra Alluminio\", per riconoscerlo facilmente.")

    nome_p = st.text_input("Nome prodotto", key=f"nuovo_prod_nome_{contatore_form}", placeholder="Es. Finestra Alluminio")

    col_mat, col_prezzo = st.columns(2)
    with col_mat:
        materiale_p = st.selectbox("Materiale", MATERIALI, key=f"nuovo_prod_materiale_{contatore_form}")
    with col_prezzo:
        prezzo_p = st.number_input("Prezzo standard (€/m²)", min_value=0.0, step=10.0, value=400.0, key=f"nuovo_prod_prezzo_{contatore_form}")

    descrizione_p = st.text_area("Descrizione", key=f"nuovo_prod_descr_{contatore_form}", height=80)
    foto_p = st.file_uploader("Foto prodotto (opzionale)", type=["jpg", "jpeg", "png"], key=f"nuovo_prod_foto_{contatore_form}")

    if st.button("Aggiungi prodotto", icon=":material/add:", type="primary", use_container_width=True):
        if not nome_p:
            st.warning("Inserisci almeno il nome del prodotto.")
        else:
            foto_url = None
            if foto_p is not None:
                foto_url = carica_foto_prodotto(foto_p.getvalue(), foto_p.type, foto_p.name)
            supabase.table("catalogo_prodotti").insert({
                "nome": nome_p,
                "descrizione": descrizione_p,
                "prezzo_standard_mq": prezzo_p,
                "materiale": materiale_p,
                "foto_url": foto_url
            }).execute()
            st.session_state["catalogo_form_counter"] += 1
            st.success("Prodotto aggiunto!")
            st.rerun()

st.markdown("<div class='section-spacer'></div>", unsafe_allow_html=True)
st.markdown("### Prodotti nel catalogo")

ricerca = st.text_input("Cerca prodotto per nome", key="ricerca_catalogo", placeholder="Cerca prodotto per nome", label_visibility="collapsed")

prodotti = supabase.table("catalogo_prodotti").select("*").order("nome").execute().data or []

if ricerca:
    prodotti = [p for p in prodotti if ricerca.lower() in p['nome'].lower()]

if not prodotti:
    st.markdown(
        "<div class='empty-state'>"
        f"<div class='empty-state-title'>{'Nessun risultato' if ricerca else 'Nessun prodotto ancora'}</div>"
        f"<div class='empty-state-description'>{'Nessun prodotto trovato con questo nome.' if ricerca else 'Aggiungine uno qui sopra per iniziare.'}</div>"
        "</div>",
        unsafe_allow_html=True
    )
else:
    gruppi = {}
    for p in prodotti:
        mat = p.get("materiale") or "Non specificato"
        gruppi.setdefault(mat, []).append(p)

    for mat in list(MATERIALI) + ["Non specificato"]:
        if mat not in gruppi:
            continue

        with st.expander(f"Prodotti in {mat} ({len(gruppi[mat])})", expanded=False):
            with st.container(border=True):
                for idx, p in enumerate(gruppi[mat]):
                    chiave_dettagli = f"mostra_dettagli_{p['id']}"
                    if chiave_dettagli not in st.session_state:
                        st.session_state[chiave_dettagli] = False

                    col_foto, col_info, col_toggle = st.columns([1, 3, 1])
                    with col_foto:
                        if p.get('foto_url'):
                            st.image(p['foto_url'], width=64)
                        else:
                            st.caption("—")
                    with col_info:
                        st.markdown(f"<span style='font-weight:600; color:var(--color-title); font-size:0.88rem;'>{p['nome']}</span>", unsafe_allow_html=True)
                        prezzo_str = f"{p['prezzo_standard_mq']:.2f} €/m²" if p.get('prezzo_standard_mq') is not None else "Prezzo non impostato"
                        st.markdown(f"<span class='num-tabular' style='color:var(--color-text-secondary); font-size:0.8rem;'>{prezzo_str}</span>", unsafe_allow_html=True)
                    with col_toggle:
                        etichetta_bottone = "Chiudi" if st.session_state[chiave_dettagli] else "Dettagli"
                        icona_bottone = "close" if st.session_state[chiave_dettagli] else "tune"
                        if st.button(etichetta_bottone, icon=f":material/{icona_bottone}:", key=f"toggle_{p['id']}", use_container_width=True):
                            st.session_state[chiave_dettagli] = not st.session_state[chiave_dettagli]
                            st.rerun()

                    if st.session_state[chiave_dettagli]:
                        st.markdown(card_divider(), unsafe_allow_html=True)
                        nuovo_nome = st.text_input("Nome", value=p['nome'], key=f"nome_{p['id']}")

                        col_m2, col_pr2 = st.columns(2)
                        with col_m2:
                            indice_mat = MATERIALI.index(p['materiale']) if p.get('materiale') in MATERIALI else 0
                            nuovo_materiale = st.selectbox("Materiale", MATERIALI, index=indice_mat, key=f"mat_{p['id']}")
                        with col_pr2:
                            nuovo_prezzo = st.number_input("Prezzo (€/m²)", value=float(p['prezzo_standard_mq'] or 0), min_value=0.0, step=10.0, key=f"prezzo_{p['id']}")

                        nuova_descr = st.text_area("Descrizione", value=p.get('descrizione') or "", key=f"descr_{p['id']}", height=70)
                        nuova_foto = st.file_uploader("Cambia foto", type=["jpg", "jpeg", "png"], key=f"foto_{p['id']}")

                        col_salva, col_elimina = st.columns(2)
                        with col_salva:
                            if st.button("Salva", icon=":material/save:", key=f"salva_{p['id']}", use_container_width=True, type="primary"):
                                aggiornamento = {
                                    "nome": nuovo_nome,
                                    "materiale": nuovo_materiale,
                                    "prezzo_standard_mq": nuovo_prezzo,
                                    "descrizione": nuova_descr
                                }
                                if nuova_foto is not None:
                                    aggiornamento["foto_url"] = carica_foto_prodotto(nuova_foto.getvalue(), nuova_foto.type, nuova_foto.name)
                                supabase.table("catalogo_prodotti").update(aggiornamento).eq("id", p['id']).execute()
                                st.success("Aggiornato!")
                                st.rerun()
                        with col_elimina:
                            with st.container(key=f"dangerwrap_elimina_{p['id']}"):
                                if st.button("Elimina", icon=":material/delete:", key=f"elimina_{p['id']}", use_container_width=True):
                                    supabase.table("catalogo_prodotti").delete().eq("id", p['id']).execute()
                                    st.rerun()

                    if idx < len(gruppi[mat]) - 1:
                        st.markdown(card_divider(), unsafe_allow_html=True)
