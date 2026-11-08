from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .models import Mailing


class OwnerListView(LoginRequiredMixin, ListView):
    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_manager:
            return qs
        return qs.filter(owner=self.request.user)


class OwnerDetailView(LoginRequiredMixin, DetailView):
    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_manager:
            return qs
        return qs.filter(owner=self.request.user)

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if isinstance(obj, Mailing):
            obj.update_status()
        return obj


class OwnerCreateView(LoginRequiredMixin, CreateView):
    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class OwnerUpdateView(LoginRequiredMixin, UpdateView):
    def get_queryset(self):
        return super().get_queryset().filter(owner=self.request.user)


class OwnerDeleteView(LoginRequiredMixin, DeleteView):
    def get_queryset(self):
        return super().get_queryset().filter(owner=self.request.user)


class MailingFormMixin:
    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw['user'] = self.request.user
        return kw