import json
from decouple import config
from openai import OpenAI

import logging

logger = logging.getLogger(__name__)

OPENAI_API_KEY = config('OPENAI_API_KEY', default='')
OPENAI_MODEL = config('OPENAI_MODEL', default='gpt-4o-mini')
openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None


def _extract_json_content(response) -> dict | list:
    content = json.loads(response.choices[0].message.content)
    if isinstance(content, dict):
        return content
    return {"data": content}


def _local_question_fallback(job_title, question_count=5):
    return [
        {
            "id": f"q{i + 1}",
            "question": question,
            "type": "mixed",
            "rubric": "Answer with context, actions, measurable impact, and what you learned."
        }
        for i, question in enumerate([
            f"Can you introduce yourself for the {job_title} role?",
            f"What makes you a strong fit for the {job_title} position?",
            f"Describe a challenging project related to {job_title}.",
            "How do you prioritize work when deadlines are tight?",
            "What value would you bring in your first 90 days?",
            "How do you handle constructive feedback during a project?",
        ][:question_count])
    ]


def _local_grade_fallback():
    return {
        "overallScore": 7.2,
        "hireReadiness": "needs_practice",
        "strengths": ["Clear communication baseline", "Good role understanding"],
        "improvements": ["Add more measurable outcomes", "Use sharper STAR-style examples"],
        "summaryToReadAloud": "You have a solid baseline. Add more quantified impact and more specific examples to strengthen your interview performance.",
    }


def _local_answer_evaluation(answer_text):
    word_count = len(answer_text.split())
    has_numbers = any(character.isdigit() for character in answer_text)
    score = 5.5
    if word_count >= 20:
        score += 1.0
    if word_count >= 40:
        score += 0.8
    if has_numbers:
        score += 0.8
    score = min(score, 9.2)
    feedback = "Answer is understandable."
    if word_count < 20:
        feedback = "Answer is too short. Add more context, action, and measurable impact."
    elif not has_numbers:
        feedback = "Good baseline answer. Add measurable outcomes to make it stronger."
    else:
        feedback = "Strong baseline answer. The quantified detail improves credibility."
    return {"score": round(score, 2), "feedback": feedback}


def _local_chat_response(message, context_type="career_advice"):
    normalized = message.lower()
    if "salary" in normalized or "compensation" in normalized:
        return {
            "content": "For salary discussions, anchor your expectation on scope, impact, and local market demand. I can help you frame a negotiation message next.",
            "suggestions": [
                "Estimate my salary range",
                "How do I negotiate confidently?",
            ],
        }
    if "cv" in normalized or "resume" in normalized:
        return {
            "content": "Focus your CV on measurable impact, core skills, and the role you are targeting. Stronger bullets usually start with action, then outcome, then evidence.",
            "suggestions": [
                "How do I improve my CV summary?",
                "Write stronger achievement bullets",
            ],
        }
    if "interview" in normalized:
        return {
            "content": "Prepare concise answers built around context, action, and result. The clearest answers usually quantify impact and explain your decision-making.",
            "suggestions": [
                "Give me a mock interview question",
                "How should I answer behavioral questions?",
            ],
        }
    return {
        "content": (
            "I can help you structure applications, improve interview readiness, and make your profile more compelling. "
            f"Tell me what you need most for your {context_type.replace('_', ' ')} workflow."
        ),
        "suggestions": [
            "Help me tailor my application",
            "How do I stand out for this role?",
        ],
    }


def _local_cover_letter(job_title, company_name, tone="professional"):
    greeting = "Dear Hiring Team,"
    if tone == "confident":
        opening = f"I am excited to bring proven delivery discipline to the {job_title} opportunity at {company_name}."
    elif tone == "creative":
        opening = f"{company_name} is building the kind of work that makes the {job_title} role genuinely compelling to me."
    elif tone == "formal":
        opening = f"I am writing to express my interest in the {job_title} position at {company_name}."
    else:
        opening = f"I am applying for the {job_title} role at {company_name} with strong interest in contributing quickly and effectively."

    return (
        f"{greeting}\n\n"
        f"{opening} My background combines structured execution, collaborative delivery, and a strong focus on measurable impact. "
        "I am comfortable translating business goals into clear priorities, maintaining quality under pressure, and communicating effectively with cross-functional teams.\n\n"
        f"What attracts me most to {company_name} is the opportunity to contribute in a role where ownership, adaptability, and continuous improvement matter. "
        "I would welcome the opportunity to discuss how I can add value from the first weeks of collaboration.\n\n"
        "Sincerely,\n"
        "Nexora Candidate"
    )


def _local_salary_estimate(job_title, city, experience_level):
    experience_multiplier = {
        "0-2": 1.0,
        "3-5": 1.25,
        "5-8": 1.55,
        "8+": 1.85,
    }.get(experience_level, 1.2)
    base = 350000
    if "architect" in job_title.lower():
        base = 850000
    elif "engineer" in job_title.lower():
        base = 650000
    elif "designer" in job_title.lower():
        base = 450000
    elif "manager" in job_title.lower():
        base = 700000

    estimated_median = int(base * experience_multiplier)
    estimated_min = int(estimated_median * 0.82)
    estimated_max = int(estimated_median * 1.22)
    return {
        "job_title": job_title,
        "city": city,
        "experience_level": experience_level,
        "estimated_min": estimated_min,
        "estimated_median": estimated_median,
        "estimated_max": estimated_max,
        "confidence_level": 0.72,
        "data_points_used": 24,
        "explanation": (
            "This estimate is based on role seniority, demand intensity, and the market proxy available in the current environment. "
            "Use it as a negotiation anchor, not as a guaranteed offer."
        ),
    }

def generate_interview_questions_openai(job_title, job_description, interview_type, question_count=5, seniority='mid', skills=None):
    """
    Generate interview questions using GPT-4.
    """
    logger.info(f"Generating {question_count} questions for {job_title} ({seniority})")
    skills_str = ", ".join(skills) if skills else "relevant technical and soft skills"
    
    prompt = f"""
    Generate {question_count} interview questions for a {seniority} level {job_title} position.
    Job Description: {job_description}
    Interview Type: {interview_type}
    Focus Skills: {skills_str}

    Return the result ONLY as a JSON array of objects with the following keys:
    - id: unique string ID for the question (e.g., "q1", "q2")
    - question: the text of the interview question
    - type: the type of question (behavioral, technical, situational)
    - rubric: a brief guide on what a good answer should include
    """

    if not openai_client:
        logger.warning("OPENAI_API_KEY is missing, using local interview question fallback")
        return _local_question_fallback(job_title, question_count)

    response = openai_client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": "You are an expert technical interviewer. Output strictly valid JSON."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"}
    )
    
    logger.debug(f"OpenAI response received for question generation")

    try:
        content = _extract_json_content(response)
        # The prompt asks for an array, but json_object format often wraps in a root key.
        # Let's handle both or ensure we extract the list.
        if isinstance(content, dict):
             # If GPT wrapped it like {"questions": [...]}
             questions = content.get('questions', list(content.values())[0] if content else [])
        else:
             questions = content
        return questions
    except (json.JSONDecodeError, KeyError, IndexError) as e:
        logger.error(f"Error parsing OpenAI question generation response: {e}")
        return _local_question_fallback(job_title, question_count)

def grade_interview_openai(job_metadata, questions_with_answers):
    """
    Grades an interview based on questions and answers.
    questions_with_answers: list of dicts with {id, question, answer}
    """
    logger.info(f"Grading interview for {job_metadata.get('jobTitle', 'unknown role')}")
    
    prompt = f"""
    Grade the following interview for a {job_metadata.get('jobTitle', 'this')} role.
    
    Interview Session:
    {json.dumps(questions_with_answers, indent=2)}

    Provide a evaluation in JSON format with:
    - overallScore: a decimal from 0 to 10
    - hireReadiness: "not_ready", "needs_practice", "ready", or "strong_ready"
    - strengths: array of strings
    - improvements: array of strings
    - summaryToReadAloud: a 2-3 sentence summary that the AI assistant can read to the candidate.
    """

    if not openai_client:
        logger.warning("OPENAI_API_KEY is missing, using local interview grading fallback")
        return _local_grade_fallback()

    response = openai_client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": "You are a senior hiring manager. Be fair but critical. Output strictly valid JSON."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"}
    )
    
    logger.debug(f"OpenAI response received for interview grading")

    try:
        return json.loads(response.choices[0].message.content)
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing OpenAI grading response: {e}")
        return _local_grade_fallback()


def evaluate_interview_answer(job_title, question_text, answer_text, seniority='mid'):
    logger.info(f"Evaluating answer for {job_title} ({seniority})")
    prompt = f"""
    Evaluate the following interview answer for a {seniority} level {job_title} role.

    Question:
    {question_text}

    Answer:
    {answer_text}

    Return valid JSON with:
    - score: decimal from 0 to 10
    - feedback: one concise actionable paragraph
    """

    if not openai_client:
        logger.warning("OPENAI_API_KEY is missing, using local answer evaluation fallback")
        return _local_answer_evaluation(answer_text)

    response = openai_client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": "You are an interview evaluator. Output strictly valid JSON."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"}
    )

    try:
        data = json.loads(response.choices[0].message.content)
        return {
            "score": float(data.get("score", 0)),
            "feedback": str(data.get("feedback", "")).strip(),
        }
    except (json.JSONDecodeError, ValueError, TypeError) as e:
        logger.error(f"Error parsing OpenAI answer evaluation response: {e}")
        return _local_answer_evaluation(answer_text)


def generate_chat_response(message, context_type="career_advice", conversation=None):
    prompt = f"""
    You are Nexora's AI career assistant.
    Context type: {context_type}
    Conversation so far: {json.dumps(conversation or [], ensure_ascii=False)}
    Candidate message: {message}

    Return valid JSON with:
    - content: assistant reply
    - suggestions: array of 2 short follow-up suggestions
    """

    if not openai_client:
        logger.warning("OPENAI_API_KEY is missing, using local chat fallback")
        return _local_chat_response(message, context_type)

    response = openai_client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": "You are a concise, practical career assistant. Output strictly valid JSON."},
            {"role": "user", "content": prompt},
        ],
        response_format={"type": "json_object"},
    )

    try:
        data = json.loads(response.choices[0].message.content)
        return {
            "content": str(data.get("content", "")).strip(),
            "suggestions": data.get("suggestions", [])[:3],
        }
    except (json.JSONDecodeError, TypeError, ValueError) as e:
        logger.error(f"Error parsing chat response: {e}")
        return _local_chat_response(message, context_type)


def generate_cover_letter_text(job_title, company_name, tone="professional"):
    prompt = f"""
    Write a concise cover letter for the role "{job_title}" at "{company_name}".
    Tone: {tone}
    Keep it professional, concrete, and easy to personalize.
    """

    if not openai_client:
        logger.warning("OPENAI_API_KEY is missing, using local cover letter fallback")
        return _local_cover_letter(job_title, company_name, tone)

    response = openai_client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": "You write concise, credible cover letters."},
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content.strip()


def estimate_salary_range(job_title, city, experience_level):
    prompt = f"""
    Estimate a salary range for the role "{job_title}" in "{city}" for experience level "{experience_level}".
    Return valid JSON with:
    - estimated_min
    - estimated_median
    - estimated_max
    - confidence_level
    - data_points_used
    - explanation
    """

    if not openai_client:
        logger.warning("OPENAI_API_KEY is missing, using local salary fallback")
        return _local_salary_estimate(job_title, city, experience_level)

    response = openai_client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": "You estimate salaries conservatively and output strictly valid JSON."},
            {"role": "user", "content": prompt},
        ],
        response_format={"type": "json_object"},
    )
    try:
        data = json.loads(response.choices[0].message.content)
        return {
            "job_title": job_title,
            "city": city,
            "experience_level": experience_level,
            "estimated_min": int(data.get("estimated_min", 0)),
            "estimated_median": int(data.get("estimated_median", 0)),
            "estimated_max": int(data.get("estimated_max", 0)),
            "confidence_level": float(data.get("confidence_level", 0)),
            "data_points_used": int(data.get("data_points_used", 0)),
            "explanation": str(data.get("explanation", "")).strip(),
        }
    except (json.JSONDecodeError, TypeError, ValueError) as e:
        logger.error(f"Error parsing salary estimate response: {e}")
        return _local_salary_estimate(job_title, city, experience_level)
