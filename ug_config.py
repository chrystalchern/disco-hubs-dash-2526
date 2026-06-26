from pathlib import Path
APP_DIR = Path(__file__).resolve().parent
PREPROCESS = {
    "pre_main_data_file": APP_DIR / "ug_results_pre_main_2025_10_01.csv",
    "pre_async_data_file": APP_DIR / "ug_results_pre_2026_02_28.csv",
    "post_main_data_file": APP_DIR / "ug_results_post_main_2026_05_16.csv",
    "post_async_data_file": APP_DIR / "ug_results_post_2025_12_13.csv",
    "hub_file": APP_DIR / "ug_official_hubs.csv",
    "cluster_size_file": APP_DIR / "ug_cluster_sizes.csv",
}
DATA_FILES = {
    "pre": APP_DIR / "ug_pre_all.csv",
    "post": APP_DIR / "ug_post_all.csv",
    "comparison": APP_DIR / "ug_pre_post_comparison.csv",
}
RAW_FILES = [
    APP_DIR / "ug_results_pre_main_2025_10_01.csv",
    APP_DIR / "ug_results_post_main_2026_05_16.csv",
    APP_DIR / "ug_official_hubs.csv",
    APP_DIR / "ug_cluster_sizes.csv",
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

FILTERS = ["HUB_01", "MENTOR_08", "CLUSTER_SIZE", "PRIOR_01", "START", "END", "TIME_IN_PROGRAM"]
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
    "PRIOR_01": [],
    "START": [],
    "END": []
}
DESCRIPTIVE_LABELS = {
    "HUB_01": "Hub",
    "MENTOR_08": "Average time spent with mentor",
    "CLUSTER_SIZE": "Number of undergraduates in cluster",
    "PRIOR_01": "Prior Research Experience",
    "START": "Start Date",
    "END": "End Date",
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

PAGE_TITLE = "Discovery Hubs AY25-26 Undergraduate Impact"