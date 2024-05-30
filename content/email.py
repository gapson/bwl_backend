from djoser.email import PasswordResetEmail

from djoser import utils
from djoser.conf import settings

class PasswordResetEmail(PasswordResetEmail):
    template_name = "email/bwl_password_reset.html"

    def get_context_data(self):
        # PasswordResetEmail can be deleted
        context = super().get_context_data()
        return context

