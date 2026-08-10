# RepoTeam

Frontend: React + Vite in `frontend/`

Backend: Django in `repoteam/`

Development flow:

1. Start the Django backend on `http://127.0.0.1:8000`
2. Start the React frontend in `frontend/`
3. The React app proxies `/api/*` requests to Django

Backend API endpoints:

- `GET /api/health/`
- `GET /api/auth/me/`
- `POST /api/auth/login/`
- `POST /api/auth/logout/`
- `POST /api/auth/register/`

The Django template frontend has been removed. React is now the only user-facing frontend, including login, registration, and logout.
