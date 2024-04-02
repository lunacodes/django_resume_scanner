from django.forms import ClearableFileInput, ModelForm
from django.forms.models import modelform_factory


class FormFactory:
    """Tools for Model Form Factories."""

    def __init__(self, model) -> None:
        """Get the department's form model."""
        self.model = model

    def create_keywords_form(self) -> type[ModelForm]:
        """Generate a KeywordForm."""
        model = self.model
        fields: list[str] = ["keywords"]
        labels: dict[str, str] = {"keywords": "Enter keywords to filter resumes"}
        help_texts: dict[str, str] = {
            "keywords": """Enter all Keywords you are looking for seperated by spaces. For example: <code>carlsbad "nuclear Scientist" Management 0500</code>.<br>You can search for a specific phrase, by surrounding the phrase in quotes."""
        }
        form: type[ModelForm] = modelform_factory(
            model, fields=fields, labels=labels, help_texts=help_texts
        )

        return form

    def create_upload_form(self) -> type[ModelForm]:
        """Generate an Upload form."""
        model = self.model
        fields: list[str] = ["file"]
        widgets: dict[str, ClearableFileInput] = {
            "file": ClearableFileInput(
                attrs={
                    "multiple": True,
                    "class": "form-control",
                    "required": True,
                },
            ),
        }

        form: type[ModelForm] = modelform_factory(model, fields=fields, widgets=widgets)

        return form
