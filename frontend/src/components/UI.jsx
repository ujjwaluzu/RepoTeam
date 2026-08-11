import { Link } from 'react-router-dom'

export function Icon({ name, size = 18 }) {
  const paths = {
    arrow: <><path d="M5 12h14"/><path d="m13 6 6 6-6 6"/></>,
    search: <><circle cx="11" cy="11" r="7"/><path d="m20 20-4-4"/></>,
    plus: <><path d="M12 5v14"/><path d="M5 12h14"/></>,
    menu: <><path d="M4 6h16"/><path d="M4 12h16"/><path d="M4 18h16"/></>,
    close: <><path d="M6 6l12 12"/><path d="M18 6 6 18"/></>,
    github: <><path d="M15 22v-4a4.8 4.8 0 0 0-1-3.5c3.3-.4 6.7-1.6 6.7-7A5.4 5.4 0 0 0 19.2 4 5 5 0 0 0 19.1.9S17.9.5 15 2.4a13.4 13.4 0 0 0-6 0C6.1.5 4.9.9 4.9.9A5 5 0 0 0 4.8 4a5.4 5.4 0 0 0-1.4 3.5c0 5.4 3.4 6.6 6.7 7A4.8 4.8 0 0 0 9 18v4"/><path d="M9 18c-4.5 2-5-2-7-2"/></>,
    chevron: <path d="m6 9 6 6 6-6"/>,
    check: <path d="m5 12 4 4L19 6"/>,
    external: <><path d="M14 3h7v7"/><path d="M10 14 21 3"/><path d="M21 14v5a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5"/></>,
    grid: <><rect x="4" y="4" width="6" height="6" rx="1"/><rect x="14" y="4" width="6" height="6" rx="1"/><rect x="4" y="14" width="6" height="6" rx="1"/><rect x="14" y="14" width="6" height="6" rx="1"/></>,
    users: <><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.9M16 3.1a4 4 0 0 1 0 7.8"/></>,
    settings: <><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.9l.1.1-1.7 1.7-.1-.1a1.7 1.7 0 0 0-1.9-.3 1.7 1.7 0 0 0-1 1.5v.2h-2.4v-.2a1.7 1.7 0 0 0-1-1.5 1.7 1.7 0 0 0-1.9.3l-.1.1L8 17l.1-.1a1.7 1.7 0 0 0 .3-1.9 1.7 1.7 0 0 0-1.5-1H6v-2.4h.2a1.7 1.7 0 0 0 1.5-1 1.7 1.7 0 0 0-.3-1.9L7.3 8.6 9 7l.1.1a1.7 1.7 0 0 0 1.9.3 1.7 1.7 0 0 0 1-1.5v-.2h2.4v.2a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.9-.3l.1-.1 1.7 1.7-.1.1a1.7 1.7 0 0 0-.3 1.9 1.7 1.7 0 0 0 1.5 1h.2V14h-.2a1.7 1.7 0 0 0-1.5 1Z"/></>,
    bell: <><path d="M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9"/><path d="M13.7 21a2 2 0 0 1-3.4 0"/></>,
    bookmark: <path d="M6 4a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v18l-6-4-6 4Z"/>,
    clock: <><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></>,
    location: <><path d="M20 10c0 5-8 11-8 11S4 15 4 10a8 8 0 1 1 16 0Z"/><circle cx="12" cy="10" r="2.5"/></>,
    heart: <path d="M20.8 8.6c0 5.5-8.8 10.4-8.8 10.4S3.2 14.1 3.2 8.6A4.6 4.6 0 0 1 12 6.3a4.6 4.6 0 0 1 8.8 2.3Z"/>,
  }
  return <svg className="icon" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">{paths[name] || paths.grid}</svg>
}

export function Button({ children, variant = 'primary', to, icon, type = 'button', className = '', ...props }) {
  const content = <>{children}{icon ? <Icon name={icon} size={16} /> : null}</>
  const classes = `button button-${variant} ${className}`
  return to ? <Link className={classes} to={to} {...props}>{content}</Link> : <button className={classes} type={type} {...props}>{content}</button>
}

export function Badge({ children, tone = 'neutral' }) { return <span className={`badge badge-${tone}`}>{children}</span> }

export function Avatar({ user, size = 'md' }) { return <span className={`avatar avatar-${size} avatar-${user?.color || 'purple'}`}>{user?.initials || 'RT'}</span> }

export function Logo() { return <Link to="/" className="brand"><span className="brand-mark"><span></span><span></span></span><span>Repo<span>Team</span></span></Link> }

export function SectionHeading({ eyebrow, title, description, action }) {
  return <div className="section-heading"><div><div className="eyebrow">{eyebrow}</div><h2>{title}</h2>{description ? <p>{description}</p> : null}</div>{action}</div>
}

export function SkillBadge({ children }) { return <span className="skill-badge">{children}</span> }

export function ProjectCard({ project, compact = false }) {
  return <article className={`project-card ${compact ? 'project-card-compact' : ''}`}>
    <div className="card-topline"><span className={`project-emblem emblem-${project.color}`}>{project.emoji}</span><Badge tone={project.status === 'Recruiting' ? 'success' : project.status === 'Planning' ? 'warning' : 'info'}>{project.status}</Badge></div>
    <div className="project-card-copy"><h3><Link to={`/projects/${project.id}`}>{project.name}</Link></h3><p>{project.description}</p></div>
    <div className="skills-row">{project.stack.map((skill) => <SkillBadge key={skill}>{skill}</SkillBadge>)}</div>
    <div className="card-meta"><span><Icon name="users" size={15} /> {project.contributors} contributors</span><span>{project.difficulty}</span></div>
    {!compact ? <div className="card-footer"><span className="owner-line"><span className={`mini-avatar avatar-${project.color}`}>{project.owner.slice(0, 1)}</span>{project.owner}</span><Link className="card-link" to={`/projects/${project.id}`}>View project <Icon name="arrow" size={15} /></Link></div> : null}
  </article>
}

export function DeveloperCard({ developer }) {
  return <article className="developer-card"><div className="developer-card-head"><Avatar user={developer} size="lg" /><span className="availability-dot" title={developer.availability}></span></div><h3><Link to={`/developers/${developer.username}`}>{developer.name}</Link></h3><p className="username">@{developer.username}</p><p className="developer-title">{developer.title}</p><div className="skills-row">{developer.skills.map((skill) => <SkillBadge key={skill}>{skill}</SkillBadge>)}</div><div className="developer-meta"><span>{developer.projects} projects</span><Badge tone="success">Available</Badge></div><Link className="text-link" to={`/developers/${developer.username}`}>View profile <Icon name="arrow" size={15} /></Link></article>
}

export function StatCard({ icon, label, value, trend }) { return <div className="stat-card"><div className="stat-icon"><Icon name={icon} size={18} /></div><div><p>{label}</p><strong>{value}</strong><span className="stat-trend">{trend}</span></div></div> }

export function ActivityItem({ activity }) { return <div className="activity-item"><Avatar user={activity} size="sm" /><div><p><strong>{activity.person}</strong> {activity.action}</p><span>{activity.time}</span></div></div> }

export function EmptyState({ title, description, action }) { return <div className="empty-state"><div className="empty-icon"><Icon name="bookmark" size={24} /></div><h3>{title}</h3><p>{description}</p>{action}</div> }

export function SearchInput({ value, onChange, placeholder = 'Search...' }) { return <label className="search-input"><Icon name="search" size={18} /><input value={value} onChange={(event) => onChange(event.target.value)} placeholder={placeholder} aria-label={placeholder} /></label> }
