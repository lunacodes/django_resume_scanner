from typing import LiteralString

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import URLPattern, URLResolver, include, path

from resume.views import ExportView, KeywordView, LoginView, UploadView

urlpatterns: list[URLPattern | URLResolver] = (
    [
        path("admin/", admin.site.urls),
        path("accounts/", include("accounts.urls")),
        path("accounts/", include("django.contrib.auth.urls")),
        path("login", LoginView.as_view(), name="login"),
        path("", UploadView.as_view(), name="home"),
        path("resume", UploadView.as_view(), name="resume"),
        path("filter", KeywordView.as_view(), name="filter"),
        path("export", ExportView.as_view(), name="exportcsv"),
    ]
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
)

handler403: LiteralString = "resume.views.handle_403"
handler404: LiteralString = "resume.views.handle_404"
handler500: LiteralString = "resume.views.handle_500"

admin.site.site_header = "Resume Scanner Admin Panel"
admin.site.site_title = "Resume Scanner"
