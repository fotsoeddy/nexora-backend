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
