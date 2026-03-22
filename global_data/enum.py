from django.db import models

class EmploymentType(models.TextChoices):
    FULL_TIME = "full_time", "Full Time"
    PART_TIME = "part_time", "Part Time"
    CONTRACT = "contract", "Contract"
    INTERNSHIP = "internship", "Internship"

class AssistantType(models.TextChoices):
    JOB_INTERVIEWER = "job_interviewer", "Job Interviewer"
    SETUP_INTERVIEWER = "setup_interviewer", "Setup Interviewer"

class SessionType(models.TextChoices):
    JOB_BASED = "job_based", "Job Based"
    GENERAL_SETUP = "general_setup", "General Setup"

class InterviewType(models.TextChoices):
    TECHNICAL = "technical", "Technical"
    BEHAVIORAL = "behavioral", "Behavioral"
    MIXED = "mixed", "Mixed"

class InterviewStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    COLLECTING_PREFERENCES = "collecting_preferences", "Collecting Preferences"
    QUESTIONS_GENERATED = "questions_generated", "Questions Generated"
    IN_PROGRESS = "in_progress", "In Progress"
    COMPLETED = "completed", "Completed"
    GRADED = "graded", "Graded"
    FAILED = "failed", "Failed"

class QuestionType(models.TextChoices):
    TECHNICAL = "technical", "Technical"
    BEHAVIORAL = "behavioral", "Behavioral"
    SITUATIONAL = "situational", "Situational"
    MIXED = "mixed", "Mixed"

class HireReadiness(models.TextChoices):
    NOT_READY = "not_ready", "Not Ready"
    NEEDS_PRACTICE = "needs_practice", "Needs Practice"
    READY = "ready", "Ready"
    STRONG_READY = "strong_ready", "Strong Ready"
