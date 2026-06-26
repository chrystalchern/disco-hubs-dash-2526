"""
Pre-process the pre and post surveys:

1) Discard extraneous data.
   i)   Irrelevant columns, e.g. start date, location, free
        response questions, and recipient name.
   ii)  Responses with null 'ExternalReference' -- these are
        empty.
   iii) Duplicate users, keeping the response with more
        columns filled.
2) Reformat lengthy questions.
3) Add column: CLUSTER_SIZE to both pre and post;
   Replace HUB_01 in post with official records;
   Add HUB_01 and MENTOR_08 to pre
   Add END to pre
   Add START to post
4) Create the following, discarding identifying data including
   name, email, and CalNetID.
   i)   A merged dataframe of common questions in the pre and
        post (pre_post_comparison.csv)
   ii)  A dataframe of all the questions that appear in the
        pre-survey (pre_all.csv)
   iii) A dataframe of the all questions that appear in the
        post-survey (post_all.csv).
   iv)  A dataframe of the questions that only appear in the
        pre-survey (pre_only.csv)
   v)   A dataframe of the questions that only appear in the
        post-survey (post_only.csv).
"""

import pandas as pd
import numpy as np
import textwrap
import json
import re

# Verbosity: allow printing.
# False = no printing;
# 1 or True = some detail;
# 2 = extensive detail
verbose = 2

## Irrelevant columns
extra_cols = [
    'StartDate',
    'EndDate',
    'Status',
    'IPAddress',
    'Progress',
    'Duration (in seconds)',
    'Finished',
    'RecordedDate',
    'RecipientLastName',
    'RecipientFirstName',
    'RecipientEmail',
    'LocationLatitude',
    'LocationLongitude',
    'DistributionChannel',
    'UserLanguage',
    'CALNETUSER',
    ]

# 0) Load the raw data

# Helper function to load, validate columns, extract dates, and stack dataframes
def load_and_stack(main_file, async_file, date_col, meta_label, async_rename_dict=None):
    main_df = pd.read_csv(main_file)
    async_df = pd.read_csv(async_file)

    # Apply one-off column corrections if provided
    if async_rename_dict:
        async_df.rename(columns=async_rename_dict, inplace=True)

    # Check for column mismatches
    main_cols = list(main_df.columns)
    async_cols = list(async_df.columns)

    if main_cols != async_cols:
        print(f"\n[Column Mismatch] Found differences between '{main_file}' and '{async_file}':")
        only_in_main = [c for c in main_cols if c not in async_cols]
        only_in_async = [c for c in async_cols if c not in main_cols]

        if only_in_main:
            print(f"  Missing from async file (will be filled with NaN): {only_in_main}")
        if only_in_async:
            print(f"  Extra in async file (will be discarded): {only_in_async}")

        # Reindex async dataframe to match the main dataframe's columns
        async_df = async_df.reindex(columns=main_df.columns)

    # Extract dates (YYYY_MM_DD) from filenames
    main_date_match = re.search(r'\d{4}_\d{2}_\d{2}', main_file.name)
    async_date_match = re.search(r'\d{4}_\d{2}_\d{2}', async_file.name)

    main_date = main_date_match.group(0) if main_date_match else "Unknown"
    async_date = async_date_match.group(0) if async_date_match else "Unknown"

    # Separate metadata (first 2 rows) from actual data (row 2 onwards)
    main_meta = main_df.iloc[:2].copy()
    main_data = main_df.iloc[2:].copy()
    async_data = async_df.iloc[2:].copy()  # Drop async metadata rows to avoid duplicating headers

    # Add date columns to data sections
    main_data[date_col] = main_date
    async_data[date_col] = async_date

    # Combine the data rows
    combined_data = pd.concat([main_data, async_data], ignore_index=True)

    # Metadata rows (row 0 gets meta_label, row 1 gets NaN)
    main_meta[date_col] = [meta_label, np.nan]

    # Stack the metadata back on top of the merged data
    return pd.concat([main_meta, combined_data], ignore_index=True)

def load_and_stack_no_async(main_file, date_col, meta_label):
    main_df = pd.read_csv(main_file)

    # Extract dates (YYYY_MM_DD) from filenames
    main_date_match = re.search(r'\d{4}_\d{2}_\d{2}', main_file.name)
    main_date = main_date_match.group(0) if main_date_match else "Unknown"

    # Separate metadata (first 2 rows) from actual data (row 2 onwards)
    main_meta = main_df.iloc[:2].copy()
    main_data = main_df.iloc[2:].copy()

    # Add date columns to data sections
    main_data[date_col] = main_date

    # Metadata rows (row 0 gets meta_label, row 1 gets NaN)
    main_meta[date_col] = [meta_label, np.nan]

    # Stack the metadata back on top of the main data
    return pd.concat([main_meta, main_data], ignore_index=True)

def reformat_question(question, width=70):
    if question is not np.nan:
        return f"{textwrap.fill(question, width)}"

def preprocess(pp_dictionary, type):
    if type == 'ug':
        results_pre_raw = load_and_stack(pp_dictionary.get('pre_main_data_file'),
                                         pp_dictionary.get('pre_async_data_file'),
                                         'START',
                                         'Earliest Discovery Hubs pre-survey date'
        )

        results_post_raw = load_and_stack(pp_dictionary.get('post_main_data_file'),
                                          pp_dictionary.get('post_async_data_file'),
                                          'END',
                                          'Latest Discovery Hubs pre-survey date',
                                          async_rename_dict={'PLANS_02_7_TEXT': 'PLANS_02_9_TEXT'}
        )
    if type == "grad":
        results_pre_raw = load_and_stack_no_async(pp_dictionary.get('pre_main_data_file'),
                                         'START',
                                         'Earliest Discovery Hubs pre-survey date'
                                         )

        results_post_raw = load_and_stack_no_async(pp_dictionary.get('post_main_data_file'),
                                          'END',
                                          'Latest Discovery Hubs pre-survey date',
                                          )

    # 1) Discard extraneous data
    header_pre = results_pre_raw.drop(labels=extra_cols, axis=1, errors='ignore').iloc[:2].copy()
    results_pre = results_pre_raw.drop(labels=extra_cols, axis=1, errors='ignore').iloc[2:].copy()
    header_post = results_post_raw.drop(labels=extra_cols, axis=1, errors='ignore').iloc[:2].copy()
    results_post = results_post_raw.drop(labels=extra_cols, axis=1, errors='ignore').iloc[2:].copy()

    ## ii)  Responses with null 'ExternalReference'
    results_pre.dropna(subset=['ExternalReference'], inplace=True)
    results_post.dropna(subset=['ExternalReference'], inplace=True)

    # iii) Duplicate users, keep the more complete response
    ## Sort by Response Id first (latest first)
    results_pre.sort_values('ResponseId', ascending=False, inplace=True, kind='mergesort')
    results_post.sort_values('ResponseId', ascending=False, inplace=True, kind='mergesort')

    ## Then count notnas, sort by notna_count (most first), then drop duplicates, keep first
    results_pre['notna_count'] = results_pre.notna().sum(axis=1)
    results_pre.sort_values('notna_count', ascending=False, inplace=True, kind='mergesort')
    results_pre.drop_duplicates(subset=['ExternalReference'], keep='first', inplace=True)
    results_pre.drop('notna_count', axis=1, inplace=True)
    results_post['notna_count'] = results_post.notna().sum(axis=1)
    results_post.sort_values('notna_count', ascending=False, inplace=True, kind='mergesort')
    results_post.drop_duplicates(subset=['ExternalReference'], keep='first', inplace=True)
    results_post.drop('notna_count', axis=1, inplace=True)

    # 2) Add columns such as CLUSTER SIZE and time spent with mentor
    # For UG data:
        # Replace HUB_01 in post with official records;
        # Add HUB_01 to pre and post
        # Add CLUSTER_SIZE to pre and post
        # Add END to pre
        # Add START to post
        # Add MENTOR_08 to pre
    # For Grad data:
        # Add HUB_01 to pre and post
        # Add CLUSTER_SIZE to pre and post
        # Add END to pre
        # Add START to post

    # Time spent with mentor (UG only)
    if type == 'ug':
        results_pre = pd.merge(results_pre, results_post[['MENTOR_08', 'ExternalReference']], on='ExternalReference',
                           how='left')

    # Add EndDate to pre and StartDate to post
    results_pre = pd.merge(results_pre, results_post[['END', 'ExternalReference']], on='ExternalReference', how='left')
    results_post = pd.merge(results_post, results_pre[['START', 'ExternalReference']], on='ExternalReference',
                            how='left')

    # Cluster sizes (no de-duplicate because response should count towards both clusters they participated in)
    cluster_sizes = pd.read_csv(pp_dictionary.get("cluster_size_file"))[['ExternalReference', 'CLUSTER_SIZE']]
    results_pre = pd.merge(results_pre, cluster_sizes, on='ExternalReference', how='left')
    results_post = pd.merge(results_post, cluster_sizes, on='ExternalReference', how='left')
    # Official hubs (no de-duplicate because response should count towards both clusters they participated in)
    if 'HUB_01' in results_post.columns:
        results_post = results_post.drop(columns=['HUB_01'])
    official_hubs = pd.read_csv(pp_dictionary.get("hub_file"))[['ExternalReference', 'HUB_01']]
    results_pre = pd.merge(results_pre, official_hubs, on='ExternalReference', how='left')
    results_post = pd.merge(results_post, official_hubs, on='ExternalReference', how='left')

    # TODO: Compute time in program
    # Add column to results_pre, results_post, header_pre, and header_post called "TIME_IN_PROGRAM"
    # Fill in column with helper function, compute_time_in_program(start, end)
    def compute_time_in_program(start, end):
        """Return number of semester student has
        participated in the Discovery Hubs"""
        if start == "..." and end == "...":
            return 1
        elif start == "..." and end == "...":
            return 1
        elif start == "..." and end == "...":
            return 2
    # TODO: Find correct pandas syntax to use compute_time_in_program to fill in the "TIME_IN_PROGRAM" column
    # results_pre["TIME_IN_PROGRAM"].apply(compute_time_in_program(results_pre["START"],results_pre["END"]))
    # results_post["TIME_IN_PROGRAM"].apply(compute_time_in_program(results_pre["START"],results_pre["END"]))

    # Add headers back on
    if verbose >= 2:
        print(f"\n{len(results_pre)=}")
        print(f"{len(results_post)=}")
    results_pre = pd.concat([header_pre,results_pre.copy()], ignore_index=True)
    results_post = pd.concat([header_post,results_post.copy()], ignore_index=True)

    # 3) Reformat lengthy questions
    # Rename columns in the pre (UG only):
    # BELONG -> BELONG_01
    # Because this question was named BELONG_01 in the post.
    # ACCESS_01_19_TEXT -> ACCESS_01_7_TEXT
    # Because this question had fewer possible answers
    # in the post and therefore was named ACCESS_01_7_TEXT.
    if type == 'ug':
        results_pre.rename(columns={'BELONG': 'BELONG_01'}, inplace=True)
        results_pre.rename(columns={'ACCESS_01_19_TEXT': 'ACCESS_01_7_TEXT'}, inplace=True)

    pre_cols = results_pre.columns
    post_cols = results_post.columns
    # TODO: add "TIME_IN_PROGRAM" as a filter
    if type == 'ug':
        filters = ["HUB_01", "CLUSTER_SIZE", "MENTOR_08", "PRIOR_01", "START", "END"]
    if type == 'grad':
        filters = ["HUB_01", "CLUSTER_SIZE", "START", "END"]
    for col in pre_cols:
        if col not in filters:
            results_pre.loc[0, col] = reformat_question(results_pre.loc[0, col])
    for col in post_cols:
        if col not in filters:
            results_post.loc[0, col] = reformat_question(results_post.loc[0, col])

    # 4) Create de-identified dataframes
    common_cols = [col for col in post_cols if col in pre_cols]
    pre_only_cols = [col for col in pre_cols if col not in post_cols]
    post_only_cols = [col for col in post_cols if col not in pre_cols]
    if verbose:
        with open("common_cols.json", "w") as f:
            json.dump(common_cols,f)
        with open("pre_only_cols.json", "w") as f:
            json.dump(pre_only_cols,f)
        with open("post_only_cols.json", "w") as f:
            json.dump(post_only_cols,f)
        print(f"\n{common_cols=}")
        print(f"\n{pre_only_cols=}")
        print(f"\n{post_only_cols=}")

    ## i) Merged dataframe with questions common to both pre and post.
    identity_col = 'ExternalReference' # Contains CalNetID
    pre_compare = results_pre.drop(pre_only_cols, axis=1).rename(columns=lambda x: x+"_pre"
                                                                if x in common_cols and x!=identity_col and x!='ResponseId'
                                                                else x)
    post_compare = results_post.drop(post_only_cols, axis=1).rename(columns=lambda x: x+"_post"
                                                                    if x in common_cols and x!=identity_col and x!='ResponseId'
                                                                    else x)
    pre_post_comparison = pd.merge(pre_compare,post_compare,
                                on=identity_col, how='inner')
    pre_post_comparison.drop(identity_col, axis=1, inplace=True)
    pre_post_comparison.to_csv(type + '_pre_post_comparison.csv')
    if verbose:
        print(f"\nTotal number of responders in pre and post:")
        print(f"{len(pre_compare)=}; 2 rows are question metadata which means N={len(pre_compare)-2}")
        print(f"{len(post_compare)=}; 2 rows are question metadata which means N={len(post_compare)-2}")
        print(F"\nTotal number of responders that responded to BOTH the pre and the post:")
        print(f"{len(pre_post_comparison)=}; 2 rows are question metadata which means N={len(pre_post_comparison)-2}")

    ## ii) Dataframe of **ALL** the questions that appear in the pre-survey
    results_pre.to_csv(type + '_pre_all.csv')

    ## ii) Dataframe of **ALL** the questions that appear in the post-survey
    results_post.to_csv(type + '_post_all.csv')

    ## iv) Dataframe of the questions that only appear in the pre-survey, but keep filtering columns
    common_cols_minus_filters = [c for c in common_cols if c not in filters]
    pre_only = results_pre.drop(common_cols_minus_filters, axis=1)
    pre_only.to_csv(type + '_pre_only.csv')
    if verbose:
        print(f"\nTotal number of responders in pre and post:")
        print(f"{len(pre_only)=}; 2 rows are question metadata which means N={len(pre_only)-2}")

    ## v) Dataframe of the questions that only appear in the post-survey, but keep filtering columns
    post_only = results_post.drop(common_cols_minus_filters, axis=1)
    post_only.to_csv(type + '_post_only.csv')
    if verbose:
        print(f"{len(post_only)=}; 2 rows are question metadata which means N={len(post_only)-2}")

if __name__ == "__main__":
    from ug_config import PREPROCESS as ug_pp_dictionary
    from grad_config import PREPROCESS as grad_pp_dictionary
    preprocess(ug_pp_dictionary, type='ug')
    preprocess(grad_pp_dictionary, type='grad')
