import React, { useEffect } from 'react';
import { Outlet, Navigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';

const DefaultFallback = () => (
  <div className="fixed inset-0 flex items-center justify-center bg-background">
    <div className="w-8 h-8 border-4 border-purple-200 border-t-purple-700 rounded-full animate-spin"></div>
  </div>
);

export const isUserAdmin = (user) => {
  if (!user) return false;
  const email = String(user?.email || "").toLowerCase().trim();
  const roles = (Array.isArray(user?.roles) ? user.roles : (user?.role ? [user.role] : []))
    .map((r) => (typeof r === "string" ? r : (r?.key || r?.name || r?.role || "")))
    .map((r) => String(r).toLowerCase().trim());

  return (
    email === "admin@crbcl.ca" ||
    email.includes("admin") ||
    user?.role === "admin" ||
    user?.role === "it_admin" ||
    roles.includes("admin") ||
    roles.includes("it_admin") ||
    roles.includes("administrator") ||
    roles.includes("system administrator")
  );
};

export default function AdminProtectedRoute({ fallback = <DefaultFallback /> }) {
  const { user, isAuthenticated, isLoadingAuth, authChecked, checkUserAuth } = useAuth();

  useEffect(() => {
    if (!authChecked && !isLoadingAuth) {
      checkUserAuth();
    }
  }, [authChecked, isLoadingAuth, checkUserAuth]);

  if (isLoadingAuth || !authChecked) {
    return fallback;
  }

  // Not authenticated at all -> go directly to Admin Login
  if (!isAuthenticated || !user) {
    return <Navigate to="/admin/login" replace />;
  }

  // Authenticated as standard staff / supervisor / caseworker, BUT NOT an IT Admin
  // Strictly prevent access to /admin and redirect to /admin/login
  if (!isUserAdmin(user)) {
    return <Navigate to="/admin/login?reason=admin_required" replace />;
  }

  return <Outlet />;
}
