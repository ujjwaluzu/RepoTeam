import { useEffect, useState } from 'react'
import { Link, NavLink, useLocation } from 'react-router-dom'
import { ActivityItem, Avatar, Button, Icon, Logo } from './UI'
import { currentUser, activities } from '../data/mockData'
import { api } from '../api'

const publicLinks = [{ to: '/projects', label: 'Explore Projects' }, { to: '/developers', label: 'Developers' }, { to: '/#about', label: 'About' }]

export function Navbar() {
  const [open, setOpen] = useState(false)
  return <header className="site-header"><div className="container nav-inner"><Logo /><nav className={`main-nav ${open ? 'nav-open' : ''}`} aria-label="Main navigation">{publicLinks.map((link) => <NavLink key={link.label} to={link.to} onClick={() => setOpen(false)}>{link.label}</NavLink>)}<span className="nav-divider"></span><NavLink to="/login" onClick={() => setOpen(false)}>Log in</NavLink><Button to="/register" onClick={() => setOpen(false)} icon="arrow">Get started</Button></nav><button className="menu-button" onClick={() => setOpen(!open)} aria-label="Toggle navigation" aria-expanded={open}><Icon name={open ? 'close' : 'menu'} /></button></div></header>
}

export function Footer() {
  return <footer className="site-footer"><div className="container footer-grid"><div className="footer-brand"><Logo /><p>Build together. Find your team. Ship better.</p><div className="social-row"><a href="https://github.com" aria-label="GitHub"><Icon name="github" /></a><a href="#" aria-label="LinkedIn">in</a><a href="#" aria-label="X">𝕏</a></div></div><div><h4>Product</h4><Link to="/projects">Explore projects</Link><Link to="/developers">Find developers</Link><Link to="/projects/create">Create a project</Link></div><div><h4>Resources</h4><a href="#">Community guide</a><a href="#">Help center</a><a href="#">Changelog</a></div><div><h4>Company</h4><a href="#about">About RepoTeam</a><a href="#">Careers</a><a href="#">Contact</a></div></div><div className="container footer-bottom"><span>© 2026 RepoTeam. Built for people who build.</span><span>Made with care for the developer community.</span></div></footer>
}

export function AppLayout({ children }) { return <><Navbar />{children}<Footer /></> }

const sideLinks = [
  { to: '/dashboard', label: 'Overview', icon: 'grid', end: true },
  { to: '/dashboard/projects', label: 'My projects', icon: 'bookmark' },
  { to: '/projects', label: 'Discover', icon: 'search' },
  { to: '/dashboard/applications', label: 'Applications', icon: 'bell' },
  { to: '/dashboard/team', label: 'Team', icon: 'users' },
  { to: '/developers/alexrivera', label: 'Profile', icon: 'users' },
  { to: '/settings', label: 'Settings', icon: 'settings' },
]

export function DashboardLayout({ children, user: providedUser }) {
  const location = useLocation()
  const [open, setOpen] = useState(false)
  const [liveUser, setLiveUser] = useState(providedUser || null)
  const [pendingApplications, setPendingApplications] = useState(0)
  useEffect(() => { if (!providedUser) api('/api/auth/me/').then((response) => { if (response.authenticated) setLiveUser(response.user) }).catch(() => {}) }, [providedUser])
  useEffect(() => { api('/api/applications/?kind=received&status=pending').then((response) => setPendingApplications(response.count)).catch(() => {}) }, [])
  const user = liveUser || currentUser
  const displayName = user.display_name || user.name || user.username
  const userForAvatar = { ...user, name: displayName, initials: displayName.split(' ').map((part) => part[0]).join('').slice(0, 2).toUpperCase() }
  return <div className="dashboard-shell"><aside className={`dashboard-sidebar ${open ? 'sidebar-open' : ''}`}><div className="sidebar-brand"><Logo /><button className="sidebar-close" onClick={() => setOpen(false)} aria-label="Close sidebar"><Icon name="close" /></button></div><div className="sidebar-label">Workspace</div><nav className="sidebar-nav">{sideLinks.map((link) => <NavLink key={link.label} to={link.to} end={link.end} className={({ isActive }) => isActive || (link.label === 'Discover' && location.pathname.startsWith('/projects')) ? 'active' : ''} onClick={() => setOpen(false)}><Icon name={link.icon} size={18} /><span>{link.label}</span>{link.label === 'Applications' && pendingApplications ? <span className="nav-count">{pendingApplications}</span> : null}</NavLink>)}</nav><div className="sidebar-bottom"><div className="user-mini"><Avatar user={userForAvatar} size="sm" /><div><strong>{displayName}</strong><span>@{user.username}</span></div><Icon name="chevron" size={15} /></div></div></aside><div className="dashboard-content"><div className="dashboard-mobilebar"><button className="menu-button" onClick={() => setOpen(true)} aria-label="Open sidebar"><Icon name="menu" /></button><Logo /><button className="icon-button" aria-label="Notifications"><Icon name="bell" /></button></div>{children}</div></div>
}

export function ActivityPanel({ title = 'Recent activity', items = activities }) { return <div className="panel activity-panel"><div className="panel-heading"><h3>{title}</h3><Link to="/dashboard">View all</Link></div><div>{items.map((activity, index) => <ActivityItem activity={activity} key={`${activity.person}-${index}`} />)}</div></div> }
