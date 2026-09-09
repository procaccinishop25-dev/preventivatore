import streamlit as st
from services.supabase import supabase
from services.theme import apply_custom_theme, badge, card_divider, material_icon
from services.pdf import genera_preventivo_rapido, trigger_download_automatico, dialog_dopo_generazione_preventivo
import re


def slug(testo):
    testo = (testo or "").strip().replace(" ", "_")
    return re.sub(r"[^A-Za-z0-9_-]", "", testo)


@st.dialog(":material/warning: Elimina progetto")
def conferma_eliminazione(progetto_id, nome_completo):
    st.warning(
        f"Stai per eliminare definitivamente il progetto di **{nome_completo}**, "
        f"con tutti i suoi infissi e le foto caricate. Questa azione non si può annullare."
    )
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Sì, elimina", icon=":material/delete:", type="primary", use_container_width=True):
            cartella_progetto = slug(nome_completo)

            file_esistenti = supabase.storage.from_("foto").list(cartella_progetto)
            if file_esistenti:
                percorsi = [f"{cartella_progetto}/{f['name']}" for f in file_esistenti]
                supabase.storage.from_("foto").remove(percorsi)

            supabase.table("infissi").delete().eq("progetto_id", progetto_id).execute()

            preventivi_collegati = supabase.table("preventivi").select("id").eq("progetto_id", progetto_id).execute()
            for prev in preventivi_collegati.data:
                supabase.table("preventivo_maggiorazioni").delete().eq("preventivo_id", prev["id"]).execute()
            supabase.table("preventivi").delete().eq("progetto_id", progetto_id).execute()

            supabase.table("progetti").delete().eq("id", progetto_id).execute()

            st.success("Progetto eliminato completamente.")
            st.rerun()
    with col2:
        if st.button("Annulla", use_container_width=True):
            st.rerun()


st.set_page_config(page_title="Progetti", page_icon="📁")
apply_custom_theme()

st.markdown(
    f"<div class='page-header'><h1>Progetti</h1>"
    "<p>Riprendi un progetto o generane subito il preventivo.</p></div>",
    unsafe_allow_html=True
)

progetti = supabase.table("progetti").select("*, clienti(nome, cognome_azienda, telefono, email)").order("created_at", desc=True).execute()

if not progetti.data:
    st.markdown(
        "<div class='empty-state'>"
        "<div class='empty-state-title'>Nessun progetto ancora</div>"
        "<div class='empty-state-description'>Crea il tuo primo progetto per iniziare a generare preventivi.</div>"
        "</div>",
        unsafe_allow_html=True
    )
    st.page_link("pages/1_Nuovo_Progetto.py", label="Nuovo progetto", icon=":material/note_add:")
else:
    ricerca = st.text_input("Cerca per cliente o città", placeholder="Cerca per cliente o città", label_visibility="collapsed")

    st.markdown("<div class='spacer-sm'></div>", unsafe_allow_html=True)

    progetti_filtrati = []
    for p in progetti.data:
        nome_completo = f"{p['clienti']['nome']} {p['clienti']['cognome_azienda']}"
        if ricerca and ricerca.lower() not in nome_completo.lower() and ricerca.lower() not in (p['citta'] or "").lower():
            continue
        progetti_filtrati.append((p, nome_completo))

    if not progetti_filtrati:
        st.markdown(
            "<div class='empty-state'>"
            "<div class='empty-state-title'>Nessun risultato</div>"
            "<div class='empty-state-description'>Nessun progetto corrisponde alla ricerca.</div>"
            "</div>",
            unsafe_allow_html=True
        )
    else:
        with st.container(border=True):
            for idx, (p, nome_completo) in enumerate(progetti_filtrati):
                infissi = supabase.table("infissi").select("id, mq, quantita").eq("progetto_id", p['id']).execute()
                num_infissi = len(infissi.data)
                mq_totali = sum(i['mq'] * i['quantita'] for i in infissi.data) if infissi.data else 0

                col1, col2, col3, col4 = st.columns([2.8, 1.6, 1.1, 1.8])
                with col1:
                    st.markdown(f"<span style='font-weight:600; color:var(--color-title); font-size:0.88rem;'>{nome_completo}</span>", unsafe_allow_html=True)
                    st.markdown(f"<span style='color:var(--color-text-secondary); font-size:0.8rem;'>{p['indirizzo']}, {p['citta']}</span>", unsafe_allow_html=True)
                with col2:
                    st.markdown(
                        f"<span style='color:var(--color-text); font-size:0.85rem;'>{num_infissi} infissi</span><br>"
                        f"<span class='num-tabular' style='color:var(--color-text-secondary); font-size:0.8rem;'>{mq_totali:.2f} m²</span>",
                        unsafe_allow_html=True
                    )
                with col3:
                    st.markdown(badge((p.get('stato') or "—").capitalize(), "neutral"), unsafe_allow_html=True)
                with col4:
                    b1, b2, b3 = st.columns(3)
                    with b1:
                        if st.button("", icon=":material/arrow_forward:", key=f"apri_{p['id']}", use_container_width=True, help="Apri progetto"):
                            st.session_state["progetto_corrente_id"] = p['id']
                            st.session_state["progetto_corrente_nome"] = nome_completo
                            st.switch_page("pages/5_Gestione_Progetto.py")
                    with b2:
                        if st.button("", icon=":material/payments:", key=f"genera_{p['id']}", use_container_width=True, help="Genera preventivo"):
                            if num_infissi == 0:
                                st.warning("Aggiungi almeno un infisso prima di generare il preventivo.")
                            else:
                                with st.spinner("Generazione preventivo e PDF in corso..."):
                                    preventivo_id, pdf_buffer, contesto = genera_preventivo_rapido(p['id'], p, p['clienti'])
                                trigger_download_automatico(pdf_buffer.getvalue(), f"preventivo_{slug(nome_completo)}.pdf")
                                dialog_dopo_generazione_preventivo(
                                    preventivo_id, pdf_buffer, contesto, p['clienti'], nome_completo,
                                    p['indirizzo'], p['citta']
                                )
                    with b3:
                        st.markdown("<div class='btn-ghost'>", unsafe_allow_html=True)
                        if st.button("", icon=":material/delete:", key=f"elimina_{p['id']}", use_container_width=True, help="Elimina"):
                            conferma_eliminazione(p['id'], nome_completo)
                        st.markdown("</div>", unsafe_allow_html=True)

                if idx < len(progetti_filtrati) - 1:
                    st.markdown(card_divider(), unsafe_allow_html=True)
