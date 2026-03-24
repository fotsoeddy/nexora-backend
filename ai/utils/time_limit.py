from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
from ai.models import InterviewSession, GlobalSettings

def get_user_remaining_seconds(user):
    """
    Calculates the remaining interview seconds for a user.
    Total Limit = Global Default + User Extra Minutes.
    Spent = Sum of durations of all completed sessions.
    """
    if not user or not user.is_authenticated:
        return 0
    
    settings = GlobalSettings.get_settings()
    extra_minutes = user.profile.extra_minutes if hasattr(user, 'profile') else 0.0
    total_allowed_seconds = int((settings.default_minutes_per_assistant + extra_minutes) * 60)
    
    # Calculate spent seconds across all user sessions that have both start and end times
    sessions = InterviewSession.objects.filter(
        user=user, 
        started_at__isnull=False, 
        completed_at__isnull=False
    )
    
    total_spent_seconds = 0
    for session in sessions:
        duration = (session.completed_at - session.started_at).total_seconds()
        total_spent_seconds += max(0, duration)
    
    remaining = int(total_allowed_seconds - total_spent_seconds)
    return max(0, remaining)
