import { lazy, Suspense } from 'react';
import { Toaster } from "@/components/ui/toaster"
import { QueryClientProvider } from '@tanstack/react-query'
import { queryClientInstance } from '@/lib/query-client'
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
import PageNotFound from '@/pages/PageNotFound';
import { AuthProvider, useAuth } from '@/context/AuthContext';
import { ThemeProvider } from '@/context/ThemeContext';
import UserNotRegisteredError from '@/components/auth/UserNotRegisteredError';
import ProtectedRoute from '@/components/auth/ProtectedRoute';

// Auth pages
import Login from '@/pages/Login';
import AdminLogin from '@/pages/AdminLogin';
import Register from '@/pages/Register';
import ForgotPassword from '@/pages/ForgotPassword';
import ResetPassword from '@/pages/ResetPassword';
import Profile from '@/pages/Profile';
import DirectorsDashboard from '@/pages/DirectorsDashboard';
import ExecutiveDashboard from '@/pages/ExecutiveDashboard';
import CEODashboard from '@/pages/CEODashboard';
import BoardDashboard from '@/pages/BoardDashboard';

// Layout
import AppLayout from '@/components/layout/AppLayout';

// Phase 3 Intake & Referrals
import IntakeList from '@/pages/IntakeList';
import NewIntake from '@/pages/NewIntake';
import IntakeDetail from '@/pages/IntakeDetail';
import IntakeDecision from '@/pages/IntakeDecision';
import SupervisorApprovalQueue from '@/pages/SupervisorApprovalQueue';

// Phase 5 Configurable Assessment Engine
import AssessmentDetail from '@/pages/AssessmentDetail';

// Phase 6 Safety Plans & Case Plans
import PlanDetail from '@/pages/PlanDetail';
import PlanEditor from '@/pages/PlanEditor';

// Phase 8 Placement Homes & Facilities
import PlacementHomesList from '@/pages/PlacementHomesList';
import PlacementHomeDetail from '@/pages/PlacementHomeDetail';

// Phase 9 Scheduling, Staffing Facilitator & Notifications
import MySchedule from '@/pages/MySchedule';
import TeamSchedule from '@/pages/TeamSchedule';
import StaffingFacilitator from '@/pages/StaffingFacilitator';
import StaffingSessionDetail from '@/pages/StaffingSessionDetail';
import Notifications from '@/pages/Notifications';

// Phase 10 Finance & Placement Billing (Lazy Loaded for Bundle Optimization)
const FinanceDashboard = lazy(() => import('@/pages/FinanceDashboard'));
const FinanceRequests = lazy(() => import('@/pages/FinanceRequests'));
const FinanceRequestNew = lazy(() => import('@/pages/FinanceRequestNew'));
const FinanceRequestDetail = lazy(() => import('@/pages/FinanceRequestDetail'));
const FinanceInvoices = lazy(() => import('@/pages/FinanceInvoices'));
const FinanceInvoiceDetail = lazy(() => import('@/pages/FinanceInvoiceDetail'));
const FinanceRates = lazy(() => import('@/pages/FinanceRates'));
const FinanceBudgetLines = lazy(() => import('@/pages/FinanceBudgetLines'));
const FinanceLedger = lazy(() => import('@/pages/FinanceLedger'));

// Phase 11 Reporting, Quality Assurance & Passports
const ReportsHub = lazy(() => import('@/pages/ReportsHub'));
const ReportBuilder = lazy(() => import('@/pages/ReportBuilder'));
const ChildPassport = lazy(() => import('@/pages/ChildPassport'));
const ParentPassport = lazy(() => import('@/pages/ParentPassport'));
const QADashboard = lazy(() => import('@/pages/QADashboard'));
const QAAuditsList = lazy(() => import('@/pages/QAAuditsList'));
const QAAuditNew = lazy(() => import('@/pages/QAAuditNew'));

// Phase 12 Fleet Management & Vehicle Operations
const FleetDashboard = lazy(() => import('@/pages/FleetDashboard'));
const VehiclesList = lazy(() => import('@/pages/VehiclesList'));
const VehicleDetail = lazy(() => import('@/pages/VehicleDetail'));
const FleetMaintenance = lazy(() => import('@/pages/FleetMaintenance'));

// Phase 13 Enterprise Integrations, OCR & Communications
const AdminIntegrations = lazy(() => import('@/pages/AdminIntegrations'));
const OCRReview = lazy(() => import('@/pages/OCRReview'));
const CommunicationsHub = lazy(() => import('@/pages/CommunicationsHub'));

// Completion Sprint A — Organizational Operations Pages
const Housing = lazy(() => import('@/pages/Housing'));
const Facilities = lazy(() => import('@/pages/Facilities'));
const ITAssets = lazy(() => import('@/pages/ITAssets'));
const Volunteers = lazy(() => import('@/pages/Volunteers'));

// Completion Sprint B — Clinical Notes & Terminology Pages
const ClinicalNotes = lazy(() => import('@/pages/ClinicalNotes'));
const AdminTerminology = lazy(() => import('@/pages/AdminTerminology'));

// Resource Unit & Recruitment (Sprint 1 & 3)
const ResourceDashboard = lazy(() => import('@/pages/ResourceDashboard'));
const RecruitmentPipeline = lazy(() => import('@/pages/RecruitmentPipeline'));
const RecruitmentDetail = lazy(() => import('@/pages/RecruitmentDetail'));
const RecruitmentNew = lazy(() => import('@/pages/RecruitmentNew'));
const PlacementMatching = lazy(() => import('@/pages/PlacementMatching'));
const FrontDeskDashboard = lazy(() => import('@/pages/FrontDeskDashboard'));
const NavigatorDashboard = lazy(() => import('@/pages/NavigatorDashboard'));
const OfficeCoordinator = lazy(() => import('@/pages/OfficeCoordinator'));
const OfflineWorkspace = lazy(() => import('@/pages/OfflineWorkspace'));



// Pages
import Dashboard from '@/pages/Dashboard';
import Cases from '@/pages/Cases';
import CaseDetail from '@/pages/CaseDetail';

import Clients from '@/pages/Clients';
import ClientDetail from '@/pages/ClientDetail';
import PersonDetail from '@/pages/PersonDetail';
import Families from '@/pages/Families';
import FamilyDetail from '@/pages/FamilyDetail';
import Programs from '@/pages/Programs';
import Employees from '@/pages/Employees';
import HRDashboard from '@/pages/HRDashboard';
import Appointments from '@/pages/Appointments';
import Funding from '@/pages/Funding';
import Donations from '@/pages/Donations';
import Documents from '@/pages/Documents';
import Incidents from '@/pages/Incidents';
import AskRedBear from '@/pages/AskRedBear';
import Teams from '@/pages/Teams';
import TeamDashboard from '@/pages/TeamDashboard';
import AdminDashboard from '@/pages/AdminDashboard';

const AuthenticatedApp = () => {
  const { isLoadingAuth, isLoadingPublicSettings, authError, navigateToLogin } = useAuth();

  if (isLoadingPublicSettings || isLoadingAuth) {
    return (
      <div className="fixed inset-0 flex items-center justify-center bg-background">
        <div className="text-center">
          <div className="w-10 h-10 border-4 border-primary/20 border-t-primary rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-sm text-muted-foreground">Loading CRBCL Platform…</p>
        </div>
      </div>
    );
  }

  if (authError) {
    if (authError.type === 'user_not_registered') {
      return <UserNotRegisteredError />;
    } else if (authError.type === 'auth_required') {
      navigateToLogin();
      return null;
    }
  }

  return (
    <Suspense
      fallback={
        <div className="p-8 text-center text-sm text-muted-foreground">
          <div className="w-8 h-8 border-3 border-primary/20 border-t-primary rounded-full animate-spin mx-auto mb-3"></div>
          Loading financial module...
        </div>
      }
    >
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/admin/login" element={<AdminLogin />} />
        <Route path="/register" element={<Register />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />
        <Route path="/reset-password" element={<ResetPassword />} />

        {/* Dedicated Admin Portal Routes (Exclusively for IT Admins / System Admins) */}
        <Route element={<ProtectedRoute unauthenticatedElement={<Navigate to="/admin/login" replace />} />}>
          <Route element={<AppLayout />}>
            <Route path="/admin" element={<AdminDashboard />} />
            <Route path="/admin/integrations" element={<AdminIntegrations />} />
            <Route path="/admin/terminology" element={<AdminTerminology />} />
          </Route>
        </Route>

        {/* Standard Staff & Caseworker Protected Routes (Redirects to /login when unauthenticated) */}
        <Route element={<ProtectedRoute unauthenticatedElement={<Navigate to="/login" replace />} />}>
          <Route element={<AppLayout />}>
            <Route path="/" element={<Dashboard />} />
            <Route path="/profile" element={<Profile />} />
            <Route path="/director" element={<DirectorsDashboard />} />
            <Route path="/executive" element={<ExecutiveDashboard />} />
            <Route path="/ceo" element={<CEODashboard />} />
            <Route path="/board" element={<BoardDashboard />} />
            <Route path="/hr" element={<HRDashboard />} />
            <Route path="/terminology" element={<AdminTerminology />} />
            <Route path="/front-desk" element={<FrontDeskDashboard />} />
            <Route path="/office-coordinator" element={<OfficeCoordinator />} />
            <Route path="/navigator" element={<NavigatorDashboard />} />
            <Route path="/intake" element={<IntakeList />} />
            <Route path="/intake/new" element={<NewIntake />} />
            <Route path="/intake/approvals" element={<SupervisorApprovalQueue />} />
            <Route path="/supervisor/approvals" element={<SupervisorApprovalQueue />} />
            <Route path="/intake/:id" element={<IntakeDetail />} />
            <Route path="/intake/:id/decision" element={<IntakeDecision />} />
            <Route path="/cases" element={<Cases />} />
            <Route path="/cases/:id" element={<CaseDetail />} />
            <Route path="/placement-homes" element={<PlacementHomesList />} />
            <Route path="/placement-homes/:id" element={<PlacementHomeDetail />} />

            {/* Resource Unit & Caregiver Recruitment Routes (Sprint 1 & 3) */}
            <Route path="/resource-team" element={<ResourceDashboard />} />
            <Route path="/resource-team/recruitment" element={<RecruitmentPipeline />} />
            <Route path="/resource-team/recruitment/new" element={<RecruitmentNew />} />
            <Route path="/resource-team/recruitment/:id" element={<RecruitmentDetail />} />
            <Route path="/resource-team/matching" element={<PlacementMatching />} />
            <Route path="/placement-matching" element={<PlacementMatching />} />
            <Route path="/schedule" element={<MySchedule />} />
            <Route path="/schedule/team" element={<TeamSchedule />} />
            <Route path="/staffing" element={<StaffingFacilitator />} />
            <Route path="/staffing/:id" element={<StaffingSessionDetail />} />
            <Route path="/notifications" element={<Notifications />} />
            <Route path="/assessments/:id" element={<AssessmentDetail />} />

            {/* Phase 10 Finance & Placement Billing Routes */}
            <Route path="/finance" element={<FinanceDashboard />} />
            <Route path="/finance/requests" element={<FinanceRequests />} />
            <Route path="/finance/requests/new" element={<FinanceRequestNew />} />
            <Route path="/finance/requests/:id" element={<FinanceRequestDetail />} />
            <Route path="/finance/invoices" element={<FinanceInvoices />} />
            <Route path="/finance/invoices/:id" element={<FinanceInvoiceDetail />} />
            <Route path="/finance/rates" element={<FinanceRates />} />
            <Route path="/finance/budget-lines" element={<FinanceBudgetLines />} />
            <Route path="/finance/ledger" element={<FinanceLedger />} />

            {/* Phase 11 Reporting, Quality Assurance & Passports Routes */}
            <Route path="/reports" element={<ReportsHub />} />
            <Route path="/reports/builder" element={<ReportBuilder />} />
            <Route path="/passports/child/:id" element={<ChildPassport />} />
            <Route path="/passports/parent/:id" element={<ParentPassport />} />
            <Route path="/qa" element={<QADashboard />} />
            <Route path="/qa/audits" element={<QAAuditsList />} />
            <Route path="/qa/audits/new" element={<QAAuditNew />} />

            {/* Phase 12 Fleet Management */}
            <Route path="/fleet" element={<FleetDashboard />} />
            <Route path="/fleet/vehicles" element={<VehiclesList />} />
            <Route path="/fleet/vehicles/:id" element={<VehicleDetail />} />
            <Route path="/fleet/maintenance" element={<FleetMaintenance />} />

            {/* Phase 13 Enterprise Integrations, OCR & Communications */}
            <Route path="/ocr/review" element={<OCRReview />} />
            <Route path="/communications" element={<CommunicationsHub />} />

            {/* Completion Sprint A — Organizational Operations */}
            <Route path="/housing" element={<Housing />} />
            <Route path="/facilities" element={<Facilities />} />
            <Route path="/assets" element={<ITAssets />} />
            <Route path="/volunteers" element={<Volunteers />} />

            <Route path="/plans/:id" element={<PlanDetail />} />
            <Route path="/plans/:id/edit" element={<PlanEditor />} />
            <Route path="/clients" element={<Clients />} />
            <Route path="/clients/:id" element={<ClientDetail />} />
            <Route path="/people/:id" element={<PersonDetail />} />
            <Route path="/families" element={<Families />} />
            <Route path="/families/:id" element={<FamilyDetail />} />
            <Route path="/programs" element={<Programs />} />
            <Route path="/employees" element={<Employees />} />
            <Route path="/appointments" element={<Appointments />} />
            <Route path="/funding" element={<Funding />} />
            <Route path="/donations" element={<Donations />} />
            <Route path="/documents" element={<Documents />} />
            <Route path="/incidents" element={<Incidents />} />
            <Route path="/clinical-notes" element={<ClinicalNotes />} />
            <Route path="/ask-red-bear" element={<AskRedBear />} />
            <Route path="/teams" element={<Teams />} />
            <Route path="/teams/:id" element={<TeamDashboard />} />
            <Route path="/prevention-healing" element={<Navigate to="/teams/3" replace />} />
            <Route path="/offline-workspace" element={<OfflineWorkspace />} />
          </Route>
        </Route>

        <Route path="*" element={<PageNotFound />} />
      </Routes>
    </Suspense>
  );
};

function App() {
  return (
    <AuthProvider>
      <ThemeProvider>
        <QueryClientProvider client={queryClientInstance}>
          <Router>
            <AuthenticatedApp />
          </Router>
          <Toaster />
        </QueryClientProvider>
      </ThemeProvider>
    </AuthProvider>
  )
}

export default App