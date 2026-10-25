import { Navigate, Route, Routes } from 'react-router-dom';
import { AuthProvider } from './hooks/AuthContext';
import { useAuth } from './hooks/useAuth';
import { LoginPage, RegisterPage } from './pages/AuthPages';
import InventoryPage from './pages/InventoryPage';

function ProtectedInventory() {
  const { session } = useAuth();
  return session ? <InventoryPage /> : <Navigate to="/login" replace />;
}

function AppRoutes() {
  const { session } = useAuth();
  return <Routes>
    <Route path="/login" element={session ? <Navigate to="/inventory" replace /> : <LoginPage />} />
    <Route path="/register" element={<RegisterPage />} />
    <Route path="/inventory" element={<ProtectedInventory />} />
    <Route path="*" element={<Navigate to={session ? '/inventory' : '/login'} replace />} />
  </Routes>;
}

export default function App() {
  return <AuthProvider><AppRoutes /></AuthProvider>;
}
