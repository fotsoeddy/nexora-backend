import json
from decouple import config
from openai import OpenAI

import logging

logger = logging.getLogger(__name__)

_missing_openai_key_logged = False


def _resolve_openai_runtime():
    global _missing_openai_key_logged

    openai_api_key = config('OPENAI_API_KEY', default='').strip() or config('AI_API_KEY', default='').strip()
    openai_model = config('OPENAI_MODEL', default='').strip() or config('AI_CHAT_MODEL', default='').strip() or 'gpt-4o-mini'
    openai_base_url = config('OPENAI_BASE_URL', default='').strip() or config('AI_API_BASE_URL', default='').strip()

    if not openai_api_key:
        if not _missing_openai_key_logged:
            logger.warning(
                "OpenAI API key is missing. Set OPENAI_API_KEY (or AI_API_KEY) to enable real AI responses."
            )
            _missing_openai_key_logged = True
        return None, openai_model

    client_kwargs = {'api_key': openai_api_key}
    if openai_base_url:
        client_kwargs['base_url'] = openai_base_url.rstrip('/')

    return OpenAI(**client_kwargs), openai_model


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
    Generate interview questions using GPT-4o.
    """
    logger.info(f"Generating {question_count} questions for {job_title} ({seniority})")
    skills_str = ", ".join(skills) if skills else "relevant technical and soft skills"
    
    prompt = f"""
    You are an expert technical recruiter and hiring manager.
    Generate {question_count} high-quality interview questions for a {seniority} level {job_title} position.
    
    Job Description context:
    {job_description}
    
    Interview Type: {interview_type}
    Focus Skills: {skills_str}

    Instructions:
    1. Create a mix of technical competency and behavioral questions.
    2. For {seniority} level, ensure the depth of the questions is appropriate.
    3. Include a 'rubric' for each question that defines what a stellar answer looks like.

    Return the result ONLY as a JSON object with a 'questions' key containing an array of objects:
    - id: unique string ID (e.g., "q1", "q2")
    - question: the text of the interview question
    - type: the type (behavioral, technical, situational)
    - rubric: a detailed guide on what a good answer should include (e.g., mention specific technologies, use STAR method)
    """

    openai_client, openai_model = _resolve_openai_runtime()
    if not openai_client:
        logger.warning("OPENAI_API_KEY is missing, using local interview question fallback")
        return _local_question_fallback(job_title, question_count)

    response = openai_client.chat.completions.create(
        model=openai_model,
        messages=[
            {"role": "system", "content": "You are a world-class HR technology assistant. You output strictly valid JSON."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"}
    )
    
    try:
        content = _extract_json_content(response)
        if isinstance(content, dict):
             questions = content.get('questions', list(content.values())[0] if content else [])
        else:
             questions = content
        return questions
    except (json.JSONDecodeError, KeyError, IndexError) as e:
        logger.error(f"Error parsing OpenAI question generation response: {e}")
        return _local_question_fallback(job_title, question_count)

def grade_interview_openai(job_metadata, questions_with_answers):
    """
    Grades an interview based on questions and answers using GPT-4o.
    """
    logger.info(f"Grading interview for {job_metadata.get('jobTitle', 'unknown role')}")
    
    prompt = f"""
    You are a Senior Hiring Manager evaluating a candidate for a {job_metadata.get('jobTitle', 'this')} role.
    
    Interview Transcript:
    {json.dumps(questions_with_answers, indent=2)}

    Your task:
    1. Evaluate each answer for depth, correctness, and professional naming conventions.
    2. Provide an overall score and a readiness assessment.
    3. Identify 3 specific strengths and 3 actionable areas for improvement.

    Return the result ONLY as a JSON object with:
    - overallScore: decimal from 0 to 10.0
    - hireReadiness: "not_ready", "needs_practice", "ready", or "strong_ready"
    - strengths: array of 3 specific positive traits or answers
    - improvements: array of 3 specific, actionable steps the candidate should take
    - summaryToReadAloud: a warm, professional 3-sentence summary the AI assistant will read back to the candidate.
    """

    openai_client, openai_model = _resolve_openai_runtime()
    if not openai_client:
        logger.warning("OPENAI_API_KEY is missing, using local interview grading fallback")
        return _local_grade_fallback()

    response = openai_client.chat.completions.create(
        model=openai_model,
        messages=[
            {"role": "system", "content": "You are a critical but constructive hiring expert. Output strictly valid JSON."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"}
    )
    
    try:
        return json.loads(response.choices[0].message.content)
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing OpenAI grading response: {e}")
        return _local_grade_fallback()


def evaluate_interview_answer(job_title, question_text, answer_text, seniority='mid'):
    """
    Evaluate a single interview answer immediately.
    """
    logger.info(f"Evaluating individual answer for {job_title} ({seniority})")
    prompt = f"""
    Evaluate this specific interview answer for a {seniority} level {job_title} role.

    Question: {question_text}
    Answer: {answer_text}

    Task:
    - Rate the answer quality based on relevance, clarity, and use of specific examples.
    - Provide constructive, immediate feedback.

    Return valid JSON with:
    - score: decimal from 0 to 10.0
    - feedback: one concise, high-impact paragraph of advice
    """

    openai_client, openai_model = _resolve_openai_runtime()
    if not openai_client:
        logger.warning("OPENAI_API_KEY is missing, using local answer evaluation fallback")
        return _local_answer_evaluation(answer_text)

    response = openai_client.chat.completions.create(
        model=openai_model,
        messages=[
            {"role": "system", "content": "You are an AI Interview Coach. Give sharp, actionable feedback. Output strictly valid JSON."},
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
    """
    Generate a conversational response from the Career Assistant.
    """
    prompt = f"""
    You are Nexora's Premium AI Career Strategist.
    Current context: {context_type}
    Recent chat history: {json.dumps(conversation or [], ensure_ascii=False)}
    User input: {message}

    Guidelines:
    - Be professional, encouraging, and data-driven.
    - Keep responses under 3 sentences unless complex.
    - Always provide 2 relevant follow-up suggestions.

    Return valid JSON with:
    - content: Your tactical response
    - suggestions: array of 2 short follow-up buttons (e.g., "Analyze my resume", "Mock interview")
    """

    openai_client, openai_model = _resolve_openai_runtime()
    if not openai_client:
        logger.warning("OPENAI_API_KEY is missing, using local chat fallback")
        return _local_chat_response(message, context_type)

    response = openai_client.chat.completions.create(
        model=openai_model,
        messages=[
            {"role": "system", "content": "You are a career growth expert. You empower users with clear, actionable advice. Output strictly valid JSON."},
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
    """
    Generate a tailored cover letter.
    """
    prompt = f"""
    Write a high-conversion, professional cover letter for a {job_title} position at {company_name}.
    Desired Tone: {tone}
    
    Requirements:
    - Start with a compelling hook.
    - Highlight adaptability and value-add.
    - Use placeholders like [Specific Achievement] for the user to fill in.
    - Keep it under 300 words.
    """

    openai_client, openai_model = _resolve_openai_runtime()
    if not openai_client:
        logger.warning("OPENAI_API_KEY is missing, using local cover letter fallback")
        return _local_cover_letter(job_title, company_name, tone)

    response = openai_client.chat.completions.create(
        model=openai_model,
        messages=[
            {"role": "system", "content": "You are a professional copywriter specializing in career applications."},
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content.strip()


def estimate_salary_range(job_title, city, experience_level):
    """
    Estimate global or regional salary ranges.
    """
    prompt = f"""
    As a compensation analyst, estimate the current market salary range for:
    Role: {job_title}
    Location: {city}
    Experience: {experience_level}

    Return valid JSON with:
    - estimated_min: integer
    - estimated_median: integer
    - estimated_max: integer
    - confidence_level: float 0.0-1.0
    - data_points_used: integer
    - explanation: short summary of market drivers (e.g., remote work influence, tech stack demand)
    """

    openai_client, openai_model = _resolve_openai_runtime()
    if not openai_client:
        logger.warning("OPENAI_API_KEY is missing, using local salary fallback")
        return _local_salary_estimate(job_title, city, experience_level)

    response = openai_client.chat.completions.create(
        model=openai_model,
        messages=[
            {"role": "system", "content": "You provide conservative, realistic salary insights. Output strictly valid JSON."},
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

def scan_cv_openai(cv_text):
    """
    Comprehensive CV/Resume analysis.
    """
    logger.info("Performing enhanced CV scan")
    
    prompt = f"""
    You are an AI Talent Auditor. Analyze this resume text with extreme precision.
    
    Resume Content:
    {cv_text}
    
    Evaluation Criteria:
    1. Impact: Are achievements quantified (e.g., increased revenue by 20%)?
    2. Readability: Is the structure logical and professional?
    3. Keywords: Are industry-standard skills present?
    4. Red Flags: Gaps, spelling errors, or poor formatting.

    Return the result ONLY as a JSON object with:
    - score: Integer 0-100
    - summary: A high-level overview of the professional profile.
    - strengths: Array of 3 key competitive advantages.
    - improvements: Array of 3 actionable items to increase the score.
    - errors: Array of errors (typos, contact info missing, missing dates).
    - details: A deep-dive analysis of why the score was given.
    """

    openai_client, openai_model = _resolve_openai_runtime()
    if not openai_client:
        logger.warning("OPENAI_API_KEY is missing, returning mock scanning result")
        return {
            "score": 75,
            "summary": "Solid CV with good professional experience. Needs better formatting in some areas.",
            "strengths": ["Clear experience history", "Relevant skill set"],
            "improvements": ["Quantify achievements", "Add a stronger summary section"],
            "errors": ["Some date inconsistencies found"],
            "details": "The CV is well-structured but could benefit from more specific metrics and a clearer summary."
        }

    response = openai_client.chat.completions.create(
        model=openai_model,
        messages=[
            {"role": "system", "content": "You are an expert ATS (Applicant Tracking System) auditor. Output strictly valid JSON."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"}
    )
    
    logger.debug(f"OpenAI CV Scan Raw Response: {response.choices[0].message.content}")
    
    try:
        return json.loads(response.choices[0].message.content)
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing OpenAI CV scanning response: {e}")
        return {
            "score": 0,
            "summary": "Error analyzing CV",
            "strengths": [],
            "improvements": [],
            "errors": ["Failed to parse AI response"],
            "details": "There was an error processing the CV analysis."
        }

def match_cv_to_job_openai(cv_text, job_title, job_description):
    """
    Match a Resume against a specific Job Description.
    """
    logger.info(f"Performing deep Job-Resume match for: {job_title}")
    
    prompt = f"""
    You are an expert Technical Recruiter. Match this candidate's Resume against the specified Job Description.
    
    Job Context:
    Title: {job_title}
    Description: {job_description}
    
    Candidate Resume:
    {cv_text}
    
    Evaluation Task:
    1. Calculate a match percentage based on skills, experience years, and seniority.
    2. Identify specific 'missing' keywords that are in the JD but missing from the Resume.
    3. Highlight direct evidence from the Resume that proves suitability for the role.

    Return the result ONLY as a JSON object with:
    - match_score: Integer 0-100
    - fit_analysis: A brief executive summary of candidate-job alignment.
    - missing_skills: Array of essential requirements from the JD not found in the resume.
    - relevant_experience: Array of specific past roles/projects that align with this JD.
    - improvements: How to rewrite or re-order the resume to pass the ATS for THIS specific job.
    - result_detail: Detailed justification of the match percentage.
    """

    openai_client, openai_model = _resolve_openai_runtime()
    if not openai_client:
        logger.warning("OPENAI_API_KEY is missing, returning mock matching result")
        return {
            "match_score": 82,
            "fit_analysis": "Good match for the role's core requirements.",
            "missing_skills": ["Experience with specific tool X", "Certification Y"],
            "relevant_experience": ["3 years in similar role", "Background in relevant industry"],
            "improvements": ["Highlight experience with Z more prominently"],
            "result_detail": "The candidate has most of the required background, but lacks some specific certifications."
        }

    response = openai_client.chat.completions.create(
        model=openai_model,
        messages=[
            {"role": "system", "content": "You are a specialized Recruitment Intelligence bot. Output strictly valid JSON."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"}
    )
    
    try:
        return json.loads(response.choices[0].message.content)
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing OpenAI Job Match response: {e}")
        return {
            "match_score": 0,
            "fit_analysis": "Error analyzing match",
            "missing_skills": [],
            "relevant_experience": [],
            "improvements": [],
            "result_detail": "There was an error processing the job match analysis."
        }
