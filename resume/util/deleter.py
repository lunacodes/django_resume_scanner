from pathlib import Path

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin


class Deleter(LoginRequiredMixin):
    """Contains helper methods for deleting files and database info."""

    def __init__(
        self, resume_model, keywords_model, media_root: Path = settings.MEDIA_ROOT
    ) -> None:
        """Take custom uploads dir, or default to /uploads.

        Purpose: prevent unit tests from affecting the main uploads directory
        """
        self.uploads_path: Path = Path(media_root, "uploads")
        self.Resume = resume_model
        self.Keywords = keywords_model

    def delete_all_uploads(self) -> None:
        """Delete all files in uploads directory, after keywords are filtered."""
        up_glob = self.uploads_path.glob("**/*")
        for f in up_glob:
            f.unlink() if f.is_file else None

    def delete_resume_text_from_db(self) -> None:
        """Delete all data in resume_text column of resume_resume db table."""
        self.Resume.objects.all().values("resume_text").update(resume_text="")

    def delete_keyword_queries_from_db(self) -> None:
        """Delete keywords rows in database."""
        self.Keywords.objects.all().delete()

    def delete_resume_files_and_text(self) -> None:
        """Call methods to delete resume files & text, but not keyword scores."""
        self.delete_all_uploads()
        self.delete_resume_text_from_db()

    def delete_all_resumes_and_queries_nuclear(self) -> None:
        """Delete all resume uploads, and all rows in resume and keywords tables."""
        self.delete_all_uploads()
        self.delete_keyword_queries_from_db()
        self.Resume.objects.all().delete()
