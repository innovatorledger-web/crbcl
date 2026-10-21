# Prevention & Healing — Financial Coding & Annual Summary Reporting

**Department:** Prevention & Healing (Department Team 3) / Finance  
**Organization:** Chief Red Bear Children's Lodge (CRBCL)  
**Classification:** Financial Systems Specification & Reporting Design  

---

## 1. Decimal-Safe Financial Architecture

To eliminate floating-point arithmetic errors and ensure absolute audit compliance:

> [!IMPORTANT]
> **Strict Decimal Precision:** All monetary amounts are stored as `Numeric(12, 2)` in PostgreSQL and parsed via Python's standard `decimal.Decimal`. Binary floating-point types (`float`) are strictly forbidden in persistence, calculations, and financial validation.

### Payment Instrument Columns:
Each operational stream tracks expenditure by approved payment instruments:
- `expense_gift_card`: Store gift card disbursements (e.g. grocery, retail).
- `expense_purchase_order`: Approved vendor purchase orders.
- `expense_eft`: Electronic funds transfers.
- `expense_cheque`: Issued accounts payable cheques.
- `expense_credit_card`: Corporate credit card purchases.
- `expense_petty_cash`: Direct operational cash vouchers.
- `expense_courtesy_card`: Client courtesy cards.

### Total Cost Computed Properties:
Total expenditure per record is calculated deterministically on the server:
```python
@property
def total_cost(self) -> Decimal:
    return (
        self.expense_gift_card
        + self.expense_purchase_order
        + self.expense_eft
        + self.expense_cheque
        + self.expense_credit_card
        + self.expense_petty_cash
        + self.expense_courtesy_card
    )
```

---

## 2. Multi-Dimensional Financial Coding

Prevention & Healing operations are classified across four financial dimensions aligned with the Chart of Accounts:

1. **Account Codes (`account_code`):**
   - `41000`: Federal Funding (Indigenous Services Canada / Jordan's Principle / Bill C-92)
   - `42000`: Provincial / Foundation Grant Allocations
2. **Department Codes (`dept`):**
   - `100`: Growing Up Well
   - `200`: Prevention & Healing
   - `300`: Family Preservation
3. **Subcodes (`subcode`):**
   - `Intervention`: Targeted crisis and family intervention activities
   - `Cultural`: Traditional ceremonies, lodge gatherings, beading circles
   - `Parenting`: Traditional parenting workshops, parenting capacity building
   - `Early Years`: Infant safety, early childhood developmental support
4. **Project Codes (`project_code`):**
   - `215I`: Eagle Nest Intensive Support
   - `215C`: Eagle Nest Community Engagement

---

## 3. Annual Summary Reconstruction

In the legacy spreadsheet, the `Annual Summary` worksheet calculates static macro sums from individual sheets. In the CRBCL platform, this is superseded by the real-time API endpoint:
`GET /api/v1/ph/summary?fiscal_year=2026-2027`

### Dynamic Database Aggregations:
The endpoint evaluates server-side SQL aggregate queries:
- **Enhancement Programs:** Total activities logged, total expenditure, total families served (in-province vs. out-of-province), and total participant demographic counts (children, youth, post-majority, caregivers, others).
- **Family Support Services:** Total direct support service events, total expenditure, breakdown by support type (Food, Utilities, Accommodations, Clothing, Daycare, etc.).
- **Other Nations Support:** Total off-reserve assistance events, total expenditure, breakdown by on-reserve vs. off-reserve location and community connection.
- **Combined Departmental Total:** Total consolidated investment for the selected fiscal period.
- **Operational Health Metrics:** Count of pending staff profiles needing verification, and count of unresolved client references requiring administrative match.

---

## 4. Preventing Duplicate Counting & Metrics Separation

> [!CAUTION]
> **Participant Counts vs. Unique Clients:** An individual child or family may attend multiple Enhancement workshops throughout the year. Demographic counts in Enhancement Programs represent **event participant counts**, NOT unique individuals.

- **Enhancement Programs:** Records aggregate attendance tallies.
- **Family Support Records:** Records specific service events.
- **Other Nations Support:** Tracked as a distinct operational stream unless CRBCL leadership formally directs combining it with Family Support in provincial reporting.
- **Unique Client Reporting:** Unique individual counts must be derived exclusively from confirmed canonical `Person` records via the reconciliation queue, never by summing spreadsheet attendance rows.

---

## 5. Export & Reconciliation Safeguards

- **Reconciliation Warnings:** The workspace flags any batch where individual payment instrument sums diverge from reported line totals.
- **Authorized Export:** Reports can be exported to Excel or printed via authorized browser layouts by users holding `Permissions.PH_REPORT_EXPORT`.
- **Finance Boundary:** Finance users holding `Permissions.PH_REPORT_READ` can view financial summaries and coding breakdowns, but are restricted from viewing confidential child protection narratives.
