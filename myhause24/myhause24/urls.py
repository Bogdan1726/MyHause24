from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('old_admin/', admin.site.urls),
    path('', include('main.urls')),
    path('account/', include('user.urls')),
    path('admin/', include('crm.urls')),
    path('cabinet/', include('cabinet.urls')),
    # path("select2/", include("django_select2.urls")),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
