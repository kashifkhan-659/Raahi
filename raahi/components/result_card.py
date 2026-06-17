from html import escape

import streamlit as st


RANK_EMOJIS = {
    1: "\U0001f947",
    2: "\U0001f948",
    3: "\U0001f949",
}

ADMISSION_BADGES = {
    "Strong Match": ("Strong Match \u2705", "#dcfce7", "#166534", "#86efac"),
    "Likely": ("Likely \U0001f7e1", "#fef9c3", "#854d0e", "#fde047"),
    "Reach": ("Reach \u26a0\ufe0f", "#ffedd5", "#9a3412", "#fdba74"),
}

BUDGET_BADGES = {
    "Comfortable": ("Comfortable \u2705", "#dcfce7", "#166534", "#86efac"),
    "Within Budget": ("Within Budget \u2705", "#dcfce7", "#166534", "#86efac"),
    "Slightly Over Budget": (
        "Slightly Over \u26a0\ufe0f",
        "#ffedd5",
        "#9a3412",
        "#fdba74",
    ),
}


def show_result_card(rank, result, field_data):
    """Render one recommendation card for a matched university program."""
    rank_emoji = RANK_EMOJIS.get(rank, "")
    program_name = result.get("program_name", "Unknown program")
    university_name = result.get("university_name", "Unknown university")
    city = result.get("city", "Unknown city")
    sector = str(result.get("sector", "Unknown")).title()
    ranking_tier = result.get("ranking_tier", "Unknown")

    st.markdown("<br>", unsafe_allow_html=True)
    with st.container(border=True):
        header_left, header_right = st.columns([4, 1], vertical_alignment="center")
        with header_left:
            st.caption(f"{rank_emoji} Option #{rank}")
            st.markdown(f"#### {escape(program_name)} at {escape(university_name)}")
            st.caption(f"{city} | {sector} | Ranking Tier {ranking_tier}")
        with header_right:
            total_score = result.get("total_score", 0)
            st.metric("Score", f"{total_score:g}")

        st.markdown("<br>", unsafe_allow_html=True)
        admission_col, budget_col = st.columns(2)

        with admission_col:
            st.markdown("**\U0001f393 Admission Status**")
            _show_badge(result.get("admission_label"), ADMISSION_BADGES)
            st.caption(
                "Your FSc: "
                f"{_format_percent(result.get('fsc_percentage'))} | "
                f"Cutoff: {_format_percent(result.get('merit_cutoff_percentage'))}"
            )

        with budget_col:
            st.markdown("**\U0001f4b0 Budget Status**")
            st.write(f"Fees: PKR {_format_money(result.get('annual_fee_pkr'))}/year")
            _show_badge(result.get("budget_label"), BUDGET_BADGES)

        st.markdown("<br>", unsafe_allow_html=True)
        why_col, risk_col = st.columns(2)

        with why_col:
            st.markdown("**\u2728 Why This**")
            _show_bullet_list(result.get("why_list", []))

        risks = result.get("risk_list", [])
        if risks:
            with risk_col:
                st.markdown("**\u26a0\ufe0f Risks**")
                for risk in risks[:2]:
                    st.markdown(
                        (
                            "<div style='color:#9a3412;background:#ffedd5;"
                            "border:1px solid #fdba74;border-radius:6px;"
                            "padding:0.45rem 0.6rem;margin-bottom:0.35rem;"
                            "overflow-wrap:anywhere;'>"
                            f"{escape(str(risk))}</div>"
                        ),
                        unsafe_allow_html=True,
                    )

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**\U0001f4bc Salary Outlook**")
        salary_col, demand_col = st.columns(2)
        with salary_col:
            st.write(
                "After graduation: "
                f"PKR {_format_money(field_data.get('salary_min_pkr'))}-"
                f"{_format_money(field_data.get('salary_max_pkr'))}/month"
            )
        with demand_col:
            st.write(f"Market Demand: {field_data.get('demand', 'Unknown')}")

        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("\U0001f447 What graduates actually do"):
            jobs = field_data.get("jobs_after_3_years", [])
            if jobs:
                _show_bullet_list(jobs)

            reality_note = field_data.get("reality_note")
            if reality_note:
                st.write(reality_note)

            growth_outlook = field_data.get("growth_outlook")
            if growth_outlook:
                st.caption(f"Growth outlook: {growth_outlook}")

    st.markdown("<br>", unsafe_allow_html=True)


def _show_badge(label, badge_map):
    badge_text, bg_color, text_color, border_color = badge_map.get(
        label,
        (str(label or "Unknown"), "#f3f4f6", "#374151", "#d1d5db"),
    )
    st.markdown(
        (
            "<span style='display:inline-block;padding:0.25rem 0.6rem;"
            f"border-radius:999px;background:{bg_color};color:{text_color};"
            f"border:1px solid {border_color};font-weight:700;font-size:0.9rem;"
            "white-space:normal;overflow-wrap:anywhere;'>"
            f"{escape(badge_text)}</span>"
        ),
        unsafe_allow_html=True,
    )


def _show_bullet_list(items):
    if not items:
        st.caption("No details available yet.")
        return

    for item in items:
        st.markdown(f"- {escape(str(item))}")


def _format_money(value):
    try:
        return f"{int(value):,}"
    except (TypeError, ValueError):
        return "N/A"


def _format_percent(value):
    try:
        return f"{float(value):.1f}%"
    except (TypeError, ValueError):
        return "N/A"
