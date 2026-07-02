from pathlib import Path
APP_DIR = Path(__file__).resolve().parent
PREPROCESS = {
    "pre_main_data_file": APP_DIR / "grad_results_pre_main_2025_10_01.csv",
    "post_main_data_file": APP_DIR / "grad_results_post_main_2026_05_16.csv",
    "hub_file": APP_DIR / "grad_official_hubs_cluster_sizes.csv",
    "cluster_size_file": APP_DIR / "grad_official_hubs_cluster_sizes.csv",
    "dropped_cols_prepost": ["PRIOR"]
}
DATA_FILES = {
    "pre": APP_DIR / "grad_pre_all.csv",
    "post": APP_DIR / "grad_post_all.csv",
    "comparison": APP_DIR / "grad_pre_post_comparison.csv",
}
RAW_FILES = [
    APP_DIR / "grad_results_pre_main_2025_10_01.csv",
    APP_DIR / "grad_results_post_main_2026_05_16.csv",
    APP_DIR / "grad_official_hubs_cluster_sizes.csv",
]

QTYPES_CATEGORIZED = {
    "PRIOR": [
        'PRIOR',
    ],
    "TIME": [
        'TIME',
    ],
    "REWARD": [
        'REWARD_01',
        'REWARD_02',
    ],
    "SUPPORT": [
        'SUPPORT_01',
        'SUPPORT_02',
        'SUPPORT_03',
        'SUPPORT_04',
    ],
    "PROFICIENCY_PROJ": [
        'PROFICIENCY_PROJ_01',
        'PROFICIENCY_PROJ_02',
        'PROFICIENCY_PROJ_03',
        'PROFICIENCY_PROJ_04',
    ],
    "PROFICIENCY_COMM": [
        'PROFICIENCY_COMM_01',
        'PROFICIENCY_COMM_02',
        'PROFICIENCY_COMM_03',
        'PROFICIENCY_COMM_04',
        'PROFICIENCY_COMM_05',
    ],
    "INTEREST": [
        "INTEREST_1", # post only
        "INTEREST_2_1",  # post only
        "INTEREST_2_4",  # post only
        "INTEREST_2_5",  # post only
        "INTEREST_2_6",  # post only
        "INTEREST_2_9",  # post only
        "INTEREST_2_10", # post only
        "INTEREST_2_11", # post only
        "INTEREST_3", # post only
        "INTEREST_4_1", # post only
        "INTEREST_4_2", # post only
        "INTEREST_4_3", # post only
        "INTEREST_4_4", # post only
        "INTEREST_5", # post only
    ],
    "MENTOR_FORMAT": [
        "MENTOR_FORMAT_1_1",  # post only
    ],
    "FREE_RESPONSE": [
        "FUTURE",  # free response
        "RESOURCES_01",  # free response, post only
        "MENTOR_FORMAT_2",  # free response, post only
        "OPPORTUNITIES",  # free response, post only
        "TESTIM_01", # free response, post only
        "TESTIM_02", # free response, post only
        "TESTIM_03", # free response, post only
        "INTEREST_5_2_TEXT",  # post only
    ]
}

COLS = {
    "prior_semesters" : [
        'PRIOR',
    ],
    "prior_weekly" : [
        'TIME',
    ],
    "agree" : [
        'REWARD_01',
        'REWARD_02',
        'SUPPORT_01',
        'SUPPORT_02',
        'SUPPORT_03',
        'SUPPORT_04',
    ],
    "proficiency": [
        'PROFICIENCY_PROJ_01',
        'PROFICIENCY_PROJ_02',
        'PROFICIENCY_PROJ_03',
        'PROFICIENCY_PROJ_04',
        'PROFICIENCY_COMM_01',
        'PROFICIENCY_COMM_02',
        'PROFICIENCY_COMM_03',
        'PROFICIENCY_COMM_04',
        'PROFICIENCY_COMM_05',
    ],
    "slider": [
        "MENTOR_FORMAT_1_1" # post only
    ],
    "yesno": [
        "INTEREST_1" # post only
    ],
    "rank_aspects": [
        "INTEREST_2_1",  # post only
        "INTEREST_2_4",  # post only
        "INTEREST_2_5",  # post only
        "INTEREST_2_6",  # post only
        "INTEREST_2_9",  # post only
        "INTEREST_2_10", # post only
        "INTEREST_2_11", # post only
    ],
    "length": [
        "INTEREST_3" # post only
    ],
    "rank_format": [
        "INTEREST_4_1", # post only
        "INTEREST_4_2", # post only
        "INTEREST_4_3", # post only
        "INTEREST_4_4", # post only
    ],
    "topics": [
        "INTEREST_5" # post only
    ],
    "other": [
        "FUTURE", # free response
        "RESOURCES_01", # free response, post only
        "MENTOR_FORMAT_2", # free response, post only
        "OPPORTUNITIES", # free response, post only
        "TESTIM_01", # free response, post only
        "TESTIM_02", # free response, post only
        "TESTIM_03", # free response, post only
        "INTEREST_5_2_TEXT" # post only
    ]
}


LABELS = {
    "prior_semesters"  : ["3+ semesters", "1-2 semesters", "<1 semester", "None"],
    "prior_weekly" : ["12+ hrs/wk", "8-12 hrs/wk", "4-8 hrs/wk", "0-4 hrs/wk", "None"],
    "agree" : ["Strongly Agree", "Agree", "Somewhat Agree", "Somewhat Disagree", "Disagree", "Strongly Disagree"],
    "proficiency" : ["Excellent", "Very Good", "Good", "Fair", "Poor", "Very Poor"],
    "slider": None, # 0=within hub; 100=standard grad program structure
    "yesno" : ["Yes", "No", "Other"],
    "rank_aspects": [ # ranking
                "The opportunity to mentor",
                "Leadership workshops",
                "Stipend",
                "Undergraduate assistance to move your research forward",
                "The opportunity to look into a new research topic",
                "Funding for supplies and equipment",
                "Research Symposium"
                     ],
    "length": [ # multiselect
                "Semester long",
                "Year long",
                "Year with possibility of extending into summer",
                "Spring with possibility of extending into summer",
              ],
    "rank_format": [ # ranking
                "Lecture/Lesson",
                "Interactive workshop",
                "Panel/Q&A",
                "Guided discussion with peers"
                    ],
    "topics": [ # multiselect
                "Research Design & Grant Writing",
                "Project & Budget Management",
                "Leadership & Team Management",
                "Mentorship & Teaching Skills",
                "Community-Centered Leadership",
                "Communication & Presentation",
                "Networking & Professional Growth"
              ],
    "other": None # text
}


ANS_FORMAT = {
    # "single_select": ["prior_semesters","prior_weekly","agree","proficiency","yesno"],
    "single_select": ["prior_semesters","prior_weekly","agree","proficiency"],
    "multi_select": ["length","topics"],
    "slider": ["slider"],
    "ranking": ["rank_aspects","rank_format"],
    "text": ["other"]
}

FILTERS = ["HUB_01", "CLUSTER_SIZE", "START", "END", "TIME_IN_PROGRAM"]
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
    "CLUSTER_SIZE": ["1", "2", "3", "4", "5", "6", "7", "8"],
    "START": [],
    "END": []
}
DESCRIPTIVE_LABELS = {
    "HUB_01": "Hub",
    "CLUSTER_SIZE": "Number of undergraduates in cluster",
    "START": "Start Date",
    "END": "End Date",
    "TIME_IN_PROGRAM": "Number of semesters in program",
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

QTYPE_CATEGORY_LABELS = {
    "PRIOR": "Prior experience",
    "TIME": "Time commitment",
    "REWARD": "Reward",
    "SUPPORT": "Support",
    "PROFICIENCY_PROJ": "Proficiency: managing research projects",
    "PROFICIENCY_COMM": "Proficiency: communicating & mentoring",
    "INTEREST": "Future interest",
    "MENTOR_FORMAT": "Mentor format",
    "FREE_RESPONSE": "Free response",
}

PAGE_TITLE = "Discovery Hubs AY25-26 Graduate Impact"