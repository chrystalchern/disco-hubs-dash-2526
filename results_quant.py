import pandas as pd
from pathlib import Path
import os
import matplotlib.pyplot as plt
from qualtrics_utils import clear_questions, write_shortened_question, write_questions
from qualtrics_utils import single_select_tables, multi_select_tables
from qualtrics_utils import multi_axis_barh, single_select_compare_tables, multi_select_compare_tables
from qualtrics_utils import slider_tables, slider_kde, rank_tables, rank_plots, string_tables
import glob

# Which tables to compute
COMPUTE_NEW = {
    "compare": True,
    "pre": True,
    "post": True,
}

# Colors for plots
COLORS = plt.rcParams['axes.prop_cycle'].by_key()['color']

# Read data and set output directories
results = {
    'pre': pd.read_csv(f"pre_only.csv"),
    'post': pd.read_csv(f"post_only.csv"),
    'comparison': pd.read_csv(f"pre_post_comparison.csv")
}

OUT_DIRS = {
    'pre': Path("out/pre-survey"),
    'post': Path("out/post-survey"),
    'comparison': Path("out/comparison"),
    'compare_pre': Path("out/comparison/pre"),
    'compare_post': Path("out/comparison/post")
}
for out_dir in OUT_DIRS.values():
    if not out_dir.exists():
        os.makedirs(out_dir)



# Survey-specific information
COLS = {
    "agree" : [
        'BELONG_01',
        'BELONG_02', # post only
        'MENTOR_02',
        'MENTOR_03',
        'MENTOR_06_1', # post only
        'MENTOR_06_2', # post only
        'MENTOR_06_3', # post only
        'MENTOR_06_4', # post only
        'MENTOR_06_5', # post only
        'MENTOR_06_6', # post only
        'MENTOR_07_1', # post only
        'MENTOR_07_2', # post only
        'MENTOR_07_3', # post only
        'MENTOR_07_4', # post only
        'MENTOR_07_5', # post only
    ],
    "proficiency": [
        'PROFICIENCY_01',
        'PROFICIENCY_02',
        'PROFICIENCY_03',
        'PROFICIENCY_04',
        'PROFICIENCY_05', # post only
    ],
    "yesno": [
        'PRIOR_01',
        'MENTOR_01', # pre only
    ],
    "prior" : [ # multiselect
        'PRIOR_02',
    ],
    "prior_considered" : [ # multiselect
        'PRIOR_06',
    ],
    "num_emails": [
        'PRIOR_03' # pre only
    ],
    "why": [ # multiselect
        'MOTIVATION_01', # post only
    ],
    "mentor_04": [ # multiselect
        'MENTOR_04' # pre only
    ],
    "mentor_05": [ # multiselect
        'MENTOR_05' # pre only
    ],
    "barriers": [ # mutiselect
        'ACCESS_01'
    ],
    "comms": [ # multiselect
        'ACCESS_02' # pre only
    ],
    "plans_01": [
        'PLANS_01', # post only
    ],
    "plans_02": [
        'PLANS_02', # post only
    ],
    "plans_03": [
        'PLANS_03', # post only
    ],
    "interest_01": [
        'INTEREST_01', # post only
    ],
    "length": [
        'INTEREST_03', # post only
    ],
    "timing": [
        'INTEREST_04', # post only
        'INTEREST_05', # post only
    ],
    "other": [ # text questions
        'ACCESS_01_7_TEXT',
        'PRIOR_02_17_TEXT',
        'ACCESS_02_10_TEXT', # pre only
        'PRIOR_06_3_TEXT', # post only
        'MOTIVATION_01_8_TEXT', # post only
        'PLANS_02_9_TEXT', # post only
    ],
    "HUB_01": [ # filtering question
        "HUB_01"
    ],
    "MENTOR_08": [ # filtering question
        "MENTOR_O8"
    ],
    "CLUSTER_SIZE": [ # filtering question
        "CLUSTER_SIZE"
    ],
}

LABELS = {
    "agree" : ["Strongly Agree", "Agree", "Somewhat Agree", "Somewhat Disagree", "Disagree", "Strongly Disagree"],
    "proficiency" : ["Excellent", "Very Good", "Good", "Fair", "Poor", "Very Poor"],
    "yesno" : ["Yes", "No"],
    "prior" : [ # multiselect
        "Participated in this program in a previous academic term",
        "Reached out directly to a professor",
        "Friend or acquaintance connected me to a research group",
        "Seminar or conference",
        "Another program on campus (URAP, SURF, Rose Hills, Haas Scholars, UCDC)",
        "Other"
    ],
    "prior_considered" : [ # multiselect
        "Reaching out directly to a professor",
        "Another program on campus (URAP, SURF, Rose Hills, Haas Scholars)",
        "Other"
    ],
    "num_emails" : ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10+"],
    "why": [ # multiselect
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
    "mentor_04": [ # multiselect
        "My mentor is generally available to meet or talk when I need them.",
        "My mentor is an active listener.",
        "My mentor takes a sincere interest in my career.",
        "My mentor acknowledges my contributions appropriately.",
        "My mentor is supportive of work-life balance.",
        "My mentor motivates me to improve my work.",
    ],
    "mentor_05": [ # multiselect
        "My mentor demonstrates professional expertise.",
        "My mentor is helpful in providing direction and guidance on professional issues.",
        "My mentor helps me to formulate clear goals.",
        "My mentor facilitates building my professional network.",
        "My mentor provides thoughtful advice on my scholarly work.",
    ],
    "barriers": [ # multiselect
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
    "comms": [ # multiselect
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
    "plans_02": [ # multiselect
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
        "Actively applying",
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
    "timing": [
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
    ],
    "other": None, # text questions
    "HUB_01": [ # filtering question
        "Social Sciences",
        "Kavli ENSI",
        "CICI",
        "NASA Space Biosciences",
        "Molecular Foundry",
        "UCSF Anesthesia and Perioperative Care",
        "CNMAT",
        "KALX",
    ],
    "MENTOR_08": [ # filtering question
        "None",
        "More than zero, but less than one hour per week",
        "1-2 hrs/wk",
        "3-4 hrs/week",
        "More than 5 hrs/week",
    ],
    "CLUSTER_SIZE": [ # filtering question
        # "1","2","3","4","5","6","7","8"
        1,2,3,4,5,6,7,8
        ]
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
        "timing"
        ],
    "multi_select": [
        "prior",
        "prior_considered",
        "why",
        "mentor_04",
        "mentor_05",
        "barriers",
        "comms",
        "plans_02"
        ],
    "text": ["other"],
}

# For filtering by HUB_01, MENTOR_08, and CLUSTER_SIZE.
# The columns will be the survey responses for other questions, e.g. "Strongly Agree", "Agree", "Somewhat Agree", etc.
# The rows will be the categories:
#   SOCS
#   KAVL
#   CICI
#   ...
#   0
#   0.5
#   1
#   ...
#   1
#   2
#   3
#   ...
#   Overall

FILTERS = ["HUB_01", "MENTOR_08", "CLUSTER_SIZE"]

FILTER_LABELS = {question_id:answers for question_id,answers in LABELS.items() if question_id in FILTERS}

# Make sure the number of question categories is consistent
assert len(COLS) == len(LABELS)
assert len(COLS) == ( sum([len(aft) for aft in ANS_FORMAT.values()]) + len(FILTERS) )

# Clear the questions list
clear_questions()      

# Generate tables and charts
for qtype,cols in COLS.items():
    labels = LABELS[qtype]
    if qtype=='proficiency':
        # Pre-post comparison for proficiency questions, overall only (no filtering)
        fig = multi_axis_barh(cols=cols[:4], # first four only are comparison
                            labels=labels,
                            qtype=qtype,
                            results=results['comparison'],
                            nrows=2,
                            fig_title="Please rate your level of proficiency in the following areas.")
        fig.savefig(OUT_DIRS['comparison']/f"proficiency.png", dpi=400)
        plt.close()
    for i,col in enumerate(cols):
        # Pre-post comparison. Filtered.
        if f"{col}_pre" in results['comparison'].columns and COMPUTE_NEW['compare']:
            data = results['comparison']
            if qtype in ANS_FORMAT["single_select"]:
                single_select_compare_tables(col=col,compare_data=data,labels=labels,
                                             out_dirs=OUT_DIRS,
                                             filters=FILTERS,filter_labels=FILTER_LABELS)
            elif qtype in ANS_FORMAT["multi_select"]:
                multi_select_compare_tables(col=col,compare_data=data,labels=labels,
                                            out_dirs=OUT_DIRS,
                                            filters=FILTERS,filter_labels=FILTER_LABELS)
            write_shortened_question(col=col,data=data,qtype=qtype)
            write_questions(col=col,data=data)
        # Pre-only and Post-only
        for mode in ['pre','post']:
            if f"{col}" in results[mode].columns and COMPUTE_NEW[mode]:
                data = results[mode]
                if qtype in ANS_FORMAT["single_select"]:
                    single_select_tables(col=col,data=data,labels=labels,
                                         out_dir=OUT_DIRS[mode],
                                         filters=FILTERS,filter_labels=FILTER_LABELS)
                elif qtype in ANS_FORMAT["multi_select"]:
                    multi_select_tables(col=col,data=data,labels=labels,
                                        out_dir=OUT_DIRS[mode],
                                        filters=FILTERS,filter_labels=FILTER_LABELS)
                # No slider in UG Mentees survey
                # elif qtype in ANS_FORMAT["slider"]:
                #     slider_tables(col=col,data=data,out_dir=OUT_DIRS[mode])
                #     fig = slider_kde(col=col,data=data)
                #     fig.savefig(OUT_DIRS[mode]/f"{col}.png", dpi=400)
                #     plt.close()
                elif qtype in ANS_FORMAT["text"]:
                    string_tables(col=col,data=data[col],out_dir=OUT_DIRS[mode])
                # No ranking in UG Mentees survey
                # elif qtype in ANS_FORMAT["ranking"]:
                #     rank_tables(cols=cols,data=data,qtype=qtype,labels=labels,out_dir=OUT_DIRS[mode])
                #     fig = rank_plots(cols=cols,data=data,qtype=qtype,labels=labels,n_ranks=len(COLS[qtype]))
                #     fig.savefig(OUT_DIRS[mode]/f"{col}.png", dpi=400)
                #     plt.close()

                write_shortened_question(col=col,data=results[mode],qtype=qtype)
                write_questions(col=col,data=results[mode])


# Export concatenated data tables

table_order = [
    # common columns
    'HUB_01',
    'MENTOR_08',
    'CLUSTER_SIZE'
    'BELONG_01',
    'MENTOR_02',
    'MENTOR_03',
    'PRIOR_01',
    'PRIOR_02',
    'PRIOR_02_17_TEXT',
    'PROFICIENCY_01',
    'PROFICIENCY_02',
    'PROFICIENCY_03',
    'PROFICIENCY_04',
    'ACCESS_01',
    'ACCESS_01_7_TEXT',
    # pre-only columns
    'MENTOR_01',
    'MENTOR_04',
    'MENTOR_05',
    'PRIOR_03',
    'ACCESS_02',
    # post-only columns
    'BELONG_02',
    'MOTIVATION_01',
    'MENTOR_06_1',
    'MENTOR_06_2',
    'MENTOR_06_3',
    'MENTOR_06_4',
    'MENTOR_06_5',
    'MENTOR_06_6',
    'MENTOR_07_1',
    'MENTOR_07_2',
    'MENTOR_07_3',
    'MENTOR_07_4',
    'MENTOR_07_5',
    'PRIOR_06',
    'PROFICIENCY_05',
    'PLANS_01',
    'PLANS_02',
    'PLANS_03',
    'INTEREST_01',
    'INTEREST_03',
    'INTEREST_04',
    'INTEREST_05'
    # pre-only text columns
    'ACCESS_02_10_TEXT'
    # post-only text columns
    'MOTIVATION_01_8_TEXT',
    'PRIOR_06_3_TEXT',
    'PLANS_02_9_TEXT',
    ]

def combine_files(path, label):
    all_files = glob.glob(path)

    # Clear the combined file
    with open(f"out/{label}-combined.csv", "w") as writefile:
        pass
    # Add each table, in table_order, to the combine file
    with open(f"out/{label}-combined.csv", "a") as appendfile:
        for table in table_order:
            for file in all_files:
                if table in str(file):
                    with open(file, 'r') as readfile:
                        current_table = readfile.read()
                    appendfile.write(current_table)
                    appendfile.write('\n')

combine_files("out/pre-survey/*.csv", 'pre')
combine_files("out/post-survey/*.csv", 'post')

combine_files("out/comparison/pre/*.csv", 'compare-pre')
combine_files("out/comparison/post/*.csv", 'compare-post')