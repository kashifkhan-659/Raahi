from pathlib import Path

import pandas as pd


DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "universities.csv"
MAX_PERSONALITY_SCORE = 18

PROGRAM_TO_PERSONALITY_KEY = {
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

REQUIRED_COLUMNS = [
    "university_name",
    "city",
    "program_name",
    "annual_fee_pkr",
    "merit_cutoff_percentage",
    "sector",
    "ranking_tier",
]


def _load_universities(csv_path):
    try:
        universities = pd.read_csv(csv_path)
    except FileNotFoundError:
        return pd.DataFrame(columns=REQUIRED_COLUMNS)
    except pd.errors.EmptyDataError:
        return pd.DataFrame(columns=REQUIRED_COLUMNS)

    for column in REQUIRED_COLUMNS:
        if column not in universities.columns:
            universities[column] = pd.NA

    universities["annual_fee_pkr"] = pd.to_numeric(
        universities["annual_fee_pkr"], errors="coerce"
    )
    universities["merit_cutoff_percentage"] = pd.to_numeric(
        universities["merit_cutoff_percentage"], errors="coerce"
    )

    return universities


def _score_admission(fsc_percentage, merit_cutoff):
    if pd.isna(merit_cutoff):
        return None, None

    if fsc_percentage >= merit_cutoff + 5:
        return 30, "Strong Match"
    if fsc_percentage >= merit_cutoff:
        return 20, "Likely"
    if fsc_percentage >= merit_cutoff - 3:
        return 10, "Reach"

    return 0, None


def _score_budget(annual_budget, annual_fee):
    if pd.isna(annual_fee):
        return None, None

    if annual_fee <= annual_budget * 0.8:
        return 25, "Comfortable"
    if annual_fee <= annual_budget:
        return 20, "Within Budget"
    if annual_fee <= annual_budget * 1.15:
        return 10, "Slightly Over Budget"

    return 0, None


def _score_personality(program_name, personality_scores):
    field_key = PROGRAM_TO_PERSONALITY_KEY.get(program_name)
    if not field_key:
        return 0

    raw_score = personality_scores.get(field_key, 0) or 0
    normalized_score = (raw_score / MAX_PERSONALITY_SCORE) * 30
    return round(min(normalized_score, 30), 2)


def _score_city(city, preferred_cities):
    if not preferred_cities:
        return 0

    normalized_preferences = {str(city_name).strip().lower() for city_name in preferred_cities}
    if "any" in normalized_preferences:
        return 15

    return 15 if str(city).strip().lower() in normalized_preferences else 0


def rank_university_programs(
    fsc_percentage,
    annual_budget,
    preferred_cities,
    gender,
    personality_scores,
    csv_path=DATA_PATH,
):
    """Rank university and program combinations for a student profile.

    The current scoring model uses admission fit, affordability, personality
    fit, and preferred city. Gender is accepted for the profile contract but is
    not scored until gender-policy rules are defined in the product.
    """
    del gender

    universities = _load_universities(csv_path)
    if universities.empty:
        return []

    personality_scores = personality_scores or {}
    preferred_cities = preferred_cities or []
    ranked_results = []

    for _, row in universities.iterrows():
        admission_score, admission_label = _score_admission(
            fsc_percentage, row["merit_cutoff_percentage"]
        )
        if not admission_score:
            continue

        budget_score, budget_label = _score_budget(annual_budget, row["annual_fee_pkr"])
        if not budget_score:
            continue

        personality_score = _score_personality(row["program_name"], personality_scores)
        city_score = _score_city(row["city"], preferred_cities)
        total_score = admission_score + budget_score + personality_score + city_score

        ranked_results.append(
            {
                "university_name": row["university_name"],
                "program_name": row["program_name"],
                "city": row["city"],
                "sector": row.get("sector", "Unknown"),
                "ranking_tier": row.get("ranking_tier", "Unknown"),
                "annual_fee_pkr": int(row["annual_fee_pkr"]),
                "merit_cutoff_percentage": float(row["merit_cutoff_percentage"]),
                "fsc_percentage": float(fsc_percentage),
                "total_score": round(total_score, 2),
                "admission_score": admission_score,
                "budget_score": budget_score,
                "personality_score": personality_score,
                "city_score": city_score,
                "admission_label": admission_label,
                "budget_label": budget_label,
            }
        )

    ranked_results.sort(key=lambda result: result["total_score"], reverse=True)
    return ranked_results[:10]
