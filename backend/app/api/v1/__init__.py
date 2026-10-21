"""API v1 router bundle."""

from fastapi import APIRouter

from app.api.v1.active_efforts import router as active_efforts_router
from app.api.v1.ask_red_bear import router as ask_red_bear_router
from app.api.v1.assessment_templates import router as assessment_templates_router
from app.api.v1.assessments import router as assessments_router
from app.api.v1.background_checks import router as background_checks_router
from app.api.v1.board_dashboard import router as board_dashboard_router
from app.api.v1.calendar import router as calendar_router
from app.api.v1.caregiver_supports import router as caregiver_supports_router
from app.api.v1.caregiver_training import router as caregiver_training_router
from app.api.v1.case_notes import router as case_notes_router
from app.api.v1.cases import router as cases_router
from app.api.v1.ceo_dashboard import router as ceo_dashboard_router
from app.api.v1.clients import router as clients_router
from app.api.v1.clinical_notes import router as clinical_notes_router
from app.api.v1.communications import router as communications_router
from app.api.v1.court_events import router as court_events_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.dashboard_control import router as dashboard_control_router
from app.api.v1.documents import router as documents_router
from app.api.v1.families import router as families_router
from app.api.v1.finance import router as finance_router
from app.api.v1.fleet import router as fleet_router
from app.api.v1.front_desk import router as front_desk_router
from app.api.v1.health import router as health_router
from app.api.v1.households import router as households_router
from app.api.v1.integrations import router as integrations_router
from app.api.v1.lookups import router as lookups_router
from app.api.v1.notification_preferences import router as notification_preferences_router
from app.api.v1.notification_templates import router as notification_templates_router
from app.api.v1.notifications import router as notifications_router
from app.api.v1.ocr import router as ocr_router
from app.api.v1.operations import router as operations_router
from app.api.v1.org_ops import router as org_ops_router
from app.api.v1.passports import router as passports_router
from app.api.v1.permanency_plans import router as permanency_plans_router
from app.api.v1.persons import router as persons_router
from app.api.v1.placement_homes import router as placement_homes_router
from app.api.v1.placement_matching import router as placement_matching_router
from app.api.v1.placements import router as placements_router
from app.api.v1.plans import router as plans_router
from app.api.v1.prevention_healing import router as prevention_healing_router
from app.api.v1.providers import router as providers_router
from app.api.v1.qa import router as qa_router
from app.api.v1.referrals import router as referrals_router
from app.api.v1.removals import router as removals_router
from app.api.v1.reporting import router as reporting_router
from app.api.v1.resource_complaints import router as resource_complaints_router
from app.api.v1.resource_finance import router as resource_finance_router
from app.api.v1.resource_monitoring import router as resource_monitoring_router
from app.api.v1.resource_outcomes import router as resource_outcomes_router
from app.api.v1.resource_recruitments import router as resource_recruitments_router
from app.api.v1.schools import router as schools_router
from app.api.v1.sprint_b_legacy import router as sprint_b_legacy_router
from app.api.v1.staffing import router as staffing_router
from app.api.v1.sync import router as sync_router
from app.api.v1.teams import router as teams_router
from app.api.v1.users import router as users_router
from app.auth.router import router as auth_router

api_v1_router = APIRouter(prefix="/api/v1")

# Mount sub-routers
api_v1_router.include_router(health_router)
api_v1_router.include_router(clinical_notes_router)
api_v1_router.include_router(sprint_b_legacy_router)
api_v1_router.include_router(sync_router, prefix="/sync", tags=["Sync"])
api_v1_router.include_router(auth_router)
api_v1_router.include_router(referrals_router)
api_v1_router.include_router(persons_router)
api_v1_router.include_router(documents_router)
api_v1_router.include_router(clients_router)
api_v1_router.include_router(families_router)
api_v1_router.include_router(households_router)
api_v1_router.include_router(providers_router)
api_v1_router.include_router(schools_router)
api_v1_router.include_router(cases_router)
api_v1_router.include_router(case_notes_router)
api_v1_router.include_router(assessment_templates_router)
api_v1_router.include_router(assessments_router)
api_v1_router.include_router(plans_router)
api_v1_router.include_router(prevention_healing_router)
api_v1_router.include_router(active_efforts_router)
api_v1_router.include_router(background_checks_router)
api_v1_router.include_router(court_events_router)
api_v1_router.include_router(permanency_plans_router)
api_v1_router.include_router(placement_homes_router)
api_v1_router.include_router(placements_router)
api_v1_router.include_router(removals_router)
api_v1_router.include_router(users_router)
api_v1_router.include_router(teams_router)
api_v1_router.include_router(lookups_router)
api_v1_router.include_router(calendar_router)
api_v1_router.include_router(staffing_router)
api_v1_router.include_router(notifications_router)
api_v1_router.include_router(notification_preferences_router)
api_v1_router.include_router(notification_templates_router)
api_v1_router.include_router(finance_router)
api_v1_router.include_router(reporting_router)
api_v1_router.include_router(qa_router)
api_v1_router.include_router(passports_router)
api_v1_router.include_router(dashboard_router)
api_v1_router.include_router(fleet_router)
api_v1_router.include_router(integrations_router)
api_v1_router.include_router(ocr_router)
api_v1_router.include_router(ask_red_bear_router)
api_v1_router.include_router(communications_router)
api_v1_router.include_router(resource_recruitments_router)
api_v1_router.include_router(caregiver_training_router)
api_v1_router.include_router(placement_matching_router)
api_v1_router.include_router(resource_monitoring_router)
api_v1_router.include_router(resource_complaints_router)
api_v1_router.include_router(caregiver_supports_router)
api_v1_router.include_router(resource_finance_router)
api_v1_router.include_router(resource_outcomes_router)
api_v1_router.include_router(front_desk_router)
api_v1_router.include_router(ceo_dashboard_router)
api_v1_router.include_router(board_dashboard_router)
api_v1_router.include_router(dashboard_control_router)
api_v1_router.include_router(operations_router)
api_v1_router.include_router(org_ops_router, prefix="/org-ops", tags=["Organizational Operations"])
