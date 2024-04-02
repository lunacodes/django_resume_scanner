from typing import Any, LiteralString

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import AbstractBaseUser
from django.core.files.uploadedfile import UploadedFile
from django.db.models import Q
from django.db.models.query import QuerySet
from django.forms.models import ModelFormMetaclass
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.utils.translation import gettext as _
from django.utils.version import get_docs_version
from django.views import View

from .custom_types import FilteredData
from .forms import LoginForm, UploadFileForm
from .models import Keywords, Resume
from .util.csv import CSVExporter
from .util.data import DataFiltering
from .util.deleter import Deleter
from .util.form_util import FormFactory
from .util.format import FormatUtilies
from .util.resume import Processor

FT: FormatUtilies = FormatUtilies()


class UploadView(View):
    """Generate and POST uploads form for resumes."""

    # form_class = UploadFileForm
    # template_name = "upload.html"
    # success_url = "..."  # Replace with your URL or reverse().

    def __init__(self) -> None:
        self.keywords_model: Keywords = Keywords
        self.resume_model: Resume = Resume

    def get(self, request: HttpRequest) -> HttpResponse:
        """Render the upload file form on the homepage."""
        # form: ModelFormMetaclass = FormFactory(self.resume_model).create_upload_form()
        # context: dict[str, ModelFormMetaclass] = {"form": form}
        form = UploadFileForm()
        context = {"form": form}
        # context = {}

        return render(request, "upload.html", context)

    def post(self, request: HttpRequest) -> HttpResponse:
        """Post the data from the upload file form."""
        # form_class = self.get_form_class()
        # form = self.get_form(form_class)
        form = UploadFileForm(request.POST, request.FILES)
        files: list[UploadedFile] = request.FILES.getlist("file")

        if form.is_valid():
            Processor(self.resume_model).upload_and_process_resumes(files)

        else:
            context: dict[str, ModelFormMetaclass] = {
                "form": form,
                "message": "Only PDF files are accepted. Please upload in PDF format.",
            }
            return render(request, "upload.html", context)

        return HttpResponseRedirect("filter")


class KeywordView(View):
    """Generates keyword form, POSTs to generate_keyword_match_data(), and removes resume data."""

    def __init__(self) -> None:
        self.resume_model: Resume = Resume
        self.keywords_model: Keywords = Keywords

    def get(self, request: HttpRequest) -> HttpResponse:
        """Render the keyword form on the filter page."""
        form: ModelFormMetaclass = FormFactory(
            self.keywords_model
        ).create_keywords_form()
        context: dict[str, ModelFormMetaclass] = {"form": form}

        return render(request, "filter.html", context=context)

    def post(self, request: HttpRequest) -> HttpResponse:
        """POST keywords to be filtered. Remove resume files & data, on success."""
        form: ModelFormMetaclass = FormFactory(
            self.keywords_model
        ).create_keywords_form()
        self.form = form(request.POST)

        if self.form.is_valid():
            self.form.save()
            data: DataFiltering = DataFiltering(self.resume_model)
            context: FilteredData = data.generate_keyword_match_data(request, self.form)

        return render(request, "results.html", context=context)


class DeleteView(View):
    """Contains resume & data deletion methods."""

    def __init__(self):
        self.resume_model: Resume = Resume
        self.keywords_model: Keywords = Keywords

    def get(self, request: HttpRequest) -> HttpResponse:
        """Call delete_all_resumes_and_queries_nuclear() if user navigates to /deleteall."""
        Deleter(
            self.resume_model, self.keywords_model
        ).delete_all_resumes_and_queries_nuclear()

        return render(request, "delete_all.html")


class ExportView(View):
    """Export all entries from resume_uploadfile db table to a .csv file."""

    def __init__(self) -> None:
        self.resume_model: Resume = Resume
        self.keywords_model: Keywords = Keywords

    def get(self, request: HttpRequest) -> HttpResponse:
        """Render Export page. If rows exist in db, call export_csv()."""
        context: dict[str, bool] = {"resumes_exist": False}

        if not self.resume_model.objects.all():
            return render(request, "export.html", context)

        rows_with_matches: QuerySet[Resume] = self.resume_model.objects.exclude(
            Q(keyword_matches__isnull=True) | Q(keyword_matches__iexact="{}")
        )

        if rows_with_matches:
            context = {"resumes_exist": True}
            return CSVExporter(self.resume_model, self.keywords_model).export_csv(
                request
            )

        return render(request, "export.html", context)


class LoginView(View):
    """Custom View for LoginForm."""

    def get(self, request) -> HttpResponse:
        """Render the login form."""
        form: LoginForm = LoginForm()
        context: dict[str, LoginForm] = {"form": form}

        return render(request, "registration/login.html", context)

    def post(self, request) -> HttpResponseRedirect | HttpResponse:
        """Handle user login via POST request."""
        form: LoginForm = LoginForm(request.POST)
        message = ""
        if form.is_valid():
            user: AbstractBaseUser | None = authenticate(
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password"],
            )
            if user:
                login(request, user)
            else:
                message: str = "Login failed!"

        context: dict[str, LoginForm | str] = {"form": form, "message": message}

        return render(request, "registration/login.html", context)


class LogOutView(View):
    """Custom LogOut view."""

    def get(self, request) -> HttpResponseRedirect:
        """Log the user out, and redirect to hoempage."""
        try:
            logout(request)
        except AttributeError:
            # Avoid server error, if someone who wasn't logged in
            # tries to logout
            return redirect("home")
        return redirect("home")


class ProfileView(View):
    """User Profile view."""

    def get(self, request) -> HttpResponse:
        """Display the user profile."""
        user = request.user

        if user.groups.exists():
            user_groups = [g.name for g in user.groups.all()]

        return render(request, "profile.html", {"user_groups": user_groups})


def handle_403(request: HttpRequest, exception: HttpResponse) -> HttpResponse:
    """Handle 403 Error by rendering the 403 template."""
    return render(request, "403.html", status=403)


def handle_404(request: HttpRequest, exception: HttpResponse) -> HttpResponse:
    """Handle 404 Error by rendering the 404 template."""
    template_name: LiteralString = "404.html"
    # if request.path.startswith("/bohr/"):
    #     template_name = "bohr/404.html"
    # else:
    #     template_name = "404.html"
    return render(request, template_name, status=404)


def handle_500(request: HttpRequest) -> HttpResponse:
    """Handle 500 Error by rendering the 500 template."""
    return render(request, "500.html", status=500)


def csrf_failure(request, reason="") -> HttpResponse:
    """Handle CSRF Failures with a less ugly error page."""
    from django.middleware.csrf import REASON_NO_CSRF_COOKIE, REASON_NO_REFERER

    c: dict[str, Any] = {
        "title": _("Forbidden"),
        "main": _("CSRF verification failed. Request aborted."),
        "reason": reason,
        "no_referer": reason == REASON_NO_REFERER,
        "no_referer1": _(
            "You are seeing this message because this HTTPS site requires a "
            "“Referer header” to be sent by your web browser, but none was "
            "sent. This header is required for security reasons, to ensure "
            "that your browser is not being hijacked by third parties."
        ),
        "no_referer2": _(
            "If you have configured your browser to disable “Referer” headers, "
            "please re-enable them, at least for this site, or for HTTPS "
            "connections, or for “same-origin” requests."
        ),
        "no_referer3": _(
            'If you are using the <meta name="referrer" '
            'content="no-referrer"> tag or including the “Referrer-Policy: '
            "no-referrer” header, please remove them. The CSRF protection "
            "requires the “Referer” header to do strict referer checking. If "
            "you’re concerned about privacy, use alternatives like "
            '<a rel="noreferrer" …> for links to third-party sites.'
        ),
        "no_cookie": reason == REASON_NO_CSRF_COOKIE,
        "no_cookie1": _(
            "You are seeing this message because this site requires a CSRF "
            "cookie when submitting forms. This cookie is required for "
            "security reasons, to ensure that your browser is not being "
            "hijacked by third parties."
        ),
        "no_cookie2": _(
            "If you have configured your browser to disable cookies, please "
            "re-enable them, at least for this site, or for “same-origin” "
            "requests."
        ),
        "DEBUG": settings.DEBUG,
        "docs_version": get_docs_version(),
        "more": _("More information is available with DEBUG=True."),
    }

    return render(request, "403_csrf.html", context=c)
