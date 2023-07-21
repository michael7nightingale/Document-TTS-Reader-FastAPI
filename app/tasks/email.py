from .worker import celery
from app.services.email import send_message


@celery.task(name='send_message_task')
def send_message_task(subject: str, to_addrs: list, body: str):
    send_message(
        subject=subject,
        to_addrs=to_addrs,
        body=body
    )
