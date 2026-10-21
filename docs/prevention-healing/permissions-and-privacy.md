# Prevention & Healing — Permissions, Security & Privacy Boundaries

**Department:** Prevention & Healing (Department Team 3) / Information Security & Compliance  
**Organization:** Chief Red Bear Children's Lodge (CRBCL)  
**Classification:** Information Security & Role-Based Access Control Specification  

---

## 1. Role-Based Access Control (RBAC) Permissions

Thirteen specialized permissions are defined in `app.permissions.constants.Permissions` to govern the Prevention & Healing Workspace:

| Permission Key | Display Name | Category | Scope & Authority |
|---|---|---|---|
| `ph.record.read` | Read Prevention & Healing Records | `prevention_healing` | View programs, family support, and other nations records |
| `ph.record.create` | Create Prevention & Healing Records | `prevention_healing` | Log new program activities and support disbursements |
| `ph.record.update` | Update Prevention & Healing Records | `prevention_healing` | Edit draft or operational details within permitted scope |
| `ph.record.delete` | Delete Prevention & Healing Records | `prevention_healing` | Delete erroneous uncommitted entries (restricted) |
| `ph.report.read` | Read Prevention & Healing Summary Reports | `prevention_healing` | View annual summary aggregations and KPI dashboards |
| `ph.report.export` | Export Prevention & Healing Reports | `prevention_healing` | Download Excel workbooks and print audited summaries |
| `ph.import.upload` | Upload & Analyze Workbooks | `prevention_healing` | Upload spreadsheets and initiate Step 1–6 analysis |
| `ph.import.approve` | Approve Import Batches | `prevention_healing` | Authorize validated batch for database ingestion (Step 7) |
| `ph.import.execute` | Execute Import Batches | `prevention_healing` | Trigger transaction execution (Step 8) |
| `ph.import.history.read` | View Import History | `prevention_healing` | Inspect batch ledgers and row-level audit logs |
| `ph.staff.onboard.read` | Read Pending Staff Profiles | `prevention_healing` | View quarantined staff names and onboarding statuses |
| `ph.staff.onboard.manage` | Manage Staff Onboarding & Activation | `prevention_healing` | Verify emails, promote profiles, link historical records |
| `ph.client.reconcile` | Reconcile Client References | `prevention_healing` | Search canonical Person directory and confirm links |

---

## 2. Role-Permission Matrix

| Role | `record.*` | `report.*` | `import.upload` | `import.approve` | `import.execute` | `staff.onboard` | `client.reconcile` |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Prevention Worker** | Read, Create, Update (own) | Read | Upload (Draft) | ❌ | ❌ | Read | ❌ |
| **Prevention Supervisor** | Full CRUD | Full | Yes | Yes | Yes | Read | Yes |
| **Executive Director / CEO** | Read | Full | ❌ | Yes | ❌ | Read | Read |
| **Finance Officer** | Read (Financials) | Full | ❌ | ❌ | ❌ | ❌ | ❌ |
| **HR / Admin Officer** | ❌ | ❌ | ❌ | ❌ | ❌ | Full Manage | ❌ |
| **IT Administrator** | ❌ (Narratives blocked) | Read | Yes | ❌ | ❌ | Read | ❌ |
| **Board Member** | Read (Aggregated only) | Read (Summary) | ❌ | ❌ | ❌ | ❌ | ❌ |

---

## 3. Privacy & Legislative Compliance

The workspace architecture adheres strictly to Saskatchewan provincial privacy legislation:
- **FOIP (Freedom of Information and Protection of Privacy Act):** Client names and legacy numbers are segregated from public operational reports.
- **LAFOIP (Local Authority Freedom of Information and Protection of Privacy Act):** First Nation operational data governance principles (OCAP: Ownership, Control, Access, Possession) are maintained. Historical files reside solely on secure servers.
- **HIPA (Health Information Protection Act):** Any health or mental wellness referrals captured in support descriptions are protected under restricted clinical role access.
- **Audit Logging:** Every administrative confirmation of an employee profile (`ph_pending_staff_profiles`), legacy client reconciliation (`ph_client_refs`), or batch execution (`ph_import_batches`) records the actor user ID and UTC timestamp.
