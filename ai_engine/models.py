"""
AI Engine models — All AI-powered features for the Estuaire Emploi platform.

Covers: smart matching, CV analysis, interview simulation,
salary estimation, cover letter generation, natural language search,
career chatbot, and formation recommendations.

All models inherit from core.BaseModel which provides:
- id (BigAutoField)
- uuid (UUIDField, unique, indexed)
- created_at / updated_at (auto timestamps)
- is_active (soft delete flag)
"""

from __future__ import annotations

from django.conf import settings
from django.db import models

from core.models import BaseModel


# ──────────────────────────────────────────────
#  Enums / Choices
# ──────────────────────────────────────────────

class AITaskStatus(models.TextChoices):
    PENDING = "pending", "En attente"
    PROCESSING = "processing", "En cours"
    COMPLETED = "completed", "Terminé"
    FAILED = "failed", "Échoué"


class InterviewDifficulty(models.TextChoices):
    EASY = "easy", "Facile"
    MEDIUM = "medium", "Moyen"
    HARD = "hard", "Difficile"


class MessageRole(models.TextChoices):
    SYSTEM = "system", "Système"
    AI = "ai", "IA"
    USER = "user", "Utilisateur"


class RecommendationType(models.TextChoices):
    SKILL_GAP = "skill_gap", "Compétence manquante"
    CAREER_GROWTH = "career_growth", "Évolution de carrière"
    TRENDING = "trending", "Tendance du marché"


# ──────────────────────────────────────────────
#  1. Smart Matching
# ──────────────────────────────────────────────

class AIMatchScore(BaseModel):
    """
    Score de compatibilité IA entre un candidat et une offre d'emploi.
    Calculé en analysant compétences, expérience, localisation et secteur.
    """
    candidate = models.ForeignKey(
        "jobs.CandidateProfile",
        on_delete=models.CASCADE,
        related_name="ai_match_scores",
    )
    job_offer = models.ForeignKey(
        "jobs.JobOffer",
        on_delete=models.CASCADE,
        related_name="ai_match_scores",
    )
    overall_score = models.FloatField(
        help_text="Score global de matching 0-100",
    )
    skills_score = models.FloatField(
        default=0,
        help_text="Score compétences 0-100",
    )
    experience_score = models.FloatField(
        default=0,
        help_text="Score expérience 0-100",
    )
    education_score = models.FloatField(
        default=0,
        help_text="Score formation 0-100",
    )
    location_score = models.FloatField(
        default=0,
        help_text="Score localisation 0-100",
    )
    feedback = models.TextField(
        blank=True,
        help_text="Explication textuelle de l'IA sur le score",
    )
    matched_skills = models.JSONField(
        default=list, blank=True,
        help_text="Liste des compétences qui matchent",
    )
    missing_skills = models.JSONField(
        default=list, blank=True,
        help_text="Compétences manquantes chez le candidat",
    )
    strengths = models.JSONField(
        default=list, blank=True,
        help_text="Points forts du candidat pour ce poste",
    )
    weaknesses = models.JSONField(
        default=list, blank=True,
        help_text="Points à améliorer",
    )
    model_version = models.CharField(
        max_length=50, blank=True,
        help_text="Version du modèle IA utilisé",
    )
    processing_time_ms = models.PositiveIntegerField(
        blank=True, null=True,
        help_text="Temps de calcul en ms",
    )

    class Meta(BaseModel.Meta):
        unique_together = ("candidate", "job_offer")
        ordering = ["-overall_score"]
        verbose_name = "Score de matching IA"
        verbose_name_plural = "Scores de matching IA"
        indexes = [
            models.Index(fields=["candidate", "-overall_score"]),
            models.Index(fields=["job_offer", "-overall_score"]),
        ]

    def __str__(self) -> str:
        return (
            f"Match {self.overall_score:.0f}% — "
            f"{self.candidate.user.email} × {self.job_offer.title}"
        )


# ──────────────────────────────────────────────
#  2. CV Analysis
# ──────────────────────────────────────────────

class AICVAnalysis(BaseModel):
    """
    IA analysis of a CV: quality score, suggestions, keyword optimization.
    """
    cv = models.ForeignKey(
        "jobs.CV",
        on_delete=models.CASCADE,
        related_name="ai_analyses",
    )
    status = models.CharField(
        max_length=20,
        choices=AITaskStatus.choices,
        default=AITaskStatus.PENDING,
    )
    quality_score = models.FloatField(
        blank=True, null=True,
        help_text="Score qualité global 0-100",
    )
    content_score = models.FloatField(
        blank=True, null=True,
        help_text="Score du contenu (pertinence, clarté)",
    )
    structure_score = models.FloatField(
        blank=True, null=True,
        help_text="Score de la structure (organisation, sections)",
    )
    keywords_score = models.FloatField(
        blank=True, null=True,
        help_text="Score optimisation mots-clés",
    )
    suggestions = models.JSONField(
        default=list, blank=True,
        help_text='Ex: [{"section": "experience", "text": "Ajoutez des chiffres"}]',
    )
    detected_skills = models.JSONField(
        default=list, blank=True,
        help_text="Compétences détectées automatiquement dans le CV",
    )
    missing_keywords = models.JSONField(
        default=list, blank=True,
        help_text="Mots-clés importants absents du CV",
    )
    summary_generated = models.TextField(
        blank=True,
        help_text="Résumé professionnel généré par l'IA",
    )
    raw_ai_response = models.JSONField(
        default=dict, blank=True,
        help_text="Réponse brute du modèle IA (debug)",
    )
    model_version = models.CharField(max_length=50, blank=True)
    processing_time_ms = models.PositiveIntegerField(blank=True, null=True)

    class Meta(BaseModel.Meta):
        ordering = ["-created_at"]
        verbose_name = "Analyse IA de CV"
        verbose_name_plural = "Analyses IA de CV"

    def __str__(self) -> str:
        score = f"{self.quality_score:.0f}%" if self.quality_score else "en cours"
        return f"Analyse CV ({score}) — {self.cv}"


# ──────────────────────────────────────────────
#  3. Interview Simulation
# ──────────────────────────────────────────────

class AIInterviewSession(BaseModel):
    """
    Simulated interview session: the AI plays the recruiter role
    based on a specific job offer's requirements.
    """
    candidate = models.ForeignKey(
        "jobs.CandidateProfile",
        on_delete=models.CASCADE,
        related_name="interview_sessions",
    )
    job_offer = models.ForeignKey(
        "jobs.JobOffer",
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="interview_sessions",
        help_text="L'offre sur laquelle est basé l'entretien",
    )
    custom_job_title = models.CharField(
        max_length=200, blank=True,
        help_text="Titre de poste personnalisé (si pas d'offre liée)",
    )
    difficulty = models.CharField(
        max_length=10,
        choices=InterviewDifficulty.choices,
        default=InterviewDifficulty.MEDIUM,
    )
    status = models.CharField(
        max_length=20,
        choices=AITaskStatus.choices,
        default=AITaskStatus.PENDING,
    )
    overall_score = models.FloatField(
        blank=True, null=True,
        help_text="Score global d'entretien 0-100",
    )
    communication_score = models.FloatField(blank=True, null=True)
    technical_score = models.FloatField(blank=True, null=True)
    confidence_score = models.FloatField(blank=True, null=True)
    ai_feedback = models.TextField(
        blank=True,
        help_text="Feedback et conseils de l'IA après l'entretien",
    )
    strengths_noted = models.JSONField(default=list, blank=True)
    areas_to_improve = models.JSONField(default=list, blank=True)
    duration_seconds = models.PositiveIntegerField(
        blank=True, null=True,
        help_text="Durée totale de l'entretien en secondes",
    )
    questions_count = models.PositiveSmallIntegerField(default=0)
    started_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    class Meta(BaseModel.Meta):
        ordering = ["-created_at"]
        verbose_name = "Session d'entretien IA"
        verbose_name_plural = "Sessions d'entretien IA"

    def __str__(self) -> str:
        title = self.job_offer.title if self.job_offer else self.custom_job_title
        return f"Entretien: {self.candidate.user.email} — {title}"


class AIInterviewMessage(BaseModel):
    """A single question-answer exchange within an interview session."""
    session = models.ForeignKey(
        AIInterviewSession,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    role = models.CharField(max_length=10, choices=MessageRole.choices)
    content = models.TextField()
    question_number = models.PositiveSmallIntegerField(
        blank=True, null=True,
        help_text="Numéro de la question (pour les messages IA)",
    )
    answer_score = models.FloatField(
        blank=True, null=True,
        help_text="Score de la réponse du candidat 0-100",
    )
    answer_feedback = models.TextField(
        blank=True,
        help_text="Feedback spécifique pour cette réponse",
    )

    class Meta(BaseModel.Meta):
        ordering = ["created_at"]
        verbose_name = "Message d'entretien"
        verbose_name_plural = "Messages d'entretien"

    def __str__(self) -> str:
        return f"[{self.role}] Q{self.question_number or '?'} — Session {self.session_id}"


# ──────────────────────────────────────────────
#  4. Cover Letter Generator
# ──────────────────────────────────────────────

class AICoverLetter(BaseModel):
    """AI-generated cover letter tailored to a specific job offer."""
    candidate = models.ForeignKey(
        "jobs.CandidateProfile",
        on_delete=models.CASCADE,
        related_name="ai_cover_letters",
    )
    job_offer = models.ForeignKey(
        "jobs.JobOffer",
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="ai_cover_letters",
    )
    cv = models.ForeignKey(
        "jobs.CV",
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="ai_cover_letters",
        help_text="CV utilisé comme base pour la génération",
    )
    status = models.CharField(
        max_length=20,
        choices=AITaskStatus.choices,
        default=AITaskStatus.PENDING,
    )
    generated_text = models.TextField(
        blank=True,
        help_text="Lettre de motivation générée",
    )
    tone = models.CharField(
        max_length=30, default="professional",
        help_text="Ton de la lettre: professional, enthusiastic, formal",
    )
    language = models.CharField(
        max_length=10, default="fr",
        help_text="Langue de la lettre (fr, en)",
    )
    user_instructions = models.TextField(
        blank=True,
        help_text="Instructions supplémentaires du candidat",
    )
    model_version = models.CharField(max_length=50, blank=True)

    class Meta(BaseModel.Meta):
        ordering = ["-created_at"]
        verbose_name = "Lettre de motivation IA"
        verbose_name_plural = "Lettres de motivation IA"

    def __str__(self) -> str:
        offer = self.job_offer.title if self.job_offer else "Général"
        return f"Lettre: {self.candidate.user.email} → {offer}"


# ──────────────────────────────────────────────
#  5. Salary Estimation
# ──────────────────────────────────────────────

class AISalaryEstimate(BaseModel):
    """
    AI-powered salary estimation for a given job position,
    based on sector, city, experience level, and market data.
    """
    job_offer = models.ForeignKey(
        "jobs.JobOffer",
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="salary_estimates",
    )
    job_title = models.CharField(max_length=200, help_text="Titre du poste analysé")
    domain = models.ForeignKey(
        "jobs.JobDomain",
        on_delete=models.SET_NULL,
        null=True, blank=True,
    )
    city = models.CharField(max_length=120)
    experience_level = models.CharField(max_length=20, blank=True)
    estimated_min = models.PositiveIntegerField(help_text="Salaire min estimé (FCFA/mois)")
    estimated_max = models.PositiveIntegerField(help_text="Salaire max estimé (FCFA/mois)")
    estimated_median = models.PositiveIntegerField(help_text="Salaire médian estimé (FCFA/mois)")
    confidence_level = models.FloatField(
        default=0.5,
        help_text="Niveau de confiance de l'estimation 0.0-1.0",
    )
    data_points_used = models.PositiveIntegerField(
        default=0,
        help_text="Nombre de données utilisées pour l'estimation",
    )
    explanation = models.TextField(blank=True)
    model_version = models.CharField(max_length=50, blank=True)

    class Meta(BaseModel.Meta):
        ordering = ["-created_at"]
        verbose_name = "Estimation salariale IA"
        verbose_name_plural = "Estimations salariales IA"

    def __str__(self) -> str:
        return f"Salaire: {self.job_title} @ {self.city} — {self.estimated_median} FCFA"


# ──────────────────────────────────────────────
#  6. Natural Language Search
# ──────────────────────────────────────────────

class AISearchQuery(BaseModel):
    """
    Stores natural language search queries and the AI's parsed interpretation.
    e.g. "Trouve-moi un stage marketing à Douala payé +50000"
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ai_search_queries",
    )
    raw_query = models.TextField(help_text="Requête en langage naturel")
    parsed_filters = models.JSONField(
        default=dict, blank=True,
        help_text='Filtres extraits: {"domain": "marketing", "city": "Douala", "min_salary": 50000, "contract": "STAGE"}',
    )
    results_count = models.PositiveIntegerField(default=0)
    results_job_ids = models.JSONField(
        default=list, blank=True,
        help_text="IDs des offres retournées",
    )
    response_time_ms = models.PositiveIntegerField(blank=True, null=True)
    was_helpful = models.BooleanField(
        blank=True, null=True,
        help_text="Feedback utilisateur sur la pertinence",
    )

    class Meta(BaseModel.Meta):
        ordering = ["-created_at"]
        verbose_name = "Recherche IA"
        verbose_name_plural = "Recherches IA"

    def __str__(self) -> str:
        return f"Search: \"{self.raw_query[:60]}\" — {self.results_count} résultats"


# ──────────────────────────────────────────────
#  7. Career Chatbot
# ──────────────────────────────────────────────

class AIChatSession(BaseModel):
    """A career chatbot conversation session."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ai_chat_sessions",
    )
    title = models.CharField(
        max_length=200, blank=True,
        help_text="Titre auto-généré de la conversation",
    )
    context_type = models.CharField(
        max_length=30, blank=True,
        help_text="Contexte: job_search, cv_help, career_advice, interview_prep",
    )
    messages_count = models.PositiveIntegerField(default=0)

    class Meta(BaseModel.Meta):
        ordering = ["-updated_at"]
        verbose_name = "Session chatbot IA"
        verbose_name_plural = "Sessions chatbot IA"

    def __str__(self) -> str:
        return f"Chat: {self.title or 'Sans titre'} — {self.user.email}"


class AIChatMessage(BaseModel):
    """A single message in a chatbot session."""
    session = models.ForeignKey(
        AIChatSession,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    role = models.CharField(max_length=10, choices=MessageRole.choices)
    content = models.TextField()
    metadata = models.JSONField(
        default=dict, blank=True,
        help_text="Données structurées (liens, offres suggérées, etc.)",
    )
    tokens_used = models.PositiveIntegerField(
        blank=True, null=True,
        help_text="Tokens consommés pour cette réponse",
    )

    class Meta(BaseModel.Meta):
        ordering = ["created_at"]
        verbose_name = "Message chatbot"
        verbose_name_plural = "Messages chatbot"

    def __str__(self) -> str:
        return f"[{self.role}] {self.content[:80]}"


# ──────────────────────────────────────────────
#  8. Formation Recommendations
# ──────────────────────────────────────────────

class AIFormationRecommendation(BaseModel):
    """
    AI-recommended training/formation based on skill gaps
    between a candidate and their target job market.
    """
    candidate = models.ForeignKey(
        "jobs.CandidateProfile",
        on_delete=models.CASCADE,
        related_name="formation_recommendations",
    )
    recommendation_type = models.CharField(
        max_length=20,
        choices=RecommendationType.choices,
        default=RecommendationType.SKILL_GAP,
    )
    skill_name = models.CharField(
        max_length=120,
        help_text="Compétence à développer",
    )
    formation_title = models.CharField(
        max_length=255,
        help_text="Titre de la formation recommandée",
    )
    formation_url = models.URLField(
        blank=True,
        help_text="Lien vers la formation (ex: INSAM, insamtechs.com)",
    )
    provider = models.CharField(
        max_length=120, blank=True,
        help_text="Ex: INSAM, Coursera, Udemy",
    )
    priority = models.PositiveSmallIntegerField(
        default=5,
        help_text="Priorité 1 (haute) à 10 (basse)",
    )
    reasoning = models.TextField(
        blank=True,
        help_text="Pourquoi cette formation est recommandée",
    )
    related_job_offers = models.ManyToManyField(
        "jobs.JobOffer", blank=True,
        related_name="formation_recommendations",
        help_text="Offres qui nécessitent cette compétence",
    )
    is_dismissed = models.BooleanField(default=False, help_text="Rejetée par l'utilisateur")

    class Meta(BaseModel.Meta):
        ordering = ["priority", "-created_at"]
        verbose_name = "Recommandation de formation IA"
        verbose_name_plural = "Recommandations de formation IA"

    def __str__(self) -> str:
        return f"Reco: {self.skill_name} → {self.formation_title}"


# ──────────────────────────────────────────────
#  9. AI Usage Tracking
# ──────────────────────────────────────────────

class AIUsageLog(BaseModel):
    """
    Tracks all AI feature usage for analytics, billing and rate limiting.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ai_usage_logs",
    )
    feature = models.CharField(
        max_length=40,
        help_text="matching, cv_analysis, interview, cover_letter, salary, search, chat",
    )
    status = models.CharField(
        max_length=20,
        choices=AITaskStatus.choices,
        default=AITaskStatus.COMPLETED,
    )
    tokens_input = models.PositiveIntegerField(default=0)
    tokens_output = models.PositiveIntegerField(default=0)
    cost_estimate = models.FloatField(
        default=0,
        help_text="Coût estimé de la requête (en unités internes)",
    )
    processing_time_ms = models.PositiveIntegerField(blank=True, null=True)
    model_name = models.CharField(max_length=60, blank=True, help_text="Ex: gpt-4, gemini-pro")
    error_message = models.TextField(blank=True)
    request_metadata = models.JSONField(default=dict, blank=True)

    class Meta(BaseModel.Meta):
        ordering = ["-created_at"]
        verbose_name = "Log d'utilisation IA"
        verbose_name_plural = "Logs d'utilisation IA"
        indexes = [
            models.Index(fields=["user", "feature", "-created_at"]),
            models.Index(fields=["feature", "-created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.feature} — {self.user.email} ({self.status})"
