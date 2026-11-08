from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import cache_control, cache_page
from django.views.decorators.vary import vary_on_cookie
from django.views.generic import TemplateView

from .forms import MailingForm, MessageForm, RecipientForm
from .mixins import (
    MailingFormMixin, OwnerCreateView, OwnerDeleteView, OwnerDetailView,
    OwnerListView, OwnerUpdateView,
)
from .models import Attempt, Mailing, Message, Recipient
from .services import send_mailing


@method_decorator(cache_page(60), name='dispatch')
@method_decorator(vary_on_cookie, name='dispatch')
@method_decorator(cache_control(public=True, max_age=60), name='dispatch')
class HomeView(TemplateView):
    template_name = 'mailing/home.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        now = timezone.now()
        ctx['total_mailings'] = Mailing.objects.count()
        ctx['active_mailings'] = Mailing.objects.filter(
            start_time__lte=now, end_time__gte=now, is_disabled=False,
        ).count()
        ctx['unique_recipients'] = Recipient.objects.count()
        return ctx


class RecipientListView(OwnerListView):
    model = Recipient
    template_name = 'mailing/recipient_list.html'
    context_object_name = 'recipients'


class RecipientCreateView(OwnerCreateView):
    model = Recipient
    form_class = RecipientForm
    template_name = 'mailing/form.html'
    success_url = reverse_lazy('mailing:recipient_list')


class RecipientUpdateView(OwnerUpdateView):
    model = Recipient
    form_class = RecipientForm
    template_name = 'mailing/form.html'
    success_url = reverse_lazy('mailing:recipient_list')


class RecipientDeleteView(OwnerDeleteView):
    model = Recipient
    template_name = 'mailing/confirm_delete.html'
    success_url = reverse_lazy('mailing:recipient_list')


class MessageListView(OwnerListView):
    model = Message
    template_name = 'mailing/message_list.html'
    context_object_name = 'messages_list'


class MessageCreateView(OwnerCreateView):
    model = Message
    form_class = MessageForm
    template_name = 'mailing/form.html'
    success_url = reverse_lazy('mailing:message_list')


class MessageUpdateView(OwnerUpdateView):
    model = Message
    form_class = MessageForm
    template_name = 'mailing/form.html'
    success_url = reverse_lazy('mailing:message_list')


class MessageDeleteView(OwnerDeleteView):
    model = Message
    template_name = 'mailing/confirm_delete.html'
    success_url = reverse_lazy('mailing:message_list')


class MailingListView(OwnerListView):
    model = Mailing
    template_name = 'mailing/mailing_list.html'
    context_object_name = 'mailings'


class MailingDetailView(OwnerDetailView):
    model = Mailing
    template_name = 'mailing/mailing_detail.html'
    context_object_name = 'mailing'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['attempts'] = self.object.attempts.all()
        return ctx


class MailingCreateView(MailingFormMixin, OwnerCreateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailing/form.html'
    success_url = reverse_lazy('mailing:mailing_list')


class MailingUpdateView(MailingFormMixin, OwnerUpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailing/form.html'
    success_url = reverse_lazy('mailing:mailing_list')


class MailingDeleteView(OwnerDeleteView):
    model = Mailing
    template_name = 'mailing/confirm_delete.html'
    success_url = reverse_lazy('mailing:mailing_list')


class MailingSendView(LoginRequiredMixin, View):
    def post(self, request, pk):
        mailing = get_object_or_404(Mailing, pk=pk, owner=request.user)
        try:
            count = send_mailing(mailing)
            messages.success(request, f'Рассылка отправлена. Писем: {count}.')
        except ValueError as exc:
            messages.error(request, f'Ошибка: {exc}')
        return redirect('mailing:mailing_detail', pk=pk)


class MailingDisableView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_manager

    def post(self, request, pk):
        mailing = get_object_or_404(Mailing, pk=pk)
        mailing.is_disabled = not mailing.is_disabled
        mailing.save(update_fields=['is_disabled'])
        state = 'отключена' if mailing.is_disabled else 'включена'
        messages.success(request, f'Рассылка {state}.')
        return redirect('mailing:mailing_detail', pk=pk)


class StatisticsView(LoginRequiredMixin, TemplateView):
    template_name = 'mailing/statistics.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        mailings = Mailing.objects.all() if user.is_manager else Mailing.objects.filter(owner=user)
        attempts = Attempt.objects.filter(mailing__in=mailings)
        ctx['total_mailings'] = mailings.count()
        ctx['total_attempts'] = attempts.count()
        ctx['success_attempts'] = attempts.filter(status=Attempt.Status.SUCCESS).count()
        ctx['failed_attempts'] = attempts.filter(status=Attempt.Status.FAILED).count()
        return ctx