from pathlib import Path
from typing import Any, LiteralString

from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db.models import (
    CharField,
    FileField,
    IntegerField,
    JSONField,
    Model,
    TextField,
)


def _upload_path(
    instance: Any, filename: str, media_root: LiteralString = settings.MEDIA_ROOT
) -> Path:
    """Set upload path to media_root/uploads/app_name/file.

    Note: the `uploads/` prefix comes from settings.MEDIA_URL
    Production: uploads/app_name/file
    Tests: resume/tests/uploads/app_name/file
    """
    return Path("uploads", instance._meta.app_label, filename)


class KeywordsInfo(Model):
    """Keywords Parent Model."""

    class Meta:
        """Keywords Parent Model Meta."""

        abstract: bool = True
        verbose_name: str = "Keywords"

    name = "Keywords"
    keywords = CharField(max_length=150, default="")
    error_messages: dict[str, dict[str, str]] = {
        "keywords": {"required": "Please enter some keywords to filter by."}
    }
    field_classes: dict[str, str] = {"keywords": "textinput textInput"}

    def __str__(self) -> str:
        """Return model name as string."""
        return str(self.name)


class Keywords(KeywordsInfo):
    """Keywords Model."""

    class Meta:
        """Keywords Model Meta."""

        verbose_name: str = "Keywords"
        verbose_name_plural: str = "Keywords"


class ResumeInfo(Model):
    """Resume Parent Model."""

    class Meta:
        """Resume Parent Model Meta."""

        abstract: bool = True
        verbose_name: str = "ResumeInfo"

    file: FileField = FileField(
        upload_to=_upload_path,
        null=True,
        blank=True,
        validators=[
            FileExtensionValidator(
                ["pdf"], "Only PDFs are allowed", "only_pdfs_allowed"
            )
        ],
    )
    name = CharField(max_length=100, default=str(file), primary_key=True)
    resume_text = TextField(default="")
    unique_matches = IntegerField(null=True)
    keyword_matches: JSONField = JSONField(null=True)

    def __str__(self) -> str:
        """Return model name as string."""
        return str(self.name)


class Resume(ResumeInfo):
    """Resume Model."""

    class Meta:
        """Resume Model Meta."""

        verbose_name: str = "Resume"
        verbose_name_plural: str = "Resumes"
