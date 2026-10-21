import React, { useState, useEffect, useCallback } from "react";
import {
  Sparkles,
  Shield,
  HeartHandshake,
  Users,
  UserPlus,
  FileSpreadsheet,
  UploadCloud,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Search,
  Plus,
  RefreshCw,
  FileText,
  DollarSign,
  Calendar,
  MapPin,
  Building,
  Filter,
  Check,
  ExternalLink,
  Lock,
  Eye,
  Trash2,
  Edit2,
  PieChart as PieChartIcon,
  TrendingUp,
  AlertCircle,
  ArrowRight,
  ShieldCheck,
  Download,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { toast } from "@/components/ui/use-toast";
import PageHeader from "@/components/shared/PageHeader";
import StatCard from "@/components/shared/StatCard";
import StatusBadge from "@/components/shared/StatusBadge";
import preventionHealingApi from "@/api/preventionHealing";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  PieChart,
  Pie,
  Cell,
  Legend,
} from "recharts";

const CHART_COLORS = [
  "#dc2626", // red-600
  "#d97706", // amber-600
  "#059669", // emerald-600
  "#2563eb", // blue-600
  "#7c3aed", // violet-600
  "#db2777", // pink-600
];

export default function PreventionHealingWorkspace() {
  const [fiscalYear, setFiscalYear] = useState("2026-2027");
  const [activeTab, setActiveTab] = useState("overview");
  const [loading, setLoading] = useState(true);

  // Core Data
  const [summary, setSummary] = useState(null);
  const [enhancementPrograms, setEnhancementPrograms] = useState([]);
  const [familySupportRecords, setFamilySupportRecords] = useState([]);
  const [otherNationsRecords, setOtherNationsRecords] = useState([]);
  const [pendingStaffList, setPendingStaffList] = useState([]);
  const [clientRefsList, setClientRefsList] = useState([]);
  const [importBatches, setImportBatches] = useState([]);

  // Search & Filters
  const [epSearch, setEpSearch] = useState("");
  const [fsrSearch, setFsrSearch] = useState("");
  const [onsSearch, setOnsSearch] = useState("");
  const [staffFilter, setStaffFilter] = useState("ALL");
  const [clientFilter, setClientFilter] = useState("ALL");

  // Modals & Forms
  const [epModalOpen, setEpModalOpen] = useState(false);
  const [epForm, setEpForm] = useState({
    program: "",
    program_activity: "",
    employee_name_raw: "",
    position_raw: "",
    record_date: new Date().toISOString().split("T")[0],
    city: "Regina",
    province: "SK",
    families_in_province: 0,
    families_out_of_province: 0,
    participants_children_0_12: 0,
    participants_youth_13_17: 0,
    participants_post_majority_18_26: 0,
    participants_parents_caregivers: 0,
    participants_family_members: 0,
    participants_others: 0,
    account_code: "41000",
    subcode: "213",
    expense_gift_card: 0,
    expense_purchase_order: 0,
    expense_eft: 0,
    expense_cheque: 0,
    expense_credit_card: 0,
    expense_courtesy_card: 0,
    comments: "",
    fiscal_year: "2026-2027",
  });

  const [fsrModalOpen, setFsrModalOpen] = useState(false);
  const [fsrForm, setFsrForm] = useState({
    program: "Direct Family Intervention",
    support_type: "Emergency Food & Utility Relief",
    employee_name_raw: "",
    position_raw: "Family Support Worker",
    client_ref_legacy_id: "",
    record_date: new Date().toISOString().split("T")[0],
    city: "Regina",
    province: "SK",
    participants_children_0_12: 0,
    participants_youth_13_17: 0,
    participants_post_majority_18_26: 0,
    participants_adults_18_plus: 0,
    account_code: "41000",
    subcode: "213",
    project_code: "",
    expense_gift_card: 0,
    expense_purchase_order: 0,
    expense_eft: 0,
    expense_cheque: 0,
    expense_credit_card: 0,
    expense_petty_cash: 0,
    expense_courtesy_card: 0,
    comments: "",
    fiscal_year: "2026-2027",
  });

  const [onsModalOpen, setOnsModalOpen] = useState(false);
  const [onsForm, setOnsForm] = useState({
    worker_name_raw: "",
    record_date: new Date().toISOString().split("T")[0],
    family_reference_raw: "",
    service_type: "Eagle Nest Lodging & Emergency Support",
    cost: 0,
    on_reserve: false,
    cowessess_connection: "Band Member / Descendant",
    other_community: "",
    historical_reference_number: "",
    comments: "",
    fiscal_year: "2026-2027",
  });

  // Staff Onboarding Activation Modal
  const [activateStaffModalOpen, setActivateStaffModalOpen] = useState(false);
  const [selectedStaff, setSelectedStaff] = useState(null);
  const [staffEmail, setStaffEmail] = useState("");
  const [staffPosition, setStaffPosition] = useState("");
  const [activatingStaff, setActivatingStaff] = useState(false);

  // Client Reconciliation Modal
  const [reconcileClientModalOpen, setReconcileClientModalOpen] = useState(false);
  const [selectedClientRef, setSelectedClientRef] = useState(null);
  const [personQuery, setPersonQuery] = useState("");
  const [personResults, setPersonResults] = useState([]);
  const [searchingPersons, setSearchingPersons] = useState(false);
  const [selectedPersonId, setSelectedPersonId] = useState("");
  const [reconcilingClient, setReconcilingClient] = useState(false);

  // Excel Import Wizard State
  const [importFile, setImportFile] = useState(null);
  const [importWorksheet, setImportWorksheet] = useState("Enhancement Programs");
  const [importRecordType, setImportRecordType] = useState("ENHANCEMENT_PROGRAMS");
  const [analyzingImport, setAnalyzingImport] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [executingBatchId, setExecutingBatchId] = useState(null);

  // Initial load
  const loadWorkspaceData = useCallback(async () => {
    setLoading(true);
    try {
      const [sumRes, epRes, fsrRes, onsRes, staffRes, clientRes, batchesRes] = await Promise.allSettled([
        preventionHealingApi.getSummary(fiscalYear),
        preventionHealingApi.getEnhancementPrograms({ fiscal_year: fiscalYear, limit: 100 }),
        preventionHealingApi.getFamilySupportRecords({ fiscal_year: fiscalYear, limit: 100 }),
        preventionHealingApi.getOtherNationsSupport({ fiscal_year: fiscalYear, limit: 100 }),
        preventionHealingApi.getPendingStaff({ limit: 100 }),
        preventionHealingApi.getClientRefs({ limit: 100 }),
        preventionHealingApi.getImportBatches({ limit: 20 }),
      ]);

      if (sumRes.status === "fulfilled") setSummary(sumRes.value);
      if (epRes.status === "fulfilled") setEnhancementPrograms(epRes.value || []);
      if (fsrRes.status === "fulfilled") setFamilySupportRecords(fsrRes.value || []);
      if (onsRes.status === "fulfilled") setOtherNationsRecords(onsRes.value || []);
      if (staffRes.status === "fulfilled") setPendingStaffList(staffRes.value || []);
      if (clientRes.status === "fulfilled") setClientRefsList(clientRes.value || []);
      if (batchesRes.status === "fulfilled") setImportBatches(batchesRes.value || []);
    } catch (err) {
      console.error("Failed to load workspace data:", err);
      toast({
        title: "Workspace Load Error",
        description: "Could not retrieve records. Please verify server connectivity.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  }, [fiscalYear]);

  useEffect(() => {
    loadWorkspaceData();
  }, [loadWorkspaceData]);

  // Handle Form Submissions
  const handleSaveEP = async (e) => {
    e.preventDefault();
    try {
      await preventionHealingApi.createEnhancementProgram({
        ...epForm,
        fiscal_year: fiscalYear,
      });
      toast({ title: "Success", description: "Enhancement Program record created." });
      setEpModalOpen(false);
      loadWorkspaceData();
    } catch (err) {
      toast({
        title: "Creation Error",
        description: err.message || "Failed to create program record.",
        variant: "destructive",
      });
    }
  };

  const handleSaveFSR = async (e) => {
    e.preventDefault();
    try {
      await preventionHealingApi.createFamilySupportRecord({
        ...fsrForm,
        fiscal_year: fiscalYear,
      });
      toast({ title: "Success", description: "Family Support record created." });
      setFsrModalOpen(false);
      loadWorkspaceData();
    } catch (err) {
      toast({
        title: "Creation Error",
        description: err.message || "Failed to create family support record.",
        variant: "destructive",
      });
    }
  };

  const handleSaveONS = async (e) => {
    e.preventDefault();
    try {
      await preventionHealingApi.createOtherNationsRecord({
        ...onsForm,
        fiscal_year: fiscalYear,
      });
      toast({ title: "Success", description: "Other Nations (Eagle Nest) record created." });
      setOnsModalOpen(false);
      loadWorkspaceData();
    } catch (err) {
      toast({
        title: "Creation Error",
        description: err.message || "Failed to create record.",
        variant: "destructive",
      });
    }
  };

  // Staff Verification & Linking (Does not activate login account)
  const handleActivateStaff = async () => {
    if (!staffEmail || !staffEmail.includes("@")) {
      toast({
        title: "Invalid Email",
        description: "A valid verified email address is required to verify an employee profile.",
        variant: "destructive",
      });
      return;
    }
    setActivatingStaff(true);
    try {
      await preventionHealingApi.verifyPendingStaff(selectedStaff.id, {
        email: staffEmail,
        position: staffPosition || selectedStaff.position,
      });
      toast({
        title: "Staff Profile Verified & Linked",
        description: `${selectedStaff.display_name_from_excel} verified and linked to Employee profile. Login user account remains inactive.`,
      });
      setActivateStaffModalOpen(false);
      loadWorkspaceData();
    } catch (err) {
      toast({
        title: "Verification Error",
        description: err.message || "Could not verify staff profile.",
        variant: "destructive",
      });
    } finally {
      setActivatingStaff(false);
    }
  };

  // Person Search for Client Reconciliation
  const handleSearchPerson = async (q) => {
    setPersonQuery(q);
    if (!q || q.trim().length < 2) {
      setPersonResults([]);
      return;
    }
    setSearchingPersons(true);
    try {
      const results = await preventionHealingApi.searchPersons(q);
      setPersonResults(results || []);
    } catch (err) {
      console.warn("Person search error:", err);
    } finally {
      setSearchingPersons(false);
    }
  };

  const handleConfirmClientMatch = async () => {
    if (!selectedPersonId) {
      toast({
        title: "Selection Needed",
        description: "Please choose a verified canonical Person from the candidate list.",
        variant: "destructive",
      });
      return;
    }
    setReconcilingClient(true);
    try {
      await preventionHealingApi.reconcileClientRef(selectedClientRef.id, {
        person_id: selectedPersonId,
        action: "CONFIRM",
      });
      toast({
        title: "Client Linked",
        description: `Legacy ID ${selectedClientRef.legacy_id} linked to Person #${selectedPersonId}.`,
      });
      setReconcileClientModalOpen(false);
      loadWorkspaceData();
    } catch (err) {
      toast({
        title: "Reconciliation Error",
        description: err.message || "Failed to reconcile client identifier.",
        variant: "destructive",
      });
    } finally {
      setReconcilingClient(false);
    }
  };

  const handleRejectClientMatch = async () => {
    setReconcilingClient(true);
    try {
      await preventionHealingApi.reconcileClientRef(selectedClientRef.id, {
        action: "REJECT",
      });
      toast({
        title: "Marked Rejected",
        description: `Legacy identifier ${selectedClientRef.legacy_id} quarantined.`,
      });
      setReconcileClientModalOpen(false);
      loadWorkspaceData();
    } catch (err) {
      toast({
        title: "Reconciliation Error",
        description: err.message || "Failed to update record.",
        variant: "destructive",
      });
    } finally {
      setReconcilingClient(false);
    }
  };

  // Safe Excel Import Wizard Workflow
  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setImportFile(file);
      setAnalysisResult(null);
    }
  };

  const handleAnalyzeWorkbook = async () => {
    if (!importFile) {
      toast({
        title: "No File Selected",
        description: "Please select an Excel workbook (.xlsx) to analyze.",
        variant: "destructive",
      });
      return;
    }
    setAnalyzingImport(true);
    try {
      const formData = new FormData();
      formData.append("file", importFile);
      formData.append("worksheet_name", importWorksheet);
      formData.append("record_type", importRecordType);

      const result = await preventionHealingApi.analyzeImport(formData);
      setAnalysisResult(result);
      toast({
        title: "Workbook Analyzed",
        description: `Analyzed ${result.total_rows_analyzed} rows with ${result.valid_rows} valid entries.`,
      });
      loadWorkspaceData();
    } catch (err) {
      toast({
        title: "Analysis Error",
        description: err.message || "Failed to parse Excel workbook.",
        variant: "destructive",
      });
    } finally {
      setAnalyzingImport(false);
    }
  };

  const handleApproveBatch = async (batchId) => {
    try {
      await preventionHealingApi.approveImportBatch(batchId);
      toast({
        title: "Batch Approved",
        description: "Batch authorized for execution. You may now commit the records.",
      });
      if (analysisResult && analysisResult.batch_id === batchId) {
        setAnalysisResult((prev) => ({ ...prev, status: "APPROVED" }));
      }
      loadWorkspaceData();
    } catch (err) {
      toast({
        title: "Approval Error",
        description: err.message || "Failed to approve import batch.",
        variant: "destructive",
      });
    }
  };

  const handleExecuteBatch = async (batchId) => {
    setExecutingBatchId(batchId);
    try {
      const res = await preventionHealingApi.executeImportBatch(batchId);
      toast({
        title: "Import Complete",
        description: `Successfully imported ${res.imported_rows} records into the Prevention & Healing registry.`,
      });
      setAnalysisResult(null);
      setImportFile(null);
      loadWorkspaceData();
    } catch (err) {
      toast({
        title: "Execution Error",
        description: err.message || "Failed to commit import records.",
        variant: "destructive",
      });
    } finally {
      setExecutingBatchId(null);
    }
  };

  // Filtered views
  const filteredEP = enhancementPrograms.filter(
    (p) =>
      p.program?.toLowerCase().includes(epSearch.toLowerCase()) ||
      p.program_activity?.toLowerCase().includes(epSearch.toLowerCase()) ||
      p.employee_name_raw?.toLowerCase().includes(epSearch.toLowerCase()) ||
      p.city?.toLowerCase().includes(epSearch.toLowerCase())
  );

  const filteredFSR = familySupportRecords.filter(
    (f) =>
      f.program?.toLowerCase().includes(fsrSearch.toLowerCase()) ||
      f.support_type?.toLowerCase().includes(fsrSearch.toLowerCase()) ||
      f.employee_name_raw?.toLowerCase().includes(fsrSearch.toLowerCase()) ||
      f.client_ref_legacy_id?.toLowerCase().includes(fsrSearch.toLowerCase())
  );

  const filteredONS = otherNationsRecords.filter(
    (o) =>
      o.worker_name_raw?.toLowerCase().includes(onsSearch.toLowerCase()) ||
      o.family_reference_raw?.toLowerCase().includes(onsSearch.toLowerCase()) ||
      o.service_type?.toLowerCase().includes(onsSearch.toLowerCase()) ||
      o.other_community?.toLowerCase().includes(onsSearch.toLowerCase())
  );

  const filteredStaff = pendingStaffList.filter((s) => {
    if (staffFilter === "ALL") return true;
    return s.onboarding_status === staffFilter;
  });

  const filteredClients = clientRefsList.filter((c) => {
    if (clientFilter === "ALL") return true;
    return c.status === clientFilter;
  });

  // Chart prep for overview
  const expenseBreakdownData = summary?.expense_breakdown
    ? Object.entries(summary.expense_breakdown)
        .filter(([, val]) => val > 0)
        .map(([key, val]) => ({
          name: key.replace(/_/g, " ").toUpperCase(),
          value: Number(val),
        }))
    : [];

  const programDemographicsData = summary?.enhancement_programs?.participants_breakdown
    ? Object.entries(summary.enhancement_programs.participants_breakdown).map(([k, v]) => ({
        name: k.replace(/_/g, " "),
        count: v,
      }))
    : [];

  const unresolvedClientsCount = clientRefsList.filter((c) => c.status === "UNRESOLVED").length;
  const pendingStaffCount = pendingStaffList.filter((s) => s.onboarding_status === "PENDING" || s.onboarding_status === "EMAIL_NEEDED").length;

  return (
    <div className="space-y-6">
      {/* ── Page Header & Controls ── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border pb-5">
        <div>
          <div className="flex items-center gap-2">
            <span className="p-2 rounded-lg bg-amber-500/10 text-amber-600">
              <Sparkles className="w-6 h-6" />
            </span>
            <h1 className="text-2xl font-bold font-heading text-foreground tracking-tight">
              Prevention & Healing Records Workspace
            </h1>
          </div>
          <p className="text-sm text-muted-foreground mt-1">
            Department Team 3 · Comprehensive tracking for Enhancement Programs, Family Support Services, and Other Nations Support.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 bg-card border border-border px-3 py-1.5 rounded-lg">
            <Calendar className="w-4 h-4 text-muted-foreground" />
            <span className="text-xs font-medium text-muted-foreground">Fiscal Year:</span>
            <Select value={fiscalYear} onValueChange={(v) => setFiscalYear(v)}>
              <SelectTrigger className="h-8 border-none bg-transparent shadow-none w-[120px] text-xs font-semibold">
                <SelectValue placeholder="Fiscal Year" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="2026-2027">2026-2027</SelectItem>
                <SelectItem value="2025-2026">2025-2026</SelectItem>
                <SelectItem value="2027-2028">2027-2028</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <Button
            variant="outline"
            size="sm"
            onClick={loadWorkspaceData}
            disabled={loading}
            className="gap-2"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
            Refresh
          </Button>

          <Button
            size="sm"
            onClick={() => setActiveTab("import_wizard")}
            className="bg-amber-600 hover:bg-amber-700 text-white gap-2"
          >
            <UploadCloud className="w-4 h-4" />
            Safe Excel Import
          </Button>
        </div>
      </div>

      {/* ── Navigation Tabs ── */}
      <div className="flex items-center gap-2 overflow-x-auto border-b border-border pb-2 text-sm font-medium">
        <button
          onClick={() => setActiveTab("overview")}
          className={`flex items-center gap-2 px-3 py-2 rounded-lg transition-colors ${
            activeTab === "overview"
              ? "bg-primary text-primary-foreground font-semibold"
              : "text-muted-foreground hover:bg-muted"
          }`}
        >
          <PieChartIcon className="w-4 h-4" />
          Overview & Metrics
        </button>

        <button
          onClick={() => setActiveTab("enhancement_programs")}
          className={`flex items-center gap-2 px-3 py-2 rounded-lg transition-colors ${
            activeTab === "enhancement_programs"
              ? "bg-primary text-primary-foreground font-semibold"
              : "text-muted-foreground hover:bg-muted"
          }`}
        >
          <Sparkles className="w-4 h-4" />
          Enhancement Programs ({enhancementPrograms.length})
        </button>

        <button
          onClick={() => setActiveTab("family_support")}
          className={`flex items-center gap-2 px-3 py-2 rounded-lg transition-colors ${
            activeTab === "family_support"
              ? "bg-primary text-primary-foreground font-semibold"
              : "text-muted-foreground hover:bg-muted"
          }`}
        >
          <HeartHandshake className="w-4 h-4" />
          Family Support Services ({familySupportRecords.length})
        </button>

        <button
          onClick={() => setActiveTab("other_nations")}
          className={`flex items-center gap-2 px-3 py-2 rounded-lg transition-colors ${
            activeTab === "other_nations"
              ? "bg-primary text-primary-foreground font-semibold"
              : "text-muted-foreground hover:bg-muted"
          }`}
        >
          <Shield className="w-4 h-4" />
          Other Nations / Eagle Nest ({otherNationsRecords.length})
        </button>

        <button
          onClick={() => setActiveTab("staff_onboarding")}
          className={`flex items-center gap-2 px-3 py-2 rounded-lg transition-colors ${
            activeTab === "staff_onboarding"
              ? "bg-primary text-primary-foreground font-semibold"
              : "text-muted-foreground hover:bg-muted"
          }`}
        >
          <Users className="w-4 h-4" />
          Staff Onboarding
          {pendingStaffCount > 0 && (
            <Badge variant="destructive" className="ml-1 text-[10px] px-1.5 py-0 h-4">
              {pendingStaffCount} Pending
            </Badge>
          )}
        </button>

        <button
          onClick={() => setActiveTab("client_reconciliation")}
          className={`flex items-center gap-2 px-3 py-2 rounded-lg transition-colors ${
            activeTab === "client_reconciliation"
              ? "bg-primary text-primary-foreground font-semibold"
              : "text-muted-foreground hover:bg-muted"
          }`}
        >
          <ShieldCheck className="w-4 h-4" />
          Client Reconciliation
          {unresolvedClientsCount > 0 && (
            <Badge variant="warning" className="ml-1 text-[10px] px-1.5 py-0 h-4 bg-amber-500 text-white">
              {unresolvedClientsCount} Unresolved
            </Badge>
          )}
        </button>

        <button
          onClick={() => setActiveTab("import_wizard")}
          className={`flex items-center gap-2 px-3 py-2 rounded-lg transition-colors ${
            activeTab === "import_wizard"
              ? "bg-primary text-primary-foreground font-semibold"
              : "text-muted-foreground hover:bg-muted"
          }`}
        >
          <UploadCloud className="w-4 h-4" />
          Excel Import Wizard
        </button>

        <button
          onClick={() => setActiveTab("annual_summary")}
          className={`flex items-center gap-2 px-3 py-2 rounded-lg transition-colors ${
            activeTab === "annual_summary"
              ? "bg-primary text-primary-foreground font-semibold"
              : "text-muted-foreground hover:bg-muted"
          }`}
        >
          <FileText className="w-4 h-4" />
          Annual Summary & Audit
        </button>
      </div>

      {/* ───────────────────────────────────────────────────────────── */}
      {/* 1. OVERVIEW & METRICS TAB */}
      {/* ───────────────────────────────────────────────────────────── */}
      {activeTab === "overview" && (
        <div className="space-y-6">
          {/* Top KPI Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <StatCard
              title="Combined Prevention Spend"
              value={`$${(summary?.combined_total_cost || 0).toLocaleString("en-CA", {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2,
              })}`}
              icon={DollarSign}
              color="primary"
              changeLabel={`Fiscal Year ${fiscalYear}`}
            />
            <StatCard
              title="Enhancement Program Families"
              value={summary?.enhancement_programs?.total_families || 0}
              icon={Sparkles}
              color="accent"
              changeLabel={`${summary?.enhancement_programs?.total_records || 0} recorded sessions`}
            />
            <StatCard
              title="Family Support Services"
              value={`$${(summary?.family_support?.total_cost || 0).toLocaleString("en-CA", {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2,
              })}`}
              icon={HeartHandshake}
              color="success"
              changeLabel={`${summary?.family_support?.total_records || 0} direct support events`}
            />
            <StatCard
              title="Other Nations Support Cost"
              value={`$${(summary?.other_nations_support?.total_cost || 0).toLocaleString("en-CA", {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2,
              })}`}
              icon={Shield}
              color="warning"
              changeLabel={`${summary?.other_nations_support?.total_records || 0} Eagle Nest records`}
            />
          </div>

          {/* Alert Warnings if pending items exist */}
          {(unresolvedClientsCount > 0 || pendingStaffCount > 0) && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {pendingStaffCount > 0 && (
                <div className="bg-amber-500/10 border border-amber-500/30 rounded-xl p-4 flex items-start gap-3">
                  <AlertCircle className="w-5 h-5 text-amber-600 mt-0.5 shrink-0" />
                  <div className="flex-1">
                    <h4 className="text-sm font-semibold text-amber-800">
                      Inactive Staff Onboarding Required ({pendingStaffCount} Staff)
                    </h4>
                    <p className="text-xs text-amber-700 mt-1">
                      Employees detected in Excel trackers have no active logins or verified emails. Link verified email addresses to complete activation.
                    </p>
                    <Button
                      variant="link"
                      size="sm"
                      onClick={() => setActiveTab("staff_onboarding")}
                      className="text-amber-800 p-0 h-auto text-xs font-semibold mt-2 gap-1"
                    >
                      View Pending Profiles <ArrowRight className="w-3 h-3" />
                    </Button>
                  </div>
                </div>
              )}

              {unresolvedClientsCount > 0 && (
                <div className="bg-blue-500/10 border border-blue-500/30 rounded-xl p-4 flex items-start gap-3">
                  <ShieldCheck className="w-5 h-5 text-blue-600 mt-0.5 shrink-0" />
                  <div className="flex-1">
                    <h4 className="text-sm font-semibold text-blue-800">
                      Client ID Reconciliation Queue ({unresolvedClientsCount} RedMane IDs)
                    </h4>
                    <p className="text-xs text-blue-700 mt-1">
                      Legacy RedMane identifiers (RM-...) are quarantined. Review and link to verified 10-digit canonical Person records.
                    </p>
                    <Button
                      variant="link"
                      size="sm"
                      onClick={() => setActiveTab("client_reconciliation")}
                      className="text-blue-800 p-0 h-auto text-xs font-semibold mt-2 gap-1"
                    >
                      Reconcile Client Queue <ArrowRight className="w-3 h-3" />
                    </Button>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Charts Row */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Expense Method Breakdown */}
            <Card>
              <CardHeader>
                <CardTitle className="text-base font-semibold flex items-center gap-2">
                  <DollarSign className="w-4 h-4 text-emerald-600" />
                  Expenditure Distribution by Payment Method
                </CardTitle>
                <CardDescription className="text-xs">
                  Controlled breakdown across Gift Cards, Purchase Orders, EFTs, and Cheques
                </CardDescription>
              </CardHeader>
              <CardContent className="h-[280px]">
                {expenseBreakdownData.length > 0 ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={expenseBreakdownData}
                        cx="50%"
                        cy="50%"
                        innerRadius={60}
                        outerRadius={95}
                        paddingAngle={4}
                        dataKey="value"
                      >
                        {expenseBreakdownData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip
                        formatter={(val) =>
                          `$${Number(val).toLocaleString("en-CA", {
                            minimumFractionDigits: 2,
                          })}`
                        }
                      />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="h-full flex items-center justify-center text-xs text-muted-foreground">
                    No expense data recorded for fiscal year {fiscalYear}.
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Demographics Breakdown */}
            <Card>
              <CardHeader>
                <CardTitle className="text-base font-semibold flex items-center gap-2">
                  <Users className="w-4 h-4 text-primary" />
                  Program Participant Demographics
                </CardTitle>
                <CardDescription className="text-xs">
                  Age categories and family member participation in Enhancement Programs
                </CardDescription>
              </CardHeader>
              <CardContent className="h-[280px]">
                {programDemographicsData.length > 0 ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={programDemographicsData} margin={{ top: 20, right: 20, left: -10, bottom: 20 }}>
                      <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
                      <XAxis dataKey="name" tick={{ fontSize: 10 }} />
                      <YAxis tick={{ fontSize: 10 }} />
                      <Tooltip />
                      <Bar dataKey="count" fill="hsl(var(--primary))" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="h-full flex items-center justify-center text-xs text-muted-foreground">
                    No demographic data recorded for fiscal year {fiscalYear}.
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Quick Action Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <Card
              className="cursor-pointer hover:border-primary/50 transition-colors"
              onClick={() => {
                setActiveTab("enhancement_programs");
                setEpModalOpen(true);
              }}
            >
              <CardContent className="p-4 flex items-center gap-3">
                <span className="p-2.5 rounded-lg bg-red-500/10 text-red-600">
                  <Plus className="w-5 h-5" />
                </span>
                <div>
                  <h4 className="text-sm font-semibold">Record Enhancement Program</h4>
                  <p className="text-xs text-muted-foreground">Log workshop, healing circle, or cultural camp</p>
                </div>
              </CardContent>
            </Card>

            <Card
              className="cursor-pointer hover:border-primary/50 transition-colors"
              onClick={() => {
                setActiveTab("family_support");
                setFsrModalOpen(true);
              }}
            >
              <CardContent className="p-4 flex items-center gap-3">
                <span className="p-2.5 rounded-lg bg-emerald-500/10 text-emerald-600">
                  <Plus className="w-5 h-5" />
                </span>
                <div>
                  <h4 className="text-sm font-semibold">Record Family Support</h4>
                  <p className="text-xs text-muted-foreground">Log direct emergency relief or family wellness</p>
                </div>
              </CardContent>
            </Card>

            <Card
              className="cursor-pointer hover:border-primary/50 transition-colors"
              onClick={() => {
                setActiveTab("other_nations");
                setOnsModalOpen(true);
              }}
            >
              <CardContent className="p-4 flex items-center gap-3">
                <span className="p-2.5 rounded-lg bg-amber-500/10 text-amber-600">
                  <Plus className="w-5 h-5" />
                </span>
                <div>
                  <h4 className="text-sm font-semibold">Record Other Nations Support</h4>
                  <p className="text-xs text-muted-foreground">Eagle Nest off-reserve support tracking</p>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      )}

      {/* ───────────────────────────────────────────────────────────── */}
      {/* 2. ENHANCEMENT PROGRAMS TAB */}
      {/* ───────────────────────────────────────────────────────────── */}
      {activeTab === "enhancement_programs" && (
        <div className="space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div className="relative flex-1 max-w-md">
              <Search className="w-4 h-4 absolute left-3 top-2.5 text-muted-foreground" />
              <Input
                placeholder="Search by program, activity, staff, or city..."
                value={epSearch}
                onChange={(e) => setEpSearch(e.target.value)}
                className="pl-9 h-9 text-xs"
              />
            </div>
            <Button
              size="sm"
              onClick={() => setEpModalOpen(true)}
              className="bg-primary hover:bg-primary/90 text-primary-foreground gap-1.5"
            >
              <Plus className="w-4 h-4" />
              New Enhancement Program
            </Button>
          </div>

          <div className="border border-border rounded-xl overflow-hidden bg-card">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-muted/60 text-muted-foreground font-semibold border-b border-border">
                  <tr>
                    <th className="p-3">Date</th>
                    <th className="p-3">Program & Activity</th>
                    <th className="p-3">Facilitator / Worker</th>
                    <th className="p-3">Location</th>
                    <th className="p-3 text-center">Families</th>
                    <th className="p-3 text-center">Participants</th>
                    <th className="p-3">Account Code</th>
                    <th className="p-3 text-right">Total Cost</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {filteredEP.length > 0 ? (
                    filteredEP.map((p) => (
                      <tr key={p.id} className="hover:bg-muted/30 transition-colors">
                        <td className="p-3 font-mono text-[11px] text-muted-foreground whitespace-nowrap">
                          {p.record_date || "—"}
                        </td>
                        <td className="p-3">
                          <div className="font-semibold text-foreground">{p.program}</div>
                          {p.program_activity && (
                            <div className="text-[11px] text-muted-foreground truncate max-w-xs">
                              {p.program_activity}
                            </div>
                          )}
                        </td>
                        <td className="p-3">
                          <span className="font-medium text-foreground">
                            {p.employee_name_raw || "Unassigned"}
                          </span>
                          {p.position_raw && (
                            <div className="text-[10px] text-muted-foreground">{p.position_raw}</div>
                          )}
                        </td>
                        <td className="p-3 text-muted-foreground">
                          {p.city ? `${p.city}, ${p.province || "SK"}` : "—"}
                        </td>
                        <td className="p-3 text-center font-medium">
                          <Badge variant="outline" className="text-[10px]">
                            {p.total_families || p.families_in_province + p.families_out_of_province}
                          </Badge>
                        </td>
                        <td className="p-3 text-center font-medium">
                          <Badge variant="secondary" className="text-[10px]">
                            {p.total_participants || 0}
                          </Badge>
                        </td>
                        <td className="p-3 font-mono text-[11px] text-muted-foreground">
                          {p.account_code || "—"}{p.subcode ? `-${p.subcode}` : ""}
                        </td>
                        <td className="p-3 text-right font-mono font-semibold text-foreground whitespace-nowrap">
                          ${Number(p.total_cost || 0).toLocaleString("en-CA", { minimumFractionDigits: 2 })}
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={8} className="p-8 text-center text-muted-foreground">
                        No Enhancement Program records match your filters.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* ───────────────────────────────────────────────────────────── */}
      {/* 3. FAMILY SUPPORT SERVICES TAB */}
      {/* ───────────────────────────────────────────────────────────── */}
      {activeTab === "family_support" && (
        <div className="space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div className="relative flex-1 max-w-md">
              <Search className="w-4 h-4 absolute left-3 top-2.5 text-muted-foreground" />
              <Input
                placeholder="Search by support type, worker, RedMane ID..."
                value={fsrSearch}
                onChange={(e) => setFsrSearch(e.target.value)}
                className="pl-9 h-9 text-xs"
              />
            </div>
            <Button
              size="sm"
              onClick={() => setFsrModalOpen(true)}
              className="bg-primary hover:bg-primary/90 text-primary-foreground gap-1.5"
            >
              <Plus className="w-4 h-4" />
              New Family Support Record
            </Button>
          </div>

          <div className="border border-border rounded-xl overflow-hidden bg-card">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-muted/60 text-muted-foreground font-semibold border-b border-border">
                  <tr>
                    <th className="p-3">Date</th>
                    <th className="p-3">Support Type / Program</th>
                    <th className="p-3">Worker</th>
                    <th className="p-3">Client Reference</th>
                    <th className="p-3">Reconciliation Status</th>
                    <th className="p-3 text-center">Participants</th>
                    <th className="p-3">Financial Code</th>
                    <th className="p-3 text-right">Cost</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {filteredFSR.length > 0 ? (
                    filteredFSR.map((f) => (
                      <tr key={f.id} className="hover:bg-muted/30 transition-colors">
                        <td className="p-3 font-mono text-[11px] text-muted-foreground whitespace-nowrap">
                          {f.record_date || "—"}
                        </td>
                        <td className="p-3">
                          <div className="font-semibold text-foreground">{f.support_type || f.program}</div>
                          {f.program && f.support_type && (
                            <div className="text-[11px] text-muted-foreground">{f.program}</div>
                          )}
                        </td>
                        <td className="p-3">
                          <span className="font-medium text-foreground">
                            {f.employee_name_raw || "Unassigned"}
                          </span>
                        </td>
                        <td className="p-3 font-mono text-[11px]">
                          {f.client_ref_legacy_id ? (
                            <span className="px-2 py-0.5 rounded bg-muted font-bold text-foreground">
                              {f.client_ref_legacy_id}
                            </span>
                          ) : (
                            <span className="text-muted-foreground">General</span>
                          )}
                        </td>
                        <td className="p-3">
                          {f.client_match_status === "CONFIRMED" || f.person_id ? (
                            <Badge variant="outline" className="text-[10px] text-emerald-700 border-emerald-300 bg-emerald-50">
                              ✓ Canonical Person Linked
                            </Badge>
                          ) : f.client_ref_legacy_id ? (
                            <Badge variant="outline" className="text-[10px] text-amber-700 border-amber-300 bg-amber-50">
                              ⚠ RedMane Unreconciled
                            </Badge>
                          ) : (
                            <span className="text-muted-foreground text-[10px]">No Legacy ID</span>
                          )}
                        </td>
                        <td className="p-3 text-center">
                          <Badge variant="secondary" className="text-[10px]">
                            {(f.participants_children_0_12 || 0) +
                              (f.participants_youth_13_17 || 0) +
                              (f.participants_adults_18_plus || 0)}
                          </Badge>
                        </td>
                        <td className="p-3 font-mono text-[11px] text-muted-foreground">
                          {f.account_code || "41000"}-{f.subcode || "213"}
                        </td>
                        <td className="p-3 text-right font-mono font-semibold text-foreground whitespace-nowrap">
                          ${Number(f.total_cost || 0).toLocaleString("en-CA", { minimumFractionDigits: 2 })}
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={8} className="p-8 text-center text-muted-foreground">
                        No Family Support records found.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* ───────────────────────────────────────────────────────────── */}
      {/* 4. OTHER NATIONS / EAGLE NEST TAB */}
      {/* ───────────────────────────────────────────────────────────── */}
      {activeTab === "other_nations" && (
        <div className="space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div className="relative flex-1 max-w-md">
              <Search className="w-4 h-4 absolute left-3 top-2.5 text-muted-foreground" />
              <Input
                placeholder="Search by worker, family reference, community..."
                value={onsSearch}
                onChange={(e) => setOnsSearch(e.target.value)}
                className="pl-9 h-9 text-xs"
              />
            </div>
            <Button
              size="sm"
              onClick={() => setOnsModalOpen(true)}
              className="bg-primary hover:bg-primary/90 text-primary-foreground gap-1.5"
            >
              <Plus className="w-4 h-4" />
              New Other Nations Record
            </Button>
          </div>

          <div className="border border-border rounded-xl overflow-hidden bg-card">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-muted/60 text-muted-foreground font-semibold border-b border-border">
                  <tr>
                    <th className="p-3">Date</th>
                    <th className="p-3">Family / Client Ref</th>
                    <th className="p-3">Worker</th>
                    <th className="p-3">Service Type</th>
                    <th className="p-3">Jurisdiction</th>
                    <th className="p-3">Cowessess Connection / Community</th>
                    <th className="p-3">Historical Ref</th>
                    <th className="p-3 text-right">Cost</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {filteredONS.length > 0 ? (
                    filteredONS.map((o) => (
                      <tr key={o.id} className="hover:bg-muted/30 transition-colors">
                        <td className="p-3 font-mono text-[11px] text-muted-foreground whitespace-nowrap">
                          {o.record_date || "—"}
                        </td>
                        <td className="p-3 font-semibold text-foreground">
                          {o.family_reference_raw || "Anonymous"}
                        </td>
                        <td className="p-3 text-muted-foreground">
                          {o.worker_name_raw || "—"}
                        </td>
                        <td className="p-3">
                          <span className="font-medium text-foreground">{o.service_type || "Support"}</span>
                        </td>
                        <td className="p-3">
                          {o.on_reserve ? (
                            <Badge variant="outline" className="text-[10px] bg-emerald-50 text-emerald-700 border-emerald-200">
                              On Reserve
                            </Badge>
                          ) : (
                            <Badge variant="outline" className="text-[10px] bg-blue-50 text-blue-700 border-blue-200">
                              Off Reserve
                            </Badge>
                          )}
                        </td>
                        <td className="p-3 text-muted-foreground">
                          {o.cowessess_connection || o.other_community || "—"}
                        </td>
                        <td className="p-3 font-mono text-[11px] text-muted-foreground">
                          {o.historical_reference_number || "—"}
                        </td>
                        <td className="p-3 text-right font-mono font-semibold text-foreground whitespace-nowrap">
                          ${Number(o.cost || 0).toLocaleString("en-CA", { minimumFractionDigits: 2 })}
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={8} className="p-8 text-center text-muted-foreground">
                        No Other Nations support records found.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* ───────────────────────────────────────────────────────────── */}
      {/* 5. INACTIVE STAFF ONBOARDING TAB */}
      {/* ───────────────────────────────────────────────────────────── */}
      {activeTab === "staff_onboarding" && (
        <div className="space-y-4">
          <div className="bg-amber-500/10 border border-amber-500/30 rounded-xl p-4">
            <div className="flex items-start gap-3">
              <AlertTriangle className="w-5 h-5 text-amber-600 mt-0.5 shrink-0" />
              <div>
                <h3 className="text-sm font-semibold text-amber-900">
                  Data Governance & Inactive Staff Quarantine (Account Activation Disabled by Policy)
                </h3>
                <p className="text-xs text-amber-800 mt-1 leading-relaxed">
                  The original Excel tracker contains staff names and positions but <strong>zero email addresses</strong>. Under CRBCL security policies, direct staff login activation is disabled by default (<code className="font-mono text-[11px] bg-amber-200/60 px-1 py-0.5 rounded">CRBCL_PH_STAFF_ACTIVATION_ENABLED=false</code>). Real employees remain quarantined in this queue. Clicking <em>Verify & Link Profile</em> verifies the employee's work email and links their HR Employee profile and historical program records (status: <strong>VERIFIED_PENDING_ACCOUNT</strong>), but <strong>strictly does not activate login credentials</strong>.
                </p>
              </div>
            </div>
          </div>

          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div className="flex items-center gap-2">
              <span className="text-xs font-medium text-muted-foreground">Filter Status:</span>
              <div className="flex gap-1">
                {["ALL", "PENDING", "EMAIL_NEEDED", "ACTIVATED"].map((st) => (
                  <Button
                    key={st}
                    variant={staffFilter === st ? "default" : "outline"}
                    size="sm"
                    onClick={() => setStaffFilter(st)}
                    className="h-7 text-xs px-2.5"
                  >
                    {st}
                  </Button>
                ))}
              </div>
            </div>
          </div>

          <div className="border border-border rounded-xl overflow-hidden bg-card">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-muted/60 text-muted-foreground font-semibold border-b border-border">
                  <tr>
                    <th className="p-3">Staff Name (from Tracker)</th>
                    <th className="p-3">Detected Position</th>
                    <th className="p-3">Department</th>
                    <th className="p-3">Email Status</th>
                    <th className="p-3">Onboarding State</th>
                    <th className="p-3 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {filteredStaff.length > 0 ? (
                    filteredStaff.map((s) => (
                      <tr key={s.id} className="hover:bg-muted/30 transition-colors">
                        <td className="p-3">
                          <div className="font-semibold text-foreground">
                            {s.display_name_from_excel || `${s.first_name} ${s.last_name}`}
                          </div>
                        </td>
                        <td className="p-3 text-muted-foreground">{s.position || "Staff"}</td>
                        <td className="p-3 text-muted-foreground">{s.department || "Prevention & Healing"}</td>
                        <td className="p-3">
                          {s.email ? (
                            <span className="font-mono text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                              {s.email}
                            </span>
                          ) : (
                            <Badge variant="outline" className="text-[10px] text-red-600 border-red-200 bg-red-50">
                              Missing Email
                            </Badge>
                          )}
                        </td>
                        <td className="p-3">
                          {s.onboarding_status === "ACCOUNT_ACTIVATED" ? (
                            <Badge variant="outline" className="text-[10px] text-emerald-700 border-emerald-200 bg-emerald-50">
                              ✓ Active Login Account
                            </Badge>
                          ) : s.onboarding_status === "VERIFIED_PENDING_ACCOUNT" || s.onboarding_status === "ACTIVATED" ? (
                            <Badge variant="outline" className="text-[10px] text-blue-700 border-blue-200 bg-blue-50">
                              ✓ Verified Profile (No Login)
                            </Badge>
                          ) : (
                            <Badge variant="outline" className="text-[10px] text-amber-700 border-amber-200 bg-amber-50">
                              Pending Verification (No Login)
                            </Badge>
                          )}
                        </td>
                        <td className="p-3 text-right">
                          {s.onboarding_status !== "ACCOUNT_ACTIVATED" && s.onboarding_status !== "VERIFIED_PENDING_ACCOUNT" && s.onboarding_status !== "ACTIVATED" ? (
                            <Button
                              size="sm"
                              onClick={() => {
                                setSelectedStaff(s);
                                setStaffEmail(s.email || "");
                                setStaffPosition(s.position || "");
                                setActivateStaffModalOpen(true);
                              }}
                              className="h-7 text-xs bg-amber-600 hover:bg-amber-700 text-white gap-1"
                            >
                              <UserPlus className="w-3.5 h-3.5" />
                              Verify & Link Profile
                            </Button>
                          ) : (
                            <span className="text-xs text-muted-foreground">Profile Verified</span>
                          )}
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={6} className="p-8 text-center text-muted-foreground">
                        No pending staff profiles match the selected filter.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* ───────────────────────────────────────────────────────────── */}
      {/* 6. CLIENT RECONCILIATION QUEUE TAB */}
      {/* ───────────────────────────────────────────────────────────── */}
      {activeTab === "client_reconciliation" && (
        <div className="space-y-4">
          <div className="bg-blue-500/10 border border-blue-500/30 rounded-xl p-4">
            <div className="flex items-start gap-3">
              <ShieldCheck className="w-5 h-5 text-blue-600 mt-0.5 shrink-0" />
              <div>
                <h3 className="text-sm font-semibold text-blue-900">
                  Client Identity Safeguard & RedMane ID Reconciliation
                </h3>
                <p className="text-xs text-blue-800 mt-1 leading-relaxed">
                  CRBCL canon requires all true client records to be anchored to a 10-digit canonical Person ID (<code>Person.person_id_number</code>). Legacy RedMane codes (<code>RM-...</code>) or band status numbers cannot be automatically assumed to be valid Person IDs. Unreconciled client references are isolated here for privacy protection until an authorized supervisor links them to a verified Person.
                </p>
              </div>
            </div>
          </div>

          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div className="flex items-center gap-2">
              <span className="text-xs font-medium text-muted-foreground">Filter Status:</span>
              <div className="flex gap-1">
                {["ALL", "UNRESOLVED", "CONFIRMED", "REJECTED"].map((st) => (
                  <Button
                    key={st}
                    variant={clientFilter === st ? "default" : "outline"}
                    size="sm"
                    onClick={() => setClientFilter(st)}
                    className="h-7 text-xs px-2.5"
                  >
                    {st}
                  </Button>
                ))}
              </div>
            </div>
          </div>

          <div className="border border-border rounded-xl overflow-hidden bg-card">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-muted/60 text-muted-foreground font-semibold border-b border-border">
                  <tr>
                    <th className="p-3">Legacy Identifier</th>
                    <th className="p-3">Identifier Type</th>
                    <th className="p-3">Status</th>
                    <th className="p-3">Linked Canonical Person</th>
                    <th className="p-3">Confirmed At</th>
                    <th className="p-3 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {filteredClients.length > 0 ? (
                    filteredClients.map((c) => (
                      <tr key={c.id} className="hover:bg-muted/30 transition-colors">
                        <td className="p-3 font-mono font-bold text-foreground">{c.legacy_id}</td>
                        <td className="p-3 text-muted-foreground">{c.legacy_id_type}</td>
                        <td className="p-3">
                          {c.status === "CONFIRMED" ? (
                            <Badge variant="outline" className="text-[10px] text-emerald-700 border-emerald-300 bg-emerald-50">
                              ✓ Confirmed Link
                            </Badge>
                          ) : c.status === "REJECTED" ? (
                            <Badge variant="outline" className="text-[10px] text-red-600 border-red-200 bg-red-50">
                              Rejected
                            </Badge>
                          ) : (
                            <Badge variant="outline" className="text-[10px] text-amber-700 border-amber-300 bg-amber-50">
                              Unresolved Quarantine
                            </Badge>
                          )}
                        </td>
                        <td className="p-3 font-mono text-[11px]">
                          {c.person ? (
                            <span className="text-foreground font-semibold">
                              #{c.person.person_id_number} · {c.person.first_name} {c.person.last_name}
                            </span>
                          ) : (
                            <span className="text-muted-foreground">—</span>
                          )}
                        </td>
                        <td className="p-3 text-muted-foreground font-mono text-[11px]">
                          {c.confirmed_at ? new Date(c.confirmed_at).toLocaleDateString() : "—"}
                        </td>
                        <td className="p-3 text-right">
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => {
                              setSelectedClientRef(c);
                              setPersonQuery("");
                              setPersonResults([]);
                              setSelectedPersonId("");
                              setReconcileClientModalOpen(true);
                            }}
                            className="h-7 text-xs gap-1"
                          >
                            <ShieldCheck className="w-3.5 h-3.5 text-primary" />
                            Reconcile Match
                          </Button>
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={6} className="p-8 text-center text-muted-foreground">
                        No client references found matching the filter.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* ───────────────────────────────────────────────────────────── */}
      {/* 7. SAFE 8-STEP EXCEL IMPORT WIZARD TAB */}
      {/* ───────────────────────────────────────────────────────────── */}
      {activeTab === "import_wizard" && (
        <div className="space-y-6">
          {/* Wizard Stepper Card */}
          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <span className="p-2 rounded-lg bg-primary/10 text-primary">
                  <FileSpreadsheet className="w-5 h-5" />
                </span>
                <div>
                  <CardTitle className="text-base font-bold">
                    Safe 8-Step Excel Import Protocol
                  </CardTitle>
                  <CardDescription className="text-xs">
                    Rigorous parsing, anomaly detection, staff matching, client ID quarantine, and two-person approval.
                  </CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Rollout Control Policy Notice */}
              <div className="bg-blue-500/10 border border-blue-500/30 rounded-xl p-3.5 flex items-start gap-3">
                <AlertCircle className="w-5 h-5 text-blue-600 mt-0.5 shrink-0" />
                <div className="text-xs">
                  <div className="font-semibold text-blue-950">
                    Historical Import Execution Rollout Control (<code className="font-mono text-[10px] bg-blue-200/60 px-1 py-0.5 rounded">CRBCL_PH_REAL_IMPORT_ENABLED=false</code>)
                  </div>
                  <p className="text-blue-800 mt-0.5 leading-relaxed">
                    Live database ingestion of historical spreadsheets is strictly disabled by default. Administrators can safely upload workbooks, parse sheets, validate financial calculations, preview row ledgers, and detect duplicates. Database write operations remain locked until formal release authorization is granted by CRBCL leadership.
                  </p>
                </div>
              </div>

              {/* Step indicator */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-xs">
                <div className="p-2.5 rounded-lg border border-border bg-muted/30">
                  <span className="font-bold text-primary">Step 1: Upload</span>
                  <p className="text-[11px] text-muted-foreground mt-0.5">Select workbook & worksheet</p>
                </div>
                <div className="p-2.5 rounded-lg border border-border bg-muted/30">
                  <span className="font-bold text-primary">Step 2: Validate</span>
                  <p className="text-[11px] text-muted-foreground mt-0.5">Analyze dates & decimal costs</p>
                </div>
                <div className="p-2.5 rounded-lg border border-border bg-muted/30">
                  <span className="font-bold text-primary">Step 3: Reconcile</span>
                  <p className="text-[11px] text-muted-foreground mt-0.5">Quarantine RedMane & staff</p>
                </div>
                <div className="p-2.5 rounded-lg border border-border bg-muted/30">
                  <span className="font-bold text-primary">Step 4: Execute</span>
                  <p className="text-[11px] text-muted-foreground mt-0.5">Admin approval & DB commit</p>
                </div>
              </div>

              {/* Upload Controls */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2">
                <div>
                  <Label className="text-xs">Select Tracker Workbook (.xlsx)</Label>
                  <Input
                    type="file"
                    accept=".xlsx, .xls"
                    onChange={handleFileChange}
                    className="mt-1 h-9 text-xs file:text-xs"
                  />
                  {importFile && (
                    <p className="text-[11px] text-muted-foreground mt-1">
                      Loaded: {importFile.name} ({(importFile.size / 1024).toFixed(1)} KB)
                    </p>
                  )}
                </div>

                <div>
                  <Label className="text-xs">Worksheet Target</Label>
                  <Select
                    value={importWorksheet}
                    onValueChange={(v) => {
                      setImportWorksheet(v);
                      if (v === "Enhancement Programs") setImportRecordType("ENHANCEMENT_PROGRAMS");
                      else if (v === "Family Support") setImportRecordType("FAMILY_SUPPORT");
                      else setImportRecordType("OTHER_NATIONS");
                    }}
                  >
                    <SelectTrigger className="mt-1 h-9 text-xs">
                      <SelectValue placeholder="Choose Sheet" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Enhancement Programs">Enhancement Programs</SelectItem>
                      <SelectItem value="Family Support">Family Support</SelectItem>
                      <SelectItem value="DATA (Dec-Mar)">DATA (Dec-Mar)</SelectItem>
                      <SelectItem value="Sheet1">Sheet1 (Eagle Nest Other Nations)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label className="text-xs">Record Entity Type</Label>
                  <Select value={importRecordType} onValueChange={(v) => setImportRecordType(v)}>
                    <SelectTrigger className="mt-1 h-9 text-xs">
                      <SelectValue placeholder="Record Type" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="ENHANCEMENT_PROGRAMS">Enhancement Programs</SelectItem>
                      <SelectItem value="FAMILY_SUPPORT">Family Support Records</SelectItem>
                      <SelectItem value="OTHER_NATIONS">Other Nations (Eagle Nest)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="flex justify-end pt-2">
                <Button
                  onClick={handleAnalyzeWorkbook}
                  disabled={!importFile || analyzingImport}
                  className="bg-primary hover:bg-primary/90 text-primary-foreground gap-2 text-xs"
                >
                  <UploadCloud className={`w-4 h-4 ${analyzingImport ? "animate-spin" : ""}`} />
                  {analyzingImport ? "Parsing & Validating Workbook..." : "Analyze & Preview Import"}
                </Button>
              </div>

              {/* Analysis Result Preview */}
              {analysisResult && (
                <div className="border border-border rounded-xl p-4 bg-muted/20 space-y-4">
                  <div className="flex items-center justify-between border-b border-border pb-3">
                    <div>
                      <h4 className="text-sm font-bold text-foreground">
                        Batch Analysis Summary #{analysisResult.batch_id.slice(0, 8)}
                      </h4>
                      <p className="text-xs text-muted-foreground mt-0.5">
                        Status: <strong className="text-foreground">{analysisResult.status}</strong>
                      </p>
                    </div>

                    <div className="flex items-center gap-2">
                      {analysisResult.status === "AWAITING_APPROVAL" && (
                        <Button
                          size="sm"
                          onClick={() => handleApproveBatch(analysisResult.batch_id)}
                          className="bg-emerald-600 hover:bg-emerald-700 text-white text-xs gap-1"
                        >
                          <CheckCircle2 className="w-3.5 h-3.5" />
                          Approve Batch
                        </Button>
                      )}

                      {analysisResult.status === "APPROVED" && (
                        <Button
                          size="sm"
                          onClick={() => handleExecuteBatch(analysisResult.batch_id)}
                          disabled={executingBatchId === analysisResult.batch_id}
                          className="bg-primary hover:bg-primary/90 text-primary-foreground text-xs gap-1"
                        >
                          <Check className="w-3.5 h-3.5" />
                          {executingBatchId === analysisResult.batch_id
                            ? "Committing Records..."
                            : "Execute Import to Database"}
                        </Button>
                      )}
                    </div>
                  </div>

                  <div className="grid grid-cols-3 gap-3 text-center">
                    <div className="p-3 bg-card border border-border rounded-lg">
                      <div className="text-xl font-bold font-mono">{analysisResult.total_rows_analyzed}</div>
                      <div className="text-[11px] text-muted-foreground">Total Rows Parsed</div>
                    </div>
                    <div className="p-3 bg-card border border-emerald-300 rounded-lg text-emerald-700">
                      <div className="text-xl font-bold font-mono">{analysisResult.valid_rows}</div>
                      <div className="text-[11px]">Valid Clean Entries</div>
                    </div>
                    <div className="p-3 bg-card border border-red-300 rounded-lg text-red-600">
                      <div className="text-xl font-bold font-mono">{analysisResult.invalid_rows}</div>
                      <div className="text-[11px]">Validation Rejections</div>
                    </div>
                  </div>

                  {/* Issues lists */}
                  {analysisResult.employee_matching_issues?.length > 0 && (
                    <div className="p-3 bg-amber-500/10 border border-amber-500/20 rounded-lg text-xs space-y-1">
                      <span className="font-semibold text-amber-800">
                        Staff Members Assigned to Inactive Pending Profiles:
                      </span>
                      <div className="flex flex-wrap gap-1 mt-1">
                        {analysisResult.employee_matching_issues.map((name, i) => (
                          <Badge key={i} variant="outline" className="text-[10px] bg-amber-100/50">
                            {name}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}

                  {analysisResult.unresolved_client_ids?.length > 0 && (
                    <div className="p-3 bg-blue-500/10 border border-blue-500/20 rounded-lg text-xs space-y-1">
                      <span className="font-semibold text-blue-800">
                        RedMane Client Identifiers Quarantined in Reconciliation Queue:
                      </span>
                      <div className="flex flex-wrap gap-1 mt-1">
                        {analysisResult.unresolved_client_ids.map((id, i) => (
                          <Badge key={i} variant="outline" className="text-[10px] font-mono bg-blue-100/50">
                            {id}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Past Import Batches Audit History */}
          <div className="space-y-3">
            <h3 className="text-sm font-bold text-foreground">Import Batches Audit Trail</h3>
            <div className="border border-border rounded-xl overflow-hidden bg-card">
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-muted/60 text-muted-foreground font-semibold border-b border-border">
                    <tr>
                      <th className="p-3">Batch ID</th>
                      <th className="p-3">File Name</th>
                      <th className="p-3">Sheet & Type</th>
                      <th className="p-3">Rows</th>
                      <th className="p-3">Status</th>
                      <th className="p-3">Approved By</th>
                      <th className="p-3 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border">
                    {importBatches.length > 0 ? (
                      importBatches.map((b) => (
                        <tr key={b.id} className="hover:bg-muted/30 transition-colors">
                          <td className="p-3 font-mono text-[11px] text-muted-foreground">
                            {b.id.slice(0, 8)}...
                          </td>
                          <td className="p-3 font-medium text-foreground">{b.original_filename}</td>
                          <td className="p-3 text-muted-foreground">
                            {b.worksheet_name} ({b.record_type})
                          </td>
                          <td className="p-3 font-mono">
                            {b.imported_rows} / {b.total_rows_analyzed}
                          </td>
                          <td className="p-3">
                            <Badge
                              variant="outline"
                              className={`text-[10px] ${
                                b.status === "COMPLETED"
                                  ? "text-emerald-700 bg-emerald-50 border-emerald-300"
                                  : b.status === "APPROVED"
                                  ? "text-blue-700 bg-blue-50 border-blue-300"
                                  : b.status === "AWAITING_APPROVAL"
                                  ? "text-amber-700 bg-amber-50 border-amber-300"
                                  : "text-muted-foreground"
                              }`}
                            >
                              {b.status}
                            </Badge>
                          </td>
                          <td className="p-3 text-muted-foreground">
                            {b.approved_by?.email || "—"}
                          </td>
                          <td className="p-3 text-right">
                            {b.status === "AWAITING_APPROVAL" && (
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => handleApproveBatch(b.id)}
                                className="h-6 text-[11px] text-emerald-700 hover:text-emerald-800"
                              >
                                Approve
                              </Button>
                            )}
                            {b.status === "APPROVED" && (
                              <Button
                                size="sm"
                                onClick={() => handleExecuteBatch(b.id)}
                                disabled={executingBatchId === b.id}
                                className="h-6 text-[11px] bg-primary text-primary-foreground"
                              >
                                {executingBatchId === b.id ? "Importing..." : "Execute"}
                              </Button>
                            )}
                          </td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan={7} className="p-6 text-center text-muted-foreground">
                          No previous import batches logged.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ───────────────────────────────────────────────────────────── */}
      {/* 8. ANNUAL SUMMARY & REPORTS TAB */}
      {/* ───────────────────────────────────────────────────────────── */}
      {activeTab === "annual_summary" && (
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-base font-bold">
                    Official Annual Summary Report · Fiscal Year {fiscalYear}
                  </CardTitle>
                  <CardDescription className="text-xs">
                    Synthesizes financial expenditures, participant counts, and service outcomes matching the Annual Summary tracker.
                  </CardDescription>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => window.print()}
                  className="gap-2 text-xs"
                >
                  <Download className="w-3.5 h-3.5" />
                  Print / Export Summary
                </Button>
              </div>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Summary Table */}
              <div className="border border-border rounded-xl overflow-hidden">
                <table className="w-full text-left text-xs">
                  <thead className="bg-muted/70 text-muted-foreground font-semibold border-b border-border">
                    <tr>
                      <th className="p-3">Program Category / Area</th>
                      <th className="p-3 text-center">Total Events</th>
                      <th className="p-3 text-center">Families Served</th>
                      <th className="p-3 text-center">Participants</th>
                      <th className="p-3 text-right">Total Expenditure</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border">
                    <tr className="hover:bg-muted/20">
                      <td className="p-3 font-semibold text-foreground flex items-center gap-2">
                        <Sparkles className="w-4 h-4 text-amber-600" />
                        Enhancement Programs
                      </td>
                      <td className="p-3 text-center font-mono">{summary?.enhancement_programs?.total_records || 0}</td>
                      <td className="p-3 text-center font-mono font-medium">
                        {summary?.enhancement_programs?.total_families || 0}
                      </td>
                      <td className="p-3 text-center font-mono">
                        {summary?.enhancement_programs?.total_participants || 0}
                      </td>
                      <td className="p-3 text-right font-mono font-bold text-foreground">
                        ${Number(summary?.enhancement_programs?.total_cost || 0).toLocaleString("en-CA", {
                          minimumFractionDigits: 2,
                        })}
                      </td>
                    </tr>
                    <tr className="hover:bg-muted/20">
                      <td className="p-3 font-semibold text-foreground flex items-center gap-2">
                        <HeartHandshake className="w-4 h-4 text-emerald-600" />
                        Family Support Services
                      </td>
                      <td className="p-3 text-center font-mono">{summary?.family_support?.total_records || 0}</td>
                      <td className="p-3 text-center font-mono font-medium">—</td>
                      <td className="p-3 text-center font-mono">
                        {summary?.family_support?.total_participants || 0}
                      </td>
                      <td className="p-3 text-right font-mono font-bold text-foreground">
                        ${Number(summary?.family_support?.total_cost || 0).toLocaleString("en-CA", {
                          minimumFractionDigits: 2,
                        })}
                      </td>
                    </tr>
                    <tr className="hover:bg-muted/20">
                      <td className="p-3 font-semibold text-foreground flex items-center gap-2">
                        <Shield className="w-4 h-4 text-blue-600" />
                        Other Nations Support (Eagle Nest)
                      </td>
                      <td className="p-3 text-center font-mono">{summary?.other_nations_support?.total_records || 0}</td>
                      <td className="p-3 text-center font-mono font-medium">—</td>
                      <td className="p-3 text-center font-mono">—</td>
                      <td className="p-3 text-right font-mono font-bold text-foreground">
                        ${Number(summary?.other_nations_support?.total_cost || 0).toLocaleString("en-CA", {
                          minimumFractionDigits: 2,
                        })}
                      </td>
                    </tr>
                    <tr className="bg-muted/40 font-bold border-t-2 border-border">
                      <td className="p-3 text-foreground">Combined Prevention & Healing Total</td>
                      <td className="p-3 text-center font-mono">
                        {(summary?.enhancement_programs?.total_records || 0) +
                          (summary?.family_support?.total_records || 0) +
                          (summary?.other_nations_support?.total_records || 0)}
                      </td>
                      <td className="p-3 text-center font-mono">
                        {summary?.enhancement_programs?.total_families || 0}
                      </td>
                      <td className="p-3 text-center font-mono">
                        {(summary?.enhancement_programs?.total_participants || 0) +
                          (summary?.family_support?.total_participants || 0)}
                      </td>
                      <td className="p-3 text-right font-mono text-primary text-sm">
                        ${Number(summary?.combined_total_cost || 0).toLocaleString("en-CA", {
                          minimumFractionDigits: 2,
                        })}
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>

              {/* Expense by payment instrument */}
              <div className="space-y-2">
                <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                  Financial Code Allocations
                </h4>
                <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2">
                  {summary?.expense_breakdown &&
                    Object.entries(summary.expense_breakdown).map(([k, v]) => (
                      <div key={k} className="p-2.5 rounded-lg border border-border bg-card">
                        <span className="text-[10px] text-muted-foreground uppercase">{k.replace(/_/g, " ")}</span>
                        <p className="text-sm font-mono font-bold text-foreground mt-0.5">
                          ${Number(v).toLocaleString("en-CA", { minimumFractionDigits: 2 })}
                        </p>
                      </div>
                    ))}
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* ───────────────────────────────────────────────────────────── */}
      {/* DIALOG: NEW ENHANCEMENT PROGRAM */}
      {/* ───────────────────────────────────────────────────────────── */}
      <Dialog open={epModalOpen} onOpenChange={setEpModalOpen}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Record Enhancement Program</DialogTitle>
            <DialogDescription className="text-xs">
              Log program activities, participant attendance counts, and financial expense coding.
            </DialogDescription>
          </DialogHeader>

          <form onSubmit={handleSaveEP} className="space-y-4 text-xs">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <Label>Program Name *</Label>
                <Input
                  required
                  placeholder="e.g. Youth Cultural Healing Circle"
                  value={epForm.program}
                  onChange={(e) => setEpForm({ ...epForm, program: e.target.value })}
                  className="mt-1 h-8 text-xs"
                />
              </div>
              <div>
                <Label>Activity Specifics</Label>
                <Input
                  placeholder="e.g. Land-based storytelling"
                  value={epForm.program_activity}
                  onChange={(e) => setEpForm({ ...epForm, program_activity: e.target.value })}
                  className="mt-1 h-8 text-xs"
                />
              </div>
            </div>

            <div className="grid grid-cols-3 gap-3">
              <div>
                <Label>Date</Label>
                <Input
                  type="date"
                  value={epForm.record_date}
                  onChange={(e) => setEpForm({ ...epForm, record_date: e.target.value })}
                  className="mt-1 h-8 text-xs"
                />
              </div>
              <div>
                <Label>Facilitator Name</Label>
                <Input
                  placeholder="Worker Name"
                  value={epForm.employee_name_raw}
                  onChange={(e) => setEpForm({ ...epForm, employee_name_raw: e.target.value })}
                  className="mt-1 h-8 text-xs"
                />
              </div>
              <div>
                <Label>Position</Label>
                <Input
                  placeholder="e.g. Facilitator"
                  value={epForm.position_raw}
                  onChange={(e) => setEpForm({ ...epForm, position_raw: e.target.value })}
                  className="mt-1 h-8 text-xs"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <Label>City</Label>
                <Input
                  value={epForm.city}
                  onChange={(e) => setEpForm({ ...epForm, city: e.target.value })}
                  className="mt-1 h-8 text-xs"
                />
              </div>
              <div>
                <Label>Province</Label>
                <Input
                  value={epForm.province}
                  onChange={(e) => setEpForm({ ...epForm, province: e.target.value })}
                  className="mt-1 h-8 text-xs"
                />
              </div>
            </div>

            {/* Families & Demographics */}
            <div className="border-t border-border pt-3 space-y-2">
              <span className="font-semibold text-muted-foreground uppercase text-[10px] tracking-wider">
                Family & Participant Counts
              </span>
              <div className="grid grid-cols-4 gap-2">
                <div>
                  <Label className="text-[11px]">Families In-Prov</Label>
                  <Input
                    type="number"
                    min="0"
                    value={epForm.families_in_province}
                    onChange={(e) => setEpForm({ ...epForm, families_in_province: parseInt(e.target.value) || 0 })}
                    className="mt-1 h-8 text-xs"
                  />
                </div>
                <div>
                  <Label className="text-[11px]">Families Out-Prov</Label>
                  <Input
                    type="number"
                    min="0"
                    value={epForm.families_out_of_province}
                    onChange={(e) => setEpForm({ ...epForm, families_out_of_province: parseInt(e.target.value) || 0 })}
                    className="mt-1 h-8 text-xs"
                  />
                </div>
                <div>
                  <Label className="text-[11px]">Children (0-12)</Label>
                  <Input
                    type="number"
                    min="0"
                    value={epForm.participants_children_0_12}
                    onChange={(e) => setEpForm({ ...epForm, participants_children_0_12: parseInt(e.target.value) || 0 })}
                    className="mt-1 h-8 text-xs"
                  />
                </div>
                <div>
                  <Label className="text-[11px]">Youth (13-17)</Label>
                  <Input
                    type="number"
                    min="0"
                    value={epForm.participants_youth_13_17}
                    onChange={(e) => setEpForm({ ...epForm, participants_youth_13_17: parseInt(e.target.value) || 0 })}
                    className="mt-1 h-8 text-xs"
                  />
                </div>
              </div>
            </div>

            {/* Financial Coding & Costs */}
            <div className="border-t border-border pt-3 space-y-2">
              <span className="font-semibold text-muted-foreground uppercase text-[10px] tracking-wider">
                Financial Expense Coding
              </span>
              <div className="grid grid-cols-3 gap-2">
                <div>
                  <Label className="text-[11px]">Account Code</Label>
                  <Input
                    value={epForm.account_code}
                    onChange={(e) => setEpForm({ ...epForm, account_code: e.target.value })}
                    className="mt-1 h-8 text-xs font-mono"
                  />
                </div>
                <div>
                  <Label className="text-[11px]">Subcode</Label>
                  <Input
                    value={epForm.subcode}
                    onChange={(e) => setEpForm({ ...epForm, subcode: e.target.value })}
                    className="mt-1 h-8 text-xs font-mono"
                  />
                </div>
                <div>
                  <Label className="text-[11px]">Gift Card ($)</Label>
                  <Input
                    type="number"
                    step="0.01"
                    min="0"
                    value={epForm.expense_gift_card}
                    onChange={(e) => setEpForm({ ...epForm, expense_gift_card: parseFloat(e.target.value) || 0 })}
                    className="mt-1 h-8 text-xs font-mono"
                  />
                </div>
              </div>

              <div className="grid grid-cols-3 gap-2">
                <div>
                  <Label className="text-[11px]">Purchase Order ($)</Label>
                  <Input
                    type="number"
                    step="0.01"
                    min="0"
                    value={epForm.expense_purchase_order}
                    onChange={(e) => setEpForm({ ...epForm, expense_purchase_order: parseFloat(e.target.value) || 0 })}
                    className="mt-1 h-8 text-xs font-mono"
                  />
                </div>
                <div>
                  <Label className="text-[11px]">EFT ($)</Label>
                  <Input
                    type="number"
                    step="0.01"
                    min="0"
                    value={epForm.expense_eft}
                    onChange={(e) => setEpForm({ ...epForm, expense_eft: parseFloat(e.target.value) || 0 })}
                    className="mt-1 h-8 text-xs font-mono"
                  />
                </div>
                <div>
                  <Label className="text-[11px]">Cheque ($)</Label>
                  <Input
                    type="number"
                    step="0.01"
                    min="0"
                    value={epForm.expense_cheque}
                    onChange={(e) => setEpForm({ ...epForm, expense_cheque: parseFloat(e.target.value) || 0 })}
                    className="mt-1 h-8 text-xs font-mono"
                  />
                </div>
              </div>
            </div>

            <DialogFooter>
              <Button type="button" variant="outline" size="sm" onClick={() => setEpModalOpen(false)}>
                Cancel
              </Button>
              <Button type="submit" size="sm" className="bg-primary text-primary-foreground">
                Save Enhancement Program
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* ───────────────────────────────────────────────────────────── */}
      {/* DIALOG: NEW FAMILY SUPPORT RECORD */}
      {/* ───────────────────────────────────────────────────────────── */}
      <Dialog open={fsrModalOpen} onOpenChange={setFsrModalOpen}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Record Family Support Service</DialogTitle>
            <DialogDescription className="text-xs">
              Direct emergency relief, utility support, or wellness service provided to a client/family.
            </DialogDescription>
          </DialogHeader>

          <form onSubmit={handleSaveFSR} className="space-y-4 text-xs">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <Label>Support Type *</Label>
                <Input
                  required
                  placeholder="e.g. Utility Arrears / Grocery Relief"
                  value={fsrForm.support_type}
                  onChange={(e) => setFsrForm({ ...fsrForm, support_type: e.target.value })}
                  className="mt-1 h-8 text-xs"
                />
              </div>
              <div>
                <Label>Program Area</Label>
                <Input
                  placeholder="e.g. Family Support Services"
                  value={fsrForm.program}
                  onChange={(e) => setFsrForm({ ...fsrForm, program: e.target.value })}
                  className="mt-1 h-8 text-xs"
                />
              </div>
            </div>

            <div className="grid grid-cols-3 gap-3">
              <div>
                <Label>Date</Label>
                <Input
                  type="date"
                  value={fsrForm.record_date}
                  onChange={(e) => setFsrForm({ ...fsrForm, record_date: e.target.value })}
                  className="mt-1 h-8 text-xs"
                />
              </div>
              <div>
                <Label>Worker Name</Label>
                <Input
                  placeholder="Staff Worker"
                  value={fsrForm.employee_name_raw}
                  onChange={(e) => setFsrForm({ ...fsrForm, employee_name_raw: e.target.value })}
                  className="mt-1 h-8 text-xs"
                />
              </div>
              <div>
                <Label>Client RedMane ID (Optional)</Label>
                <Input
                  placeholder="e.g. RM-2024-042"
                  value={fsrForm.client_ref_legacy_id}
                  onChange={(e) => setFsrForm({ ...fsrForm, client_ref_legacy_id: e.target.value })}
                  className="mt-1 h-8 text-xs font-mono"
                />
              </div>
            </div>

            <div className="grid grid-cols-3 gap-2 border-t border-border pt-3">
              <div>
                <Label className="text-[11px]">Gift Card ($)</Label>
                <Input
                  type="number"
                  step="0.01"
                  min="0"
                  value={fsrForm.expense_gift_card}
                  onChange={(e) => setFsrForm({ ...fsrForm, expense_gift_card: parseFloat(e.target.value) || 0 })}
                  className="mt-1 h-8 text-xs font-mono"
                />
              </div>
              <div>
                <Label className="text-[11px]">EFT ($)</Label>
                <Input
                  type="number"
                  step="0.01"
                  min="0"
                  value={fsrForm.expense_eft}
                  onChange={(e) => setFsrForm({ ...fsrForm, expense_eft: parseFloat(e.target.value) || 0 })}
                  className="mt-1 h-8 text-xs font-mono"
                />
              </div>
              <div>
                <Label className="text-[11px]">Cheque ($)</Label>
                <Input
                  type="number"
                  step="0.01"
                  min="0"
                  value={fsrForm.expense_cheque}
                  onChange={(e) => setFsrForm({ ...fsrForm, expense_cheque: parseFloat(e.target.value) || 0 })}
                  className="mt-1 h-8 text-xs font-mono"
                />
              </div>
            </div>

            <div>
              <Label>Comments / Case Context</Label>
              <Input
                placeholder="Details of support rendered..."
                value={fsrForm.comments}
                onChange={(e) => setFsrForm({ ...fsrForm, comments: e.target.value })}
                className="mt-1 h-8 text-xs"
              />
            </div>

            <DialogFooter>
              <Button type="button" variant="outline" size="sm" onClick={() => setFsrModalOpen(false)}>
                Cancel
              </Button>
              <Button type="submit" size="sm" className="bg-primary text-primary-foreground">
                Save Family Support Record
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* ───────────────────────────────────────────────────────────── */}
      {/* DIALOG: NEW OTHER NATIONS SUPPORT */}
      {/* ───────────────────────────────────────────────────────────── */}
      <Dialog open={onsModalOpen} onOpenChange={setOnsModalOpen}>
        <DialogContent className="max-w-xl">
          <DialogHeader>
            <DialogTitle>Record Other Nations Support (Eagle Nest)</DialogTitle>
            <DialogDescription className="text-xs">
              Log off-reserve or partner nation support, lodging, and community connection.
            </DialogDescription>
          </DialogHeader>

          <form onSubmit={handleSaveONS} className="space-y-4 text-xs">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <Label>Family / Client Reference *</Label>
                <Input
                  required
                  placeholder="e.g. Delorme Family"
                  value={onsForm.family_reference_raw}
                  onChange={(e) => setOnsForm({ ...onsForm, family_reference_raw: e.target.value })}
                  className="mt-1 h-8 text-xs"
                />
              </div>
              <div>
                <Label>Service Type *</Label>
                <Input
                  required
                  placeholder="e.g. Emergency Lodging"
                  value={onsForm.service_type}
                  onChange={(e) => setOnsForm({ ...onsForm, service_type: e.target.value })}
                  className="mt-1 h-8 text-xs"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <Label>Worker Name</Label>
                <Input
                  placeholder="Staff Worker"
                  value={onsForm.worker_name_raw}
                  onChange={(e) => setOnsForm({ ...onsForm, worker_name_raw: e.target.value })}
                  className="mt-1 h-8 text-xs"
                />
              </div>
              <div>
                <Label>Cost ($) *</Label>
                <Input
                  type="number"
                  step="0.01"
                  min="0"
                  required
                  value={onsForm.cost}
                  onChange={(e) => setOnsForm({ ...onsForm, cost: parseFloat(e.target.value) || 0 })}
                  className="mt-1 h-8 text-xs font-mono"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <Label>Cowessess Connection</Label>
                <Input
                  placeholder="e.g. Married to band member"
                  value={onsForm.cowessess_connection}
                  onChange={(e) => setOnsForm({ ...onsForm, cowessess_connection: e.target.value })}
                  className="mt-1 h-8 text-xs"
                />
              </div>
              <div>
                <Label>Other Community / Nation</Label>
                <Input
                  placeholder="e.g. Zagimay / Kahkewistahaw"
                  value={onsForm.other_community}
                  onChange={(e) => setOnsForm({ ...onsForm, other_community: e.target.value })}
                  className="mt-1 h-8 text-xs"
                />
              </div>
            </div>

            <div className="flex items-center gap-2 pt-1">
              <input
                type="checkbox"
                id="on_reserve_check"
                checked={onsForm.on_reserve}
                onChange={(e) => setOnsForm({ ...onsForm, on_reserve: e.target.checked })}
                className="rounded border-border"
              />
              <Label htmlFor="on_reserve_check" className="text-xs cursor-pointer">
                Provided On Reserve
              </Label>
            </div>

            <DialogFooter>
              <Button type="button" variant="outline" size="sm" onClick={() => setOnsModalOpen(false)}>
                Cancel
              </Button>
              <Button type="submit" size="sm" className="bg-primary text-primary-foreground">
                Save Other Nations Record
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* ───────────────────────────────────────────────────────────── */}
      {/* DIALOG: VERIFY & LINK INACTIVE STAFF */}
      {/* ───────────────────────────────────────────────────────────── */}
      <Dialog open={activateStaffModalOpen} onOpenChange={setActivateStaffModalOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <UserPlus className="w-5 h-5 text-amber-600" />
              Verify & Link Staff Member
            </DialogTitle>
            <DialogDescription className="text-xs">
              Verifies the employee's work email and position, creating or linking their canonical Employee record and associating historical records.
              <span className="block mt-1 text-amber-800 font-medium">
                Note: This verifies the employment profile and DOES NOT activate a login account. Login credentials remain inactive until separately provisioned.
              </span>
            </DialogDescription>
          </DialogHeader>

          {selectedStaff && (
            <div className="space-y-4 text-xs py-2">
              <div className="p-3 bg-muted/40 rounded-lg space-y-1">
                <div className="font-semibold text-foreground text-sm">
                  {selectedStaff.display_name_from_excel}
                </div>
                <div className="text-muted-foreground">
                  Detected Position: {selectedStaff.position || "Staff"} · Department: {selectedStaff.department || "Prevention & Healing"}
                </div>
              </div>

              <div>
                <Label>Verified CRBCL Work Email *</Label>
                <Input
                  required
                  type="email"
                  placeholder="e.g. first.last@crbcl.ca"
                  value={staffEmail}
                  onChange={(e) => setStaffEmail(e.target.value)}
                  className="mt-1 h-9 text-xs"
                />
                <p className="text-[11px] text-muted-foreground mt-1">
                  A real, verified individual address is required. No generic or shared emails.
                </p>
              </div>

              <div>
                <Label>Confirmed Title / Position</Label>
                <Input
                  value={staffPosition}
                  onChange={(e) => setStaffPosition(e.target.value)}
                  placeholder="Position"
                  className="mt-1 h-9 text-xs"
                />
              </div>

              <DialogFooter className="pt-2">
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => setActivateStaffModalOpen(false)}
                >
                  Cancel
                </Button>
                <Button
                  onClick={handleActivateStaff}
                  disabled={activatingStaff}
                  className="bg-amber-600 hover:bg-amber-700 text-white gap-1.5"
                >
                  <CheckCircle2 className="w-4 h-4" />
                  {activatingStaff ? "Verifying..." : "Confirm & Link Profile"}
                </Button>
              </DialogFooter>
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* ───────────────────────────────────────────────────────────── */}
      {/* DIALOG: RECONCILE CLIENT IDENTIFIER */}
      {/* ───────────────────────────────────────────────────────────── */}
      <Dialog open={reconcileClientModalOpen} onOpenChange={setReconcileClientModalOpen}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <ShieldCheck className="w-5 h-5 text-blue-600" />
              Reconcile Legacy RedMane Client ID
            </DialogTitle>
            <DialogDescription className="text-xs">
              Search the canonical Person registry to match this legacy identifier.
            </DialogDescription>
          </DialogHeader>

          {selectedClientRef && (
            <div className="space-y-4 text-xs py-2">
              <div className="p-3 bg-muted/40 rounded-lg space-y-1">
                <div className="flex items-center justify-between">
                  <span className="font-mono font-bold text-sm text-foreground">
                    {selectedClientRef.legacy_id}
                  </span>
                  <Badge variant="outline" className="text-[10px]">
                    {selectedClientRef.legacy_id_type}
                  </Badge>
                </div>
                <p className="text-muted-foreground text-[11px]">
                  Current Status: {selectedClientRef.status}
                </p>
              </div>

              <div>
                <Label>Search Canonical Persons (10-digit ID, First Name, Last Name)</Label>
                <div className="relative mt-1">
                  <Search className="w-4 h-4 absolute left-3 top-2.5 text-muted-foreground" />
                  <Input
                    placeholder="Type name or 10-digit ID to search..."
                    value={personQuery}
                    onChange={(e) => handleSearchPerson(e.target.value)}
                    className="pl-9 h-9 text-xs"
                  />
                </div>
              </div>

              {/* Search Candidate Results */}
              <div className="space-y-2 max-h-48 overflow-y-auto border border-border rounded-lg p-2 bg-card">
                {searchingPersons ? (
                  <p className="text-center text-muted-foreground py-4 text-xs">Searching registry...</p>
                ) : personResults.length > 0 ? (
                  personResults.map((p) => (
                    <div
                      key={p.id}
                      onClick={() => setSelectedPersonId(p.id)}
                      className={`p-2.5 rounded-lg border cursor-pointer transition-colors ${
                        selectedPersonId === p.id
                          ? "border-primary bg-primary/10 text-primary"
                          : "border-border hover:bg-muted/40"
                      }`}
                    >
                      <div className="flex items-center justify-between font-semibold">
                        <span>{p.first_name} {p.last_name}</span>
                        <span className="font-mono text-[11px]">ID #{p.person_id_number}</span>
                      </div>
                      <div className="text-[11px] text-muted-foreground mt-0.5">
                        DOB: {p.date_of_birth || "—"} · Band: {p.band_affiliation || "Cowessess First Nation"}
                      </div>
                    </div>
                  ))
                ) : (
                  <p className="text-center text-muted-foreground py-4 text-xs">
                    {personQuery.length >= 2
                      ? "No matching person records found. Do not create fake records."
                      : "Type at least 2 characters to search existing client profiles."}
                  </p>
                )}
              </div>

              <DialogFooter className="pt-2 flex items-center justify-between">
                <Button
                  type="button"
                  variant="destructive"
                  size="sm"
                  onClick={handleRejectClientMatch}
                  disabled={reconcilingClient}
                >
                  Mark Ineligible / Reject
                </Button>

                <div className="flex gap-2">
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={() => setReconcileClientModalOpen(false)}
                  >
                    Cancel
                  </Button>
                  <Button
                    onClick={handleConfirmClientMatch}
                    disabled={!selectedPersonId || reconcilingClient}
                    className="bg-primary text-primary-foreground"
                  >
                    Confirm Canonical Link
                  </Button>
                </div>
              </DialogFooter>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
