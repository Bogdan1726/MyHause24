from django.contrib.sitemaps import Sitemap
from django.http import HttpResponse
from django.views.decorators.http import require_GET
from django.urls import reverse


class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = 'daily'

    def items(self):
        return ['main', 'about', 'site_services', 'contact']

    def location(self, item):
        return reverse(item)


@require_GET
def robots_txt(request):
    lines = [
        "User-Agent: *",
        f"Disallow: {reverse('admin')} \n",
        f"Host: {request.build_absolute_uri(reverse('main'))} \n"
        f"Sitemap: {request.build_absolute_uri(reverse('django.contrib.sitemaps.views.sitemap'))}",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")
