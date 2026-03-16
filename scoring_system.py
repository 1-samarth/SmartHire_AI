def calculate_score(text, skills):

    text = text.lower()

    matched = []

    for skill in skills:
        if skill in text:
            matched.append(skill)

    score = (len(matched) / len(skills)) * 100

    return score, matched