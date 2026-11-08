from django.core.mail import send_mail
from django.utils import timezone

from .models import Attempt


def send_mailing(mailing):
    now = timezone.now()
    if mailing.is_disabled:
        raise ValueError('Рассылка отключена менеджером.')
    if not (mailing.start_time <= now <= mailing.end_time):
        raise ValueError('Текущее время вне интервала рассылки (start_time — end_time).')

    attempts = []
    for recipient in mailing.recipients.all():
        try:
            send_mail(
                subject=mailing.message.subject,
                message=mailing.message.body,
                from_email=None,
                recipient_list=[recipient.email],
                fail_silently=False,
            )
            attempts.append(Attempt(
                mailing=mailing,
                status=Attempt.Status.SUCCESS,
                server_response='OK',
            ))
        except Exception as exc:
            attempts.append(Attempt(
                mailing=mailing,
                status=Attempt.Status.FAILED,
                server_response=str(exc),
            ))

    Attempt.objects.bulk_create(attempts)  # batch-создание
    return len(attempts)