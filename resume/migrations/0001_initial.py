# Generated by Django 5.0.3 on 2024-04-02 17:26

import django.core.validators
from django.db import migrations, models

import resume.models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Keywords",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("keywords", models.CharField(default="", max_length=150)),
            ],
            options={
                "verbose_name": "Keywords",
                "verbose_name_plural": "Keywords",
            },
        ),
        migrations.CreateModel(
            name="Resume",
            fields=[
                (
                    "file",
                    models.FileField(
                        blank=True,
                        null=True,
                        upload_to=resume.models._upload_path,
                        validators=[
                            django.core.validators.FileExtensionValidator(
                                ["pdf"], "Only PDFs are allowed", "only_pdfs_allowed"
                            )
                        ],
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        default="<django.db.models.fields.files.FileField>",
                        max_length=100,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("resume_text", models.TextField(default="")),
                ("unique_matches", models.IntegerField(null=True)),
                ("keyword_matches", models.JSONField(null=True)),
            ],
            options={
                "verbose_name": "Resume",
                "verbose_name_plural": "Resumes",
            },
        ),
    ]
