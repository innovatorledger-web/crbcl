"""CRBCL Platform — SQLAlchemy Models Package.

All models are imported here so Alembic can discover them.
"""

from app.models.assessment import (  # noqa: F401
    Assessment,
    AssessmentAnswer,
    AssessmentAnswerOption,
    AssessmentQuestion,
    AssessmentQuestionOption,
    AssessmentSection,
    AssessmentSequence,
    AssessmentStatusHistory,
    AssessmentTemplate,
    AssessmentTemplateVersion,
    AssessmentUnlockEvent,
)
from app.models.audit import AccessEvent, AuditEvent  # noqa: F401
from app.models.board_action import BoardAction, BoardActionHistory  # noqa: F401
from app.models.calendar import (  # noqa: F401
    CalendarEvent,
    CalendarRecurrenceRule,
)
from app.models.caregiver_support import CaregiverSupport  # noqa: F401
from app.models.caregiver_training import CaregiverTraining  # noqa: F401
from app.models.case import Case  # noqa: F401
from app.models.case_management import (  # noqa: F401
    CaseAssignment,
    CaseExternalWorker,
    CaseLink,
    CasePerson,
    CaseRestriction,
    CaseSequence,
    CaseSource,
    CaseStatusHistory,
    CaseTransfer,
)
from app.models.case_note import (  # noqa: F401
    CaseNote,
    CaseNoteAddendum,
    CaseNoteAttachment,
    CaseNotePerson,
)
from app.models.client import Client, ClientApprovalHistory  # noqa: F401
from app.models.config import LookupList, LookupValue, SystemConfig  # noqa: F401
from app.models.department_update import DepartmentExecutiveUpdate, DepartmentExecutiveUpdateHistory  # noqa: F401
from app.models.device import MobileDevice  # noqa: F401
from app.models.document import Document, DocumentAccessEvent, DocumentLink, DocumentVersion  # noqa: F401
from app.models.executive_initiative import (  # noqa: F401
    ExecutiveInitiative,
    ExecutiveInitiativeHistory,
)
from app.models.family import Family  # noqa: F401
from app.models.finance import (  # noqa: F401
    BillingRate,
    BudgetLine,
    FundingSource,
    Invoice,
    InvoiceItem,
    ServiceRequest,
    ServiceRequestApproval,
    ServiceRequestItem,
)
from app.models.fleet import (  # noqa: F401
    FleetGeofence,
    FleetGeofenceEvent,
    Vehicle,
    VehicleAssignment,
    VehicleInsurancePolicy,
    VehicleLocation,
    VehicleMaintenance,
    VehicleTelematicsLink,
    VehicleTrip,
)
from app.models.front_desk import (  # noqa: F401
    FrontDeskRoutingHistory,
    FrontDeskSequence,
    FrontDeskSubmission,
    PublicIntakeConversionLink,
)
from app.models.idempotency import IdempotencyKey  # noqa: F401
from app.models.integrations import (  # noqa: F401
    AiRequestAudit,
    CommunicationsPost,
    IntegrationExternalLink,
    IntegrationRegistry,
    OcrJob,
)
from app.models.medical import (  # noqa: F401
    ClientAllergy,
    ClientMedicalCondition,
    ClientMedicalProfile,
    ClientMedication,
)
from app.models.migration import MigrationLedger  # noqa: F401
from app.models.notification import (  # noqa: F401
    Notification,
    NotificationDelivery,
    NotificationPreference,
    NotificationTemplate,
)
from app.models.operations import (  # noqa: F401
    OperationsRequest,
    RoomBooking,
    SupplyItem,
    VehicleKeyLog,
    VehicleReservation,
)
from app.models.org_ops import (  # noqa: F401
    AssetAssignment,
    Donation,
    Donor,
    Employee,
    EmployeeCertification,
    Facility,
    FacilityInspection,
    FacilityWorkOrder,
    FundraisingCampaign,
    HousingOccupancy,
    HousingUnit,
    ITAsset,
    Volunteer,
    VolunteerApplication,
    VolunteerAssignment,
    VolunteerHour,
)
from app.models.outbox import OutboxEvent  # noqa: F401
from app.models.person import (  # noqa: F401
    Person,
    PersonAddress,
    PersonChallenge,
    PersonContact,
    PersonCulturalProfile,
    PersonMerge,
    PersonPhysicalDescription,
    PersonSequence,
    PersonStrength,
)
from app.models.placement import (  # noqa: F401
    ActiveEffort,
    BackgroundCheck,
    CourtEvent,
    DischargeEpisode,
    InHomePlacement,
    PermanencyPlan,
    PlacementEpisode,
    RemovalEpisode,
    RespiteEpisode,
    VisitationPlan,
)
from app.models.placement_home import (  # noqa: F401
    PlacementHome,
    PlacementHomeContactLog,
    PlacementHomeLicense,
    PlacementHomeMember,
    PlacementHomeVisit,
)
from app.models.plan import (  # noqa: F401
    GoalProgressUpdate,
    Plan,
    PlanActivity,
    PlanAssessment,
    PlanConcern,
    PlanGoal,
    PlanParticipant,
    PlanSequence,
    PlanSignature,
    PlanStrength,
    PlanVersion,
)
from app.models.provider import (  # noqa: F401
    ClientProvider,
    Provider,
    ProviderLocation,
    ProviderSpecialty,
)
from app.models.referral import (  # noqa: F401
    ChildDisposition,
    IntakeDecision,
    Referral,
    ReferralConcern,
    ReferralIncident,
    ReferralLink,
    ReferralPerson,
    ReferralReporter,
    ReferralSequence,
)
from app.models.relationship import (  # noqa: F401
    FamilyMember,
    FamilyRelationship,
    Household,
    HouseholdMembership,
)
from app.models.reporting_qa import (  # noqa: F401
    DashboardWidget,
    QAAudit,
    QAAuditResult,
    QAAuditTemplate,
    QAAuditTemplateItem,
    QAAuditTemplateVersion,
    ReportRun,
    SavedReport,
    UserDashboardWidget,
)
from app.models.resource_complaint import ResourceComplaint  # noqa: F401
from app.models.resource_monitoring import ResourceHomeMonitoring  # noqa: F401
from app.models.resource_recruitment import (  # noqa: F401
    ApplicantRole,
    RecruitmentState,
    ResourceRecruitment,
    ResourceRecruitmentApplicant,
    ResourceRecruitmentHistory,
)
from app.models.role import Permission, Role, RolePermission, UserRole  # noqa: F401
from app.models.school import (  # noqa: F401
    ClientSchoolEnrolment,
    School,
)
from app.models.sprint_b_models import (  # noqa: F401
    Appointment,
    ClinicalNote,
    ClinicalNoteAddendum,
    FundingGrant,
    Incident,
    Program,
)
from app.models.staffing import (  # noqa: F401
    StaffingAttendee,
    StaffingCase,
    StaffingSession,
)
from app.models.team import Team, TeamMembership, UserTeamAccess  # noqa: F401
from app.models.terminology import TerminologyKey, TerminologyTranslation  # noqa: F401
from app.models.timeline import TimelineEvent  # noqa: F401
from app.models.user import EmailVerificationCode, Session, User, UserPreference  # noqa: F401
from app.models.prevention_healing import (  # noqa: F401
    EnhancementProgram,
    FamilySupportRecord,
    OtherNationsSupport,
    PHClientRef,
    PHImportBatch,
    PHImportRow,
    PendingStaffProfile,
)
