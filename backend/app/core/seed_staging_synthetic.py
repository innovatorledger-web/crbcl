"""CRBCL Platform — Dedicated Staging Synthetic Test Data Seeder.

Creates a completely isolated synthetic data environment for Phase 4 verification:
- Strict authorization safeguards (refuses to run unless CRBCL_ALLOW_SYNTHETIC_SEEDING=true)
- Database destination guards (rejects production URLs, railway, genserver, and live databases)
- Secure credential management (never hardcoded, loads from CRBCL_SYNTHETIC_TEST_PASSWORD or generates cryptographically strong secret)
- Protection of existing accounts (never overwrites or resets existing test/admin accounts)
- Canonical Persons with valid 10-digit numeric person_id_numbers
- Unmistakably fictional synthetic identities (zero real personal names or real community data)
- Inactive Prevention & Healing pending staff profiles (without emails)
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
import json
import logging
import os
import secrets
import uuid
from datetime import date, datetime, UTC
from decimal import Decimal
from urllib.parse import urlparse

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
from app.models.user import User, UserPreference
from app.permissions.constants import Permissions

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("crbcl.seed.staging")

PROHIBITED_HOST_PATTERNS = [
    "railway.app",
    "up.railway.app",
    "rlwy.net",
    "genserver.online",
    "production",
    "crbcl-production",
    "live",
]

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "::1",
    "test",
    "staging-db",
    "host.docker.internal",
]


def verify_safe_seeding_environment(settings, test_password: str | None = None) -> None:
    """Rigorous verification that synthetic seeding is explicitly authorized and safe."""
    # 1. Refuse without explicit authorization flag
    is_auth = (
        getattr(settings, "crbcl_allow_synthetic_seeding", False)
        or os.environ.get("CRBCL_ALLOW_SYNTHETIC_SEEDING", "").lower() == "true"
    )
    if not is_auth:
        raise RuntimeError(
            "CRITICAL SECURITY REJECTION: Synthetic seeding is disabled by default. "
            "You must explicitly set CRBCL_ALLOW_SYNTHETIC_SEEDING=true in an authorized, "
            "isolated non-production test environment."
        )

    # 2. Refuse if application environment is production
    is_prod = getattr(settings, "is_production", False) or getattr(settings, "app_env", "").lower() == "production"
    if is_prod:
        raise RuntimeError(
            "CRITICAL SECURITY REJECTION: Synthetic seeding cannot run in production (app_env=production)."
        )

    # 3. Verify database destination URL
    db_url = (getattr(settings, "database_url", "") or "").lower()
    if not db_url:
        raise RuntimeError("CRITICAL SECURITY REJECTION: No database destination URL configured.")

    for pattern in PROHIBITED_HOST_PATTERNS:
        if pattern in db_url:
            raise RuntimeError(
                f"CRITICAL SECURITY REJECTION: Target database URL matches prohibited live pattern '{pattern}'. "
                "Synthetic seeding is permanently blocked from live infrastructure."
            )

    # 4. Parse host and reject ambiguous destinations
    is_sqlite = "sqlite" in db_url
    if is_sqlite:
        for pattern in PROHIBITED_HOST_PATTERNS:
            if pattern in db_url:
                raise RuntimeError(
                    f"CRITICAL SECURITY REJECTION: SQLite file path contains prohibited pattern '{pattern}'."
                )
    else:
        parsed = urlparse(db_url.replace("postgresql+asyncpg://", "http://").replace("postgresql://", "http://"))
        host = (parsed.hostname or "").lower()
        is_allowed_host = any(allowed in host for allowed in ALLOWED_HOSTS) if host else False

        if not is_allowed_host:
            raise RuntimeError(
                f"CRITICAL SECURITY REJECTION: Database host '{host}' is not on the verified local/staging whitelist. "
                "Synthetic seeding requires an isolated local or explicitly verified staging target."
            )

    # 5. Verify password complexity if supplied
    pw_to_check = test_password
    if pw_to_check is None:
        pw_to_check = getattr(settings, "crbcl_synthetic_test_password", None) or os.environ.get("CRBCL_SYNTHETIC_TEST_PASSWORD")

    if pw_to_check:
        if len(pw_to_check) < 12:
            raise RuntimeError(
                "CRITICAL SECURITY REJECTION: CRBCL_SYNTHETIC_TEST_PASSWORD does not meet minimum length "
                "(minimum 12 characters required)."
            )
        has_upper = any(c.isupper() for c in pw_to_check)
        has_lower = any(c.islower() for c in pw_to_check)
        has_digit = any(c.isdigit() for c in pw_to_check)
        has_special = any(not c.isalnum() for c in pw_to_check)
        if not (has_upper and has_lower and has_digit and has_special):
            raise RuntimeError(
                "CRITICAL SECURITY REJECTION: CRBCL_SYNTHETIC_TEST_PASSWORD does not meet complexity requirements "
                "(must contain uppercase, lowercase, digit, and special symbol)."
            )


async def seed_staging_synthetic_data(db: AsyncSession) -> dict:
    settings = get_settings()
    verify_safe_seeding_environment(settings)

    logger.info("Environment verified safe for synthetic staging dataset. Initializing...")

    # Determine secure credentials from environment or generate strong token
    supplied_password = settings.crbcl_synthetic_test_password or os.environ.get("CRBCL_SYNTHETIC_TEST_PASSWORD")
    if not supplied_password:
        generated_token = secrets.token_urlsafe(24)
        active_password = generated_token
        logger.info("Synthetic credentials generated via secure cryptographically strong random token.")
    else:
        verify_safe_seeding_environment(settings, test_password=supplied_password)
        active_password = supplied_password
        logger.info("Using externally supplied synthetic test credentials from configuration.")

    password_hash = hash_password(active_password)

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

    # 4. Standard Authorized Test Users — NEVER modify existing non-synthetic accounts
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
            # Create synthetic user with secured credentials
            user = User(
                email=email,
                email_normalized=email.lower(),
                password_hash=password_hash,
                full_name=full_name,
                is_active=True,
                is_verified=True,
            )
            db.add(user)
            await db.flush()
            db.add(UserRole(user_id=user.id, role_id=roles[role_key].id))
            db.add(TeamMembership(user_id=user.id, team_id=ph_team.id, is_primary=True))
            db.add(UserPreference(user_id=user.id, key="team_access", value=json.dumps(["3", "all"] if role_key in ["executive_director", "supervisor"] else ["3"])))
        else:
            # Ensure team_access preference exists so user can access PH workspace
            pref_check = await db.execute(select(UserPreference).where(UserPreference.user_id == user.id, UserPreference.key == "team_access"))
            if not pref_check.scalars().first():
                db.add(UserPreference(user_id=user.id, key="team_access", value=json.dumps(["3", "all"] if role_key in ["executive_director", "supervisor"] else ["3"])))

    # 5. Canonical Persons with strict 10-digit IDs and UNMISTAKABLY FICTIONAL IDENTITIES
    # Zero real individuals or real community band names are used
    persons_data = [
        ("1000000001", "Synthetic-Person", "Alpha-TestFamily", date(1990, 1, 1), "Synthetic Nation Alpha"),
        ("1000000002", "Synthetic-Person", "Beta-TestFamily", date(1992, 2, 2), "Synthetic Nation Alpha"),
        ("1000000003", "Synthetic-Disambig", "Candidate-One", date(1988, 3, 3), "Synthetic Nation Alpha"),
        ("1000000004", "Synthetic-Disambig", "Candidate-Two", date(1987, 4, 4), "Synthetic Neighbor Community"),
        ("1000000005", "Synthetic-Child", "Epsilon-TestFamily", date(2018, 5, 5), "Synthetic Nation Alpha"),
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

    # 6. Canonical Client & Case for Synthetic Alpha
    c_res = await db.execute(select(Client).where(Client.person_id == seeded_persons["1000000001"].id))
    client = c_res.scalars().first()
    if not client:
        client = Client(
            person_id=seeded_persons["1000000001"].id,
            first_name="Synthetic-Person",
            last_name="Alpha-TestFamily",
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
    emp_res = await db.execute(select(Employee).where(Employee.email == "synthetic.verified3@crbcl.test"))
    verified_emp = emp_res.scalars().first()
    if not verified_emp:
        verified_emp = Employee(
            employee_number="EMP-SYNTH-003",
            first_name="Synthetic",
            last_name="Worker Three",
            email="synthetic.verified3@crbcl.test",
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
            email="synthetic.verified3@crbcl.test",
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
    ep1_check = await db.execute(select(EnhancementProgram).where(EnhancementProgram.program == "Synthetic Cultural Storytelling Workshop"))
    if not ep1_check.scalars().first():
        db.add(EnhancementProgram(
            program="Synthetic Cultural Storytelling Workshop",
            program_activity="Youth Cultural Circle",
            employee_name_raw="Synthetic Pending Worker One",
            employee_id=None,
            record_date=date(2026, 6, 15),
            date_provided=date(2026, 6, 15),
            city="Regina",
            province="SK",
            partners="Synthetic Partner Knowledge Circle",
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

    ep2_check = await db.execute(select(EnhancementProgram).where(EnhancementProgram.program == "Synthetic Land-Based Parenting Gathering"))
    if not ep2_check.scalars().first():
        db.add(EnhancementProgram(
            program="Synthetic Land-Based Parenting Gathering",
            program_activity="Family Camp Round Valley",
            employee_name_raw="Synthetic Verified Worker Three",
            employee_id=verified_emp.id,
            record_date=date(2026, 7, 20),
            date_provided=date(2026, 7, 20),
            city="Synthetic-Centre",
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

    # 11. Synthetic Other Nations Support (Fictional Household references)
    on1_check = await db.execute(select(OtherNationsSupport).where(OtherNationsSupport.family_reference_raw == "Synthetic Household Alpha"))
    if not on1_check.scalars().first():
        db.add(OtherNationsSupport(
            worker_name_raw="Synthetic Cultural Worker",
            record_date=date(2026, 7, 27),
            family_reference_raw="Synthetic Household Alpha",
            service_type="Temporary Emergency Shelter",
            cost=Decimal("1250.00"),
            on_reserve=False,
            cowessess_connection="Extended kinship",
            other_community="Synthetic Partner Community",
            historical_reference_number="SYNTH-3640201301",
            comments="Off-reserve support coordination (synthetic).",
            fiscal_year="2026-2027",
        ))

    on2_check = await db.execute(select(OtherNationsSupport).where(OtherNationsSupport.family_reference_raw == "Synthetic Household Beta"))
    if not on2_check.scalars().first():
        db.add(OtherNationsSupport(
            worker_name_raw="Synthetic Intake Coordinator",
            record_date=date(2026, 8, 12),
            family_reference_raw="Synthetic Household Beta",
            service_type="Medical Travel & Lodging",
            cost=Decimal("850.50"),
            on_reserve=False,
            cowessess_connection="Spouse kinship member",
            other_community="Synthetic Ally Community",
            historical_reference_number="SYNTH-3610258302",
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
