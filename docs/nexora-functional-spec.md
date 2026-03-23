# Nexora Local Functional Specification

## Scope

This document defines the local functional baseline implemented in the workspace on `2026-03-23`.

It intentionally does **not** replace or overwrite APIs already identified on the remote deployment.
To avoid future merge conflicts with the incoming pull, the local additions are split as follows:

- remote-compatible routes kept under `/ai/api/...`
- new local candidate and assistant routes added under `/api/...` and `/api/ai/...`

## Current project structure

- Backend: `nexora-mobile-app` (`Django`, `DRF`, `SimpleJWT`, `drf-spectacular`)
- Frontend: `nexora-frontend` (`Expo`, `React Native`, `Expo Router`, `TypeScript`)

## Frontend architecture

The frontend now follows a feature-oriented structure:

- `src/features/auth`
- `src/features/jobs`
- `src/features/interviews`
- `src/features/applications`
- `src/features/savedJobs`
- `src/features/jobAlerts`
- `src/features/assistant`
- `src/shared/api`
- `src/shared/config`
- `src/shared/lib`
- `src/shared/storage`

Rules applied:

- route files in `app/` stay thin
- API calls live in feature services
- backend DTOs are typed
- screens no longer own transport logic
- shared formatters and API client are centralized

## Email workflows

### 1. Account verification email

Handled by the `accounts` app.

Trigger:
- user registration

Purpose:
- verify ownership of the email before full account usage

Local behavior:
- in development, `config/settings/dev.py` uses console email backend
- in tests, locmem backend is used

Required environment for SMTP delivery:

- `EMAIL_BACKEND`
- `EMAIL_HOST`
- `EMAIL_PORT`
- `EMAIL_HOST_USER`
- `EMAIL_HOST_PASSWORD`
- `EMAIL_USE_TLS`
- `EMAIL_USE_SSL`
- `DEFAULT_FROM_EMAIL`

Related frontend behavior:
- signup calls `/api/auth/register`
- verify screen instructs the user to confirm through the verification email link

### 2. Password reset email

Handled by the `accounts` app.

Trigger:
- forgot password request

Purpose:
- send a reset link to the account owner

Required URL configuration:

- `FRONTEND_RESET_URL`

### 3. Application confirmation email

Handled by `jobs/emails.py`.

Trigger:
- successful `POST /api/applications/`

Purpose:
- confirm that the application was recorded
- expose the initial application status

Payload currently included in the email:

- job title
- company name
- application status

## Backend API surface

### Existing aligned routes

Authentication:

- `POST /api/auth/register`
- `POST /api/auth/login`
- `POST /api/auth/refresh`
- `GET/PATCH /api/auth/me`

Jobs:

- `GET /ai/api/jobs/`
- `GET /ai/api/jobs/{id}/`
- `POST /ai/api/jobs/`
- `PUT /ai/api/jobs/{id}/`
- `DELETE /ai/api/jobs/{id}/`

Interviews:

- `GET /ai/api/interviews/sessions/`
- `POST /ai/api/interviews/sessions/`
- `GET /ai/api/interviews/sessions/{id}/`
- `POST /ai/api/interviews/sessions/generate/`
- `POST /api/ai/interviews/sessions/{id}/answers/`

### New local candidate routes

- `GET /api/applications/`
- `POST /api/applications/`
- `GET /api/saved-jobs/`
- `POST /api/saved-jobs/`
- `DELETE /api/saved-jobs/{job_id}/`
- `GET /api/job-alerts/`
- `POST /api/job-alerts/`
- `PATCH /api/job-alerts/{id}/`

### New local AI assistant routes

- `POST /api/ai/cover-letters/generate/`
- `POST /api/ai/salary-estimates/`
- `GET /api/ai/chat/sessions/`
- `POST /api/ai/chat/sessions/`
- `GET /api/ai/chat/sessions/{id}/`
- `POST /api/ai/chat/sessions/{id}/messages/`

## Functional definitions

### Applications

Input:

- `job_offer_id`
- optional `cv_id`
- optional `cover_letter`

Business rules:

- authenticated candidate required
- duplicate active applications are rejected
- submission sends a confirmation email

Frontend screens using it:

- `JobDetailScreen`
- `ApplicationsScreen`
- `SavedScreen`

### Saved jobs

Input:

- `job_offer_id`

Business rules:

- authenticated candidate required
- delete performs a soft delete
- re-saving a previously deleted bookmark reactivates it

Frontend screens using it:

- `JobDetailScreen`
- `SavedScreen`

### Job alerts

Input:

- `name`
- `keywords`
- `cities`
- `frequency`
- notification flags

Business rules:

- authenticated candidate required
- active state can be toggled without deleting the alert
- match count is computed from current active job offers

Frontend screens using it:

- `AlertsScreen`

### Cover letter generation

Input:

- `job_title`
- `company_name`
- optional `job_offer_id`
- `tone`

Output:

- generated letter text
- normalized role/company metadata

Frontend screens using it:

- `CoverLetterScreen`

### Salary estimation

Input:

- `job_title`
- `city`
- `experience_level`

Output:

- `estimated_min`
- `estimated_median`
- `estimated_max`
- `confidence_level`
- `data_points_used`
- explanation

Frontend screens using it:

- `SalaryScreen`

### AI career assistant chat

Behavior:

- create or reuse a personal chat session
- persist AI and user messages
- return suggested next prompts

Frontend screens using it:

- `ChatScreen`

### Interview generation and scoring

Behavior:

- create a role-specific question set
- reveal questions progressively in the text interview UI
- score each submitted answer
- persist per-answer feedback
- compute final session score and final feedback

Frontend screens using it:

- `InterviewScreen`
- `InterviewChatScreen`
- `VoiceInterviewScreen`
- `InterviewResultScreen`

## Validation status

Backend checks:

- `python manage.py makemigrations --check`
- `python manage.py test jobs.tests_api jobs.tests_more_api ai_engine.tests_api ai_engine.tests_more_api accounts.tests`

Frontend checks:

- `tsc --noEmit`

## Reserved for future pull

The following remote areas were intentionally left untouched for later reconciliation with the collaborator's code:

- remote-only Vapi endpoints under `/ai/api/vapi/...`
- any remote implementation details not present in the local repositories
- any server-side code currently deployed but not yet recovered from the correct host or git source
