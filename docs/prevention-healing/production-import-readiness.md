# Prevention & Healing — Production Import Readiness & Governance Decisions

**Department:** Prevention & Healing (Department Team 3) / Executive Leadership  
**Organization:** Chief Red Bear Children's Lodge (CRBCL)  
**Classification:** Executive Governance & Operational Release Readiness Report  

---

## 1. Readiness Status Dashboard

| Lifecycle Phase | Status | Verification & Evidence |
|---|:---:|---|
| **SOURCE IMPLEMENTED** | **COMPLETED** | All 7 models, Alembic migration 031, 13 RBAC permissions, backend router, frontend API client, and full React workspace built and integrated. |
| **TESTED** | **COMPLETED** | 8/8 Prevention & Healing test suites PASSED. 15/15 core platform regression suites (auth, case notes, person, finance) PASSED. |
| **STAGING VERIFIED** | **READY** | Automated test suite verified locally; migration ready for execution in staging PostgreSQL database. |
| **PRODUCTION DEPLOYED** | **PENDING** | Code staged in repository; deployment to Railway/production environment pending scheduled release window. |
| **LIVE VERIFIED** | **PENDING** | Requires staging promotion and end-to-end smoke test on production domain (`genserver.online`). |
| **REAL HISTORICAL IMPORT** | **STRICTLY PENDING APPROVAL** | Import wizard built and verified with synthetic data. **Real historical client tracker files have NOT been imported into production database.** |

---

## 2. Five Outstanding CRBCL Governance Decisions

Before executing the historical Excel data import or enabling production workflows, the following five operational decisions must be formally resolved by CRBCL leadership:

### Decision 1: Other Nations Support Reporting Relationship
- **Context:** The Eagle Nest tracker (`Prevention Other Nations Tracking - Eagle Nest Oct 9 2026.xlsx`) documents off-reserve and non-Cowessess indigenous community members.
- **Question:** Should Other Nations Support remain a completely separate operational reporting stream, or should its totals also be rolled up into Family Support Services for provincial and federal grant reporting?
- **Current Architecture:** Implemented as a separate operational table (`ph_other_nations_support`) with configurable combined reporting in `/ph/summary`.

### Decision 2: Prevention Service Records & Case Note Linkage
- **Context:** Prevention services (groceries, utility support, hotel accommodations) sometimes assist families who also have an active Case in the child safety system.
- **Question:** Should Prevention & Healing service records optionally link to Case Notes, or should Case Notes be strictly mandatory for certain high-acuity crisis services?
- **Current Architecture:** Prevention & Healing service records remain completely separate from confidential Case Notes, protecting clinical narratives from Finance review. Optional linkage can be activated once CRBCL approves the workflow.

### Decision 3: Financial Coding Approval Authority
- **Context:** Excel records frequently contain legacy subcodes, non-standard project codes, or missing GL account numbers.
- **Question:** Which authorized CRBCL role (Prevention Supervisor, Finance Manager, or Executive Director) holds the authority to correct or approve financial coding exceptions during import validation?
- **Current Architecture:** Configured under `Permissions.PH_IMPORT_APPROVE` (`ph.import.approve`).

### Decision 4: Handling Unresolved Historical Identities
- **Context:** Several historical records list entire households (e.g., *"Lisa/Laurie Delorme"*) or obsolete RedMane numbers that cannot be matched to a canonical 10-digit Person ID.
- **Question:** How should unresolved historical family/client identities be handled before final operational launch? Should they be imported as quarantined household entries, or must every row be linked to a confirmed Person before ingestion?
- **Current Architecture:** Unresolved records are preserved in the reconciliation queue (`ph_client_refs`, status `UNRESOLVED`) with the raw string preserved, preventing duplicate client creation.

### Decision 5: Master Financial Coding Lists & Fiscal Year Cutoffs
- **Context:** The `CODING` worksheet lists account codes (41000, 42000), department codes (100, 200, 300), and project codes (215I).
- **Question:** What is the approved, authoritative list of active general ledger codes and fiscal year boundaries for 2026-2027 and future fiscal periods?
- **Current Architecture:** Handled via database configuration and filter parameters, ready for synchronization with CRBCL's Sage accounting system.

---

## 3. Production Launch & Data Migration Checklist

- [x] Schema models defined and reviewed.
- [x] Additive migration (`031_prevention_healing.py`) created.
- [x] Inactive staff onboarding lifecycle implemented and tested.
- [x] Person search and legacy ID reconciliation implemented and tested.
- [x] Decimal-safe financial calculations verified.
- [x] 8-step import wizard built with row error isolation and batch cancellation.
- [x] Confidential Case Notes kept segregated from financial operational logs.
- [x] Zero existing test accounts or test records deleted or modified.
- [x] Automated pytest and regression suites passed (100%).
- [ ] CRBCL Leadership approves the 5 Outstanding Governance Decisions.
- [ ] Staging deployment: Execute Alembic migration `031_prevention_healing.py` on staging DB.
- [ ] Authorized supervisor executes trial import of historical workbooks in staging environment.
- [ ] HR/Admin verifies and activates real Prevention & Healing staff profiles with verified corporate emails.
- [ ] Final signoff: CRBCL Executive Director authorizes live production import.
