/**
 * App.jsx - Main Application with Role-Based Routing
 *
 * Architecture:
 * - AuthGuard: Blocks rendering until auth state is determined
 * - AdminRoute: Only allows admin users
 * - UserRoute: Only allows regular users
 * - PublicRoute: Only allows unauthenticated users
 *
 * Routes:
 * - /login - Public only
 * - /admin/* - Admin only
 * - /user - Regular users only
 * - / - Redirects based on role
 */

import { BrowserRouter, Routes, Route, Navigate, useLocation } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { Toaster } from "sonner";
import { AuthProvider, useAuth } from "./context/AuthContext";
import { ThemeProvider } from "./context/ThemeContext";

// Pages
import LandingPage from "./pages/LandingPage";
import LoginPage from "./pages/LoginPage";
import ChatPage from "./pages/ChatPage";
import AdminDashboard from "./pages/AdminDashboard";
import ExecutiveDashboardPage from "./pages/ExecutiveDashboardPage";
import TablePage from "./pages/TablePage";
import UploadPage from "./pages/UploadPage";
import ModelVisualizationPage from "./pages/ModelVisualizationPage";
import ReportsPage from "./pages/ReportsPage";
import ForecastComparisonPage from "./pages/ForecastComparisonPage";
import UserManagementPage from "./pages/UserManagementPage";

// Styles
import "./styles/dashboard.css";

// =============================================================================
// LOADING COMPONENT
// =============================================================================

function LoadingScreen() {
  const { t } = useTranslation();
  return (
    <div className="loading-screen" style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      height: '100vh',
      background: 'var(--bg-primary, #0a0a0f)',
      color: 'var(--text-secondary, #888)',
      fontSize: '14px',
    }}>
      <div style={{ textAlign: 'center' }}>
        <div className="loading-spinner" style={{
          width: '32px',
          height: '32px',
          border: '3px solid rgba(255,255,255,0.1)',
          borderTopColor: 'var(--accent, #6366f1)',
          borderRadius: '50%',
          animation: 'spin 1s linear infinite',
          margin: '0 auto 16px',
        }} />
        <div>{t('common.loading')}</div>
      </div>
      <style>{`
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}

// =============================================================================
// ROUTE GUARDS
// =============================================================================

/**
 * AuthGuard - Blocks all rendering until auth state is determined
 * This prevents flash of wrong content
 */
function AuthGuard({ children }) {
  const { isLoading } = useAuth();

  if (isLoading) {
    return <LoadingScreen />;
  }

  return children;
}

/**
 * PublicRoute - Only accessible when NOT authenticated
 * Redirects authenticated users to their appropriate dashboard
 */
function PublicRoute({ children }) {
  const { isAuthenticated, isAdmin } = useAuth();
  const location = useLocation();

  if (isAuthenticated) {
    // Redirect to appropriate dashboard
    const redirectTo = isAdmin ? '/admin' : '/user';
    return <Navigate to={redirectTo} replace state={{ from: location }} />;
  }

  return children;
}

/**
 * AdminRoute - Only accessible by admin users
 * Redirects non-admins to user area, unauthenticated to login
 */
function AdminRoute({ children }) {
  const { isAuthenticated, isAdmin } = useAuth();
  const location = useLocation();

  if (!isAuthenticated) {
    return <Navigate to="/" replace state={{ from: location }} />;
  }

  if (!isAdmin) {
    // Regular users go to user area
    return <Navigate to="/user" replace />;
  }

  return children;
}

/**
 * UserRoute - Only accessible by regular (non-admin) users
 * Redirects admins to admin area, unauthenticated to login
 */
function UserRoute({ children }) {
  const { isAuthenticated, isAdmin } = useAuth();
  const location = useLocation();

  if (!isAuthenticated) {
    return <Navigate to="/" replace state={{ from: location }} />;
  }

  if (isAdmin) {
    // Admins go to admin area
    return <Navigate to="/admin" replace />;
  }

  return children;
}

/**
 * RoleBasedRedirect - Redirects to appropriate area based on role
 * Used for catch-all routes
 */
function RoleBasedRedirect() {
  const { isAuthenticated, isAdmin } = useAuth();

  if (!isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  if (isAdmin) {
    return <Navigate to="/admin" replace />;
  }

  return <Navigate to="/user" replace />;
}

// =============================================================================
// ROUTES
// =============================================================================

function AppRoutes() {
  return (
    <Routes>
      {/* ============================================
          LANDING PAGE - Public (with auth modal)
          ============================================ */}
      <Route path="/" element={<LandingPage />} />

      {/* ============================================
          PUBLIC ROUTES
          ============================================ */}
      <Route
        path="/login"
        element={
          <PublicRoute>
            <LoginPage />
          </PublicRoute>
        }
      />

      {/* ============================================
          USER ROUTES - AI Chat
          ============================================ */}
      <Route
        path="/user"
        element={
          <UserRoute>
            <ChatPage />
          </UserRoute>
        }
      />

      {/* ============================================
          ADMIN ROUTES
          ============================================ */}
      <Route
        path="/admin"
        element={
          <AdminRoute>
            <ExecutiveDashboardPage />
          </AdminRoute>
        }
      />
      <Route
        path="/admin/forecast"
        element={
          <AdminRoute>
            <AdminDashboard />
          </AdminRoute>
        }
      />
      <Route
        path="/admin/users"
        element={
          <AdminRoute>
            <UserManagementPage />
          </AdminRoute>
        }
      />
      <Route
        path="/admin/table"
        element={
          <AdminRoute>
            <TablePage />
          </AdminRoute>
        }
      />
      <Route
        path="/admin/upload"
        element={
          <AdminRoute>
            <UploadPage />
          </AdminRoute>
        }
      />
      <Route
        path="/admin/compare"
        element={
          <AdminRoute>
            <ForecastComparisonPage />
          </AdminRoute>
        }
      />
      <Route
        path="/admin/reports"
        element={
          <AdminRoute>
            <ReportsPage />
          </AdminRoute>
        }
      />
      <Route
        path="/admin/model"
        element={
          <AdminRoute>
            <ModelVisualizationPage />
          </AdminRoute>
        }
      />

      {/* ============================================
          LEGACY ROUTES - Redirect to new paths
          These ensure old bookmarks/links still work
          ============================================ */}
      <Route path="/forecast" element={<Navigate to="/admin/forecast" replace />} />
      <Route path="/table" element={<Navigate to="/admin/table" replace />} />
      <Route path="/upload" element={<Navigate to="/admin/upload" replace />} />
      <Route path="/model" element={<Navigate to="/admin/model" replace />} />
      <Route path="/chat" element={<RoleBasedRedirect />} />

      {/* ============================================
          CATCH-ALL - Redirect based on role
          ============================================ */}
      <Route path="*" element={<RoleBasedRedirect />} />
    </Routes>
  );
}

// =============================================================================
// MAIN APP
// =============================================================================

export default function App() {
  return (
    <BrowserRouter>
      <ThemeProvider>
        <AuthProvider>
          <AuthGuard>
            <AppRoutes />
          </AuthGuard>
        </AuthProvider>
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: "var(--bg-secondary, #1a1a2e)",
              border: "1px solid var(--border, #2a2a3e)",
              color: "var(--text-primary, #e0e0e0)",
              fontSize: "14px",
            },
          }}
          theme="dark"
          richColors
          closeButton
        />
      </ThemeProvider>
    </BrowserRouter>
  );
}