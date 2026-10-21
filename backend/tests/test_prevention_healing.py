"""Prevention & Healing Records Workspace test suite.

Covers:
  - Enhancement Programs CRUD & decimal expense calculations
  - Family Support Services CRUD & legacy RedMane ID handling
  - Other Nations Support CRUD
  - Inactive Staff Onboarding workflow (pending -> verified email -> activated & historical linking)
  - Canonical Client linking & reconciliation queue (10-digit Person ID)
  - Safe Excel Import Wizard (Analyze -> Preview -> Approval -> Execution)
  - Annual Summary reporting & financial aggregations
  - Role-based security & IT Admin boundary enforcement
"""

from __future__ import annotations

import io
import uuid
from datetime import date
from decimal import Decimal

import openpyxl
import pytest
from httpx import AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import get_settings
from app.models.case_note import CaseNote
from app.models.org_ops import Employee
from app.models.person import Person
from app.models.prevention_healing import (
    EnhancementProgram,
    FamilySupportRecord,
    OtherNationsSupport,
    PHClientRef,
    PHImportBatch,
    PHImportRow,
    PendingStaffProfile,
)


@pytest.mark.asyncio
async def test_enhancement_program_crud_and_expense_totals(
    client: AsyncClient, executive_director_user, db_session: AsyncSession
):
    headers = executive_director_user["headers"]

    payload = {
        "program": "Family Wellness & Culture",
        "program_activity": "Beading & Traditional Parenting Workshop",
        "record_date": "2026-05-15",
        "date_provided": "2026-05-15",
        "city": "Regina",
        "province": "SK",
        "partners": "Cowessess Knowledge Keepers",
        "families_in_province": 12,
        "families_out_of_province": 2,
        "participants_children_0_12": 15,
        "participants_youth_13_17": 8,
        "participants_post_majority_18_26": 4,
        "participants_parents_caregivers": 14,
        "participants_family_members": 6,
        "participants_others": 2,
        "account_code": "41000",
        "subcode": "213",
        "expense_gift_card": "250.00",
        "expense_purchase_order": "500.00",
        "expense_eft": "150.00",
        "expense_cheque": "0.00",
        "expense_credit_card": "125.50",
        "expense_courtesy_card": "0.00",
        "comments": "High engagement, traditional teachings well received.",
        "fiscal_year": "2026-2027",
    }

    # 1. Create
    res = await client.post("/api/v1/ph/enhancement-programs", json=payload, headers=headers)
    assert res.status_code == 201, res.text
    data = res.json()
    rec_id = data["id"]
    assert data["total_families"] == 14  # 12 + 2
    assert data["total_participants"] == 49  # 15 + 8 + 4 + 14 + 6 + 2
    assert data["total_cost"] == 1025.50  # 250 + 500 + 150 + 125.50

    # 2. Get
    get_res = await client.get(f"/api/v1/ph/enhancement-programs/{rec_id}", headers=headers)
    assert get_res.status_code == 200
    assert get_res.json()["program"] == "Family Wellness & Culture"

    # 3. List
    list_res = await client.get("/api/v1/ph/enhancement-programs?fiscal_year=2026-2027", headers=headers)
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 1

    # 4. Update
    payload["program_activity"] = "Updated Traditional Parenting Workshop"
    up_res = await client.put(f"/api/v1/ph/enhancement-programs/{rec_id}", json=payload, headers=headers)
    assert up_res.status_code == 200
    assert up_res.json()["program_activity"] == "Updated Traditional Parenting Workshop"

    # 5. Delete
    del_res = await client.delete(f"/api/v1/ph/enhancement-programs/{rec_id}", headers=headers)
    assert del_res.status_code == 204


@pytest.mark.asyncio
async def test_family_support_crud_and_redmane_id(
    client: AsyncClient, executive_director_user, db_session: AsyncSession
):
    headers = executive_director_user["headers"]

    payload = {
        "program": "Family Support Services",
        "support_type": "Emergency Food & Utility",
        "service_area": "Regina Urban",
        "record_date": "2026-06-10",
        "date_provided": "2026-06-10",
        "client_ref_legacy_id": "RM-99482",
        "city": "Regina",
        "province": "SK",
        "participants_children_0_12": 3,
        "participants_youth_13_17": 1,
        "participants_post_majority_18_26": 0,
        "participants_adults_18_plus": 2,
        "account_code": "41000",
        "subcode": "110",
        "project_code": "215",
        "expense_gift_card": "200.00",
        "expense_purchase_order": "350.00",
        "expense_eft": "0.00",
        "expense_cheque": "0.00",
        "expense_credit_card": "0.00",
        "expense_petty_cash": "50.00",
        "expense_courtesy_card": "0.00",
        "comments": "Groceries voucher and emergency power support.",
        "fiscal_year": "2026-2027",
    }

    # 1. Create
    res = await client.post("/api/v1/ph/family-support", json=payload, headers=headers)
    assert res.status_code == 201, res.text
    data = res.json()
    rec_id = data["id"]
    assert data["client_ref_legacy_id"] == "RM-99482"
    assert data["total_cost"] == 600.00  # 200 + 350 + 50
    assert data["client_match_status"] == "UNRESOLVED"

    # 2. List
    list_res = await client.get("/api/v1/ph/family-support?fiscal_year=2026-2027", headers=headers)
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 1

    # 3. Delete
    del_res = await client.delete(f"/api/v1/ph/family-support/{rec_id}", headers=headers)
    assert del_res.status_code == 204


@pytest.mark.asyncio
async def test_other_nations_support_crud(
    client: AsyncClient, executive_director_user, db_session: AsyncSession
):
    headers = executive_director_user["headers"]

    payload = {
        "worker_name_raw": "Tammy Breen",
        "record_date": "2026-07-27",
        "family_reference_raw": "Delorme Family",
        "service_type": "Utility Arrears",
        "cost": "2812.82",
        "on_reserve": False,
        "cowessess_connection": "Married to band member",
        "other_community": "Zagimay",
        "historical_reference_number": "3640201301",
        "comments": "Off reserve support coordination.",
        "fiscal_year": "2026-2027",
    }

    # 1. Create
    res = await client.post("/api/v1/ph/other-nations", json=payload, headers=headers)
    assert res.status_code == 201, res.text
    data = res.json()
    rec_id = data["id"]
    assert data["worker_name_raw"] == "Tammy Breen"
    assert data["cost"] == 2812.82
    assert data["on_reserve"] is False

    # 2. Get
    get_res = await client.get(f"/api/v1/ph/other-nations/{rec_id}", headers=headers)
    assert get_res.status_code == 200
    assert get_res.json()["other_community"] == "Zagimay"

    # 3. Update
    payload["comments"] = "Updated confirmation received from band administration."
    up_res = await client.put(f"/api/v1/ph/other-nations/{rec_id}", json=payload, headers=headers)
    assert up_res.status_code == 200
    assert up_res.json()["comments"] == "Updated confirmation received from band administration."


@pytest.mark.asyncio
async def test_staff_onboarding_inactive_and_activation_workflow(
    client: AsyncClient, executive_director_user, db_session: AsyncSession
):
    """Verifies:

    - Pending profile is created without email
    - Profile remains PENDING and cannot be activated without verified email
    - Providing verified email and activating creates an active Employee profile
    - Historical records referencing pending staff profile are automatically linked to Employee
    """
    headers = executive_director_user["headers"]

    # 1. Create pending staff profile from Excel without email
    staff_payload = {
        "first_name": "Valerie",
        "last_name": "Standingready",
        "display_name_from_excel": "Valerie Standingready",
        "position": "Prevention Worker",
        "department": "Prevention & Healing",
        "email": None,
        "phone": "306-555-0199",
        "notes": "Identified in historical 2026 Prevention tracker",
        "onboarding_status": "PENDING",
    }
    create_res = await client.post("/api/v1/ph/pending-staff", json=staff_payload, headers=headers)
    assert create_res.status_code == 201
    staff_data = create_res.json()
    profile_id = staff_data["id"]
    assert staff_data["onboarding_status"] == "PENDING"
    assert staff_data["employee_id"] is None

    # 2. Create historical EnhancementProgram referencing this pending staff profile
    ep = EnhancementProgram(
        pending_staff_id=uuid.UUID(profile_id),
        employee_name_raw="Valerie Standingready",
        program="Youth Cultural Camp",
        record_date=date(2026, 6, 1),
        fiscal_year="2026-2027",
    )
    db_session.add(ep)
    await db_session.commit()
    await db_session.refresh(ep)
    assert ep.employee_id is None

    # 3. Attempt to activate WITHOUT email -> must fail with 400
    fail_act = await client.post(f"/api/v1/ph/pending-staff/{profile_id}/activate", json={}, headers=headers)
    assert fail_act.status_code == 400
    assert "email" in fail_act.text.lower()

    # 4. Verify & Link WITH verified email (Creates Employee profile, links historical records, but DOES NOT create login account)
    act_res = await client.post(
        f"/api/v1/ph/pending-staff/{profile_id}/verify-and-link",
        json={"email": "valerie.standingready@crbcl.ca", "position": "Prevention Worker"},
        headers=headers,
    )
    assert act_res.status_code == 200
    verified_data = act_res.json()
    assert verified_data["onboarding_status"] == "VERIFIED_PENDING_ACCOUNT"
    assert verified_data["employee_id"] is not None
    assert verified_data["has_login_account"] is False
    assert verified_data["can_authenticate"] is False

    # 5. Verify Employee record was created in employees table
    emp_res = await db_session.execute(select(Employee).where(Employee.email == "valerie.standingready@crbcl.ca"))
    emp = emp_res.scalars().first()
    assert emp is not None
    assert emp.first_name == "Valerie"
    assert emp.last_name == "Standingready"
    assert emp.department == "Prevention & Healing"

    # 6. Verify historical EnhancementProgram now links to new Employee
    await db_session.refresh(ep)
    assert ep.employee_id == emp.id

    # 7. CRITICAL SECURITY CHECK: Verify that verified employee CANNOT authenticate / log in
    login_attempt = await client.post(
        "/api/v1/auth/login",
        json={"email": "valerie.standingready@crbcl.ca", "password": "RandomPassword123!"},
    )
    assert login_attempt.status_code == 401
    assert "invalid" in login_attempt.text.lower()

    # 8. Rollout Control Test: Account Activation is DISABLED by default
    settings = get_settings()
    assert settings.crbcl_ph_staff_activation_enabled is False

    refused_act = await client.post(
        f"/api/v1/ph/pending-staff/{profile_id}/activate-account",
        json={"password": "VerifiedPassword2026!"},
        headers=headers,
    )
    assert refused_act.status_code == 403
    assert "disabled by administrative policy" in refused_act.text.lower()

    # 9. Temporarily enable rollout control for authorized activation testing
    settings.crbcl_ph_staff_activation_enabled = True
    try:
        acc_act = await client.post(
            f"/api/v1/ph/pending-staff/{profile_id}/activate-account",
            json={"password": "VerifiedPassword2026!"},
            headers=headers,
        )
        assert acc_act.status_code == 200
        acc_data = acc_act.json()
        assert acc_data["onboarding_status"] == "ACCOUNT_ACTIVATED"
        assert acc_data["has_login_account"] is True
        assert acc_data["can_authenticate"] is True

        # 10. Now employee CAN authenticate with their provisioned credentials
        login_success = await client.post(
            "/api/v1/auth/login",
            json={"email": "valerie.standingready@crbcl.ca", "password": "VerifiedPassword2026!"},
        )
        assert login_success.status_code == 200
        assert "user" in login_success.json()
    finally:
        settings.crbcl_ph_staff_activation_enabled = False


@pytest.mark.asyncio
async def test_client_reconciliation_linking(
    client: AsyncClient, executive_director_user, db_session: AsyncSession
):
    """Verifies:

    - Legacy RedMane ID is registered in reconciliation queue
    - Confirming matches to canonical 10-digit Person ID
    - Rejecting updates status to REJECTED
    """
    headers = executive_director_user["headers"]

    # Create a canonical Person with 10-digit person_id_number
    person = Person(
        person_id_number="1234567890",
        first_name="George",
        last_name="Pelletier",
    )
    db_session.add(person)
    await db_session.commit()
    await db_session.refresh(person)

    # Register legacy client ref
    cref = PHClientRef(
        legacy_id="RM-88219",
        legacy_id_type="REDMANE",
        status="UNRESOLVED",
    )
    db_session.add(cref)
    await db_session.commit()
    await db_session.refresh(cref)
    cref_id = str(cref.id)

    # 1. Search canonical persons
    search_res = await client.get("/api/v1/ph/persons/search?q=George", headers=headers)
    assert search_res.status_code == 200
    search_data = search_res.json()
    assert len(search_data) >= 1
    assert any(p["person_id_number"] == "1234567890" for p in search_data)

    # Also search by 10-digit number
    num_search = await client.get("/api/v1/ph/persons/search?q=1234567890", headers=headers)
    assert num_search.status_code == 200
    assert len(num_search.json()) == 1

    # Create a FamilySupportRecord referencing legacy ID RM-88219
    fsr = FamilySupportRecord(
        program="Family Support",
        client_ref_legacy_id="RM-88219",
        client_match_status="UNRESOLVED",
        fiscal_year="2026-2027",
    )
    db_session.add(fsr)
    await db_session.commit()
    await db_session.refresh(fsr)
    assert fsr.person_id is None
    assert fsr.client_match_status == "UNRESOLVED"

    # 2. List unresolved client refs
    list_res = await client.get("/api/v1/ph/client-refs?status=UNRESOLVED", headers=headers)
    assert list_res.status_code == 200
    assert any(r["id"] == cref_id for r in list_res.json())

    # 3. Confirm link to canonical Person via reconcile endpoint
    confirm_res = await client.post(
        f"/api/v1/ph/client-refs/{cref_id}/reconcile",
        json={"action": "CONFIRM", "person_id": str(person.id)},
        headers=headers,
    )
    assert confirm_res.status_code == 200
    assert confirm_res.json()["status"] == "CONFIRMED"
    assert confirm_res.json()["person_id"] == str(person.id)
    assert confirm_res.json()["person_id_number"] == "1234567890"

    # Verify FamilySupportRecord was updated with the canonical Person link
    await db_session.refresh(fsr)
    assert fsr.person_id == person.id
    assert fsr.client_match_status == "CONFIRMED"

    # 4. Negative Test: Idempotent re-confirmation (same person) returns 200 OK
    idem_res = await client.post(
        f"/api/v1/ph/client-refs/{cref_id}/reconcile",
        json={"action": "CONFIRM", "person_id": str(person.id)},
        headers=headers,
    )
    assert idem_res.status_code == 200
    assert idem_res.json()["status"] == "CONFIRMED"

    # 5. Negative Test: Conflicting re-confirmation (different person) returns 409 Conflict
    person2 = Person(person_id_number="9876543210", first_name="Jane", last_name="Pelletier")
    db_session.add(person2)
    await db_session.commit()
    await db_session.refresh(person2)

    conflict_res = await client.post(
        f"/api/v1/ph/client-refs/{cref_id}/reconcile",
        json={"action": "CONFIRM", "person_id": str(person2.id)},
        headers=headers,
    )
    assert conflict_res.status_code == 409
    assert "already confirmed" in conflict_res.text.lower()

    # 6. Negative Test: Nonexistent Person ID returns 404 Not Found
    cref_missing = PHClientRef(legacy_id="RM-MISSING", legacy_id_type="REDMANE", status="UNRESOLVED")
    db_session.add(cref_missing)
    await db_session.commit()
    await db_session.refresh(cref_missing)

    missing_res = await client.post(
        f"/api/v1/ph/client-refs/{cref_missing.id}/reconcile",
        json={"action": "CONFIRM", "person_id": str(uuid.uuid4())},
        headers=headers,
    )
    assert missing_res.status_code == 404

    # 7. Negative Test: Person without valid 10-digit ID returns 400 Bad Request
    invalid_person = Person(person_id_number="12345", first_name="Invalid", last_name="Digits")
    db_session.add(invalid_person)
    await db_session.commit()
    await db_session.refresh(invalid_person)

    invalid_res = await client.post(
        f"/api/v1/ph/client-refs/{cref_missing.id}/reconcile",
        json={"action": "CONFIRM", "person_id": str(invalid_person.id)},
        headers=headers,
    )
    assert invalid_res.status_code == 400
    assert "10 numeric digits" in invalid_res.text or "10-digit" in invalid_res.text

    # 8. Negative Test: Conflicting link in FamilySupportRecord returns 409 Conflict
    cref_col = PHClientRef(legacy_id="RM-COLLISION", legacy_id_type="REDMANE", status="UNRESOLVED")
    db_session.add(cref_col)
    fsr_col = FamilySupportRecord(
        program="Family Support",
        client_ref_legacy_id="RM-COLLISION",
        person_id=person2.id,
        client_match_status="CONFIRMED",
        fiscal_year="2026-2027",
    )
    db_session.add(fsr_col)
    await db_session.commit()
    await db_session.refresh(cref_col)

    col_res = await client.post(
        f"/api/v1/ph/client-refs/{cref_col.id}/reconcile",
        json={"action": "CONFIRM", "person_id": str(person.id)},
        headers=headers,
    )
    assert col_res.status_code == 409
    assert "conflict" in col_res.text.lower()

    # 9. Reject a different client ref via reconcile endpoint
    cref2 = PHClientRef(legacy_id="RM-INVALID", legacy_id_type="REDMANE", status="UNRESOLVED")
    db_session.add(cref2)
    await db_session.commit()
    await db_session.refresh(cref2)

    rej_res = await client.post(
        f"/api/v1/ph/client-refs/{cref2.id}/reconcile",
        json={"action": "REJECT"},
        headers=headers,
    )
    assert rej_res.status_code == 200
    assert rej_res.json()["status"] == "REJECTED"


@pytest.mark.asyncio
async def test_excel_import_wizard_analyze_approve_execute(
    client: AsyncClient, executive_director_user, db_session: AsyncSession
):
    """End-to-end test of the 8-step Excel Import Wizard using synthetic data:

    1. Generate synthetic workbook in memory with Enhancement Programs headers
    2. Upload to /ph/import/analyze (Step 2 & 3: Validate & preview)
    3. Verify execution blocked by default rollout control (CRBCL_PH_REAL_IMPORT_ENABLED=False)
    4. Temporarily enable rollout control and test approval & execution
    5. Verify records imported into database
    6. Verify duplicate workbook upload is rejected with 400 Bad Request
    7. Verify import batch cancellation cascades CANCELLED status to staged rows
    """
    headers = executive_director_user["headers"]

    # 1. Create synthetic workbook in memory
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Enhancement Programs"

    # Set up row 7 headers matching real tracker
    headers_row = [
        "", "Date\n(dd-Mon-yy)", "Employee Name", "Employee Position", "Program", "Program Activity",
        "Date Provided\n(dd-Mon-yy)", "City\n(e.g. Regina)", "Province\n(e.g. SK)", "Partners/Collaborators",
        "Closing Date", "In Province Families", "Out of Province Families", "Total Families", "Prev",
        "Children \n0-12", "Youth\n13-17", "Post Majority\n18-26", "Parents/Caregivers", "Family Members",
        "Others", "Total Participants", "Account", "Sub", "Gift Card", "Purchase Order", "EFT", "Cheque",
        "Credit Card", "Courtesy Card", "Total Cost", "Comments"
    ]
    for c_idx, h in enumerate(headers_row, 1):
        ws.cell(7, c_idx, h)

    # Add 2 synthetic rows (row 8 & row 9)
    # Row 8: Valid row
    ws.cell(8, 2, "2026-05-10")
    ws.cell(8, 3, "Synthetic Staff One")
    ws.cell(8, 4, "Facilitator")
    ws.cell(8, 5, "Youth Healing Circle")
    ws.cell(8, 6, "Cultural Workshop")
    ws.cell(8, 8, "Regina")
    ws.cell(8, 9, "SK")
    ws.cell(8, 12, 5)   # in province fam
    ws.cell(8, 13, 1)   # out of province fam
    ws.cell(8, 16, 6)   # children
    ws.cell(8, 17, 4)   # youth
    ws.cell(8, 23, "41000")
    ws.cell(8, 24, "213")
    ws.cell(8, 25, 100.00) # gift card
    ws.cell(8, 26, 200.00) # PO
    ws.cell(8, 31, 300.00) # total cost
    ws.cell(8, 32, "Synthetic test row 1")

    # Row 9: Valid row
    ws.cell(9, 2, "2026-05-12")
    ws.cell(9, 3, "Synthetic Staff Two")
    ws.cell(9, 4, "Counsellor")
    ws.cell(9, 5, "Parenting Wisdom")
    ws.cell(9, 8, "Saskatoon")
    ws.cell(9, 9, "SK")
    ws.cell(9, 12, 8)
    ws.cell(9, 16, 10)
    ws.cell(9, 23, "41000")
    ws.cell(9, 24, "215")
    ws.cell(9, 27, 450.00) # EFT
    ws.cell(9, 31, 450.00)
    ws.cell(9, 32, "Synthetic test row 2")

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)

    # 2. Upload to analyze endpoint
    files = {"file": ("synthetic_tracker.xlsx", buf.getvalue(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    analyze_res = await client.post("/api/v1/ph/import/analyze", files=files, headers=headers)
    assert analyze_res.status_code == 200, analyze_res.text
    analyze_data = analyze_res.json()

    batch_id = analyze_data["batch_id"]
    assert analyze_data["total_rows_analyzed"] == 2
    assert analyze_data["valid_rows"] == 2
    assert analyze_data["invalid_rows"] == 0
    assert analyze_data["ready_for_approval"] is True
    assert "Synthetic Staff One" in analyze_data["employee_matching_issues"]
    assert "Synthetic Staff Two" in analyze_data["employee_matching_issues"]

    # 3. Verify execution blocked by default rollout control
    settings = get_settings()
    assert settings.crbcl_ph_real_import_enabled is False

    exec_blocked = await client.post(f"/api/v1/ph/import/execute/{batch_id}", headers=headers)
    assert exec_blocked.status_code == 403
    assert "disabled by administrative policy" in exec_blocked.text.lower()

    # 4. Temporarily enable rollout control for authorized testing
    settings.crbcl_ph_real_import_enabled = True
    try:
        # Cannot execute before approval
        exec_fail = await client.post(f"/api/v1/ph/import/execute/{batch_id}", headers=headers)
        assert exec_fail.status_code == 400
        assert "APPROVED" in exec_fail.text

        # Approve batch
        appr_res = await client.post(f"/api/v1/ph/import/approve/{batch_id}", headers=headers)
        assert appr_res.status_code == 200
        assert appr_res.json()["status"] == "APPROVED"

        # Execute import
        exec_res = await client.post(f"/api/v1/ph/import/execute/{batch_id}", headers=headers)
        assert exec_res.status_code == 200
        exec_data = exec_res.json()
        assert exec_data["status"] == "COMPLETED"
        assert exec_data["imported_rows"] == 2
    finally:
        settings.crbcl_ph_real_import_enabled = False

    # 5. Verify records exist in EnhancementProgram table
    db_records = await db_session.execute(
        select(EnhancementProgram).where(EnhancementProgram.import_batch_id == uuid.UUID(batch_id))
    )
    records = db_records.scalars().all()
    assert len(records) == 2
    assert {r.program for r in records} == {"Youth Healing Circle", "Parenting Wisdom"}

    # 6. Test duplicate prevention: Uploading the exact same file returns 400 Bad Request
    dup_res = await client.post("/api/v1/ph/import/analyze", files=files, headers=headers)
    assert dup_res.status_code == 400
    assert "duplicate" in dup_res.text.lower() and "detected" in dup_res.text.lower()

    # 7. Test cancelling a newly analyzed distinct batch
    wb2 = openpyxl.Workbook()
    ws2 = wb2.active
    ws2.title = "Enhancement Programs"
    for c_idx, h in enumerate(headers_row, 1):
        ws2.cell(7, c_idx, h)
    ws2.cell(8, 2, "2026-06-15")
    ws2.cell(8, 3, "Distinct Staff Three")
    ws2.cell(8, 5, "Youth Workshop Distinct")
    ws2.cell(8, 31, 150.00)
    buf2 = io.BytesIO()
    wb2.save(buf2)
    buf2.seek(0)

    files2 = {"file": ("synthetic_tracker_2.xlsx", buf2.getvalue(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    analyze_res2 = await client.post("/api/v1/ph/import/analyze", files=files2, headers=headers)
    assert analyze_res2.status_code == 200
    batch_id2 = analyze_res2.json()["batch_id"]

    cancel_res = await client.post(f"/api/v1/ph/import/cancel/{batch_id2}", headers=headers)
    assert cancel_res.status_code == 200
    assert cancel_res.json()["status"] == "CANCELLED"

    # Verify staged rows in DB also have status CANCELLED
    staged_rows = await db_session.execute(
        select(PHImportRow).where(PHImportRow.batch_id == uuid.UUID(batch_id2))
    )
    rows_list = staged_rows.scalars().all()
    assert len(rows_list) >= 1
    for r in rows_list:
        assert r.status == "CANCELLED"


@pytest.mark.asyncio
async def test_annual_summary_reporting(
    client: AsyncClient, executive_director_user, db_session: AsyncSession
):
    """Verifies that the /ph/summary endpoint aggregates totals accurately across reporting streams."""
    headers = executive_director_user["headers"]

    # Seed one of each record
    ep = EnhancementProgram(
        program="Annual Culture Gathering",
        fiscal_year="2026-2027",
        families_in_province=10,
        families_out_of_province=2,
        participants_children_0_12=20,
        participants_youth_13_17=10,
        expense_gift_card=Decimal("500.00"),
        expense_purchase_order=Decimal("1000.00"),
    )
    fsr = FamilySupportRecord(
        program="Direct Family Support",
        fiscal_year="2026-2027",
        expense_gift_card=Decimal("300.00"),
        expense_cheque=Decimal("200.00"),
    )
    ons = OtherNationsSupport(
        service_type="Eagle Nest Lodging",
        fiscal_year="2026-2027",
        cost=Decimal("750.00"),
    )
    db_session.add_all([ep, fsr, ons])
    await db_session.commit()

    res = await client.get("/api/v1/ph/summary?fiscal_year=2026-2027", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["fiscal_year"] == "2026-2027"
    assert data["enhancement_programs"]["total_cost"] == 1500.00
    assert data["enhancement_programs"]["total_families"] == 12
    assert data["family_support"]["total_cost"] == 500.00
    assert data["other_nations_support"]["total_cost"] == 750.00
    assert data["combined_total_cost"] == 2750.00


@pytest.mark.asyncio
async def test_security_it_admin_boundary(
    client: AsyncClient, it_admin_user
):
    """IT Admin must NOT have clinical or Prevention & Healing record management access.

    Verifies the principle of least privilege & privacy boundaries.
    """
    headers = it_admin_user["headers"]

    # IT Admin attempting to read PH records
    res = await client.get("/api/v1/ph/enhancement-programs", headers=headers)
    assert res.status_code == 403

    # IT Admin attempting to execute import
    res2 = await client.post(f"/api/v1/ph/import/execute/{uuid.uuid4()}", headers=headers)
    assert res2.status_code == 403


@pytest.mark.asyncio
async def test_unauthorized_activation_and_reconciliation_attempts(
    client: AsyncClient, caseworker_user
):
    """Verifies that unauthorized caseworkers without PH admin permissions cannot verify, activate, reconcile, or approve."""
    headers = caseworker_user["headers"]
    fake_id = str(uuid.uuid4())

    # Caseworker cannot verify & link staff
    res_link = await client.post(f"/api/v1/ph/pending-staff/{fake_id}/verify-and-link", json={"email": "test@crbcl.ca"}, headers=headers)
    assert res_link.status_code == 403

    # Caseworker cannot activate account
    res_act = await client.post(f"/api/v1/ph/pending-staff/{fake_id}/activate-account", json={"password": "Pass123!"}, headers=headers)
    assert res_act.status_code == 403

    # Caseworker cannot reconcile client refs
    res_rec = await client.post(f"/api/v1/ph/client-refs/{fake_id}/reconcile", json={"action": "CONFIRM"}, headers=headers)
    assert res_rec.status_code == 403

    # Caseworker cannot approve import batches
    res_appr = await client.post(f"/api/v1/ph/import/approve/{fake_id}", headers=headers)
    assert res_appr.status_code == 403


@pytest.mark.asyncio
async def test_existing_test_users_unaffected(
    client: AsyncClient,
    caseworker_user,
    supervisor_user,
    it_admin_user,
    finance_user,
    executive_director_user,
):
    """Existing test accounts across all roles must remain completely intact, active, and able to authenticate."""
    for test_fixture in [caseworker_user, supervisor_user, it_admin_user, finance_user, executive_director_user]:
        user = test_fixture["user"]
        assert user.is_active is True
        login_res = await client.post(
            "/api/v1/auth/login",
            json={"email": user.email, "password": "password123"},
        )
        assert login_res.status_code == 200, f"Login failed for existing test user {user.email}"
        token_data = login_res.json()
        assert "access_token" in token_data
        assert token_data["user"]["email"] == user.email


@pytest.mark.asyncio
async def test_case_note_privacy_boundary(
    client: AsyncClient, executive_director_user, finance_user, db_session: AsyncSession
):
    """Verifies:
    1. Creating or modifying Prevention & Healing records never creates or modifies CaseNote entries.
    2. Finance users cannot access Case Note clinical narratives.
    """
    ed_headers = executive_director_user["headers"]
    fin_headers = finance_user["headers"]

    # Count initial case notes
    cn_initial = await db_session.execute(select(func.count(CaseNote.id)))
    initial_count = cn_initial.scalar_one()

    # Create FamilySupportRecord
    fsr_payload = {
        "program": "Family Support Services",
        "support_type": "Crisis Intervention",
        "service_area": "Regina Urban",
        "record_date": "2026-08-01",
        "city": "Regina",
        "province": "SK",
        "account_code": "41000",
        "expense_gift_card": "100.00",
        "comments": "Confidential family support interaction.",
        "fiscal_year": "2026-2027",
    }
    create_res = await client.post("/api/v1/ph/family-support", json=fsr_payload, headers=ed_headers)
    assert create_res.status_code == 201

    # Verify zero CaseNote records were added or altered
    cn_after = await db_session.execute(select(func.count(CaseNote.id)))
    assert cn_after.scalar_one() == initial_count

    # Finance user attempting to read case notes
    cn_attempt = await client.get(f"/api/v1/cases/{uuid.uuid4()}/notes", headers=fin_headers)
    assert cn_attempt.status_code in [403, 404]


@pytest.mark.asyncio
async def test_financial_decimal_accuracy_and_fiscal_years(
    client: AsyncClient, executive_director_user, db_session: AsyncSession
):
    """Verifies that monetary calculations maintain exact Decimal precision down to the cent,
    and fiscal year queries do not leak data across fiscal boundaries.
    """
    headers = executive_director_user["headers"]

    # Record in 2025-2026
    ep_prev = EnhancementProgram(
        program="Historical Gathering",
        fiscal_year="2025-2026",
        expense_gift_card=Decimal("123.45"),
        expense_purchase_order=Decimal("234.55"),  # Total = 358.00
    )
    # Record in 2026-2027
    ep_curr = EnhancementProgram(
        program="Current Gathering",
        fiscal_year="2026-2027",
        expense_gift_card=Decimal("111.11"),
        expense_purchase_order=Decimal("222.22"),
        expense_eft=Decimal("333.33"),  # Total = 666.66
    )
    db_session.add_all([ep_prev, ep_curr])
    await db_session.commit()

    # Query 2025-2026
    res_prev = await client.get("/api/v1/ph/summary?fiscal_year=2025-2026", headers=headers)
    assert res_prev.status_code == 200
    assert res_prev.json()["fiscal_year"] == "2025-2026"
    assert res_prev.json()["enhancement_programs"]["total_cost"] == 358.00

    # Query 2026-2027
    res_curr = await client.get("/api/v1/ph/summary?fiscal_year=2026-2027", headers=headers)
    assert res_curr.status_code == 200
    assert res_curr.json()["fiscal_year"] == "2026-2027"
    assert res_curr.json()["enhancement_programs"]["total_cost"] == 666.66
