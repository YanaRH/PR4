from django.contrib.auth.backends import ModelBackend


class EmailVerifiedBackend(ModelBackend):
    """Пускать только тех, кто подтвердил email и не заблокирован."""

    def user_can_authenticate(self, user):
        if not user.email_verified:
            return False
        if user.is_blocked:
            return False
        return super().user_can_authenticate(user)