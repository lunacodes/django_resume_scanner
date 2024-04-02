"""Custom Type Aliases."""

from typing import TypeAlias, TypedDict

from django.contrib.auth.models import User

from resume.models import Keywords, Resume

CSVRow: TypeAlias = list[str | int]


class TableRow(TypedDict):
    """Format for the table rows used in DataFiltering class methods.

    candidate (str): candidate's name
    kw_matches (dict[str, int]): calculated keyword counts
    unique_score (int): total unique matches
    """

    candidate: str
    candidate_url: str
    kw_matches: dict[str, int]
    unique_score: int


TableRowsList: TypeAlias = list[TableRow]


class PopulatedTable(TypedDict):
    """Dict containing the table row for each candidate.

    table_rows (list): table data for results.html
    matches_found (bool): candidates with matches found
    """

    table_rows: list[TableRow]
    matches_found: bool


class FilteredData(TypedDict):
    """Final filtered data that gets passed as context to results.html.

    key_words_with_case (list): keywords submitted to form
    table_rows (list): table data for results.html
    resumes_exist (bool): used by results.html
    matches_found (bool): any candidates with keyword matches?
    """

    key_words_with_case: list[str]
    table_rows: TableRowsList
    resumes_exist: bool
    matches_found: bool


class ScoreData(TypedDict):
    """Dict containing keyword matches and unique score for each candidate.

    kw_counts (dict): word counts for POSTed keywords
    unique_matches (int): total unique words matched
    """

    kw_counts: dict[str, int]
    unique_score: int


class CSVRowsDict(TypedDict):
    """The row format used by the CSV Export."""

    table_headers: list[str]
    table_rows: list[list[str | int]]


class ResumeRowData(TypedDict):
    """Row of resume data used in tests.

    file: str
    resume_text: str
    keyword_matches: dict[str, int]
    name: str
    unique_matches: int | None
    """

    file: str
    resume_text: str
    keyword_matches: dict[str, int]
    name: str
    unique_matches: int | None


class UserLogins(TypedDict):
    """User logins for metrics.

    users: list[str]
    login_counts: list[int]
    """

    users: list[str]
    login_counts: list[int]


class UserLoginSets(TypedDict):
    """Department sets of user login metrics.

    department: str
    labels: list[str]
    data: list[int]
    """

    department: str
    labels: list[str]
    data: list[int]


class AppDataSet(TypedDict):
    """App Data Set for tests.

    user: User
    app_name: str
    app_url: str
    delete_url: str
    export_url: str
    filter_url: str
    kw_model: type[Keywords]
    res_model: type[Resume]
    """

    user: User
    app_name: str
    app_url: str
    delete_url: str
    export_url: str
    filter_url: str
    kw_model: type[Keywords]
    res_model: type[Resume]


class DeptDBData(TypedDict):
    """Department metrics data from the database.

    Example data:
    department_logins: 1
    resumes_saved: 4
    keyword_queries_run: 1
    keywords_queried: some string of words here
    """

    department_logins: int
    resumes_saved: int
    keyword_queries_run: int
    keywords_queried: int
    csv_exports: int


class DeptMonthData(TypedDict):
    """Department metrics data.

    Example data:
    graph_id: bohr_Apr_2023
    month: April 2023
    department_name: bohr
    labels: []
    label_colors:
    """

    graph_id: str
    month: str
    department_name: str
    labels: str
    data: list[str]
    label_colors: list[str]


class DeptDataSet(TypedDict):
    """Department metrics data set to be rendered by template.

    department: str
    labels: list[str]
    data: DeptData
    """

    department: str
    labels: list[str]
    data: DeptMonthData


class MetricsViewContext(TypedDict):
    """Context for metrics.views.MetricsView, used by metrics/metrics.html.

    user_sets: list[UserLoginSets]
    dept_sets: list[DeptData]
    """

    user_sets: list[UserLoginSets]
    dept_sets: list[DeptMonthData]
