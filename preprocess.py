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

# 0) Load the raw data

# Helper function to load, validate columns, extract dates, and stack dataframes safely
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

        # Reindex async dataframe to perfectly match the main dataframe's columns
        async_df = async_df.reindex(columns=main_df.columns)

    # Extract dates (YYYY_MM_DD) from filenames
    main_date_match = re.search(r'\d{4}_\d{2}_\d{2}', main_file)
    async_date_match = re.search(r'\d{4}_\d{2}_\d{2}', async_file)

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

    # Configure date column for metadata rows (row 0 gets the custom label, row 1 gets NaN)
    main_meta[date_col] = [meta_label, np.nan]

    # Stack the metadata back on top of the merged data tracking
    return pd.concat([main_meta, combined_data], ignore_index=True)


results_pre_raw = load_and_stack(
    'results_pre_main_2025_10_01.csv',
    'results_pre_2026_02_28.csv',
    'START',
    'Earliest Discovery Hubs pre-survey date'
)

results_post_raw = load_and_stack(
    'results_post_main_2026_05_16.csv',
    'results_post_2025_12_13.csv',
    'END',
    'Latest Discovery Hubs pre-survey date',
    async_rename_dict={'PLANS_02_7_TEXT': 'PLANS_02_9_TEXT'}
)

# 1) Discard extraneous data

## i) Irrelevant columns
extra_cols = [
    'StartDate',
    'EndDate',
    'Status',
    'IPAddress',
    'Progress',
    'Duration (in seconds)',
    'Finished',
    'RecordedDate',
    # 'ResponseId',
    'RecipientLastName',
    'RecipientFirstName',
    'RecipientEmail',
    'LocationLatitude',
    'LocationLongitude',
    'DistributionChannel',
    'UserLanguage',
    # 'PRIOR_04', # free response, both pre and post.
    # 'PRIOR_05', # free response, post only
    # 'PRIOR_07', # free response, post only
    # 'INTEREST_02', # free response, post only
    # 'INTEREST_06', # free response, post only
    # 'TESTIMONIAL', # free response, post only
    'CALNETUSER',
    ]
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

if verbose >= 2:
    print(f"\n{len(results_pre)=}")
    print(f"{len(results_post)=}")

results_pre = pd.concat([header_pre,results_pre.copy()], ignore_index=True)
results_post = pd.concat([header_post,results_post.copy()], ignore_index=True)

# 2) Add CLUSTER_SIZE to both pre and post;
    # Replace HUB_01 in post with official records;
    # Add HUB_01 to pre;
    # Add MENTOR_08 to pre
# Cluster sizes
cluster_sizes = pd.read_csv("cluster_sizes.csv")[['ExternalReference', 'CLUSTER_SIZE']]
results_pre = pd.merge(results_pre, cluster_sizes, on='ExternalReference', how='left')
results_post = pd.merge(results_post, cluster_sizes, on='ExternalReference', how='left')
# Official hubs
results_post = results_post.drop(columns=['HUB_01'])
official_hubs = pd.read_csv("official_hubs.csv")[['ExternalReference', 'HUB_01']]
results_pre = pd.merge(results_pre, official_hubs, on='ExternalReference', how='left')
results_post = pd.merge(results_post, official_hubs, on='ExternalReference', how='left')

results_pre = pd.merge(results_pre, results_post[['MENTOR_08', 'ExternalReference']], on='ExternalReference', how='left')

# 3) Reformat lengthy questions
def reformat_question(question, width=70):
    if question is not np.nan:
        return f"{textwrap.fill(question,width)}"
    

# Rename columns in the pre:
# BELONG -> BELONG_01
    # Because this question was named BELONG_01 in the post.
# ACCESS_01_19_TEXT -> ACCESS_01_7_TEXT
    # Because this question had fewer possible answers
    # in the post and therefore was named ACCESS_01_7_TEXT.
results_pre.rename(columns={'BELONG':'BELONG_01'}, inplace=True)
results_pre.rename(columns={'ACCESS_01_19_TEXT':'ACCESS_01_7_TEXT'}, inplace=True)

pre_cols = results_pre.columns
post_cols = results_post.columns
for col in pre_cols:
    if col not in ["HUB_01", "CLUSTER_SIZE", "MENTOR_08"]:
        results_pre.loc[0,col] = reformat_question(results_pre.loc[0,col])
for col in post_cols:
    if col not in ["HUB_01", "CLUSTER_SIZE", "MENTOR_08"]:
        results_post.loc[0,col] = reformat_question(results_post.loc[0,col])

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
pre_post_comparison.to_csv('pre_post_comparison.csv')
if verbose:
    print(f"\nTotal number of responders in pre and post:")
    print(f"{len(pre_compare)=}; 2 rows are question metadata which means N={len(pre_compare)-2}")
    print(f"{len(post_compare)=}; 2 rows are question metadata which means N={len(post_compare)-2}")
    print(F"\nTotal number of responders that responded to BOTH the pre and the post:")
    print(f"{len(pre_post_comparison)=}; 2 rows are question metadata which means N={len(pre_post_comparison)-2}")

## ii) Dataframe of **ALL** the questions that appear in the pre-survey
results_pre.to_csv('pre_all.csv')

## ii) Dataframe of **ALL** the questions that appear in the post-survey
results_post.to_csv('post_all.csv')

## iv) Dataframe of the questions that only appear in the pre-survey, but keep filtering columns
common_cols_minus_filters = [c for c in common_cols if c not in ["HUB_01", "CLUSTER_SIZE", "MENTOR_08"]]
pre_only = results_pre.drop(common_cols_minus_filters, axis=1)
pre_only.to_csv('pre_only.csv')
if verbose:
    print(f"\nTotal number of responders in pre and post:")
    print(f"{len(pre_only)=}; 2 rows are question metadata which means N={len(pre_only)-2}")

## v) Dataframe of the questions that only appear in the post-survey, but keep filtering columns
post_only = results_post.drop(common_cols_minus_filters, axis=1)
post_only.to_csv('post_only.csv')
if verbose:
    print(f"{len(post_only)=}; 2 rows are question metadata which means N={len(post_only)-2}")
