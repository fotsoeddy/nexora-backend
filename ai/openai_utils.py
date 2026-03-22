import json
from decouple import config
from openai import OpenAI

import logging

logger = logging.getLogger(__name__)

openai_client = OpenAI(api_key=config('OPENAI_API_KEY'))

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

    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an expert technical interviewer. Output strictly valid JSON."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"}
    )
    
    logger.debug(f"OpenAI response received for question generation")

    try:
        content = json.loads(response.choices[0].message.content)
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
        return []

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

    response = openai_client.chat.completions.create(
        model="gpt-4o",
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
        return {
            "overallScore": 0,
            "hireReadiness": "not_ready",
            "strengths": [],
            "improvements": ["Failed to parse grading response"],
            "summaryToReadAloud": "I'm sorry, there was an error processing your feedback."
        }
