import { useEffect, useMemo, useState } from 'react'
import './App.css'

const emptyForm = {
  username: '',
  email: '',
  password: '',
  confirmation: '',
}

function App() {
  const [backendHealth, setBackendHealth] = useState('Checking backend...')
  const [backendError, setBackendError] = useState('')
  const [authMode, setAuthMode] = useState('login')
  const [form, setForm] = useState(emptyForm)
  const [statusMessage, setStatusMessage] = useState('')
  const [statusType, setStatusType] = useState('neutral')
  const [currentUser, setCurrentUser] = useState(null)
  const [loading, setLoading] = useState(false)

  const authTitle = useMemo(
    () => (authMode === 'login' ? 'Welcome back' : 'Create your account'),
    [authMode],
  )

  useEffect(() => {
    const controller = new AbortController()

    async function loadBackendState() {
      try {
        const [healthResponse, meResponse] = await Promise.all([
          fetch('/api/health/', { signal: controller.signal }),
          fetch('/api/auth/me/', { signal: controller.signal, credentials: 'include' }),
        ])

        if (!healthResponse.ok) {
          throw new Error(`Health check failed with ${healthResponse.status}`)
        }

        const healthData = await healthResponse.json()
        setBackendHealth(
          `${healthData.service} is ${healthData.status} on ${healthData.backend}.`,
        )

        if (meResponse.ok) {
          const meData = await meResponse.json()
          setCurrentUser(meData.authenticated ? meData.user : null)
        }
      } catch (requestError) {
        if (requestError.name === 'AbortError') {
          return
        }

        setBackendError(
          'Backend not reachable yet. Start the Django server on port 8000.',
        )
        setBackendHealth('Waiting for backend...')
      }
    }

    loadBackendState()

    return () => controller.abort()
  }, [])

  function updateField(event) {
    const { name, value } = event.target
    setForm((previousForm) => ({
      ...previousForm,
      [name]: value,
    }))
  }

  async function submitAuth(event) {
    event.preventDefault()
    setLoading(true)
    setStatusMessage('')

    const endpoint =
      authMode === 'login' ? '/api/auth/login/' : '/api/auth/register/'

    try {
      const response = await fetch(endpoint, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(form),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Request failed.')
      }

      setCurrentUser(data.user)
      setStatusType('success')
      setStatusMessage(data.message)
      setForm(emptyForm)
    } catch (submitError) {
      setStatusType('error')
      setStatusMessage(submitError.message)
    } finally {
      setLoading(false)
    }
  }

  async function handleLogout() {
    setLoading(true)
    setStatusMessage('')

    try {
      const response = await fetch('/api/auth/logout/', {
        method: 'POST',
        credentials: 'include',
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Logout failed.')
      }

      setCurrentUser(null)
      setStatusType('success')
      setStatusMessage(data.message)
    } catch (logoutError) {
      setStatusType('error')
      setStatusMessage(logoutError.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">RepoTeam</p>
          <h1>React frontend, Python backend.</h1>
        </div>

        <nav className="nav">
          <a href="#auth">Auth</a>
          <a href="#status">Status</a>
          <a href="#workflow">Workflow</a>
        </nav>
      </header>

      <main className="content">
        <section className="hero">
          <div className="hero-copy">
            <p className="eyebrow">Team up faster</p>
            <h2>Login and registration now run from React.</h2>
            <p className="subcopy">
              The frontend talks to Django over API endpoints. Sessions are
              preserved through the browser cookie, and the UI checks the
              backend on load.
            </p>

            <div className="actions">
              <button
                type="button"
                className={`pill ${authMode === 'login' ? 'pill-active' : ''}`}
                onClick={() => setAuthMode('login')}
              >
                Login
              </button>
              <button
                type="button"
                className={`pill ${authMode === 'register' ? 'pill-active' : ''}`}
                onClick={() => setAuthMode('register')}
              >
                Register
              </button>
              <a className="secondary" href="#status">
                View backend status
              </a>
            </div>
          </div>

          <div className="status-card" id="status">
            <span className="status-label">Backend status</span>
            <strong>{backendHealth}</strong>
            <p>{backendError || 'React is connected to the Django API through /api.'}</p>
            {currentUser ? (
              <div className="user-chip">
                Signed in as <strong>{currentUser.username}</strong>
              </div>
            ) : (
              <div className="user-chip muted">Not signed in</div>
            )}
          </div>
        </section>

        <section className="auth-layout" id="auth">
          <article className="auth-card">
            <div className="auth-header">
              <div>
                <p className="eyebrow">{authMode === 'login' ? 'Sign in' : 'Join now'}</p>
                <h3>{authTitle}</h3>
              </div>

              <button
                type="button"
                className="text-button"
                onClick={() => setAuthMode(authMode === 'login' ? 'register' : 'login')}
              >
                Switch to {authMode === 'login' ? 'register' : 'login'}
              </button>
            </div>

            <form className="auth-form" onSubmit={submitAuth}>
              <label>
                Username
                <input
                  name="username"
                  value={form.username}
                  onChange={updateField}
                  autoComplete="username"
                  required
                />
              </label>

              {authMode === 'register' ? (
                <label>
                  Email
                  <input
                    name="email"
                    type="email"
                    value={form.email}
                    onChange={updateField}
                    autoComplete="email"
                    required
                  />
                </label>
              ) : null}

              <label>
                Password
                <input
                  name="password"
                  type="password"
                  value={form.password}
                  onChange={updateField}
                  autoComplete={
                    authMode === 'login' ? 'current-password' : 'new-password'
                  }
                  required
                />
              </label>

              {authMode === 'register' ? (
                <label>
                  Confirm password
                  <input
                    name="confirmation"
                    type="password"
                    value={form.confirmation}
                    onChange={updateField}
                    autoComplete="new-password"
                    required
                  />
                </label>
              ) : null}

              <button className="primary auth-submit" type="submit" disabled={loading}>
                {loading
                  ? 'Please wait...'
                  : authMode === 'login'
                    ? 'Login'
                    : 'Create account'}
              </button>
            </form>

            {statusMessage ? (
              <p className={`flash ${statusType}`}>{statusMessage}</p>
            ) : null}
          </article>

          <aside className="auth-card panel">
            <h3>Current session</h3>
            <p>
              This state comes from the Django session cookie, not from local
              storage.
            </p>

            {currentUser ? (
              <>
                <dl className="session-grid">
                  <div>
                    <dt>Username</dt>
                    <dd>{currentUser.username}</dd>
                  </div>
                  <div>
                    <dt>Email</dt>
                    <dd>{currentUser.email || 'Not set'}</dd>
                  </div>
                  <div>
                    <dt>User ID</dt>
                    <dd>{currentUser.id}</dd>
                  </div>
                </dl>

                <button
                  type="button"
                  className="secondary logout"
                  onClick={handleLogout}
                  disabled={loading}
                >
                  Logout
                </button>
              </>
            ) : (
              <p className="muted-copy">
                No active session yet. Log in or register to create one.
              </p>
            )}
          </aside>
        </section>

        <section className="workflow" id="workflow">
          <h3>Project layout</h3>
          <ol>
            <li>Frontend lives in <code>frontend/</code> as a React app.</li>
            <li>Backend lives in <code>repoteam/</code> as a Django app.</li>
            <li>Auth requests go to <code>/api/auth/*</code>.</li>
          </ol>
        </section>
      </main>
    </div>
  )
}

export default App
