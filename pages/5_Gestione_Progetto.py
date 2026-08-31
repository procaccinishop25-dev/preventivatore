import streamlit as st
from services.supabase import supabase
import pandas as pd
import io
import re


def slug(testo):
    testo = (testo or "").strip().replace(" ", "_")
    return re.sub(r"[^A-Za-z0-9_-]", "", testo)


def genera_excel_preventivo(nome_cliente, indirizzo, citta, righe_infissi, righe_maggiorazioni, totale_base, totale_maggiorazioni, totale_finale, mq_totale_progetto):
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df_infissi = pd.DataFrame(righe_infissi)
        df_infissi.to_excel(writer, sheet_name='Dettaglio Infissi', index=False)

        righe_riepilogo = [
            {"Voce": "Cliente", "Valore": nome_cliente},
            {"Voce": "Indirizzo", "Valore": f"{indirizzo}, {citta}"},
            {"Voce": "Superficie totale (m²)", "Valore": round(mq_totale_progetto, 2)},
            {"Voce": "Totale base (€)", "Valore": round(totale_base, 2)},
        ]
        for r in righe_maggiorazioni:
            righe_riepilogo.append({"Voce": f"Maggiorazione: {r['Maggiorazione']}", "Valore": r['Importo €']})
        righe_riepilogo.append({"Voce": "Totale maggiorazioni (€)", "Valore": round(totale_maggiorazioni, 2)})
        righe_riepilogo.append({"Voce": "TOTALE FINALE (€)", "Valore": round(totale_finale, 2)})
        df_riepilogo = pd.DataFrame(righe_riepilogo)
        df_riepilogo.to_excel(writer, sheet_name='Riepilogo', index=False)

    buffer.seek(0)
    return buffer


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
    progetto_selezionato = next(p for p in progetti.data if p['id'] == progetto_id)
    nome_cliente_progetto = f"{progetto_selezionato['clienti']['nome']} {progetto_selezionato['clienti']['cognome_azienda']}"

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

        righe_maggiorazioni = []
        totale_maggiorazioni = 0.0
        for m in maggiorazioni_selezionate:
            if m['tipo'] == 'mq':
                importo_calc = m['importo'] * mq_totale_progetto
            elif m['tipo'] == 'fisso':
                importo_calc = m['importo']
            elif m['tipo'] == 'percentuale':
                importo_calc = totale_base * (m['importo'] / 100)
            else:
                importo_calc = 0
            totale_maggiorazioni += importo_calc
            righe_maggiorazioni.append({"Maggiorazione": m['descrizione'], "Importo €": round(importo_calc, 2)})

        totale_finale = totale_base + totale_maggiorazioni

        st.subheader("📊 Riepilogo")
        col1, col2, col3 = st.columns(3)
        col1.metric("Totale base", f"{totale_base:.2f} €")
        col2.metric("Maggiorazioni", f"{totale_maggiorazioni:.2f} €")
        col3.metric("Totale finale", f"{totale_finale:.2f} €")

        st.divider()
        st.subheader("📋 Dettaglio infissi")

        righe_infissi = []
        for inf in infissi.data:
            prezzo = prezzi_tipologia.get(inf['tipologia'], 0)
            subtotale = inf['mq'] * inf['quantita'] * prezzo
            righe_infissi.append({
                "Infisso": inf.get('nome') or f"{inf['tipologia']} {inf.get('numero_infisso', '')}",
                "Misure": f"{inf['larghezza_cm']}x{inf['altezza_cm']} cm",
                "Quantità": inf['quantita'],
                "m²": round(inf['mq'] * inf['quantita'], 2),
                "Prezzo €/m²": prezzo,
                "Subtotale €": round(subtotale, 2)
            })

        st.dataframe(righe_infissi, use_container_width=True, hide_index=True)

        if righe_maggiorazioni:
            st.subheader("📋 Dettaglio maggiorazioni")
            st.dataframe(righe_maggiorazioni, use_container_width=True, hide_index=True)

        st.divider()

        excel_buffer = genera_excel_preventivo(
            nome_cliente_progetto, progetto_selezionato['indirizzo'], progetto_selezionato['citta'],
            righe_infissi, righe_maggiorazioni, totale_base, totale_maggiorazioni, totale_finale, mq_totale_progetto
        )
        st.download_button(
            "📥 Scarica riepilogo Excel",
            data=excel_buffer,
            file_name=f"preventivo_{slug(nome_cliente_progetto)}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

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
