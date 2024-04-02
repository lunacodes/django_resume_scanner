from typing import Literal, LiteralString

from django.urls import URLPattern, path

from .views import LoginView

app_name: Literal["resume"] = "resume"
urlpatterns: list[URLPattern] = [
    path("", LoginView.as_view(), name="home"),
]

handler403: LiteralString = "resume.views.handle_403"
handler404: LiteralString = "resume.views.handle_404"
handler500: LiteralString = "resume.views.handle_500"
