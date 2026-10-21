# Prevention & Healing — Workbook Data Mapping Specification

**Department:** Prevention & Healing (Department Team 3)  
**Organization:** Chief Red Bear Children's Lodge (CRBCL)  
**Classification:** Operational Specification / Confidential  

---

## 1. Executive Summary & Workbook Inventory

CRBCL maintains historical Prevention & Healing operations across two primary Excel workbooks located on administrative storage:

1. **`CURRENT Prevention & Healing Tracker 2026-2027 Copy.xlsx`**
   - **Worksheets:**
     - `Instructions` (Usage guidelines and conventions)
     - `CODING` (Chart of Accounts, Department Codes, Subcodes, Project Codes)
     - `Enhancement Programs` (Community events, group workshops, cultural activities, demographic counts, expenditures)
     - `Family Support` (Direct family support services, emergency relief, legacy RedMane client references, expenditures)
     - `Annual Summary` (Consolidated operational expenditure summaries and program breakdowns)
     - `DATA (Dec-Mar)` (Lookup reference validation lists for dropdown menus)

2. **`Prevention Other Nations Tracking - Eagle Nest Oct 9 2026.xlsx`**
   - **Worksheets:**
     - `Sheet1` (Eagle Nest / Other Nations operational tracking for off-reserve and non-Cowessess indigenous community members)

3. **Case Note Example Workbook Status (Audited Absence):**
   - A comprehensive automated search across `C:\Users\Shilley Pc\Downloads`, `Desktop`, `Documents`, and the repository confirmed that **no separate Case Note example workbook exists on the local filesystem**.
   - Only the two workbooks above are present.
   - Case Note integration architecture and privacy safeguards were derived directly from the platform's canonical Case Note implementation (`backend/app/models/case_note.py`, `backend/app/api/v1/case_notes.py`) and prompt requirements.

---

## 2. Employee Email Address Finding (Crucial Verification)

> [!IMPORTANT]
> **Definitive Finding:** A 100% cell-level automated inspection of every worksheet across both Excel workbooks confirmed that **ZERO employee email addresses exist** in the historical tracking files.

### Specific Findings:
- **Employee Names Present:** Raw worker strings such as *"Brianne Coghill"*, *"Samantha Cyre"*, *"McKenna Francis"*, *"Ryan Desjarlais"*, *"Nikki Duquette"*, *"Tammy Breen"*, *"Shannon Lerat"*, *"Jewel Wendler"*, *"Kristy Agecoutay"*, *"Melissa Obey"*, *"Geovonie Sparvier"*, *"Alana Obey"*, *"Tracy McKenzie"*, *"Isiah Acoose"*, *"Shayla Wing"*, *"Tori McNabb"*.
- **Positions Present:** Historical role titles such as *"Early Years Coordinator"*, *"Miyo Mahcihowin"*, *"Eagle Nest Support Worker"*, *"Youth Coordinator"*, *"Household Wellness Coordinator"*, *"Preservation Supervisor"*.
- **Department/Program Context:** Prevention & Healing, Eagle Nest, Ohpikinawasowin.
- **Absent Fields:** 
  - NO employee email addresses.
  - NO work email addresses.
  - NO employee ID numbers / payroll numbers.
  - NO phone numbers or contact details.
  - NO unique employee system identifiers.

**Architectural Implication:** Under CRBCL platform security standards, user authentication requires a verified corporate email address and role assignment. Fake or default emails must never be created. Unverified staff identified from historical spreadsheets are placed into a pending onboarding state (`PendingStaffProfile`).
- **Profile Verification (`VERIFIED_PENDING_ACCOUNT`):** Verifies the staff member's work email and links or creates an `Employee` HR record. **Strictly DOES NOT create a login user account or permit authentication.**
- **Account Activation (`ACCOUNT_ACTIVATED`):** A separate explicit administrative action that provisions login credentials (`User` record) and enables platform authentication.

---

## 3. Worksheet Structure & Column Mapping

### A. Enhancement Programs (`Enhancement Programs` Sheet)

**Header Row:** Row 7 (Columns B through Y / 1 to 24)

| Excel Column | Header Name | Model Field (`EnhancementProgram`) | Data Type | Notes & Transformation |
|---|---|---|---|---|
| B (1) | `Date (dd-Mon-yy)` | `record_date` | `Date` | Date record was logged in spreadsheet |
| C (2) | `Employee Name` | `employee_name_raw` | `String(255)` | Preserved original string; mapped to `PendingStaffProfile` |
| D (3) | `Employee Position` | `position_raw` | `String(100)` | Historical position title |
| E (4) | `Program` | `program` | `String(200)` | Dropdown category (e.g. Ohpikinawasowin, Youth) |
| F (5) | `Program Activity` | `program_activity` | `String(500)` | Detailed activity description (e.g. CFN Spring Fair) |
| G (6) | `Date Provided (dd-Mon-yy)` | `date_provided` | `Date` | Service execution date |
| H (7) | `City (e.g. Regina)` | `city` | `String(100)` | Location municipality |
| I (8) | `Province (e.g. SK)` | `province` | `String(100)` | Province abbreviation |
| J (9) | `Partners/Collaborators` | `partners` | `Text` | Partner agencies / First Nation departments |
| K (10) | `Closing Date` | `closing_date` | `Date` | Activity completion date |
| L (11) | `Families In-Province` | `families_in_province` | `Integer` | Default: 0 |
| M (12) | `Families Out-of-Province`| `families_out_of_province`| `Integer` | Default: 0 |
| N (13) | `Total Families` | *Computed Property* | `Integer` | Calculated formula: `in_province + out_of_province` |
| P (15) | `Children 0-12` | `participants_children_0_12` | `Integer` | Demographic count |
| Q (16) | `Youth 13-17` | `participants_youth_13_17` | `Integer` | Demographic count |
| R (17) | `Post Majority 18-26` | `participants_post_majority_18_26`| `Integer` | Demographic count |
| S (18) | `Parents/Caregivers` | `participants_parents_caregivers` | `Integer` | Demographic count |
| T (19) | `Family Members` | `participants_family_members` | `Integer` | Demographic count |
| U (20) | `Others` | `participants_others` | `Integer` | Demographic count |
| V (21) | `Total Participants` | *Computed Property* | `Integer` | Calculated formula: sum of demographic counts |
| W (22) | `Account` | `account_code` | `String(50)` | Chart of accounts code (e.g., 41000) |
| X (23) | `Sub` | `subcode` | `String(50)` | Activity subcode (e.g., 213) |
| Y (24) | `Gift Card` | `expense_gift_card` | `Numeric(12,2)` | Decimal-safe payment tracking |
| Z (25) | `Purchase Order` | `expense_purchase_order` | `Numeric(12,2)` | Decimal-safe payment tracking |
| AA (26) | `EFT` | `expense_eft` | `Numeric(12,2)` | Decimal-safe payment tracking |
| AB (27) | `Cheque` | `expense_cheque` | `Numeric(12,2)` | Decimal-safe payment tracking |
| AC (28) | `Credit Card` | `expense_credit_card` | `Numeric(12,2)` | Decimal-safe payment tracking |
| AD (29) | `Courtesy Card` | `expense_courtesy_card` | `Numeric(12,2)` | Decimal-safe payment tracking |
| AE (30) | `Total Cost` | *Computed Property* | `Numeric(12,2)` | Calculated formula: sum of all payment methods |
| AF (31) | `Comments` | `comments` | `Text` | Non-confidential operational notes |

---

### B. Family Support Services (`Family Support` Sheet)

**Header Row:** Row 7 (Columns B through AB)

| Excel Column | Header Name | Model Field (`FamilySupportRecord`) | Data Type | Notes & Transformation |
|---|---|---|---|---|
| B (1) | `Date` | `record_date` | `Date` | Logging date |
| C (2) | `Employee Name` | `employee_name_raw` | `String(255)` | Worker name; linked to staff profile |
| D (3) | `Position` | `position_raw` | `String(100)` | Historical position |
| E (4) | `Service Area` | `service_area` | `String(100)` | e.g. Preservation, Growing Up Well |
| F (5) | `Program` | `program` | `String(200)` | Program stream (e.g. Eagle Nest) |
| G (6) | `Type` | `support_type` | `String(200)` | e.g. Food, Utilities, Accommodations |
| H (7) | `Description` | `description` | `Text` | Operational narrative |
| I (8) | `Partners/Collaborators`| `partners` | `Text` | Partner agencies |
| J (9) | `Date Provided` | `date_provided` | `Date` | Service date |
| K (10) | `RedMane ID#` | `client_ref_legacy_id` | `String(50)` | **Legacy client ID — Quarantined; not a canonical 10-digit Person ID** |
| L (11) | `City` | `city` | `String(100)` | Municipality |
| M (12) | `Province` | `province` | `String(100)` | Province |
| N (13) | `Children 0-12` | `participants_children_0_12` | `Integer` | Demographic count |
| O (14) | `Youth 13-17` | `participants_youth_13_17` | `Integer` | Demographic count |
| P (15) | `Post Majority 18-26` | `participants_post_majority_18_26`| `Integer` | Demographic count |
| Q (16) | `Adults 18+` | `participants_adults_18_plus` | `Integer` | Demographic count |
| R (17) | `Account` | `account_code` | `String(50)` | GL Account code |
| S (18) | `Sub` | `subcode` | `String(50)` | Subcode |
| T (19) | `Project Code` | `project_code` | `String(50)` | e.g. 215I |
| U (20) | `Gift Card` | `expense_gift_card` | `Numeric(12,2)` | Decimal-safe amount |
| V (21) | `Purchase Order` | `expense_purchase_order` | `Numeric(12,2)` | Decimal-safe amount |
| W (22) | `EFT` | `expense_eft` | `Numeric(12,2)` | Decimal-safe amount |
| X (23) | `Cheque` | `expense_cheque` | `Numeric(12,2)` | Decimal-safe amount |
| Y (24) | `Credit Card` | `expense_credit_card` | `Numeric(12,2)` | Decimal-safe amount |
| Z (25) | `Petty Cash` | `expense_petty_cash` | `Numeric(12,2)` | Decimal-safe amount |
| AA (26) | `Courtesy Card` | `expense_courtesy_card` | `Numeric(12,2)` | Decimal-safe amount |
| AB (27) | `Total Cost` | *Computed Property* | `Numeric(12,2)` | Sum of expense columns |
| AC (28) | `Comments` | `comments` | `Text` | Non-confidential notes |

---

### C. Other Nations Support (`Sheet1` of Eagle Nest Tracker)

**Header Row:** Row 3 (Columns A through K)

| Excel Column | Header Name | Model Field (`OtherNationsSupport`) | Data Type | Notes & Transformation |
|---|---|---|---|---|
| A (0) | `Date` | `record_date` | `Date` | Service date |
| B (1) | `Name of Worker` | `worker_name_raw` | `String(255)` | Worker name; linked to staff profile |
| C (2) | `Family Name` | `family_reference_raw` | `String(255)` | Historical family reference (quarantined) |
| D (3) | `Service Type` | `service_type` | `String(200)` | Food Support, Utility Arrears, Rent, etc. |
| E (4) | `Cost` | `cost` | `Numeric(12,2)` | Decimal-safe cost |
| F (5) | `Status #` | `historical_reference_number` | `String(100)` | Treaty/Status reference string |
| G (6) | `Cowessess Connection` | `cowessess_connection` | `String(200)` | Kinship/community connection text |
| H (7) | `Non-Cowessess Members`| `other_community` | `String(200)` | External First Nation or community name |
| I (8) | `On Reserve` | `on_reserve` | `Boolean` | True if "Yes", False if "No" |
| J (9) | `Off Reserve` | `comments` (appended) | `Text` | Location notes (e.g. Regina, Zagimay) |

---

## 4. Financial Coding Architecture (`CODING` Sheet)

The `CODING` sheet defines reference classifications for financial attribution:
- **Account Codes (acct):** Primary general ledger funding streams (e.g., `41000` Federal Funding, `42000` Provincial/Grant Funding).
- **Department Codes (dept):** Operational areas (e.g., `100` Growing Up Well, `200` Prevention & Healing, `300` Family Preservation).
- **Subcodes (sub):** Activity categorization (e.g., `Intervention`, `Cultural`, `Parenting`, `Early Years`).
- **Project Codes (Eagle Nest):** Designated initiative codes (e.g., `215I` Eagle Nest Intensive Support).

These lists serve as reference validation rules in the safe import wizard to flag unrecognized coding for supervisor review.
