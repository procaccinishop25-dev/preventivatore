from jinja2 import Environment, FileSystemLoader
from xhtml2pdf import pisa
from services.supabase import supabase
import io
import re


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
