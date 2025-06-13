import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from core.config import smtp_settings
from services.template import get_template


async def send_email_smtp(email, subject, template, data):
    body = get_template(template, data)

    msg = MIMEMultipart()
    msg["From"] = smtp_settings.user
    msg["To"] = email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "html"))

    smtp_kwargs = {
        "hostname": smtp_settings.host,
        "port": smtp_settings.port,
        "timeout": 10,
        "use_tls": smtp_settings.use_tls,  # False для Mailpit:1025
    }
    # Добавляем username/password только если они заданы(при тесте на Mailpit:1025 не задавать!)
    if smtp_settings.user:
        smtp_kwargs["username"] = smtp_settings.user
    if smtp_settings.password:
        smtp_kwargs["password"] = smtp_settings.password

    smtp = aiosmtplib.SMTP(**smtp_kwargs)
    await smtp.connect()
    await smtp.send_message(msg)
    await smtp.quit()
