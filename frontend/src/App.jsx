import { BrowserRouter, Route, Routes } from 'react-router-dom'
import { AppLayout } from './components/Layout'
import { LandingPage, NotFoundPage } from './pages'
import { ConnectedApplicationsPage, ConnectedAuthPage, ConnectedDashboardPage, ConnectedMyProjectsPage, ConnectedTeamPage } from './connectedPages'
import { DeveloperProfilePage, DevelopersPage, SettingsPage } from './connectedPages'
import { ConnectedCreateProjectPage, ConnectedProjectDetailsPageLive, ConnectedProjectsPage } from './connectedPages'
import './App.css'

function App() {
  return <BrowserRouter><Routes><Route path="/" element={<AppLayout><LandingPage /></AppLayout>} /><Route path="/login" element={<ConnectedAuthPage />} /><Route path="/register" element={<ConnectedAuthPage mode="register" />} /><Route path="/projects" element={<AppLayout><ConnectedProjectsPage /></AppLayout>} /><Route path="/projects/create" element={<ConnectedCreateProjectPage />} /><Route path="/projects/:id" element={<AppLayout><ConnectedProjectDetailsPageLive /></AppLayout>} /><Route path="/developers" element={<AppLayout><DevelopersPage /></AppLayout>} /><Route path="/developers/:username" element={<AppLayout><DeveloperProfilePage /></AppLayout>} /><Route path="/dashboard" element={<ConnectedDashboardPage />} /><Route path="/dashboard/projects" element={<ConnectedMyProjectsPage />} /><Route path="/dashboard/applications" element={<ConnectedApplicationsPage />} /><Route path="/dashboard/team" element={<ConnectedTeamPage />} /><Route path="/settings" element={<SettingsPage />} /><Route path="*" element={<AppLayout><NotFoundPage /></AppLayout>} /></Routes></BrowserRouter>
}

export default App
