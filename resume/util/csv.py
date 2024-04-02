import csv

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.query import ValuesIterable, ValuesListIterable
from django.http import HttpRequest, HttpResponse

from ..custom_types import CSVRow, CSVRowsDict
from .format import FormatUtilies

FT: FormatUtilies = FormatUtilies()


class CSVExporter(LoginRequiredMixin):
    """Methods for formatting and exporting a CSV file."""

    def __init__(self, resume_model, keywords_model) -> None:
        self.Resume = resume_model
        self.Keywords = keywords_model

    def export_csv(self, request: HttpRequest) -> HttpResponse:
        """Export all entries from resume_uploadfile db table to a .csv file."""
        response: HttpResponse = HttpResponse()
        response["Content-Disposition"] = (
            "attachment; filename=candidates_keyword_scores.csv"
        )
        writer: csv._writer = csv.writer(response)
        csv_data: CSVRowsDict = self.prepare_csv()
        writer.writerow(csv_data["table_headers"])
        for row in csv_data["table_rows"]:
            writer.writerow(row)

        return response

    def format_kw_headers_as_list(self, kw_headers: str) -> list[str]:
        """Convert a string of keywords into a cleaned-up list for the CSV Header row."""
        headers_list: list[str] = FT.format_keywords(kw_headers)
        return headers_list

    def format_query_set_as_csv_row_list(self, cands) -> list[CSVRow]:
        """Convert a ValuesQuerySet into a list of CSVRows to be exported.

        CSVRow: "cand_name, unique_match, '', <individual scores>"
        """
        rows: list[CSVRow] = []
        for cand in cands:
            name: str = cand[0]
            unique_matches: int = cand[1]
            matches_dict: dict[str, int] = cand[2]

            if matches_dict:
                scores: list[int] = [] * 3
                csv_row: CSVRow = [name, unique_matches, ""]

                for word in matches_dict:
                    scores.append(matches_dict[word])

                csv_row.extend(scores)
                if unique_matches:
                    rows.append(csv_row)
        return rows

    def prepare_csv(self) -> CSVRowsDict:
        """Format QuerySet results for CSV export.

        Example Data:
            table_headers: ["Name, "Unique Matches, "", "word1", "word2", "word3"]
            table_rows: [
                ['resume1', 3, '', '1', '2', '1'],
                ['resume2', 1, '', '0', '0', '1'],
            ]

        Returns:
            CSVRowsDict:
                table_headers (list[str]): Headings for the CSV data
                table_rows (list): List of rows with: candidate name, unique matches (int), and an empty str for table spacing
                    candidate name,
                    unique_matches (int),
                    empty string (""), for table spacing
                table_rows (list[str | int]): Rows with
                candidate name, unique matches, and keyword counts
        """
        cands: ValuesListIterable = self.Resume.objects.values_list(
            "name", "unique_matches", "keyword_matches"
        )
        keyword_headers: tuple[str] | None = self.Keywords.objects.values_list(
            "keywords"
        ).last()
        keyword_headers_list: list[str] = self.format_kw_headers_as_list(
            keyword_headers[0]
        )

        table_headers: list[str] = ["Name", "Unique Matches", ""]
        table_headers.extend(keyword_headers_list)
        table_rows: list[CSVRow] = self.format_query_set_as_csv_row_list(cands)

        return {"table_headers": table_headers, "table_rows": table_rows}


class ExpCSV:
    """Rewritten Export CSV class."""

    def __init__(self, resume_model, keywords_model) -> None:
        self.Resume = resume_model
        self.Keywords = keywords_model

    def get_candidates_data(self) -> ValuesIterable:
        """Get candidate data ValuesIterable."""
        cands: ValuesIterable = self.Resume.objects.values_list(
            "name", "unique_matches", "keyword_matches"
        )
        return cands

    def get_keyword_headers(self) -> ValuesListIterable:
        """Get keywords used in filter query, and use as headers."""
        keyword_headers: ValuesListIterable = self.Keywords.objects.values_list(
            "keywords"
        ).last()
        # keyword_headers_list: list[str] = self.format_kw_headers_as_list(
        #     keyword_headers[0]
        # )
        return keyword_headers
