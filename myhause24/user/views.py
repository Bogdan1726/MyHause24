from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView
from .forms import UserLoginForm, RegisterUserForm
from django.contrib.auth import login as auth_login, get_user_model

User = get_user_model()

# Create your views here.


class OwnerLoginView(LoginView):
    form_class = UserLoginForm
    template_name = 'user/pages/login_owner.html'

    def get(self, request, *args, **kwargs):
        if self.request.user.is_staff is False and self.request.user.is_authenticated:
            return redirect(reverse('cabinet'))
        return super().get(request, *args, **kwargs)

    def get_success_url(self):
        messages.success(self.request, f'Добро пожаловать {self.request.user}')
        return reverse_lazy('cabinet')

    def form_valid(self, form):
        """Security check complete. Log the user in."""
        auth_login(self.request, form.get_user())
        return HttpResponseRedirect(self.get_success_url())


class AdminLoginView(LoginView):
    form_class = UserLoginForm
    template_name = 'user/pages/login_admin.html'

    def get(self, request, *args, **kwargs):
        if self.request.user.is_staff and self.request.user.is_authenticated:
            return redirect(reverse('admin'))
        return super().get(request, *args, **kwargs)

    def get_success_url(self):
        messages.success(self.request, f'Добро пожаловать {self.request.user}')
        return reverse_lazy('admin')

    def form_valid(self, form):
        """Security check complete. Log the user in."""
        auth_login(self.request, form.get_user())
        if self.request.user.is_staff and self.request.user.role.statistics is False:
            return redirect(reverse('user_profile', kwargs={'pk': self.request.user.id}))
        return HttpResponseRedirect(self.get_success_url())


class UserRegisterView(CreateView):
    model = User
    template_name = 'user/pages/register.html'
    form_class = RegisterUserForm

    def get_success_url(self):
        messages.success(self.request, f'Добро пожаловать {self.request.user}')
        return reverse_lazy('cabinet_login')


class OwnerLogout(LogoutView):
    next_page = 'cabinet_login'


class AdminLogout(LogoutView):
    next_page = 'admin_login'