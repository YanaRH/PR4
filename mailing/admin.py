from django.contrib import admin

from .models import Attempt, Mailing, Message, Recipient


@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):
    list_display = ('email', 'full_name', 'owner')
    search_fields = ('email', 'full_name')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('subject', 'owner')


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'start_time', 'end_time', 'status', 'is_disabled', 'owner')
    list_filter = ('status', 'is_disabled')
    filter_horizontal = ('recipients',)


@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = ('attempt_time', 'status', 'mailing')
    list_filter = ('status',)