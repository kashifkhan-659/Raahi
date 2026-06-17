from collections import Counter

from .scorer import PROGRAM_TO_PERSONALITY_KEY, rank_university_programs


WITHIN_BUDGET_LABELS = {"Comfortable", "Within Budget"}

PROGRAM_GROUPS = {
    "BS Computer Science": "Computing",
    "BS Software Engineering": "Computing",
    "BS Artificial Intelligence": "Computing",
    "BS Data Science": "Computing",
    "BS Electrical Engineering": "Engineering",
    "BS Mechanical Engineering": "Engineering",
    "BS Civil Engineering": "Engineering",
    "BBA": "Business",
    "BS Accounting & Finance": "Business",
    "BS Psychology": "Social Sciences",
    "BS Pharmacy": "Health Sciences",
    "MBBS": "Health Sciences",
}


def get_top_recommendations(
    fsc_percentage,
    annual_budget,
    preferred_cities,
    gender,
    personality_scores,
):
    """Score universities first, then return the best 3 balanced matches."""
    ranked_results = rank_university_programs(
        fsc_percentage=fsc_percentage,
        annual_budget=annual_budget,
        preferred_cities=preferred_cities,
        gender=gender,
        personality_scores=personality_scores,
    )
    return select_top_recommendations(ranked_results)


def get_top_3(
    fsc_percentage,
    annual_budget,
    preferred_cities,
    gender,
    personality_scores,
):
    """Compatibility wrapper for the app's top-3 recommendation flow."""
    return get_top_recommendations(
        fsc_percentage=fsc_percentage,
        annual_budget=annual_budget,
        preferred_cities=preferred_cities,
        gender=gender,
        personality_scores=personality_scores,
    )


def select_top_recommendations(ranked_results):
    """Pick 3 recommendations from scorer output with diversity guardrails."""
    if not ranked_results:
        return []

    selected = []
    university_counts = Counter()

    strong_match = _first_eligible(
        ranked_results,
        selected,
        university_counts,
        lambda result: result.get("admission_label") == "Strong Match",
    )
    if strong_match:
        _add_recommendation(selected, university_counts, strong_match)

    within_budget = _first_eligible(
        ranked_results,
        selected,
        university_counts,
        _is_fully_within_budget,
    )
    if within_budget:
        _add_recommendation(selected, university_counts, within_budget)

    while len(selected) < 3:
        next_match = _first_eligible(
            ranked_results,
            selected,
            university_counts,
            lambda result: _adds_program_variety(result, selected)
            and _adds_group_variety(result, selected),
        )
        if not next_match:
            next_match = _first_eligible(
                ranked_results,
                selected,
                university_counts,
                lambda result: _adds_program_variety(result, selected),
            )
        if not next_match:
            next_match = _first_eligible(
                ranked_results,
                selected,
                university_counts,
                lambda result: _adds_group_variety(result, selected),
            )
        if not next_match:
            next_match = _first_eligible(
                ranked_results,
                selected,
                university_counts,
                lambda result: True,
            )
        if not next_match:
            break

        _add_recommendation(selected, university_counts, next_match)

    selected.sort(key=lambda result: result.get("total_score", 0), reverse=True)
    return [_with_recommendation_details(result, index + 1) for index, result in enumerate(selected[:3])]


def _first_eligible(ranked_results, selected, university_counts, predicate):
    selected_ids = {_result_id(result) for result in selected}

    for result in ranked_results:
        if _result_id(result) in selected_ids:
            continue
        if university_counts[result.get("university_name")] >= 2:
            continue
        if predicate(result):
            return result

    return None


def _add_recommendation(selected, university_counts, result):
    selected.append(result)
    university_counts[result.get("university_name")] += 1


def _result_id(result):
    return (
        result.get("university_name"),
        result.get("program_name"),
        result.get("city"),
    )


def _is_fully_within_budget(result):
    return result.get("budget_label") in WITHIN_BUDGET_LABELS


def _adds_program_variety(result, selected):
    selected_programs = [item.get("program_name") for item in selected]
    return selected_programs.count(result.get("program_name")) < 2


def _adds_group_variety(result, selected):
    if len(selected) < 2:
        return True

    selected_groups = [PROGRAM_GROUPS.get(item.get("program_name")) for item in selected]
    next_group = PROGRAM_GROUPS.get(result.get("program_name"))

    # Avoid three picks from the same broad area when another strong area exists.
    return selected_groups.count(next_group) < 2


def _with_recommendation_details(result, rank):
    recommendation = dict(result)
    recommendation["rank"] = rank
    recommendation["why_list"] = _build_why_list(result)
    recommendation["risk_list"] = _build_risk_list(result)
    recommendation["primary_field_score"] = _primary_field_score(result)
    return recommendation


def _build_why_list(result):
    why_list = []

    admission_label = result.get("admission_label")
    if admission_label == "Strong Match":
        why_list.append("Admission looks strong")
    elif admission_label == "Likely":
        why_list.append("Admission likely")
    elif admission_label == "Reach":
        why_list.append("Possible reach option")

    budget_label = result.get("budget_label")
    if budget_label == "Comfortable":
        why_list.append("Comfortably within your budget")
    elif budget_label == "Within Budget":
        why_list.append("Within your budget")

    if result.get("personality_score", 0) >= 15:
        why_list.append("Strong fit for your thinking style")
    elif result.get("personality_score", 0) > 0:
        why_list.append("Some fit with your interests")

    if result.get("city_score", 0) == 15:
        why_list.append("Matches your city preference")

    return why_list[:4]


def _build_risk_list(result):
    risks = []

    if result.get("budget_label") == "Slightly Over Budget":
        risks.append("Slightly above budget")
    if result.get("admission_label") == "Reach":
        risks.append("Competitive merit")
    if result.get("personality_score", 0) < 8:
        risks.append("Lower personality fit")

    return risks[:2]


def _primary_field_score(result):
    program_name = result.get("program_name")
    field_key = PROGRAM_TO_PERSONALITY_KEY.get(program_name, "Unknown")
    score = result.get("personality_score", 0)
    return f"{field_key}: {score}/30"
