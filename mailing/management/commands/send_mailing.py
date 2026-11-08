from django.core.management.base import BaseCommand, CommandError

from mailing.models import Mailing
from mailing.services import send_mailing


class Command(BaseCommand):
    help = 'Отправить рассылку по её ID: python manage.py send_mailing <id>'

    def add_arguments(self, parser):
        parser.add_argument('mailing_id', type=int)

    def handle(self, *args, **options):
        try:
            mailing = Mailing.objects.get(pk=options['mailing_id'])
        except Mailing.DoesNotExist:
            raise CommandError(f'Рассылка с id={options["mailing_id"]} не найдена.')
        try:
            count = send_mailing(mailing)
        except ValueError as exc:
            raise CommandError(str(exc))
        self.stdout.write(self.style.SUCCESS(f'Отправлено писем: {count}.'))