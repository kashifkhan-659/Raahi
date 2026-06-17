import json
from html import escape
from pathlib import Path

import streamlit as st

from logic import matcher


COMPASS_ICON = "\U0001f9ed"
RIGHT_ARROW = "\u2192"
LEFT_ARROW = "\u2190"
MIDDLE_DOT = "\u00b7"
FIELDS_PATH = Path(__file__).resolve().parent / "data" / "fields.json"

st.set_page_config(page_title="Raahi", page_icon=COMPASS_ICON, layout="wide")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    :root {
        --background: #111415;
        --surface: #111415;
        --surface-container-lowest: #0c0f10;
        --surface-container-low: #191c1d;
        --surface-container: #1d2021;
        --surface-container-high: #282a2b;
        --surface-container-highest: #323536;
        --surface-bright: #373a3b;
        --surface-variant: #323536;
        --primary: #62dbb7;
        --primary-container: #15a382;
        --primary-fixed-dim: #62dbb7;
        --on-primary: #00382b;
        --on-primary-container: #003025;
        --on-background: #e1e3e4;
        --on-surface: #e1e3e4;
        --on-surface-variant: #bccac3;
        --outline: #86948d;
        --outline-variant: #3d4944;
        --error: #ffb4ab;
        --error-container: #93000a;
        --shadow-lg: 0 8px 24px rgba(0, 0, 0, 0.5);
    }

    html, body, [data-testid="stAppViewContainer"] {
        background: var(--background);
        color: var(--on-background);
        font-family: Inter, sans-serif;
        overflow-x: hidden;
    }

    .main .block-container {
        max-width: 800px;
        margin-left: max(272px, calc(50vw - 272px));
        margin-right: max(16px, calc(50vw - 528px));
        padding: 2rem 1rem 6rem;
    }

    header[data-testid="stHeader"],
    section[data-testid="stSidebar"] {
        display: none;
    }

    h1, h2, h3, h4, p, label, span, div {
        font-family: Inter, sans-serif;
    }

    h1 {
        color: var(--primary);
        font-size: 48px;
        line-height: 56px;
        letter-spacing: 0;
        font-weight: 700;
    }

    h2 {
        color: var(--on-surface);
        font-size: 32px;
        line-height: 40px;
        letter-spacing: 0;
        font-weight: 600;
    }

    h3 {
        color: var(--on-surface);
        font-size: 20px;
        line-height: 28px;
        letter-spacing: 0;
        font-weight: 500;
    }

    .stCaptionContainer,
    [data-testid="stCaptionContainer"] {
        color: var(--on-surface-variant);
    }

    .raahi-shell {
        display: flex;
        gap: 0;
        min-height: 100vh;
    }

    .raahi-side-nav {
        position: fixed;
        inset: 0 auto 0 0;
        width: 256px;
        background: var(--surface);
        border-right: 1px solid var(--outline-variant);
        padding: 24px;
        display: flex;
        flex-direction: column;
        gap: 16px;
        z-index: 1;
    }

    .raahi-brand {
        border-bottom: 1px solid var(--surface-container-low);
        padding-bottom: 24px;
        margin-bottom: 12px;
    }

    .raahi-brand-title {
        color: var(--primary);
        font-size: 32px;
        line-height: 40px;
        font-weight: 600;
        margin: 0;
    }

    .raahi-brand-subtitle {
        color: var(--on-surface-variant);
        font-size: 14px;
        line-height: 20px;
        margin: 4px 0 0;
    }

    .raahi-nav-item {
        align-items: center;
        border-radius: 16px;
        color: var(--on-surface-variant);
        display: flex;
        gap: 16px;
        padding: 12px 16px;
        font-size: 20px;
        line-height: 28px;
        font-weight: 500;
    }

    .raahi-nav-item.active {
        background: var(--surface-container-high);
        color: var(--primary);
    }

    .raahi-user {
        align-items: center;
        display: flex;
        gap: 16px;
        margin-top: auto;
    }

    .raahi-avatar {
        align-items: center;
        background: var(--surface-container-highest);
        border: 1px solid var(--outline-variant);
        border-radius: 999px;
        display: flex;
        height: 40px;
        justify-content: center;
        width: 40px;
    }

    .raahi-main {
        margin-left: 256px;
    }

    .mobile-topbar {
        display: none;
    }

    .step-dots {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        margin: 0 0 24px;
    }

    .step-dot {
        background: var(--surface-variant);
        border-radius: 999px;
        height: 8px;
        width: 8px;
    }

    .step-dot.active {
        background: var(--primary);
        width: 32px;
    }

    .step-dot.done {
        background: var(--primary);
        opacity: 0.55;
        width: 16px;
    }

    .stProgress > div > div > div > div {
        background-color: var(--primary);
    }

    .banner-card {
        align-items: flex-start;
        background: var(--primary-container);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 32px;
        box-shadow: var(--shadow-lg);
        color: var(--on-primary-container);
        display: flex;
        gap: 16px;
        margin-bottom: 40px;
        padding: 24px;
    }

    .banner-icon {
        align-items: center;
        background: rgba(255, 255, 255, 0.16);
        border-radius: 999px;
        display: flex;
        flex-shrink: 0;
        height: 40px;
        justify-content: center;
        width: 40px;
    }

    .banner-card h2 {
        color: var(--on-primary-container);
        font-size: 20px;
        line-height: 28px;
        margin: 0 0 8px;
    }

    .banner-card p {
        color: rgba(0, 48, 37, 0.82);
        font-size: 14px;
        line-height: 20px;
        margin: 0;
    }

    .section-card,
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: var(--surface-container);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 32px;
        padding: 24px;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        box-shadow: var(--shadow-lg);
    }

    .section-title {
        color: var(--on-surface-variant);
        font-size: 12px;
        font-weight: 600;
        letter-spacing: 0.05em;
        line-height: 16px;
        margin: 0 0 16px;
        text-transform: uppercase;
    }

    .quiz-card {
        background: var(--surface-bright);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 48px;
        box-shadow: var(--shadow-lg);
        margin: 24px 0;
        padding: 40px 24px;
    }

    .quiz-card h2 {
        margin-bottom: 40px;
        text-align: center;
    }

    .summary-bar {
        align-items: center;
        background: var(--surface-container-low);
        border: 1px solid var(--outline-variant);
        border-radius: 32px;
        color: var(--on-surface-variant);
        display: flex;
        flex-wrap: wrap;
        gap: 16px;
        justify-content: space-between;
        margin-bottom: 24px;
        padding: 12px;
    }

    .results-title {
        align-items: center;
        border-bottom: 1px solid var(--surface-container-high);
        display: flex;
        gap: 12px;
        margin-bottom: 24px;
        padding-bottom: 12px;
    }

    .results-title h2 {
        margin: 0;
    }

    .result-card {
        background: var(--surface-container);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 48px;
        box-shadow: var(--shadow-lg);
        margin-bottom: 16px;
        overflow: hidden;
        padding: 24px;
        position: relative;
    }

    .result-card.best {
        background: var(--surface-bright);
    }

    .result-badge {
        background: var(--primary-container);
        border-bottom-left-radius: 16px;
        color: var(--on-primary-container);
        font-size: 12px;
        font-weight: 600;
        line-height: 16px;
        padding: 6px 12px;
        position: absolute;
        right: 0;
        top: 0;
    }

    .result-head {
        align-items: flex-start;
        display: flex;
        gap: 16px;
        margin-bottom: 16px;
        padding-right: 110px;
    }

    .medal {
        align-items: center;
        border-radius: 999px;
        display: flex;
        flex-shrink: 0;
        height: 48px;
        justify-content: center;
        width: 48px;
    }

    .medal.gold {
        background: rgba(255, 215, 0, 0.16);
        border: 1px solid rgba(255, 215, 0, 0.45);
        color: #FFD700;
    }

    .medal.silver {
        background: rgba(192, 192, 192, 0.16);
        border: 1px solid rgba(192, 192, 192, 0.45);
        color: #C0C0C0;
    }

    .medal.bronze {
        background: rgba(205, 127, 50, 0.16);
        border: 1px solid rgba(205, 127, 50, 0.45);
        color: #CD7F32;
    }

    .result-card h3 {
        color: var(--on-surface);
        margin: 0 0 4px;
    }

    .result-card p {
        color: var(--on-surface-variant);
        font-size: 14px;
        line-height: 20px;
        margin: 0;
    }

    .pill-row {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin: 12px 0;
    }

    .info-pill {
        align-items: center;
        background: var(--surface-container);
        border: 1px solid var(--outline-variant);
        border-radius: 999px;
        color: var(--on-surface-variant);
        display: inline-flex;
        font-size: 12px;
        font-weight: 600;
        gap: 6px;
        line-height: 16px;
        padding: 6px 12px;
    }

    .danger-pill {
        background: rgba(255, 180, 171, 0.10);
        border-color: rgba(255, 180, 171, 0.30);
        color: var(--error);
    }

    .mini-heading {
        color: var(--on-surface);
        font-size: 14px;
        font-weight: 700;
        margin: 16px 0 8px;
    }

    ul.raahi-list {
        color: var(--on-surface-variant);
        font-size: 14px;
        line-height: 20px;
        margin: 0;
        padding-left: 20px;
    }

    .stTextInput input,
    .stNumberInput input,
    .stSelectbox div[data-baseweb="select"] > div,
    .stMultiSelect div[data-baseweb="select"] > div {
        background: var(--background);
        border-color: var(--outline-variant);
        border-radius: 12px;
        color: var(--on-surface);
    }

    label,
    .stRadio label,
    .stSlider label,
    .stSelectbox label,
    .stMultiSelect label,
    .stNumberInput label {
        color: var(--on-surface);
    }

    .stSlider [data-testid="stTickBar"] {
        color: var(--on-surface-variant);
    }

    .stButton > button {
        border-color: var(--outline-variant);
        border-radius: 16px;
        color: var(--on-surface-variant);
        font-size: 20px;
        font-weight: 500;
        line-height: 28px;
        padding: 10px 24px;
    }

    .stButton > button[kind="primary"] {
        background: var(--primary);
        border-color: var(--primary);
        box-shadow: var(--shadow-lg);
        color: #0a0a0a;
    }

    .stRadio div[role="radiogroup"] {
        gap: 8px;
    }

    .stRadio div[role="radiogroup"] label {
        background: var(--surface-variant);
        border: 1px solid var(--outline-variant);
        border-radius: 16px;
        padding: 10px 14px;
    }

    .stRadio div[role="radiogroup"] label:has(input:checked) {
        background: rgba(98, 219, 183, 0.12);
        border-color: var(--primary);
        color: var(--primary);
    }

    div[data-testid="stExpander"] {
        background: var(--surface-container-low);
        border: 1px solid var(--outline-variant);
        border-radius: 16px;
        color: var(--on-surface);
    }

    .mobile-bottom-nav {
        display: none;
    }

    @media (max-width: 900px) {
        .raahi-side-nav {
            display: none;
        }

        .raahi-main {
            margin-left: 0;
        }

        .mobile-topbar {
            align-items: center;
            background: var(--background);
            border-bottom: 1px solid var(--outline-variant);
            display: flex;
            justify-content: space-between;
            margin: -2rem -1rem 24px;
            padding: 12px 16px;
            position: sticky;
            top: 0;
            z-index: 5;
        }

        .mobile-bottom-nav {
            align-items: center;
            background: var(--surface-container);
            border-top: 1px solid var(--outline-variant);
            border-top-left-radius: 32px;
            border-top-right-radius: 32px;
            bottom: 0;
            box-shadow: var(--shadow-lg);
            display: flex;
            justify-content: space-around;
            left: 0;
            padding: 8px 16px;
            position: fixed;
            right: 0;
            z-index: 10;
        }

        .mobile-nav-item {
            color: var(--on-surface-variant);
            font-size: 12px;
            font-weight: 600;
            line-height: 16px;
            padding: 8px 14px;
            text-align: center;
        }

        .mobile-nav-item.active {
            background: var(--primary-container);
            border-radius: 24px;
            color: var(--on-primary-container);
        }

        h1 {
            font-size: 32px;
            line-height: 40px;
        }

        .main .block-container {
            margin-left: auto;
            margin-right: auto;
        }

        h2 {
            font-size: 24px;
            line-height: 32px;
        }

        .quiz-card,
        .result-card {
            border-radius: 32px;
        }

        .result-head {
            padding-right: 0;
        }

        .result-badge {
            position: static;
            display: inline-block;
            margin-bottom: 16px;
            border-radius: 16px;
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
    defaults = {
        "current_page": "profile",
        "fsc": 75.0,
        "budget": 300000,
        "city": "Rawalpindi",
        "preferred_cities": ["Any"],
        "gender": "Prefer not to say",
        "personality_scores": {},
        "quiz_question_index": 0,
        "quiz_answers": {},
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def set_page(page):
    st.session_state["current_page"] = page


def current_profile():
    return {
        "fsc_percentage": st.session_state["fsc"],
        "home_city": st.session_state["city"],
        "annual_budget_pkr": st.session_state["budget"],
        "preferred_study_cities": st.session_state["preferred_cities"],
        "gender": st.session_state["gender"],
    }


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


def render_shell_start(active_page):
    nav_items = [
        ("profile", "Profile", "person"),
        ("quiz", "Quiz", "quiz"),
        ("results", "Results", "workspace_premium"),
    ]
    nav_html = "".join(
        (
            f"<div class='raahi-nav-item {'active' if active_page == page else ''}'>"
            f"<span>{icon}</span><span>{label}</span></div>"
        )
        for page, label, icon in nav_items
    )
    mobile_nav_html = "".join(
        (
            f"<div class='mobile-nav-item {'active' if active_page == page else ''}'>"
            f"<div>{icon}</div><div>{label}</div></div>"
        )
        for page, label, icon in nav_items
    )

    st.markdown(
        f"""
        <div class="raahi-shell">
            <nav class="raahi-side-nav" aria-label="Main Navigation">
                <div class="raahi-brand">
                    <p class="raahi-brand-title">{COMPASS_ICON} Raahi</p>
                    <p class="raahi-brand-subtitle">University Guidance</p>
                </div>
                <div>{nav_html}</div>
                <div class="raahi-user">
                    <div class="raahi-avatar">person</div>
                    <div>
                        <p style="margin:0;color:var(--on-surface);font-weight:500;">Student</p>
                        <p style="margin:0;color:var(--on-surface-variant);font-size:12px;">Guest User</p>
                    </div>
                </div>
            </nav>
            <main class="raahi-main">
                <header class="mobile-topbar">
                    <div style="color:var(--primary);font-size:24px;font-weight:700;">{COMPASS_ICON} Raahi</div>
                    <div style="color:var(--on-surface-variant);">account_circle</div>
                </header>
        """,
        unsafe_allow_html=True,
    )
    st.session_state["_mobile_nav_html"] = mobile_nav_html


def render_shell_end():
    mobile_nav_html = st.session_state.get("_mobile_nav_html", "")
    st.markdown(
        f"""
            </main>
        </div>
        <nav class="mobile-bottom-nav" aria-label="Mobile Navigation">
            {mobile_nav_html}
        </nav>
        """,
        unsafe_allow_html=True,
    )


def render_step_indicator(active_step):
    dots = []
    for step in range(1, 4):
        class_name = "step-dot"
        if step == active_step:
            class_name += " active"
        elif step < active_step:
            class_name += " done"
        dots.append(f"<div class='{class_name}' aria-label='Step {step}'></div>")

    st.markdown(
        f"<div class='step-dots'>{''.join(dots)}</div>",
        unsafe_allow_html=True,
    )


def render_profile_page():
    render_shell_start("profile")

    st.title(f"{COMPASS_ICON} Raahi")
    st.caption("University guidance for Pakistani students")
    render_step_indicator(1)

    st.markdown(
        """
        <div class="banner-card">
            <div class="banner-icon">map</div>
            <div>
                <h2>Find Your Academic Path</h2>
                <p>Tell us about your background and preferences so we can tailor our university recommendations to your needs.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        st.markdown("<p class='section-title'>Academic Info</p>", unsafe_allow_html=True)
        fsc_col, city_col = st.columns(2)
        with fsc_col:
            fsc = st.number_input(
                "FSc Percentage (%)",
                min_value=40.0,
                max_value=100.0,
                value=float(st.session_state["fsc"]),
                step=0.5,
            )
        with city_col:
            city = st.selectbox(
                "Home City",
                CITIES,
                index=CITIES.index(st.session_state["city"])
                if st.session_state["city"] in CITIES
                else 0,
            )

    st.markdown("<br>", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown("<p class='section-title'>Budget</p>", unsafe_allow_html=True)
        budget = st.slider(
            "Annual Budget",
            min_value=50000,
            max_value=800000,
            value=int(st.session_state["budget"]),
            step=25000,
            label_visibility="collapsed",
        )
        st.markdown(
            f"<p style='color:var(--primary);font-size:24px;font-weight:700;text-align:center;margin:0;'>PKR {budget:,} / year</p>",
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown("<p class='section-title'>Preferences</p>", unsafe_allow_html=True)
        preferred_cities = st.multiselect(
            "Preferred Cities",
            STUDY_CITY_OPTIONS,
            default=[
                city_name
                for city_name in st.session_state["preferred_cities"]
                if city_name in STUDY_CITY_OPTIONS
            ]
            or ["Any"],
        )
        gender = st.radio(
            "Gender",
            ["Female", "Male", "Prefer not to say"],
            index=(
                ["Female", "Male", "Prefer not to say"].index(st.session_state["gender"])
                if st.session_state["gender"] in ["Female", "Male", "Prefer not to say"]
                else 2
            ),
            horizontal=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button(
        f"Next \u2014 Personality Quiz {RIGHT_ARROW}",
        use_container_width=True,
        type="primary",
    ):
        st.session_state["fsc"] = fsc
        st.session_state["budget"] = budget
        st.session_state["city"] = city
        st.session_state["preferred_cities"] = preferred_cities
        st.session_state["gender"] = gender
        st.session_state["quiz_question_index"] = 0
        st.session_state["quiz_answers"] = {}
        st.session_state["personality_scores"] = {}
        st.session_state.pop("top_recommendations", None)
        set_page("quiz")
        st.rerun()

    render_shell_end()


def render_quiz_page():
    render_shell_start("quiz")
    render_step_indicator(2)

    question_index = st.session_state["quiz_question_index"]
    total_questions = len(QUIZ_QUESTIONS)
    question_data = QUIZ_QUESTIONS[question_index]
    progress_value = (question_index + 1) / total_questions
    saved_answer = st.session_state["quiz_answers"].get(question_index, 0)

    progress_col, percent_col = st.columns([3, 1])
    with progress_col:
        st.caption(f"Question {question_index + 1} of {total_questions}")
    with percent_col:
        st.markdown(
            f"<p style='color:var(--primary);text-align:right;margin:0;font-size:12px;font-weight:600;'>{round(progress_value * 100)}%</p>",
            unsafe_allow_html=True,
        )
    st.progress(progress_value)

    st.markdown("<div class='quiz-card'>", unsafe_allow_html=True)
    st.markdown(f"## {escape(question_data['question'])}")
    selected_option_index = st.radio(
        "Choose one",
        range(len(question_data["options"])),
        format_func=lambda option_index: question_data["options"][option_index][0],
        index=saved_answer,
        label_visibility="collapsed",
        key=f"quiz_question_{question_index}",
    )
    st.markdown("</div>", unsafe_allow_html=True)

    back_col, next_col = st.columns(2)
    with back_col:
        if st.button(f"{LEFT_ARROW} Back", use_container_width=True):
            st.session_state["quiz_answers"][question_index] = selected_option_index
            if question_index > 0:
                st.session_state["quiz_question_index"] -= 1
            else:
                set_page("profile")
            st.rerun()

    with next_col:
        is_last_question = question_index == total_questions - 1
        button_label = (
            f"See My Results {RIGHT_ARROW}"
            if is_last_question
            else f"Next Question {RIGHT_ARROW}"
        )
        if st.button(button_label, use_container_width=True, type="primary"):
            st.session_state["quiz_answers"][question_index] = selected_option_index
            if is_last_question:
                st.session_state["personality_scores"] = calculate_field_scores(
                    st.session_state["quiz_answers"]
                )
                st.session_state.pop("top_recommendations", None)
                set_page("results")
            else:
                st.session_state["quiz_question_index"] += 1
            st.rerun()

    render_shell_end()


def badge_class(label):
    if label == "Slightly Over Budget" or label == "Reach":
        return "info-pill danger-pill"
    return "info-pill"


def render_bullet_list(items):
    if not items:
        return "<ul class='raahi-list'><li>No details available yet.</li></ul>"

    list_items = "".join(f"<li>{escape(str(item))}</li>" for item in items)
    return f"<ul class='raahi-list'>{list_items}</ul>"


def render_result_card(rank, result):
    medal_class = {1: "gold", 2: "silver", 3: "bronze"}.get(rank, "bronze")
    admission_label = result.get("admission_label", "Unknown")
    budget_label = result.get("budget_label", "Unknown")
    university_name = result.get("university_name", "Unknown university")
    program_name = result.get("program_name", "Unknown program")
    city = result.get("city", "Unknown city")
    why_list = result.get("why_list", [])
    risk_list = result.get("risk_list", [])
    card_class = "result-card best" if rank == 1 else "result-card"

    risk_html = ""
    if risk_list:
        risk_html = (
            "<p class='mini-heading'>Risk notes</p>"
            f"{render_bullet_list(risk_list)}"
        )

    st.markdown(
        f"""
        <div class="{card_class}">
            <div class="result-badge">{escape(str(admission_label))}</div>
            <div class="result-head">
                <div class="medal {medal_class}">award</div>
                <div>
                    <h3>{escape(str(program_name))}</h3>
                    <p>account_balance {escape(str(university_name))}, {escape(str(city))}</p>
                </div>
            </div>
            <div class="pill-row">
                <span class="{badge_class(admission_label)}">star {escape(str(admission_label))}</span>
                <span class="{badge_class(budget_label)}">payments {escape(str(budget_label))}</span>
            </div>
            <p class="mini-heading">Why this match</p>
            {render_bullet_list(why_list)}
            {risk_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_reality_check(result, field_data):
    salary_min = field_data.get("salary_min_pkr")
    salary_max = field_data.get("salary_max_pkr")
    demand = field_data.get("demand", "Unknown")
    jobs = field_data.get("jobs_after_3_years", [])
    reality_note = field_data.get("reality_note")
    growth_outlook = field_data.get("growth_outlook")

    with st.expander(
        f"Salary and reality check \u2014 {result.get('program_name', 'Program')}"
    ):
        st.write(
            "Salary outlook: "
            f"PKR {_format_money(salary_min)}-{_format_money(salary_max)}/month"
        )
        st.write(f"Market demand: {demand}")
        if jobs:
            st.markdown("**What graduates actually do**")
            for job in jobs:
                st.markdown(f"- {escape(str(job))}")
        if reality_note:
            st.write(reality_note)
        if growth_outlook:
            st.caption(f"Growth outlook: {growth_outlook}")


def render_results_page():
    render_shell_start("results")
    render_step_indicator(3)

    scores = st.session_state.get("personality_scores", {})
    if not scores:
        st.warning("Please complete your profile and quiz first.")
        if st.button("Start Over", use_container_width=True):
            reset_app()
            st.rerun()
        render_shell_end()
        return

    top_field = get_top_interest(scores)
    st.markdown(
        f"""
        <div class="summary-bar">
            <span>person {st.session_state['fsc']:.1f}% FSc | {escape(st.session_state['city'])}</span>
            <span>payments PKR {st.session_state['budget']:,}/yr</span>
            <span style="color:var(--primary);font-weight:600;">{escape(top_field)}</span>
        </div>
        <div class="results-title">
            <span style="color:var(--primary);font-size:32px;">{COMPASS_ICON}</span>
            <h2>Your Raahi Results</h2>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if "top_recommendations" not in st.session_state:
        with st.spinner("Finding your most realistic paths..."):
            st.session_state["top_recommendations"] = matcher.get_top_3(
                fsc_percentage=st.session_state["fsc"],
                annual_budget=st.session_state["budget"],
                preferred_cities=st.session_state["preferred_cities"],
                gender=st.session_state["gender"],
                personality_scores=scores,
            )

    recommendations = st.session_state.get("top_recommendations", [])
    fields_data = load_fields_data()

    if not recommendations:
        st.warning(
            "No recommendations matched this profile yet. Try increasing the "
            "budget or choosing Any city."
        )
    else:
        for index, result in enumerate(recommendations[:3], start=1):
            field_data = get_field_data_for_result(result, fields_data)
            render_result_card(result.get("rank", index), result)
            render_reality_check(result, field_data)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("refresh Start Over", use_container_width=True):
        reset_app()
        st.rerun()

    render_shell_end()


def _format_money(value):
    try:
        return f"{int(value):,}"
    except (TypeError, ValueError):
        return "N/A"


initialize_state()

current_page = st.session_state.get("current_page", "profile")

if current_page == "profile":
    render_profile_page()
elif current_page == "quiz":
    render_quiz_page()
else:
    render_results_page()
