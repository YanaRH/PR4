from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Recipient(models.Model):
    email = models.EmailField(unique=True, verbose_name='Email')
    full_name = models.CharField(max_length=255, verbose_name='Ф.И.О.')
    comment = models.TextField(blank=True, verbose_name='Комментарий')
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='recipients', null=True, blank=True,
    )

    class Meta:
        verbose_name = 'Получатель'
        verbose_name_plural = 'Получатели'

    def __str__(self):
        return f'{self.full_name} <{self.email}>'


class Message(models.Model):
    subject = models.CharField(max_length=255, verbose_name='Тема письма')
    body = models.TextField(verbose_name='Тело письма')
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='messages', null=True, blank=True,
    )

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'

    def __str__(self):
        return self.subject


class Mailing(models.Model):
    class Status(models.TextChoices):
        CREATED = 'Создана', 'Создана'
        STARTED = 'Запущена', 'Запущена'
        FINISHED = 'Завершена', 'Завершена'

    start_time = models.DateTimeField(verbose_name='Дата и время начала')
    end_time = models.DateTimeField(verbose_name='Дата и время окончания')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.CREATED, verbose_name='Статус')
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='mailings', verbose_name='Сообщение')
    recipients = models.ManyToManyField(Recipient, related_name='mailings', verbose_name='Получатели')
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='mailings', null=True, blank=True,
    )
    is_disabled = models.BooleanField(default=False, verbose_name='Отключена')

    class Meta:
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'
        ordering = ['-start_time']

    def clean(self):
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError({'end_time': 'Дата начала должна быть раньше даты окончания.'})
        if not self.pk and self.start_time and self.start_time < timezone.now():
            raise ValidationError({'start_time': 'Дата начала не может быть в прошлом.'})

    def update_status(self):
        now = timezone.now()
        if now < self.start_time:
            new_status = self.Status.CREATED
        elif self.start_time <= now <= self.end_time:
            new_status = self.Status.STARTED
        else:
            new_status = self.Status.FINISHED
        if self.pk and self.status != new_status:
            self.status = new_status
            Mailing.objects.filter(pk=self.pk).update(status=new_status)
        return new_status

    @property
    def current_status(self):
        now = timezone.now()
        if now < self.start_time:
            return self.Status.CREATED
        if now <= self.end_time:
            return self.Status.STARTED
        return self.Status.FINISHED

    @property
    def can_send(self):
        if self.is_disabled:
            return False
        now = timezone.now()
        return self.start_time <= now <= self.end_time

    def __str__(self):
        return f'Рассылка #{self.pk} — {self.message.subject}'


class Attempt(models.Model):
    class Status(models.TextChoices):
        SUCCESS = 'Успешно', 'Успешно'
        FAILED = 'Не успешно', 'Не успешно'

    attempt_time = models.DateTimeField(auto_now_add=True, verbose_name='Дата и время попытки')
    status = models.CharField(max_length=20, choices=Status.choices, verbose_name='Статус')
    server_response = models.TextField(blank=True, verbose_name='Ответ сервера')
    mailing = models.ForeignKey(Mailing, on_delete=models.CASCADE, related_name='attempts', verbose_name='Рассылка')

    class Meta:
        verbose_name = 'Попытка рассылки'
        verbose_name_plural = 'Попытки рассылок'
        ordering = ['-attempt_time']

    def __str__(self):
        return f'{self.attempt_time} — {self.status}'