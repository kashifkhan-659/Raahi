import json
import time
from pathlib import Path

import streamlit as st

from components.result_card import show_result_card
from logic import matcher


COMPASS_ICON = "\U0001f9ed"
RIGHT_ARROW = "\u2192"
FIELDS_PATH = Path(__file__).resolve().parent / "data" / "fields.json"

st.set_page_config(page_title="Raahi", page_icon=COMPASS_ICON, layout="wide")

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

STUDY_CITY_OPTIONS = CITIES + ["Any"]

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
    if "app_section" not in st.session_state:
        st.session_state["app_section"] = "profile"
    if "quiz_question_index" not in st.session_state:
        st.session_state["quiz_question_index"] = 0
    if "quiz_answers" not in st.session_state:
        st.session_state["quiz_answers"] = {}


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


def show_profile_form():
    with st.form("student_profile_form"):
        left_col, right_col = st.columns(2)

        with left_col:
            fsc_percentage = st.number_input(
                "FSc percentage",
                min_value=40.0,
                max_value=100.0,
                value=75.0,
                step=0.5,
            )
            home_city = st.selectbox("Home city", CITIES)
            gender = st.radio(
                "Gender",
                ["Male", "Female", "Prefer not to say"],
                horizontal=True,
            )

        with right_col:
            annual_budget_pkr = st.slider(
                "Annual budget in PKR",
                min_value=50000,
                max_value=800000,
                value=300000,
                step=25000,
                format="%d",
            )
            preferred_study_cities = st.multiselect(
                "Preferred study cities",
                STUDY_CITY_OPTIONS,
                default=["Any"],
            )

        submitted = st.form_submit_button(f"Find My Path {RIGHT_ARROW}")

    if submitted:
        with st.spinner("Calculating your path..."):
            time.sleep(1)

        st.session_state["student_profile"] = {
            "fsc_percentage": fsc_percentage,
            "home_city": home_city,
            "annual_budget_pkr": annual_budget_pkr,
            "preferred_study_cities": preferred_study_cities,
            "gender": gender,
        }
        st.session_state["app_section"] = "quiz"
        st.session_state["quiz_question_index"] = 0
        st.session_state["quiz_answers"] = {}
        st.rerun()


def show_quiz():
    question_index = st.session_state["quiz_question_index"]
    question_data = QUIZ_QUESTIONS[question_index]
    total_questions = len(QUIZ_QUESTIONS)
    saved_answer = st.session_state["quiz_answers"].get(question_index, 0)

    st.subheader("Personality quiz")
    st.progress((question_index + 1) / total_questions)
    st.caption(f"Question {question_index + 1} of {total_questions}")

    st.markdown(f"### {question_data['question']}")
    selected_option_index = st.radio(
        "Choose one",
        range(len(question_data["options"])),
        format_func=lambda option_index: question_data["options"][option_index][0],
        index=saved_answer,
        label_visibility="collapsed",
        key=f"quiz_question_{question_index}",
    )

    back_col, next_col = st.columns([1, 2])

    with back_col:
        if question_index > 0 and st.button("Back"):
            st.session_state["quiz_answers"][question_index] = selected_option_index
            st.session_state["quiz_question_index"] -= 1
            st.rerun()

    with next_col:
        is_last_question = question_index == total_questions - 1
        button_label = (
            f"See My Results {RIGHT_ARROW}"
            if is_last_question
            else f"Next Question {RIGHT_ARROW}"
        )

        if st.button(button_label, type="primary"):
            st.session_state["quiz_answers"][question_index] = selected_option_index

            if is_last_question:
                st.session_state["field_scores"] = calculate_field_scores(
                    st.session_state["quiz_answers"]
                )
                st.session_state.pop("top_recommendations", None)
                st.session_state["app_section"] = "results"
            else:
                st.session_state["quiz_question_index"] += 1

            st.rerun()


def show_results():
    profile = st.session_state.get("student_profile")
    scores = st.session_state.get("field_scores", {})

    if not profile or not scores:
        st.warning("Please complete your profile and quiz first.")
        if st.button("Start Over"):
            reset_app()
            st.rerun()
        return

    st.header(f"Your Raahi Results {COMPASS_ICON}")
    st.caption("Based on your marks, budget, and thinking style")

    st.markdown(
        (
            "<div style='border:1px solid #e5e7eb;border-radius:8px;"
            "padding:0.8rem 1rem;margin:1rem 0;background:#f9fafb;"
            "font-weight:600;'>"
            f"FSc: {profile['fsc_percentage']:.1f}% | "
            f"Budget: PKR {profile['annual_budget_pkr']:,}/year | "
            f"Top Interest: {get_top_interest(scores)}"
            "</div>"
        ),
        unsafe_allow_html=True,
    )

    fields_data = load_fields_data()

    if "top_recommendations" not in st.session_state:
        with st.spinner("Raahi is finding your path..."):
            st.session_state["top_recommendations"] = matcher.get_top_3(
                fsc_percentage=profile["fsc_percentage"],
                annual_budget=profile["annual_budget_pkr"],
                preferred_cities=profile["preferred_study_cities"],
                gender=profile["gender"],
                personality_scores=scores,
            )

    recommendations = st.session_state.get("top_recommendations", [])
    if not recommendations:
        st.info("No recommendations matched this profile yet. Try increasing the budget or choosing Any city.")
    else:
        for index, result in enumerate(recommendations, start=1):
            field_data = get_field_data_for_result(result, fields_data)
            show_result_card(result.get("rank", index), result, field_data)

    if st.button("Start Over"):
        reset_app()
        st.rerun()


initialize_state()

st.title(f"Raahi {COMPASS_ICON}")
st.caption("Find your realistic university path")

st.markdown(
    """
    <style>
    .block-container {
        max-width: 860px;
        padding-top: 2rem;
    }
    div[data-testid="stForm"] {
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 1.5rem;
        background: #ffffff;
    }
    .stButton > button {
        width: 100%;
        border-radius: 6px;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if st.session_state["app_section"] == "profile":
    show_profile_form()
elif st.session_state["app_section"] == "quiz":
    show_quiz()
else:
    show_results()

st.caption("Raahi MVP | Built for AtomCamp's Hackathon '26 | Data based on 2024-2025 admissions")
