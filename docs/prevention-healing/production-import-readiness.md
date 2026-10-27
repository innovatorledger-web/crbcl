# Prevention & Healing — Production Import Readiness & Governance Decisions

**Department:** Prevention & Healing (Department Team 3) / Executive Leadership  
**Organization:** Chief Red Bear Children's Lodge (CRBCL)  
**Classification:** Executive Governance & Operational Release Readiness Report  
**Phase:** Phase 3 Staging Verification, End-to-End Testing & Release Audit  

---
## 1. Readiness Status Dashboard

| Lifecycle Phase | Status | Verification & Evidence |
|---|:---:|---|
| **SOURCE IMPLEMENTED** | **COMPLETED** | All 7 models, Alembic migration 031 (with `file_hash` index), 13 RBAC permissions, backend router, frontend API client, full React workspace, Phase 5 3-tier duplicate engine, and supervisor review queue built and integrated. |
| **TESTED** | **COMPLETED** | 14/14 Prevention & Healing test suites PASSED (including 10 duplicate detection scenarios & seeder security). 29/29 platform regression suites PASSED (auth, case notes, person, finance, IT admin boundaries). Total: 43/43 tests passing (100%). |
| **BUILD VERIFIED** | **COMPLETED** | Frontend production build (`npm run build` / `vite build`) completed with 0 compilation errors or bundle warnings (3,077 modules built in 2m 15s). |
| **STAGING VERIFIED** | **VERIFIED (LOCAL ISOLATED UAT) / CLOUD BLOCKED** | Local isolated staging environment (`synthetic_uat.db`, uvicorn :8000, vite :5173) fully verified with synthetic dataset across Scenarios A through L. Cloud staging environment currently absent on Railway/Vercel; provisioning plan prepared. |
| **PRODUCTION DEPLOYED** | **NOT AUTHORIZED** | Source staged on branch `main`; deployment to Railway production environment held until CRBCL leadership approves release window. Production website (`https://genserver.online`) and backend strictly untouched. |
| **PRODUCTION MIGRATION** | **NOT AUTHORIZED** | Migration 031 verified as clean additive head, but not executed on production DB. Zero production database connections initiated. |
| **LIVE VERIFIED** | **PENDING STAGING PROMOTION** | Requires cloud staging provisioning, migration execution, and executive authorization before promotion to production. |
| **REAL HISTORICAL IMPORT** | **NOT AUTHORIZED / DISABLED** | Import execution gated behind `CRBCL_PH_REAL_IMPORT_ENABLED=false`. **Zero real historical client records have been imported into the production database.** |
| **REAL STAFF ACTIVATION** | **DISABLED** | Account activation gated behind `CRBCL_PH_STAFF_ACTIVATION_ENABLED=false`. Dormant profiles quarantined without login credentials. |

---

## 2. Phase 2 Security Hardening & Rollout Controls

To protect sensitive historical family data and prevent unauthorized account access before CRBCL launch, two server-side rollout controls have been introduced:

### Control 1: Inactive Staff Account Activation Gate
- **Setting:** `CRBCL_PH_STAFF_ACTIVATION_ENABLED=false` (in `app.core.config`).
- **Enforcement:**
  - `POST /api/v1/ph/pending-staff/{profile_id}/activate-account` strictly rejects with `HTTP 403 Forbidden` when disabled.
  - Zero active `User` accounts can be created through Prevention & Healing staff onboarding while disabled.
  - Verification of staff profiles (`POST /api/v1/ph/pending-staff/{profile_id}/verify-and-link`) continues functioning, creating canonical `Employee` profiles and linking historical records without granting login access.
  - UI displays an amber policy notice in the *Inactive Staff Onboarding* tab explaining that login account activation is administratively locked.
  - Existing test accounts (`admin@crbcl.ca`, `supervisor@crbcl.ca`, `worker@crbcl.ca`, `finance@crbcl.ca`) remain fully active and unaffected.

### Control 2: Historical Excel Import Execution Gate
- **Setting:** `CRBCL_PH_REAL_IMPORT_ENABLED=false` (in `app.core.config`).
- **Enforcement:**
  - `POST /api/v1/ph/import/execute/{batch_id}` strictly rejects with `HTTP 403 Forbidden` when disabled.
  - Workbook analysis, schema validation, row-level preview, and error inspection remain available for authorized staff.
  - Transactional persistence into operational tables (`EnhancementProgram`, `FamilySupportRecord`, `OtherNationsSupport`) is completely blocked.
  - UI displays a prominent security banner in Step 1 of the Import Wizard explaining that import execution is locked by policy.
  - Prevents accidental ingestion of historical client records into production.

---

## 3. Client Identity Reconciliation Safeguards

The platform mandates strict canonical Person identity resolution:

1. **Mandatory 10-Digit Numeric ID:**
   - Every confirmed Person match must possess a valid 10-digit numeric `person_id_number` (e.g., `1000000001`).
   - The reconcile endpoint (`POST /api/v1/ph/client-refs/{id}/reconcile`) validates that the target Person has a 10-digit numeric ID; non-compliant or missing numbers are rejected with `HTTP 400 Bad Request`.
2. **Idempotent Re-Confirmation:**
   - Submitting a confirmation for a reference that is already linked to the identical Person returns `HTTP 200 OK` safely without duplicating operations or mutating audit trails.
3. **Conflict Detection & Cross-Family Protection:**
   - If an administrator attempts to re-link an already confirmed reference to a *different* Person, the API rejects with `HTTP 409 Conflict`.
   - If any `FamilySupportRecord` with that legacy reference is already linked to a different canonical Person, the API detects the cross-family collision and rejects with `HTTP 409 Conflict` rather than silently overwriting historical links.
4. **Audit Traceability:**
   - Every reconciliation decision records `confirmed_by_id = current_user.id` and `confirmed_at = datetime.now(UTC)`.
   - Raw legacy identifiers (`RM-...`, Status numbers, family names) are permanently preserved in `ph_client_refs.legacy_id` and service record rows.

---

## 4. Excel Import Safety, 3-Tier Duplicate Engine & Cryptographic Idempotency

1. **Row-Level Source Provenance Tracking:**
   - Rather than rejecting an entire revised workbook due to file-level hash collisions, the Phase 5 engine tracks row-level provenance (`source_batch_id` + `source_row_index`) in `ph_import_rows`.
   - Only rows originating from previously `COMPLETED` batches are classified as `CONFIRMED_DUPLICATE`.
2. **3-Tier Duplicate Classification Model:**
   - Every imported row is evaluated against both historical source provenance and existing operational database records:
     - **`CONFIRMED_DUPLICATE`:** Originates from an already completed import batch with matching source provenance, or is an exact intra-sheet repetition. Automatically excluded from database insertion.
     - **`POSSIBLE_DUPLICATE`:** Matches an existing operational record on primary business dimensions (e.g. date + employee + support type + cost), but does NOT match previous source batch provenance. Because Prevention workers legitimately deliver multiple services on the same day (e.g., morning and afternoon food vouchers), these rows are flagged for supervisor review rather than silently discarded.
     - **`NEW_RECORD` / `VALID`:** No historical or operational duplicate found. Eligible for automated import execution.
3. **Authorized Duplicate Review Queue:**
   - Endpoint `GET /api/v1/ph/import/batches/{batch_id}/review-queue`: Lists all staged rows flagged as `POSSIBLE_DUPLICATE` or `CONFIRMED_DUPLICATE`.
   - Endpoint `POST /api/v1/ph/import/rows/{row_id}/review`: Requires `PH_IMPORT_APPROVE` (`ph.import.approve`). Allows authorized supervisors to adjudicate flagged rows:
     - **`CONFIRMED_SEPARATE`:** Confirms the row represents a legitimate distinct service delivered on the same day. Promoted to valid import status.
     - **`REJECTED_DUPLICATE`:** Confirms the row is a true duplicate. Excluded from execution.
4. **Execution Idempotency & Retry Safety:**
   - If `POST /api/v1/ph/import/execute/{batch_id}` is re-invoked or retried after network interruption, the batch checks `imported_record_id is not None` and `status == "IMPORTED"`. Already imported rows are safely skipped, guaranteeing zero duplicate record creation.
5. **Batch Cancellation Cascades:**
   - When an unexecuted import batch is cancelled via `DELETE /api/v1/ph/import/cancel/{batch_id}` or `POST /api/v1/ph/import/cancel/{batch_id}`, the batch status is updated to `CANCELLED` and all staged rows in `ph_import_rows` are atomically dismissed with zero operational records created.
6. **Decimal-Safe Financial Processing:**
   - All monetary figures (gift cards, purchase orders, EFT, cheques, credit cards, courtesy cards) are parsed using Python `Decimal` and persisted in PostgreSQL `NUMERIC(12, 2)` columns, completely preventing IEEE 754 floating-point rounding errors.

---

## 5. Case Note Privacy Boundary

- **Narrative Segregation:** Prevention & Healing service records (`EnhancementProgram`, `FamilySupportRecord`, `OtherNationsSupport`) are operational/financial records and remain strictly separate from clinical `CaseNote` narratives.
- **Zero Automatic Narrative Generation:** Creating or updating a Prevention & Healing record never creates, modifies, or accesses any `CaseNote` record.
- **Role Isolation:** Finance personnel granted `ph.report.read` and `ph.record.read` permissions have zero access to clinical Case Notes (`/api/v1/cases/{case_id}/notes` returns `HTTP 403 Forbidden`).
- **IT Admin Boundary:** IT Administrators have access to technical administration but are strictly forbidden from viewing clinical narratives or Prevention & Healing operational records (`HTTP 403 Forbidden`).

---

## 6. Staging Environment Blocker & Actionable Setup Plan

### Blocker Finding:
A comprehensive audit of repository deployment configurations (`railway.json`, `vercel.json`, and deployment guides) confirmed that **no dedicated staging cloud environment currently exists**. The platform currently has only:
- Local development/testing environment (`sqlite+aiosqlite` in-memory / local PostgreSQL).
- Production website: `https://genserver.online`.
- Production backend: `https://crbcl-production.up.railway.app`.

In compliance with instructions, **production was not used as a staging substitute**, and staging verification is reported as **BLOCKED (ENVIRONMENT ABSENT)** rather than falsely claimed.

### Actionable Staging Environment Setup Plan:
When authorized by CRBCL leadership, execute the following steps to establish a dedicated staging environment:

1. **Provision Staging Project on Railway:**
   - Create a new Railway environment named `staging` under the CRBCL team account.
   - Attach a staging PostgreSQL database service (`crbcl-staging-db`).
   - Attach a backend service tracking branch `main` with URL `crbcl-staging.up.railway.app`.
2. **Configure Staging Environment Variables:**
   - `APP_ENV=staging`
   - `DATABASE_URL=postgresql+asyncpg://...` (staging database connection string)
   - `CRBCL_PH_STAFF_ACTIVATION_ENABLED=false` (keep real account activation disabled)
   - `CRBCL_PH_REAL_IMPORT_ENABLED=true` (enable synthetic workbook import testing in staging only)
   - `SESSION_SECRET` (unique staging secret, distinct from production)
3. **Execute Additive Migration on Staging DB:**
   ```bash
   alembic upgrade head
   ```
   (Applies migration `031_prevention_healing.py` cleanly without touching production).
4. **Seed Staging Database with Synthetic Data:**
   - Run seed script with synthetic staff profiles, synthetic canonical Persons, and test cases.
   - Do NOT load real confidential historical spreadsheets into staging.
5. **Execute Staging Verification Protocol:**
   - Test login with authorized CRBCL staging accounts.
   - Test inactive staff verification with synthetic email.
   - Test client reconciliation with synthetic 10-digit Person records.
   - Upload and execute synthetic Excel import wizard end-to-end.
   - Verify Annual Summary aggregations match expected synthetic figures.
   - Validate RBAC permission boundaries for Caseworker, Finance, IT Admin, and Executive Director roles.
6. **Executive Signoff:**
   - Provide the Staging Verification Report to the Executive Director for final production rollout approval.

---

## 7. Five Outstanding CRBCL Governance Decisions

1. **Other Nations Support Reporting:** Should Other Nations Support remain a separate operational stream or roll up into Family Support for provincial grant reporting?
2. **Case Note Linkage:** Should high-acuity crisis support records optionally link to Case Notes, or remain strictly separate?
3. **Financial Coding Approval Authority:** Which authorized role holds sole authority to correct financial coding exceptions during import validation?
4. **Unresolved Historical Identities:** How should multi-person family entries (*"Lisa/Laurie Delorme"*) be categorized before operational launch?
5. **General Ledger Codes:** Validation of official Sage GL accounts, department codes, and project codes for 2026-2027.
