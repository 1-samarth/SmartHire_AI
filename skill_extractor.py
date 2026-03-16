def extract_skills(text):

    skills_db = [
        "python",
        "machine learning",
        "sql",
        "deep learning",
        "data analysis",
        "pandas",
        "numpy",
        "tensorflow",
        "power bi",
        "excel"
    ]

    found_skills = []

    text = text.lower()

    for skill in skills_db:
        if skill in text:
            found_skills.append(skill)

    return found_skills