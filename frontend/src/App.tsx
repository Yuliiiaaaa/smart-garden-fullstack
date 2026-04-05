// src/App.tsx
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { LandingPage } from './components/LandingPage';
import { AuthPage } from './components/AuthPage';
import { Dashboard } from './components/Dashboard';
import { AnalysisPage } from './components/AnalysisPage';
import { ResultsPage } from './components/ResultsPage';
import { AnalyticsPage } from './components/AnalyticsPage';
import { HistoryPage } from './components/HistoryPage';
import { GardensManagementPage } from './components/GardensManagementPage';   // новый
import { AdminUsersPage } from './components/AdminUsersPage';                 // новый
import { Toaster } from './components/ui/sonner';
import { getAuthToken } from './services/apiConfig';
import { GardensPage } from './components/GardensPage';

// Компонент для проверки аутентификации
const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const token = getAuthToken();
  if (!token) return <Navigate to="/auth" replace />;
  return <>{children}</>;
};

// Компонент для проверки роли
const RoleRoute = ({ children, allowedRoles }: { children: React.ReactNode, allowedRoles: string[] }) => {
  const token = getAuthToken();
  const userStr = localStorage.getItem('user');
  const user = userStr ? JSON.parse(userStr) : null;

  if (!token || !user) return <Navigate to="/auth" replace />;
  if (!allowedRoles.includes(user.role)) return <Navigate to="/dashboard" replace />;
  return <>{children}</>;
};

export default function App() {
  return (
    <BrowserRouter>
      <div className="size-full">
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/auth" element={<AuthPage />} />

          {/* Защищённые маршруты (только авторизованные) */}
          <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
          <Route path="/analysis" element={<ProtectedRoute><AnalysisPage /></ProtectedRoute>} />
          <Route path="/results" element={<ProtectedRoute><ResultsPage /></ProtectedRoute>} />
          <Route path="/analytics" element={<ProtectedRoute><AnalyticsPage /></ProtectedRoute>} />
          <Route path="/history" element={<ProtectedRoute><HistoryPage /></ProtectedRoute>} />
          <Route path="/gardens" element={<RoleRoute allowedRoles={['manager', 'admin']}><GardensPage /></RoleRoute>} />
          {/* Маршруты с ролевыми ограничениями */}
          <Route
            path="/gardens/manage"
            element={
              <RoleRoute allowedRoles={['manager', 'admin']}>
                <GardensManagementPage />
              </RoleRoute>
            }
          />
          <Route
            path="/admin/users"
            element={
              <RoleRoute allowedRoles={['admin']}>
                <AdminUsersPage />
              </RoleRoute>
            }
          />

          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
        <Toaster />
      </div>
    </BrowserRouter>
  );
}