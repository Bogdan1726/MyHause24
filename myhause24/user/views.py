from django.conf import settings
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import resolve_url

from .forms import UserLoginForm


# Create your views here.

class UserLoginView(LoginView):
    form_class = UserLoginForm
    template_name = 'user/pages/login.html'

    def get_success_url(self):
        url = self.request.POST['redirect']
        return url or resolve_url(settings.LOGIN_REDIRECT_URL)


class UserLogout(LogoutView):
    next_page = 'login'




