import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { SignIn, SignUp, useAuth } from '@clerk/clerk-react'
import HomePage from './pages/public/HomePage'
import OverviewPage from './pages/dashboard/OverviewPage'
import DashboardLayout from './components/shared/DashboardLayout'
import ConversationsPage from './pages/dashboard/ConversationsPage'
import SettingsPage from './pages/dashboard/SettingsPage'
import OnboardingPage from './pages/dashboard/OnboardingPage'
import DemoPage from './pages/dashboard/DemoPage'
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
        <Route path="/sign-in/*" element={
          <div className="min-h-screen flex items-center justify-center">
            <SignIn routing="path" path="/sign-in" />
          </div>
        } />
        <Route path="/sign-up/*" element={
          <div className="min-h-screen flex items-center justify-center">
            <SignUp routing="path" path="/sign-up" afterSignUpUrl="/billing/checkout" />
          </div>
        } />
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
        <Route path="/dashboard/demo" element={
          <ProtectedRoute>
            <DashboardLayout>
              <DemoPage />
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