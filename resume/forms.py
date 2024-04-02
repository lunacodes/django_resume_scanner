from django.forms import (
    CharField,
    ClearableFileInput,
    FileField,
    Form,
    ModelForm,
    PasswordInput,
)

from resume.models import Resume


class LoginForm(Form):
    """Custom Login Form."""

    username: CharField = CharField(max_length=150)
    password: CharField = CharField(max_length=150, widget=PasswordInput)


class MultipleFileInput(ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result


class UploadFileForm(ModelForm):
    class Meta:
        model = Resume
        fields = ("file",)
