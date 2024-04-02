from pathlib import Path

import fitz
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.uploadedfile import UploadedFile
from fitz import EmptyFileError, FileDataError


class Processor(LoginRequiredMixin):
    """Methods for processing uploaded resumes."""

    def __init__(self, resume_model, media_root: str = settings.MEDIA_ROOT):
        self.Resume = resume_model
        self.media_root: str = media_root

    def get_pdf_text(self, filename: Path | str) -> str:
        """Extract text from resume PDF via PyMuPDF and fitz."""
        pdf_text: str = ""
        filepath: Path = Path(self.media_root, filename)
        try:
            doc: fitz.Document = fitz.open(filepath)
            for page in doc.pages():
                pdf_text += page.get_text()
            doc.close()
        except EmptyFileError:
            print("EmptyFileError")
        except ValueError:
            print("ValueError")
        except FileDataError:
            print("FileDataError: file isn't a valid PDF")
        except FileNotFoundError:
            print("FileNotFound Error")

        return pdf_text

    def upload_and_process_resumes(self, files: list[UploadedFile]) -> None:
        """Save the name and text of uploaded files to the database."""
        for f in files:
            file_ext: str = Path(str(f)).suffix

            # Don't process non-pdf files that Django's form validation missed
            if file_ext == ".pdf":
                name: str = Path(str(f)).stem
                resume: self.Resume
                created: bool
                resume, created = self.Resume.objects.update_or_create(
                    name=name,
                    defaults={
                        "file": f,
                        "keyword_matches": {},
                        "unique_matches": None,
                    },
                )
                resume.resume_text = self.get_pdf_text(resume.file.name)
                resume.save()
