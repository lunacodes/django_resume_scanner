import re

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.base import ModelBase
from django.db.models.query import QuerySet
from django.http import HttpRequest

from resume.models import Resume as ResumeType

from ..custom_types import (
    FilteredData,
    PopulatedTable,
    ScoreData,
    TableRow,
    TableRowsList,
)
from .format import FormatUtilies

FT: FormatUtilies = FormatUtilies()


class DataFiltering(LoginRequiredMixin):
    """Methods for filtering, processing, and formatting keyword data."""

    def __init__(self, resume_model: ModelBase) -> None:
        """Resume model will be overridden by app."""
        self.Resume: ModelBase = resume_model

    def get_exact_match_word_count(self, word: str, str_to_search: str) -> int:
        """Get count of exact-matched lowercase word, via re.finditer.

        NOTE: While this will prevent 'htm' from matching 'html', it doesn't
        work against input like 'C-500' matching '500'.
        """
        word_lower: str = word.lower()
        return sum(
            1
            for _ in re.finditer(
                r"\b%s\b" % re.escape(word_lower), str_to_search, flags=re.IGNORECASE
            )
        )

    def calculate_word_counts(self, resume: str, key_words: list[str]) -> ScoreData:
        """Calculate keyword counts and total unique matches for each resume.

        Args:
            resume (str): lowercase text of resume.
            key_words (list[str]): list of keywords to filter by.

        Returns:
            ScoreData (dict): kw_counts, unique_matches
        """
        unique_words: list[str] = []
        kw_counts: dict[str, int] = {}
        resume_text: str = FT.remove_punctuation(resume)

        for word in key_words:
            kw_counts[word] = self.get_exact_match_word_count(word, resume_text)
            if kw_counts[word] > 0 and word not in unique_words:
                unique_words.append(word)

        return {
            "kw_counts": kw_counts,
            "unique_score": len(unique_words),
        }

    def get_scores(self, candidate: ResumeType, key_words: list[str]) -> ScoreData:
        """Calculate candidate's keyword scores.

        Args:
            candidate (Resume): Resume object from QuerySet
            key_words (list[str]): POSTed keywords to calculate scores for

        Returns:
            ScoreData (dict): kw_counts, unique_matches
        """
        resume_lowercase: str = candidate.resume_text.lower()

        score_data: ScoreData = {}  # type: ignore
        if resume_lowercase:
            counts: ScoreData = self.calculate_word_counts(resume_lowercase, key_words)

            kw_counts: dict[str, int] = counts["kw_counts"]
            unique_score: int = counts["unique_score"]

            score_data = {
                "kw_counts": kw_counts,
                "unique_score": unique_score,
            }

        return score_data

    def generate_table_row(
        self, candidate: ResumeType, key_words: list[str]
    ) -> TableRow:
        """Return table_row to be appended to table_rows list.

        Args:
            candidate (Resume): resume object
            key_words (list[str]): keywords to calculate scores for

        Returns:
            TableRow: candidate, candidate_url, kw_matches, unique_score
        """
        candidate_name: str = candidate.name
        candidate_url: str = candidate.file.url
        keyword_scores: ScoreData = self.get_scores(candidate, key_words)
        candidate.unique_matches = keyword_scores["unique_score"]
        candidate.keyword_matches = keyword_scores["kw_counts"]
        candidate.save()

        table_row: TableRow = {
            "candidate": candidate_name,
            "candidate_url": candidate_url,
            "kw_matches": keyword_scores["kw_counts"],
            "unique_score": keyword_scores["unique_score"],
        }
        return table_row

    def populate_table_rows(
        self, all_resumes: QuerySet[ResumeType], key_words: list[str]
    ) -> PopulatedTable:
        """Return list of table_rows for  generate_keyword_match_data() and results.html.

        Args:
            all_resumes (QuerySet[Resume]): All resumes in database
            key_words (list[str]): keywords to calculate scores for

        Returns:
            PopulatedTable (dict): table_rows, matches_found
        """
        table_rows: list[TableRow] = []
        matching_candidates: bool = False

        for candidate in all_resumes:
            if candidate.resume_text:
                table_row: TableRow = self.generate_table_row(candidate, key_words)
                matching_candidates = True if table_row["unique_score"] > 0 else False

                if table_row["unique_score"] > 0:
                    table_rows.append(table_row)

        return {"table_rows": table_rows, "matches_found": matching_candidates}

    def generate_keyword_match_data(
        self, request: HttpRequest, keyword_form_obj
    ) -> FilteredData:
        """Generate filtered keyword matches data, for results.html.

        Args:
            request (HttpRequest): user request.
            keyword_form_obj (KeywordForm): POSTED form data.

        Returns:
            FilteredData (dict): key_words, table_rows, resumes_exist, matches_found
        """
        kw_input: list[str] = FT.format_keywords(
            keyword_form_obj.cleaned_data["keywords"]
        )

        all_resumes: QuerySet[self.Resume] = self.Resume.objects.all()
        resumes_exist: bool = True if all_resumes else False

        match_data: PopulatedTable = self.populate_table_rows(all_resumes, kw_input)

        table_rows: TableRowsList = match_data["table_rows"]
        candidate_matches_found: bool = match_data["matches_found"]

        return {
            "key_words_with_case": kw_input,
            "table_rows": table_rows,
            "resumes_exist": resumes_exist,
            "matches_found": candidate_matches_found,
        }
