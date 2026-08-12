import { useCallback, useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { api } from './api'
import { DashboardLayout } from './components/Layout'
import { ActivityItem, Avatar, Badge, Button, EmptyState, Icon, ProjectCard, SearchInput, SkillBadge, StatCard } from './components/UI'

const profileToDeveloper = (profile) => ({
  ...profile,
  name: profile.display_name || profile.username,
  initials: (profile.display_name || profile.username).split(' ').map((part) => part[0]).join('').slice(0, 2).toUpperCase(),
  color: 'purple',
  projects: 0,
})

const projectToCard = (project) => ({
  ...project,
  name: project.title,
  emoji: project.title.slice(0, 2).toUpperCase(),
  color: 'purple',
  description: project.short_description,
  stack: project.technologies || [],
  owner: project.owner_name,
})

const activityToItem = (event) => ({
  person: event.actor?.display_name || 'A builder',
  initials: (event.actor?.display_name || 'RT').split(' ').map((part) => part[0]).join('').slice(0, 2).toUpperCase(),
  color: 'purple',
  action: event.message,
  time: new Date(event.created_at).toLocaleString([], { dateStyle: 'medium', timeStyle: 'short' }),
})

const projectTone = (status) => status === 'Recruiting' ? 'success' : status === 'Planning' ? 'warning' : 'info'

export function ConnectedProjectsPage() {
  const [query, setQuery] = useState('')
  const [technology, setTechnology] = useState('')
  const [type, setType] = useState('')
  const [difficulty, setDifficulty] = useState('')
  const [ordering, setOrdering] = useState('recent')
  const [data, setData] = useState({ count: 0, results: [], has_next: false })
  const [error, setError] = useState('')
  useEffect(() => {
    const params = new URLSearchParams({ page_size: '24', ordering })
    if (query) params.set('q', query)
    if (technology) params.set('technology', technology)
    if (type) params.set('type', type)
    if (difficulty) params.set('difficulty', difficulty)
    api(`/api/projects/?${params}`).then(setData).catch((requestError) => setError(requestError.message))
  }, [query, technology, type, difficulty, ordering])
  const reset = () => { setQuery(''); setTechnology(''); setType(''); setDifficulty('') }
  return <main><div className="page-intro container"><div><div className="eyebrow">Discover</div><h1>Explore projects</h1><p>Find your next meaningful build from community projects with momentum.</p></div><Button to="/projects/create" icon="plus">Start a project</Button></div><section className="container discovery-layout"><aside className="filter-panel"><div className="filter-heading"><h3>Filter projects</h3><button className="text-button" onClick={reset}>Reset</button></div><label>Technology<input value={technology} onChange={(event) => setTechnology(event.target.value)} placeholder="e.g. React" /></label><label>Project type<select value={type} onChange={(event) => setType(event.target.value)}><option value="">All types</option><option>Open source</option><option>Community</option><option>Side project</option><option>Learning</option></select></label><label>Difficulty<select value={difficulty} onChange={(event) => setDifficulty(event.target.value)}><option value="">All levels</option><option>Beginner</option><option>Intermediate</option><option>Advanced</option></select></label></aside><div className="results-column"><div className="results-toolbar"><SearchInput value={query} onChange={setQuery} placeholder="Search by name, technology, or keyword" /><label className="sort-select">Sort by<select value={ordering} onChange={(event) => setOrdering(event.target.value)}><option value="recent">Recently added</option><option value="title">Name</option><option value="team_capacity">Team capacity</option></select><Icon name="chevron" size={15} /></label></div><div className="results-count"><span><strong>{data.count}</strong> projects found</span></div>{error ? <div className="form-error">{error}</div> : data.results.length ? <div className="project-grid">{data.results.map((project) => <ProjectCard key={project.slug} project={projectToCard(project)} />)}</div> : <EmptyState title="No projects found" description="Try a different search or reset your filters." />}</div></section></main>
}

export function ConnectedProjectDetailsPage() {
  const { id } = useParams()
  const [project, setProject] = useState(null)
  const [error, setError] = useState('')
  useEffect(() => { api(`/api/projects/${id}/`).then((response) => setProject(response.project)).catch((requestError) => setError(requestError.message)) }, [id])
  if (error) return <main className="container section"><EmptyState title="Project unavailable" description={error} action={<Button to="/projects">Back to projects</Button>} /></main>
  if (!project) return <main className="container section"><p>Loading project...</p></main>
  const card = projectToCard(project)
  return <main><section className="detail-hero"><div className="container"><Link className="back-link" to="/projects"><Icon name="arrow" size={15} /> Back to projects</Link><div className="detail-header"><span className="project-emblem emblem-purple project-emblem-lg">{project.title.slice(0, 2).toUpperCase()}</span><div className="detail-title"><div className="title-row"><h1>{project.title}</h1><Badge tone={project.status === 'Recruiting' ? 'success' : 'info'}>{project.status}</Badge></div><p>{project.short_description}</p><div className="detail-owner"><span>Started by <strong>{project.owner_name}</strong></span></div></div>{project.repository_url ? <a href={project.repository_url} className="button button-secondary" target="_blank" rel="noreferrer"><Icon name="github" size={16} /> Repository</a> : null}</div></div></section><div className="container detail-layout"><div className="detail-main"><section className="detail-section"><h2>About the project</h2><p>{project.long_description}</p></section><section className="detail-section"><div className="section-line-heading"><h2>Open roles</h2><span>{project.roles.length} roles open</span></div><div className="roles-list">{project.roles.length ? project.roles.map((role) => <div className="role-card" key={role.id}><div><span className="role-icon">✦</span><div><h3>{role.title}</h3><p>{role.description || 'Help this project move forward with your perspective.'}</p><div className="role-tags">{role.required_skills.map((skill) => <SkillBadge key={skill}>{skill}</SkillBadge>)}<span>{role.experience}</span></div></div></div><Button variant="secondary">Apply</Button></div>) : <p>No open roles right now.</p>}</div></section></div><aside className="detail-aside"><div className="aside-block"><h3>Tech stack</h3><div className="stack-wrap">{card.stack.map((skill) => <SkillBadge key={skill}>{skill}</SkillBadge>)}</div></div><div className="aside-block"><h3>Project details</h3><dl className="detail-list"><div><dt>Project type</dt><dd>{project.project_type}</dd></div><div><dt>Difficulty</dt><dd>{project.difficulty}</dd></div><div><dt>Team capacity</dt><dd>{project.team_capacity}</dd></div><div><dt>Workflow</dt><dd>{project.workflow_status}</dd></div></dl></div></aside></div></main>
}

export function ConnectedCreateProjectPage() {
  const navigate = useNavigate()
  const [form, setForm] = useState({ title: '', short_description: '', description: '', repository_url: '', project_type: 'Open source', difficulty: 'Intermediate', status: 'Recruiting', team_capacity: '5', technologies: '', roles: 'Frontend Developer' })
  const [message, setMessage] = useState('')
  const update = (event) => setForm({ ...form, [event.target.name]: event.target.value })
  const submit = async (event, workflow_status) => {
    event.preventDefault(); setMessage('')
    try {
      const response = await api('/api/projects/', { method: 'POST', body: JSON.stringify({ ...form, team_capacity: Number(form.team_capacity), technologies: form.technologies.split(',').map((item) => item.trim()).filter(Boolean), roles: form.roles.split(',').map((title) => ({ title: title.trim() })).filter((role) => role.title), workflow_status }) })
      setMessage(workflow_status === 'published' ? 'Project published.' : 'Draft saved.')
      if (workflow_status === 'published') setTimeout(() => navigate(`/projects/${response.project.slug}`), 400)
    } catch (requestError) { setMessage(requestError.message) }
  }
  return <DashboardLayout><main className="dashboard-main create-main"><div className="form-page-heading"><Link className="back-link" to="/dashboard"><Icon name="arrow" size={15} /> Back to overview</Link><div className="eyebrow">Start something new</div><h1>Create a project</h1><p>Give your idea a home and invite people to build with you.</p></div><form className="create-form" onSubmit={(event) => submit(event, 'published')}><div className="create-form-main"><section className="form-section"><div className="form-section-heading"><span>01</span><div><h2>Project basics</h2><p>Start with the story people will see first.</p></div></div><label>Project name<input name="title" value={form.title} onChange={update} required /></label><label>Short description<textarea name="short_description" value={form.short_description} onChange={update} rows="3" required /></label><label>Full description<textarea name="description" value={form.description} onChange={update} rows="6" /></label><label>Repository URL<input name="repository_url" value={form.repository_url} onChange={update} type="url" /></label></section><section className="form-section"><div className="form-section-heading"><span>02</span><div><h2>Project details</h2><p>Help the right contributors find you.</p></div></div><div className="form-two-col"><label>Project type<select name="project_type" value={form.project_type} onChange={update}><option>Open source</option><option>Community</option><option>Side project</option><option>Learning</option></select></label><label>Difficulty<select name="difficulty" value={form.difficulty} onChange={update}><option>Beginner</option><option>Intermediate</option><option>Advanced</option></select></label><label>Status<select name="status" value={form.status} onChange={update}><option>Recruiting</option><option>Planning</option><option>In progress</option></select></label><label>Team capacity<input name="team_capacity" value={form.team_capacity} onChange={update} type="number" min="1" max="1000" /></label></div><label>Technologies <span className="optional">Separate with commas</span><input name="technologies" value={form.technologies} onChange={update} placeholder="React, TypeScript, Django" /></label><label>Roles you need <span className="optional">Separate with commas</span><input name="roles" value={form.roles} onChange={update} placeholder="Frontend Developer, Designer" /></label></section></div><aside className="create-form-side"><div className="publish-card"><h3>Ready to share it?</h3><p>You can edit the project later.</p>{message ? <div className={message.includes('success') || message.includes('published') || message.includes('saved') ? 'form-success' : 'form-error'}>{message}</div> : null}<div className="form-actions"><Button type="button" variant="secondary" onClick={(event) => submit(event, 'draft')}>Save draft</Button><Button type="submit">Publish project <Icon name="arrow" size={15} /></Button></div></div></aside></form></main></DashboardLayout>
}

export function DevelopersPage() {
  const [query, setQuery] = useState('')
  const [skill, setSkill] = useState('All skills')
  const [experience, setExperience] = useState('All experience')
  const [availability, setAvailability] = useState('Any availability')
  const [ordering, setOrdering] = useState('recommended')
  const [page, setPage] = useState(1)
  const [data, setData] = useState({ count: 0, results: [], has_next: false })
  const [error, setError] = useState('')

  useEffect(() => {
    const params = new URLSearchParams({ page: String(page), page_size: '12', ordering })
    if (query) params.set('q', query)
    if (skill !== 'All skills') params.set('skill', skill)
    if (experience !== 'All experience') params.set('experience', experience)
    if (availability !== 'Any availability') params.set('availability', availability)
    api(`/api/developers/?${params}`)
      .then((response) => { setData(response); setError('') })
      .catch((requestError) => setError(requestError.message))
  }, [query, skill, experience, availability, ordering, page])

  const reset = () => { setQuery(''); setSkill('All skills'); setExperience('All experience'); setAvailability('Any availability'); setPage(1) }
  const developers = data.results.map(profileToDeveloper)
  return <main><div className="page-intro container"><div><div className="eyebrow">The community</div><h1>Find your next teammate</h1><p>Meet developers who are curious, capable, and looking for something meaningful to build.</p></div></div><section className="container discovery-layout developer-discovery"><aside className="filter-panel"><div className="filter-heading"><h3>Filter people</h3><button className="text-button" onClick={reset}>Reset</button></div><label>Skill<select value={skill} onChange={(event) => { setSkill(event.target.value); setPage(1) }}><option>All skills</option><option>React</option><option>Python</option><option>TypeScript</option><option>Node.js</option><option>Figma</option></select></label><label>Experience<select value={experience} onChange={(event) => { setExperience(event.target.value); setPage(1) }}><option>All experience</option><option>Junior</option><option>Mid-level</option><option>Senior</option></select></label><label>Availability<select value={availability} onChange={(event) => { setAvailability(event.target.value); setPage(1) }}><option>Any availability</option><option>Open to collaborate</option><option>Looking for teammates</option><option>Available part-time</option></select></label></aside><div className="results-column"><div className="results-toolbar"><SearchInput value={query} onChange={(value) => { setQuery(value); setPage(1) }} placeholder="Search people, skills, or roles" /><label className="sort-select">Sort by<select value={ordering} onChange={(event) => { setOrdering(event.target.value); setPage(1) }}><option value="recommended">Recommended</option><option value="recent">Recently joined</option><option value="name">Name</option></select><Icon name="chevron" size={15} /></label></div><div className="results-count"><span><strong>{data.count}</strong> developers found</span></div>{error ? <div className="form-error">{error}</div> : null}{developers.length ? <><div className="developer-grid">{developers.map((developer) => <article className="developer-card" key={developer.username}><div className="developer-card-head"><Avatar user={developer} size="lg" /><span className="availability-dot" title={developer.availability}></span></div><h3><Link to={`/developers/${developer.username}`}>{developer.name}</Link></h3><p className="username">@{developer.username}</p><p className="developer-title">{developer.title || 'RepoTeam builder'}</p><div className="skills-row">{developer.skills.map((item) => <SkillBadge key={item}>{item}</SkillBadge>)}</div><div className="developer-meta"><span>{developer.experience || 'Experience not set'}</span><Badge tone="success">{developer.availability}</Badge></div><Link className="text-link" to={`/developers/${developer.username}`}>View profile <Icon name="arrow" size={15} /></Link></article>)}</div><div className="form-actions"><Button variant="secondary" disabled={page === 1} onClick={() => setPage(page - 1)}>Previous</Button><span>Page {page}</span><Button variant="secondary" disabled={!data.has_next} onClick={() => setPage(page + 1)}>Next</Button></div></> : !error ? <EmptyState title="No developers found" description="Try a different skill or search term." /> : null}</div></section></main>
}

export function DeveloperProfilePage() {
  const { username } = useParams()
  const [developer, setDeveloper] = useState(null)
  const [error, setError] = useState('')
  useEffect(() => { api(`/api/developers/${username}/`).then((response) => { setDeveloper(profileToDeveloper(response.developer)); setError('') }).catch((requestError) => setError(requestError.message)) }, [username])
  if (error) return <main className="container section"><EmptyState title="Developer unavailable" description={error} action={<Button to="/developers">Back to developers</Button>} /></main>
  if (!developer) return <main className="container section"><p>Loading developer profile...</p></main>
  return <main><section className="profile-hero"><div className="container"><Link className="back-link" to="/developers"><Icon name="arrow" size={15} /> Back to developers</Link><div className="profile-head"><Avatar user={developer} size="xl" /><div className="profile-info"><div className="profile-name-row"><div><h1>{developer.name}</h1><p>@{developer.username}</p></div><Badge tone="success">{developer.availability}</Badge></div><p className="profile-title">{developer.title || 'RepoTeam builder'}</p><div className="profile-meta">{developer.location ? <span><Icon name="location" size={15} /> {developer.location}</span> : null}{developer.github_url ? <a href={developer.github_url} target="_blank" rel="noreferrer"><Icon name="github" size={15} /> GitHub</a> : null}{developer.linkedin_url ? <a href={developer.linkedin_url} target="_blank" rel="noreferrer"><Icon name="external" size={15} /> LinkedIn</a> : null}</div></div></div></div></section><div className="container profile-layout"><div className="profile-main"><section className="profile-section"><div className="section-heading"><div><div className="eyebrow">What I bring</div><h2>Skills & tools</h2></div></div><div className="profile-skills">{developer.skills.length ? developer.skills.map((item) => <SkillBadge key={item}>{item}</SkillBadge>) : <p>No skills listed yet.</p>}</div></section><section className="profile-section"><div className="section-heading"><div><div className="eyebrow">About</div><h2>Profile</h2></div></div><p>{developer.bio || 'This builder has not added a bio yet.'}</p></section></div><aside className="profile-aside"><div className="aside-block"><h3>Experience</h3><p>{developer.experience || 'Not set'}</p></div><div className="aside-block"><h3>Availability</h3><p className="looking-for"><span className="pulse-dot"></span>{developer.availability}</p></div></aside></div></main>
}

const emptyProfile = { display_name: '', title: '', bio: '', location: '', skills: [], experience: '', availability: 'Open to collaborate', github_url: '', linkedin_url: '', email: '', is_public: true }

export function SettingsPage() {
  const [profile, setProfile] = useState(emptyProfile)
  const [message, setMessage] = useState('')
  const [loading, setLoading] = useState(true)
  useEffect(() => { api('/api/profile/me/').then((response) => { setProfile(response.profile); setLoading(false) }).catch((error) => { setMessage(error.message); setLoading(false) }) }, [])
  const update = (event) => setProfile({ ...profile, [event.target.name]: event.target.type === 'checkbox' ? event.target.checked : event.target.value })
  const save = async (event) => { event.preventDefault(); setMessage(''); try { const response = await api('/api/profile/me/', { method: 'PATCH', body: JSON.stringify({ ...profile, skills: profile.skills.split ? profile.skills.split(',').map((item) => item.trim()).filter(Boolean) : profile.skills }) }); setProfile(response.profile); setMessage('Changes saved successfully.') } catch (error) { setMessage(error.message) } }
  const skillsValue = Array.isArray(profile.skills) ? profile.skills.join(', ') : profile.skills
  return <DashboardLayout><main className="dashboard-main settings-main"><div className="dashboard-header"><div><div className="eyebrow">Your account</div><h1>Profile settings</h1><p>Update the information other builders see on RepoTeam.</p></div></div><section className="panel settings-panel">{loading ? <p>Loading profile...</p> : <form className="settings-fields" onSubmit={save}><label>Display name<input name="display_name" value={profile.display_name} onChange={update} /></label><label>Email<input name="email" type="email" value={profile.email} onChange={update} /></label><label>Title<input name="title" value={profile.title} onChange={update} placeholder="e.g. Full-stack developer" /></label><label>Bio<textarea name="bio" value={profile.bio} onChange={update} rows="4" /></label><label>Location<input name="location" value={profile.location} onChange={update} /></label><label>Skills <span className="optional">Separate with commas</span><input name="skills" value={skillsValue} onChange={update} /></label><label>Experience<select name="experience" value={profile.experience} onChange={update}><option value="">Not set</option><option>Junior</option><option>Mid-level</option><option>Senior</option></select></label><label>Availability<select name="availability" value={profile.availability} onChange={update}><option>Open to collaborate</option><option>Looking for teammates</option><option>Available part-time</option><option>Not currently available</option></select></label><label>GitHub URL<input name="github_url" type="url" value={profile.github_url} onChange={update} /></label><label>LinkedIn URL<input name="linkedin_url" type="url" value={profile.linkedin_url} onChange={update} /></label><label className="checkbox-label"><input name="is_public" type="checkbox" checked={profile.is_public} onChange={update} />Show my profile publicly</label><Button type="submit">Save changes <Icon name="check" size={15} /></Button>{message ? <div className={message.includes('successfully') ? 'form-success' : 'form-error'}>{message}</div> : null}</form>}</section></main></DashboardLayout>
}

export function ConnectedAuthPage({ mode = 'login' }) {
  const isRegister = mode === 'register'
  const navigate = useNavigate()
  const [form, setForm] = useState({ name: '', username: '', email: '', password: '', confirmation: '' })
  const [error, setError] = useState('')
  const [submitted, setSubmitted] = useState(false)
  const update = (event) => setForm({ ...form, [event.target.name]: event.target.value })
  const submit = async (event) => {
    event.preventDefault()
    setError('')
    try {
      const response = await api(`/api/auth/${isRegister ? 'register' : 'login'}/`, {
        method: 'POST',
        body: JSON.stringify(isRegister ? form : { username: form.username, password: form.password }),
      })
      setSubmitted(true)
      window.localStorage.setItem('repoteam-user', JSON.stringify(response.user))
      setTimeout(() => navigate('/dashboard'), 350)
    } catch (requestError) {
      setError(requestError.message)
    }
  }
  return <main className="auth-page"><div className="auth-split"><section className="auth-brand-panel"><div className="auth-brand-inner"><Link to="/" className="brand brand-light"><span className="brand-mark"><span></span><span></span></span><span>Repo<span>Team</span></span></Link><div className="auth-quote"><span className="quote-mark">“</span><h1>Build the thing you wish existed.</h1><p>Find collaborators, share your work, and make progress together.</p></div></div></section><section className="auth-form-panel"><div className="auth-form-wrap"><div className="mobile-auth-brand"><Link to="/" className="brand"><span className="brand-mark"><span></span><span></span></span><span>Repo<span>Team</span></span></Link></div><div className="auth-heading"><div className="eyebrow">{isRegister ? 'Join the community' : 'Welcome back'}</div><h2>{isRegister ? 'Create your account' : 'Sign in to RepoTeam'}</h2><p>{isRegister ? 'Your next project starts with a profile.' : 'Pick up where you left off.'}</p></div><form className="form-stack" onSubmit={submit}>{isRegister ? <><label>Full name<input name="name" value={form.name} onChange={update} required /></label><label>Username<input name="username" value={form.username} onChange={update} required /></label><label>Email<input name="email" type="email" value={form.email} onChange={update} required /></label></> : <label>Username<input name="username" value={form.username} onChange={update} required /></label>}<label>Password<input name="password" type="password" value={form.password} onChange={update} required /></label>{isRegister ? <label>Confirm password<input name="confirmation" type="password" value={form.confirmation} onChange={update} required /></label> : null}{error ? <div className="form-error" role="alert">{error}</div> : null}{submitted ? <div className="form-success" role="status">Success. Loading your workspace…</div> : null}<Button type="submit" className="full-button">{isRegister ? 'Create account' : 'Sign in'} <Icon name="arrow" size={16} /></Button></form><p className="auth-switch">{isRegister ? 'Already have an account?' : "Don't have an account?"} <Link to={isRegister ? '/login' : '/register'}>{isRegister ? 'Sign in' : 'Sign up'}</Link></p><Link className="back-home" to="/"><Icon name="arrow" size={15} /> Back to home</Link></div></section></div></main>
}

export function ConnectedProjectDetailsPageLive() {
  const { id } = useParams()
  const [project, setProject] = useState(null)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')
  const [busy, setBusy] = useState(false)
  useEffect(() => { api(`/api/projects/${id}/`).then((response) => setProject(response.project)).catch((requestError) => setError(requestError.message)) }, [id])
  const action = async (path, successMessage) => {
    setBusy(true); setMessage('')
    try { const response = await api(path, { method: 'POST', body: JSON.stringify({}) }); setMessage(successMessage); if (response.membership) setProject((current) => ({ ...current, is_member: true, membership: response.membership, contributors: current.contributors + 1 })); if (response.application) setProject((current) => ({ ...current, application: response.application })) } catch (requestError) { setMessage(requestError.message) } finally { setBusy(false) }
  }
  if (error) return <main className="container section"><EmptyState title="Project unavailable" description={error} action={<Button to="/projects">Back to projects</Button>} /></main>
  if (!project) return <main className="container section"><p>Loading project...</p></main>
  const applicationStatus = project.application?.status
  return <main><section className="detail-hero"><div className="container"><Link className="back-link" to="/projects"><Icon name="arrow" size={15} /> Back to projects</Link><div className="detail-header"><span className="project-emblem emblem-purple project-emblem-lg">{project.title.slice(0, 2).toUpperCase()}</span><div className="detail-title"><div className="title-row"><h1>{project.title}</h1><Badge tone={project.status === 'Recruiting' ? 'success' : 'info'}>{project.status}</Badge></div><p>{project.short_description}</p><div className="detail-owner"><span>Started by <strong>{project.owner_name}</strong></span></div></div>{project.is_owner ? <Badge tone="info">Owner</Badge> : project.is_member ? <Badge tone="success">Member</Badge> : applicationStatus === 'pending' ? <Badge tone="warning">Application pending</Badge> : <Button disabled={busy} onClick={() => action(`/api/projects/${id}/join/`, 'You joined this project.')}>Join project <Icon name="arrow" size={15} /></Button>}</div>{message ? <div className={message.includes('success') || message.includes('joined') ? 'form-success' : 'form-error'}>{message}</div> : null}</div></section><div className="container detail-layout"><div className="detail-main"><section className="detail-section"><h2>About the project</h2><p>{project.long_description}</p></section><section className="detail-section"><div className="section-line-heading"><h2>Open roles</h2><span>{project.roles.length} roles open</span></div><div className="roles-list">{project.roles.length ? project.roles.map((role) => { const applied = ['pending', 'accepted'].includes(project.application?.status) && project.application?.role?.id === role.id; return <div className="role-card" key={role.id}><div><span className="role-icon">✦</span><div><h3>{role.title}</h3><p>{role.description || 'Help this project move forward with your perspective.'}</p><div className="role-tags">{role.required_skills.map((skill) => <SkillBadge key={skill}>{skill}</SkillBadge>)}<span>{role.experience}</span></div></div></div>{project.is_owner || project.is_member ? null : <Button disabled={busy || applied || applicationStatus === 'pending'} variant={applied || applicationStatus === 'pending' ? 'success' : 'secondary'} onClick={() => action(`/api/projects/${id}/roles/${role.id}/apply/`, 'Application submitted.')}>{applied || applicationStatus === 'pending' ? 'Applied' : 'Apply'} {applied || applicationStatus === 'pending' ? <Icon name="check" size={14} /> : null}</Button>}</div> }) : <p>No open roles right now.</p>}</div></section></div><aside className="detail-aside"><div className="aside-block"><h3>Tech stack</h3><div className="stack-wrap">{project.stack.map((skill) => <SkillBadge key={skill}>{skill}</SkillBadge>)}</div></div><div className="aside-block"><h3>Project details</h3><dl className="detail-list"><div><dt>Project type</dt><dd>{project.project_type}</dd></div><div><dt>Difficulty</dt><dd>{project.difficulty}</dd></div><div><dt>Team capacity</dt><dd>{project.contributors} / {project.team_capacity}</dd></div><div><dt>Workflow</dt><dd>{project.workflow_status}</dd></div></dl></div></aside></div></main>
}

export function ConnectedDashboardPage() {
  const [data, setData] = useState(null)
  const [error, setError] = useState('')
  useEffect(() => { api('/api/dashboard/').then(setData).catch((requestError) => setError(requestError.message)) }, [])
  if (error) return <DashboardLayout><main className="dashboard-main"><EmptyState title="Workspace unavailable" description={error} action={<Button to="/login">Sign in again</Button>} /></main></DashboardLayout>
  if (!data) return <DashboardLayout><main className="dashboard-main"><p>Loading your workspace...</p></main></DashboardLayout>
  const summary = data.summary
  const name = data.user.display_name || data.user.username
  const projects = [...data.owned_projects, ...data.contributing_projects].slice(0, 4)
  const activity = data.activity.map(activityToItem)
  return <DashboardLayout user={data.user}><main className="dashboard-main"><div className="dashboard-header"><div><div className="eyebrow">{new Date().toLocaleDateString([], { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' })}</div><h1>Overview</h1><p>A clear view of what you are building and where to go next.</p></div><div className="dashboard-header-actions"><Button to="/projects/create" icon="plus">New project</Button></div></div><section className="welcome-banner"><div><span className="eyebrow">Your workspace</span><h2>Welcome back, {name.split(' ')[0]} <span className="wave">✦</span></h2><p>{summary.projects} active project{summary.projects === 1 ? '' : 's'} and {summary.applications_to_review} application{summary.applications_to_review === 1 ? '' : 's'} waiting for review.</p></div><Button to="/developers" variant="secondary" icon="arrow">Find teammates</Button></section><div className="stats-grid"><StatCard icon="bookmark" label="Projects" value={summary.projects} trend={`${summary.owned_projects} owned · ${summary.contributing_projects} contributing`} /><StatCard icon="users" label="Team members" value={summary.team_members} trend="Across your projects" /><StatCard icon="bell" label="Applications" value={summary.applications_sent} trend={`${summary.applications_to_review} need your review`} /><StatCard icon="heart" label="Contributions" value={summary.contributions} trend={`${summary.open_roles} open roles in your projects`} /></div><div className="dashboard-two-col"><div className="dashboard-projects"><div className="panel-heading"><div><h3>My projects</h3><p>Projects you own or contribute to.</p></div><Link to="/dashboard/projects">View all</Link></div>{projects.length ? projects.map((project) => <div className="project-list-row" key={project.slug}><span className="project-emblem emblem-purple">{project.title.slice(0, 2).toUpperCase()}</span><div className="project-list-info"><h4><Link to={`/projects/${project.slug}`}>{project.title}</Link></h4><p>Updated {new Date(project.updated_at).toLocaleDateString()}</p></div><div className="project-progress"><div><span>{project.contributors} / {project.team_capacity} members</span><strong>{Math.round((project.contributors / project.team_capacity) * 100)}%</strong></div><span className="progress-track"><i style={{ width: `${Math.min(100, (project.contributors / project.team_capacity) * 100)}%` }}></i></span></div><Badge tone={projectTone(project.status)}>{project.status}</Badge></div>) : <EmptyState title="No projects yet" description="Create or join your first project." action={<Button to="/projects">Explore projects</Button>} />}</div><div className="panel activity-panel"><div className="panel-heading"><h3>Recent activity</h3><Link to="/dashboard">Refresh</Link></div>{activity.length ? activity.map((item, index) => <ActivityItem activity={item} key={`${item.person}-${index}`} />) : <p>No activity yet.</p>}</div></div><section className="dashboard-recommended"><div className="panel-heading"><div><h3>Recommended for you</h3><p>Matched to your skills and availability.</p></div><Link to="/projects">Explore more</Link></div>{data.recommendations.length ? <div className="project-grid">{data.recommendations.map((project) => <ProjectCard project={projectToCard(project)} key={project.slug} compact />)}</div> : <EmptyState title="No recommendations yet" description="Add skills and availability to your profile to improve your matches." action={<Button to="/settings">Update profile</Button>} />}</section></main></DashboardLayout>
}

export function ConnectedMyProjectsPage() {
  const [data, setData] = useState(null)
  const [error, setError] = useState('')
  useEffect(() => { api('/api/dashboard/projects/').then(setData).catch((requestError) => setError(requestError.message)) }, [])
  if (error) return <DashboardLayout><main className="dashboard-main"><EmptyState title="Projects unavailable" description={error} /></main></DashboardLayout>
  if (!data) return <DashboardLayout><main className="dashboard-main"><p>Loading your projects...</p></main></DashboardLayout>
  const renderProject = (project) => <div className="table-row" key={project.slug}><div className="table-project"><span className="project-emblem emblem-purple">{project.title.slice(0, 2).toUpperCase()}</span><div><h4>{project.title}</h4><span>{project.project_type}</span></div></div><div><span className="table-label">Status</span><Badge tone={projectTone(project.status)}>{project.status}</Badge></div><div><span className="table-label">Team</span><strong>{project.contributors} / {project.team_capacity}</strong></div><div><span className="table-label">Open roles</span><strong>{project.roles.length}</strong></div><div><span className="table-label">Updated</span><span>{new Date(project.updated_at).toLocaleDateString()}</span></div><Button to={`/projects/${project.slug}`} variant="ghost">View</Button></div>
  return <DashboardLayout><main className="dashboard-main"><div className="dashboard-header"><div><div className="eyebrow">Your workspace</div><h1>My projects</h1><p>Keep track of the projects you own and the teams you are part of.</p></div><Button to="/projects/create" variant="secondary" icon="plus">New project</Button></div><div className="projects-summary"><div><strong>{data.summary.owned_projects}</strong><span>Owned</span></div><div><strong>{data.summary.contributing_projects}</strong><span>Contributing to</span></div><div><strong>{data.summary.open_roles}</strong><span>Open roles</span></div><div><strong>{data.summary.contributions}</strong><span>Contributions</span></div></div><section className="panel table-panel"><div className="panel-heading"><div><h3>Owned projects</h3><p>Projects you lead.</p></div></div><div className="project-table">{data.owned_projects.length ? data.owned_projects.map(renderProject) : <EmptyState title="No owned projects" description="Start an idea and invite your first contributors." action={<Button to="/projects/create">Create a project</Button>} />}</div></section><section className="panel table-panel" style={{ marginTop: 20 }}><div className="panel-heading"><div><h3>Projects I contribute to</h3><p>Projects where your work is part of the team.</p></div></div><div className="project-table">{data.contributing_projects.length ? data.contributing_projects.map(renderProject) : <EmptyState title="No contributions yet" description="Find a project that matches your skills and availability." action={<Button to="/projects">Explore projects</Button>} />}</div></section></main></DashboardLayout>
}

const applicationTone = (status) => status === 'accepted' ? 'success' : status === 'rejected' ? 'danger' : status === 'withdrawn' ? 'neutral' : 'warning'

export function ConnectedApplicationsPage() {
  const [tab, setTab] = useState('sent')
  const [data, setData] = useState({ count: 0, results: [] })
  const [error, setError] = useState('')
  const load = useCallback(() => api(`/api/applications/?kind=${tab}`).then(setData).catch((requestError) => setError(requestError.message)), [tab])
  useEffect(() => { load() }, [load])
  const updateApplication = async (id, action) => { try { await api(`/api/applications/${id}/${action}/`, { method: 'POST' }); load() } catch (requestError) { setError(requestError.message) } }
  return <DashboardLayout><main className="dashboard-main"><div className="dashboard-header"><div><div className="eyebrow">Collaboration</div><h1>Applications</h1><p>Keep conversations moving and find the right people for each project.</p></div></div><div className="tabs"><button className={tab === 'sent' ? 'active' : ''} onClick={() => setTab('sent')}>Sent</button><button className={tab === 'received' ? 'active' : ''} onClick={() => setTab('received')}>Received</button></div>{error ? <div className="form-error">{error}</div> : null}<div className="application-list">{data.results.map((application) => { const received = tab === 'received'; const person = received ? application.applicant.display_name : application.project.owner_name; return <div className="application-card" key={application.id}><div className="project-emblem emblem-purple">{application.project.title.slice(0, 2).toUpperCase()}</div><div className="application-info"><div className="application-title"><h3>{received ? application.applicant.display_name : application.project.title}</h3><Badge tone={applicationTone(application.status)}>{application.status}</Badge></div><p>{received ? `Applied to ${application.project.title}` : `Application to ${person}`} · {new Date(application.created_at).toLocaleDateString()}</p><span className="role-label">{application.role?.title || 'Project contributor'}</span></div>{received && application.status === 'pending' ? <><Button variant="secondary" onClick={() => updateApplication(application.id, 'reject')}>Reject</Button><Button onClick={() => updateApplication(application.id, 'accept')}>Accept</Button></> : !received && application.status === 'pending' ? <Button variant="ghost" onClick={() => updateApplication(application.id, 'withdraw')}>Withdraw</Button> : null}</div> })}{!data.results.length && !error ? <EmptyState title="No applications yet" description="Your next great collaboration could be one search away." action={<Button to="/projects">Explore projects</Button>} /> : null}</div></main></DashboardLayout>
}

export function ConnectedTeamPage() {
  const [directories, setDirectories] = useState([])
  const [error, setError] = useState('')
  useEffect(() => { api('/api/memberships/').then(async (response) => { const unique = [...new Map(response.results.map((membership) => [membership.project, membership])).values()]; const results = await Promise.all(unique.map(async (membership) => ({ project: membership, members: (await api(`/api/projects/${membership.project}/members/`)).results }))); setDirectories(results) }).catch((requestError) => setError(requestError.message)) }, [])
  return <DashboardLayout><main className="dashboard-main"><div className="dashboard-header"><div><div className="eyebrow">Your workspace</div><h1>Team directory</h1><p>See the people building each project you are part of.</p></div><Button to="/developers" variant="secondary" icon="plus">Find someone</Button></div>{error ? <div className="form-error">{error}</div> : null}{directories.map(({ project, members }) => <section className="panel table-panel" key={project.project}><div className="panel-heading"><div><h3>{project.project_title}</h3><p>{members.length} member{members.length === 1 ? '' : 's'} · {project.member_role === 'owner' ? 'You own this project' : 'You contribute here'}</p></div><Button to={`/projects/${project.project}`} variant="ghost">View project</Button></div><div className="team-directory-grid">{members.map((member) => <article className="developer-card" key={member.id}><div className="developer-card-head"><Avatar user={{ color: 'purple', initials: (member.display_name || member.username).split(' ').map((part) => part[0]).join('').slice(0, 2).toUpperCase() }} size="lg" /></div><h3>{member.display_name}</h3><p className="username">@{member.username}</p><p className="developer-title">{member.role_title}</p><div className="skills-row">{member.role?.required_skills?.slice(0, 3).map((skill) => <SkillBadge key={skill}>{skill}</SkillBadge>)}</div><Link className="text-link" to={`/developers/${member.username}`}>View profile <Icon name="arrow" size={15} /></Link></article>)}</div></section>)}{!directories.length && !error ? <EmptyState title="No team memberships yet" description="Join a project or apply for an open role to build your team." action={<Button to="/projects">Explore projects</Button>} /> : null}</main></DashboardLayout>
}
