import React, { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { 
  LayoutDashboard, Users, Heart, FolderOpen, BookOpen, 
  Calendar, DollarSign, Gift, FileText, AlertTriangle,
  UserCog, MessageCircle, ChevronLeft, ChevronRight,
  Shield, LogOut, Menu, X, LayoutGrid, Inbox, Clock, Home,
  CalendarDays, Bell, UserCheck, Receipt, BarChart3, CheckSquare, Truck,
  Crown, TrendingUp, Building, ConciergeBell, Landmark, Compass, WifiOff
} from "lucide-react";

import { api } from "@/api";
import crbclEmblem from "@/assets/crbcl-emblem.png";
import crbclLogoDark from "@/assets/crbcl-logo-dark.png";



const getStoredUser = () => {
  try {
    const s = localStorage.getItem("crbcl_current_user");
    return s ? JSON.parse(s) : null;
  } catch {
    return null;
  }
};

const getNavItems = (userRoles = [], userEmail = "", userPermissions = []) => {
  const normalizedRoles = (Array.isArray(userRoles) ? userRoles : [userRoles])
    .map((r) => (typeof r === "string" ? r : (r?.key || r?.name || r?.role || "")))
    .map((r) => String(r).toLowerCase().trim());
  const email = String(userEmail || "").toLowerCase().trim();
  const perms = new Set(
    (Array.isArray(userPermissions) ? userPermissions : [])
      .map((p) => String(p).toLowerCase().trim())
  );

  const isItAdmin =
    email === "admin@crbcl.ca" ||
    email.includes("admin") ||
    normalizedRoles.includes("it_admin") ||
    normalizedRoles.includes("admin") ||
    normalizedRoles.includes("administrator") ||
    normalizedRoles.includes("system administrator");

  const isCEO = normalizedRoles.includes("ceo");
  const isExecutive = normalizedRoles.includes("executive_director");
  const isDirector = normalizedRoles.includes("director_manager");
  const isBoardMember = normalizedRoles.includes("board_member");
  const isNavigator = normalizedRoles.includes("navigator");
  const isFrontDesk = normalizedRoles.includes("front_desk");
  const isSupervisor = normalizedRoles.includes("supervisor");
  const isHR = normalizedRoles.includes("hr_staff");
  const isCaseworker = normalizedRoles.includes("caseworker");
  const isOfficeCoordinator = normalizedRoles.includes("office_coordinator");

  // Capabilities
  const hasIntakeRead = perms.has("intake.read");
  const hasPublicIntakeRead = perms.has("public_intake.read");
  const hasIntakeApprove = perms.has("intake.approve");
  const hasHrRead = perms.has("hr.dashboard.read") || perms.has("hr.employee.read");
  const hasClientRead = perms.has("client.read");
  const hasCaseRead = perms.has("case.read");
  const hasOfficeCoordRead = perms.has("office_coordinator.dashboard.read") || perms.has("operations.request.read");

  // Board Member navigation: strictly restricted to governance oversight
  if (isBoardMember) {
    return [
      { label: "Board Overview", icon: LayoutDashboard, path: "/board" },
      { label: "Actions & Decisions", icon: CheckSquare, path: "/board?tab=actions" },
      { label: "Strategic Initiatives", icon: TrendingUp, path: "/board?tab=initiatives" },
      { label: "Performance & Risk", icon: BarChart3, path: "/board?tab=performance" },
      { label: "Department Reports", icon: FileText, path: "/board?tab=reports" },
    ];
  }

  const items = [];

  // Dedicated Portals strictly for the 3 authorized roles: IT Admin, CEO, and Executive Director
  if (isItAdmin) {
    items.push({ label: "Admin & IT Portal", icon: Shield, path: "/admin" });
  }
  if (isCEO) {
    items.push({ label: "CEO Dashboard", icon: Crown, path: "/ceo" });
  }
  if (isExecutive) {
    items.push({ label: "Executive Dashboard", icon: TrendingUp, path: "/executive" });
  }

  items.push(
    { label: "Offline Workspace", icon: WifiOff, path: "/offline-workspace" },
    { label: "My Schedule", icon: Calendar, path: "/schedule" },
    { label: "Team Calendar", icon: CalendarDays, path: "/schedule/team" },
    { label: "Staffing Facilitator", icon: UserCheck, path: "/staffing" },
    { label: "Team Dashboards", icon: LayoutGrid, path: "/teams" },
    { label: "Cases", icon: FolderOpen, path: "/cases" },
    { label: "Placement Homes", icon: Home, path: "/placement-homes" },
    { label: "Resource Team", icon: Building, path: "/resource-team" },
    { label: "Recruitment Pipeline", icon: Users, path: "/resource-team/recruitment" },
    { label: "Finance & Billing", icon: DollarSign, path: "/finance" },
    { label: "Reporting & Hub", icon: BarChart3, path: "/reports" },
    { label: "Quality Assurance", icon: CheckSquare, path: "/qa" },
    { label: "Fleet & Vehicles", icon: Truck, path: "/fleet" },
    { label: "Purchase Orders", icon: FileText, path: "/finance/requests" },
    { label: "Placement Invoices", icon: Receipt, path: "/finance/invoices" },
    { label: "Financial Ledger", icon: BookOpen, path: "/finance/ledger" },
    { label: "Clients", icon: Users, path: "/clients" },
    { label: "Families", icon: Heart, path: "/families" },
    { label: "Notifications", icon: Bell, path: "/notifications" },
    { label: "Programs", icon: BookOpen, path: "/programs" },
    { label: "Staff Directory", icon: Users, path: "/employees" },
    { label: "Housing Units", icon: Home, path: "/housing" },
    { label: "Facilities", icon: LayoutGrid, path: "/facilities" },
    { label: "IT Assets", icon: Shield, path: "/assets" },
    { label: "Volunteers", icon: UserCheck, path: "/volunteers" },
    { label: "Funding", icon: DollarSign, path: "/funding" },
    { label: "Donations", icon: Gift, path: "/donations" },
    { label: "Clinical Notes", icon: FileText, path: "/clinical-notes" },
    { label: "Incidents", icon: AlertTriangle, path: "/incidents" },
    { label: "Cultural Terminology", icon: BookOpen, path: "/terminology" },
    { label: "Ask Red Bear", icon: MessageCircle, path: "/ask-red-bear" },
  );

  return items;
};

export default function Sidebar() {
  const location = useLocation();
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [userRoles, setUserRoles] = useState(() => {
    const u = getStoredUser();
    return Array.isArray(u?.roles) ? u.roles : (u?.role ? [u.role] : []);
  });
  const [userEmail, setUserEmail] = useState(() => getStoredUser()?.email || "");
  const [userPermissions, setUserPermissions] = useState(() => {
    const u = getStoredUser();
    return Array.isArray(u?.permissions) ? u.permissions : [];
  });

  React.useEffect(() => {
    api.auth.me().then((u) => {
      if (u) {
        const roles = Array.isArray(u?.roles) ? u.roles : (u?.role ? [u.role] : []);
        setUserRoles(roles);
        setUserEmail(u?.email || "");
        setUserPermissions(Array.isArray(u?.permissions) ? u.permissions : []);
      }
    }).catch(() => {});
  }, []);

  const handleLogout = () => {
    const isItAdmin = window.location.pathname.startsWith("/admin") || userEmail === "admin@crbcl.ca" || userRoles.includes("it_admin") || userRoles.includes("admin");
    api.auth.logout(isItAdmin ? "/admin/login" : "/login");
  };

  const navContent = (
    <div className="flex flex-col h-full">
      {/* Logo */}
      <div className="p-3 border-b border-sidebar-border flex items-center justify-center min-h-[72px]">
        <Link
          to="/"
          className="group focus:outline-none flex items-center justify-center w-full transition-transform hover:scale-[1.02] duration-200"
          title="Chief Red Bear Children's Lodge"
        >
          {collapsed ? (
            <img
              src={crbclEmblem}
              alt="Chief Red Bear Children's Lodge"
              className="w-10 h-10 object-contain mx-auto transition-transform group-hover:scale-110"
            />
          ) : (
            <img
              src={crbclLogoDark}
              alt="Chief Red Bear Children's Lodge"
              className="h-16 w-auto max-w-[200px] object-contain mx-auto py-0.5"
            />
          )}
        </Link>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-3 space-y-0.5 overflow-y-auto scrollbar-thin">
        {getNavItems(userRoles, userEmail, userPermissions).map((item) => {
          const isActive = location.pathname === item.path || 
            (item.path !== "/" && location.pathname.startsWith(item.path));
          return (
            <Link
              key={`${item.label}-${item.path}`}
              to={item.path}
              onClick={() => setMobileOpen(false)}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-all duration-200 group
                ${isActive 
                  ? "bg-sidebar-primary text-sidebar-primary-foreground shadow-sm" 
                  : "text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
                }
              `}
            >
              <item.icon className={`w-[18px] h-[18px] flex-shrink-0 ${isActive ? "" : "opacity-70 group-hover:opacity-100"}`} />
              {!collapsed && <span className="truncate">{item.label}</span>}
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="p-3 border-t border-sidebar-border">
        <button 
          onClick={handleLogout}
          className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm text-sidebar-foreground/70 hover:bg-sidebar-accent hover:text-sidebar-accent-foreground w-full transition-colors"
        >
          <LogOut className="w-[18px] h-[18px] flex-shrink-0" />
          {!collapsed && <span>Sign Out</span>}
        </button>
      </div>
    </div>
  );

  return (
    <>
      {/* Mobile toggle */}
      <button 
        className="lg:hidden fixed top-4 left-4 z-50 p-2 bg-primary text-primary-foreground rounded-lg shadow-lg"
        onClick={() => setMobileOpen(!mobileOpen)}
      >
        {mobileOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
      </button>

      {/* Mobile overlay */}
      {mobileOpen && (
        <div 
          className="lg:hidden fixed inset-0 bg-black/50 z-40"
          onClick={() => setMobileOpen(false)}
        />
      )}

      {/* Mobile sidebar */}
      <aside className={`lg:hidden fixed top-0 left-0 h-full w-64 bg-sidebar z-50 transform transition-transform duration-300 ${mobileOpen ? "translate-x-0" : "-translate-x-full"}`}>
        {navContent}
      </aside>

      {/* Desktop sidebar */}
      <aside className={`hidden lg:flex flex-col bg-sidebar border-r border-sidebar-border transition-all duration-300 ${collapsed ? "w-[68px]" : "w-60"} relative h-screen sticky top-0`}>
        {navContent}
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="absolute -right-3 top-20 w-6 h-6 bg-primary text-primary-foreground rounded-full flex items-center justify-center shadow-md hover:scale-110 transition-transform"
        >
          {collapsed ? <ChevronRight className="w-3 h-3" /> : <ChevronLeft className="w-3 h-3" />}
        </button>
      </aside>
    </>
  );
}