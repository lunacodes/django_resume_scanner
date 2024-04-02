from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import URLPattern, URLResolver, include, path
from django.views.generic.base import TemplateView

urlpatterns: list[URLPattern | URLResolver] = [
    path("", TemplateView.as_view(template_name="home.html"), name="home"),
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

admin.site.site_header = "Resume Scanner Admin Panel"
admin.site.site_title = "Resume Scanner"
