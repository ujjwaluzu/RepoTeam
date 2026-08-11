import { BrowserRouter, Route, Routes } from 'react-router-dom'
import { AppLayout } from './components/Layout'
import { AuthPage, CreateProjectPage, DashboardPage, LandingPage, MyProjectsPage, NotFoundPage, ApplicationsPage, ProjectDetailsPage, ProjectsPage, TeamPage } from './pages'
import { DeveloperProfilePage, DevelopersPage, SettingsPage } from './connectedPages'
import './App.css'

function App() {
  return <BrowserRouter><Routes><Route path="/" element={<AppLayout><LandingPage /></AppLayout>} /><Route path="/login" element={<AuthPage />} /><Route path="/register" element={<AuthPage mode="register" />} /><Route path="/projects" element={<AppLayout><ProjectsPage /></AppLayout>} /><Route path="/projects/create" element={<CreateProjectPage />} /><Route path="/projects/:id" element={<AppLayout><ProjectDetailsPage /></AppLayout>} /><Route path="/developers" element={<AppLayout><DevelopersPage /></AppLayout>} /><Route path="/developers/:username" element={<AppLayout><DeveloperProfilePage /></AppLayout>} /><Route path="/dashboard" element={<DashboardPage />} /><Route path="/dashboard/projects" element={<MyProjectsPage />} /><Route path="/dashboard/applications" element={<ApplicationsPage />} /><Route path="/dashboard/team" element={<TeamPage />} /><Route path="/settings" element={<SettingsPage />} /><Route path="*" element={<AppLayout><NotFoundPage /></AppLayout>} /></Routes></BrowserRouter>
}

export default App
