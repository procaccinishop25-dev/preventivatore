import streamlit as st
from services.supabase import supabase
from services.theme import apply_custom_theme, badge
import uuid


TIPOLOGIE = ["Finestra", "Porta-finestra", "Portoncino", "Scorrevole", "Altro"]
MATERIALI = ["Alluminio", "PVC", "Ferro"]


def carica_foto_prodotto(bytes_data, tipo, nome_file):
    nome_unico = f"catalogo/{uuid.uuid4().hex[:8]}_{nome_file}"
    supabase.storage.from_("foto").upload(nome_unico, bytes_data, {"content-type": tipo, "upsert": "true"})
    return supabase.storage.from_("foto").get_public_url(nome_unico)


st.set_page_config(page_title="Catalogo", page_icon="🛒")
apply_custom_theme()

st.markdown(
    "<div class='page-header'><h1>🛒 Catalogo</h1>"
    "<p>I prodotti selezionabili quando aggiungi un infisso a un progetto.</p></div>",
    unsafe_allow_html=True
)

with st.container(border=True):
    st.markdown("#### ➕ Aggiungi nuovo prodotto")

    nome_p = st.text_input("Nome prodotto", key="nuovo_prod_nome")

    col_tip, col_mat, col_prezzo = st.columns(3)
    with col_tip:
        tipologia_p = st.selectbox("Tipologia", TIPOLOGIE, key="nuovo_prod_tipologia")
    with col_mat:
        materiale_p = st.selectbox("Materiale", MATERIALI, key="nuovo_prod_materiale")
    with col_prezzo:
        prezzo_p = st.number_input("Prezzo standard (€/m²)", min_value=0.0, step=10.0, value=400.0, key="nuovo_prod_prezzo")

    descrizione_p = st.text_area("Descrizione", key="nuovo_prod_descr", height=80)
    foto_p = st.file_uploader("Foto prodotto (opzionale)", type=["jpg", "jpeg", "png"], key="nuovo_prod_foto")

    if st.button("Aggiungi prodotto", type="primary", use_container_width=True):
        if not nome_p:
            st.warning("Inserisci almeno il nome del prodotto.")
        else:
            foto_url = None
            if foto_p is not None:
                foto_url = carica_foto_prodotto(foto_p.getvalue(), foto_p.type, foto_p.name)
            supabase.table("catalogo_prodotti").insert({
                "nome": nome_p,
                "tipologia": tipologia_p,
                "descrizione": descrizione_p,
                "prezzo_standard_mq": prezzo_p,
                "materiale": materiale_p,
                "foto_url": foto_url
            }).execute()
            st.success("Prodotto aggiunto!")
            st.rerun()

st.markdown("<div class='section-spacer'></div>", unsafe_allow_html=True)
st.markdown("#### 📋 Prodotti nel catalogo")

prodotti = supabase.table("catalogo_prodotti").select("*").order("nome").execute().data or []

if not prodotti:
    st.info("Nessun prodotto ancora. Aggiungine uno qui sopra.")
else:
    # Raggruppa: tipologia -> materiale -> lista prodotti
    gruppi = {}
    for p in prodotti:
        tip = p.get("tipologia") or "Non specificata"
        mat = p.get("materiale") or "Non specificato"
        gruppi.setdefault(tip, {}).setdefault(mat, []).append(p)

    for tip in list(TIPOLOGIE) + ["Non specificata"]:
        if tip not in gruppi:
            continue
        conteggio_tip = sum(len(lista) for lista in gruppi[tip].values())

        with st.expander(f"📁 {tip} ({conteggio_tip})", expanded=False):
            for mat in list(MATERIALI) + ["Non specificato"]:
                if mat not in gruppi[tip]:
                    continue

                st.markdown(
                    f"<div style='font-weight:600; color:var(--color-text-secondary); font-size:0.85rem; "
                    f"text-transform:uppercase; letter-spacing:0.03em; margin:0.6rem 0 0.4rem 0;'>🎨 {mat}</div>",
                    unsafe_allow_html=True
                )

                for p in gruppi[tip][mat]:
                    chiave_dettagli = f"mostra_dettagli_{p['id']}"
                    if chiave_dettagli not in st.session_state:
                        st.session_state[chiave_dettagli] = False

                    with st.container(border=True):
                        col_foto, col_info, col_toggle = st.columns([1, 3, 1])
                        with col_foto:
                            if p.get('foto_url'):
                                st.image(p['foto_url'], width=70)
                            else:
                                st.caption("Nessuna foto")
                        with col_info:
                            st.markdown(f"**{p['nome']}**")
                            st.caption(f"{p['prezzo_standard_mq']:.2f} €/m²" if p.get('prezzo_standard_mq') is not None else "Prezzo non impostato")
                        with col_toggle:
                            etichetta_bottone = "Chiudi" if st.session_state[chiave_dettagli] else "Dettagli"
                            if st.button(etichetta_bottone, key=f"toggle_{p['id']}", use_container_width=True):
                                st.session_state[chiave_dettagli] = not st.session_state[chiave_dettagli]
                                st.rerun()

                        if st.session_state[chiave_dettagli]:
                            st.divider()
                            nuovo_nome = st.text_input("Nome", value=p['nome'], key=f"nome_{p['id']}")

                            col_t2, col_m2, col_pr2 = st.columns(3)
                            with col_t2:
                                indice_tip = TIPOLOGIE.index(p['tipologia']) if p.get('tipologia') in TIPOLOGIE else 0
                                nuova_tipologia = st.selectbox("Tipologia", TIPOLOGIE, index=indice_tip, key=f"tip_{p['id']}")
                            with col_m2:
                                indice_mat = MATERIALI.index(p['materiale']) if p.get('materiale') in MATERIALI else 0
                                nuovo_materiale = st.selectbox("Materiale", MATERIALI, index=indice_mat, key=f"mat_{p['id']}")
                            with col_pr2:
                                nuovo_prezzo = st.number_input("Prezzo (€/m²)", value=float(p['prezzo_standard_mq'] or 0), min_value=0.0, step=10.0, key=f"prezzo_{p['id']}")

                            nuova_descr = st.text_area("Descrizione", value=p.get('descrizione') or "", key=f"descr_{p['id']}", height=70)
                            nuova_foto = st.file_uploader("Cambia foto", type=["jpg", "jpeg", "png"], key=f"foto_{p['id']}")

                            col_salva, col_elimina = st.columns(2)
                            with col_salva:
                                if st.button("💾 Salva", key=f"salva_{p['id']}", use_container_width=True, type="primary"):
                                    aggiornamento = {
                                        "nome": nuovo_nome,
                                        "tipologia": nuova_tipologia,
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
                                if st.button("🗑️ Elimina", key=f"elimina_{p['id']}", use_container_width=True):
                                    supabase.table("catalogo_prodotti").delete().eq("id", p['id']).execute()
                                    st.rerun()
