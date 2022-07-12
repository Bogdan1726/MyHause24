from django.conf import settings
from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpResponseRedirect
from django.shortcuts import resolve_url, redirect
from django.urls import reverse

from .forms import UserLoginForm
from django.contrib.auth import login as auth_login

# Create your views here.


class UserLoginView(LoginView):
    form_class = UserLoginForm
    template_name = 'user/pages/login.html'

    def get_success_url(self):
        url = self.request.POST['redirect']
        return url or resolve_url(settings.LOGIN_REDIRECT_URL)

    def form_valid(self, form):
        """Security check complete. Log the user in."""
        auth_login(self.request, form.get_user())
        messages.success(self.request, f'Добро пожаловать {self.request.user}')
        if self.request.user.role.statistics:
            return HttpResponseRedirect(self.get_success_url())
        return redirect(reverse('user_profile', kwargs={'pk': self.request.user.id}))


class UserLogout(LogoutView):
    next_page = 'login'
