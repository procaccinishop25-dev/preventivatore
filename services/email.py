import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import streamlit as st


def invia_email_preventivo(destinatario, oggetto, corpo, pdf_buffer, nome_file_pdf):
    mittente = st.secrets["EMAIL_MITTENTE"]
    password = st.secrets["EMAIL_PASSWORD"]
    smtp_host = st.secrets.get("EMAIL_SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(st.secrets.get("EMAIL_SMTP_PORT", 587))
    nome_mittente = st.secrets.get("EMAIL_MITTENTE_NOME", mittente)

    msg = MIMEMultipart()
    msg["From"] = f"{nome_mittente} <{mittente}>"
    msg["To"] = destinatario
    msg["Subject"] = oggetto

    msg.attach(MIMEText(corpo, "plain"))

    pdf_buffer.seek(0)
    allegato = MIMEApplication(pdf_buffer.read(), _subtype="pdf")
    allegato.add_header("Content-Disposition", "attachment", filename=nome_file_pdf)
    msg.attach(allegato)

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        server.login(mittente, password)
        server.sendmail(mittente, destinatario, msg.as_string())
