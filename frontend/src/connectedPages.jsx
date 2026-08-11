import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { api } from './api'
import { DashboardLayout } from './components/Layout'
import { Avatar, Badge, Button, EmptyState, Icon, SearchInput, SkillBadge } from './components/UI'

const profileToDeveloper = (profile) => ({
  ...profile,
  name: profile.display_name || profile.username,
  initials: (profile.display_name || profile.username).split(' ').map((part) => part[0]).join('').slice(0, 2).toUpperCase(),
  color: 'purple',
  projects: 0,
})

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
