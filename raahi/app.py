import json
from pathlib import Path

import streamlit as st

from components.result_card import show_result_card
from logic import matcher


COMPASS_ICON = "\U0001f9ed"
ACADEMIC_ICON = "\U0001f4ca"
BUDGET_ICON = "\U0001f4b0"
CITY_ICON = "\U0001f3d9\ufe0f"
LOCATION_ICON = "\U0001f4cd"
PERSON_ICON = "\U0001f464"
RIGHT_ARROW = "\u2192"
LEFT_ARROW = "\u2190"
MIDDLE_DOT = "\u00b7"
FIELDS_PATH = Path(__file__).resolve().parent / "data" / "fields.json"

st.set_page_config(page_title="Raahi", page_icon="🧭", layout="centered")

st.markdown(
    """
    <style>
    :root {
        --raahi-teal: #0F6E56;
        --raahi-border: #E5E7EB;
        --raahi-muted: #64748B;
        --raahi-bg: #F8FAFC;
    }

    html, body, [data-testid="stAppViewContainer"] {
        background: var(--raahi-bg);
        overflow-x: hidden;
    }

    .main .block-container {
        max-width: 680px;
        margin: 0 auto;
        padding: 2rem 1rem 3rem;
    }

    [data-testid="stForm"],
    [data-testid="stVerticalBlockBorderWrapper"] {
        background: #FFFFFF;
        border: 1px solid var(--raahi-border);
        border-radius: 8px;
    }

    h1, h2, h3 {
        color: #0F172A;
        letter-spacing: 0;
    }

    .stButton > button {
        border-radius: 6px;
        font-weight: 700;
    }

    .stButton > button[kind="primary"] {
        background: var(--raahi-teal);
        border-color: var(--raahi-teal);
    }

    .stProgress > div > div > div > div {
        background-color: var(--raahi-teal);
    }

    [data-testid="stAlert"] {
        background: #E7F5F1;
        border: 1px solid #B7DED3;
        border-radius: 8px;
        color: #123D33;
    }

    [data-testid="stMarkdownContainer"],
    [data-testid="stCaptionContainer"] {
        overflow-wrap: anywhere;
    }

    section[data-testid="stSidebar"] {
        display: none;
    }

    @media (max-width: 640px) {
        .main .block-container {
            padding-left: 0.75rem;
            padding-right: 0.75rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

CITIES = [
    "Islamabad",
    "Rawalpindi",
    "Lahore",
    "Karachi",
    "Peshawar",
    "Quetta",
    "Multan",
    "Faisalabad",
    "Other",
]

STUDY_CITY_OPTIONS = [
    "Islamabad",
    "Rawalpindi",
    "Lahore",
    "Karachi",
    "Peshawar",
    "Quetta",
    "Multan",
    "Faisalabad",
    "Any",
]

FIELD_KEYS = [
    "CS",
    "SE",
    "AI",
    "Data",
    "Elec",
    "Mech",
    "Civil",
    "BBA",
    "Fin",
    "Med",
    "Pharma",
    "Psych",
]

FIELD_LABELS = {
    "CS": "Computer Science",
    "SE": "Software Engineering",
    "AI": "Artificial Intelligence",
    "Data": "Data Science",
    "Elec": "Electrical Engineering",
    "Mech": "Mechanical Engineering",
    "Civil": "Civil Engineering",
    "BBA": "BBA / Business Administration",
    "Fin": "Accounting & Finance",
    "Med": "MBBS / Medicine",
    "Pharma": "Pharmacy",
    "Psych": "Psychology",
}

PROGRAM_TO_FIELD_KEY = {
    "BS Computer Science": "CS",
    "BS Software Engineering": "SE",
    "BS Artificial Intelligence": "AI",
    "BS Data Science": "Data",
    "BS Electrical Engineering": "Elec",
    "BS Mechanical Engineering": "Mech",
    "BS Civil Engineering": "Civil",
    "BBA": "BBA",
    "BS Accounting & Finance": "Fin",
    "BS Psychology": "Psych",
    "BS Pharmacy": "Pharma",
    "MBBS": "Med",
}

QUIZ_QUESTIONS = [
    {
        "question": "You have a free weekend. Which project sounds most exciting?",
        "options": [
            ("Build a mobile app", {"CS": 3, "SE": 3, "AI": 2}),
            ("Design a bridge or structure", {"Civil": 3, "Mech": 3, "Elec": 2}),
            ("Run a small business experiment", {"BBA": 3, "Fin": 2}),
            ("Analyze a disease outbreak", {"Med": 3, "Pharma": 2, "Data": 2}),
        ],
    },
    {
        "question": "A company gives you a problem with no instructions. What do you do first?",
        "options": [
            ("Write code for a solution", {"CS": 3, "SE": 3, "AI": 2}),
            ("Draw a system or process map", {"Mech": 3, "Civil": 2, "Elec": 2}),
            ("Research data and patterns", {"Data": 3, "AI": 2, "CS": 1}),
            ("Organize people and resources", {"BBA": 3, "Fin": 2}),
        ],
    },
    {
        "question": "Which result would make you proudest?",
        "options": [
            ("Your app has 10,000 users", {"CS": 3, "SE": 3}),
            (
                "A building you designed is still standing in 50 years",
                {"Civil": 3, "Mech": 2},
            ),
            ("Your startup turns profitable", {"BBA": 3, "Fin": 2}),
            ("You discover a new drug that saves lives", {"Med": 3, "Pharma": 3}),
        ],
    },
    {
        "question": "What kind of problem do you enjoy most?",
        "options": [
            ("Logical/algorithmic puzzles", {"CS": 3, "AI": 3, "Data": 2}),
            ("Physical/mechanical challenges", {"Mech": 3, "Elec": 2, "Civil": 2}),
            ("Human behavior and markets", {"BBA": 2, "Psych": 3, "Fin": 2}),
            ("Biological or chemical problems", {"Med": 3, "Pharma": 3}),
        ],
    },
    {
        "question": "Pick your ideal work environment:",
        "options": [
            ("Tech startup or software company", {"CS": 3, "SE": 3, "AI": 2}),
            ("Construction site or manufacturing plant", {"Civil": 3, "Mech": 3}),
            ("Corporate office or bank", {"BBA": 2, "Fin": 3}),
            ("Hospital or research lab", {"Med": 3, "Pharma": 2, "Psych": 2}),
        ],
    },
    {
        "question": "Which subject did you genuinely enjoy in FSc?",
        "options": [
            ("Computer / IT", {"CS": 3, "SE": 2, "AI": 2}),
            ("Physics & Math", {"Elec": 3, "Mech": 2, "Civil": 2}),
            ("Economics or Commerce", {"BBA": 3, "Fin": 3}),
            ("Biology & Chemistry", {"Med": 3, "Pharma": 3}),
        ],
    },
]


def initialize_state():
    if "page" not in st.session_state:
        st.session_state["page"] = "profile"
    if "quiz_question_index" not in st.session_state:
        st.session_state["quiz_question_index"] = 0
    if "quiz_answers" not in st.session_state:
        st.session_state["quiz_answers"] = {}


def set_page(page):
    st.session_state["page"] = page


def show_step(progress_value, label):
    st.progress(progress_value)
    st.caption(label)
    st.markdown("<br>", unsafe_allow_html=True)


def calculate_field_scores(answers):
    scores = {field_key: 0 for field_key in FIELD_KEYS}

    for question_index, option_index in answers.items():
        option_scores = QUIZ_QUESTIONS[question_index]["options"][option_index][1]
        for field_key, points in option_scores.items():
            scores[field_key] += points

    return scores


@st.cache_data
def load_fields_data():
    try:
        with FIELDS_PATH.open("r", encoding="utf-8") as fields_file:
            return json.load(fields_file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def get_top_interest(scores):
    if not scores:
        return "Not available"

    top_field_key, _ = max(scores.items(), key=lambda item: item[1])
    return FIELD_LABELS.get(top_field_key, top_field_key)


def get_field_data_for_result(result, fields_data):
    field_key = PROGRAM_TO_FIELD_KEY.get(result.get("program_name"))
    field_name = FIELD_LABELS.get(field_key, "")
    return fields_data.get(field_name, {})


def reset_app():
    for key in list(st.session_state.keys()):
        del st.session_state[key]


def show_profile_page():
    profile = st.session_state.get("student_profile", {})
    default_city = profile.get("home_city", "Islamabad")
    default_gender = profile.get("gender", "Prefer not to say")
    preferred_default = profile.get("preferred_study_cities", ["Any"])

    st.title("🧭 Raahi")
    st.caption("University guidance for Pakistani students")
    st.markdown("<br>", unsafe_allow_html=True)

    show_step(0.33, "Step 1 of 3 \u2014 Your Profile")

    st.info(
        "Answer a few questions and Raahi will find your 3 most realistic "
        "university paths \u2014 based on your marks, budget, and how you think."
    )
    st.markdown("<br>", unsafe_allow_html=True)

    with st.container(border=True):
        st.subheader(f"{ACADEMIC_ICON} Academic info")
        fsc_col, city_col = st.columns(2)

        with fsc_col:
            fsc = st.number_input(
                "FSc Percentage",
                min_value=40.0,
                max_value=100.0,
                value=float(profile.get("fsc_percentage", 75.0)),
                step=0.5,
            )

        with city_col:
            city = st.selectbox(
                f"{CITY_ICON} Home City",
                CITIES,
                index=CITIES.index(default_city) if default_city in CITIES else 0,
            )

    st.markdown("<br>", unsafe_allow_html=True)
    with st.container(border=True):
        st.subheader(f"{BUDGET_ICON} Annual Budget")
        budget = st.slider(
            "",
            min_value=50000,
            max_value=800000,
            value=int(profile.get("annual_budget_pkr", 300000)),
            step=25000,
        )
        st.caption(f"PKR {budget:,} per year")

    st.markdown("<br>", unsafe_allow_html=True)
    with st.container(border=True):
        st.subheader(f"{LOCATION_ICON} Preferences")
        preferred_cities = st.multiselect(
            "Preferred study cities",
            STUDY_CITY_OPTIONS,
            default=[city for city in preferred_default if city in STUDY_CITY_OPTIONS]
            or ["Any"],
        )
        gender = st.radio(
            f"{PERSON_ICON} Gender (optional \u2014 affects hostel info)",
            ["Male", "Female", "Prefer not to say"],
            index=(
                ["Male", "Female", "Prefer not to say"].index(default_gender)
                if default_gender in ["Male", "Female", "Prefer not to say"]
                else 2
            ),
            horizontal=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button(
        f"Next {RIGHT_ARROW} Personality Quiz",
        use_container_width=True,
        type="primary",
    ):
        st.session_state["student_profile"] = {
            "fsc_percentage": fsc,
            "home_city": city,
            "annual_budget_pkr": budget,
            "preferred_study_cities": preferred_cities,
            "gender": gender,
        }
        st.session_state["quiz_question_index"] = 0
        st.session_state["quiz_answers"] = {}
        st.session_state.pop("field_scores", None)
        st.session_state.pop("top_recommendations", None)
        set_page("quiz")
        st.rerun()


def show_quiz_page():
    question_index = st.session_state["quiz_question_index"]
    question_data = QUIZ_QUESTIONS[question_index]
    total_questions = len(QUIZ_QUESTIONS)
    q_num = question_index + 1
    saved_answer = st.session_state["quiz_answers"].get(question_index, 0)

    show_step(0.66, "Step 2 of 3 \u2014 Personality Quiz")

    if st.button(f"{LEFT_ARROW} Back"):
        set_page("profile")
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    st.caption(f"Question {q_num} of {total_questions}")
    st.subheader(question_data["question"])

    selected_option_index = st.radio(
        "Choose one",
        range(len(question_data["options"])),
        format_func=lambda option_index: question_data["options"][option_index][0],
        index=saved_answer,
        key=f"quiz_question_{question_index}",
    )

    st.markdown("<br>", unsafe_allow_html=True)
    button_label = (
        f"See My Results {RIGHT_ARROW}"
        if question_index == total_questions - 1
        else f"Next Question {RIGHT_ARROW}"
    )

    if st.button(button_label, use_container_width=True, type="primary"):
        st.session_state["quiz_answers"][question_index] = selected_option_index

        if question_index == total_questions - 1:
            st.session_state["field_scores"] = calculate_field_scores(
                st.session_state["quiz_answers"]
            )
            st.session_state.pop("top_recommendations", None)
            set_page("results")
        else:
            st.session_state["quiz_question_index"] += 1

        st.rerun()


def show_results_page():
    profile = st.session_state.get("student_profile")
    scores = st.session_state.get("field_scores", {})

    if not profile or not scores:
        st.warning("Please complete your profile and quiz first.")
        if st.button("Start Over", use_container_width=True):
            reset_app()
            st.rerun()
        return

    show_step(1.0, "Step 3 of 3 \u2014 Your Results")

    top_field = get_top_interest(scores)
    fsc = profile["fsc_percentage"]
    budget = profile["annual_budget_pkr"]
    st.info(f"FSc: {fsc:.1f}% {MIDDLE_DOT} Budget: PKR {budget:,}/year {MIDDLE_DOT} Top interest: {top_field}")

    fields_data = load_fields_data()

    if "top_recommendations" not in st.session_state:
        with st.spinner("Finding your most realistic paths..."):
            st.session_state["top_recommendations"] = matcher.get_top_3(
                fsc_percentage=profile["fsc_percentage"],
                annual_budget=profile["annual_budget_pkr"],
                preferred_cities=profile["preferred_study_cities"],
                gender=profile["gender"],
                personality_scores=scores,
            )

    recommendations = st.session_state.get("top_recommendations", [])
    st.markdown("<br>", unsafe_allow_html=True)

    if not recommendations:
        st.warning(
            "No recommendations matched this profile yet. Try increasing the "
            "budget or choosing Any city."
        )
    else:
        for index, result in enumerate(recommendations[:3], start=1):
            field_data = get_field_data_for_result(result, fields_data)
            show_result_card(result.get("rank", index), result, field_data)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Start Over", use_container_width=True):
        reset_app()
        st.rerun()


initialize_state()

current_page = st.session_state.get("page", "profile")

if current_page == "profile":
    show_profile_page()
elif current_page == "quiz":
    show_quiz_page()
else:
    show_results_page()
