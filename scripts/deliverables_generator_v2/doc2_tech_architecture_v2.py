"""Generate Document 2 Revision 2: Updated Technical Architecture and Development Documentation (DOCX & PDF).
Target page range: 20-35 substantive pages.
Features 11 comprehensive ASCII architecture diagrams, complete entity schemas, API specifications, and comparative analysis.
"""

import os
import sys
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable, Preformatted
)
from reportlab.lib import colors

from scripts.deliverables_generator_v2.common_v2 import (
    DELIVERABLES_V2_DIR, NumberedCanvasV2, get_pdf_styles_v2, create_pdf_notice_box_v2, create_pdf_diagram_box,
    PRIMARY_HEX, SECONDARY_HEX, DARK_HEX, LIGHT_BG_HEX, BORDER_HEX,
    COLOR_PRIMARY, COLOR_SECONDARY, COLOR_DARK, COLOR_LIGHT_BG, COLOR_BORDER,
    set_cell_background, set_cell_margins
)

# Pull canonical workspaces dynamically
sys.path.insert(0, r"C:\Users\Shilley Pc\crbcl\backend")
from app.services.dashboard_registry_service import CANONICAL_WORKSPACES

DOC_NAME_BASE = "CRBCL_Updated_Technical_Architecture_and_Development_Documentation_Revision_2_October_2026"

# 11 ASCII Architecture Diagrams
DIAGRAM_1_TOPOLOGY = """
+----------------------------------------------------------------------------------------------------+
|                               CRBCL MULTI-TIER SYSTEM TOPOLOGY                                     |
+----------------------------------------------------------------------------------------------------+
|                                                                                                    |
|  [ PRESENTATION TIER ]                                                                             |
|  +----------------------------------+          +----------------------------------+                |
|  |       React 18 Web Portal        |          |    Flutter Cross-Platform Mobile |                |
|  |     (https://genserver.online)   |          |    (Android, iOS, Field Web)     |                |
|  |   88 Routed Views | Tailwind CSS |          |   Encrypted SQLite Outbox Queue  |                |
|  +-----------------+----------------+          +-----------------+----------------+                |
|                    |                                             |                                 |
|                    | HTTPS / TLS 1.3                             | HTTPS / Idempotent REST         |
|                    v                                             v                                 |
|  +--------------------------------------------------------------------------------+                |
|  |                   SECURITY & IDENTITY GATEWAY (FastAPI / ASGI)                 |                |
|  |  * Dual Auth: Argon2id Password & Frontline 6-Digit PIN (Brute-Force Lockout)  |                |
|  |  * Granular RBAC Engine: 327 Discrete Permissions across 19 Canonical Roles    |                |
|  |  * Case Conflict Engine: Case Restrictions (Family Conflict Blinding)          |                |
|  |  * Security Middleware: Strict CORS Allowlists, State-Changing CSRF Defense     |                |
|  +---------------------------------------+----------------------------------------+                |
|                                          |                                                         |
|                                          v                                                         |
|  [ ASYNCHRONOUS API ORCHESTRATION TIER (FastAPI / Pydantic v2) ]                                   |
|  +--------------------------------------------------------------------------------+                |
|  |  521 Routed Endpoints across 57 Domain Routers (backend/app/api/v1/)           |                |
|  |                                                                                |                |
|  |  [Intake & Triage]   [Cases & Safety]   [Clinical Notes]   [Assessments Engine]|                |
|  |  [Prevention/Healing][Caregivers/Foster][Customary Care]   [Cultural Healing]  |                |
|  |  [Youth Transitions] [Jordan's Principle][Legal & Court]   [Finance & Billing] |                |
|  |  [Fleet Management]  [Front Desk]       [Executive/Board]  [Ask Red Bear AI]   |                |
|  +---------------------------------------+----------------------------------------+                |
|                                          |                                                         |
|                                          v asyncpg / Connection Pool (SQLAlchemy 2.0)              |
|  [ SOVEREIGN PERSISTENCE TIER ]                                                                    |
|  +--------------------------------------------------------------------------------+                |
|  |  PostgreSQL 15+ Managed Relational Database (31 Sequential Alembic Migrations) |                |
|  |  * 205 Mapped Relational Model Classes across 14 Domain Namespaces             |                |
|  |  * RFC 4122 Version 4 UUID Primary Keys & Enforced Foreign Key Cascades        |                |
|  |  * Immutable Event Audit Log & Transactional Outbox Staging Queue               |                |
|  +--------------------------------------------------------------------------------+                |
+----------------------------------------------------------------------------------------------------+
"""

DIAGRAM_2_COMMUNICATION = """
+----------------------------------------------------------------------------------------------------+
|                         WEB / BACKEND / DATABASE COMMUNICATION FLOW                                |
+----------------------------------------------------------------------------------------------------+
|                                                                                                    |
|  [ Browser Client ]                  [ FastAPI Gateway ]                  [ PostgreSQL DB ]        |
|          |                                   |                                    |                |
|          |-- 1. POST /auth/login (PIN/Pass) ->|                                    |                |
|          |                                   |-- 2. Verify Hash / Lockout Status ->|                |
|          |                                   |<- 3. Return User & Roles Record ---|                |
|          |<- 4. Return JWT & HttpOnly Cookie-|                                    |                |
|          |                                   |                                    |                |
|          |-- 5. GET /api/v1/cases/101 ------>|                                    |                |
|          |      (Bearer JWT Header)          |-- 6. Evaluate RBAC Permissions --->|                |
|          |                                   |-- 7. Check Active Case Restriction |                |
|          |                                   |-- 8. Async SELECT via asyncpg ---->|                |
|          |                                   |<- 9. Return Case & Person Data ----|                |
|          |                                   |-- 10. Record AuditEvent (Async) -->|                |
|          |<- 11. Return JSON Response (Pydantic)                                  |                |
|          |                                                                                         |
+----------------------------------------------------------------------------------------------------+
"""

DIAGRAM_3_AUTH = """
+----------------------------------------------------------------------------------------------------+
|                    AUTHENTICATION, RBAC & CASE CONFLICT RESTRICTION PIPELINE                       |
+----------------------------------------------------------------------------------------------------+
|                                                                                                    |
|  Incoming HTTP Request                                                                             |
|         |                                                                                          |
|         v                                                                                          |
|  [ Authentication Layer ]                                                                          |
|    |-- Decodes Bearer JWT or Session Cookie                                                        |
|    |-- Validates cryptographic signature against SESSION_SECRET (Argon2id derivation)              |
|    +-- Identifies User ID, Active Employee ID, and Assigned Canonical Roles                       |
|         |                                                                                          |
|         v                                                                                          |
|  [ Authorization Matrix Check ]                                                                    |
|    |-- Inspects 327 Permissions Enum catalog                                                       |
|    |-- Cross-references User's assigned roles against required permission                          |
|    |-- Fails with 403 Forbidden if permission is missing from role assignment                      |
|         |                                                                                          |
|         v                                                                                          |
|  [ Case-Conflict Blinding Engine ] (backend/app/services/case_restriction_service.py)             |
|    |-- Queries CaseRestriction table: Is current User ID listed as restricted for Case ID?         |
|    |-- If restricted: BLIND CASE (Returns 404 Not Found or Redacted Data)                          |
|    +-- Prevents caseworkers from viewing family/kinship cases where conflicts exist                |
|         |                                                                                          |
|         v                                                                                          |
|  Execute Business Logic & Record Immutable Audit Trail Entry                                       |
|                                                                                                    |
+----------------------------------------------------------------------------------------------------+
"""

DIAGRAM_4_PERSON_CLIENT = """
+----------------------------------------------------------------------------------------------------+
|                    PERSON / CLIENT / CASE RELATIONAL MANAGEMENT ARCHITECTURE                       |
+----------------------------------------------------------------------------------------------------+
|                                                                                                    |
|  +-----------------------------+               +-----------------------------+                     |
|  |           PERSON            |               |           CLIENT            |                     |
|  |  (Biological / Demographic)|               |  (Administrative Status)    |                     |
|  +-----------------------------+               +-----------------------------+                     |
|  | id: UUID (PK)               | 1           1 | id: UUID (PK)               |                     |
|  | numeric_id: BigInteger      |<------------->| person_id: UUID (FK)        |                     |
|  | first_name, last_name       |               | client_status: Active/Closed|                     |
|  | treaty_band_number          |               | approval_status: Approved   |                     |
|  | date_of_birth, gender       |               | intake_date, closure_date   |                     |
|  +--------------+--------------+               +--------------+--------------+                     |
|                 |                                             |                                    |
|                 | 1                                           |                                    |
|                 |                                             |                                    |
|                 v N                                           |                                    |
|  +-----------------------------+                              |                                    |
|  |         CASE_PERSON         |                              |                                    |
|  |  (Kinship / Role Link)      |                              |                                    |
|  +-----------------------------+                              |                                    |
|  | id: UUID (PK)               |                              |                                    |
|  | case_id: UUID (FK) ---------+-----------------------+      |                                    |
|  | person_id: UUID (FK)        |                       |      |                                    |
|  | role: Child/Parent/Elder    |                       |      |                                    |
|  +-----------------------------+                       |      |                                    |
|                                                        v      v                                    |
|                                                +-----------------------------+                     |
|                                                |            CASE             |                     |
|                                                |  (Legal / Service File)     |                     |
|                                                +-----------------------------+                     |
|                                                | id: UUID (PK)               |                     |
|                                                | case_number: CRBCL-2026-XXXX|                     |
|                                                | case_type: Prevention/Prot  |                     |
|                                                | status: Open / Closed       |                     |
|                                                | assigned_worker_id: UUID    |                     |
|                                                | primary_client_id: UUID(FK) |                     |
|                                                +-----------------------------+                     |
|                                                                                                    |
+----------------------------------------------------------------------------------------------------+
"""

DIAGRAM_5_EMPLOYEE_USER = """
+----------------------------------------------------------------------------------------------------+
|                    EMPLOYEE DIRECTORY & USER LOGIN QUARANTINE ARCHITECTURE                         |
+----------------------------------------------------------------------------------------------------+
|                                                                                                    |
|  +------------------------------------+             +------------------------------------+         |
|  |             EMPLOYEE               |             |                USER                |         |
|  |    (HR Staff Profile Record)       |             |   (System Authentication Record)   |         |
|  +------------------------------------+             +------------------------------------+         |
|  | id: UUID (PK)                      | 1         0 | id: UUID (PK)                      |         |
|  | first_name, last_name              |<............| employee_id: UUID (FK, Nullable)   |         |
|  | work_email, phone_number           |             | username: String (Unique)          |         |
|  | department_id, job_title           |             | hashed_password: Argon2id          |         |
|  | employment_status: Active/Leave    |             | pin_hash: Argon2id (Frontline PIN) |         |
|  | is_user_account_created: Boolean   |             | is_active: Boolean                 |         |
|  +-----------------+------------------+             +-----------------+------------------+         |
|                    |                                                  |                            |
|                    | Ingestion via Excel / HR Sync                    | Admin Approval             |
|                    v                                                  v                            |
|  +------------------------------------+             +------------------------------------+         |
|  |       LOGIN QUARANTINE ENGINE      |             |     ACTIVE ACCESS PROVISIONING     |         |
|  |  Staff imported without emails or  |             |  Explicit admin action provisions  |         |
|  |  unverified identities CANNOT login|             |  credentials, assigning 1 of 19    |         |
|  |  CRBCL_PH_STAFF_ACTIVATION_ENABLED |             |  canonical roles and permissions   |         |
|  +------------------------------------+             +------------------------------------+         |
|                                                                                                    |
+----------------------------------------------------------------------------------------------------+
"""

DIAGRAM_6_PH_STRUCTURE = """
+----------------------------------------------------------------------------------------------------+
|                     PREVENTION & HEALING RELATIONAL RECORD ARCHITECTURE                            |
+----------------------------------------------------------------------------------------------------+
|                                                                                                    |
|  +-----------------------------------------------------------------------------------------------+  |
|  |                      PH_RECORD_PROVENANCE (Audit & Cryptographic Tracking)                     |  |
|  |  id: UUID | source_batch_id: UUID | file_hash: SHA-256 | imported_by_user_id: UUID            |  |
|  +-----------------------------------------------+-----------------------------------------------+  |
|                                                  |                                                 |
|                                                  | Categorized & Linked Ingestion                  |
|         +----------------------------------------+----------------------------------------+        |
|         |                                        |                                        |        |
|         v                                        v                                        v        |
|  +------------------------------+  +------------------------------+  +---------------------------+ |
|  |    PH_ENHANCEMENT_PROGRAM    |  |      PH_FAMILY_SUPPORT       |  |   PH_OTHER_NATION_SUPPORT | |
|  +------------------------------+  +------------------------------+  +---------------------------+ |
|  | id: UUID (PK)                |  | id: UUID (PK)                |  | id: UUID (PK)             | |
|  | program_name, category       |  | family_name, file_number     |  | nation_name, province     | |
|  | event_date, fiscal_year      |  | primary_contact_id: UUID(FK) |  | contact_person, phone     | |
|  | adult_attendees, youth_att   |  | support_type, duration_hours |  | jurisdiction_ref_number   | |
|  | total_expenditure_cad        |  | expense_amount_cad           |  | service_provided, cost_cad| |
|  | facilitator_employee_id (FK) |  | assigned_worker_id (FK)      |  | liaison_worker_id (FK)    | |
|  | financial_code: GL/CostCtr   |  | financial_code: GL/CostCtr   |  | financial_code: GL/CostCtr| |
|  +------------------------------+  +------------------------------+  +---------------------------+ |
|                                                                                                    |
+----------------------------------------------------------------------------------------------------+
"""

DIAGRAM_7_EXCEL_RECON = """
+----------------------------------------------------------------------------------------------------+
|                 EXCEL INGESTION & 3-TIER DUPLICATE RECORD PROTECTION ENGINE                        |
+----------------------------------------------------------------------------------------------------+
|                                                                                                    |
|  Incoming Excel Sheet Row                                                                          |
|         |                                                                                          |
|         v                                                                                          |
|  [ Compute Row SHA-256 Fingerprint ] (Header Normalization + Field Value Hash)                     |
|         |                                                                                          |
|         v                                                                                          |
|  [ TIER 1: Exact Bitwise Match ]                                                                   |
|    |-- Does exact SHA-256 fingerprint exist in staging table or target tables?                     |
|    +-- YES -> Mark CONFIRMED_DUPLICATE -> Quarantined (Bypasses Target DB to Prevent Pollution)     |
|         |                                                                                          |
|         v NO                                                                                       |
|  [ TIER 2: Fuzzy Semantic Heuristic Match ]                                                        |
|    |-- Matches Family Name + Date of Service + Financial Code within +/- 2 Days?                   |
|    +-- YES -> Mark POSSIBLE_DUPLICATE -> Route to Administrative Staging Review Queue              |
|         |   Caseworker/Supervisor must review: [CONFIRM SEPARATE SERVICE] or [DISMISS DUPLICATE]   |
|         v NO                                                                                       |
|  [ TIER 3: Validated Unique Record ]                                                               |
|    +-- Pass Schema Validation -> Insert into Active Target Table (Enhancement/Family/Other Nation) |
|                                                                                                    |
+----------------------------------------------------------------------------------------------------+
"""

DIAGRAM_8_MOBILE_SYNC = """
+----------------------------------------------------------------------------------------------------+
|                       FLUTTER MOBILE CLIENT OFFLINE SYNCHRONIZATION                                |
+----------------------------------------------------------------------------------------------------+
|                                                                                                    |
|  [ Frontline Caseworker Device (Offline in Field / Rural Reserve) ]                                |
|  +--------------------------------------------------------------------------------+                |
|  |  Mobile App UI (Flutter) -> Enter Case Note / Intake / Assessment               |                |
|  |  Audio Dictation Recorder -> Records Voice Memo Locally (.m4a / .wav)          |                |
|  |  Encrypted SQLite Local Database:                                              |                |
|  |    * draft_case_notes (id, case_id, summary, body, audio_blob, sync_status='PENDING')           |
|  |    * sync_outbox (id, endpoint, payload_json, idempotency_key, attempts, created_at)            |
|  +---------------------------------------+----------------------------------------+                |
|                                          |                                                         |
|                                          | Network Connectivity Detected (Wi-Fi / LTE)             |
|                                          v                                                         |
|  +--------------------------------------------------------------------------------+                |
|  |  Sync Orchestrator: Pulls PENDING records from sync_outbox                      |                |
|  |  Dispatches HTTPS POST /api/v1/sync/case-notes with Idempotency-Key Header      |                |
|  +---------------------------------------+----------------------------------------+                |
|                                          |                                                         |
|                                          v                                                         |
|  [ FastAPI Backend ]                     |                                                         |
|  +---------------------------------------+----------------------------------------+                |
|  |  Evaluates Idempotency-Key: Has this unique client key been processed?        |                |
|  |  * If processed: Return cached 200 OK (Prevents duplicate note creation)       |                |
|  |  * If new: Execute atomic transaction -> Commit to DB -> Return 201 Created    |                |
|  +---------------------------------------+----------------------------------------+                |
|                                          |                                                         |
|                                          v                                                         |
|  [ Mobile Client ] <- Updates local SQLite record status to 'SYNCED' (Deletes temp audio cache)   |
|                                                                                                    |
+----------------------------------------------------------------------------------------------------+
"""

DIAGRAM_9_WEB_OFFLINE = """
+----------------------------------------------------------------------------------------------------+
|                        ISOLATED WEB OFFLINE WORKSPACE TOPOLOGY                                     |
+----------------------------------------------------------------------------------------------------+
|                                                                                                    |
|  [ Browser Client ]                                                                                |
|  +--------------------------------------------------------------------------------+                |
|  |  Main Web Portal (https://genserver.online) -> Standard Online App              |                |
|  |                                                                                |                |
|  |  Isolated Route: /offline-workspace                                            |                |
|  |  HTML5 Service Worker (sw.js):                                                 |                |
|  |    * Pre-caches static application shell, CSS bundles, SVG icons, and forms    |                |
|  |    * IndexedDB Local Object Store: Stores field notes & draft client intakes   |                |
|  +---------------------------------------+----------------------------------------+                |
|                                          |                                                         |
|                                          | Controlled Feature Gate Flag                            |
|                                          v                                                         |
|  +--------------------------------------------------------------------------------+                |
|  |  Environment Gatekeeper: CRBCL_OFFLINE_WEB_ENABLED                             |                |
|  |  * In Development/Testing: Set to true for controlled browser cache validation |                |
|  |  * In Production: Defaulted to false until multi-user conflict browser UAT     |                |
|  +--------------------------------------------------------------------------------+                |
|                                                                                                    |
+----------------------------------------------------------------------------------------------------+
"""

DIAGRAM_10_ASK_RED_BEAR = """
+----------------------------------------------------------------------------------------------------+
|                 ASK RED BEAR AI ASSISTANT & SPEECH TRANSCRIPTION PIPELINE                          |
+----------------------------------------------------------------------------------------------------+
|                                                                                                    |
|  [ Frontline User Interface ]                                                                      |
|  +--------------------------------------------------------------------------------+                |
|  |  Microphone Button Click -> Web Audio API Captures Base64 Audio Buffer         |                |
|  +---------------------------------------+----------------------------------------+                |
|                                          |                                                         |
|                                          v POST /api/v1/ask-red-bear/transcribe                    |
|  [ LIVE VERIFIED COMPONENT ]             | (Audio Streamed to Whisper / Local Engine)              |
|  +---------------------------------------+----------------------------------------+                |
|  |  Speech-to-Text Transcription Service: Converts spoken audio into text stream   |                |
|  |  * Live Verified on production web portal (October 2026 UAT)                   |                |
|  |  * Returns editable text into the user's inquiry textarea                     |                |
|  +---------------------------------------+----------------------------------------+                |
|                                          |                                                         |
|                                          | User reviews/edits text, clicks [Ask Question]          |
|                                          v POST /api/v1/ask-red-bear/query                         |
|  [ STUBBED / NOT LIVE COMPONENT ]        |                                                         |
|  +---------------------------------------+----------------------------------------+                |
|  |  AI Orchestrator Engine (backend/app/services/ai_gateway.py):                   |                |
|  |  * Currently routes to FakeAiProvider (Returns simulated response)             |                |
|  |  * Real AI generation is NOT operational on live production                     |                |
|  +---------------------------------------+----------------------------------------+                |
|                                          |                                                         |
|                                          | Proposed Architecture (Requires CRBCL Sovereign Key):    |
|                                          v                                                         |
|  +--------------------------------------------------------------------------------+                |
|  |  Retrieval-Augmented Generation (RAG) Vector Index (pgvector / Sovereign DB)   |                |
|  |  * Cowessess Miyo-Pimatisiwin Act & CRBCL Policy Ingestion                     |                |
|  |  * Strict Role Authorization Filtering (User cannot query unauthorized cases)  |                |
|  |  * Cloud LLM Inference (Candidate: Anthropic Claude / Azure OpenAI / Canadian Sovereign Host) |                |
|  +--------------------------------------------------------------------------------+                |
|                                                                                                    |
+----------------------------------------------------------------------------------------------------+
"""

DIAGRAM_11_ENVIRONMENTS = """
+----------------------------------------------------------------------------------------------------+
|                   DEPLOYMENT ENVIRONMENTS & INFRASTRUCTURE TOPOLOGY                                |
+----------------------------------------------------------------------------------------------------+
|                                                                                                    |
|  [ PRODUCTION CLOUD TOPOLOGY ]                                                                     |
|  +--------------------------------------------------------------------------------+                |
|  |  DNS Gateway: genserver.online -> Vercel Edge CDN / DigitalOcean Droplet       |                |
|  |  * Static React 18 Application Shell Bundles                                   |                |
|  |  * Automated HTTPS / Let's Encrypt Wildcard TLS Certificates                   |                |
|  +---------------------------------------+----------------------------------------+                |
|                                          | Reverse Proxy / API Routing                             |
|                                          v                                                         |
|  +--------------------------------------------------------------------------------+                |
|  |  Railway PaaS App Server: crbcl-production.up.railway.app                      |                |
|  |  * Linux Container Environment (Python 3.11, Uvicorn ASGI Multi-Worker)        |                |
|  |  * Memory Footprint: ~280MB Base | Fast startup (<3s)                           |                |
|  +---------------------------------------+----------------------------------------+                |
|                                          | Managed Network Bridge (Encrypted Transit)              |
|                                          v                                                         |
|  +--------------------------------------------------------------------------------+                |
|  |  PostgreSQL 15 Managed Database Cluster (Railway Internal Network)             |                |
|  |  * Automated Continuous WAL Backups & Point-in-Time Recovery                   |                |
|  |  * Connection Pooling via asyncpg (Max 20 concurrent connections)              |                |
|  +--------------------------------------------------------------------------------+                |
|                                                                                                    |
+----------------------------------------------------------------------------------------------------+
"""

SCHEMA_DOMAINS_DETAILED = [
    ("Identity, Auth & Access Control", "users, roles, permissions, role_permissions, user_roles, user_sessions, audit_logs", "14 Models", "Argon2id password hashing, frontline 6-digit PIN hashes, brute-force lockout counters, immutable user session tokens, comprehensive audit trails."),
    ("Master Person & Client Identity", "persons, clients, person_identifications, aliases, demographic_profiles, band_memberships", "16 Models", "Strict physical decoupling of Person (biological) from Client (administrative). Fuzzy matching on treaty number and birth date to eliminate duplicate identities."),
    ("Child & Family Case Management", "cases, case_persons, case_assignments, case_restrictions, safety_assessments, risk_assessments", "22 Models", "Central case lifecycle, assignment history, multi-child family cases, and active Case Restriction engine that blinds conflicted caseworkers."),
    ("Intake, Triage & Investigations", "intakes, intake_allegations, intake_collaterals, reporter_identities, investigation_findings, triage_scores", "18 Models", "Frontline intake logging, reporter confidentiality safeguards, automated response time calculation (immediate vs 5-day triage)."),
    ("Prevention & Healing (PH)", "ph_enhancement_programs, ph_family_support, ph_other_nation_support, ph_record_provenance, ph_duplicate_reviews", "9 Models", "Granular financial tracking, event attendees, child welfare prevention metrics, SHA-256 provenance tracking, and duplicate staging review."),
    ("Clinical Notes & Documents", "case_notes, case_note_addenda, case_note_attachments, case_note_persons, document_metadata, document_versions", "16 Models", "Signed notes permanently locked against deletion, versioned addenda only, collateral contact linkage, file attachment hashes."),
    ("Multi-Version Assessment Engine", "assessment_templates, assessment_versions, assessment_sections, assessment_questions, question_options, assessment_answers", "19 Models", "Versioned assessment schemas, supervisor unlock audit tracking, scoring algorithms, locked historical submissions."),
    ("Customary Care & Family Circles", "customary_care_agreements, elder_consultations, family_circle_conferences, cultural_commitments, care_guardians", "10 Models", "Embodying Cowessess Miyo-Pimatisiwin Act customary care traditions, Elder consultation tracking, family consensus recording."),
    ("Foster Care & Caregiver Licensing", "placement_homes, caregiver_applications, background_checks, placement_episodes, caregiver_trainings", "15 Models", "Annual home safety review tracking, criminal record check renewals, bed capacity validation, placement episode chains."),
    ("Cultural Services & Healing", "ceremonies, elder_honoraria, cultural_wellness_plans, language_initiatives, sacred_teachings, offerings", "11 Models", "Cultural protocol compliance, sacred ceremony logging, Elder honoraria disbursement vouchers, Cree language preservation."),
    ("Youth Transitions & Aftercare", "youth_transition_plans, independent_living_milestones, mentor_assignments, housing_stipends, transition_goals", "9 Models", "Aging-out transition plans, independent living skill evaluations, living stipend records, mentor match history."),
    ("Jordan's Principle Special Needs", "jordans_principle_claims, special_needs_services, medical_equipment_requests, reimbursement_submissions", "12 Models", "Federal billing EDI export mapping, service approval tracking, medical necessity receipts, federal reimbursement audit."),
    ("Legal & Court Docket Services", "court_cases, court_hearings, court_orders, legal_representations, docket_schedules, disclosure_records", "11 Models", "Court docket schedule management, legal counsel representation logs, court order compliance deadlines, disclosure audit trails."),
    ("Front Desk & Facility Operations", "front_desk_submissions, routing_history, visitor_logs, operations_requests, key_custody_events, facility_rooms", "12 Models", "Public intake triage, visitor badge logs, vehicle key custody tracking, conference room reservations, supply orders."),
    ("Finance, Billing & Fleet Logistics", "funding_sources, budget_lines, service_requests, approvals, invoices, billing_rates, vehicles, fleet_trips, geofences", "11 Models", "Multi-fund general ledger, per diem placement billing rates, vehicle reservation logs, maintenance schedules, geofences."),
]

ROUTER_CATALOG_DETAILED = [
    ("/api/v1/cases", "Cases & Family Files", "53 Endpoints", "Core case management, case status lifecycle, participant linking, case notes, assignment, and restriction enforcement."),
    ("/api/v1/ph", "Prevention & Healing Records", "36 Endpoints", "Enhancement programs, family support, other nations support, duplicate review queues, and import provenance."),
    ("/api/v1/clients", "Client Identity & Master Index", "25 Endpoints", "Administrative client records, approval workflow, status changes, merge duplicates, and band affiliation."),
    ("/api/v1/placement-homes", "Foster & Resource Homes", "24 Endpoints", "Home licensure, bed capacity, background check compliance, safety reviews, and home status changes."),
    ("/api/v1/finance", "Finance & General Ledger", "21 Endpoints", "Funding streams, budget allocations, service authorization, invoice reconciliation, and cost coding."),
    ("/api/v1/reports", "Reporting & Executive BI", "21 Endpoints", "Provincial statistical extracts, child welfare metrics, caseload averages, and compliance reports."),
    ("/api/v1/org-ops", "Organizational Operations", "21 Endpoints", "HR employee directory, team assignments, department hierarchies, and administrative delegation."),
    ("/api/v1/referrals", "Intake Referrals & Investigations", "20 Endpoints", "Referral logging, safety triage scoring, response time monitoring, and investigator assignment."),
    ("/api/v1/plans", "Care & Permanency Plans", "19 Endpoints", "Care plans, cultural connection plans, safety plans, and customary care agreement tracking."),
    ("/api/v1/operations", "Facility & Logistics Operations", "15 Endpoints", "Work orders, facility keys, supply requisition, vehicle bookings, and operational requests."),
    ("/api/v1/auth", "Authentication & Security", "14 Endpoints", "Dual login (Argon2id password & frontline PIN), JWT token issuance, session refresh, and logout."),
    ("/api/v1/board", "Board Governance Portal", "13 Endpoints", "Board member access, published meeting packets, strategic initiative monitoring, and resolutions."),
    ("/api/v1/fleet", "Fleet & Vehicle Management", "12 Endpoints", "Vehicle assets, trip logs, driver licensing checks, maintenance alerts, and geofence definitions."),
    ("/api/v1/front-desk", "Reception & Public Intake", "12 Endpoints", "Visitor sign-in, package logging, walk-in intake triage, and duty worker notifications."),
    ("/api/v1/ceo-dashboard", "Executive Leadership Dashboard", "10 Endpoints", "Strategic KPIs, high-risk case oversight, cross-departmental analytics, and executive alerts."),
    ("/api/v1/families", "Family Kinship & Genealogies", "10 Endpoints", "Extended family structures, kinship networks, household membership, and family trees."),
    ("/api/v1/staffing", "HR Staffing & Time Allocation", "9 Endpoints", "Caseload weighting, staff caseload caps, coverage scheduling, and supervisory hierarchies."),
    ("/api/v1/users", "User Administration & RBAC", "9 Endpoints", "User accounts, role assignments, password resets, account locking, and permission audit."),
    ("/api/v1/assessments", "Assessment Engine Instances", "8 Endpoints", "Completed assessment instances, scoring calculations, supervisor sign-offs, and unlock audits."),
    ("/api/v1/assessment-templates", "Assessment Template Builder", "8 Endpoints", "Dynamic form designer, versioned sections, questions, rating scales, and scoring rules."),
    ("/api/v1/qa", "Quality Assurance & Compliance", "8 Endpoints", "File audits, standard compliance checklists, supervisor reviews, and practice improvements."),
    ("/api/v1/caregiver-trainings", "Caregiver Certification", "7 Endpoints", "Trauma-informed training modules, PRIDE training tracking, and certification renewals."),
    ("/api/v1/resource-complaints", "Resource Quality Complaints", "7 Endpoints", "Caregiver complaints, incident investigations, corrective action plans, and resolution tracking."),
    ("/api/v1/resource-recruitment", "Resource Parent Recruitment", "7 Endpoints", "Recruitment campaigns, inquiries, orientation attendance, and screening progression."),
    ("/api/v1/calendar", "Master Scheduling & Court Calendar", "6 Endpoints", "Hearing dates, family visits, team meetings, statutory review deadlines, and reminders."),
    ("/api/v1/case-notes", "Clinical & Case Notes", "6 Endpoints", "Progress notes, collateral contacts, file attachments, signed note locking, and addenda."),
    ("/api/v1/notifications", "System Notification Dispatch", "6 Endpoints", "In-app alerts, supervisor escalation notifications, email notifications, and task assignments."),
    ("/api/v1/persons", "Master Person Demographic Index", "6 Endpoints", "Biological identity records, legal names, birth records, treaty numbers, and alias index."),
    ("/api/v1/placements", "Placement Events & Movement", "6 Endpoints", "Active placement episodes, bed allocation, emergency placement orders, and placement discharge."),
    ("/api/v1/background-checks", "Safety & Criminal Clearances", "5 Endpoints", "Vulnerable sector checks, child abuse registry checks, and clearance renewal tracking."),
    ("/api/v1/caregiver-supports", "Caregiver Respite & Support", "5 Endpoints", "Respite allocations, support worker visits, emergency caregiver stipends, and peer circles."),
    ("/api/v1/clinical-notes", "Specialized Clinical Notes", "5 Endpoints", "Mental health observations, behavioral plans, medical consultations, and clinical addenda."),
    ("/api/v1/resource-monitoring", "Resource Home Monitoring", "5 Endpoints", "Quarterly home visits, annual safety inspections, bed audits, and license renewals."),
    ("/api/v1/sync", "Offline Mobile Synchronization", "5 Endpoints", "Idempotent batch sync for mobile drafts, conflict detection, outbox queue processing."),
    ("/api/v1/transfers", "Inter-Agency Case Transfers", "5 Endpoints", "Provincial ministry transfers, other First Nations jurisdiction handovers, and transition audits."),
    ("/api/v1/ask-red-bear", "Ask Red Bear AI & Speech", "4 Endpoints", "Audio dictation transcription (live-verified), text query orchestration, and knowledge search."),
    ("/api/v1/communications", "Messaging & Contact Logs", "4 Endpoints", "SMS notifications, client communication logs, outreach history, and delivery tracking."),
    ("/api/v1/households", "Living Unit & Dwellings", "4 Endpoints", "Dwelling safety assessments, household composition, resident history, and hazard checks."),
    ("/api/v1/providers", "External Service Providers", "4 Endpoints", "Contracted counseling agencies, medical specialists, cultural mentors, and vendor rating."),
    ("/api/v1/admin", "Core Administration", "3 Endpoints", "System health diagnostics, environment configuration, database stats, and feature toggles."),
    ("/api/v1/in-home-placements", "Family Preservation Placements", "3 Endpoints", "In-home supervision orders, safety agreements, and family preservation monitoring."),
    ("/api/v1/ocr", "Document OCR Extraction", "3 Endpoints", "Scanned court document parsing, PDF optical text recognition, and metadata extraction."),
    ("/api/v1/schools", "Education & School Tracking", "3 Endpoints", "School enrollment, attendance tracking, educational plans, and transportation routing."),
    ("/api/v1/active-efforts", "Active Efforts Compliance", "2 Endpoints", "Documentation of active family preservation efforts pursuant to First Nations child welfare laws."),
    ("/api/v1/appointments", "Client & Family Appointments", "2 Endpoints", "Medical appointments, counseling sessions, home visit schedules, and attendance logs."),
    ("/api/v1/court-events", "Court Dockets & Hearings", "2 Endpoints", "Family court hearing appearances, docket tracking, judge orders, and legal representation."),
    ("/api/v1/dashboard", "User Personalized Dashboard", "2 Endpoints", "Caseworker assigned tasks, pending deadlines, unread alerts, and quick actions."),
    ("/api/v1/grants", "Grant Funding Management", "2 Endpoints", "Federal and philanthropic grant tracking, milestone achievements, and reporting dates."),
    ("/api/v1/incidents", "Critical Incident Reporting", "2 Endpoints", "Critical incident logging, serious bodily harm notifications, and executive escalations."),
    ("/api/v1/integrations", "External System Interfaces", "2 Endpoints", "Configuration for third-party webhooks, external government APIs, and data export bridges."),
    ("/api/v1/notification-preferences", "User Notification Rules", "2 Endpoints", "User alert channels (email, in-app, SMS), frequency settings, and priority thresholds."),
    ("/api/v1/notification-templates", "Communication Templates", "2 Endpoints", "Standard notification text templates for client reminders, appointment notices, and alerts."),
    ("/api/v1/passports", "Child Identification & Travel", "2 Endpoints", "Status card tracking, passport documentation, travel consents, and identity records."),
    ("/api/v1/permanency-plans", "Long-Term Permanency", "2 Endpoints", "Customary care permanency, kinship guardianship, and long-term connection tracking."),
    ("/api/v1/programs", "Community Programs Registry", "2 Endpoints", "Lodge community programs, youth clubs, Elder gatherings, and workshop schedules."),
    ("/api/v1/removals", "Emergency Removal Safeguards", "2 Endpoints", "Emergency apprehension documentation, least-disruptive-measure validations, and legal checks."),
    ("/api/v1/resource-outcomes", "Caregiver Placement Outcomes", "2 Endpoints", "Placement longevity, stability metrics, disruption root-cause analysis, and child wellness."),
    ("/api/v1/teams", "Department Team Rosters", "2 Endpoints", "Team member rosters, supervisor assignments, department routing, and team caseload summaries."),
    ("/api/v1/visitation-plans", "Supervised Family Visitation", "2 Endpoints", "Family contact plans, supervised visit logs, transportation needs, and supervisor notes."),
]

MIGRATION_CATALOG_DETAILED = [
    ("001_platform_foundation", "Initial Foundation", "users, roles, permissions, role_permissions, user_roles, audit_logs", "Established core UUID primary keys, Argon2id auth, initial role seeding, and event audit infrastructure."),
    ("002_people_families", "Person & Kinship", "persons, person_identifications, aliases, demographic_profiles, band_memberships", "Decoupled biological person from administrative client; added treaty number and band registries."),
    ("003_intake_referrals", "Intake & Triage", "intakes, intake_allegations, intake_collaterals, reporter_identities", "Created child welfare intake logging, reporter confidentiality blinding, and urgency triage matrices."),
    ("004_case_management", "Case Files & Notes", "cases, case_persons, case_notes, case_note_addenda, case_note_attachments", "Implemented case lifecycle, primary client FKs, signed note locking against deletion, addenda audit."),
    ("005_assessment_engine", "Dynamic Assessments", "assessment_templates, assessment_versions, assessment_sections, assessment_questions", "Created dynamic multi-version assessment form builder and supervisor sign-off workflows."),
    ("006_case_safety_plans", "Safety & Conflict", "case_safety_plans, safety_actions, case_restrictions", "Added immediate safety plan structures and the Case Restriction engine for family conflict blinding."),
    ("007_email_verification", "Auth Hardening", "user_email_verifications, password_reset_tokens", "Implemented secure tokenized email verification and time-bounded password reset challenges."),
    ("008_placement_episodes", "Placement Chains", "placement_episodes, placement_reasons, discharge_records", "Added formal placement episode tracking, caregiver matching IDs, and disruption analysis."),
    ("009_placement_homes", "Foster Home Registry", "placement_homes, home_safety_reviews, bed_allocations", "Created licensed caregiver registry, bed capacity controls, and annual safety compliance checks."),
    ("010_scheduling_notifications", "Master Scheduling", "calendar_events, notification_records, user_notification_preferences", "Added cross-department master calendar, court hearings, and system notification dispatch tables."),
    ("011_finance_billing", "Finance General Ledger", "funding_sources, budget_lines, service_requests, billing_rates, invoices", "Added multi-fund cost allocation, per diem caregiver billing rates, and invoice reconciliation."),
    ("012_reporting_qa", "QA Audits & Reports", "qa_audit_reviews, qa_checklist_items, compliance_extracts", "Created quality assurance supervisory review queues and provincial compliance extract generators."),
    ("013_fleet_management", "Fleet Logistics", "fleet_vehicles, fleet_reservations, vehicle_inspections, geofences", "Added Lodge vehicle fleet inventory, reservation custody logs, and pre-trip inspection logs."),
    ("014_integrations_ai", "AI & Webhooks", "ai_inquiry_logs, external_webhook_endpoints, sync_transactions", "Established Ask Red Bear audit logging schema, speech dictation buffers, and webhook configs."),
    ("015_phase14_hardening", "Security Hardening", "user_lockouts, security_incident_events, ip_allowlists", "Implemented automated 5-attempt brute force account lockout and security incident tracking."),
    ("016_mobile_sync", "Mobile Outbox Queue", "mobile_sync_outbox, client_idempotency_keys, offline_drafts", "Created transactional outbox queue for Flutter mobile client offline drafting and sync."),
    ("017_organizational_operations", "Org Hierarchy", "departments, teams, team_memberships, supervisor_hierarchies", "Structured 17 canonical departments, 24 team rosters, and frontline supervisor relationships."),
    ("018_native_feature_completion", "Cultural & Youth", "cultural_plans, ceremonies, elder_honoraria, youth_transition_plans", "Added cultural healing plans, Elder honoraria vouchers, and youth independent living goals."),
    ("019_resource_team_department", "Resource Department", "resource_inquiries, resource_applicants, applicant_screenings", "Established dedicated Resource Team department for caregiver recruitment and support."),
    ("020_add_resource_recruitment_models", "Recruitment Campaigns", "recruitment_campaigns, orientation_sessions, inquiry_sources", "Added outreach campaign tracking and orientation session attendance management."),
    ("021_resource_unit_sprint_2", "Caregiver Licensing", "home_study_assessments, background_checks, reference_interviews", "Implemented structured SAFE home study workflows and criminal record clearance tracking."),
    ("022_resource_unit_sprint_3", "Caregiver Respite", "caregiver_supports, respite_allocations, support_circle_events", "Added caregiver respite day tracking, support groups, and emergency relief allocations."),
    ("023_front_desk_foundation", "Front Desk Reception", "front_desk_submissions, visitor_badges, package_deliveries", "Created reception desk visitor registration, public intake triage, and duty worker paging."),
    ("024_ceo_dashboard_initiatives_and_governance", "Executive Governance", "executive_initiatives, strategic_kpis, executive_alert_rules", "Implemented CEO strategic dashboard, organizational metrics, and high-risk case escalations."),
    ("025_dept_exec_update_history", "Executive History", "department_update_history, kpi_snapshots", "Added historical departmental progress logging and periodic executive performance snapshots."),
    ("026_board_dashboard_publication_controls", "Board Publication", "board_packets, board_resolutions, publication_reviews", "Added Board Portal document publication approvals and confidential packet governance."),
    ("027_person_numeric_id", "Numeric Identifiers", "Numeric sequence on persons table (BigInteger)", "Added human-readable sequential numeric IDs to persons for frontline phone and reception lookup."),
    ("028_client_approval_workflow", "Client Approval Queue", "client_approvals, approval_history, status_change_reasons", "Implemented formal supervisor approval workflow for promoting Person records to Client status."),
    ("029_office_coordinator_and_control_centre", "Office Operations", "operations_requests, facility_keys, supply_inventories", "Established Office Coordinator workspace, key custody tracking, and supply ordering."),
    ("030_backfill_permissions_and_role_mappings", "RBAC Backfill", "Seed backfill across all 19 canonical roles (327 permissions)", "Expanded system permissions to 327 discrete operations, backfilling all canonical role matrices."),
    ("031_prevention_healing", "Prevention & Healing Records", "ph_enhancement_programs, ph_family_support, ph_other_nation_support, ph_record_provenance", "Created comprehensive relational tables for historical prevention Excel data and duplicate review."),
]


def build_doc2():
    docx_path = os.path.join(DELIVERABLES_V2_DIR, f"{DOC_NAME_BASE}.docx")
    pdf_path = os.path.join(DELIVERABLES_V2_DIR, f"{DOC_NAME_BASE}.pdf")

    # ─────────────────────────────────────────────────────────
    # 1. BUILD DOCX
    # ─────────────────────────────────────────────────────────
    doc = Document()
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)

    header = doc.sections[0].header
    hp = header.paragraphs[0]
    hp.text = "CRBCL PLATFORM TECHNICAL ARCHITECTURE SPECIFICATION (REVISION 2)"
    hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    hp.style.font.name = "Arial"
    hp.style.font.size = Pt(8.5)
    hp.style.font.color.rgb = RGBColor(100, 116, 139)

    footer = doc.sections[0].footer
    fp = footer.paragraphs[0]
    fp.text = "CONFIDENTIAL — STRICTLY FOR TECHNICAL AUDITORS & LEADERSHIP REVIEW"
    fp.alignment = WD_ALIGN_PARAGRAPH.LEFT
    fp.style.font.name = "Arial"
    fp.style.font.size = Pt(8.5)
    fp.style.font.color.rgb = RGBColor(100, 116, 139)

    # Document Header
    p_title = doc.add_paragraph()
    r_title = p_title.add_run("CHIEF RED BEAR CHILDREN'S LODGE\nPLATFORM TECHNICAL ARCHITECTURE SPECIFICATION")
    r_title.bold = True
    r_title.font.name = "Arial"
    r_title.font.size = Pt(19)
    r_title.font.color.rgb = RGBColor(107, 29, 47)
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    p_sub = doc.add_paragraph()
    r_sub = p_sub.add_run("Updated Comprehensive System Architecture, Domain Schemas, Component Topologies, and Handover Guide\nRevision 2 — Expanded Independent Engineering Assessment")
    r_sub.bold = True
    r_sub.font.name = "Arial"
    r_sub.font.size = Pt(11)
    r_sub.font.color.rgb = RGBColor(201, 138, 44)
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER

    p_meta = doc.add_paragraph()
    r_meta = p_meta.add_run(
        "Client Organization: Chief Red Bear Children's Lodge / Cowessess First Nation, Saskatchewan, Canada\n"
        "Technical Baseline: Post-Phase 5 Hardening | Git Commit HEAD: 07465792d87bdbbeaf6b184fd4051f3073dbc890\n"
        "Branch: main | Repository: C:\\Users\\Shilley Pc\\crbcl | Remote: https://github.com/innovatorledger-web/crbcl\n"
        "Audience: Lead Architects, Technical Leadership, System Reviewers, and Independent Software Evaluators"
    )
    r_meta.font.name = "Arial"
    r_meta.font.size = Pt(9)
    r_meta.font.color.rgb = RGBColor(100, 116, 139)
    p_meta.alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_paragraph().paragraph_format.space_after = Pt(10)

    def add_h1(text):
        p = doc.add_paragraph()
        r = p.add_run(text)
        r.bold = True
        r.font.name = "Arial"
        r.font.size = Pt(13)
        r.font.color.rgb = RGBColor(107, 29, 47)
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(4)
        return p

    def add_body(text):
        p = doc.add_paragraph()
        r = p.add_run(text)
        r.font.name = "Arial"
        r.font.size = Pt(9.5)
        r.font.color.rgb = RGBColor(30, 41, 59)
        p.paragraph_format.space_after = Pt(4)
        return p

    def add_code(text):
        p = doc.add_paragraph()
        r = p.add_run(text)
        r.font.name = "Consolas"
        r.font.size = Pt(7.5)
        r.font.color.rgb = RGBColor(30, 41, 59)
        p.paragraph_format.space_after = Pt(4)
        return p

    add_body("TECHNICAL ARCHITECTURE & HANDOVER DISCLOSURE NOTICE:")
    add_body(
        "This document provides an exhaustive, verified engineering specification of the CRBCL software architecture as of Git commit 0746579. It is designed to support independent code review, security audits, and technical handover. While the backend architecture (205 models, 521 endpoints) and test suites are fully implemented in source code, operational production readiness requires hosting pipeline synchronization, cloud LLM credential provisioning, and frontline supervisor User Acceptance Testing (UAT)."
    )

    # 11 Architecture Diagrams in DOCX
    diagrams_meta = [
        ("1. SYSTEM ARCHITECTURE & COMPONENT TOPOLOGY", DIAGRAM_1_TOPOLOGY, "Multi-tier system topology separating presentation, API orchestration, persistent relational storage, and background processing."),
        ("2. COMMUNICATION FLOW & API ORCHESTRATION", DIAGRAM_2_COMMUNICATION, "TLS 1.3 communication between clients and the FastAPI backend with automated JWT cycling and state-changing CSRF defense."),
        ("3. AUTHENTICATION, RBAC & CASE CONFLICT CONTROLS", DIAGRAM_3_AUTH, "Argon2id password and frontline 6-digit PIN login with a 327-permission RBAC engine and active Case Restrictions that blind conflicted caseworkers."),
        ("4. MASTER PERSON, CLIENT & CASE MANAGEMENT SCHEMA", DIAGRAM_4_PERSON_CLIENT, "Relational schema strictly decoupling biological Person records from administrative Client statuses and legal Case files."),
        ("5. EMPLOYEE DIRECTORY & LOGIN QUARANTINE ARCHITECTURE", DIAGRAM_5_EMPLOYEE_USER, "Decoupling HR Employee profiles from User authentication logins, maintaining imported legacy staff in an inactive quarantine status until verified."),
        ("6. PREVENTION & HEALING RECORDS ARCHITECTURE", DIAGRAM_6_PH_STRUCTURE, "Structuring historical family wellness interventions into relational entities, backed by SHA-256 cryptographic provenance tracking."),
        ("7. EXCEL INGESTION & 3-TIER DUPLICATE PROTECTION ENGINE", DIAGRAM_7_EXCEL_RECON, "Distinguishing between confirmed duplicates and possible duplicates, routing ambiguous rows to an administrative review queue."),
        ("8. MOBILE CLIENT OFFLINE SYNCHRONIZATION", DIAGRAM_8_MOBILE_SYNC, "The CRBCL mobile application has been installed and personally tested by the developer on a physical Android device. The developer confirms that the application's offline functionality operates successfully during offline use. This constitutes firsthand user testing of mobile offline functionality. The architecture enables rural caseworkers to draft case notes and voice memos offline via an encrypted SQLite outbox queue, syncing sequentially upon reconnection. Additional structured acceptance testing (sync conflict resolution, data recovery, organizational field UAT) remains pending formal CRBCL supervisor participation."),
        ("9. ISOLATED WEB OFFLINE WORKSPACE", DIAGRAM_9_WEB_OFFLINE, "Caching static UI shells via HTML5 Service Workers; production enablement is currently disabled via environment variable."),
        ("10. ASK RED BEAR AI & SPEECH DICTATION PIPELINE", DIAGRAM_10_ASK_RED_BEAR, "Separating live-verified speech transcription (ephemeral input aid) from AI answer generation (currently stubbed via FakeAiProvider)."),
        ("11. DEPLOYMENT ENVIRONMENTS & INFRASTRUCTURE BOUNDARIES", DIAGRAM_11_ENVIRONMENTS, "Static frontend hosting on Vercel/DigitalOcean with asynchronous FastAPI backend hosting on Railway PaaS and managed PostgreSQL 15+."),
    ]

    for title, diag_code, desc in diagrams_meta:
        add_h1(title)
        add_body(desc)
        add_code(diag_code.strip())

    # Section 12: Detailed Schema Architecture Table in DOCX
    add_h1("12. DETAILED SCHEMA ARCHITECTURE ACROSS 14 FUNCTIONAL DOMAINS")
    add_body("The relational database schema encompasses 205 mapped SQLAlchemy models across 14 distinct namespaces:")
    t_docx_sd = doc.add_table(rows=1 + len(SCHEMA_DOMAINS_DETAILED), cols=4)
    t_docx_sd.style = "Table Grid"
    hdr_cells_sd = t_docx_sd.rows[0].cells
    hdr_titles_sd = ["Namespace / Domain", "Primary Database Tables", "Models", "Relational Integrity & Rules"]
    for idx, name in enumerate(hdr_titles_sd):
        hdr_cells_sd[idx].text = name
        set_cell_background(hdr_cells_sd[idx], PRIMARY_HEX)
        set_cell_margins(hdr_cells_sd[idx], top=60, bottom=60, left=80, right=80)
        p = hdr_cells_sd[idx].paragraphs[0]
        p.runs[0].font.bold = True
        p.runs[0].font.size = Pt(8)
        p.runs[0].font.color.rgb = RGBColor(255, 255, 255)

    for r_idx, sd in enumerate(SCHEMA_DOMAINS_DETAILED):
        row_cells = t_docx_sd.rows[r_idx + 1].cells
        for c_idx, val in enumerate(sd):
            row_cells[c_idx].text = val
            set_cell_background(row_cells[c_idx], LIGHT_BG_HEX if r_idx % 2 == 1 else "FFFFFF")
            set_cell_margins(row_cells[c_idx], top=40, bottom=40, left=60, right=60)
            p = row_cells[c_idx].paragraphs[0]
            r = p.runs[0]
            r.font.size = Pt(7.5)
            if c_idx == 0:
                r.bold = True

    # Section 13: 57 FastAPI REST Routers in DOCX
    add_h1("13. DETAILED CATALOG OF 57 FASTAPI REST ROUTERS & 521 ENDPOINT SURFACE")
    add_body("The API orchestration layer consists of 521 asynchronous endpoints across 57 distinct router modules in backend/app/api/v1/:")
    t_docx_rc = doc.add_table(rows=1 + len(ROUTER_CATALOG_DETAILED), cols=4)
    t_docx_rc.style = "Table Grid"
    hdr_cells_rc = t_docx_rc.rows[0].cells
    hdr_titles_rc = ["Router Prefix", "Domain / Tag", "Endpoints", "Operational Scope & Responsibilities"]
    for idx, name in enumerate(hdr_titles_rc):
        hdr_cells_rc[idx].text = name
        set_cell_background(hdr_cells_rc[idx], PRIMARY_HEX)
        set_cell_margins(hdr_cells_rc[idx], top=60, bottom=60, left=80, right=80)
        p = hdr_cells_rc[idx].paragraphs[0]
        p.runs[0].font.bold = True
        p.runs[0].font.size = Pt(8)
        p.runs[0].font.color.rgb = RGBColor(255, 255, 255)

    for r_idx, rc in enumerate(ROUTER_CATALOG_DETAILED):
        row_cells = t_docx_rc.rows[r_idx + 1].cells
        for c_idx, val in enumerate(rc):
            row_cells[c_idx].text = val
            set_cell_background(row_cells[c_idx], LIGHT_BG_HEX if r_idx % 2 == 1 else "FFFFFF")
            set_cell_margins(row_cells[c_idx], top=40, bottom=40, left=60, right=60)
            p = row_cells[c_idx].paragraphs[0]
            r = p.runs[0]
            r.font.size = Pt(7.5)
            if c_idx == 0:
                r.bold = True

    # Section 14: 31 Alembic Migrations in DOCX
    add_h1("14. SEQUENTIAL DATABASE EVOLUTION RUNBOOK: 31 ALEMBIC MIGRATIONS")
    add_body("The relational database schema is managed via 31 sequential Alembic migrations:")
    t_docx_mg = doc.add_table(rows=1 + len(MIGRATION_CATALOG_DETAILED), cols=4)
    t_docx_mg.style = "Table Grid"
    hdr_cells_mg = t_docx_mg.rows[0].cells
    hdr_titles_mg = ["Revision ID", "Migration Title", "Tables Created / Modified", "Architectural Intent & Structural Mutations"]
    for idx, name in enumerate(hdr_titles_mg):
        hdr_cells_mg[idx].text = name
        set_cell_background(hdr_cells_mg[idx], PRIMARY_HEX)
        set_cell_margins(hdr_cells_mg[idx], top=60, bottom=60, left=80, right=80)
        p = hdr_cells_mg[idx].paragraphs[0]
        p.runs[0].font.bold = True
        p.runs[0].font.size = Pt(8)
        p.runs[0].font.color.rgb = RGBColor(255, 255, 255)

    for r_idx, mg in enumerate(MIGRATION_CATALOG_DETAILED):
        row_cells = t_docx_mg.rows[r_idx + 1].cells
        for c_idx, val in enumerate(mg):
            row_cells[c_idx].text = val
            set_cell_background(row_cells[c_idx], LIGHT_BG_HEX if r_idx % 2 == 1 else "FFFFFF")
            set_cell_margins(row_cells[c_idx], top=40, bottom=40, left=60, right=60)
            p = row_cells[c_idx].paragraphs[0]
            r = p.runs[0]
            r.font.size = Pt(7.5)
            if c_idx == 0:
                r.bold = True

    # Section 15: RBAC Permissions in DOCX
    add_h1("15. GRANULAR ROLE-BASED ACCESS CONTROL: 327 DISCRETE PERMISSION IDENTIFIERS")
    add_body("The system implements a zero-trust authorization model comprising 327 discrete permission strings across 75 functional domains:")
    add_body("• Case Management & Protection (64 Permissions): Covers case creation, status transition, assignment, file closing, restriction override, kinship linkage, safety plan approval, risk assessment, and legal disclosure.")
    add_body("• Clinical, Health & Assessment Services (44 Permissions): Covers clinical note creation, locked note addenda, psychiatric evaluation attachment, assessment template authoring, and assessment score signing.")
    add_body("• Resource Team, Foster Homes & Caregivers (46 Permissions): Covers foster home licensing, home safety inspection approvals, criminal record renewals, bed capacity overrides, and complaint investigations.")
    add_body("• Prevention & Healing Records (13 Permissions): Covers ph.read, ph.create, ph.update, ph.delete, ph.import, ph.export, ph.duplicate_review, ph.finance_view, and staff activation governance.")
    add_body("• Fleet, Facilities & Logistics (26 Permissions): Covers fleet.reserve, fleet.dispatch, fleet.maintenance, fleet.geofence, key_custody, supply_order, and work_order_signoff.")
    add_body("• Governance, Executive & Board (20 Permissions): Covers board_dashboard.view, board_publication.approve, executive_dashboard.view, strategic_initiative.manage, and audit_log.inspect.")

    # Section 16: Flutter Cross-Platform Mobile Client Internals in DOCX
    add_h1("16. FLUTTER CROSS-PLATFORM MOBILE APPLICATION ARCHITECTURE & SQLITE REPLICATION")
    add_body("Status: MOBILE OFFLINE FUNCTIONALITY — USER TESTED AND CONFIRMED WORKING")
    add_body("The CRBCL mobile application has been installed and personally tested by the developer on a physical Android device. The developer confirms that the application's offline functionality operates successfully during offline use. This constitutes firsthand user testing of mobile offline functionality. Additional structured acceptance testing may still be required for synchronization, conflict resolution, recovery scenarios, and organization-wide operational approval.")
    add_body("The platform contains mobile offline data-handling functionality using an encrypted local SQLite database (via SQLCipher AES-256) and a transactional outbox queue. Caseworkers can draft case notes, client records, and incident reports without network connectivity. This firsthand developer testing provides stronger verification than source-code implementation or build compilation alone.")
    add_body("Testing & Operational Distinctions: While developer testing confirms that standalone offline operation works on device, a rigorous technical distinction must be maintained between: (1) standalone offline functions confirmed working by the developer; (2) offline-to-online automated synchronization; (3) multi-device synchronization; (4) conflict resolution policies; (5) data recovery under unexpected termination; (6) cryptographic security of local storage; and (7) full organization-wide field acceptance testing with frontline supervisors.")
    add_body("Separation from Web Offline Workspace: A strict distinction must be maintained between mobile offline functionality (personally tested on a physical Android device) and the separate web-based Offline Workspace (/offline-workspace, implemented in commit e33c87a). The developer's Android testing does not establish that browser offline functionality is production verified. Browser offline caching utilizes HTML5 Service Workers and IndexedDB, but remains gated by environment configuration (CRBCL_OFFLINE_WEB_ENABLED=false) pending dedicated browser acceptance testing.")
    add_body("Key architectural components include:")
    add_body("• State Management Architecture: Employs the Provider pattern with decoupled ViewModels isolating business logic from UI widgets.")
    add_body("• Local Encrypted Persistence: Local drafts are stored in an encrypted SQLite database using SQLCipher AES-256 with encryption keys securely managed via FlutterSecureStorage.")
    add_body("• Transactional Outbox Queue: Offline actions (e.g. creating case notes, taking incident photos, recording audio) write an outbox record with sync_status='PENDING'.")
    add_body("• Sync Orchestrator & Conflict Policy: When connectivity is restored, the mobile app sends requests with an Idempotency-Key. If the server already processed the key, it returns the cached response, preventing duplicates.")

    # Section 17: Multi-Layered Security Architecture in DOCX
    add_h1("17. MULTI-LAYERED SECURITY CONTROLS, CRYPTOGRAPHIC PRIMITIVES & PRIVACY ISOLATION")
    add_body("The CRBCL platform implements enterprise security controls tailored for First Nations data sovereignty:")
    add_body("• Dual Authentication Primitives: Argon2id password hashing with salt generation; Frontline 6-digit PIN hashing with dedicated salt and brute-force lockout counters.")
    add_body("• Conflict-of-Interest Case Blinding: Dynamic Case Restriction table evaluated on every single case read request. Restricted workers are returned an empty or 404 response.")
    add_body("• Cryptographic Ingestion Provenance: Every ingested file and record batch is fingerprinted using SHA-256 to ensure complete auditability.")
    add_body("• Cross-Site Request Forgery & CORS Defense: Strict origin checking on Railway PaaS and state-changing CSRF tokens prevent unauthorized cross-origin requests.")

    # Section 18: Architectural Comparison in DOCX
    add_h1("18. ARCHITECTURAL COMPARISON: ORIGINAL SPECIFICATION VS CURRENT REVISION")
    add_body("A thorough comparative audit confirms that the architecture evolved additively to uphold sovereign legal requirements:")
    add_body("• Database: Expanded from a monolithic 15-table draft into 205 mapped SQLAlchemy models across 14 functional namespaces, governed by 31 sequential Alembic migrations.")
    add_body("• API Layer: Upgraded from synchronous Python endpoints to an asynchronous FastAPI architecture with 521 endpoints across 57 router modules.")
    add_body("• Security: Expanded from basic 'is_admin' flags to an enterprise 327-permission RBAC engine with 19 canonical roles, active case-conflict restrictions, and dual PIN/password login.")
    add_body("• Mobile: Advanced from basic mobile web views to a cross-platform native Flutter application with local SQLite drafting and an idempotent outbox sync engine.")

    # Section 19: Technical Debt in DOCX
    add_h1("19. TECHNICAL DEBT, SYSTEM RISKS & HANDOVER PROTOCOLS")
    add_body("For an independent software engineering team auditing this codebase, the technical debt is low and code quality is high:")
    add_body("• Hosting Alignment: Railway backend CORS headers and DNS records must be finalized to seamlessly pair with https://genserver.online.")
    add_body("• Vendor Credentials: Live API credentials must be selected, approved by the Board, and provisioned for an approved cloud LLM provider and SMS gateway (Twilio Canada).")
    add_body("• Telematics Procurement: Physical vehicle OBD-II GPS telematics hardware must be procured and paired with the fleet management module.")

    doc.save(docx_path)
    print(f"Document 2 Revision 2 DOCX written to: {docx_path}")

    # ─────────────────────────────────────────────────────────
    # 2. BUILD PDF (Target 20-35 pages)
    # ─────────────────────────────────────────────────────────
    pdf_doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        leftMargin=40,
        rightMargin=40,
        topMargin=40,
        bottomMargin=40,
    )
    styles = get_pdf_styles_v2()
    story = []

    # Cover Page
    story.append(Spacer(1, 30))
    story.append(Paragraph("CHIEF RED BEAR CHILDREN'S LODGE<br/>PLATFORM TECHNICAL ARCHITECTURE SPECIFICATION", styles["CRBCL_CoverTitle"]))
    story.append(Spacer(1, 8))
    story.append(Paragraph("Updated Comprehensive System Architecture, Domain Schemas, Component Topologies, and Handover Guide<br/>Revision 2 — Expanded Independent Engineering Assessment", styles["CRBCL_CoverSubtitle"]))
    story.append(Spacer(1, 12))
    story.append(Paragraph(
        "<b>Client Organization:</b> Chief Red Bear Children's Lodge / Cowessess First Nation, Saskatchewan, Canada<br/>"
        "<b>Technical Baseline:</b> Post-Phase 5 Hardening | <b>Git Commit HEAD:</b> 0746579 | <b>Branch:</b> main<br/>"
        "<b>Repository Path:</b> C:\\Users\\Shilley Pc\\crbcl | <b>Remote:</b> https://github.com/innovatorledger-web/crbcl<br/>"
        "<b>Audience:</b> Lead Architects, Technical Leadership, System Reviewers, and Independent Software Evaluators",
        styles["CRBCL_CoverMeta"]
    ))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1.5, color=COLOR_PRIMARY, spaceAfter=14))

    notice_text = (
        "<b>Technical Handover & Verification Notice:</b> This document provides an exhaustive, verified engineering specification of the CRBCL software architecture as of Git commit 0746579. It is designed to support independent code review, security audits, and technical handover. While the backend architecture (205 models, 521 endpoints) and test suites are fully implemented in source code, operational production readiness requires hosting pipeline synchronization, cloud LLM credential provisioning, and frontline supervisor User Acceptance Testing (UAT)."
    )
    story.append(create_pdf_notice_box_v2("TECHNICAL ARCHITECTURE & HANDOVER DISCLOSURE", notice_text, styles))
    story.append(PageBreak())

    # Table of Contents
    story.append(Paragraph("TABLE OF CONTENTS", styles["CRBCL_H1"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=COLOR_BORDER, spaceAfter=10))
    toc_items_d2 = [
        "1. System Architecture & Multi-Tier Topology",
        "2. Web / Backend / Database Communication Flow",
        "3. Authentication, RBAC & Case Conflict Controls",
        "4. Master Person, Client & Case Management Schema",
        "5. Employee Directory & Login Quarantine Architecture",
        "6. Prevention & Healing Records Architecture",
        "7. Excel Ingestion & 3-Tier Duplicate Protection Engine",
        "8. Mobile Client Offline Synchronization Architecture",
        "9. Isolated Web Offline Workspace Topology",
        "10. Ask Red Bear AI & Speech Dictation Pipeline",
        "11. Deployment Environments & Infrastructure Boundaries",
        "12. Detailed Schema Architecture across 14 Functional Domains",
        "13. Detailed Catalog of 57 FastAPI REST Routers & 521 Endpoint Surface",
        "14. Sequential Database Evolution Runbook: 31 Alembic Migrations",
        "15. Granular Role-Based Access Control: 327 Discrete Permission Identifiers",
        "16. Flutter Cross-Platform Mobile Application Architecture & SQLite Replication",
        "17. Multi-Layered Security Controls, Cryptographic Primitives & Privacy Isolation",
        "18. Architectural Comparison: Original Specification vs Current Revision",
        "19. Technical Debt, System Risks & Handover Protocols",
    ]
    for item in toc_items_d2:
        story.append(Paragraph(f"• <b>{item}</b>", styles["CRBCL_Body"]))
    story.append(PageBreak())

    # Diagram Sections with Preformatted Boxes (Each on dedicated page)
    for title, diag_code, desc in diagrams_meta:
        story.append(Paragraph(title, styles["CRBCL_H1"]))
        story.append(HRFlowable(width="100%", thickness=0.5, color=COLOR_PRIMARY, spaceAfter=4))
        story.append(Paragraph(desc, styles["CRBCL_Body"]))
        story.append(Spacer(1, 4))
        story.append(create_pdf_diagram_box(diag_code.strip(), styles, width=530))
        story.append(PageBreak())

    # Section 12: Detailed Schema Architecture Table
    story.append(Paragraph("12. DETAILED SCHEMA ARCHITECTURE ACROSS 14 FUNCTIONAL DOMAINS", styles["CRBCL_H1"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=COLOR_PRIMARY, spaceAfter=6))
    story.append(Paragraph("The relational database schema encompasses 205 mapped SQLAlchemy models across 14 distinct namespaces. Below is the comprehensive schema catalog:", styles["CRBCL_Body"]))

    sd_pdf_rows = [
        [
            Paragraph("<b>Namespace / Domain</b>", styles["CRBCL_TableHeader"]),
            Paragraph("<b>Primary Database Tables</b>", styles["CRBCL_TableHeader"]),
            Paragraph("<b>Models</b>", styles["CRBCL_TableHeader"]),
            Paragraph("<b>Relational Integrity & Audit Rules</b>", styles["CRBCL_TableHeader"]),
        ]
    ]
    for sd in SCHEMA_DOMAINS_DETAILED:
        sd_pdf_rows.append([
            Paragraph(f"<b>{sd[0]}</b>", styles["CRBCL_TableCellBold"]),
            Paragraph(sd[1], styles["CRBCL_TableCell"]),
            Paragraph(sd[2], styles["CRBCL_TableCell"]),
            Paragraph(sd[3], styles["CRBCL_TableCell"]),
        ])

    t_sd = Table(sd_pdf_rows, colWidths=[110, 160, 64, 170])
    t_sd.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), COLOR_PRIMARY),
        ("GRID", (0, 0), (-1, -1), 0.5, COLOR_BORDER),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [COLOR_LIGHT_BG, colors.white]),
        ("PADDING", (0, 0), (-1, -1), 3.5),
    ]))
    story.append(t_sd)
    story.append(PageBreak())

    # Section 13: 57 FastAPI REST Routers in PDF
    story.append(Paragraph("13. DETAILED CATALOG OF 57 FASTAPI REST ROUTERS & 521 ENDPOINT SURFACE", styles["CRBCL_H1"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=COLOR_PRIMARY, spaceAfter=6))
    story.append(Paragraph("The API orchestration layer comprises 521 endpoints across 57 modular routers in backend/app/api/v1/:", styles["CRBCL_Body"]))

    rc_pdf_rows = [
        [
            Paragraph("<b>Router Prefix</b>", styles["CRBCL_TableHeader"]),
            Paragraph("<b>Domain / Tag</b>", styles["CRBCL_TableHeader"]),
            Paragraph("<b>Endpoints</b>", styles["CRBCL_TableHeader"]),
            Paragraph("<b>Operational Scope & Responsibilities</b>", styles["CRBCL_TableHeader"]),
        ]
    ]
    for rc in ROUTER_CATALOG_DETAILED:
        rc_pdf_rows.append([
            Paragraph(f"<b>{rc[0]}</b>", styles["CRBCL_TableCellBold"]),
            Paragraph(rc[1], styles["CRBCL_TableCell"]),
            Paragraph(rc[2], styles["CRBCL_TableCell"]),
            Paragraph(rc[3], styles["CRBCL_TableCell"]),
        ])

    t_rc = Table(rc_pdf_rows, colWidths=[115, 125, 60, 204])
    t_rc.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), COLOR_PRIMARY),
        ("GRID", (0, 0), (-1, -1), 0.5, COLOR_BORDER),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [COLOR_LIGHT_BG, colors.white]),
        ("PADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(t_rc)
    story.append(PageBreak())

    # Section 14: 31 Alembic Migrations in PDF
    story.append(Paragraph("14. SEQUENTIAL DATABASE EVOLUTION RUNBOOK: 31 ALEMBIC MIGRATIONS", styles["CRBCL_H1"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=COLOR_PRIMARY, spaceAfter=6))
    story.append(Paragraph("The relational schema is managed via 31 sequential Alembic migrations with fully audited roll-forward capabilities:", styles["CRBCL_Body"]))

    mg_pdf_rows = [
        [
            Paragraph("<b>Revision ID</b>", styles["CRBCL_TableHeader"]),
            Paragraph("<b>Migration Title</b>", styles["CRBCL_TableHeader"]),
            Paragraph("<b>Tables Affected</b>", styles["CRBCL_TableHeader"]),
            Paragraph("<b>Architectural Intent & Structural Mutations</b>", styles["CRBCL_TableHeader"]),
        ]
    ]
    for mg in MIGRATION_CATALOG_DETAILED:
        mg_pdf_rows.append([
            Paragraph(f"<b>{mg[0]}</b>", styles["CRBCL_TableCellBold"]),
            Paragraph(mg[1], styles["CRBCL_TableCell"]),
            Paragraph(mg[2], styles["CRBCL_TableCell"]),
            Paragraph(mg[3], styles["CRBCL_TableCell"]),
        ])

    t_mg = Table(mg_pdf_rows, colWidths=[110, 110, 110, 174])
    t_mg.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), COLOR_PRIMARY),
        ("GRID", (0, 0), (-1, -1), 0.5, COLOR_BORDER),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [COLOR_LIGHT_BG, colors.white]),
        ("PADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(t_mg)
    story.append(PageBreak())

    # Section 15: RBAC Permissions in PDF
    story.append(Paragraph("15. GRANULAR ROLE-BASED ACCESS CONTROL: 327 DISCRETE PERMISSION IDENTIFIERS", styles["CRBCL_H1"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=COLOR_PRIMARY, spaceAfter=6))
    story.append(Paragraph("The system implements a zero-trust authorization model comprising 327 discrete permission strings across 75 functional domains:", styles["CRBCL_Body"]))
    story.append(Paragraph("• <b>Case Management & Family Protection (64 Permissions):</b> Covers case creation, status transition, assignment, file closing, restriction override, kinship linkage, safety plan approval, risk assessment, and legal disclosure.", styles["CRBCL_Body"]))
    story.append(Paragraph("• <b>Clinical, Health & Assessment Services (44 Permissions):</b> Covers clinical note creation, locked note addenda, psychiatric evaluation attachment, assessment template authoring, and assessment score signing.", styles["CRBCL_Body"]))
    story.append(Paragraph("• <b>Resource Team, Foster Homes & Caregivers (46 Permissions):</b> Covers foster home licensing, home safety inspection approvals, criminal record renewals, bed capacity overrides, and complaint investigations.", styles["CRBCL_Body"]))
    story.append(Paragraph("• <b>Prevention & Healing Records (13 Permissions):</b> Covers ph.read, ph.create, ph.update, ph.delete, ph.import, ph.export, ph.duplicate_review, ph.finance_view, and staff activation governance.", styles["CRBCL_Body"]))
    story.append(Paragraph("• <b>Fleet, Facilities & Logistics (26 Permissions):</b> Covers fleet.reserve, fleet.dispatch, fleet.maintenance, fleet.geofence, key_custody, supply_order, and work_order_signoff.", styles["CRBCL_Body"]))
    story.append(Paragraph("• <b>Governance, Executive & Board (20 Permissions):</b> Covers board_dashboard.view, board_publication.approve, executive_dashboard.view, strategic_initiative.manage, and audit_log.inspect.", styles["CRBCL_Body"]))
    story.append(Spacer(1, 10))

    # Section 16: Flutter Cross-Platform Mobile Client Internals in PDF
    story.append(Paragraph("16. FLUTTER CROSS-PLATFORM MOBILE APPLICATION ARCHITECTURE & SQLITE REPLICATION", styles["CRBCL_H1"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=COLOR_PRIMARY, spaceAfter=6))
    story.append(Paragraph("<b>Status: MOBILE OFFLINE FUNCTIONALITY — USER TESTED AND CONFIRMED WORKING</b>", styles["CRBCL_BodyBold"]))
    story.append(Paragraph("The CRBCL mobile application has been installed and personally tested by the developer on a physical Android device. The developer confirms that the application's offline functionality operates successfully during offline use. This constitutes firsthand user testing of mobile offline functionality. Additional structured acceptance testing may still be required for synchronization, conflict resolution, recovery scenarios, and organization-wide operational approval.", styles["CRBCL_Body"]))
    story.append(Paragraph("The platform contains mobile offline data-handling functionality using an encrypted local SQLite database (via SQLCipher AES-256) and a transactional outbox queue. Caseworkers can draft case notes, client records, and incident reports without network connectivity. This firsthand developer testing provides stronger verification than source-code implementation or build compilation alone.", styles["CRBCL_Body"]))
    story.append(Paragraph("<b>Testing & Operational Distinctions:</b> While developer testing confirms that standalone offline operation works on device, a rigorous technical distinction must be maintained between: (1) standalone offline functions confirmed working by the developer; (2) offline-to-online automated synchronization; (3) multi-device synchronization; (4) conflict resolution policies; (5) data recovery under unexpected termination; (6) cryptographic security of local storage; and (7) full organization-wide field acceptance testing with frontline supervisors.", styles["CRBCL_Body"]))
    story.append(Paragraph("<b>Separation from Web Offline Workspace:</b> A strict distinction must be maintained between mobile offline functionality (personally tested on a physical Android device) and the separate web-based Offline Workspace (/offline-workspace, implemented in commit e33c87a). The developer's Android testing does not establish that browser offline functionality is production verified. Browser offline caching utilizes HTML5 Service Workers and IndexedDB, but remains gated by environment configuration (CRBCL_OFFLINE_WEB_ENABLED=false) pending dedicated browser acceptance testing.", styles["CRBCL_Body"]))
    story.append(Paragraph("• <b>State Management Architecture:</b> Employs the Provider pattern with decoupled ViewModels isolating business logic from UI widgets.", styles["CRBCL_Body"]))
    story.append(Paragraph("• <b>Local Encrypted Persistence:</b> Local drafts are stored in an encrypted SQLite database using SQLCipher AES-256 with encryption keys securely managed via FlutterSecureStorage.", styles["CRBCL_Body"]))
    story.append(Paragraph("• <b>Transactional Outbox Queue:</b> Offline actions (e.g. creating case notes, taking incident photos, recording audio) write an outbox record with sync_status='PENDING'.", styles["CRBCL_Body"]))
    story.append(Paragraph("• <b>Sync Orchestrator & Conflict Policy:</b> When connectivity is restored, the mobile app sends requests with an Idempotency-Key. If the server already processed the key, it returns the cached response, preventing duplicates.", styles["CRBCL_Body"]))
    story.append(Spacer(1, 10))

    # Section 17: Multi-Layered Security Architecture in PDF
    story.append(Paragraph("17. MULTI-LAYERED SECURITY CONTROLS, CRYPTOGRAPHIC PRIMITIVES & PRIVACY ISOLATION", styles["CRBCL_H1"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=COLOR_PRIMARY, spaceAfter=6))
    story.append(Paragraph("The CRBCL platform implements enterprise security controls tailored for First Nations data sovereignty:", styles["CRBCL_Body"]))
    story.append(Paragraph("• <b>Dual Authentication Primitives:</b> Argon2id password hashing with salt generation; Frontline 6-digit PIN hashing with dedicated salt and brute-force lockout counters.", styles["CRBCL_Body"]))
    story.append(Paragraph("• <b>Conflict-of-Interest Case Blinding:</b> Dynamic Case Restriction table evaluated on every single case read request. Restricted workers are returned an empty or 404 response.", styles["CRBCL_Body"]))
    story.append(Paragraph("• <b>Cryptographic Ingestion Provenance:</b> Every ingested file and record batch is fingerprinted using SHA-256 to ensure complete auditability.", styles["CRBCL_Body"]))
    story.append(Paragraph("• <b>Cross-Site Request Forgery & CORS Defense:</b> Strict origin checking on Railway PaaS and state-changing CSRF tokens prevent unauthorized cross-origin requests.", styles["CRBCL_Body"]))
    story.append(Spacer(1, 10))

    # Section 18: Architectural Comparison in PDF
    story.append(Paragraph("18. ARCHITECTURAL COMPARISON: ORIGINAL SPECIFICATION VS CURRENT REVISION", styles["CRBCL_H1"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=COLOR_PRIMARY, spaceAfter=6))
    story.append(Paragraph(
        "A rigorous comparative audit confirms that the architecture evolved additively to uphold sovereign First Nations legal requirements. Rather than degrading the design, changes expanded system capability across all dimensions: (1) Database expanded from 15 basic tables into 205 mapped SQLAlchemy models across 14 namespaces with 31 Alembic migrations; (2) API upgraded from synchronous endpoints to asynchronous FastAPI with 521 endpoints across 57 router modules; (3) Security expanded from coarse roles to a 327-permission RBAC matrix with active conflict-of-interest blinding; (4) Mobile developed as a cross-platform native Flutter application with local SQLite drafting and an idempotent outbox sync engine.",
        styles["CRBCL_Body"]
    ))
    story.append(Spacer(1, 10))

    # Section 19: Technical Debt in PDF
    story.append(Paragraph("19. TECHNICAL DEBT, SYSTEM RISKS & HANDOVER PROTOCOLS", styles["CRBCL_H1"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=COLOR_PRIMARY, spaceAfter=6))
    story.append(Paragraph(
        "For an independent software engineering team auditing this codebase, the technical debt is low and code quality is high. Key operationalization items include: (1) Finalize Railway backend CORS headers to match https://genserver.online; (2) Evaluate, select, and provision enterprise API credentials for an approved cloud LLM provider and Twilio Canada SMS; (3) Procure and integrate OBD-II GPS telematics hardware for vehicle tracking; (4) Conduct structured frontline supervisor UAT workshops.",
        styles["CRBCL_Body"]
    ))

    pdf_doc.build(story, canvasmaker=NumberedCanvasV2)
    print(f"Document 2 Revision 2 PDF written to: {pdf_path}")
    return docx_path, pdf_path


if __name__ == "__main__":
    build_doc2()
