import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { SignIn, SignUp, useAuth } from '@clerk/clerk-react'
import HomePage from './pages/public/HomePage'
import OverviewPage from './pages/dashboard/OverviewPage'
import DashboardLayout from './components/shared/DashboardLayout'
import ConversationsPage from './pages/dashboard/ConversationsPage'
import SettingsPage from './pages/dashboard/SettingsPage'
import OnboardingPage from './pages/dashboard/OnboardingPage'
import CheckoutPage from './pages/billing/CheckoutPage'
import SuccessPage from './pages/billing/SuccessPage'
import CancelPage from './pages/billing/CancelPage'

function ProtectedRoute({ children }) {
  const { isSignedIn, isLoaded } = useAuth()
  if (!isLoaded) return null
  if (!isSignedIn) return <Navigate to="/sign-in" />
  return children
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/sign-in/*" element={<SignIn routing="path" path="/sign-in" />} />
        <Route path="/sign-up/*" element={<SignUp routing="path" path="/sign-up" afterSignUpUrl="/billing/checkout" />} />
        <Route path="/dashboard/overview" element={
          <ProtectedRoute>
            <DashboardLayout>
              <OverviewPage />
            </DashboardLayout>
          </ProtectedRoute>
        } />
        <Route path="/dashboard/onboarding" element={
          <ProtectedRoute>
            <DashboardLayout>
              <OnboardingPage />
            </DashboardLayout>
          </ProtectedRoute>
        } />
        <Route path="/dashboard/conversations" element={
          <ProtectedRoute>
            <DashboardLayout>
              <ConversationsPage />
            </DashboardLayout>
          </ProtectedRoute>
        } />
        <Route path="/dashboard/settings" element={
          <ProtectedRoute>
            <DashboardLayout>
              <SettingsPage />
            </DashboardLayout>
          </ProtectedRoute>
        } />
        <Route path="/billing/success" element={<SuccessPage />} />
        <Route path="/billing/cancel" element={<CancelPage />} />
        <Route path="/billing/checkout" element={
          <ProtectedRoute>
            <CheckoutPage />
          </ProtectedRoute>
        } />
      </Routes>
    </BrowserRouter>
  )
}