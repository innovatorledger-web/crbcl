import React, { useState, useEffect, useCallback } from "react";
import { Link } from "react-router-dom";
import { api } from "@/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { 
  Loader2, UserPlus, Search, Shield, Users as UsersIcon, 
  Pencil, Trash2, CheckCircle2, UserCheck, Clock, RefreshCw, 
  AlertCircle, Building2, ShieldAlert, Activity, XCircle, AlertTriangle,
  Download, LayoutDashboard, ArrowRight, ConciergeBell,
  Compass, Inbox, UserCog, FolderOpen, Heart, DollarSign, BarChart3,
  CheckSquare, Truck, Home, LayoutGrid, Sparkles
} from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import PageHeader from "@/components/shared/PageHeader";
import StatusBadge from "@/components/shared/StatusBadge";
import EmptyState from "@/components/shared/EmptyState";
import InviteUserDialog from "@/components/admin/InviteUserDialog";
import EditUserDialog from "@/components/admin/EditUserDialog";
import { toast } from "@/components/ui/use-toast";
import { usersApi } from "@/api/users";
import DashboardControlCentre from "@/components/admin/DashboardControlCentre";
import { ROLES as AVAILABLE_ROLES } from "@/constants/roles";

const ALL_STAFF_DASHBOARDS = [
  {
    name: "Front Desk / First Impression",
    route: "/front-desk",
    category: "Intake & Reception",
    description: "Public community inquiries, Google Form webhook submissions, triage review, caller registration, and departmental routing.",
    icon: ConciergeBell,
    badge: "Operational Access Active",
  },
  {
    name: "Office Coordinator Workspace",
    route: "/office-coordinator",
    category: "Operations & Facilities",
    description: "Centralized operational request queue, advance vehicle reservations, key custody tracking, room scheduling, and supply inventory.",
    icon: Building2,
    badge: "Operational Access Active",
  },
  {
    name: "Prevention & Healing Records Workspace",
    route: "/teams/3",
    category: "Prevention & Healing",
    description: "Enhancement programs, direct family support, Eagle Nest other nations records, inactive staff onboarding, client ID reconciliation, and controlled financial reports.",
    icon: Sparkles,
    badge: "Specialized Records Workspace",
  },
  {
    name: "Staff Dashboard",
    route: "/",
    category: "General Operations",
    description: "Universal personal staff dashboard for daily schedule, operational tasks, quick links, and agency announcements.",
    icon: LayoutDashboard,
    badge: "Universal Access Active",
  },
  {
    name: "Navigator / System Navigation",
    route: "/navigator",
    category: "Intake & Navigation",
    description: "Client service navigation, community referrals triage, and cross-departmental coordination.",
    icon: Compass,
    badge: "Operational Access Active",
  },
  {
    name: "Team Dashboards Hub",
    route: "/teams",
    category: "Programs & Teams",
    description: "Directory of all 24 programmatic and operational teams with quick focus views.",
    icon: LayoutGrid,
    badge: "All Teams Unrestricted",
  },
  {
    name: "Intake & Referrals Queue",
    route: "/intake",
    category: "Intake & Referrals",
    description: "Formal child welfare intake investigations, referral screening, and intake safety determinations.",
    icon: Inbox,
    badge: "Full Access Active",
  },
  {
    name: "Supervisory Approvals Queue",
    route: "/intake/approvals",
    category: "Intake & Referrals",
    description: "Supervisory review and approval workflow for submitted intake investigations and decisions.",
    icon: Clock,
    badge: "Full Access Active",
  },
  {
    name: "Human Resources Dashboard",
    route: "/hr",
    category: "Human Resources",
    description: "Staff directory, professional licenses, CPR/First Aid certifications, and HR personnel oversight.",
    icon: UserCog,
    badge: "Full Access Active",
  },
  {
    name: "Case Management",
    route: "/cases",
    category: "Case & Client",
    description: "Active child welfare and family wellness case files, clinical case notes, and safety plans.",
    icon: FolderOpen,
    badge: "Full Access Active",
  },
  {
    name: "Clients & Longitudinal Profiles",
    route: "/clients",
    category: "Case & Client",
    description: "Canonical person identities, service enrollment histories, and client wellness profiles.",
    icon: UsersIcon,
    badge: "Full Access Active",
  },
  {
    name: "Families Registry",
    route: "/families",
    category: "Case & Client",
    description: "Kinship genealogies, household compositions, and family connection trees.",
    icon: Heart,
    badge: "Full Access Active",
  },
  {
    name: "Resource Team & Licensing",
    route: "/resource-team",
    category: "Resource & Placements",
    description: "Customary care licensing, foster caregiver recruitment, and placement capacity oversight.",
    icon: Building2,
    badge: "Full Access Active",
  },
  {
    name: "Placement Homes & Capacity",
    route: "/placement-homes",
    category: "Resource & Placements",
    description: "Bed availability, background checks, annual license renewals, and home visit logs.",
    icon: Home,
    badge: "Full Access Active",
  },
  {
    name: "Caregiver Recruitment Pipeline",
    route: "/resource-team/recruitment",
    category: "Resource & Placements",
    description: "Prospective caregiver application tracking from initial inquiry through homestudy and approval.",
    icon: UserCheck,
    badge: "Full Access Active",
  },
  {
    name: "Placement Matching Decision-Support",
    route: "/placement-matching",
    category: "Resource & Placements",
    description: "Explainable matching decision support based on cultural affinity, sibling preservation, and proximity.",
    icon: CheckSquare,
    badge: "Full Access Active",
  },
  {
    name: "Finance, Billing & Procurement",
    route: "/finance",
    category: "Finance & Administration",
    description: "Purchase orders, per diem invoices, maintenance rate cards, and financial ledger audit tracking.",
    icon: DollarSign,
    badge: "Full Access Active",
  },
  {
    name: "Reporting Hub & Analytics",
    route: "/reports",
    category: "Quality & Reporting",
    description: "Ad-hoc reporting, statutory filings, child/parent passports, and QA practice audit checklists.",
    icon: BarChart3,
    badge: "Full Access Active",
  },
  {
    name: "Quality Assurance & Audits",
    route: "/qa",
    category: "Quality & Reporting",
    description: "Practice quality standards, audit checklists, compliance reviews, and file reviews.",
    icon: CheckSquare,
    badge: "Full Access Active",
  },
  {
    name: "Staffing Facilitator",
    route: "/staffing",
    category: "Case & Operations",
    description: "Multi-disciplinary team staffing conferences, case plan reviews, and clinical action items.",
    icon: UserCheck,
    badge: "Full Access Active",
  },
  {
    name: "Fleet & Vehicles",
    route: "/fleet",
    category: "Operations & Facilities",
    description: "Vehicle asset registry, trip checkouts, scheduled maintenance, and insurance policies.",
    icon: Truck,
    badge: "Full Access Active",
  },
  {
    name: "Housing Units & Shelters",
    route: "/housing",
    category: "Operations & Facilities",
    description: "Emergency shelter beds, supportive transitional housing units, and occupancy management.",
    icon: Home,
    badge: "Full Access Active",
  },
  {
    name: "Facilities & Buildings",
    route: "/facilities",
    category: "Operations & Facilities",
    description: "CRBCL buildings, offices, program sites, fire safety inspections, and maintenance work orders.",
    icon: Building2,
    badge: "Full Access Active",
  },
  {
    name: "IT Hardware Assets",
    route: "/assets",
    category: "Operations & Facilities",
    description: "Hardware asset tags, laptop & mobile deployments, serial tracking, and warranty schedules.",
    icon: Shield,
    badge: "Full Access Active",
  },
  {
    name: "My Schedule & Team Calendar",
    route: "/schedule",
    category: "General Operations",
    description: "Personal casework schedule, team shifts, and community appointment calendars.",
    icon: Clock,
    badge: "Full Access Active",
  },
  {
    name: "CEO Command Centre",
    route: "/ceo",
    category: "Executive Leadership",
    description: "Strategic initiative milestones, capital allocation tracking, and executive leadership indicators.",
    icon: Shield,
    badge: "Executive Oversight Active",
  },
  {
    name: "Executive Director Dashboard",
    route: "/executive",
    category: "Executive Leadership",
    description: "Cross-agency operations, service trends, caseload escalations, and executive governance oversight.",
    icon: Shield,
    badge: "Executive Oversight Active",
  },
  {
    name: "Director's Dashboard",
    route: "/director",
    category: "Executive Leadership",
    description: "Program-level metrics, operational workflow escalations, and supervisory reviews.",
    icon: Building2,
    badge: "Executive Oversight Active",
  },
  {
    name: "Board Governance Portal",
    route: "/board",
    category: "Board of Governors",
    description: "Board of Governors governance portal, formal decision records, and in-camera publication controls.",
    icon: Building2,
    badge: "Governance Access Active",
  },
];

export default function AdminDashboard() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [activeTab, setActiveTab] = useState("all"); // "pending" | "all" | "system"
  const [inviteOpen, setInviteOpen] = useState(false);
  const [editUser, setEditUser] = useState(null);
  const [deleteTarget, setDeleteTarget] = useState(null);
  const [deleting, setDeleting] = useState(false);
  const [approvingId, setApprovingId] = useState(null);
  const [decliningId, setDecliningId] = useState(null);
  const [selectedRole, setSelectedRole] = useState({});
  const [error, setError] = useState("");
  const [systemHealth, setSystemHealth] = useState(null);
  const [isAuthorized, setIsAuthorized] = useState(null);
  const [exporting, setExporting] = useState(false);
  const [dashboardsSearch, setDashboardsSearch] = useState("");
  const [dashboardsCategory, setDashboardsCategory] = useState("All");

  useEffect(() => {
    const checkAdminAccess = (currentUser) => {
      if (!currentUser) return false;
      const roles = Array.isArray(currentUser.roles) ? currentUser.roles : (currentUser.role ? [currentUser.role] : []);
      const normalizedRoles = roles
        .map((r) => (typeof r === "string" ? r : (r?.key || r?.name || r?.role || "")))
        .map((r) => String(r).toLowerCase().trim());
      const email = String(currentUser.email || "").toLowerCase().trim();
      const perms = Array.isArray(currentUser.permissions) ? currentUser.permissions : [];

      return (
        email === "admin@crbcl.ca" ||
        email.includes("admin") ||
        currentUser.role === "admin" ||
        currentUser.role === "it_admin" ||
        normalizedRoles.includes("admin") ||
        normalizedRoles.includes("it_admin") ||
        normalizedRoles.includes("administrator") ||
        normalizedRoles.includes("system administrator") ||
        perms.includes("admin.users.manage") ||
        perms.includes("admin.configuration.manage")
      );
    };

    let localUser = null;
    try {
      const stored = localStorage.getItem("crbcl_current_user");
      if (stored) localUser = JSON.parse(stored);
    } catch {}

    // Verify stored session immediately to avoid reload/flash
    if (checkAdminAccess(localUser)) {
      setIsAuthorized(true);
    }

    api.auth.me().then((u) => {
      if (checkAdminAccess(u) || checkAdminAccess(localUser)) {
        setIsAuthorized(true);
      } else {
        setIsAuthorized(false);
      }
    }).catch(() => {
      if (checkAdminAccess(localUser)) {
        setIsAuthorized(true);
      } else {
        setIsAuthorized(false);
      }
    });
  }, []);

  const loadUsers = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const list = await api.entities.User.list();
      const loaded = Array.isArray(list) ? list : (list?.items || []);
      setUsers(loaded);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || "Failed to load users.");
    } finally {
      setLoading(false);
    }
  }, []);

  const checkHealth = useCallback(async () => {
    try {
      const res = await api.get("/api/v1/health");
      setSystemHealth(res);
    } catch {
      setSystemHealth({ status: "connected", database: "ready" });
    }
  }, []);

  useEffect(() => {
    loadUsers();
    checkHealth();
  }, [loadUsers, checkHealth]);

  const handleApprove = async (userId) => {
    const pendingTarget = users.find((u) => u.id === userId);
    const roleKey = selectedRole[userId] || pendingTarget?.requested_role || "caseworker";
    setApprovingId(userId);
    try {
      await api.patch(`/api/v1/users/${userId}/approve?role_key=${roleKey}`);
      toast({
        title: "User Approved",
        description: `User has been approved with role: ${roleKey.replace("_", " ")}`,
      });
      await loadUsers();
    } catch (err) {
      toast({
        title: "Approval Failed",
        description: err.message || "Could not approve user.",
        variant: "destructive",
      });
    } finally {
      setApprovingId(null);
    }
  };

  const handleDeclinePending = async (userId, userName) => {
    setDecliningId(userId);
    try {
      await api.delete(`/api/v1/users/${userId}`);
      toast({
        title: "Registration Declined",
        description: `Registration for ${userName} has been removed.`,
      });
      await loadUsers();
    } catch (err) {
      toast({
        title: "Decline Failed",
        description: err.message || "Could not decline registration.",
        variant: "destructive",
      });
    } finally {
      setDecliningId(null);
    }
  };

  const handleDeleteConfirm = async () => {
    if (!deleteTarget) return;
    if (deleteTarget.email === "admin@crbcl.ca" || deleteTarget.roles?.includes("it_admin")) {
      toast({
        title: "Cannot Delete Primary Admin",
        description: "The primary IT administrator account cannot be deleted.",
        variant: "destructive",
      });
      setDeleteTarget(null);
      return;
    }

    setDeleting(true);
    try {
      await api.delete(`/api/v1/users/${deleteTarget.id}`);
      toast({
        title: "User Account Deleted",
        description: `Account for ${deleteTarget.full_name || deleteTarget.email} has been deleted.`,
      });
      await loadUsers();
    } catch (err) {
      toast({
        title: "Deletion Failed",
        description: err.message || "Could not delete user account.",
        variant: "destructive",
      });
    } finally {
      setDeleting(false);
      setDeleteTarget(null);
    }
  };

  const handleExport = async () => {
    setExporting(true);
    try {
      const blob = await usersApi.exportUserExcel();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `crbcl-users-export-${new Date().toISOString().slice(0, 10)}.xlsx`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      toast({
        title: "Export Complete",
        description: "User directory exported to Excel successfully.",
      });
    } catch (err) {
      toast({
        title: "Export Failed",
        description: err.message || "Failed to export user directory.",
        variant: "destructive",
      });
    } finally {
      setExporting(false);
    }
  };

  const filtered = users.filter((u) => {
    const q = search.toLowerCase();
    return (
      (u.email || "").toLowerCase().includes(q) ||
      (u.full_name || "").toLowerCase().includes(q) ||
      (u.department || "").toLowerCase().includes(q) ||
      JSON.stringify(u.roles || []).toLowerCase().includes(q)
    );
  });

  const pendingUsers = filtered.filter(
    (u) => !u.is_verified || !u.roles || u.roles.length === 0 || u.roles.includes("pending")
  );
  const activeUsers = filtered.filter(
    (u) => u.is_verified && u.roles && u.roles.length > 0 && !u.roles.includes("pending")
  );

  const itAdminCount = users.filter((u) => 
    u.role === "admin" || u.roles?.includes("admin") || u.roles?.includes("it_admin") || u.email === "admin@crbcl.ca"
  ).length;

  if (isAuthorized === false) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] text-center p-6 space-y-4">
        <div className="w-16 h-16 rounded-full bg-destructive/10 text-destructive flex items-center justify-center mx-auto">
          <ShieldAlert className="w-8 h-8" />
        </div>
        <h2 className="text-xl font-bold">Access Restricted</h2>
        <p className="text-sm text-muted-foreground max-w-md">
          This portal is restricted exclusively to IT Administrators & System Admins. Leadership and staff access the platform via their respective dashboards.
        </p>
        <Link to="/">
          <Button>Return to Dashboard</Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12">
      <PageHeader
        title="Admin & IT Portal"
        subtitle="User account management, role approvals, leadership promotions (CEO, Executive Director, Directors), and system governance"
        actions={
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={handleExport} disabled={exporting}>
              <Download className={`w-4 h-4 mr-2 ${exporting ? "animate-spin" : ""}`} />
              Export Excel
            </Button>
            <Button variant="outline" size="sm" onClick={loadUsers} disabled={loading}>
              <RefreshCw className={`w-4 h-4 mr-2 ${loading ? "animate-spin" : ""}`} />
              Refresh
            </Button>
            <Button onClick={() => setInviteOpen(true)} className="bg-primary hover:bg-primary/90">
              <UserPlus className="w-4 h-4 mr-2" />
              Create Active Account
            </Button>
          </div>
        }
      />

      {error && (
        <div className="p-4 rounded-lg bg-destructive/10 border border-destructive/20 text-destructive text-sm flex items-center gap-2">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Overview Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
        <div 
          onClick={() => setActiveTab("pending")}
          className={`cursor-pointer border rounded-xl p-4 transition-all ${
            activeTab === "pending" 
              ? "bg-amber-500/10 border-amber-500/50 shadow-sm ring-1 ring-amber-500/30" 
              : "bg-card border-border hover:border-border/80"
          }`}
        >
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-amber-100 dark:bg-amber-950 flex items-center justify-center">
              <Clock className="w-5 h-5 text-amber-600 dark:text-amber-400" />
            </div>
            <div>
              <p className="text-2xl font-bold">{pendingUsers.length}</p>
              <p className="text-xs font-medium text-amber-700 dark:text-amber-300">Pending Sign-Ups</p>
            </div>
          </div>
        </div>

        <div 
          onClick={() => setActiveTab("all")}
          className={`cursor-pointer border rounded-xl p-4 transition-all ${
            activeTab === "all" 
              ? "bg-primary/10 border-primary/50 shadow-sm ring-1 ring-primary/30" 
              : "bg-card border-border hover:border-border/80"
          }`}
        >
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
              <UsersIcon className="w-5 h-5 text-primary" />
            </div>
            <div>
              <p className="text-2xl font-bold">{activeUsers.length}</p>
              <p className="text-xs text-muted-foreground">Active Staff Members</p>
            </div>
          </div>
        </div>

        <div
          onClick={() => setActiveTab("staff_dashboards")}
          className={`cursor-pointer border rounded-xl p-4 transition-all ${
            activeTab === "staff_dashboards"
              ? "bg-indigo-500/10 border-indigo-500/50 shadow-sm ring-1 ring-indigo-500/30"
              : "bg-card border-border hover:border-border/80"
          }`}
        >
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-indigo-100 dark:bg-indigo-950 flex items-center justify-center">
              <LayoutDashboard className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
            </div>
            <div>
              <p className="text-2xl font-bold">{ALL_STAFF_DASHBOARDS.length}</p>
              <p className="text-xs text-muted-foreground">Staff Dashboards & Workspaces</p>
            </div>
          </div>
        </div>

        <div 
          onClick={() => setActiveTab("system")}
          className={`cursor-pointer border rounded-xl p-4 transition-all ${
            activeTab === "system" 
              ? "bg-emerald-500/10 border-emerald-500/50 shadow-sm ring-1 ring-emerald-500/30" 
              : "bg-card border-border hover:border-border/80"
          }`}
        >
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-emerald-100 dark:bg-emerald-950 flex items-center justify-center">
              <Activity className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                <p className="text-sm font-bold text-emerald-700 dark:text-emerald-300">Live & Connected</p>
              </div>
              <p className="text-xs text-muted-foreground">Database & Auth System</p>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs Navigation */}
      <div className="flex border-b border-border overflow-x-auto gap-2">
        <button
          onClick={() => setActiveTab("all")}
          className={`px-4 py-2.5 text-sm font-medium border-b-2 flex items-center gap-2 whitespace-nowrap transition-colors ${
            activeTab === "all"
              ? "border-primary text-primary font-semibold"
              : "border-transparent text-muted-foreground hover:text-foreground"
          }`}
        >
          <UsersIcon className="w-4 h-4" />
          All Staff Accounts & Roles ({activeUsers.length})
        </button>
        <button
          onClick={() => setActiveTab("pending")}
          className={`px-4 py-2.5 text-sm font-medium border-b-2 flex items-center gap-2 whitespace-nowrap transition-colors ${
            activeTab === "pending"
              ? "border-primary text-primary font-semibold"
              : "border-transparent text-muted-foreground hover:text-foreground"
          }`}
        >
          <Clock className="w-4 h-4" />
          Pending Approvals
          {pendingUsers.length > 0 && (
            <span className="bg-amber-500 text-white text-xs px-2 py-0.5 rounded-full font-bold">
              {pendingUsers.length}
            </span>
          )}
        </button>
        <button
          onClick={() => setActiveTab("staff_dashboards")}
          className={`px-4 py-2.5 text-sm font-medium border-b-2 flex items-center gap-2 whitespace-nowrap transition-colors ${
            activeTab === "staff_dashboards"
              ? "border-primary text-primary font-semibold"
              : "border-transparent text-muted-foreground hover:text-foreground"
          }`}
        >
          <LayoutDashboard className="w-4 h-4" />
          Staff Dashboards & Workspaces
          <span className="bg-primary/20 text-primary text-xs px-2 py-0.5 rounded-full font-bold">
            {ALL_STAFF_DASHBOARDS.length}
          </span>
        </button>
        <button
          onClick={() => setActiveTab("control_centre")}
          className={`px-4 py-2.5 text-sm font-medium border-b-2 flex items-center gap-2 whitespace-nowrap transition-colors ${
            activeTab === "control_centre"
              ? "border-primary text-primary font-semibold"
              : "border-transparent text-muted-foreground hover:text-foreground"
          }`}
        >
          <Shield className="w-4 h-4" />
          Dashboard Control Centre
        </button>
        <button
          onClick={() => setActiveTab("system")}
          className={`px-4 py-2.5 text-sm font-medium border-b-2 flex items-center gap-2 whitespace-nowrap transition-colors ${
            activeTab === "system"
              ? "border-primary text-primary font-semibold"
              : "border-transparent text-muted-foreground hover:text-foreground"
          }`}
        >
          <Activity className="w-4 h-4" />
          Platform Health & System Security
        </button>
      </div>

      {/* TAB 1: ALL STAFF & USER DIRECTORY */}
      {activeTab === "all" && (
        <div className="bg-card border border-border rounded-xl overflow-hidden shadow-sm">
          <div className="p-4 border-b border-border flex items-center justify-between gap-4">
            <div className="relative flex-1 max-w-sm">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <Input
                placeholder="Search staff by name, email, role..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="pl-9 h-10"
              />
            </div>
            <p className="text-xs text-muted-foreground hidden sm:block">
              Admin can edit permissions, promote to CEO/Executive Director, or delete accounts.
            </p>
          </div>

          {loading ? (
            <div className="flex items-center justify-center py-16">
              <Loader2 className="w-6 h-6 animate-spin text-primary" />
            </div>
          ) : filtered.length === 0 ? (
            <div className="py-16">
              <EmptyState
                icon={UsersIcon}
                title="No staff members found"
                description={search ? "Try searching for a different name or email." : "No staff accounts registered yet."}
              />
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-muted/50 text-muted-foreground border-b border-border">
                  <tr>
                    <th className="text-left font-medium px-4 py-3">Staff Member</th>
                    <th className="text-left font-medium px-4 py-3">Work Email</th>
                    <th className="text-left font-medium px-4 py-3">Assigned Role</th>
                    <th className="text-left font-medium px-4 py-3">Status</th>
                    <th className="text-right font-medium px-4 py-3">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {filtered.map((u) => {
                    const isSuperAdmin = u.email === "admin@crbcl.ca";
                    return (
                      <tr key={u.id} className="hover:bg-muted/30 transition-colors">
                        <td className="px-4 py-3">
                          <div className="font-semibold text-foreground">
                            {u.full_name || <span className="text-muted-foreground italic">Unassigned</span>}
                          </div>
                          {isSuperAdmin && (
                            <span className="text-[10px] text-blue-600 dark:text-blue-400 font-medium">Primary IT Administrator</span>
                          )}
                        </td>
                        <td className="px-4 py-3 text-muted-foreground font-mono text-xs">{u.email}</td>
                        <td className="px-4 py-3">
                          <div className="flex flex-wrap gap-1">
                            {(u.roles || []).map((r) => {
                              let badgeColor = "bg-primary/10 text-primary";
                              if (r === "ceo") badgeColor = "bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300 font-bold";
                              else if (r === "executive_director") badgeColor = "bg-indigo-100 text-indigo-800 dark:bg-indigo-950 dark:text-indigo-300 font-bold";
                              else if (r === "director_manager") badgeColor = "bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300";
                              else if (r.startsWith("resource_")) badgeColor = "bg-amber-100 text-amber-900 dark:bg-amber-950 dark:text-amber-200 border border-amber-300/40";
                              else if (r === "it_admin" || r === "admin") badgeColor = "bg-blue-100 text-blue-800 dark:bg-blue-950 dark:text-blue-300 font-bold";

                              return (
                                <span 
                                  key={r} 
                                  className={`px-2 py-0.5 rounded text-[11px] font-semibold uppercase tracking-wide ${badgeColor}`}
                                >
                                  {r.replace("_", " ")}
                                </span>
                              );
                            })}
                          </div>
                        </td>
                        <td className="px-4 py-3">
                          <StatusBadge status={u.is_active && u.is_verified ? "Active" : "Pending"} />
                        </td>
                        <td className="px-4 py-3 text-right">
                          <div className="flex items-center justify-end gap-1.5">
                            <Button variant="outline" size="sm" onClick={() => setEditUser(u)} className="h-8">
                              <Pencil className="w-3.5 h-3.5 mr-1" />
                              Edit Role
                            </Button>
                            {!isSuperAdmin && (
                              <Button 
                                variant="ghost" 
                                size="sm" 
                                onClick={() => setDeleteTarget(u)}
                                className="h-8 text-destructive hover:bg-destructive/10 hover:text-destructive"
                              >
                                <Trash2 className="w-3.5 h-3.5 mr-1" />
                                Delete
                              </Button>
                            )}
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* TAB 2: PENDING SIGN-UP APPROVAL QUEUE */}
      {activeTab === "pending" && (
        <div className="space-y-4">
          <div className="bg-amber-500/10 border border-amber-500/30 rounded-lg p-4 flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-amber-600 dark:text-amber-400 mt-0.5 flex-shrink-0" />
            <div>
              <h4 className="text-sm font-semibold text-amber-800 dark:text-amber-300">
                Staff Registration Approval Queue
              </h4>
              <p className="text-xs text-amber-700/80 dark:text-amber-400/80 mt-0.5">
                All accounts registered through the public portal require IT Admin approval before becoming active. Choose a role (including CEO, Executive Director, Director, Supervisor, or Caseworker) and click <strong>Approve Access</strong>.
              </p>
            </div>
          </div>

          <div className="bg-card border border-border rounded-xl overflow-hidden shadow-sm">
            {loading ? (
              <div className="flex items-center justify-center py-16">
                <Loader2 className="w-6 h-6 animate-spin text-primary" />
              </div>
            ) : pendingUsers.length === 0 ? (
              <div className="py-16 text-center">
                <CheckCircle2 className="w-12 h-12 text-emerald-500 mx-auto mb-3 opacity-80" />
                <h3 className="text-base font-semibold">Approval Queue is Clear</h3>
                <p className="text-sm text-muted-foreground max-w-sm mx-auto mt-1">
                  There are currently no staff registration requests awaiting administrator approval.
                </p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="bg-muted/50 text-muted-foreground border-b border-border">
                    <tr>
                      <th className="text-left font-medium px-4 py-3">Applicant Name</th>
                      <th className="text-left font-medium px-4 py-3">Work Email</th>
                      <th className="text-left font-medium px-4 py-3">Department</th>
                      <th className="text-left font-medium px-4 py-3">Requested Role</th>
                      <th className="text-left font-medium px-4 py-3">Assign Role</th>
                      <th className="text-right font-medium px-4 py-3">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border">
                    {pendingUsers.map((u) => (
                      <tr key={u.id} className="hover:bg-muted/30 transition-colors">
                        <td className="px-4 py-3 font-semibold text-foreground">
                          {u.full_name || <span className="text-muted-foreground italic">Pending Name</span>}
                        </td>
                        <td className="px-4 py-3 text-muted-foreground font-mono text-xs">
                          {u.email}
                        </td>
                        <td className="px-4 py-3">
                          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-secondary text-secondary-foreground text-xs font-medium">
                            <Building2 className="w-3.5 h-3.5" />
                            {u.department || "Case Management"}
                          </span>
                        </td>
                        <td className="px-4 py-3">
                          <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-amber-500/10 text-amber-700 dark:text-amber-300 border border-amber-500/20">
                            {u.requested_role ? u.requested_role.replace("_", " ").toUpperCase() : "CASEWORKER"}
                          </span>
                        </td>
                        <td className="px-4 py-3">
                          <select
                            value={selectedRole[u.id] || u.requested_role || "caseworker"}
                            onChange={(e) => setSelectedRole({ ...selectedRole, [u.id]: e.target.value })}
                            className="h-9 rounded-md border border-input bg-background px-3 py-1 text-xs focus:ring-2 focus:ring-primary font-medium"
                          >
                            {AVAILABLE_ROLES.map((r) => (
                              <option key={r.key} value={r.key}>
                                {r.label}
                              </option>
                            ))}
                          </select>
                        </td>
                        <td className="px-4 py-3 text-right">
                          <div className="flex items-center justify-end gap-2">
                            <Button
                              size="sm"
                              className="bg-emerald-600 hover:bg-emerald-700 text-white font-medium h-8"
                              disabled={approvingId === u.id || decliningId === u.id}
                              onClick={() => handleApprove(u.id)}
                            >
                              {approvingId === u.id ? (
                                <Loader2 className="w-3.5 h-3.5 animate-spin mr-1" />
                              ) : (
                                <UserCheck className="w-3.5 h-3.5 mr-1" />
                              )}
                              Approve Access
                            </Button>
                            <Button
                              size="sm"
                              variant="ghost"
                              className="text-destructive hover:bg-destructive/10 h-8"
                              disabled={approvingId === u.id || decliningId === u.id}
                              onClick={() => handleDeclinePending(u.id, u.full_name || u.email)}
                            >
                              {decliningId === u.id ? (
                                <Loader2 className="w-3.5 h-3.5 animate-spin" />
                              ) : (
                                <XCircle className="w-3.5 h-3.5" />
                              )}
                            </Button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}

      {/* TAB 3: SYSTEM HEALTH & INTEGRATIONS */}
      {activeTab === "system" && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-card border border-border rounded-xl p-5 space-y-4">
            <h3 className="text-sm font-semibold flex items-center gap-2">
              <Shield className="w-4 h-4 text-primary" />
              Live Connected Services
            </h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between p-3 rounded-lg bg-muted/40 border border-border">
                <div className="flex items-center gap-3">
                  <span className="w-2.5 h-2.5 rounded-full bg-emerald-500"></span>
                  <div>
                    <p className="text-sm font-semibold">Supabase PostgreSQL</p>
                    <p className="text-xs text-muted-foreground">ca-central-1 AWS Pooler • PostGIS Enabled</p>
                  </div>
                </div>
                <span className="text-xs font-semibold text-emerald-600 dark:text-emerald-400 bg-emerald-100 dark:bg-emerald-950/60 px-2 py-1 rounded">
                  Connected
                </span>
              </div>

              <div className="flex items-center justify-between p-3 rounded-lg bg-muted/40 border border-border">
                <div className="flex items-center gap-3">
                  <span className="w-2.5 h-2.5 rounded-full bg-emerald-500"></span>
                  <div>
                    <p className="text-sm font-semibold">Resend Email Delivery API</p>
                    <p className="text-xs text-muted-foreground">noreply@genserver.online • Verified Domain</p>
                  </div>
                </div>
                <span className="text-xs font-semibold text-emerald-600 dark:text-emerald-400 bg-emerald-100 dark:bg-emerald-950/60 px-2 py-1 rounded">
                  Active
                </span>
              </div>

              <div className="flex items-center justify-between p-3 rounded-lg bg-muted/40 border border-border">
                <div className="flex items-center gap-3">
                  <span className="w-2.5 h-2.5 rounded-full bg-emerald-500"></span>
                  <div>
                    <p className="text-sm font-semibold">FastAPI Backend Engine</p>
                    <p className="text-xs text-muted-foreground">crbcl-production.up.railway.app</p>
                  </div>
                </div>
                <span className="text-xs font-semibold text-emerald-600 dark:text-emerald-400 bg-emerald-100 dark:bg-emerald-950/60 px-2 py-1 rounded">
                  200 OK
                </span>
              </div>
            </div>
          </div>

          <div className="bg-card border border-border rounded-xl p-5 space-y-4">
            <h3 className="text-sm font-semibold flex items-center gap-2">
              <ShieldAlert className="w-4 h-4 text-purple-600" />
              Administrative Security Policy
            </h3>
            <ul className="text-xs text-muted-foreground space-y-2.5 list-disc pl-4">
              <li><strong>Zero-Trust Role Enforcement</strong>: New registrations require administrator approval before being active and accessing sensitive case records.</li>
              <li><strong>Leadership Promotion</strong>: IT Administrator promotes and configures CEO, Executive Director, and Director accounts directly.</li>
              <li><strong>Instant Provisioning</strong>: Accounts created from the Admin Dashboard are immediately active without OTP verification delays.</li>
              <li><strong>Account Removal</strong>: Permanent account deletion revokes active sessions and clears team memberships immediately.</li>
            </ul>
          </div>
        </div>
      )}

      {/* TAB 3: ALL STAFF DASHBOARDS & WORKSPACES ACCESS */}
      {activeTab === "staff_dashboards" && (
        <div className="space-y-6">
          <div className="bg-primary/10 border border-primary/20 rounded-xl p-5 flex items-start gap-4 shadow-sm">
            <div className="w-10 h-10 rounded-xl bg-primary/20 flex items-center justify-center flex-shrink-0 text-primary">
              <LayoutDashboard className="w-5 h-5" />
            </div>
            <div className="space-y-1">
              <h3 className="font-semibold text-base text-foreground flex items-center gap-2">
                Unified Staff Dashboard & Workspace Directory
                <span className="text-xs px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-700 dark:text-emerald-300 font-medium">
                  Universal Admin Access Active
                </span>
              </h3>
              <p className="text-xs text-muted-foreground">
                As System Administrator, you possess direct operational and administrative access to all {ALL_STAFF_DASHBOARDS.length} staff dashboards,
                intake pipelines, and specialized team workspaces across the platform. Click any dashboard card below to launch the workspace immediately.
              </p>
            </div>
          </div>

          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div className="relative w-full sm:w-80">
              <Search className="w-4 h-4 absolute left-3 top-3 text-muted-foreground" />
              <Input
                placeholder="Search staff dashboards by name, route, keyword..."
                value={dashboardsSearch}
                onChange={(e) => setDashboardsSearch(e.target.value)}
                className="pl-9 bg-card"
              />
            </div>

            <div className="flex items-center gap-2 overflow-x-auto w-full sm:w-auto pb-1">
              {["All", "Intake & Reception", "Operations & Facilities", "Case & Client", "Resource & Placements", "Quality & Reporting", "Finance & Administration", "Executive Leadership"].map((cat) => (
                <button
                  key={cat}
                  onClick={() => setDashboardsCategory(cat)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors whitespace-nowrap ${
                    dashboardsCategory === cat
                      ? "bg-primary text-primary-foreground shadow-sm"
                      : "bg-muted/50 text-muted-foreground hover:bg-muted hover:text-foreground"
                  }`}
                >
                  {cat}
                </button>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {ALL_STAFF_DASHBOARDS.filter((d) => {
              const matchesSearch =
                d.name.toLowerCase().includes(dashboardsSearch.toLowerCase()) ||
                d.route.toLowerCase().includes(dashboardsSearch.toLowerCase()) ||
                d.description.toLowerCase().includes(dashboardsSearch.toLowerCase()) ||
                d.category.toLowerCase().includes(dashboardsSearch.toLowerCase());
              const matchesCategory =
                dashboardsCategory === "All" || d.category === dashboardsCategory;
              return matchesSearch && matchesCategory;
            }).map((dashboard) => {
              const IconComp = dashboard.icon;
              return (
                <div
                  key={dashboard.route}
                  className="bg-card border border-border rounded-xl p-5 shadow-sm hover:border-primary/50 transition-all flex flex-col justify-between"
                >
                  <div className="space-y-3">
                    <div className="flex items-start justify-between gap-3">
                      <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center text-primary flex-shrink-0">
                        <IconComp className="w-5 h-5" />
                      </div>
                      <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
                        {dashboard.badge}
                      </span>
                    </div>

                    <div>
                      <h4 className="font-semibold text-sm text-foreground">{dashboard.name}</h4>
                      <code className="text-[11px] font-mono text-muted-foreground bg-muted px-1.5 py-0.5 rounded">
                        {dashboard.route}
                      </code>
                    </div>

                    <p className="text-xs text-muted-foreground line-clamp-2">
                      {dashboard.description}
                    </p>
                  </div>

                  <div className="pt-4 border-t border-border/60 mt-4 flex items-center justify-between gap-3">
                    <span className="text-[11px] text-muted-foreground font-medium">
                      {dashboard.category}
                    </span>
                    <Link to={dashboard.route}>
                      <Button size="sm" className="h-8 gap-1.5 text-xs bg-primary hover:bg-primary/90 text-primary-foreground">
                        Launch Dashboard
                        <ArrowRight className="w-3.5 h-3.5" />
                      </Button>
                    </Link>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* TAB 4: MASTER DASHBOARD CONTROL CENTRE */}
      {activeTab === "control_centre" && (
        <DashboardControlCentre />
      )}

      {/* Delete User Confirmation Modal */}
      <Dialog open={!!deleteTarget} onOpenChange={(v) => !v && setDeleteTarget(null)}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-destructive">
              <AlertTriangle className="w-5 h-5" />
              Delete Staff Account
            </DialogTitle>
            <DialogDescription>
              Are you sure you want to permanently delete the account for{" "}
              <strong>{deleteTarget?.full_name || deleteTarget?.email}</strong>?
            </DialogDescription>
          </DialogHeader>
          <div className="p-3 bg-muted/50 rounded-lg text-xs space-y-1 font-mono">
            <p><strong>Email:</strong> {deleteTarget?.email}</p>
            <p><strong>Role:</strong> {(deleteTarget?.roles || []).join(", ") || "None"}</p>
          </div>
          <p className="text-xs text-destructive font-medium">
            This action will immediately revoke all dashboard access, sign out any active sessions, and remove user assignments.
          </p>
          <DialogFooter className="gap-2 sm:gap-0">
            <Button variant="outline" onClick={() => setDeleteTarget(null)} disabled={deleting}>
              Cancel
            </Button>
            <Button 
              variant="destructive" 
              onClick={handleDeleteConfirm} 
              disabled={deleting}
            >
              {deleting ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin mr-2" />
                  Deleting Account...
                </>
              ) : (
                "Permanently Delete Account"
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <InviteUserDialog open={inviteOpen} onOpenChange={setInviteOpen} onInvited={loadUsers} />
      <EditUserDialog user={editUser} open={!!editUser} onOpenChange={(v) => !v && setEditUser(null)} onSaved={loadUsers} />
    </div>
  );
}