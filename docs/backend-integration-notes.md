# Backend Integration Notes

This branch ports part of the local Codex backend work into the collaborator backend architecture without importing the second backend tree.

Integrated improvements:

- safer OpenAI usage with local fallback in `ai/openai_utils.py`
- persistent interview answer saving
- structured answer evaluation
- final interview grading persisted into `InterviewFeedback`
- nested interview session serialization
- authenticated client endpoint for answer submission

Not ported in this branch:

- the separate `accounts/jobs/ai_engine` backend architecture from the other repository
- mobile-specific local candidate APIs for saved jobs, alerts, applications, chat assistant, cover letters, and salary estimates

Reason:

The collaborator repository has a different backend architecture. Porting those features safely requires a separate adaptation pass, not a raw history merge.
