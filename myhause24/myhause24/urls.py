from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
import debug_toolbar
from django.contrib.sitemaps.views import sitemap
from .sitemaps import StaticViewSitemap, robots_txt


urlpatterns = [
    path('old_admin/', admin.site.urls),
    path('', include('main.urls')),
    path('account/', include('user.urls')),
    path('admin/', include('crm.urls')),
    path('cabinet/', include('cabinet.urls')),

]

# robots.txt and sitemap.xml

sitemaps = {
    'static': StaticViewSitemap,
}

urlpatterns += [
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps},
         name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', robots_txt, name='robots_txt'),
]


if settings.DEBUG:
    urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

