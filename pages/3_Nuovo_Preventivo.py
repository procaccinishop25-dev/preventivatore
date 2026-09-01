import streamlit as st
from services.supabase import supabase
import pandas as pd
import io
import re


def slug(testo):
    testo = (testo or "").strip().replace(" ", "_")
    return re.sub(r"[^A-Za-z0-9_-]", "", testo)


def format_num(x, decimali=2):
    return f"{x:.{decimali}f}".replace(".", ",")


def format_euro(x):
    s = f"{x:,.2f}"
    s = s.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{s} €"


def genera_excel_preventivo(nome_cliente, indirizzo, citta, righe_riepilogo_excel, mq_totale_progetto):
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df_riepilogo = pd.DataFrame(righe_riepilogo_excel)
        df_riepilogo.to_excel(writer, sheet_name='Riepilogo', index=False)

        df_intestazione = pd.DataFrame([
            {"Campo": "Cliente", "Valore": nome_cliente},
            {"Campo": "Indirizzo", "Valore": f"{indirizzo}, {citta}"},
            {"Campo": "Superficie totale (m²)", "Valore": round(mq_totale_progetto, 2)},
        ])
        df_intestazione.to_excel(writer, sheet_name='Dati progetto', index=False)

    buffer.seek(0)
    return buffer


@st.dialog("Applica maggiorazione")
def dialog_applicazione_maggiorazione(m, lista_infissi):
    st.write(f"Vuoi applicare **{m['descrizione']}** a tutti gli infissi o solo a uno specifico?")

    scelta = st.radio(
        "Applicazione",
        ["Tutti gli infissi", "Un infisso specifico"],
        key=f"dialog_scelta_{m['id']}"
    )

    infisso_id = None
    infisso_nome = None
    if scelta == "Un infisso specifico":
        opzioni_infissi = {f"{inf.get('nome') or inf['tipologia']}": inf['id'] for inf in lista_infissi}
        nome_scelto = st.selectbox("Seleziona infisso", list(opzioni_infissi.keys()), key=f"dialog_infisso_{m['id']}")
        infisso_id = opzioni_infissi[nome_scelto]
        infisso_nome = nome_scelto

    if st.button("Conferma", key=f"dialog_conferma_{m['id']}"):
        st.session_state["magg_applicazione"][m['id']] = {"infisso_id": infisso_id, "infisso_nome": infisso_nome}
        st.rerun()


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
        st.subheader("➕ Maggiorazioni predefinite")

        if "magg_applicazione" not in st.session_state:
            st.session_state["magg_applicazione"] = {}
        if "magg_prev_stato" not in st.session_state:
            st.session_state["magg_prev_stato"] = {}

        maggiorazioni_disponibili = supabase.table("maggiorazioni").select("*").order("descrizione").execute()

        maggiorazioni_selezionate = []
        if maggiorazioni_disponibili.data:
            for m in maggiorazioni_disponibili.data:
                etichetta_tipo = {"mq": "€/m²", "fisso": "€ fisso", "percentuale": "%"}.get(m['tipo'], m['tipo'])

                stato_precedente = st.session_state["magg_prev_stato"].get(m['id'], False)
                selezionata = st.checkbox(f"{m['descrizione']} (+{m['importo']} {etichetta_tipo})", key=f"magg_{m['id']}")
                appena_selezionata = selezionata and not stato_precedente
                st.session_state["magg_prev_stato"][m['id']] = selezionata

                if not selezionata:
                    st.session_state["magg_applicazione"].pop(m['id'], None)

                if appena_selezionata:
                    dialog_applicazione_maggiorazione(m, infissi.data)

                if selezionata:
                    info_appl = st.session_state["magg_applicazione"].get(m['id'])
                    col_info, col_modifica = st.columns([4, 1])
                    with col_info:
                        if info_appl and info_appl.get('infisso_id'):
                            st.caption(f"↳ applicata solo su: **{info_appl['infisso_nome']}**")
                        else:
                            st.caption("↳ applicata su tutti gli infissi")
                    with col_modifica:
                        if st.button("✏️", key=f"modifica_appl_{m['id']}"):
                            dialog_applicazione_maggiorazione(m, infissi.data)
                    maggiorazioni_selezionate.append(m)
        else:
            st.caption("Nessuna maggiorazione predefinita configurata.")
        st.page_link("pages/6_Maggiorazioni.py", label="Aggiungi una nuova maggiorazione", icon="➕")

        st.divider()

        totale_base = sum(prezzi_tipologia[t] * info["mq_totali"] for t, info in tipologie.items())
        mq_totale_progetto = sum(info["mq_totali"] for info in tipologie.values())

        righe_riepilogo = []

        for t, info in tipologie.items():
            prezzo = prezzi_tipologia[t]
            subtotale = info["mq_totali"] * prezzo
            righe_riepilogo.append({
                "voce": t,
                "calcolo": f"{format_num(info['mq_totali'])} m² × {format_num(prezzo)} €/m²",
                "totale": subtotale,
                "bold": False
            })

        righe_riepilogo.append({"voce": "Totale base", "calcolo": "", "totale": totale_base, "bold": True})

        totale_maggiorazioni = 0.0

        for m in maggiorazioni_selezionate:
            info_appl = st.session_state["magg_applicazione"].get(m['id'], {})
            infisso_id_appl = info_appl.get('infisso_id')

            if infisso_id_appl:
                infisso_rif = next((i for i in infissi.data if i['id'] == infisso_id_appl), None)
                base_mq = (infisso_rif['mq'] * infisso_rif['quantita']) if infisso_rif else 0
                base_valore = (infisso_rif['mq'] * infisso_rif['quantita'] * prezzi_tipologia.get(infisso_rif['tipologia'], 0)) if infisso_rif else 0
                riferimento = info_appl.get('infisso_nome')
            else:
                base_mq = mq_totale_progetto
                base_valore = totale_base
                riferimento = "tutti gli infissi"

            if m['tipo'] == 'mq':
                importo_calc = m['importo'] * base_mq
                calcolo_str = f"{format_num(base_mq)} m² ({riferimento}) × {format_num(m['importo'])} €/m²"
            elif m['tipo'] == 'fisso':
                importo_calc = m['importo']
                calcolo_str = f"Importo fisso ({riferimento})"
            elif m['tipo'] == 'percentuale':
                importo_calc = base_valore * (m['importo'] / 100)
                calcolo_str = f"{format_num(m['importo'])}% su {format_euro(base_valore)} ({riferimento})"
            else:
                importo_calc = 0
                calcolo_str = ""

            totale_maggiorazioni += importo_calc
            righe_riepilogo.append({"voce": m['descrizione'], "calcolo": calcolo_str, "totale": importo_calc, "bold": False})

        righe_riepilogo.append({"voce": "Maggiorazioni", "calcolo": "", "totale": totale_maggiorazioni, "bold": True})

        subtotale_pre_sconto = totale_base + totale_maggiorazioni

        # --- Sconto ---
        st.subheader("💸 Sconto (opzionale)")
        col_sconto_val, col_sconto_tipo = st.columns(2)
        with col_sconto_val:
            valore_sconto = st.number_input("Valore sconto", min_value=0.0, step=1.0, key="valore_sconto")
        with col_sconto_tipo:
            tipo_sconto = st.selectbox("Tipo sconto", ["Nessuno", "€ fisso", "%"], key="tipo_sconto")

        sconto_calcolato = 0.0
        if tipo_sconto == "€ fisso":
            sconto_calcolato = valore_sconto
        elif tipo_sconto == "%":
            sconto_calcolato = subtotale_pre_sconto * (valore_sconto / 100)

        if sconto_calcolato > 0:
            calcolo_sconto_str = (
                f"Importo fisso" if tipo_sconto == "€ fisso"
                else f"{format_num(valore_sconto)}% su {format_euro(subtotale_pre_sconto)}"
            )
            righe_riepilogo.append({"voce": "Sconto", "calcolo": calcolo_sconto_str, "totale": -sconto_calcolato, "bold": False})

        totale_finale = subtotale_pre_sconto - sconto_calcolato

        righe_riepilogo.append({"voce": "Totale finale", "calcolo": "", "totale": totale_finale, "bold": True})

        st.divider()
        st.subheader("📊 Riepilogo — calcolo automatico")

        righe_md = ["| Voce | Calcolo | Totale |", "|---|---|---|"]
        for r in righe_riepilogo:
            voce = f"**{r['voce']}**" if r['bold'] else r['voce']
            totale_fmt = f"**{format_euro(r['totale'])}**" if r['bold'] else format_euro(r['totale'])
            righe_md.append(f"| {voce} | {r['calcolo']} | {totale_fmt} |")

        st.markdown("\n".join(righe_md))

        st.divider()

        righe_riepilogo_excel = [
            {"Voce": r["voce"], "Calcolo": r["calcolo"], "Totale €": round(r["totale"], 2)}
            for r in righe_riepilogo
        ]

        excel_buffer = genera_excel_preventivo(
            nome_cliente_progetto, progetto_selezionato['indirizzo'], progetto_selezionato['citta'],
            righe_riepilogo_excel, mq_totale_progetto
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
                "sconti": sconto_calcolato,
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
                info_appl = st.session_state["magg_applicazione"].get(m['id'], {})
                supabase.table("preventivo_maggiorazioni").insert({
                    "preventivo_id": preventivo_id,
                    "maggiorazione_id": m["id"],
                    "infisso_id": info_appl.get('infisso_id')
                }).execute()

            st.session_state["magg_applicazione"] = {}
            st.session_state["magg_prev_stato"] = {}
            st.success(f"Preventivo salvato! Totale: {format_euro(totale_finale)}")
            st.balloons()
