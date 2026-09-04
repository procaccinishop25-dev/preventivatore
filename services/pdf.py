from jinja2 import Environment, FileSystemLoader
from xhtml2pdf import pisa
from services.supabase import supabase
from services.email import invia_email_preventivo
from services.catalogo import ottieni_mappa_prezzi_catalogo
import streamlit as st
import streamlit.components.v1 as components
from datetime import date, datetime, timezone
import io
import re
import base64


def slug(testo):
    testo = (testo or "").strip().replace(" ", "_")
    return re.sub(r"[^A-Za-z0-9_-]", "", testo)


def format_euro(x):
    s = f"{x:,.2f}"
    s = s.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{s} €"


def elenco_foto_generali(cartella_progetto):
    file_esistenti = supabase.storage.from_("foto").list(cartella_progetto) or []
    generali = [f for f in file_esistenti if f["name"].startswith("generale_")]
    return [supabase.storage.from_("foto").get_public_url(f"{cartella_progetto}/{f['name']}") for f in generali]


def costruisci_contesto_pdf(numero_preventivo, data, progetto, cliente, prezzi_tipologia, maggiorazioni_righe, totale_base, sconto, totale_finale):
    progetto_id = progetto['id']
    nome_cliente = f"{cliente.get('nome', '')} {cliente.get('cognome_azienda', '')}"
    cartella_progetto = slug(nome_cliente)

    infissi_db = supabase.table("infissi").select("*").eq("progetto_id", progetto_id).order("numero_infisso").execute()

    infissi_ctx = []
    superficie_totale = 0.0
    for inf in infissi_db.data or []:
        prezzo = prezzi_tipologia.get(inf['tipologia'], 0)
        mq_riga = inf['mq'] * inf['quantita']
        subtotale = mq_riga * prezzo
        superficie_totale += mq_riga
        infissi_ctx.append({
            "nome": inf.get('nome') or f"{inf['tipologia']} {inf.get('numero_infisso', '')}",
            "misure": f"{inf['larghezza_cm']}x{inf['altezza_cm']} cm",
            "mq": f"{mq_riga:.2f}",
            "prezzo_mq": format_euro(prezzo),
            "subtotale": format_euro(subtotale),
            "foto_url": inf.get('foto_url'),
            "schizzo_url": inf.get('schizzo_url')
        })

    progetto_extra = supabase.table("progetti").select("schizzo_url").eq("id", progetto_id).execute()
    schizzo_generale_url = progetto_extra.data[0].get('schizzo_url') if progetto_extra.data else None

    foto_generali = elenco_foto_generali(cartella_progetto)

    mostra_allegato = bool(
        schizzo_generale_url or foto_generali or
        any(i['foto_url'] or i['schizzo_url'] for i in infissi_ctx)
    )

    return {
        "azienda_nome": "La Tua Azienda Serramenti",
        "azienda_contatti": "Via Esempio 1, 00000 Città — Tel: 000 0000000 — email@esempio.it",
        "numero_preventivo": numero_preventivo,
        "data": data,
        "cliente_nome": nome_cliente,
        "cliente_telefono": cliente.get('telefono'),
        "cliente_email": cliente.get('email'),
        "progetto_indirizzo": progetto.get('indirizzo', ''),
        "progetto_citta": progetto.get('citta', ''),
        "data_sopralluogo": progetto.get('data_sopralluogo'),
        "operatore": progetto.get('operatore'),
        "numero_infissi": len(infissi_ctx),
        "superficie_totale": f"{superficie_totale:.2f}",
        "infissi": infissi_ctx,
        "totale_base": format_euro(totale_base),
        "maggiorazioni": maggiorazioni_righe,
        "sconto": format_euro(sconto) if sconto else None,
        "totale_finale": format_euro(totale_finale),
        "schizzo_generale_url": schizzo_generale_url,
        "foto_generali": foto_generali,
        "mostra_allegato": mostra_allegato,
    }


def genera_pdf_preventivo(contesto):
    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("preventivo.html")
    html_renderizzato = template.render(**contesto)

    buffer = io.BytesIO()
    pisa.CreatePDF(html_renderizzato, dest=buffer)
    buffer.seek(0)
    return buffer


def trigger_download_automatico(pdf_bytes, filename):
    """Avvia automaticamente il download del PDF nel browser, senza bisogno di un click aggiuntivo."""
    b64 = base64.b64encode(pdf_bytes).decode()
    html = f"""
    <html><body>
    <a id="auto_dl" href="data:application/pdf;base64,{b64}" download="{filename}" style="display:none;"></a>
    <script>document.getElementById('auto_dl').click();</script>
    </body></html>
    """
    components.html(html, height=0, width=0)


def genera_preventivo_rapido(progetto_id, progetto_info, cliente_info, prezzo_default=400.0):
    """Genera un preventivo usando il prezzo del Catalogo per ogni prodotto e le maggiorazioni salvate a livello di progetto."""
    mappa_catalogo = ottieni_mappa_prezzi_catalogo()

    infissi_db = supabase.table("infissi").select("id, tipologia, mq, quantita, nome").eq("progetto_id", progetto_id).execute()
    righe_infissi = infissi_db.data or []

    tipologie = sorted(set(i['tipologia'] for i in righe_infissi))
    prezzi_tipologia = {t: mappa_catalogo.get(t, prezzo_default) for t in tipologie}

    totale_base = sum(i['mq'] * i['quantita'] * prezzi_tipologia[i['tipologia']] for i in righe_infissi)
    mq_totale_progetto = sum(i['mq'] * i['quantita'] for i in righe_infissi)

    maggiorazioni_progetto = supabase.table("progetto_maggiorazioni").select("*").eq("progetto_id", progetto_id).execute().data or []

    totale_maggiorazioni = 0.0
    maggiorazioni_righe_pdf = []

    for m in maggiorazioni_progetto:
        if m.get('infisso_id'):
            infisso_rif = next((i for i in righe_infissi if i['id'] == m['infisso_id']), None)
            if infisso_rif:
                base_mq = infisso_rif['mq'] * infisso_rif['quantita']
                base_valore = base_mq * prezzi_tipologia.get(infisso_rif['tipologia'], prezzo_default)
                riferimento = infisso_rif.get('nome') or infisso_rif['tipologia']
            else:
                base_mq, base_valore, riferimento = 0, 0, "infisso non trovato"
        else:
            base_mq = mq_totale_progetto
            base_valore = totale_base
            riferimento = "tutti gli infissi"

        if m['tipo'] == 'mq':
            importo_calc = m['importo'] * base_mq
        elif m['tipo'] == 'fisso':
            importo_calc = m['importo']
        elif m['tipo'] == 'percentuale':
            importo_calc = base_valore * (m['importo'] / 100)
        else:
            importo_calc = 0

        totale_maggiorazioni += importo_calc
        maggiorazioni_righe_pdf.append({
            "descrizione": f"{m['descrizione']} ({riferimento})",
            "importo": format_euro(importo_calc)
        })

    totale_finale = totale_base + totale_maggiorazioni

    preventivo = supabase.table("preventivi").insert({
        "progetto_id": progetto_id,
        "totale_base": totale_base,
        "sconti": 0,
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

    for m in maggiorazioni_progetto:
        supabase.table("preventivo_maggiorazioni").insert({
            "preventivo_id": preventivo_id,
            "infisso_id": m.get('infisso_id'),
            "descrizione_personalizzata": m['descrizione'],
            "importo_personalizzato": m['importo'],
            "tipo_personalizzato": m['tipo']
        }).execute()

    oggi = date.today()
    data_formattata = f"{oggi.day:02d}/{oggi.month:02d}/{oggi.year}"

    contesto = costruisci_contesto_pdf(
        numero_preventivo=preventivo_id[:8].upper(),
        data=data_formattata,
        progetto=progetto_info,
        cliente=cliente_info,
        prezzi_tipologia=prezzi_tipologia,
        maggiorazioni_righe=maggiorazioni_righe_pdf,
        totale_base=totale_base,
        sconto=0,
        totale_finale=totale_finale
    )
    pdf_buffer = genera_pdf_preventivo(contesto)

    return preventivo_id, pdf_buffer, contesto


@st.dialog("✅ Preventivo generato", width="large")
def dialog_dopo_generazione_preventivo(preventivo_id, pdf_buffer, contesto, cliente_info, nome_cliente_display, indirizzo, citta):
    st.success(f"Totale: {contesto['totale_finale']}")
    st.caption(
        "Il download del PDF è partito automaticamente. Prezzi presi dal Catalogo, maggiorazioni del progetto già incluse — "
        "puoi gestirle in qualsiasi momento da Gestione Progetto."
    )

    st.divider()
    invia_ora = st.radio(
        "Vuoi inviarlo subito via email al cliente?",
        ["Non ora", "Sì, invia subito"],
        horizontal=True,
        key=f"invia_scelta_{preventivo_id}"
    )

    if invia_ora == "Sì, invia subito":
        email_default = cliente_info.get('email') or ""
        destinatario = st.text_input("Email destinatario", value=email_default, key=f"dest_quick_{preventivo_id}")
        oggetto = st.text_input(
            "Oggetto",
            value=f"Preventivo n. {contesto['numero_preventivo']} - {contesto['azienda_nome']}",
            key=f"ogg_quick_{preventivo_id}"
        )
        corpo = st.text_area(
            "Messaggio",
            value=(
                f"Gentile {nome_cliente_display},\n\n"
                f"In allegato il preventivo n. {contesto['numero_preventivo']} del {contesto['data']} "
                f"per i lavori presso {indirizzo}, {citta}.\n\n"
                f"Totale: {contesto['totale_finale']}\n\n"
                f"Restiamo a disposizione per qualsiasi chiarimento.\n\n"
                f"Cordiali saluti,\n{contesto['azienda_nome']}"
            ),
            height=180,
            key=f"corpo_quick_{preventivo_id}"
        )

        if st.button("✉️ Invia email", type="primary", use_container_width=True, key=f"invia_btn_quick_{preventivo_id}"):
            if not destinatario:
                st.warning("Inserisci l'indirizzo email del destinatario.")
            else:
                try:
                    pdf_buffer.seek(0)
                    invia_email_preventivo(destinatario, oggetto, corpo, pdf_buffer, f"preventivo_{slug(nome_cliente_display)}.pdf")
                    supabase.table("preventivi").update({
                        "email_inviata_a": destinatario,
                        "email_inviata_il": datetime.now(timezone.utc).isoformat(),
                        "stato": "inviato"
                    }).eq("id", preventivo_id).execute()
                    st.success(f"Email inviata a {destinatario}!")
                except Exception as e:
                    st.error(f"Errore nell'invio: {e}")
    else:
        if st.button("Chiudi", use_container_width=True, key=f"chiudi_quick_{preventivo_id}"):
            st.rerun()
