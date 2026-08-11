# RepoTeam Backend Roadmap

This document tracks the backend work needed to connect the React frontend to a real Django API and database.

## Phase 1 — Backend foundation ✅ Completed

The Django project and `core` application are in place. The backend exposes a health endpoint and the React application is configured to use `/api/*` endpoints through its development proxy.

Completed:

- Django project structure
- `core` application and URL routing
- API health endpoint: `GET /api/health/`
- Base API information endpoint
- React-to-Django development proxy setup

## Phase 2 — Authentication baseline ✅ Completed

Basic session-based user authentication has been implemented with Django's built-in user model.

Completed:

- Account registration: `POST /api/auth/register/`
- Login: `POST /api/auth/login/`
- Logout: `POST /api/auth/logout/`
- Current-user lookup: `GET /api/auth/me/`
- Password confirmation and duplicate-username checks

Still needed in this area:

- Connect the React login and registration screens to these APIs (they currently use mock/local storage behavior)
- Strengthen validation and return consistent API error formats
- Configure CSRF protection correctly for production instead of relying on CSRF exemptions

## Phase 3 — User profiles ⏳ Next

Status: completed. Profiles, public discovery, profile settings, and developer pagination now use the live Django API.

Completed in this phase:

- `Profile` database model linked one-to-one to Django users
- Public developer list and profile-detail APIs
- Developer filtering by query, skill, experience, and availability
- Authenticated read/update API for the signed-in user's profile
- Automated API coverage for profile visibility, filtering, and updates

Completed Phase 3 on the React side:

- Developer directory and public profile pages fetch live API data
- Profile settings load and save through the authenticated profile API
- Developer results have backend pagination and previous/next controls

## Phase 4 — Projects and roles ⏳ Planned

Create the core project data model and APIs so project cards, details pages, and project creation use database data rather than `mockData.js`.

Build:

- Projects with owner, title, descriptions, repository URL, type, difficulty, status, and team capacity
- Technologies/skills attached to projects
- Open project roles with required skills and experience level
- Draft, publish, edit, and archive workflows
- Project detail, list, create, and update APIs
- Backend search, filtering, sorting, and pagination
- Owner authorization: only project owners can change their projects

## Phase 5 — Membership and applications ⏳ Planned

Implement the workflow for people joining projects or applying for open roles.

Build:

- Project membership records and member roles
- Applications with pending, accepted, withdrawn, and rejected states
- Apply-to-role and join-project endpoints
- Owner review, accept, and reject actions
- Duplicate-application and capacity checks
- Sent and received applications for the dashboard

## Phase 6 — Dashboard, teams, and activity ⏳ Planned

Provide the real data behind the workspace pages.

Build:

- Dashboard summary counts
- Owned projects and projects a user contributes to
- Team/member directory for each project
- Activity events such as project creation, membership changes, and application decisions
- Personalised project recommendations based on skills and availability

## Phase 7 — Notifications and preferences ⏳ Planned

Make collaboration updates visible and configurable.

Build:

- In-app notifications for applications, decisions, invitations, and project updates
- Read/unread notification state
- Email notification preferences
- Privacy and visibility preferences
- Appearance preferences if they should be shared across devices

## Phase 8 — Quality, security, and deployment ⏳ Planned

Prepare the application for reliable production use.

Build:

- API input validation and consistent error responses
- Permission and authorization tests
- Unit and integration tests for every main API flow
- Rate limiting and secure production session/CSRF configuration
- Environment-based secrets and PostgreSQL configuration
- Logging, error monitoring, database backup plan, and deployment setup
- API documentation for the frontend team

## Recommended implementation order

1. Connect the existing authentication APIs to React.
2. Build user profiles and developer discovery.
3. Build projects, roles, and project discovery.
4. Build applications and membership management.
5. Build dashboard/activity data and notifications.
6. Finish security, test coverage, and deployment preparation.
