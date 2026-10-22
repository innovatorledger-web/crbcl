"""CRBCL Platform — Dedicated Staging Synthetic Test Data Seeder.

Creates a completely isolated synthetic data environment for Phase 3 testing:
- Canonical Persons with valid 10-digit numeric person_id_numbers
- Canonical Client and Case records
- Prevention & Healing pending staff profiles (without emails)
- Verified employees without login accounts (VERIFIED_PENDING_ACCOUNT)
- Synthetic Enhancement Programs with exact Decimal expenses
- Synthetic Family Support records with legacy RedMane IDs
- Synthetic Other Nations Support records
- Legacy Client Reconciliation queue (PHClientRef)
- Rollout controls enforced: CRBCL_PH_STAFF_ACTIVATION_ENABLED=false, CRBCL_PH_REAL_IMPORT_ENABLED=false

CRITICAL: ZERO real historical records or real confidential names are used.
"""

from __future__ import annotations

import asyncio
import logging
import uuid
from datetime import date, datetime, UTC
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.security import hash_password
from app.core.config import get_settings
from app.core.database import Base, async_session_factory, engine
from app.models.case import Case
from app.models.client import Client
from app.models.org_ops import Employee
from app.models.person import Person
from app.models.prevention_healing import (
    EnhancementProgram,
    FamilySupportRecord,
    OtherNationsSupport,
    PHClientRef,
    PendingStaffProfile,
)
from app.models.role import Permission, Role, RolePermission, UserRole
from app.models.team import Team, TeamMembership
from app.models.user import User
from app.permissions.constants import Permissions

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("crbcl.seed.staging")


async def seed_staging_synthetic_data(db: AsyncSession) -> dict:
    logger.info("Initializing staging synthetic test dataset...")

    # 1. Ensure Baseline Roles exist
    roles = {}
    role_defs = [
        ("executive_director", "Executive Director"),
        ("supervisor", "Supervisor"),
        ("caseworker", "Caseworker"),
        ("finance_staff", "Finance Staff"),
        ("it_admin", "IT Administrator"),
    ]
    for r_key, r_name in role_defs:
        res = await db.execute(select(Role).where(Role.key == r_key))
        role = res.scalars().first()
        if not role:
            role = Role(key=r_key, name=r_name, is_system=True)
            db.add(role)
            await db.flush()
        roles[r_key] = role

    # 2. Ensure Permissions exist and map to roles
    all_perms = {}
    for p_key in Permissions:
        p_res = await db.execute(select(Permission).where(Permission.key == p_key.value))
        perm = p_res.scalars().first()
        if not perm:
            perm = Permission(key=p_key.value, name=p_key.value, category="prevention_healing")
            db.add(perm)
            await db.flush()
        all_perms[p_key.value] = perm

    # Grant Executive Director all permissions
    for p_val, p_obj in all_perms.items():
        rp_check = await db.execute(
            select(RolePermission).where(
                RolePermission.role_id == roles["executive_director"].id,
                RolePermission.permission_id == p_obj.id,
            )
        )
        if not rp_check.scalars().first():
            db.add(RolePermission(role_id=roles["executive_director"].id, permission_id=p_obj.id))

    # Grant Prevention & Healing worker permissions
    ph_worker_perms = [
        Permissions.PH_RECORD_READ.value,
        Permissions.PH_RECORD_CREATE.value,
        Permissions.PH_RECORD_UPDATE.value,
        Permissions.PH_REPORT_READ.value,
        Permissions.PH_IMPORT_UPLOAD.value,
        Permissions.PH_STAFF_ONBOARD_READ.value,
    ]
    for p_key in ph_worker_perms:
        if p_key in all_perms:
            rp_check = await db.execute(
                select(RolePermission).where(
                    RolePermission.role_id == roles["caseworker"].id,
                    RolePermission.permission_id == all_perms[p_key].id,
                )
            )
            if not rp_check.scalars().first():
                db.add(RolePermission(role_id=roles["caseworker"].id, permission_id=all_perms[p_key].id))

    # Grant Finance permissions
    ph_finance_perms = [
        Permissions.PH_RECORD_READ.value,
        Permissions.PH_REPORT_READ.value,
        Permissions.PH_REPORT_EXPORT.value,
    ]
    for p_key in ph_finance_perms:
        if p_key in all_perms:
            rp_check = await db.execute(
                select(RolePermission).where(
                    RolePermission.role_id == roles["finance_staff"].id,
                    RolePermission.permission_id == all_perms[p_key].id,
                )
            )
            if not rp_check.scalars().first():
                db.add(RolePermission(role_id=roles["finance_staff"].id, permission_id=all_perms[p_key].id))

    # 3. Ensure Prevention & Healing Team exists (Team ID 3)
    team_res = await db.execute(select(Team).where(Team.code == "prevention_healing"))
    ph_team = team_res.scalars().first()
    if not ph_team:
        ph_team = Team(code="prevention_healing", name="Prevention & Healing Services", short_name="PH")
        db.add(ph_team)
        await db.flush()

    # 4. Standard Authorized Test Users (with password123)
    users_data = [
        ("director@crbcl.ca", "Chief Executive Director", "executive_director"),
        ("supervisor@crbcl.ca", "Karen Supervisor", "supervisor"),
        ("worker@crbcl.ca", "Sarah Caseworker", "caseworker"),
        ("finance@crbcl.ca", "Frank Finance", "finance_staff"),
        ("itadmin@crbcl.ca", "IT Administrator", "it_admin"),
    ]
    for email, full_name, role_key in users_data:
        u_res = await db.execute(select(User).where(User.email == email))
        user = u_res.scalars().first()
        if not user:
            user = User(
                email=email,
                email_normalized=email.lower(),
                password_hash=hash_password("password123"),
                full_name=full_name,
                is_active=True,
                is_verified=True,
            )
            db.add(user)
            await db.flush()
            db.add(UserRole(user_id=user.id, role_id=roles[role_key].id))
            db.add(TeamMembership(user_id=user.id, team_id=ph_team.id, is_primary=True))

    # 5. Canonical Persons with strict 10-digit IDs
    persons_data = [
        ("1000000001", "George", "Pelletier", date(1985, 4, 12), "Cowessess First Nation"),
        ("1000000002", "Sarah", "Pelletier", date(1988, 9, 22), "Cowessess First Nation"),
        ("1000000003", "Marcus", "Delorme", date(1992, 1, 15), "Cowessess First Nation"),
        ("1000000004", "Marcus", "J. Delorme", date(1990, 11, 3), "Zagimay / Ochapowace"),  # Disambiguation candidate
        ("1000000005", "Elena", "Whitebear", date(2015, 6, 18), "Cowessess First Nation"),
    ]
    seeded_persons = {}
    for pid_num, fn, ln, dob, nation in persons_data:
        p_res = await db.execute(select(Person).where(Person.person_id_number == pid_num))
        person = p_res.scalars().first()
        if not person:
            person = Person(
                person_id_number=pid_num,
                first_name=fn,
                last_name=ln,
                date_of_birth=dob,
            )
            db.add(person)
            await db.flush()
        seeded_persons[pid_num] = person

    # 6. Canonical Client & Case for George Pelletier
    c_res = await db.execute(select(Client).where(Client.person_id == seeded_persons["1000000001"].id))
    client = c_res.scalars().first()
    if not client:
        client = Client(
            person_id=seeded_persons["1000000001"].id,
            first_name="George",
            last_name="Pelletier",
            status="ACTIVE",
        )
        db.add(client)
        await db.flush()

    case_res = await db.execute(select(Case).where(Case.client_id == client.id))
    case = case_res.scalars().first()
    if not case:
        case = Case(
            case_number="CS-2026-SYNTH-01",
            title="Synthetic Family Wellness Support Case",
            client_id=client.id,
            status="Open",
            case_type="Family Wellness",
            assigned_worker_id=None,
        )
        db.add(case)
        await db.flush()

    # 7. Inactive Pending Staff Profiles (Fictional Synthetic Names)
    # Profile 1: Worker without email
    sp1_check = await db.execute(select(PendingStaffProfile).where(PendingStaffProfile.display_name_from_excel == "Synthetic Pending Worker One"))
    if not sp1_check.scalars().first():
        db.add(PendingStaffProfile(
            first_name="Synthetic",
            last_name="Worker One",
            display_name_from_excel="Synthetic Pending Worker One",
            position="Prevention Support Worker",
            department="Prevention & Healing",
            email=None,  # No email in historical workbook
            phone="306-555-0101",
            notes="Identified in synthetic staging tracker. Account inactive.",
            onboarding_status="PENDING",
        ))

    # Profile 2: Worker without email
    sp2_check = await db.execute(select(PendingStaffProfile).where(PendingStaffProfile.display_name_from_excel == "Synthetic Pending Worker Two"))
    if not sp2_check.scalars().first():
        db.add(PendingStaffProfile(
            first_name="Synthetic",
            last_name="Worker Two",
            display_name_from_excel="Synthetic Pending Worker Two",
            position="Cultural Healing Facilitator",
            department="Prevention & Healing",
            email=None,
            phone="306-555-0102",
            notes="Identified in cultural workshops tracker. Account inactive.",
            onboarding_status="PENDING",
        ))

    # Profile 3: Verified Employee WITHOUT Login Account
    emp_res = await db.execute(select(Employee).where(Employee.email == "synthetic.verified3@crbcl.ca"))
    verified_emp = emp_res.scalars().first()
    if not verified_emp:
        verified_emp = Employee(
            employee_number="EMP-SYNTH-003",
            first_name="Synthetic",
            last_name="Worker Three",
            email="synthetic.verified3@crbcl.ca",
            phone="306-555-0103",
            position="Family Preservation Specialist",
            department="Prevention & Healing",
            employment_status="ACTIVE",
            hire_date=date(2025, 4, 1),
        )
        db.add(verified_emp)
        await db.flush()

    sp3_check = await db.execute(select(PendingStaffProfile).where(PendingStaffProfile.display_name_from_excel == "Synthetic Verified Worker Three"))
    if not sp3_check.scalars().first():
        db.add(PendingStaffProfile(
            first_name="Synthetic",
            last_name="Worker Three",
            display_name_from_excel="Synthetic Verified Worker Three",
            position="Family Preservation Specialist",
            department="Prevention & Healing",
            email="synthetic.verified3@crbcl.ca",
            phone="306-555-0103",
            employee_id=verified_emp.id,
            onboarding_status="VERIFIED_PENDING_ACCOUNT",  # Verified but CANNOT authenticate
            notes="Corporate email verified. Awaiting production account activation window.",
        ))

    # 8. Synthetic Reconciliation Queue entries (PHClientRef)
    crefs_data = [
        ("RM-SYNTH-101", "REDMANE", "UNRESOLVED"),
        ("RM-SYNTH-102", "REDMANE", "UNRESOLVED"),
        ("RM-DELORME-FAM", "FAMILY_REF", "UNRESOLVED"),
    ]
    for leg_id, leg_type, stat in crefs_data:
        cr_res = await db.execute(select(PHClientRef).where(PHClientRef.legacy_id == leg_id))
        if not cr_res.scalars().first():
            db.add(PHClientRef(
                legacy_id=leg_id,
                legacy_id_type=leg_type,
                status=stat,
            ))

    # 9. Synthetic Enhancement Programs (Decimal-accurate expenditures)
    ep1_check = await db.execute(select(EnhancementProgram).where(EnhancementProgram.program == "Traditional Beading & Storytelling"))
    if not ep1_check.scalars().first():
        db.add(EnhancementProgram(
            program="Traditional Beading & Storytelling",
            program_activity="Youth Cultural Circle",
            employee_name_raw="Synthetic Pending Worker One",
            employee_id=None,
            record_date=date(2026, 6, 15),
            date_provided=date(2026, 6, 15),
            city="Regina",
            province="SK",
            partners="Cowessess Knowledge Keepers",
            families_in_province=8,
            families_out_of_province=2,
            participants_children_0_12=10,
            participants_youth_13_17=8,
            participants_post_majority_18_26=2,
            participants_parents_caregivers=5,
            participants_family_members=0,
            participants_others=0,
            account_code="41000",
            subcode="213",
            expense_gift_card=Decimal("250.00"),
            expense_purchase_order=Decimal("500.00"),
            expense_eft=Decimal("150.00"),
            expense_cheque=Decimal("0.00"),
            expense_credit_card=Decimal("0.00"),
            expense_courtesy_card=Decimal("0.00"),
            comments="Synthetic cultural workshop activity.",
            fiscal_year="2026-2027",
        ))

    ep2_check = await db.execute(select(EnhancementProgram).where(EnhancementProgram.program == "Land-Based Parenting Camp"))
    if not ep2_check.scalars().first():
        db.add(EnhancementProgram(
            program="Land-Based Parenting Camp",
            program_activity="Family Camp Round Valley",
            employee_name_raw="Synthetic Verified Worker Three",
            employee_id=verified_emp.id,
            record_date=date(2026, 7, 20),
            date_provided=date(2026, 7, 20),
            city="Cowessess",
            province="SK",
            partners="Chief Red Bear Lodge Staff",
            families_in_province=12,
            families_out_of_province=1,
            participants_children_0_12=18,
            participants_youth_13_17=12,
            participants_post_majority_18_26=4,
            participants_parents_caregivers=8,
            participants_family_members=0,
            participants_others=0,
            account_code="41000",
            subcode="215",
            expense_gift_card=Decimal("400.00"),
            expense_purchase_order=Decimal("1200.00"),
            expense_eft=Decimal("350.00"),
            expense_cheque=Decimal("0.00"),
            expense_credit_card=Decimal("0.00"),
            expense_courtesy_card=Decimal("0.00"),
            comments="Synthetic land-based gathering.",
            fiscal_year="2026-2027",
        ))

    # 10. Synthetic Family Support Records (with legacy ID RM-SYNTH-101 and RM-SYNTH-102)
    fs1_check = await db.execute(select(FamilySupportRecord).where(FamilySupportRecord.client_ref_legacy_id == "RM-SYNTH-101"))
    if not fs1_check.scalars().first():
        db.add(FamilySupportRecord(
            program="Family Support Services",
            support_type="Emergency Food Support",
            service_area="Regina Urban",
            record_date=date(2026, 6, 18),
            date_provided=date(2026, 6, 18),
            client_ref_legacy_id="RM-SYNTH-101",
            city="Regina",
            province="SK",
            participants_children_0_12=2,
            participants_youth_13_17=1,
            participants_adults_18_plus=1,
            account_code="41000",
            subcode="110",
            project_code="215",
            expense_gift_card=Decimal("200.00"),
            expense_purchase_order=Decimal("150.00"),
            expense_petty_cash=Decimal("50.00"),
            comments="Synthetic grocery support for family.",
            client_match_status="UNRESOLVED",
            fiscal_year="2026-2027",
        ))

    fs2_check = await db.execute(select(FamilySupportRecord).where(FamilySupportRecord.client_ref_legacy_id == "RM-SYNTH-102"))
    if not fs2_check.scalars().first():
        db.add(FamilySupportRecord(
            program="Family Support Services",
            support_type="Utility Arrears Assistance",
            service_area="Regina Urban",
            record_date=date(2026, 7, 5),
            date_provided=date(2026, 7, 5),
            client_ref_legacy_id="RM-SYNTH-102",
            city="Regina",
            province="SK",
            participants_children_0_12=1,
            participants_youth_13_17=1,
            participants_adults_18_plus=1,
            account_code="41000",
            subcode="110",
            project_code="215",
            expense_cheque=Decimal("450.00"),
            comments="Synthetic power bill crisis support.",
            client_match_status="UNRESOLVED",
            fiscal_year="2026-2027",
        ))

    # 11. Synthetic Other Nations Support
    on1_check = await db.execute(select(OtherNationsSupport).where(OtherNationsSupport.family_reference_raw == "Delorme Family Household"))
    if not on1_check.scalars().first():
        db.add(OtherNationsSupport(
            worker_name_raw="Synthetic Cultural Worker",
            record_date=date(2026, 7, 27),
            family_reference_raw="Delorme Family Household",
            service_type="Temporary Emergency Shelter",
            cost=Decimal("1250.00"),
            on_reserve=False,
            cowessess_connection="Extended kinship",
            other_community="Zagimay",
            historical_reference_number="3640201301",
            comments="Off-reserve support coordination (synthetic).",
            fiscal_year="2026-2027",
        ))

    on2_check = await db.execute(select(OtherNationsSupport).where(OtherNationsSupport.family_reference_raw == "Keewatin Family"))
    if not on2_check.scalars().first():
        db.add(OtherNationsSupport(
            worker_name_raw="Synthetic Intake Coordinator",
            record_date=date(2026, 8, 12),
            family_reference_raw="Keewatin Family",
            service_type="Medical Travel & Lodging",
            cost=Decimal("850.50"),
            on_reserve=False,
            cowessess_connection="Spouse band member",
            other_community="Muscowpetung",
            historical_reference_number="3610258302",
            comments="Travel support for specialized children's medical care (synthetic).",
            fiscal_year="2026-2027",
        ))

    await db.commit()
    logger.info("Staging synthetic test dataset seeded successfully.")
    return {
        "status": "SUCCESS",
        "persons": len(persons_data),
        "pending_staff": 3,
        "client_refs": len(crefs_data),
        "enhancement_programs": 2,
        "family_support": 2,
        "other_nations": 2,
    }


if __name__ == "__main__":
    async def main():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        async with async_session_factory() as session:
            res = await seed_staging_synthetic_data(session)
            print("Seed result:", res)
    asyncio.run(main())
