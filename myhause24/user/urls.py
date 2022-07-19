from django.urls import path
from .views import OwnerLoginView, OwnerLogout, AdminLogout, UserRegisterView, AdminLoginView

urlpatterns = [
    path('cabinet/login/', OwnerLoginView.as_view(), name='cabinet_login'),
    path('admin/login/', AdminLoginView.as_view(), name='admin_login'),
    path('register/', UserRegisterView.as_view(), name='register'),
    path('cabinet/logout/', OwnerLogout.as_view(), name='cabinet_logout'),
    path('admin/logout/', AdminLogout.as_view(), name='admin_logout')
]
