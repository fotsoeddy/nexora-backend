"""
Jobs app models — Core data for the Estuaire Emploi AI platform.

Covers: profiles (candidate & company), job domains, job offers,
CVs (with experience, education, skills), applications, pricing plans
and subscriptions.

All models inherit from core.BaseModel which provides:
- id (BigAutoField)
- uuid (UUIDField, unique, indexed)
- created_at / updated_at (auto timestamps)
- is_active (soft delete flag)
"""

from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils import timezone

from core.models import BaseModel


# ──────────────────────────────────────────────
#  Enums / Choices
# ──────────────────────────────────────────────

class UserRole(models.TextChoices):
    CANDIDATE = "candidate", "Chercheur d'emploi"
    EMPLOYER = "employer", "Entreprise"
    ADMIN = "admin", "Administrateur"


class ContractType(models.TextChoices):
    CDI = "CDI", "CDI"
    CDD = "CDD", "CDD"
    STAGE = "STAGE", "Stage"
    FREELANCE = "FREELANCE", "Freelance"
    INTERIM = "INTERIM", "Intérim"
    ALTERNANCE = "ALTERNANCE", "Alternance"
    BENEVOLAT = "BENEVOLAT", "Bénévolat"


class ExperienceLevel(models.TextChoices):
    JUNIOR = "junior", "Junior (0-2 ans)"
    MID = "mid", "Intermédiaire (2-5 ans)"
    SENIOR = "senior", "Senior (5-10 ans)"
    EXPERT = "expert", "Expert (10+ ans)"


class ApplicationStatus(models.TextChoices):
    PENDING = "pending", "En attente"
    REVIEWED = "reviewed", "Consultée"
    SHORTLISTED = "shortlisted", "Présélectionné"
    INTERVIEW = "interview", "Entretien planifié"
    ACCEPTED = "accepted", "Acceptée"
    REJECTED = "rejected", "Refusée"
    WITHDRAWN = "withdrawn", "Retirée"


class SkillLevel(models.TextChoices):
    BEGINNER = "beginner", "Débutant"
    INTERMEDIATE = "intermediate", "Intermédiaire"
    ADVANCED = "advanced", "Avancé"
    EXPERT = "expert", "Expert"


class EducationLevel(models.TextChoices):
    BEPC = "bepc", "BEPC"
    BAC = "bac", "Baccalauréat"
    BTS = "bts", "BTS / DUT"
    LICENCE = "licence", "Licence (Bac+3)"
    MASTER = "master", "Master (Bac+5)"
    DOCTORAT = "doctorat", "Doctorat"
    AUTRE = "autre", "Autre"


class PlanTarget(models.TextChoices):
    CANDIDATE = "candidate", "Chercheur d'emploi"
    EMPLOYER = "employer", "Entreprise"


class SubscriptionStatus(models.TextChoices):
    ACTIVE = "active", "Actif"
    EXPIRED = "expired", "Expiré"
    CANCELLED = "cancelled", "Annulé"


class JobOfferStatus(models.TextChoices):
    DRAFT = "draft", "Brouillon"
    ACTIVE = "active", "Active"
    CLOSED = "closed", "Clôturée"
    EXPIRED = "expired", "Expirée"


# ──────────────────────────────────────────────
#  Profiles
# ──────────────────────────────────────────────

class CandidateProfile(BaseModel):
    """Extended profile for job seekers."""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="candidate_profile",
    )
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.CANDIDATE,
    )
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(
        max_length=10,
        choices=[("M", "Homme"), ("F", "Femme"), ("O", "Autre")],
        blank=True,
    )
    city = models.CharField(max_length=120, blank=True)
    country = models.CharField(max_length=80, default="Cameroun")
    address = models.CharField(max_length=255, blank=True)
    bio = models.TextField(blank=True, help_text="Résumé professionnel court")
    photo = models.ImageField(upload_to="candidates/photos/", blank=True, null=True)
    linkedin_url = models.URLField(blank=True)
    portfolio_url = models.URLField(blank=True)
    experience_level = models.CharField(
        max_length=20,
        choices=ExperienceLevel.choices,
        default=ExperienceLevel.JUNIOR,
    )
    desired_salary_min = models.PositiveIntegerField(
        blank=True, null=True,
        help_text="Salaire minimum souhaité (FCFA)",
    )
    desired_salary_max = models.PositiveIntegerField(
        blank=True, null=True,
        help_text="Salaire maximum souhaité (FCFA)",
    )
    is_available = models.BooleanField(default=True, help_text="Disponible pour emploi")
    desired_contract_types = models.JSONField(
        default=list, blank=True,
        help_text='Ex: ["CDI", "CDD", "STAGE"]',
    )
    desired_domains = models.ManyToManyField(
        "JobDomain", blank=True, related_name="interested_candidates",
    )

    class Meta(BaseModel.Meta):
        verbose_name = "Profil candidat"
        verbose_name_plural = "Profils candidats"

    def __str__(self) -> str:
        return f"Candidate: {self.user.email}"


class CompanyProfile(BaseModel):
    """Profile for employers / companies."""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="company_profile",
    )
    company_name = models.CharField(max_length=255)
    industry = models.CharField(max_length=120, blank=True)
    description = models.TextField(blank=True)
    website = models.URLField(blank=True)
    logo = models.ImageField(upload_to="companies/logos/", blank=True, null=True)
    city = models.CharField(max_length=120, blank=True)
    country = models.CharField(max_length=80, default="Cameroun")
    address = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=32, blank=True)
    employee_count = models.PositiveIntegerField(
        blank=True, null=True,
        help_text="Nombre approximatif d'employés",
    )
    founded_year = models.PositiveSmallIntegerField(blank=True, null=True)
    is_verified = models.BooleanField(
        default=False,
        help_text="Entreprise vérifiée par l'admin",
    )

    class Meta(BaseModel.Meta):
        verbose_name = "Profil entreprise"
        verbose_name_plural = "Profils entreprises"

    def __str__(self) -> str:
        return self.company_name


# ──────────────────────────────────────────────
#  Job domains & offers
# ──────────────────────────────────────────────

class JobDomain(BaseModel):
    """Industry sector / job domain (e.g. Marketing, IT, Finance)."""
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True)
    icon = models.CharField(max_length=60, blank=True, help_text="Nom d'icône (ex: briefcase)")
    description = models.TextField(blank=True)

    class Meta(BaseModel.Meta):
        ordering = ["name"]
        verbose_name = "Domaine d'emploi"
        verbose_name_plural = "Domaines d'emploi"

    def __str__(self) -> str:
        return self.name


class JobOffer(BaseModel):
    """A job posting published by a company."""
    company = models.ForeignKey(
        CompanyProfile,
        on_delete=models.CASCADE,
        related_name="job_offers",
    )
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=280, unique=True)
    domain = models.ForeignKey(
        JobDomain,
        on_delete=models.SET_NULL,
        null=True,
        related_name="job_offers",
    )
    description = models.TextField()
    responsibilities = models.TextField(blank=True, help_text="Missions principales")
    requirements = models.TextField(blank=True, help_text="Profil recherché")
    contract_type = models.CharField(
        max_length=20,
        choices=ContractType.choices,
        default=ContractType.CDI,
    )
    experience_level = models.CharField(
        max_length=20,
        choices=ExperienceLevel.choices,
        default=ExperienceLevel.JUNIOR,
    )
    education_level = models.CharField(
        max_length=20,
        choices=EducationLevel.choices,
        blank=True,
    )
    salary_min = models.PositiveIntegerField(
        blank=True, null=True,
        help_text="Salaire minimum (FCFA/mois)",
    )
    salary_max = models.PositiveIntegerField(
        blank=True, null=True,
        help_text="Salaire maximum (FCFA/mois)",
    )
    is_salary_visible = models.BooleanField(default=True)
    city = models.CharField(max_length=120)
    country = models.CharField(max_length=80, default="Cameroun")
    is_remote = models.BooleanField(default=False)
    application_deadline = models.DateField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=JobOfferStatus.choices,
        default=JobOfferStatus.ACTIVE,
    )
    required_skills = models.ManyToManyField(
        "Skill", blank=True, related_name="required_by_offers",
    )
    views_count = models.PositiveIntegerField(default=0)
    applications_count = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False, help_text="Mise en avant")
    external_apply_url = models.URLField(
        blank=True,
        help_text="Lien externe de candidature (si applicable)",
    )

    class Meta(BaseModel.Meta):
        ordering = ["-created_at"]
        verbose_name = "Offre d'emploi"
        verbose_name_plural = "Offres d'emploi"
        indexes = [
            models.Index(fields=["status", "-created_at"]),
            models.Index(fields=["domain", "status"]),
            models.Index(fields=["city"]),
        ]

    def __str__(self) -> str:
        return f"{self.title} — {self.company.company_name}"

    @property
    def is_expired(self) -> bool:
        if self.application_deadline:
            return self.application_deadline < timezone.now().date()
        return False


# ──────────────────────────────────────────────
#  Skills
# ──────────────────────────────────────────────

class Skill(BaseModel):
    """Reusable skill definition (e.g. Python, Excel, Gestion de projet)."""
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True)
    domain = models.ForeignKey(
        JobDomain,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="skills",
    )

    class Meta(BaseModel.Meta):
        ordering = ["name"]
        verbose_name = "Compétence"
        verbose_name_plural = "Compétences"

    def __str__(self) -> str:
        return self.name


# ──────────────────────────────────────────────
#  CV (Resume)
# ──────────────────────────────────────────────

class CV(BaseModel):
    """A candidate's resume / CV document."""
    candidate = models.ForeignKey(
        CandidateProfile,
        on_delete=models.CASCADE,
        related_name="cvs",
    )
    title = models.CharField(
        max_length=200,
        default="Mon CV",
        help_text="Ex: CV Marketing Digital, CV Stage Ingénieur",
    )
    summary = models.TextField(blank=True, help_text="Résumé professionnel")
    is_primary = models.BooleanField(
        default=False,
        help_text="CV principal visible dans la CVthèque",
    )
    is_public = models.BooleanField(
        default=True,
        help_text="Visible par les recruteurs",
    )
    languages = models.JSONField(
        default=list, blank=True,
        help_text='Ex: [{"lang": "Français", "level": "Natif"}, {"lang": "Anglais", "level": "Intermédiaire"}]',
    )
    hobbies = models.TextField(blank=True)
    pdf_file = models.FileField(
        upload_to="cvs/pdf/",
        blank=True, null=True,
        help_text="CV uploadé en PDF",
    )
    template_name = models.CharField(
        max_length=50,
        default="classic",
        help_text="Modèle de design du CV généré",
    )
    ai_quality_score = models.FloatField(
        blank=True, null=True,
        help_text="Score qualité 0-100 attribué par l'IA",
    )

    class Meta(BaseModel.Meta):
        ordering = ["-is_primary", "-updated_at"]
        verbose_name = "CV"
        verbose_name_plural = "CVs"

    def __str__(self) -> str:
        return f"{self.title} — {self.candidate.user.email}"


class Experience(BaseModel):
    """Work experience entry in a CV."""
    cv = models.ForeignKey(CV, on_delete=models.CASCADE, related_name="experiences")
    job_title = models.CharField(max_length=200)
    company_name = models.CharField(max_length=200)
    city = models.CharField(max_length=120, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True, help_text="Vide = poste actuel")
    is_current = models.BooleanField(default=False)
    description = models.TextField(blank=True, help_text="Missions et réalisations")

    class Meta(BaseModel.Meta):
        ordering = ["-start_date"]
        verbose_name = "Expérience professionnelle"
        verbose_name_plural = "Expériences professionnelles"

    def __str__(self) -> str:
        return f"{self.job_title} @ {self.company_name}"


class Education(BaseModel):
    """Education entry in a CV."""
    cv = models.ForeignKey(CV, on_delete=models.CASCADE, related_name="educations")
    institution = models.CharField(max_length=255)
    degree = models.CharField(max_length=200, help_text="Intitulé du diplôme")
    level = models.CharField(
        max_length=20,
        choices=EducationLevel.choices,
        blank=True,
    )
    field_of_study = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=120, blank=True)
    start_year = models.PositiveSmallIntegerField()
    end_year = models.PositiveSmallIntegerField(blank=True, null=True)
    description = models.TextField(blank=True)

    class Meta(BaseModel.Meta):
        ordering = ["-start_year"]
        verbose_name = "Formation"
        verbose_name_plural = "Formations"

    def __str__(self) -> str:
        return f"{self.degree} — {self.institution}"


class CVSkill(BaseModel):
    """Link between a CV and a Skill with a mastery level."""
    cv = models.ForeignKey(CV, on_delete=models.CASCADE, related_name="cv_skills")
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name="cv_entries")
    level = models.CharField(
        max_length=20,
        choices=SkillLevel.choices,
        default=SkillLevel.INTERMEDIATE,
    )
    years_of_experience = models.PositiveSmallIntegerField(
        blank=True, null=True,
        help_text="Années d'expérience avec cette compétence",
    )

    class Meta(BaseModel.Meta):
        unique_together = ("cv", "skill")
        verbose_name = "Compétence CV"
        verbose_name_plural = "Compétences CV"

    def __str__(self) -> str:
        return f"{self.skill.name} ({self.get_level_display()}) — {self.cv}"


# ──────────────────────────────────────────────
#  Applications
# ──────────────────────────────────────────────

class Application(BaseModel):
    """A candidate's application to a job offer."""
    candidate = models.ForeignKey(
        CandidateProfile,
        on_delete=models.CASCADE,
        related_name="applications",
    )
    job_offer = models.ForeignKey(
        JobOffer,
        on_delete=models.CASCADE,
        related_name="applications",
    )
    cv = models.ForeignKey(
        CV,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="applications",
    )
    cover_letter = models.TextField(blank=True, help_text="Lettre de motivation")
    ai_generated_cover_letter = models.TextField(
        blank=True,
        help_text="Lettre de motivation générée par l'IA",
    )
    status = models.CharField(
        max_length=20,
        choices=ApplicationStatus.choices,
        default=ApplicationStatus.PENDING,
    )
    recruiter_notes = models.TextField(blank=True, help_text="Notes internes du recruteur")
    ai_match_score = models.FloatField(
        blank=True, null=True,
        help_text="Score de matching IA 0-100 au moment de la candidature",
    )
    applied_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(blank=True, null=True)

    class Meta(BaseModel.Meta):
        unique_together = ("candidate", "job_offer")
        ordering = ["-applied_at"]
        verbose_name = "Candidature"
        verbose_name_plural = "Candidatures"
        indexes = [
            models.Index(fields=["status", "-applied_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.candidate.user.email} → {self.job_offer.title}"


# ──────────────────────────────────────────────
#  Pricing & Subscriptions
# ──────────────────────────────────────────────

class PricingPlan(BaseModel):
    """Subscription plan (Silver, Gold, Platinum) for candidates or employers."""
    name = models.CharField(max_length=60, help_text="Ex: Silver, Gold, Platinum")
    slug = models.SlugField(max_length=80, unique=True)
    target = models.CharField(
        max_length=20,
        choices=PlanTarget.choices,
    )
    price = models.PositiveIntegerField(help_text="Prix en FCFA")
    duration_days = models.PositiveIntegerField(default=30, help_text="Durée en jours")
    features = models.JSONField(
        default=list,
        help_text='Ex: ["Conception CV gratuite", "Accès CVthèque", "Visibilité premium"]',
    )
    max_job_posts = models.PositiveIntegerField(
        blank=True, null=True,
        help_text="Nombre max d'offres publiables (entreprises uniquement)",
    )
    has_cv_builder = models.BooleanField(default=False)
    has_cvtheque_access = models.BooleanField(default=False)
    has_ai_features = models.BooleanField(
        default=False,
        help_text="Accès aux fonctionnalités IA (matching, analyse CV, etc.)",
    )
    is_featured = models.BooleanField(default=False, help_text="Mise en avant")
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta(BaseModel.Meta):
        ordering = ["target", "sort_order", "price"]
        verbose_name = "Plan tarifaire"
        verbose_name_plural = "Plans tarifaires"

    def __str__(self) -> str:
        return f"{self.name} ({self.get_target_display()}) — {self.price} FCFA"


class Subscription(BaseModel):
    """A user's active subscription to a pricing plan."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="subscriptions",
    )
    plan = models.ForeignKey(
        PricingPlan,
        on_delete=models.PROTECT,
        related_name="subscriptions",
    )
    status = models.CharField(
        max_length=20,
        choices=SubscriptionStatus.choices,
        default=SubscriptionStatus.ACTIVE,
    )
    starts_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField()
    payment_reference = models.CharField(
        max_length=120, blank=True,
        help_text="Référence de paiement (mobile money, etc.)",
    )
    amount_paid = models.PositiveIntegerField(default=0, help_text="Montant payé (FCFA)")

    class Meta(BaseModel.Meta):
        ordering = ["-starts_at"]
        verbose_name = "Abonnement"
        verbose_name_plural = "Abonnements"

    def __str__(self) -> str:
        return f"{self.user.email} — {self.plan.name} ({self.status})"

    @property
    def is_currently_active(self) -> bool:
        return self.status == SubscriptionStatus.ACTIVE and self.expires_at > timezone.now()


# ──────────────────────────────────────────────
#  Job Alerts
# ──────────────────────────────────────────────

class JobAlert(BaseModel):
    """Smart alert: notify candidate when matching jobs appear."""
    candidate = models.ForeignKey(
        CandidateProfile,
        on_delete=models.CASCADE,
        related_name="job_alerts",
    )
    name = models.CharField(max_length=120, help_text="Ex: Alertes Marketing Douala")
    domains = models.ManyToManyField(JobDomain, blank=True)
    contract_types = models.JSONField(
        default=list, blank=True,
        help_text='Ex: ["CDI", "STAGE"]',
    )
    cities = models.JSONField(
        default=list, blank=True,
        help_text='Ex: ["Douala", "Yaoundé"]',
    )
    keywords = models.CharField(max_length=255, blank=True)
    min_salary = models.PositiveIntegerField(blank=True, null=True)
    min_match_score = models.PositiveSmallIntegerField(
        default=60,
        help_text="Score IA minimum pour déclencher l'alerte (0-100)",
    )
    notify_by_email = models.BooleanField(default=True)
    notify_by_push = models.BooleanField(default=True)
    last_notified_at = models.DateTimeField(blank=True, null=True)

    class Meta(BaseModel.Meta):
        verbose_name = "Alerte emploi"
        verbose_name_plural = "Alertes emploi"

    def __str__(self) -> str:
        return f"Alert: {self.name} — {self.candidate.user.email}"
