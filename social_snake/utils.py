from email.message import EmailMessage
from . import smtp, app


async def send_mail(message: EmailMessage, recipients: str):
    await smtp.connect()
    await smtp.login(app.config["SMTP_USERNAME"], app.config["SMTP_PASSWORD"])
    await smtp.send_message(
        message,
        sender=f"Social Snake <{app.config['SMTP_USERNAME']}>",
        recipients=recipients,
    )
    await smtp.quit()
