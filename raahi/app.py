import streamlit as st
import json
import os
import google.generativeai as genai

try:
    from logic.scorer import get_scores
except ImportError:
    get_scores = None

from logic.matcher import get_top_3
from components.result_card import show_result_card


st.set_page_config(
    page_title="Raahi 🧭",
    page_icon="🧭",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
<style>
div.stButton > button {
    background-color: #0F6E56;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 0.6rem 1.2rem;
    font-size: 15px;
    font-weight: 500;
    width: 100%;
}
div.stButton > button:hover {
    background-color: #085041;
    color: white;
}
div[data-testid="stNumberInput"] input {
    border-radius: 8px;
}
</style>
""",
    unsafe_allow_html=True,
)

if "page" not in st.session_state:
    st.session_state.page = "profile"
if "quiz_index" not in st.session_state:
    st.session_state.quiz_index = 0
if "quiz_answers" not in st.session_state:
    st.session_state.quiz_answers = {}


QUESTIONS = [
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
                "A building you designed still stands in 50 years",
                {"Civil": 3, "Mech": 2},
            ),
            ("Your startup turns profitable", {"BBA": 3, "Fin": 2}),
            ("You discover a drug that saves lives", {"Med": 3, "Pharma": 3}),
        ],
    },
    {
        "question": "What kind of problem do you enjoy most?",
        "options": [
            ("Logical or algorithmic puzzles", {"CS": 3, "AI": 3, "Data": 2}),
            ("Physical or mechanical challenges", {"Mech": 3, "Elec": 2, "Civil": 2}),
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
        "question": "Which FSc subject did you genuinely enjoy?",
        "options": [
            ("Computer / IT", {"CS": 3, "SE": 2, "AI": 2}),
            ("Physics and Math", {"Elec": 3, "Mech": 2, "Civil": 2}),
            ("Economics or Commerce", {"BBA": 3, "Fin": 3}),
            ("Biology and Chemistry", {"Med": 3, "Pharma": 3}),
        ],
    },
]

FIELD_MAP = {
    "CS": "Computer Science",
    "SE": "Software Engineering",
    "AI": "Artificial Intelligence",
    "Data": "Data Science",
    "Elec": "Electrical Engineering",
    "Mech": "Mechanical Engineering",
    "Civil": "Civil Engineering",
    "BBA": "Business Administration",
    "Fin": "Finance",
    "Med": "Medicine",
    "Pharma": "Pharmacy",
    "Psych": "Psychology",
}

PROGRAM_FIELD_MAP = {
    "BS Computer Science": "Computer Science",
    "BS Software Engineering": "Software Engineering",
    "BS Artificial Intelligence": "Artificial Intelligence",
    "BS Data Science": "Data Science",
    "BS Electrical Engineering": "Electrical Engineering",
    "BS Mechanical Engineering": "Mechanical Engineering",
    "BS Civil Engineering": "Civil Engineering",
    "BBA": "BBA / Business Administration",
    "BS Accounting & Finance": "Accounting & Finance",
    "BS Psychology": "Psychology",
    "BS Pharmacy": "Pharmacy",
    "MBBS": "MBBS / Medicine",
}


def show_profile():
    st.title("🧭 Raahi")
    st.caption("University guidance for Pakistani students")
    st.markdown("---")

    st.progress(0.33)
    st.caption("Step 1 of 3 — Your profile")
    st.markdown(" ")

    st.info(
        "💡 Answer a few questions and Raahi will find your 3 most realistic "
        "university paths — based on your marks, budget, and how you think."
    )
    st.markdown(" ")

    with st.container(border=True):
        st.markdown("##### 📊 Academic Info")

        col1, col2 = st.columns(2)
        with col1:
            fsc = st.number_input(
                "FSc Percentage",
                min_value=40.0,
                max_value=100.0,
                value=float(st.session_state.get("fsc", 75.0)),
                step=0.5,
                help="Enter your FSc marks percentage",
            )
        with col2:
            cities = [
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
            saved_city = st.session_state.get("city", "Islamabad")
            city = st.selectbox(
                "Home City",
                cities,
                index=cities.index(saved_city) if saved_city in cities else 0,
            )

        st.markdown("---")
        st.markdown("##### 💰 Annual Budget")

        budget = st.slider(
            "Budget (PKR per year)",
            min_value=50000,
            max_value=800000,
            value=int(st.session_state.get("budget", 300000)),
            step=25000,
            label_visibility="collapsed",
        )
        st.markdown(f"**PKR {budget:,} / year**")

        st.markdown("---")
        st.markdown("##### 📍 Preferences")

        preferred_options = [
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
        saved_preferred = st.session_state.get("preferred_cities", ["Any"])
        preferred_cities = st.multiselect(
            "Preferred study cities",
            preferred_options,
            default=[
                option for option in saved_preferred if option in preferred_options
            ]
            or ["Any"],
        )

        gender_options = ["Male", "Female", "Prefer not to say"]
        saved_gender = st.session_state.get("gender", "Prefer not to say")
        gender = st.radio(
            "Gender (optional — affects hostel info)",
            gender_options,
            index=gender_options.index(saved_gender)
            if saved_gender in gender_options
            else 2,
            horizontal=True,
        )

    st.markdown(" ")
    if st.button("Next — Personality Quiz →", use_container_width=True):
        if not preferred_cities:
            st.warning("Please select at least one preferred city.")
        else:
            st.session_state.fsc = fsc
            st.session_state.city = city
            st.session_state.budget = budget
            st.session_state.preferred_cities = preferred_cities
            st.session_state.gender = gender
            st.session_state.quiz_index = 0
            st.session_state.quiz_answers = {}
            st.session_state.page = "quiz"
            st.rerun()

    st.markdown("---")
    st.caption(
        "Raahi MVP | Built for AtomCamp's Hackathon '26 | Data based on 2024-2025 admissions"
    )


def show_quiz():
    st.title("🧭 Raahi")
    st.caption("University guidance for Pakistani students")
    st.markdown("---")

    idx = st.session_state.get("quiz_index", 0)
    progress = (idx + 1) / len(QUESTIONS)

    st.progress(progress)
    st.caption(f"Step 2 of 3 — Question {idx + 1} of {len(QUESTIONS)}")
    st.markdown(" ")

    q = QUESTIONS[idx]

    with st.container(border=True):
        st.markdown(f"### {q['question']}")
        st.markdown(" ")

        option_labels = [opt[0] for opt in q["options"]]
        saved_selection = st.session_state.get(f"selected_q_{idx}", option_labels[0])
        selected = st.radio(
            "Choose one:",
            option_labels,
            index=option_labels.index(saved_selection)
            if saved_selection in option_labels
            else 0,
            key=f"q_{idx}",
            label_visibility="collapsed",
        )

    st.markdown(" ")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("← Back", use_container_width=True):
            st.session_state[f"selected_q_{idx}"] = selected
            if idx == 0:
                st.session_state.page = "profile"
            else:
                st.session_state.quiz_index -= 1
            st.rerun()

    with col2:
        label = (
            "See My Results →"
            if idx == len(QUESTIONS) - 1
            else "Next Question →"
        )
        if st.button(label, use_container_width=True):
            st.session_state[f"selected_q_{idx}"] = selected
            for opt_label, scores in q["options"]:
                if opt_label == selected:
                    st.session_state.quiz_answers[idx] = scores
                    break

            if idx == len(QUESTIONS) - 1:
                personality_scores = {}
                for scores in st.session_state.get("quiz_answers", {}).values():
                    for key, val in scores.items():
                        personality_scores[key] = personality_scores.get(key, 0) + val

                st.session_state.personality_scores = personality_scores
                st.session_state.page = "results"
            else:
                st.session_state.quiz_index += 1
            st.rerun()

    st.markdown("---")
    st.caption(
        "Raahi MVP | Built for AtomCamp's Hackathon '26 | Data based on 2024-2025 admissions"
    )


def get_field_data(fields_data, result):
    program_name = result.get("program_name", "")
    field_name = PROGRAM_FIELD_MAP.get(program_name, program_name)
    return fields_data.get(field_name, fields_data.get(program_name, {}))


def show_results():
    st.title("🧭 Raahi")
    st.caption("University guidance for Pakistani students")
    st.markdown("---")

    st.progress(1.0)
    st.caption("Step 3 of 3 — Your results")
    st.markdown(" ")

    fsc = st.session_state.get("fsc", 75.0)
    budget = st.session_state.get("budget", 300000)
    city = st.session_state.get("city", "")
    preferred_cities = st.session_state.get("preferred_cities", ["Any"])
    gender = st.session_state.get("gender", "")
    personality_scores = st.session_state.get("personality_scores", {})

    top_field = (
        max(personality_scores, key=personality_scores.get)
        if personality_scores
        else "General"
    )
    top_field_name = FIELD_MAP.get(top_field, top_field)

    st.info(
        f"📊 FSc: **{fsc}%** · Budget: **PKR {budget:,}/year** · "
        f"Top interest: **{top_field_name}**"
    )
    st.markdown(" ")

    st.markdown("## Your Raahi Results")
    st.caption("3 realistic paths matched to your profile")
    st.markdown(" ")

    fields_path = os.path.join(os.path.dirname(__file__), "data", "fields.json")
    try:
        with open(fields_path, "r", encoding="utf-8") as f:
            fields_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        fields_data = {}

    with st.spinner("🧭 Raahi is finding your path..."):
        try:
            top_3 = get_top_3(
                fsc_percentage=fsc,
                annual_budget=budget,
                preferred_cities=preferred_cities,
                gender=gender,
                personality_scores=personality_scores,
            )
        except Exception as e:
            st.error(f"Could not generate recommendations: {e}")
            return

    if not top_3:
        st.warning(
            "No matches found. Try increasing your budget or adjusting your city preferences."
        )
    else:
        for i, result in enumerate(top_3):
            show_result_card(
                rank=i + 1,
                result=result,
                field_data=get_field_data(fields_data, result),
            )
            st.markdown(" ")

        st.markdown("---")
        st.markdown("### 🤖 Your Personal Career Guidance")
        st.caption("Generated by Gemini AI based on your unique profile")

        prompt = f"""
You are a university and career counselor for Pakistani students.
A student has the following profile:
- FSc Percentage: {fsc}%
- Annual Budget: PKR {budget:,}
- Home City: {city}
- Top personality strength: {top_field_name}
- Personality scores: {personality_scores}
- Top 3 recommended programs: {[r['program_name'] + ' at ' + r['university_name'] for r in top_3]}

Write a short, honest, and encouraging 3-4 sentence career 
guidance message for this student. 
- Mention their strongest trait based on personality scores
- Reference their top recommended program
- Give one practical piece of advice for success in that field
- Be direct and realistic, not generic or overly motivational
- Write as if you are talking directly to the student
- Do not use bullet points, just natural paragraph text
- Keep it under 100 words
"""

        try:
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            model = genai.GenerativeModel("gemini-2.0-flash")
            with st.spinner("Gemini is generating your personal guidance..."):
                response = model.generate_content(prompt)

            st.info(response.text)

        except Exception as e:
            st.error(f"Gemini error: {str(e)}")

    st.markdown("---")
    if st.button("↺ Start Over", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    st.caption(
        "Raahi MVP | Built for AtomCamp's Hackathon '26 | Data based on 2024-2025 admissions"
    )


page = st.session_state.get("page", "profile")

if page == "profile":
    show_profile()
elif page == "quiz":
    show_quiz()
elif page == "results":
    show_results()
