from collections import Counter


def summarize_text(content: str) -> str:
    words = content.split()
    if len(words) <= 50:
        return content
    return ' '.join(words[:50]) + '...'


def generate_quiz(content: str) -> list[dict]:
    tokens = [w.strip('.,!?').lower() for w in content.split() if len(w) > 4]
    common = [word for word, _ in Counter(tokens).most_common(3)]
    questions = []
    for keyword in common:
        questions.append({
            'question': f"Which topic is emphasized in this lesson?",
            'options': [keyword, 'unrelated', 'generic', 'unknown'],
            'answer': keyword
        })
    return questions


def recommend_courses(interests: list[str], catalog: list[dict]) -> list[dict]:
    result = []
    for item in catalog:
        score = sum(1 for interest in interests if interest.lower() in item['topic'].lower())
        if score:
            result.append({**item, 'match_score': score})
    return sorted(result, key=lambda x: x['match_score'], reverse=True)


def build_roadmap(goal: str) -> dict:
    return {
        'goal': goal,
        'steps': [
            'Week 1-2: Fundamentals and vocabulary',
            'Week 3-4: Build mini projects',
            'Week 5-6: Complete assignments and peer discussion',
            'Week 7-8: Capstone + certification'
        ]
    }
