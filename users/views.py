from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import CreateView, ListView

from .forms import RegisterForm

User = get_user_model()


class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:login')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.email_verified = False
        user.is_active = True
        user.save()

        current_site = get_current_site(self.request)
        link = f'http://{current_site.domain}{reverse("users:verify_email", args=[user.verification_token])}'
        send_mail(
            subject='Подтверждение email',
            message=f'Здравствуйте!\n\nПерейдите по ссылке для подтверждения регистрации:\n{link}\n',
            from_email=None,
            recipient_list=[user.email],
        )
        messages.info(self.request, 'Проверьте почту (в dev-режиме письмо выведено в консоль PyCharm) и подтвердите email.')
        return redirect(self.success_url)


class VerifyEmailView(View):
    def get(self, request, token):
        user = User.objects.filter(verification_token=token).first()
        if not user:
            return render(request, 'users/verify_failed.html')
        if not user.email_verified:
            user.email_verified = True
            user.save(update_fields=['email_verified'])
        return render(request, 'users/verify_success.html')


class UserListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = User
    template_name = 'users/user_list.html'
    context_object_name = 'users'
    ordering = ['email']

    def test_func(self):
        return self.request.user.is_manager


class UserBlockView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_manager

    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        if user.pk == request.user.pk:
            messages.error(request, 'Нельзя заблокировать самого себя.')
            return redirect('users:user_list')
        user.is_blocked = not user.is_blocked
        user.save(update_fields=['is_blocked'])
        messages.success(request, f'Пользователь {user.email} {"заблокирован" if user.is_blocked else "разблокирован"}.')
        return redirect('users:user_list')