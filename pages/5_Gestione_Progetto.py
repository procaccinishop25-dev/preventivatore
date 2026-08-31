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


def genera_excel_preventivo(nome_cliente, indirizzo, citta, righe_riepilogo_excel, totale_base, totale_maggiorazioni, totale_finale, mq_totale_progetto):
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
        st.subheader("✏️ Maggiorazioni personalizzate")

        if "maggiorazioni_personalizzate" not in st.session_state:
            st.session_state["maggiorazioni_personalizzate"] = []

        with st.form("nuova_maggiorazione_personalizzata", clear_on_submit=True):
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                descr_personalizzata = st.text_input("Descrizione (es. Infisso particolare triplo)")
            with col2:
                importo_personalizzato = st.number_input("Importo", min_value=0.0, step=1.0)
            with col3:
                tipo_personalizzato = st.selectbox("Tipo", ["€ fisso", "€/m²", "%"])

            applicazione = st.radio("Applicazione", ["All'intero preventivo", "A un infisso specifico"], horizontal=True)

            infisso_scelto_id = None
            nome_infisso_scelto = None
            if applicazione == "A un infisso specifico":
                opzioni_infissi = {
                    f"{inf.get('nome') or inf['tipologia']}": inf['id'] for inf in infissi.data
                }
                nome_infisso_scelto = st.selectbox("Seleziona infisso", list(opzioni_infissi.keys()))
                infisso_scelto_id = opzioni_infissi[nome_infisso_scelto]

            aggiungi = st.form_submit_button("➕ Aggiungi maggiorazione personalizzata")

            if aggiungi and descr_personalizzata:
                tipo_map = {"€ fisso": "fisso", "€/m²": "mq", "%": "percentuale"}
                st.session_state["maggiorazioni_personalizzate"].append({
                    "descrizione": descr_personalizzata,
                    "importo": importo_personalizzato,
                    "tipo": tipo_map[tipo_personalizzato],
                    "applicazione": applicazione,
                    "infisso_id": infisso_scelto_id,
                    "infisso_nome": nome_infisso_scelto
                })
                st.rerun()

        if st.session_state["maggiorazioni_personalizzate"]:
            for idx, mp in enumerate(st.session_state["maggiorazioni_personalizzate"]):
                etichetta_tipo = {"mq": "€/m²", "fisso": "€ fisso", "percentuale": "%"}.get(mp['tipo'])
                dettaglio_applicazione = f"su {mp['infisso_nome']}" if mp['infisso_id'] else "sull'intero preventivo"
                col_desc, col_rimuovi = st.columns([5, 1])
                with col_desc:
                    st.write(f"• **{mp['descrizione']}** — {mp['importo']} {etichetta_tipo}, {dettaglio_applicazione}")
                with col_rimuovi:
                    if st.button("🗑️", key=f"rimuovi_mp_{idx}"):
                        st.session_state["maggiorazioni_personalizzate"].pop(idx)
                        st.rerun()

        st.divider()

        totale_base = sum(prezzi_tipologia[t] * info["mq_totali"] for t, info in tipologie.items())
        mq_totale_progetto = sum(info["mq_totali"] for info in tipologie.values())

        # --- Costruzione righe del riepilogo con formula di calcolo ---
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

        righe_riepilogo.append({
            "voce": "Totale base", "calcolo": "", "totale": totale_base, "bold": True
        })

        totale_maggiorazioni = 0.0

        for m in maggiorazioni_selezionate:
            if m['tipo'] == 'mq':
                importo_calc = m['importo'] * mq_totale_progetto
                calcolo_str = f"{format_num(mq_totale_progetto)} m² totali × {format_num(m['importo'])} €/m²"
            elif m['tipo'] == 'fisso':
                importo_calc = m['importo']
                calcolo_str = "Importo fisso"
            elif m['tipo'] == 'percentuale':
                importo_calc = totale_base * (m['importo'] / 100)
                calcolo_str = f"{format_num(m['importo'])}% su {format_euro(totale_base)}"
            else:
                importo_calc = 0
                calcolo_str = ""
            totale_maggiorazioni += importo_calc
            righe_riepilogo.append({
                "voce": m['descrizione'], "calcolo": calcolo_str, "totale": importo_calc, "bold": False
            })

        for mp in st.session_state["maggiorazioni_personalizzate"]:
            if mp['infisso_id']:
                infisso_rif = next((i for i in infissi.data if i['id'] == mp['infisso_id']), None)
                base_calcolo_mq = (infisso_rif['mq'] * infisso_rif['quantita']) if infisso_rif else 0
                base_calcolo_valore = (infisso_rif['mq'] * infisso_rif['quantita'] * prezzi_tipologia.get(infisso_rif['tipologia'], 0)) if infisso_rif else 0
                nome_riferimento = mp['infisso_nome']
            else:
                base_calcolo_mq = mq_totale_progetto
                base_calcolo_valore = totale_base
                nome_riferimento = "intero preventivo"

            if mp['tipo'] == 'mq':
                importo_calc = mp['importo'] * base_calcolo_mq
                calcolo_str = f"{format_num(base_calcolo_mq)} m² ({nome_riferimento}) × {format_num(mp['importo'])} €/m²"
            elif mp['tipo'] == 'fisso':
                importo_calc = mp['importo']
                calcolo_str = f"Importo fisso ({nome_riferimento})"
            elif mp['tipo'] == 'percentuale':
                importo_calc = base_calcolo_valore * (mp['importo'] / 100)
                calcolo_str = f"{format_num(mp['importo'])}% su {format_euro(base_calcolo_valore)} ({nome_riferimento})"
            else:
                importo_calc = 0
                calcolo_str = ""

            totale_maggiorazioni += importo_calc
            righe_riepilogo.append({
                "voce": mp['descrizione'], "calcolo": calcolo_str, "totale": importo_calc, "bold": False
            })

        righe_riepilogo.append({
            "voce": "Maggiorazioni", "calcolo": "", "totale": totale_maggiorazioni, "bold": True
        })

        totale_finale = totale_base + totale_maggiorazioni

        righe_riepilogo.append({
            "voce": "Totale finale", "calcolo": "", "totale": totale_finale, "bold": True
        })

        # --- Rendering della tabella markdown ---
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
            righe_riepilogo_excel, totale_base, totale_maggiorazioni, totale_finale, mq_totale_progetto
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

            for mp in st.session_state["maggiorazioni_personalizzate"]:
                supabase.table("preventivo_maggiorazioni").insert({
                    "preventivo_id": preventivo_id,
                    "infisso_id": mp['infisso_id'],
                    "descrizione_personalizzata": mp['descrizione'],
                    "importo_personalizzato": mp['importo'],
                    "tipo_personalizzato": mp['tipo']
                }).execute()

            st.session_state["maggiorazioni_personalizzate"] = []
            st.success(f"Preventivo salvato! Totale: {format_euro(totale_finale)}")
            st.balloons()
