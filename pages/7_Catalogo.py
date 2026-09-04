import streamlit as st
from services.supabase import supabase
from services.theme import apply_custom_theme, badge
import uuid


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

    col_mat, col_prezzo = st.columns(2)
    with col_mat:
        materiale_p = st.selectbox("Materiale", ["Alluminio", "PVC", "Ferro"], key="nuovo_prod_materiale")
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
                "descrizione": descrizione_p,
                "prezzo_standard_mq": prezzo_p,
                "materiale": materiale_p,
                "foto_url": foto_url
            }).execute()
            st.success("Prodotto aggiunto!")
            st.rerun()

st.markdown("<div class='section-spacer'></div>", unsafe_allow_html=True)
st.markdown(f"#### 📋 Prodotti nel catalogo")

prodotti = supabase.table("catalogo_prodotti").select("*").order("nome").execute()

if not prodotti.data:
    st.info("Nessun prodotto ancora. Aggiungine uno qui sopra.")
else:
    for p in prodotti.data:
        with st.container(border=True):
            col_foto, col_campi, col_azioni = st.columns([1, 3, 1])

            with col_foto:
                if p.get('foto_url'):
                    st.image(p['foto_url'], width=90)
                else:
                    st.caption("Nessuna foto")

            with col_campi:
                nuovo_nome = st.text_input("Nome", value=p['nome'], key=f"nome_{p['id']}")
                col_m, col_pr = st.columns(2)
                with col_m:
                    indice_mat = ["Alluminio", "PVC", "Ferro"].index(p['materiale']) if p.get('materiale') in ["Alluminio", "PVC", "Ferro"] else 0
                    nuovo_materiale = st.selectbox("Materiale", ["Alluminio", "PVC", "Ferro"], index=indice_mat, key=f"mat_{p['id']}")
                with col_pr:
                    nuovo_prezzo = st.number_input("Prezzo (€/m²)", value=float(p['prezzo_standard_mq'] or 0), min_value=0.0, step=10.0, key=f"prezzo_{p['id']}")
                nuova_descr = st.text_area("Descrizione", value=p.get('descrizione') or "", key=f"descr_{p['id']}", height=70)

                nuova_foto = st.file_uploader("Cambia foto", type=["jpg", "jpeg", "png"], key=f"foto_{p['id']}")

            with col_azioni:
                st.write("")
                if st.button("💾 Salva", key=f"salva_{p['id']}", use_container_width=True, type="primary"):
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
                if st.button("🗑️ Elimina", key=f"elimina_{p['id']}", use_container_width=True):
                    supabase.table("catalogo_prodotti").delete().eq("id", p['id']).execute()
                    st.rerun()
