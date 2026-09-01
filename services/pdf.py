from jinja2 import Environment, FileSystemLoader
from xhtml2pdf import pisa
import io


def genera_pdf_preventivo(contesto):
    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("preventivo.html")
    html_renderizzato = template.render(**contesto)

    buffer = io.BytesIO()
    pisa.CreatePDF(html_renderizzato, dest=buffer)
    buffer.seek(0)
    return buffer
