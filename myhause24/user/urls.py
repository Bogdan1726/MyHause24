from django.urls import path
from django.views.generic import TemplateView

from .views import OwnerLoginView, OwnerLogout, AdminLogout, UserRegisterView, AdminLoginView, EmailVerificationDone

urlpatterns = [
    path('cabinet/login/', OwnerLoginView.as_view(), name='cabinet_login'),
    path('admin/login/', AdminLoginView.as_view(), name='admin_login'),
    path('register/', UserRegisterView.as_view(), name='register'),
    path('cabinet/logout/', OwnerLogout.as_view(), name='cabinet_logout'),
    path('admin/logout/', AdminLogout.as_view(), name='admin_logout'),
    path('register/confirm/', TemplateView.as_view(
        template_name='user/pages/confirm_email.html'), name='confirm'
         ),
    path('register/confirm/done/', TemplateView.as_view(
        template_name='user/pages/done_confirm_email.html'), name='done_confirm'),

    path('register/verification_email/<uidb64>/<token>/',
         EmailVerificationDone.as_view(), name='verification_email')
]
