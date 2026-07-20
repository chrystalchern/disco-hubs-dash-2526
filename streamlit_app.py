from __future__ import annotations

import pandas as pd
import streamlit as st


def clean_label(value: object) -> str | None:
    if pd.isna(value):
        return None
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    text = str(value).strip()
    if text.endswith(".0") and text[:-2].isdigit():
        return text[:-2]
    return text or None

def filter_value_label(value: object, missing_label: str) -> str:
    return clean_label(value) or missing_label

def readable_text(value: object, fallback: str) -> str:
    if pd.isna(value):
        return fallback
    return " ".join(str(value).split())

def drop_metadata(df: pd.DataFrame) -> pd.DataFrame:
    return df.iloc[2:].copy()

@st.cache_data(show_spinner=False)
def load_data(data_files: dict) -> dict[str, pd.DataFrame]:
    datasets = {}
    for key, path in data_files.items():
        df = pd.read_csv(path)
        unnamed_cols = [col for col in df.columns if col.startswith("Unnamed:")]
        df = df.drop(columns=unnamed_cols, errors="ignore")
        datasets[key] = df
    return datasets

def available_qtypes(
    dataset_key: str, df: pd.DataFrame, cols_dict: dict, dropped: set[str] | None = None
) -> list[str]:
    qtypes = []
    for qtype, cols in cols_dict.items():
        available = bool(available_questions(dataset_key, df, qtype, cols_dict, dropped))
        if available:
            qtypes.append(qtype)
    return qtypes

def available_questions(
    dataset_key: str, df: pd.DataFrame, qtype: str, cols_dict: dict, dropped: set[str] | None = None
) -> list[str]:
    # `dropped` questions are hidden from the pre/post comparison view only; the
    # underlying columns stay in the data so filters that reference them still work.
    drop = set(dropped) if (dropped and dataset_key == "comparison") else set()
    if dataset_key == "comparison":
        return [
            col
            for col in cols_dict[qtype]
            if col not in drop
            and f"{col}_pre" in df.columns
            and f"{col}_post" in df.columns
        ]
    return [col for col in cols_dict[qtype] if col in df.columns]

def question_text(dataset_key: str, df: pd.DataFrame, col: str) -> str:
    if dataset_key == "comparison":
        source_col = f"{col}_post" if f"{col}_post" in df.columns else f"{col}_pre"
    else:
        source_col = col
    return readable_text(df[source_col].iloc[0], col)

def answer_kind(qtype: str, ans_format_dict: dict) -> str:
    for kind, qtypes in ans_format_dict.items():
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

def filter_options(rows: pd.DataFrame, col: str, filter_id: str, filter_labels: dict, missing_label: str) -> list[str]:
    known = filter_labels.get(filter_id, [])
    actual = [filter_value_label(value, missing_label) for value in rows[col].unique()]
    options = list(dict.fromkeys([*known, *sorted(set(actual) - set(known))]))
    return [value for value in options if value in set(actual)]

def apply_filters(
    rows: pd.DataFrame,
    selections: dict[str, list[str]],
    filter_cols: dict[str, str],
    missing_label: str
) -> pd.DataFrame:
    filtered = rows.copy()
    for filter_id, selected in selections.items():
        col = filter_cols.get(filter_id)
        if not col or not selected:
            continue
        selected_set = set(selected)
        filtered = filtered[filtered[col].map(lambda v: filter_value_label(v, missing_label)).isin(selected_set)]
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
        width = 'stretch',
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
    ans_format_dict: dict
) -> pd.DataFrame:
    if answer_kind(qtype, ans_format_dict) == "multi_select":
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
        color=["#002676", "#FDB515"],
        stack=False,
        sort=False
    )

    st.dataframe(
        table,
        width = 'stretch',
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
    filters_list: list
) -> pd.DataFrame:
    # Ordered mapping of output label -> source column in `rows`.
    # A question that is also a filter (e.g. PRIOR_01) must not be selected
    # twice, or the rename collapses both into a duplicate column name.
    mapping: dict[str, str] = {}
    for filter_id in filters_list:
        src = filter_cols.get(filter_id)
        if src and src in rows.columns:
            mapping[filter_id] = src

    question_cols = [f"{col}_pre", f"{col}_post"] if dataset_key == "comparison" else [col]
    for qcol in question_cols:
        if qcol in rows.columns and qcol not in mapping:
            mapping[qcol] = qcol

    out = rows[list(mapping.values())].copy()
    out.columns = list(mapping.keys())
    return out


def render_dashboard(cfg):
    st.title(cfg.PAGE_TITLE)

    # Cap the height of multiselect filter boxes to ~2 rows of tags; scroll the rest.
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] [data-baseweb="select"] > div:first-child {
            max-height: 5.5rem;
            overflow-y: auto;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        datasets = load_data(cfg.DATA_FILES)
        dataset_key = st.radio(
            "Dataset",
            list(cfg.DATASET_LABELS),
            format_func=cfg.DATASET_LABELS.get,
        )

    df = datasets[dataset_key]
    rows = drop_metadata(df)

    filter_cols = {
        filter_id: col
        for filter_id in cfg.FILTERS
        if (col := filter_column(dataset_key, df, filter_id)) is not None
    }

    with st.sidebar:
        st.divider()
        selections = {}
        for filter_id, col in filter_cols.items():
            options = filter_options(rows, col, filter_id, cfg.FILTER_LABELS, cfg.MISSING_FILTER_LABEL)
            # Fetch a descriptive label if available, otherwise fallback to ID
            label = getattr(cfg, "DESCRIPTIVE_LABELS", {}).get(filter_id, filter_id)
            # Pretty display labels for option values (values stay raw so filtering works).
            value_labels = getattr(cfg, "FILTER_VALUE_LABELS", {}).get(filter_id, {})
            selections[filter_id] = st.multiselect(
                label,
                options,
                default=options,
                format_func=lambda v, m=value_labels: m.get(v, v),
            )

    filtered_rows = apply_filters(rows, selections, filter_cols, cfg.MISSING_FILTER_LABEL)

    # Group questions by topical category (QTYPES_CATEGORIZED), but derive each
    # question's answer format by mapping its column back through COLS.
    col_to_format = {col:fmt for fmt,cols in cfg.COLS.items() for col in cols}

    dropped_prepost = set(getattr(cfg, "PREPROCESS", {}).get("dropped_cols_prepost", []))
    qtypes = available_qtypes(dataset_key, df, cfg.QTYPES_CATEGORIZED, dropped_prepost)
    with st.sidebar:
        st.divider()
        qtype = st.selectbox(
            "Question group",
            qtypes,
            format_func=lambda value: cfg.QTYPE_CATEGORY_LABELS.get(value, value),
        )
        question_ids = available_questions(dataset_key, df, qtype, cfg.QTYPES_CATEGORIZED, dropped_prepost)
        question_id = st.selectbox(
            "Question",
            question_ids,
            format_func=lambda value: f"{value}: {question_text(dataset_key, df, value)}",
        )

    ans_format = col_to_format.get(question_id)
    labels = cfg.LABELS.get(ans_format, [])
    kind = answer_kind(ans_format, cfg.ANS_FORMAT)
    question = question_text(dataset_key, df, question_id)

    st.caption(cfg.DATASET_LABELS[dataset_key])
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
            st.dataframe(text_responses(filtered_rows, f"{question_id}_pre"), width='stretch')
        with tabs[1]:
            st.dataframe(text_responses(filtered_rows, f"{question_id}_post"), width='stretch')
        with tabs[2]:
            st.dataframe(
                filtered_question_rows(filtered_rows, dataset_key, question_id, filter_cols, cfg.FILTERS),
                width='stretch',
                hide_index=True,
            )
        return

    if dataset_key == "comparison":
        table = comparison_distribution(filtered_rows, question_id, ans_format, labels, cfg.ANS_FORMAT)
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
                filtered_question_rows(filtered_rows, dataset_key, question_id, filter_cols, cfg.FILTERS),
                width='stretch',
                hide_index=True,
            )
        return

    if kind == "text":
        table = text_responses(filtered_rows, question_id)
        st.dataframe(table, width='stretch', hide_index=True)
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
            filtered_question_rows(filtered_rows, dataset_key, question_id, filter_cols, cfg.FILTERS),
            width = 'stretch',
            hide_index=True,
        )
