import streamlit as st
from services.supabase import supabase

st.set_page_config(page_title="Nuovo Preventivo", page_icon="💰")

st.title("💰 Nuovo Preventivo")

progetti = supabase.table("progetti").select("id, indirizzo, citta, clienti(nome, cognome_azienda)").execute()

if not progetti.data:
    st.info("Nessun progetto disponibile.")
    st.page_link("pages/1_Nuovo_Progetto.py", label="Crea un progetto →", icon="📋")
else:
    opzioni = {
        f"{p['clienti']['nome']} {p['clienti']['cognome_azienda']} - {p['indirizzo']}, {p['citta']}": p['id']
        for p in progetti.data
    }
    scelta = st.selectbox("Seleziona progetto", list(opzioni.keys()))
    progetto_id = opzioni[scelta]

    infissi = supabase.table("infissi").select("*").eq("progetto_id", progetto_id).order("numero_infisso").execute()

    if not infissi.data:
        st.warning("Questo progetto non ha ancora infissi. Aggiungili prima di creare un preventivo.")
        st.page_link("pages/2_Progetti.py", label="Vai a I Miei Progetti →", icon="📁")
    else:
        tipologie = {}
        for inf in infissi.data:
            t = inf['tipologia']
            tipologie.setdefault(t, {"mq_totali": 0.0, "count": 0})
            tipologie[t]["mq_totali"] += inf['mq'] * inf['quantita']
            tipologie[t]["count"] += inf['quantita']

        st.subheader("💶 Prezzo base per tipologia")
        prezzi_tipologia = {}
        for t, info in tipologie.items():
            prezzi_tipologia[t] = st.number_input(
                f"{t} — {info['count']} pezzi, {info['mq_totali']:.2f} m² totali (€/m²)",
                min_value=0.0, value=400.0, step=10.0, key=f"prezzo_{t}"
            )

        st.divider()
        st.subheader("➕ Maggiorazioni")
        maggiorazioni_disponibili = supabase.table("maggiorazioni").select("*").execute()

        maggiorazioni_selezionate = []
        if maggiorazioni_disponibili.data:
            for m in maggiorazioni_disponibili.data:
                etichetta_tipo = {"mq": "€/m²", "fisso": "€ fisso", "percentuale": "%"}.get(m['tipo'], m['tipo'])
                selezionata = st.checkbox(f"{m['descrizione']} (+{m['importo']} {etichetta_tipo})", key=f"magg_{m['id']}")
                if selezionata:
                    maggiorazioni_selezionate.append(m)
        else:
            st.caption("Nessuna maggiorazione predefinita configurata.")

        st.divider()

        totale_base = sum(prezzi_tipologia[t] * info["mq_totali"] for t, info in tipologie.items())
        mq_totale_progetto = sum(info["mq_totali"] for info in tipologie.values())

        totale_maggiorazioni = 0.0
        for m in maggiorazioni_selezionate:
            if m['tipo'] == 'mq':
                totale_maggiorazioni += m['importo'] * mq_totale_progetto
            elif m['tipo'] == 'fisso':
                totale_maggiorazioni += m['importo']
            elif m['tipo'] == 'percentuale':
                totale_maggiorazioni += totale_base * (m['importo'] / 100)

        totale_finale = totale_base + totale_maggiorazioni

        st.subheader("📊 Riepilogo")
        col1, col2, col3 = st.columns(3)
        col1.metric("Totale base", f"{totale_base:.2f} €")
        col2.metric("Maggiorazioni", f"{totale_maggiorazioni:.2f} €")
        col3.metric("Totale finale", f"{totale_finale:.2f} €")

        if st.button("💾 Salva preventivo"):
            preventivo = supabase.table("preventivi").insert({
                "progetto_id": progetto_id,
                "totale_base": totale_base,
                "totale_finale": totale_finale,
                "stato": "bozza"
            }).execute()
            preventivo_id = preventivo.data[0]["id"]

            for t, prezzo in prezzi_tipologia.items():
                supabase.table("preventivo_prezzi_tipologia").insert({
                    "preventivo_id": preventivo_id,
                    "tipologia": t,
                    "prezzo_mq": prezzo
                }).execute()

            for m in maggiorazioni_selezionate:
                supabase.table("preventivo_maggiorazioni").insert({
                    "preventivo_id": preventivo_id,
                    "maggiorazione_id": m["id"]
                }).execute()

            st.success(f"Preventivo salvato! Totale: {totale_finale:.2f} €")
            st.balloons()
