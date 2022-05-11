from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('old_admin/', admin.site.urls),
    path('', include('main.urls')),
    path('user/', include('user.urls')),
    path('admin/', include('crm.urls')),
    path('cabinet/', include('cabinet.urls'))
]
