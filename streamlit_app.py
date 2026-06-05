from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pandas as pd
import streamlit as st


APP_DIR = Path(__file__).resolve().parent
DATA_FILES = {
    "pre": APP_DIR / "pre_all.csv",
    "post": APP_DIR / "post_all.csv",
    "comparison": APP_DIR / "pre_post_comparison.csv",
}
RAW_FILES = [
    APP_DIR / "results_pre.csv",
    APP_DIR / "results_post.csv",
    APP_DIR / "cluster_sizes.csv",
    APP_DIR / "official_hubs.csv",
]

COLS = {
    "agree": [
        "BELONG_01",
        "BELONG_02",
        "MENTOR_02",
        "MENTOR_03",
        "MENTOR_06_1",
        "MENTOR_06_2",
        "MENTOR_06_3",
        "MENTOR_06_4",
        "MENTOR_06_5",
        "MENTOR_06_6",
        "MENTOR_07_1",
        "MENTOR_07_2",
        "MENTOR_07_3",
        "MENTOR_07_4",
        "MENTOR_07_5",
    ],
    "proficiency": [
        "PROFICIENCY_01",
        "PROFICIENCY_02",
        "PROFICIENCY_03",
        "PROFICIENCY_04",
        "PROFICIENCY_05",
    ],
    "yesno": [
        "PRIOR_01",
        "MENTOR_01",
    ],
    "prior": [
        "PRIOR_02",
    ],
    "prior_considered": [
        "PRIOR_06",
    ],
    "num_emails": [
        "PRIOR_03",
    ],
    "why": [
        "MOTIVATION_01",
    ],
    "mentor_04": [
        "MENTOR_04",
    ],
    "mentor_05": [
        "MENTOR_05",
    ],
    "barriers": [
        "ACCESS_01",
    ],
    "comms": [
        "ACCESS_02",
    ],
    "plans_01": [
        "PLANS_01",
    ],
    "plans_02": [
        "PLANS_02",
    ],
    "plans_03": [
        "PLANS_03",
    ],
    "interest_01": [
        "INTEREST_01",
    ],
    "length": [
        "INTEREST_03",
    ],
    "timing": [
        "INTEREST_04",
        "INTEREST_05",
    ],
    "other": [
        "ACCESS_01_7_TEXT",
        "PRIOR_02_17_TEXT",
        "ACCESS_02_10_TEXT",
        "PRIOR_06_3_TEXT",
        "MOTIVATION_01_8_TEXT",
        "PLANS_02_9_TEXT",
        'PRIOR_04', # free response, both pre and post.
        'PRIOR_05', # free response, post only
        'PRIOR_07', # free response, post only
        'INTEREST_02', # free response, post only
        'INTEREST_06', # free response, post only
        'TESTIMONIAL',
    ],
}

LABELS = {
    "agree": [
        "Strongly Agree",
        "Agree",
        "Somewhat Agree",
        "Somewhat Disagree",
        "Disagree",
        "Strongly Disagree",
    ],
    "proficiency": [
        "Excellent",
        "Very Good",
        "Good",
        "Fair",
        "Poor",
        "Very Poor",
    ],
    "yesno": ["Yes", "No"],
    "prior": [
        "Participated in this program in a previous academic term",
        "Reached out directly to a professor",
        "Friend or acquaintance connected me to a research group",
        "Seminar or conference",
        "Another program on campus (URAP, SURF, Rose Hills, Haas Scholars, UCDC)",
        "Other",
    ],
    "prior_considered": [
        "Reaching out directly to a professor",
        "Another program on campus (URAP, SURF, Rose Hills, Haas Scholars)",
        "Other",
    ],
    "num_emails": ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10+"],
    "why": [
        "To make my undergraduate experience complete",
        "To engage in more active learning compared to the traditional classroom experience (e.g., reading textbooks with no application)",
        "To shape knowledge, not just consume it",
        "To gain hands-on skills",
        "To explore career interests",
        "To build mentorship connections",
        "To prepare for graduate school",
        "Other",
        "I do not feel research is necessary (exclusive choice)",
    ],
    "mentor_04": [
        "My mentor is generally available to meet or talk when I need them.",
        "My mentor is an active listener.",
        "My mentor takes a sincere interest in my career.",
        "My mentor acknowledges my contributions appropriately.",
        "My mentor is supportive of work-life balance.",
        "My mentor motivates me to improve my work.",
    ],
    "mentor_05": [
        "My mentor demonstrates professional expertise.",
        "My mentor is helpful in providing direction and guidance on professional issues.",
        "My mentor helps me to formulate clear goals.",
        "My mentor facilitates building my professional network.",
        "My mentor provides thoughtful advice on my scholarly work.",
    ],
    "barriers": [
        "My academic workload and responsibilities",
        "My job responsibilties and work hours",
        "My family responsibilities/commitments",
        "Financial concerns (e.g., related expenses, need for paid work left no time for something that feels 'extra')",
        "I did not have the skills I felt I needed to build before I could engage in research",
        "Lack of interest",
        "Too few or no positions available in my major",
        "Too few or no positions available for students in my year",
        "I applied, but did not secure a position",
        "I didn't know where to look",
        "I didn't know how to approach or reach out to a lab or researcher to join their project",
        "Transportation to/from research site (cost or time)",
        "Other",
    ],
    "comms": [
        "A class at Berkeley",
        "A friend or acquaintance",
        "A campus event/seminar or conference",
        "A department email",
        "The Discovery Opportunities Database",
        "Golden Bear Orientation",
        "Other",
    ],
    "plans_01": [
        "Yes, in the same group.",
        "Yes, in a different group.",
        "No.",
    ],
    "plans_02": [
        "Non-academic / industry research.",
        "Artistic / creative endeavors.",
        "Business / consulting.",
        "Professional practice.",
        "Teaching / education.",
        "Government / nonprofit.",
        "Other",
        "None of the above",
    ],
    "plans_03": [
        "Position secured or offer accepted",
        "Actively appREDACTEDg",
        "Strongly considering",
        "Generally considering",
        "Exploring options",
    ],
    "interest_01": [
        "Yes",
        "No",
        "I would be interested, but I am not eligible due to graduating this semester",
    ],
    "length": [
        "Semester long",
        "Year long",
        "Year with possibility of extending into summer",
        "Spring with possibility of extending into summer",
    ],
    "timing": ["March", "April", "May", "June", "July", "August"],
}

ANS_FORMAT = {
    "single_select": [
        "agree",
        "proficiency",
        "yesno",
        "num_emails",
        "plans_01",
        "plans_03",
        "interest_01",
        "length",
        "timing",
    ],
    "multi_select": [
        "prior",
        "prior_considered",
        "why",
        "mentor_04",
        "mentor_05",
        "barriers",
        "comms",
        "plans_02",
    ],
    "text": ["other"],
}

FILTERS = ["HUB_01", "MENTOR_08", "CLUSTER_SIZE"]
MISSING_FILTER_LABEL = "(Missing)"
FILTER_LABELS = {
    "HUB_01": [
        "Social Sciences",
        "Kavli ENSI",
        "CICI",
        "NASA Space Biosciences",
        "Molecular Foundry",
        "UCSF Anesthesia and Perioperative Care",
        "CNMAT",
        "KALX",
    ],
    "MENTOR_08": [
        "None",
        "More than zero, but less than one hour per week",
        "1-2 hrs/wk",
        "3-4 hrs/week",
        "More than 5 hrs/week",
    ],
    "CLUSTER_SIZE": ["1", "2", "3", "4", "5", "6", "7", "8"],
}

DESCRIPTIVE_LABELS = {
    "HUB_01": "Hub",
    "MENTOR_08": "Average time spent with mentor",
    "CLUSTER_SIZE": "Number of undergraduates in cluster"
}

DATASET_LABELS = {
    "comparison": "Pre/post comparison",
    "post": "Post survey questions",
    "pre": "Pre survey questions",
}

QTYPE_LABELS = {
    "agree": "Agreement",
    "proficiency": "Proficiency",
    "yesno": "Yes/no",
    "prior": "Prior research path",
    "prior_considered": "Other paths considered",
    "num_emails": "Number of emails/applications",
    "why": "Research motivation",
    "mentor_04": "Mentor relationship",
    "mentor_05": "Mentor guidance",
    "barriers": "Barriers",
    "comms": "Communication channels",
    "plans_01": "Continuation plans",
    "plans_02": "Other future plans",
    "plans_03": "Plan certainty",
    "interest_01": "Future interest",
    "length": "Preferred project length",
    "timing": "Application timing",
    "other": "Text responses",
}


def run_preprocess() -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(APP_DIR / "preprocess.py")],
        cwd=APP_DIR,
        capture_output=True,
        text=True,
        check=False,
    )


def needs_preprocess() -> bool:
    if not all(path.exists() for path in DATA_FILES.values()):
        return True
    newest_raw = max(path.stat().st_mtime for path in RAW_FILES if path.exists())
    oldest_processed = min(path.stat().st_mtime for path in DATA_FILES.values())
    return newest_raw > oldest_processed


def clean_label(value: object) -> str | None:
    if pd.isna(value):
        return None
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    text = str(value).strip()
    if text.endswith(".0") and text[:-2].isdigit():
        return text[:-2]
    return text or None


def filter_value_label(value: object) -> str:
    return clean_label(value) or MISSING_FILTER_LABEL


def readable_text(value: object, fallback: str) -> str:
    if pd.isna(value):
        return fallback
    return " ".join(str(value).split())


def drop_metadata(df: pd.DataFrame) -> pd.DataFrame:
    return df.iloc[2:].copy()


@st.cache_data(show_spinner=False)
def load_data() -> dict[str, pd.DataFrame]:
    datasets = {}
    for key, path in DATA_FILES.items():
        df = pd.read_csv(path)
        unnamed_cols = [col for col in df.columns if col.startswith("Unnamed:")]
        df = df.drop(columns=unnamed_cols, errors="ignore")
        datasets[key] = df
    return datasets


def available_qtypes(dataset_key: str, df: pd.DataFrame) -> list[str]:
    qtypes = []
    for qtype, cols in COLS.items():
        if dataset_key == "comparison":
            available = any(f"{col}_pre" in df.columns and f"{col}_post" in df.columns for col in cols)
        else:
            available = any(col in df.columns for col in cols)
        if available:
            qtypes.append(qtype)
    return qtypes


def available_questions(dataset_key: str, df: pd.DataFrame, qtype: str) -> list[str]:
    if dataset_key == "comparison":
        return [
            col
            for col in COLS[qtype]
            if f"{col}_pre" in df.columns and f"{col}_post" in df.columns
        ]
    return [col for col in COLS[qtype] if col in df.columns]


def question_text(dataset_key: str, df: pd.DataFrame, col: str) -> str:
    if dataset_key == "comparison":
        source_col = f"{col}_post" if f"{col}_post" in df.columns else f"{col}_pre"
    else:
        source_col = col
    return readable_text(df[source_col].iloc[0], col)


def answer_kind(qtype: str) -> str:
    for kind, qtypes in ANS_FORMAT.items():
        if qtype in qtypes:
            return kind
    raise ValueError(f"Unknown question type: {qtype}")


def filter_column(dataset_key: str, df: pd.DataFrame, filter_id: str) -> str | None:
    if dataset_key == "comparison":
        for suffix in ("_post", "_pre"):
            col = f"{filter_id}{suffix}"
            if col in df.columns:
                return col
        return None
    if filter_id in df.columns:
        return filter_id
    return None


def filter_options(rows: pd.DataFrame, col: str, filter_id: str) -> list[str]:
    known = FILTER_LABELS.get(filter_id, [])
    actual = [filter_value_label(value) for value in rows[col].unique()]
    options = list(dict.fromkeys([*known, *sorted(set(actual) - set(known))]))
    return [value for value in options if value in set(actual)]


def apply_filters(
    rows: pd.DataFrame,
    selections: dict[str, list[str]],
    filter_cols: dict[str, str],
) -> pd.DataFrame:
    filtered = rows.copy()
    for filter_id, selected in selections.items():
        col = filter_cols.get(filter_id)
        if not col or not selected:
            continue
        selected_set = set(selected)
        filtered = filtered[filtered[col].map(filter_value_label).isin(selected_set)]
    return filtered


def split_multi_response(value: object) -> list[str]:
    if pd.isna(value):
        return []
    sentinel = "<<COMMA_SPACE>>"
    protected = str(value).replace(", ", sentinel)
    parts = [part.replace(sentinel, ", ").strip() for part in protected.split(",")]
    return [part for part in parts if part]


def ordered_index(labels: list[str] | None, values: pd.Index) -> list[str]:
    known = labels or []
    extras = sorted(str(value) for value in values if str(value) not in known)
    return [*known, *extras]


def single_distribution(rows: pd.DataFrame, col: str, labels: list[str]) -> pd.DataFrame:
    responses = rows[col].dropna().map(clean_label).dropna()
    counts = responses.value_counts()
    order = ordered_index(labels, counts.index)
    table = pd.DataFrame({"Response": order})
    table["Count"] = table["Response"].map(counts).fillna(0).astype(int)
    denominator = int(table["Count"].sum())
    table["Percent"] = (table["Count"] / denominator * 100) if denominator else 0
    return table


def multi_distribution(rows: pd.DataFrame, col: str, labels: list[str]) -> pd.DataFrame:
    nonblank = rows[col].dropna()
    all_choices = [choice for value in nonblank for choice in split_multi_response(value)]
    counts = pd.Series(all_choices).value_counts() if all_choices else pd.Series(dtype=int)
    order = ordered_index(labels, counts.index)
    table = pd.DataFrame({"Response": order})
    table["Count"] = table["Response"].map(counts).fillna(0).astype(int)
    denominator = len(nonblank)
    table["Percent"] = (table["Count"] / denominator * 100) if denominator else 0
    return table


def text_responses(rows: pd.DataFrame, col: str) -> pd.DataFrame:
    responses = rows[col].dropna().map(lambda value: str(value).strip())
    responses = responses[responses.ne("")]
    return pd.DataFrame({"Response": responses.reset_index(drop=True)})


def display_distribution(table: pd.DataFrame) -> None:
    chart_data = table.set_index("Response")["Percent"]
    st.bar_chart(chart_data, height=320)
    st.dataframe(
        table,
        width="stretch",
        hide_index=True,
        column_config={
            "Percent": st.column_config.ProgressColumn(
                "Percent",
                format="%.1f%%",
                min_value=0,
                max_value=100,
            )
        },
    )


def comparison_distribution(
    rows: pd.DataFrame,
    col: str,
    qtype: str,
    labels: list[str],
) -> pd.DataFrame:
    if answer_kind(qtype) == "multi_select":
        pre = multi_distribution(rows, f"{col}_pre", labels)
        post = multi_distribution(rows, f"{col}_post", labels)
    else:
        pre = single_distribution(rows, f"{col}_pre", labels)
        post = single_distribution(rows, f"{col}_post", labels)

    table = pre[["Response", "Count", "Percent"]].merge(
        post[["Response", "Count", "Percent"]],
        on="Response",
        how="outer",
        suffixes=(" Pre", " Post"),
    )
    table = table.fillna({"Count Pre": 0, "Percent Pre": 0, "Count Post": 0, "Percent Post": 0})
    table["Count Pre"] = table["Count Pre"].astype(int)
    table["Count Post"] = table["Count Post"].astype(int)
    table["Response"] = pd.Categorical(table["Response"], categories=labels, ordered=True)
    table = table.sort_values("Response").reset_index(drop=True)
    return table


def display_comparison(table: pd.DataFrame) -> None:
    chart = table.set_index("Response")[["Percent Pre", "Percent Post"]]

    st.bar_chart(
        chart, 
        height=350, 
        color=["#002676", "#FDB515"], # Berkeley Blue for Pre, Berkeley Gold for Post
        stack=False,  # Unstacks the bars so they group side-by-side for each answer
        sort=False    # Prevents Streamlit from automatically sorting alphabetically
    )

    st.dataframe(
        table,
        width="stretch",
        hide_index=True,
        column_config={
            "Percent Pre": st.column_config.ProgressColumn(
                "Pre %",
                format="%.1f%%",
                min_value=0,
                max_value=100,
                color="#002676",
            ),
            "Percent Post": st.column_config.ProgressColumn(
                "Post %",
                format="%.1f%%",
                min_value=0,
                max_value=100,
                color="#FDB515",
            ),
        },
    )


def filtered_question_rows(
    rows: pd.DataFrame,
    dataset_key: str,
    col: str,
    filter_cols: dict[str, str],
) -> pd.DataFrame:
    cols = [filter_cols[filter_id] for filter_id in FILTERS if filter_id in filter_cols]
    if dataset_key == "comparison":
        cols.extend([f"{col}_pre", f"{col}_post"])
    else:
        cols.append(col)
    out = rows[[column for column in cols if column in rows.columns]].copy()
    out = out.rename(columns={filter_cols.get(filter_id, ""): filter_id for filter_id in FILTERS})
    return out


def main() -> None:
    st.set_page_config(page_title="Discovery Hubs AY25-26 Student Impact", layout="wide")
    st.title("Discovery Hubs AY25-26 Student Impact")

    if needs_preprocess():
        with st.spinner("Preparing survey data"):
            result = run_preprocess()
        if result.returncode != 0:
            st.error("The preprocessing step failed.")
            st.code(result.stderr or result.stdout)
            st.stop()

    with st.sidebar:
        if st.button("Refresh data"):
            result = run_preprocess()
            st.cache_data.clear()
            if result.returncode != 0:
                st.error("Refresh failed.")
                st.code(result.stderr or result.stdout)
                st.stop()
            st.success("Data refreshed.")

        datasets = load_data()
        dataset_key = st.radio(
            "Dataset",
            list(DATASET_LABELS),
            format_func=DATASET_LABELS.get,
        )

    df = datasets[dataset_key]
    rows = drop_metadata(df)

    filter_cols = {
        filter_id: col
        for filter_id in FILTERS
        if (col := filter_column(dataset_key, df, filter_id)) is not None
    }

    with st.sidebar:
        st.divider()
        selections = {}
        for filter_id, col in filter_cols.items():
            options = filter_options(rows, col, filter_id)
            label = DESCRIPTIVE_LABELS.get(filter_id, filter_id)
            selections[filter_id] = st.multiselect(
                label,
                options,
                default=options,
            )

    filtered_rows = apply_filters(rows, selections, filter_cols)

    qtypes = available_qtypes(dataset_key, df)
    with st.sidebar:
        st.divider()
        qtype = st.selectbox(
            "Question group",
            qtypes,
            format_func=lambda value: QTYPE_LABELS.get(value, value),
        )
        question_ids = available_questions(dataset_key, df, qtype)
        question_id = st.selectbox(
            "Question",
            question_ids,
            format_func=lambda value: f"{value}: {question_text(dataset_key, df, value)}",
        )

    labels = LABELS.get(qtype, [])
    kind = answer_kind(qtype)
    question = question_text(dataset_key, df, question_id)

    st.caption(DATASET_LABELS[dataset_key])
    st.subheader(question)

    metric_cols = st.columns(3)
    metric_cols[0].metric("Filtered respondents", len(filtered_rows))
    metric_cols[1].metric("Total respondents", len(rows))
    if dataset_key == "comparison":
        answered = filtered_rows[[f"{question_id}_pre", f"{question_id}_post"]].dropna(how="all")
    else:
        answered = filtered_rows[[question_id]].dropna()
    metric_cols[2].metric("Answered selected question", len(answered))

    if dataset_key == "comparison" and kind == "text":
        tabs = st.tabs(["Pre", "Post", "Filtered rows"])
        with tabs[0]:
            st.dataframe(text_responses(filtered_rows, f"{question_id}_pre"), width="stretch")
        with tabs[1]:
            st.dataframe(text_responses(filtered_rows, f"{question_id}_post"), width="stretch")
        with tabs[2]:
            st.dataframe(
                filtered_question_rows(filtered_rows, dataset_key, question_id, filter_cols),
                width="stretch",
                hide_index=True,
            )
        return

    if dataset_key == "comparison":
        table = comparison_distribution(filtered_rows, question_id, qtype, labels)
        tabs = st.tabs(["Summary", "Filtered rows"])
        with tabs[0]:
            display_comparison(table)
            st.download_button(
                "Download summary CSV",
                table.to_csv(index=False).encode("utf-8"),
                file_name=f"{question_id}_comparison_summary.csv",
                mime="text/csv",
            )
        with tabs[1]:
            st.dataframe(
                filtered_question_rows(filtered_rows, dataset_key, question_id, filter_cols),
                width="stretch",
                hide_index=True,
            )
        return

    if kind == "text":
        table = text_responses(filtered_rows, question_id)
        st.dataframe(table, width="stretch", hide_index=True)
        st.download_button(
            "Download responses CSV",
            table.to_csv(index=False).encode("utf-8"),
            file_name=f"{question_id}_responses.csv",
            mime="text/csv",
        )
        return

    if kind == "multi_select":
        table = multi_distribution(filtered_rows, question_id, labels)
    else:
        table = single_distribution(filtered_rows, question_id, labels)

    tabs = st.tabs(["Summary", "Filtered rows"])
    with tabs[0]:
        display_distribution(table)
        st.download_button(
            "Download summary CSV",
            table.to_csv(index=False).encode("utf-8"),
            file_name=f"{question_id}_summary.csv",
            mime="text/csv",
        )
    with tabs[1]:
        st.dataframe(
            filtered_question_rows(filtered_rows, dataset_key, question_id, filter_cols),
            width="stretch",
            hide_index=True,
        )


if __name__ == "__main__":
    main()
