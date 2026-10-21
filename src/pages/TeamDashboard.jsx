import React, { useState, useEffect } from "react";
import { api } from "@/api";
import { useParams, Link, Navigate } from "react-router-dom";
import { ChevronLeft, FolderOpen, Users, Heart, AlertTriangle, Calendar, BookOpen, DollarSign, UserCog, Clock, TrendingUp, Lock } from "lucide-react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from "recharts";
import PageHeader from "@/components/shared/PageHeader";
import StatusBadge from "@/components/shared/StatusBadge";
import StatCard from "@/components/shared/StatCard";
import PreventionHealingWorkspace from "@/components/prevention_healing/PreventionHealingWorkspace";
import { TEAMS } from "./Teams";

const CHART_COLORS = ["hsl(4,60%,38%)", "hsl(36,70%,52%)", "hsl(152,45%,35%)", "hsl(220,50%,45%)", "hsl(280,45%,45%)"];

// Map each team to the data slices it cares about
const TEAM_FOCUS = {
  1:  { cases: true, clients: true, funding: true, employees: true, label: "Organization-wide overview" },
  2:  { cases: true, clients: true, families: true, incidents: true, appointments: true, label: "Child safety & family plans" },
  3:  { cases: true, clients: true, families: true, appointments: true, programs: true, label: "Prevention, counselling & wellness" },
  4:  { cases: true, clients: true, families: true, programs: true, appointments: true, label: "Residential & family stabilization" },
  5:  { cases: true, families: true, clients: true, appointments: true, label: "Housing & home stability" },
  6:  { cases: true, clients: true, families: true, appointments: true, label: "Frontline family relationships" },
  7:  { programs: true, appointments: true, clients: true, label: "Cultural teachings & ceremonies" },
  8:  { programs: true, clients: true, appointments: true, label: "Youth development & education" },
  9:  { cases: true, clients: true, appointments: true, incidents: true, label: "Mental health & therapeutic services" },
  10: { cases: true, clients: true, incidents: true, appointments: true, label: "Intake, screening & assessment" },
  11: { cases: true, incidents: true, programs: true, label: "Compliance, audits & reporting" },
  12: { cases: true, incidents: true, label: "Legal matters & court coordination" },
  13: { employees: true, label: "Recruitment, training & HR" },
  14: { funding: true, donations: true, label: "Finance, payroll & administration" },
  15: { cases: true, documents: true, label: "IT systems & digital transformation" },
  16: { programs: true, appointments: true, donations: true, label: "Community engagement & communications" },
  17: { employees: true, programs: true, label: "Staff training & professional development" },
  18: { cases: true, clients: true, families: true, programs: true, funding: true, label: "Data, reporting & outcomes" },
  19: { cases: true, clients: true, appointments: true, label: "Navigation & referral coordination" },
  20: { cases: true, clients: true, families: true, incidents: true, appointments: true, label: "Social worker intervention & child development" },
  21: { programs: true, appointments: true, clients: true, label: "Cultural programming & language preservation" },
  22: { cases: true, clients: true, programs: true, appointments: true, label: "Young adult transition & aftercare" },
  23: { operations: true, label: "Office Coordination & Facilities Operations" },
  24: { front_desk: true, label: "Front Desk & Public Intake Reception" },
};

export default function TeamDashboard() {
  const { id } = useParams();
  const teamId = parseInt(id);

  const team = TEAMS.find(t => t.id === teamId);
  const focus = TEAM_FOCUS[teamId] || {};

  const getStoredUser = () => {
    try {
      const s = localStorage.getItem("crbcl_current_user");
      return s ? JSON.parse(s) : null;
    } catch {
      return null;
    }
  };

  const [data, setData] = useState({ cases: [], clients: [], families: [], programs: [], funding: [], donations: [], employees: [], incidents: [], appointments: [], documents: [] });
  const [loading, setLoading] = useState(true);
  const [currentUser, setCurrentUser] = useState(getStoredUser);

  useEffect(() => {
    api.auth.me().then((u) => {
      if (u) setCurrentUser(u);
    }).catch(() => {});
  }, []);

  const extractRoles = (u) => {
    const list = [];
    if (u?.role) list.push(u.role);
    if (Array.isArray(u?.roles)) {
      for (const r of u.roles) {
        if (typeof r === "string") list.push(r);
        else if (r && typeof r === "object") list.push(r.key || r.name || r.role || "");
      }
    }
    return list.map((r) => String(r).toLowerCase().trim());
  };

  const roles = extractRoles(currentUser);
  const email = String(currentUser?.email || "").toLowerCase().trim();
  const permissions = Array.isArray(currentUser?.permissions) ? currentUser.permissions.map((p) => String(p).toLowerCase()) : [];

  const isAdminOrExecutive =
    email === "admin@crbcl.ca" ||
    email.includes("admin") ||
    roles.includes("admin") ||
    roles.includes("it_admin") ||
    roles.includes("administrator") ||
    roles.includes("system administrator") ||
    roles.includes("executive_director") ||
    roles.includes("director_manager") ||
    roles.includes("ceo") ||
    currentUser?.is_admin === true ||
    currentUser?.is_system === true ||
    permissions.some((p) => p.includes("admin") || p.includes("teams.manage") || p.includes("users.manage"));

  const rawAccess = currentUser?.team_access || [];
  const access = Array.isArray(rawAccess) ? rawAccess : [];
  const hasAccess =
    isAdminOrExecutive ||
    access.some((a) => String(a).toLowerCase() === "all" || String(a) === String(teamId));

  useEffect(() => {
    if (!currentUser) return;
    if (!hasAccess) {
      setLoading(false);
      return;
    }

    let isMounted = true;
    async function load() {
      setLoading(true);
      try {
        const safeFetch = async (promise) => {
          try {
            const res = await promise;
            return Array.isArray(res) ? res : (res?.items || []);
          } catch (err) {
            console.warn("Slice load error (non-fatal):", err);
            return [];
          }
        };

        const fetches = {};
        if (focus.cases)        fetches.cases        = safeFetch(api.entities.Case.list("-created_date", 100));
        if (focus.clients)      fetches.clients      = safeFetch(api.entities.Client.list("-created_date", 100));
        if (focus.families)     fetches.families     = safeFetch(api.entities.Family.list("-created_date", 100));
        if (focus.programs)     fetches.programs     = safeFetch(api.entities.Program.list("-created_date", 100));
        if (focus.funding)      fetches.funding      = safeFetch(api.entities.FundingGrant.list("-created_date", 50));
        if (focus.donations)    fetches.donations    = safeFetch(api.entities.Donation.list("-created_date", 50));
        if (focus.employees)    fetches.employees    = safeFetch(api.entities.Employee.list("-created_date", 100));
        if (focus.incidents)    fetches.incidents    = safeFetch(api.entities.Incident.list("-created_date", 50));
        if (focus.appointments) fetches.appointments = safeFetch(api.entities.Appointment.list("-created_date", 50));
        if (focus.documents)    fetches.documents    = safeFetch(api.entities.Document.list("-created_date", 50));

        const keys = Object.keys(fetches);
        const results = await Promise.all(Object.values(fetches));
        if (!isMounted) return;

        const resolved = {};
        keys.forEach((k, i) => { resolved[k] = results[i]; });
        setData(prev => ({ ...prev, ...resolved }));
      } catch (err) {
        console.error("TeamDashboard load failed:", err);
      } finally {
        if (isMounted) setLoading(false);
      }
    }
    load();

    return () => {
      isMounted = false;
    };
  }, [teamId, currentUser, hasAccess]);

  if (teamId === 23) {
    return <Navigate to="/office-coordinator" replace />;
  }

  if (!team) return <div className="p-8 text-center text-muted-foreground">Team not found.</div>;

  if (currentUser && !hasAccess) {
    return (
      <div className="flex flex-col items-center justify-center h-[60vh] gap-3">
        <div className="w-14 h-14 rounded-full bg-destructive/10 flex items-center justify-center">
          <Lock className="w-7 h-7 text-destructive" />
        </div>
        <p className="text-lg font-semibold">Access Restricted</p>
        <p className="text-sm text-muted-foreground max-w-sm text-center">
          You don't have access to this team dashboard. Contact an administrator to request access.
        </p>
        <Link to="/teams" className="text-sm text-primary hover:underline mt-2">Back to Teams</Link>
      </div>
    );
  }

  if (loading || !currentUser) {
    return (
      <div className="flex items-center justify-center h-[60vh]">
        <div className="w-8 h-8 border-4 border-primary/20 border-t-primary rounded-full animate-spin" />
      </div>
    );
  }

  if (teamId === 3) {
    return (
      <div className="space-y-6">
        <div>
          <Link to="/teams" className="inline-flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground mb-4 transition-colors">
            <ChevronLeft className="w-4 h-4" /> All Teams
          </Link>
        </div>
        <PreventionHealingWorkspace />
      </div>
    );
  }

  // Derived metrics
  const activeCases = data.cases.filter(c => c.status !== "Closed").length;
  const urgentCases = data.cases.filter(c => c.priority === "Critical" || c.priority === "Urgent" || c.priority === "High").length;
  const activeClients = data.clients.filter(c => c.status === "Active").length;
  const activeFamilies = data.families.filter(f => f.status === "Active").length;
  const activePrograms = data.programs.filter(p => p.status === "Active").length;
  const enrolledTotal = data.programs.reduce((s, p) => s + (p.enrolled_count || 0), 0);
  const totalFunding = data.funding.filter(f => f.status === "Active" || f.status === "Approved").reduce((s, f) => s + (f.amount || 0), 0);
  const totalDonations = data.donations.reduce((s, d) => s + (d.amount || 0), 0);
  const activeEmployees = data.employees.filter(e => e.status === "Active").length;
  const openIncidents = data.incidents.filter(i => i.status !== "Resolved").length;
  const scheduledAppts = data.appointments.filter(a => a.status === "Scheduled").length;

  const casesByStatus = Object.entries(
    data.cases.reduce((acc, c) => { acc[c.status] = (acc[c.status] || 0) + 1; return acc; }, {})
  ).map(([name, value]) => ({ name, value }));

  const casesByType = Object.entries(
    data.cases.reduce((acc, c) => { acc[c.case_type || "Other"] = (acc[c.case_type || "Other"] || 0) + 1; return acc; }, {})
  ).map(([name, value]) => ({ name: name.length > 12 ? name.substring(0, 12) + "…" : name, value }));

  const programChart = data.programs.filter(p => p.status === "Active").slice(0, 6).map(p => ({
    name: p.name?.length > 14 ? p.name.substring(0, 14) + "…" : p.name,
    enrolled: p.enrolled_count || 0,
    capacity: p.capacity || 0,
  }));

  const recentCases = data.cases.slice(0, 6);
  const upcomingAppts = data.appointments.filter(a => a.status === "Scheduled").slice(0, 5);

  return (
    <div className="space-y-6">
      <div>
        <Link to="/teams" className="inline-flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground mb-4 transition-colors">
          <ChevronLeft className="w-4 h-4" /> All Teams
        </Link>
        <PageHeader
          title={team.short}
          subtitle={focus.label || team.responsibilities}
        />
      </div>

      {/* Responsibilities banner */}
      <div className={`${team.color} rounded-xl p-4 text-white`}>
        <p className="text-sm font-medium opacity-90">{team.responsibilities}</p>
      </div>

      {/* Stat Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {focus.cases       && <StatCard title="Active Cases"      value={activeCases}    icon={FolderOpen}    color="primary"      />}
        {focus.cases       && <StatCard title="High Priority"     value={urgentCases}    icon={AlertTriangle} color={urgentCases > 0 ? "destructive" : "success"} />}
        {focus.clients     && <StatCard title="Active Clients"    value={activeClients}  icon={Users}         color="blue"         />}
        {focus.families    && <StatCard title="Active Families"   value={activeFamilies} icon={Heart}         color="accent"       />}
        {focus.programs    && <StatCard title="Active Programs"   value={activePrograms} icon={BookOpen}      color="success"      />}
        {focus.programs    && <StatCard title="Total Enrolled"    value={enrolledTotal}  icon={Users}         color="blue"         />}
        {focus.funding     && <StatCard title="Active Funding"    value={`$${(totalFunding/1000).toFixed(0)}K`} icon={DollarSign} color="success" />}
        {focus.donations   && <StatCard title="Donations"         value={`$${(totalDonations/1000).toFixed(0)}K`} icon={DollarSign} color="purple" />}
        {focus.employees   && <StatCard title="Active Staff"      value={activeEmployees} icon={UserCog}      color="primary"      />}
        {focus.incidents   && <StatCard title="Open Incidents"    value={openIncidents}  icon={AlertTriangle} color={openIncidents > 0 ? "warning" : "success"} />}
        {focus.appointments && <StatCard title="Scheduled Appts"  value={scheduledAppts} icon={Calendar}      color="blue"         />}
      </div>

      {/* Charts row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {focus.cases && casesByStatus.length > 0 && (
          <div className="bg-card rounded-xl border border-border p-5">
            <h3 className="text-sm font-semibold text-foreground mb-4 flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-primary" /> Case Status Distribution
            </h3>
            <div className="flex items-center gap-4">
              <ResponsiveContainer width="50%" height={180}>
                <PieChart>
                  <Pie data={casesByStatus} cx="50%" cy="50%" innerRadius={40} outerRadius={70} dataKey="value" paddingAngle={2}>
                    {casesByStatus.map((_, i) => <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />)}
                  </Pie>
                  <Tooltip contentStyle={{ borderRadius: "8px", fontSize: "12px" }} />
                </PieChart>
              </ResponsiveContainer>
              <div className="flex-1 space-y-1.5">
                {casesByStatus.map((item, i) => (
                  <div key={item.name} className="flex items-center gap-2 text-xs">
                    <div className="w-3 h-3 rounded-sm flex-shrink-0" style={{ backgroundColor: CHART_COLORS[i % CHART_COLORS.length] }} />
                    <span className="text-muted-foreground">{item.name}</span>
                    <span className="font-semibold text-foreground ml-auto">{item.value}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {focus.cases && casesByType.length > 0 && (
          <div className="bg-card rounded-xl border border-border p-5">
            <h3 className="text-sm font-semibold text-foreground mb-4 flex items-center gap-2">
              <FolderOpen className="w-4 h-4 text-primary" /> Cases by Type
            </h3>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={casesByType} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                <XAxis dataKey="name" tick={{ fontSize: 10 }} />
                <YAxis tick={{ fontSize: 11 }} allowDecimals={false} />
                <Tooltip contentStyle={{ borderRadius: "8px", fontSize: "12px" }} />
                <Bar dataKey="value" fill="hsl(4,60%,38%)" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}

        {focus.programs && programChart.length > 0 && (
          <div className="bg-card rounded-xl border border-border p-5">
            <h3 className="text-sm font-semibold text-foreground mb-4 flex items-center gap-2">
              <BookOpen className="w-4 h-4 text-primary" /> Program Utilization
            </h3>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={programChart} layout="vertical" margin={{ top: 0, right: 10, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                <XAxis type="number" tick={{ fontSize: 11 }} allowDecimals={false} />
                <YAxis dataKey="name" type="category" width={100} tick={{ fontSize: 10 }} />
                <Tooltip contentStyle={{ borderRadius: "8px", fontSize: "12px" }} />
                <Bar dataKey="enrolled" fill="hsl(4,60%,38%)" radius={[0, 4, 4, 0]} name="Enrolled" />
                <Bar dataKey="capacity" fill="hsl(var(--border))" radius={[0, 4, 4, 0]} name="Capacity" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}

        {focus.appointments && upcomingAppts.length > 0 && (
          <div className="bg-card rounded-xl border border-border p-5">
            <h3 className="text-sm font-semibold text-foreground mb-4 flex items-center gap-2">
              <Calendar className="w-4 h-4 text-primary" /> Upcoming Appointments
            </h3>
            <div className="space-y-2.5">
              {upcomingAppts.map(a => (
                <div key={a.id} className="flex items-center gap-3 p-2.5 rounded-lg bg-muted/50">
                  <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0">
                    <Clock className="w-4 h-4 text-primary" />
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-medium text-foreground truncate">{a.title}</p>
                    <p className="text-xs text-muted-foreground">{a.date} • {a.time || "TBD"}</p>
                  </div>
                  <StatusBadge status={a.status} />
                </div>
              ))}
            </div>
          </div>
        )}

        {focus.employees && data.employees.length > 0 && (
          <div className="bg-card rounded-xl border border-border p-5">
            <h3 className="text-sm font-semibold text-foreground mb-4 flex items-center gap-2">
              <UserCog className="w-4 h-4 text-primary" /> Staff by Department
            </h3>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart
                data={Object.entries(data.employees.reduce((acc, e) => { acc[e.department || "Other"] = (acc[e.department || "Other"] || 0) + 1; return acc; }, {})).map(([name, value]) => ({ name: name.length > 14 ? name.substring(0, 14) + "…" : name, value }))}
                margin={{ top: 0, right: 0, left: -20, bottom: 0 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                <XAxis dataKey="name" tick={{ fontSize: 9 }} />
                <YAxis tick={{ fontSize: 11 }} allowDecimals={false} />
                <Tooltip contentStyle={{ borderRadius: "8px", fontSize: "12px" }} />
                <Bar dataKey="value" fill="hsl(220,50%,45%)" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}

        {focus.funding && data.funding.length > 0 && (
          <div className="bg-card rounded-xl border border-border p-5">
            <h3 className="text-sm font-semibold text-foreground mb-4 flex items-center gap-2">
              <DollarSign className="w-4 h-4 text-primary" /> Funding by Status
            </h3>
            <div className="space-y-2">
              {Object.entries(data.funding.reduce((acc, f) => { acc[f.status] = (acc[f.status] || 0) + (f.amount || 0); return acc; }, {})).map(([status, amount]) => (
                <div key={status} className="flex items-center justify-between py-1.5 border-b border-border/50 last:border-0 text-sm">
                  <StatusBadge status={status} />
                  <span className="font-semibold text-foreground">${amount.toLocaleString()}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Recent Cases Table */}
      {focus.cases && recentCases.length > 0 && (
        <div className="bg-card rounded-xl border border-border p-5">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-foreground flex items-center gap-2">
              <FolderOpen className="w-4 h-4 text-primary" /> Recent Cases
            </h3>
            <Link to="/cases" className="text-xs text-primary hover:underline">View All →</Link>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border">
                  <th className="text-left pb-2 text-xs font-medium text-muted-foreground">Case</th>
                  <th className="text-left pb-2 text-xs font-medium text-muted-foreground hidden sm:table-cell">Type</th>
                  <th className="text-left pb-2 text-xs font-medium text-muted-foreground">Status</th>
                  <th className="text-left pb-2 text-xs font-medium text-muted-foreground hidden md:table-cell">Priority</th>
                  <th className="text-left pb-2 text-xs font-medium text-muted-foreground hidden lg:table-cell">Worker</th>
                </tr>
              </thead>
              <tbody>
                {recentCases.map(c => (
                  <tr key={c.id} className="border-b border-border/50 last:border-0">
                    <td className="py-2.5">
                      <Link to={`/cases/${c.id}`} className="font-medium text-foreground hover:text-primary transition-colors">{c.title}</Link>
                      {c.case_number && <p className="text-xs text-muted-foreground">{c.case_number}</p>}
                    </td>
                    <td className="py-2.5 text-muted-foreground hidden sm:table-cell">{c.case_type}</td>
                    <td className="py-2.5"><StatusBadge status={c.status} /></td>
                    <td className="py-2.5 hidden md:table-cell"><StatusBadge status={c.priority} /></td>
                    <td className="py-2.5 text-muted-foreground hidden lg:table-cell">{c.assigned_worker_name || "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}