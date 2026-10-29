"""Client management endpoints with comprehensive Phase 2 sub-profiles, duplicate detection, and field-level permissions."""

from __future__ import annotations

import uuid
from datetime import UTC, date, datetime

from fastapi import APIRouter, Depends, File, HTTPException, Query, Request, UploadFile, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.audit.service import AuditService
from app.core.database import get_db
from app.models.client import Client, ClientApprovalHistory
from app.models.person import (
    Person,
    PersonAddress,
)
from app.models.user import User
from app.permissions.constants import Permissions
from app.permissions.dependencies import require_any_permission, require_permission
from app.permissions.service import PermissionService
from app.repositories.client_repo import ClientRepository
from app.repositories.medical_repo import MedicalRepository
from app.repositories.person_repo import PersonRepository
from app.repositories.provider_repo import ProviderRepository
from app.repositories.school_repo import SchoolRepository
from app.schemas.client import (
    ClientApprovalHistoryResponse,
    ClientApprovalItemResponse,
    ClientCreate,
    ClientDecisionRequest,
    ClientResponse,
    ClientReviewResponse,
    ClientSubmitExistingRequest,
    ClientSubmitNewRequest,
    ClientUpdate,
)
from app.schemas.common import PaginatedResponse, PaginationMeta
from app.schemas.person import PersonCreate, PersonSearchResultResponse
from app.services.duplicate_service import DuplicateService
from app.services.file_security import generate_signed_file_url
from app.services.merge_service import MergeService
from app.services.person_service import PersonService
from app.workflows.timeline import TimelineEventType, TimelineService

router = APIRouter(prefix="/clients", tags=["Clients"])


def _populate_client_response(
    client: Client,
    person: Person | None = None,
    submitter: User | None = None,
    decider: User | None = None,
) -> ClientResponse:
    res = ClientResponse.model_validate(client)
    p = person or client.person
    if p:
        res.person_id = p.id
        res.person_id_number = p.person_id_number
        if p.photo_document_id:
            res.photo_url = generate_signed_file_url(p.photo_document_id, expiry_seconds=3600)
        elif p.photo_url:
            res.photo_url = p.photo_url

    sub = submitter or client.submitter
    if sub:
        res.submitted_by = sub.id
        res.submitted_by_name = (sub.display_name or sub.full_name or "").strip()

    dec = decider or client.decider
    if dec:
        res.decided_by = dec.id
        res.decided_by_name = (dec.display_name or dec.full_name or "").strip()

    res.is_deleted = client.is_deleted
    res.deleted_at = client.deleted_at
    if client.deleted_at:
        days_in_trash = (datetime.now(UTC) - client.deleted_at).days
        res.days_until_purge = max(0, 45 - days_in_trash)

    return res


# ── Phase 2 Schemas ──────────────────────────────────────────


class DuplicateCheckRequest(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: str | None = None
    treaty_number: str | None = None
    health_card_number: str | None = None
    phone: str | None = None
    email: str | None = None


class MergeRequest(BaseModel):
    source_person_id: uuid.UUID
    target_person_id: uuid.UUID
    reason: str
    notes: str = ""


class AddressCreate(BaseModel):
    address_type: str = "Residential"
    address_line_1: str
    address_line_2: str | None = None
    city: str = "Regina"
    province: str = "Saskatchewan"
    postal_code: str | None = None
    on_reserve: bool = False
    latitude: float | None = None
    longitude: float | None = None
    is_primary: bool = True
    valid_from: date | None = None
    valid_to: date | None = None


class AllergyCreate(BaseModel):
    allergen: str
    reaction: str = ""
    severity: str = "Moderate"
    is_active: bool = True
    notes: str | None = None


class ConditionCreate(BaseModel):
    condition_name: str
    diagnosed_date: date | None = None
    is_chronic: bool = False
    is_active: bool = True
    treatment_plan: str | None = None
    notes: str | None = None


class MedicationCreate(BaseModel):
    medication_name: str
    dosage: str
    frequency: str
    route: str = "Oral"
    prescriber_id: uuid.UUID | None = None
    prescriber_name: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    status: str = "Active"
    instructions: str | None = None
    notes: str | None = None


class MedicalProfileUpdate(BaseModel):
    dental_notes: str | None = None
    mental_health_notes: str | None = None
    chemical_dependency_history: str | None = None
    general_notes: str | None = None
    primary_physician_name: str | None = None
    primary_physician_phone: str | None = None


class ProviderLinkCreate(BaseModel):
    provider_id: uuid.UUID
    role: str = "Primary Care"
    start_date: date | None = None
    end_date: date | None = None
    notes: str = ""


class SchoolEnrollmentCreate(BaseModel):
    school_id: uuid.UUID
    grade_level: str = "Grade 1"
    start_date: date | None = None
    has_iep: bool = False
    iep_details: str | None = None
    school_contact_person: str | None = None
    attendance_concerns: str | None = None
    notes: str | None = None


class StrengthCreate(BaseModel):
    name: str
    notes: str | None = None


class ChallengeCreate(BaseModel):
    name: str
    severity: str = "Moderate"
    is_active: bool = True
    notes: str | None = None


class CulturalProfileUpdate(BaseModel):
    cultural_connections: str | None = None
    ceremonies: str | None = None
    elders_connected: str | None = None
    land_based_activities: str | None = None
    language_goals: str | None = None
    dietary_preferences: str | None = None
    extracurricular_activities: str | None = None
    notes: str | None = None


# ── Client Base Endpoints ────────────────────────────────────


@router.get("/counts", response_model=dict[str, int])
async def get_client_counts(
    user: User = Depends(require_permission(Permissions.CLIENT_READ)),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve aggregate counts for client directory filter tabs including Trash."""
    perm_service = PermissionService(db)
    accessible_team_ids = await perm_service.get_user_accessible_team_ids(user.id)
    repo = ClientRepository(db)
    return await repo.get_status_counts(accessible_team_ids=accessible_team_ids)


@router.get("", response_model=PaginatedResponse[ClientResponse])
async def list_clients(
    request: Request,
    query: str | None = Query(default=None, description="Search by name, email, phone, Person ID"),
    status_filter: str | None = Query(default=None, alias="status"),
    approval_status: str | None = Query(default=None, description="Filter by approval status: APPROVED, PENDING_APPROVAL, RETURNED, DECLINED"),
    risk_level: str | None = Query(default=None),
    team_id: uuid.UUID | None = Query(default=None),
    trash: bool = Query(default=False, description="Whether to fetch soft-deleted clients currently in trash"),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    sort: str | None = Query(default=None),
    user: User = Depends(require_permission(Permissions.CLIENT_READ)),
    db: AsyncSession = Depends(get_db),
):
    # Enforce role boundaries: IT Admin and Board Member cannot access client operational records
    person_service = PersonService(db)
    await person_service.assert_client_role_authorized(user, "list Clients")

    perm_service = PermissionService(db)
    accessible_team_ids = await perm_service.get_user_accessible_team_ids(user.id)

    repo = ClientRepository(db)
    clients, total = await repo.search(
        query_text=query,
        status=status_filter,
        approval_status=approval_status,
        risk_level=risk_level,
        team_id=team_id,
        accessible_team_ids=accessible_team_ids,
        offset=offset,
        limit=limit,
        sort_by=sort,
        trash=trash,
    )

    return PaginatedResponse[ClientResponse](
        items=[_populate_client_response(c) for c in clients],
        pagination=PaginationMeta(
            total=total,
            limit=limit,
            offset=offset,
            has_more=(offset + limit) < total,
        ),
    )


@router.get("/search-person", response_model=PaginatedResponse[PersonSearchResultResponse])
async def search_persons_before_client(
    query: str | None = Query(default=None, description="Search by name, aliases, or digits"),
    person_id_number: str | None = Query(default=None, description="Exact or prefix Person ID number"),
    date_of_birth: str | None = Query(default=None, description="YYYY-MM-DD"),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    user: User = Depends(require_any_permission(Permissions.CLIENT_READ, Permissions.CLIENT_CREATE)),
    db: AsyncSession = Depends(get_db),
):
    """
    Search canonical Person identities before client creation.
    Identifies whether a person already has an approved client context or a pending proposal.
    Does NOT disclose photographs in candidate search results.
    """
    person_service = PersonService(db)
    await person_service.assert_client_role_authorized(user, "search")

    items, total = await person_service.person_repo.search_people(
        query_text=query,
        person_id_number=person_id_number,
        date_of_birth=date_of_birth,
        limit=limit,
        offset=offset,
    )

    client_repo = ClientRepository(db)
    results: list[PersonSearchResultResponse] = []
    for p in items:
        sr = PersonSearchResultResponse.model_validate(p)
        client = await client_repo.get_by_person_id(p.id)
        if client:
            sr.client_id = client.id
            sr.client_approval_status = client.approval_status
        results.append(sr)

    return PaginatedResponse[PersonSearchResultResponse](
        items=results,
        pagination=PaginationMeta(
            total=total,
            limit=limit,
            offset=offset,
            has_more=(offset + limit) < total,
        ),
    )


@router.post("/submit-existing", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
async def submit_existing_person(
    payload: ClientSubmitExistingRequest,
    request: Request,
    user: User = Depends(require_any_permission(Permissions.CLIENT_CREATE, Permissions.CLIENT_SUBMIT)),
    db: AsyncSession = Depends(get_db),
):
    """Propose an existing canonical Person as a Client for Supervisor/Director approval."""
    person_service = PersonService(db)
    await person_service.assert_client_role_authorized(user, "propose as client")
    person = await person_service.get_person_or_404(payload.person_id)

    client_repo = ClientRepository(db)
    existing_client = await client_repo.get_by_person_id(person.id)
    now = datetime.now(UTC)

    perm_service = PermissionService(db)
    has_approve_perm = await perm_service.user_has_permission(user.id, Permissions.CLIENT_APPROVE)

    if existing_client:
        if existing_client.approval_status == "APPROVED":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "error": {
                        "code": "ALREADY_CLIENT",
                        "message": f"{person.first_name} {person.last_name} is already an approved client.",
                        "client_id": str(existing_client.id),
                    }
                },
            )
        if existing_client.approval_status == "PENDING_APPROVAL":
            if not has_approve_perm:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail={
                        "error": {
                            "code": "CLIENT_PENDING_APPROVAL",
                            "message": f"{person.first_name} {person.last_name} already has a pending client proposal awaiting review.",
                            "client_id": str(existing_client.id),
                        }
                    },
                )
            # Authorized approver direct review & activation of existing pending proposal
            old_status = existing_client.approval_status
            existing_client.approval_status = "APPROVED"
            existing_client.status = "Active"
            existing_client.decided_by = user.id
            existing_client.decided_at = now
            existing_client.decision_reason = payload.submission_notes or "Direct authorized approval by supervisor/director."
            if payload.submission_notes:
                existing_client.submission_notes = payload.submission_notes
            existing_client.risk_level = payload.risk_level
            if payload.assigned_team_id:
                existing_client.assigned_team_id = payload.assigned_team_id
            existing_client.updated_by = user.id

            history_entry = ClientApprovalHistory(
                client_id=existing_client.id,
                person_id=person.id,
                action="APPROVED",
                from_status=old_status,
                to_status="APPROVED",
                actor_id=user.id,
                notes=payload.submission_notes or "Direct authorized approval by supervisor/director.",
                created_at=now,
            )
            await client_repo.add_approval_history(history_entry)
            target_client = existing_client
        else:
            # Re-submitting or directly approving a previously RETURNED or DECLINED client proposal
            old_status = existing_client.approval_status
            if has_approve_perm:
                existing_client.approval_status = "APPROVED"
                existing_client.status = "Active"
                existing_client.decided_by = user.id
                existing_client.decided_at = now
                existing_client.decision_reason = payload.submission_notes or "Direct authorized approval by supervisor/director."
                action_type = "APPROVED"
                to_status = "APPROVED"
                hist_notes = payload.submission_notes or "Direct authorized approval by supervisor/director."
            else:
                existing_client.approval_status = "PENDING_APPROVAL"
                existing_client.status = "Pending Intake"
                existing_client.decided_by = None
                existing_client.decided_at = None
                existing_client.decision_reason = None
                action_type = "SUBMITTED"
                to_status = "PENDING_APPROVAL"
                hist_notes = payload.submission_notes

            existing_client.submitted_by = user.id
            existing_client.submitted_at = now
            existing_client.submission_notes = payload.submission_notes
            existing_client.risk_level = payload.risk_level
            if payload.assigned_team_id:
                existing_client.assigned_team_id = payload.assigned_team_id
            existing_client.updated_by = user.id

            history_entry = ClientApprovalHistory(
                client_id=existing_client.id,
                person_id=person.id,
                action=action_type,
                from_status=old_status,
                to_status=to_status,
                actor_id=user.id,
                notes=hist_notes,
                created_at=now,
            )
            await client_repo.add_approval_history(history_entry)
            target_client = existing_client
    else:
        # Create fresh client record linked to canonical Person
        if has_approve_perm:
            client_approval_status = "APPROVED"
            client_status = "Active"
            decided_by = user.id
            decided_at = now
            decision_reason = payload.submission_notes or "Direct authorized creation and approval by supervisor/director."
            action_type = "APPROVED"
            hist_notes = payload.submission_notes or "Direct authorized creation and approval by supervisor/director."
        else:
            client_approval_status = "PENDING_APPROVAL"
            client_status = "Pending Intake"
            decided_by = None
            decided_at = None
            decision_reason = None
            action_type = "SUBMITTED"
            hist_notes = payload.submission_notes

        target_client = Client(
            person_id=person.id,
            first_name=person.first_name,
            last_name=person.last_name,
            date_of_birth=person.date_of_birth,
            gender=person.gender,
            status=client_status,
            approval_status=client_approval_status,
            risk_level=payload.risk_level,
            phone=person.phone,
            email=person.email,
            indigenous_identity=person.indigenous_identity,
            band_nation=person.band_nation,
            submission_notes=payload.submission_notes,
            submitted_by=user.id,
            submitted_at=now,
            decided_by=decided_by,
            decided_at=decided_at,
            decision_reason=decision_reason,
            assigned_team_id=payload.assigned_team_id,
            created_by=user.id,
            updated_by=user.id,
        )
        db.add(target_client)
        await db.flush()

        history_entry = ClientApprovalHistory(
            client_id=target_client.id,
            person_id=person.id,
            action=action_type,
            from_status=None,
            to_status=client_approval_status,
            actor_id=user.id,
            notes=hist_notes,
            created_at=now,
        )
        await client_repo.add_approval_history(history_entry)

    # Audit & Timeline
    audit_service = AuditService(db)
    if has_approve_perm:
        await audit_service.log_event(
            event_type="CLIENT_APPROVED",
            user_id=user.id,
            entity_type="client",
            entity_id=target_client.id,
            after_data={
                "person_id": str(person.id),
                "person_id_number": person.person_id_number,
                "approval_status": "APPROVED",
                "decided_by": str(user.id),
                "decided_at": now.isoformat(),
            },
            ip_address=request.client.host if request.client else None,
        )

        timeline_service = TimelineService(db)
        await timeline_service.record_event(
            event_type=TimelineEventType.CLIENT_CREATED,
            title=f"Client Created & Approved: {person.first_name} {person.last_name}",
            description=f"Directly created and approved client context (ID: {person.person_id_number}).",
            entity_type="client",
            entity_id=target_client.id,
            client_id=target_client.id,
            created_by=user.id,
        )
    else:
        await audit_service.log_event(
            event_type="CLIENT_SUBMITTED",
            user_id=user.id,
            entity_type="client",
            entity_id=target_client.id,
            after_data={
                "person_id": str(person.id),
                "person_id_number": person.person_id_number,
                "approval_status": "PENDING_APPROVAL",
                "submission_notes": payload.submission_notes,
            },
            ip_address=request.client.host if request.client else None,
        )

        timeline_service = TimelineService(db)
        await timeline_service.record_event(
            event_type=TimelineEventType.CLIENT_CREATED,
            title=f"Client Proposal Submitted: {person.first_name} {person.last_name}",
            description=f"Submitted for Supervisor/Director approval (ID: {person.person_id_number}).",
            entity_type="client",
            entity_id=target_client.id,
            client_id=target_client.id,
            created_by=user.id,
        )

    await db.commit()
    return _populate_client_response(target_client, person=person, submitter=user, decider=user if has_approve_perm else None)


@router.post("/submit-new", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
async def submit_new_person_and_client(
    payload: ClientSubmitNewRequest,
    request: Request,
    user: User = Depends(require_any_permission(Permissions.CLIENT_CREATE, Permissions.CLIENT_SUBMIT)),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new canonical Person with automatic permanent 10-digit ID,
    and submit as a Client (or auto-approve if user has CLIENT_APPROVE authority).
    """
    person_service = PersonService(db)
    await person_service.assert_client_role_authorized(user, "create person and propose client")

    # 1. Create canonical Person record with permanent 10-digit numeric ID
    person = await person_service.create_person(payload.person, current_user_id=user.id)

    # 2. Check approver authority
    perm_service = PermissionService(db)
    has_approve_perm = await perm_service.user_has_permission(user.id, Permissions.CLIENT_APPROVE)

    now = datetime.now(UTC)
    client_repo = ClientRepository(db)
    primary_addr = next((a.address_line_1 for a in person.addresses if a.is_primary), None)
    primary_city = next((a.city for a in person.addresses if a.is_primary), "Regina")
    primary_province = next((a.province for a in person.addresses if a.is_primary), "Saskatchewan")

    if has_approve_perm:
        client_approval_status = "APPROVED"
        client_status = "Active"
        decided_by = user.id
        decided_at = now
        decision_reason = payload.submission_notes or "Direct authorized creation and approval by supervisor/director."
        action_type = "APPROVED"
        hist_notes = payload.submission_notes or "Direct authorized creation and approval by supervisor/director."
    else:
        client_approval_status = "PENDING_APPROVAL"
        client_status = "Pending Intake"
        decided_by = None
        decided_at = None
        decision_reason = None
        action_type = "SUBMITTED"
        hist_notes = payload.submission_notes

    target_client = Client(
        person_id=person.id,
        first_name=person.first_name,
        last_name=person.last_name,
        date_of_birth=person.date_of_birth,
        gender=person.gender,
        status=client_status,
        approval_status=client_approval_status,
        risk_level=payload.risk_level,
        phone=person.phone,
        email=person.email,
        address=primary_addr,
        city=primary_city,
        province=primary_province,
        indigenous_identity=person.indigenous_identity,
        band_nation=person.band_nation,
        submission_notes=payload.submission_notes,
        submitted_by=user.id,
        submitted_at=now,
        decided_by=decided_by,
        decided_at=decided_at,
        decision_reason=decision_reason,
        assigned_team_id=payload.assigned_team_id,
        created_by=user.id,
        updated_by=user.id,
    )
    db.add(target_client)
    await db.flush()

    # 3. Record in append-only approval history
    history_entry = ClientApprovalHistory(
        client_id=target_client.id,
        person_id=person.id,
        action=action_type,
        from_status=None,
        to_status=client_approval_status,
        actor_id=user.id,
        notes=hist_notes,
        created_at=now,
    )
    await client_repo.add_approval_history(history_entry)

    # 4. Audit & Timeline
    audit_service = AuditService(db)
    timeline_service = TimelineService(db)

    if has_approve_perm:
        await audit_service.log_event(
            event_type="CLIENT_APPROVED",
            user_id=user.id,
            entity_type="client",
            entity_id=target_client.id,
            after_data={
                "person_id": str(person.id),
                "person_id_number": person.person_id_number,
                "approval_status": "APPROVED",
                "decided_by": str(user.id),
                "decided_at": now.isoformat(),
            },
            ip_address=request.client.host if request.client else None,
        )

        await timeline_service.record_event(
            event_type=TimelineEventType.CLIENT_CREATED,
            title=f"Client Created & Approved: {person.first_name} {person.last_name}",
            description=f"Created canonical Person (ID: {person.person_id_number}) and approved client context.",
            entity_type="client",
            entity_id=target_client.id,
            client_id=target_client.id,
            created_by=user.id,
        )
    else:
        await audit_service.log_event(
            event_type="CLIENT_SUBMITTED",
            user_id=user.id,
            entity_type="client",
            entity_id=target_client.id,
            after_data={
                "person_id": str(person.id),
                "person_id_number": person.person_id_number,
                "approval_status": "PENDING_APPROVAL",
                "submission_notes": payload.submission_notes,
            },
            ip_address=request.client.host if request.client else None,
        )

        await timeline_service.record_event(
            event_type=TimelineEventType.CLIENT_CREATED,
            title=f"New Client Proposal: {person.first_name} {person.last_name}",
            description=f"Created canonical Person (ID: {person.person_id_number}) and submitted for approval.",
            entity_type="client",
            entity_id=target_client.id,
            client_id=target_client.id,
            created_by=user.id,
        )

    await db.commit()
    return _populate_client_response(target_client, person=person, submitter=user, decider=user if has_approve_perm else None)


@router.get("/approvals/pending", response_model=PaginatedResponse[ClientApprovalItemResponse])
async def list_pending_client_approvals(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    user: User = Depends(require_permission(Permissions.CLIENT_APPROVE)),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve queue of pending client proposals awaiting Supervisor/Director review."""
    repo = ClientRepository(db)
    clients, total = await repo.get_pending_approvals(offset=offset, limit=limit)

    items: list[ClientApprovalItemResponse] = []
    for c in clients:
        photo_url = None
        if c.person and c.person.photo_document_id:
            photo_url = generate_signed_file_url(c.person.photo_document_id, expiry_seconds=3600)

        submitter_name = None
        if c.submitter:
            submitter_name = (c.submitter.display_name or c.submitter.full_name or "").strip()

        items.append(
            ClientApprovalItemResponse(
                client_id=c.id,
                person_id=c.person_id or c.id,
                person_id_number=c.person.person_id_number if c.person else "UNKNOWN",
                first_name=c.first_name,
                middle_name=c.person.middle_name if c.person else None,
                last_name=c.last_name,
                preferred_name=c.person.preferred_name if c.person else None,
                date_of_birth=c.date_of_birth,
                gender=c.gender,
                photo_url=photo_url,
                band_nation=c.band_nation,
                city=c.city,
                province=c.province,
                risk_level=c.risk_level,
                approval_status=c.approval_status,
                submitted_by=c.submitted_by,
                submitted_by_name=submitter_name,
                submitted_at=c.submitted_at,
                submission_notes=c.submission_notes,
            )
        )

    return PaginatedResponse[ClientApprovalItemResponse](
        items=items,
        pagination=PaginationMeta(
            total=total,
            limit=limit,
            offset=offset,
            has_more=(offset + limit) < total,
        ),
    )


@router.get("/approvals/{client_id}", response_model=ClientReviewResponse)
async def get_client_approval_review(
    client_id: uuid.UUID,
    user: User = Depends(require_permission(Permissions.CLIENT_APPROVE)),
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieve comprehensive submission details for a client proposal,
    including canonical Person profile with subsection permission boundaries respected.
    """
    repo = ClientRepository(db)
    client = await repo.get(client_id)
    if not client or client.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "CLIENT_NOT_FOUND", "message": "Client record not found"}},
        )

    person_data = {}
    if client.person_id:
        person_service = PersonService(db)
        # get_comprehensive_profile enforces medical/background/etc. permissions for current user
        full_prof = await person_service.get_comprehensive_profile(client.person_id, current_user=user)
        person_data = full_prof.model_dump(mode="json")

    history_records = await repo.get_approval_history(client.id)
    history_items = []
    for h in history_records:
        actor_name = None
        if h.actor:
            actor_name = (h.actor.display_name or h.actor.full_name or "").strip()
        history_items.append(
            ClientApprovalHistoryResponse(
                id=h.id,
                client_id=h.client_id,
                person_id=h.person_id,
                action=h.action,
                from_status=h.from_status,
                to_status=h.to_status,
                actor_id=h.actor_id,
                actor_name=actor_name,
                notes=h.notes,
                created_at=h.created_at,
            )
        )

    return ClientReviewResponse(
        client=_populate_client_response(client),
        person=person_data,
        approval_history=history_items,
    )


@router.post("/approvals/{client_id}/approve", response_model=ClientResponse)
async def approve_client(
    client_id: uuid.UUID,
    request: Request,
    payload: ClientDecisionRequest | None = None,
    user: User = Depends(require_permission(Permissions.CLIENT_APPROVE)),
    db: AsyncSession = Depends(get_db),
):
    """Supervisor/Director approval of pending Client proposal."""
    dec_payload = payload or ClientDecisionRequest()
    repo = ClientRepository(db)
    client = await repo.get(client_id)
    if not client or client.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "CLIENT_NOT_FOUND", "message": "Client record not found"}},
        )

    if client.approval_status != "PENDING_APPROVAL":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": {
                    "code": "INVALID_APPROVAL_TRANSITION",
                    "message": f"Client cannot be approved from '{client.approval_status}' status. Must be PENDING_APPROVAL.",
                }
            },
        )

    now = datetime.now(UTC)
    client.approval_status = "APPROVED"
    client.status = "Active"
    client.decided_by = user.id
    client.decided_at = now
    client.decision_reason = dec_payload.notes or dec_payload.reason
    client.updated_by = user.id

    history_entry = ClientApprovalHistory(
        client_id=client.id,
        person_id=client.person_id or client.id,
        action="APPROVED",
        from_status="PENDING_APPROVAL",
        to_status="APPROVED",
        actor_id=user.id,
        notes=dec_payload.notes or dec_payload.reason,
        created_at=now,
    )
    await repo.add_approval_history(history_entry)

    audit_service = AuditService(db)
    await audit_service.log_event(
        event_type="CLIENT_APPROVED",
        user_id=user.id,
        entity_type="client",
        entity_id=client.id,
        after_data={
            "approval_status": "APPROVED",
            "decision_notes": dec_payload.notes or dec_payload.reason,
        },
        ip_address=request.client.host if request.client else None,
    )

    timeline_service = TimelineService(db)
    await timeline_service.record_event(
        event_type=TimelineEventType.CLIENT_CREATED,
        title=f"Client Approved: {client.first_name} {client.last_name}",
        description="Approved as active client by supervisor/director.",
        entity_type="client",
        entity_id=client.id,
        client_id=client.id,
        created_by=user.id,
    )

    await db.commit()
    return _populate_client_response(client, decider=user)


@router.post("/approvals/{client_id}/return", response_model=ClientResponse)
async def return_client(
    client_id: uuid.UUID,
    request: Request,
    payload: ClientDecisionRequest | None = None,
    user: User = Depends(require_permission(Permissions.CLIENT_APPROVE)),
    db: AsyncSession = Depends(get_db),
):
    """Supervisor/Director returns Client proposal to worker for revisions."""
    dec_payload = payload or ClientDecisionRequest()
    reason = dec_payload.reason or dec_payload.notes
    if not reason or not reason.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": {"code": "REASON_REQUIRED", "message": "A reason or revision instructions must be provided when returning a proposal."}},
        )

    repo = ClientRepository(db)
    client = await repo.get(client_id)
    if not client or client.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "CLIENT_NOT_FOUND", "message": "Client record not found"}},
        )

    if client.approval_status != "PENDING_APPROVAL":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": {
                    "code": "INVALID_APPROVAL_TRANSITION",
                    "message": f"Client cannot be returned from '{client.approval_status}' status. Must be PENDING_APPROVAL.",
                }
            },
        )

    now = datetime.now(UTC)
    client.approval_status = "RETURNED"
    client.status = "Returned to Worker"
    client.decided_by = user.id
    client.decided_at = now
    client.decision_reason = reason.strip()
    client.updated_by = user.id

    history_entry = ClientApprovalHistory(
        client_id=client.id,
        person_id=client.person_id or client.id,
        action="RETURNED",
        from_status="PENDING_APPROVAL",
        to_status="RETURNED",
        actor_id=user.id,
        notes=reason.strip(),
        created_at=now,
    )
    await repo.add_approval_history(history_entry)

    audit_service = AuditService(db)
    await audit_service.log_event(
        event_type="CLIENT_RETURNED",
        user_id=user.id,
        entity_type="client",
        entity_id=client.id,
        after_data={
            "approval_status": "RETURNED",
            "decision_reason": reason.strip(),
        },
        ip_address=request.client.host if request.client else None,
    )

    timeline_service = TimelineService(db)
    await timeline_service.record_event(
        event_type=TimelineEventType.CLIENT_UPDATED,
        title=f"Client Proposal Returned: {client.first_name} {client.last_name}",
        description=f"Returned for revisions: {reason.strip()}",
        entity_type="client",
        entity_id=client.id,
        client_id=client.id,
        created_by=user.id,
    )

    await db.commit()
    return _populate_client_response(client, decider=user)


@router.post("/approvals/{client_id}/decline", response_model=ClientResponse)
async def decline_client(
    client_id: uuid.UUID,
    request: Request,
    payload: ClientDecisionRequest | None = None,
    user: User = Depends(require_permission(Permissions.CLIENT_APPROVE)),
    db: AsyncSession = Depends(get_db),
):
    """Supervisor/Director declines Client proposal."""
    dec_payload = payload or ClientDecisionRequest()
    reason = dec_payload.reason or dec_payload.notes
    if not reason or not reason.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": {"code": "REASON_REQUIRED", "message": "A reason must be provided when declining a proposal."}},
        )

    repo = ClientRepository(db)
    client = await repo.get(client_id)
    if not client or client.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "CLIENT_NOT_FOUND", "message": "Client record not found"}},
        )

    if client.approval_status != "PENDING_APPROVAL":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": {
                    "code": "INVALID_APPROVAL_TRANSITION",
                    "message": f"Client cannot be declined from '{client.approval_status}' status. Must be PENDING_APPROVAL.",
                }
            },
        )

    now = datetime.now(UTC)
    client.approval_status = "DECLINED"
    client.status = "Declined"
    client.decided_by = user.id
    client.decided_at = now
    client.decision_reason = reason.strip()
    client.updated_by = user.id

    history_entry = ClientApprovalHistory(
        client_id=client.id,
        person_id=client.person_id or client.id,
        action="DECLINED",
        from_status="PENDING_APPROVAL",
        to_status="DECLINED",
        actor_id=user.id,
        notes=reason.strip(),
        created_at=now,
    )
    await repo.add_approval_history(history_entry)

    audit_service = AuditService(db)
    await audit_service.log_event(
        event_type="CLIENT_DECLINED",
        user_id=user.id,
        entity_type="client",
        entity_id=client.id,
        after_data={
            "approval_status": "DECLINED",
            "decision_reason": reason.strip(),
        },
        ip_address=request.client.host if request.client else None,
    )

    timeline_service = TimelineService(db)
    await timeline_service.record_event(
        event_type=TimelineEventType.CLIENT_UPDATED,
        title=f"Client Proposal Declined: {client.first_name} {client.last_name}",
        description=f"Declined: {reason.strip()}",
        entity_type="client",
        entity_id=client.id,
        client_id=client.id,
        created_by=user.id,
    )

    await db.commit()
    return _populate_client_response(client, decider=user)


@router.post("/duplicate-check")
async def duplicate_check(
    body: DuplicateCheckRequest,
    user: User = Depends(require_permission(Permissions.CLIENT_READ)),
    db: AsyncSession = Depends(get_db),
):
    """Check potential duplicate persons before creating a client."""
    service = DuplicateService(db)
    candidates = await service.check_duplicates(
        first_name=body.first_name,
        last_name=body.last_name,
        date_of_birth=body.date_of_birth,
        treaty_number=body.treaty_number,
        health_card_number=body.health_card_number,
        phone=body.phone,
        email=body.email,
    )
    return {"has_potential_duplicates": len(candidates) > 0, "candidates": candidates}


@router.post("/merge")
async def merge_duplicate_persons(
    body: MergeRequest,
    user: User = Depends(require_permission(Permissions.ADMIN_CONFIGURATION_MANAGE)),
    db: AsyncSession = Depends(get_db),
):
    """Perform controlled person merge with audit logging."""
    service = MergeService(db)
    merge_record = await service.merge_persons(
        source_person_id=body.source_person_id,
        target_person_id=body.target_person_id,
        merged_by=user.id,
        reason=body.reason,
        notes=body.notes,
    )
    await db.commit()
    return {"success": True, "merge_id": str(merge_record.id), "merged_at": merge_record.merged_at}


@router.get("/{client_id}")
async def get_client(
    client_id: uuid.UUID,
    request: Request,
    allow_deleted: bool = Query(default=False, description="Allow viewing deleted client from trash if authorized"),
    user: User = Depends(require_permission(Permissions.CLIENT_READ)),
    db: AsyncSession = Depends(get_db),
):
    person_service = PersonService(db)
    await person_service.assert_client_role_authorized(user, "read client")

    stmt = select(Client).where(Client.id == client_id)
    res = await db.execute(stmt)
    client = res.scalar_one_or_none()
    if not client or (client.is_deleted and not allow_deleted):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "CLIENT_NOT_FOUND", "message": "Client not found"}},
        )

    perm_service = PermissionService(db)
    can_access = await perm_service.user_can_access_team(user.id, client.assigned_team_id)
    if not can_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": {
                    "code": "TEAM_ACCESS_DENIED",
                    "message": "Access to this client is restricted to their assigned team",
                }
            },
        )

    # Log sensitive read access event
    audit_service = AuditService(db)
    await audit_service.log_access(
        event_type="CLIENT_PROFILE_VIEWED",
        user_id=user.id,
        entity_type="client",
        entity_id=client.id,
        description=f"Viewed profile of client {client.first_name} {client.last_name}",
        ip_address=request.client.host if request.client else None,
    )
    await db.commit()

    # Load canonical person if linked
    person_data = None
    person_model = None
    if client.person_id:
        person_repo = PersonRepository(db)
        person_model = await person_repo.get_full(client.person_id)
        if person_model:
            person_photo = None
            if person_model.photo_document_id:
                person_photo = generate_signed_file_url(person_model.photo_document_id, expiry_seconds=3600)
            person_data = {
                "id": str(person_model.id),
                "person_id_number": person_model.person_id_number,
                "first_name": person_model.first_name,
                "middle_name": person_model.middle_name,
                "last_name": person_model.last_name,
                "preferred_name": person_model.preferred_name,
                "aliases": person_model.aliases,
                "date_of_birth": str(person_model.date_of_birth) if person_model.date_of_birth else None,
                "gender": person_model.gender,
                "photo_url": person_photo,
                "place_of_birth": person_model.place_of_birth,
                "preferred_language": person_model.preferred_language,
                "languages_spoken": person_model.languages_spoken,
                "treaty_number": person_model.treaty_number,
                "band_nation": person_model.band_nation,
                "indigenous_identity": person_model.indigenous_identity,
                "health_card_number": person_model.health_card_number,
                "phone": person_model.phone,
                "email": person_model.email,
                "emergency_contact_name": person_model.emergency_contact_name,
                "emergency_contact_phone": person_model.emergency_contact_phone,
                "source_of_income": person_model.source_of_income,
                "employment_status": person_model.employment_status,
                "employer": person_model.employer,
                "addresses": [
                    {
                        "id": str(a.id),
                        "address_type": a.address_type,
                        "address_line_1": a.address_line_1,
                        "city": a.city,
                        "province": a.province,
                        "postal_code": a.postal_code,
                        "on_reserve": a.on_reserve,
                        "latitude": a.latitude,
                        "longitude": a.longitude,
                        "is_primary": a.is_primary,
                    }
                    for a in person_model.addresses
                ],
                "physical_description": {
                    "eye_colour": person_model.physical_description.eye_colour,
                    "hair_colour": person_model.physical_description.hair_colour,
                    "height_cm": person_model.physical_description.height_cm,
                    "weight_kg": person_model.physical_description.weight_kg,
                    "tattoos": person_model.physical_description.tattoos,
                    "piercings": person_model.physical_description.piercings,
                    "scars": person_model.physical_description.scars,
                    "glasses": person_model.physical_description.glasses,
                }
                if person_model.physical_description
                else None,
                "cultural_profile": {
                    "cultural_connections": person_model.cultural_profile.cultural_connections,
                    "ceremonies": person_model.cultural_profile.ceremonies,
                    "elders_connected": person_model.cultural_profile.elders_connected,
                    "land_based_activities": person_model.cultural_profile.land_based_activities,
                    "language_goals": person_model.cultural_profile.language_goals,
                }
                if person_model.cultural_profile
                else None,
            }

    data = _populate_client_response(client, person=person_model).model_dump()
    data["person"] = person_data
    return data


@router.post("", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
async def create_client(
    payload: ClientCreate,
    request: Request,
    user: User = Depends(require_permission(Permissions.CLIENT_CREATE)),
    db: AsyncSession = Depends(get_db),
):
    person_service = PersonService(db)
    await person_service.assert_client_role_authorized(user, "create client")

    repo = ClientRepository(db)
    person_repo = PersonRepository(db)
    person_id_number = await person_repo.generate_person_id_number()

    # 1. Create Canonical Person record
    person = await person_repo.create(
        person_id_number=person_id_number,
        first_name=payload.first_name,
        last_name=payload.last_name,
        date_of_birth=payload.date_of_birth,
        gender=payload.gender,
        phone=payload.phone,
        email=payload.email,
        indigenous_identity=payload.indigenous_identity,
        band_nation=payload.band_nation,
        created_by=user.id,
        updated_by=user.id,
    )

    # 2. If address provided, create primary address entry
    if payload.address:
        addr = PersonAddress(
            person_id=person.id,
            address_line_1=payload.address,
            city=payload.city or "Regina",
            province=payload.province or "Saskatchewan",
            is_primary=True,
        )
        db.add(addr)

    # 3. Create Client record linked to person
    valid_cols = {col.name for col in Client.__table__.columns}
    client_data = {k: v for k, v in payload.model_dump().items() if k in valid_cols}
    client_data["person_id"] = person.id
    if not client_data.get("approval_status"):
        client_data["approval_status"] = "APPROVED"
    client_data["created_by"] = user.id
    client_data["updated_by"] = user.id

    client = await repo.create(**client_data)

    # 4. Audit & Timeline
    audit_service = AuditService(db)
    await audit_service.log_event(
        event_type="CLIENT_CREATED",
        user_id=user.id,
        entity_type="client",
        entity_id=client.id,
        after_data=payload.model_dump(mode="json"),
        ip_address=request.client.host if request.client else None,
    )

    timeline_service = TimelineService(db)
    await timeline_service.record_event(
        event_type=TimelineEventType.CLIENT_CREATED,
        title=f"Client Profile Created: {client.first_name} {client.last_name}",
        description=f"Initial registration status: {client.status}, Risk Level: {client.risk_level}",
        entity_type="client",
        entity_id=client.id,
        client_id=client.id,
        created_by=user.id,
    )

    await db.commit()
    return _populate_client_response(client, person=person)


@router.patch("/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: uuid.UUID,
    payload: ClientUpdate,
    request: Request,
    user: User = Depends(require_permission(Permissions.CLIENT_UPDATE)),
    db: AsyncSession = Depends(get_db),
):
    repo = ClientRepository(db)
    client = await repo.get(client_id)
    if not client or client.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "CLIENT_NOT_FOUND", "message": "Client not found"}},
        )

    perm_service = PermissionService(db)
    if not await perm_service.user_can_access_team(user.id, client.assigned_team_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": {"code": "TEAM_ACCESS_DENIED", "message": "Unauthorized to update this client"}},
        )

    before_data = ClientResponse.model_validate(client).model_dump(mode="json")
    valid_cols = {col.name for col in Client.__table__.columns}
    update_data = {k: v for k, v in payload.model_dump(exclude_unset=True).items() if k in valid_cols}
    update_data["updated_by"] = user.id

    updated_client = await repo.update(client, **update_data)

    # Sync demographic changes to canonical Person if linked
    if client.person_id:
        person_repo = PersonRepository(db)
        person = await person_repo.get(client.person_id)
        if person:
            person_fields = [
                "first_name",
                "last_name",
                "date_of_birth",
                "gender",
                "phone",
                "email",
                "indigenous_identity",
                "band_nation",
            ]
            for field in person_fields:
                if field in update_data and update_data[field] is not None:
                    setattr(person, field, update_data[field])

    audit_service = AuditService(db)
    await audit_service.log_event(
        event_type="CLIENT_UPDATED",
        user_id=user.id,
        entity_type="client",
        entity_id=client.id,
        before_data=before_data,
        after_data=update_data,
        ip_address=request.client.host if request.client else None,
    )

    timeline_service = TimelineService(db)
    await timeline_service.record_event(
        event_type=TimelineEventType.CLIENT_UPDATED,
        title=f"Client Profile Updated: {client.first_name} {client.last_name}",
        description="Fields updated: " + ", ".join(update_data.keys()),
        entity_type="client",
        entity_id=client.id,
        client_id=client.id,
        created_by=user.id,
    )

    await db.commit()
    return _populate_client_response(updated_client)


@router.post("/{client_id}/photo")
async def upload_client_photo(
    client_id: uuid.UUID,
    file: UploadFile = File(...),
    user: User = Depends(require_permission(Permissions.CLIENT_UPDATE)),
    db: AsyncSession = Depends(get_db),
):
    """Upload and attach a profile photo to a client and their canonical Person."""
    repo = ClientRepository(db)
    client = await repo.get(client_id)
    if not client or client.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "CLIENT_NOT_FOUND", "message": "Client not found"}},
        )

    perm_service = PermissionService(db)
    if not await perm_service.user_can_access_team(user.id, client.assigned_team_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": {"code": "TEAM_ACCESS_DENIED", "message": "Unauthorized to update this client"}},
        )

    content = await file.read()
    person_service = PersonService(db)

    # Ensure linked canonical person exists
    if not client.person_id:
        person = await person_service.create_person(
            PersonCreate(
                first_name=client.first_name,
                last_name=client.last_name,
                date_of_birth=client.date_of_birth,
                gender=client.gender,
                phone=client.phone,
                email=client.email,
                address=client.address,
                city=client.city,
                province=client.province,
                indigenous_identity=client.indigenous_identity,
                band_nation=client.band_nation,
            ),
            current_user=user,
        )
        client.person_id = person.id
        await repo.update(client, person_id=person.id)

    url = await person_service.upload_photo(
        person_id=client.person_id,
        filename=file.filename or "profile_photo.jpg",
        content=content,
        content_type=file.content_type or "image/jpeg",
        current_user=user,
    )
    await db.commit()
    return {"photo_url": url}


# ── Sub-Resource Routes (Medical, Medications, Providers, Schools, etc.) ──


@router.get("/{client_id}/medical")
async def get_client_medical(
    client_id: uuid.UUID,
    user: User = Depends(require_permission(Permissions.CLIENT_MEDICAL_READ)),
    db: AsyncSession = Depends(get_db),
):
    med_repo = MedicalRepository(db)
    profile = await med_repo.get_or_create_profile(client_id)
    allergies = await med_repo.list_allergies(client_id)
    conditions = await med_repo.list_conditions(client_id)
    medications = await med_repo.list_medications(client_id)

    return {
        "profile": profile,
        "allergies": allergies,
        "conditions": conditions,
        "medications": medications,
    }


@router.patch("/{client_id}/medical")
async def update_client_medical_profile(
    client_id: uuid.UUID,
    payload: MedicalProfileUpdate,
    user: User = Depends(require_permission(Permissions.CLIENT_MEDICAL_WRITE)),
    db: AsyncSession = Depends(get_db),
):
    med_repo = MedicalRepository(db)
    profile = await med_repo.update_profile(client_id, **payload.model_dump(exclude_unset=True))
    await db.commit()
    return profile


@router.post("/{client_id}/allergies", status_code=status.HTTP_201_CREATED)
async def add_client_allergy(
    client_id: uuid.UUID,
    payload: AllergyCreate,
    user: User = Depends(require_permission(Permissions.CLIENT_MEDICAL_WRITE)),
    db: AsyncSession = Depends(get_db),
):
    med_repo = MedicalRepository(db)
    allergy = await med_repo.add_allergy(client_id, **payload.model_dump())
    await db.commit()
    return allergy


@router.post("/{client_id}/conditions", status_code=status.HTTP_201_CREATED)
async def add_client_condition(
    client_id: uuid.UUID,
    payload: ConditionCreate,
    user: User = Depends(require_permission(Permissions.CLIENT_MEDICAL_WRITE)),
    db: AsyncSession = Depends(get_db),
):
    med_repo = MedicalRepository(db)
    condition = await med_repo.add_condition(client_id, **payload.model_dump())
    await db.commit()
    return condition


@router.post("/{client_id}/medications", status_code=status.HTTP_201_CREATED)
async def add_client_medication(
    client_id: uuid.UUID,
    payload: MedicationCreate,
    user: User = Depends(require_permission(Permissions.CLIENT_MEDICAL_WRITE)),
    db: AsyncSession = Depends(get_db),
):
    med_repo = MedicalRepository(db)
    medication = await med_repo.add_medication(client_id, **payload.model_dump())

    timeline = TimelineService(db)
    await timeline.record_event(
        event_type="MEDICATION_STARTED",
        title=f"Medication Prescribed: {medication.medication_name}",
        description=f"Dosage: {medication.dosage}, Frequency: {medication.frequency}",
        entity_type="client",
        entity_id=client_id,
        client_id=client_id,
        created_by=user.id,
    )

    await db.commit()
    return medication


@router.get("/{client_id}/providers")
async def get_client_providers(
    client_id: uuid.UUID,
    user: User = Depends(require_permission(Permissions.PROVIDER_READ)),
    db: AsyncSession = Depends(get_db),
):
    repo = ProviderRepository(db)
    links = await repo.list_client_providers(client_id)
    return links


@router.post("/{client_id}/providers", status_code=status.HTTP_201_CREATED)
async def link_client_provider(
    client_id: uuid.UUID,
    payload: ProviderLinkCreate,
    user: User = Depends(require_permission(Permissions.PROVIDER_WRITE)),
    db: AsyncSession = Depends(get_db),
):
    repo = ProviderRepository(db)
    link = await repo.link_client_provider(
        client_id=client_id,
        provider_id=payload.provider_id,
        role=payload.role,
        notes=payload.notes,
    )
    await db.commit()
    return link


@router.get("/{client_id}/schools")
async def get_client_schools(
    client_id: uuid.UUID,
    user: User = Depends(require_permission(Permissions.CLIENT_SCHOOL_READ)),
    db: AsyncSession = Depends(get_db),
):
    repo = SchoolRepository(db)
    enrolments = await repo.list_client_enrolments(client_id)
    return enrolments


@router.post("/{client_id}/schools", status_code=status.HTTP_201_CREATED)
async def enroll_client_school(
    client_id: uuid.UUID,
    payload: SchoolEnrollmentCreate,
    user: User = Depends(require_permission(Permissions.CLIENT_SCHOOL_WRITE)),
    db: AsyncSession = Depends(get_db),
):
    repo = SchoolRepository(db)
    enrolment = await repo.enroll_client(
        client_id=client_id,
        school_id=payload.school_id,
        grade_level=payload.grade_level,
        start_date=payload.start_date,
        has_iep=payload.has_iep,
        iep_details=payload.iep_details,
        school_contact_person=payload.school_contact_person,
        attendance_concerns=payload.attendance_concerns,
        notes=payload.notes,
    )
    await db.commit()
    return enrolment


@router.get("/{client_id}/timeline")
async def get_client_timeline(
    client_id: uuid.UUID,
    user: User = Depends(require_permission(Permissions.TIMELINE_READ)),
    db: AsyncSession = Depends(get_db),
):
    timeline_service = TimelineService(db)
    events = await timeline_service.get_timeline_for_entity("client", client_id)
    return events


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client(
    client_id: uuid.UUID,
    request: Request,
    user: User = Depends(require_any_permission(Permissions.CLIENT_DELETE, Permissions.CLIENT_UPDATE)),
    db: AsyncSession = Depends(get_db),
):
    """Admin or authorized supervisor/director soft-deletes a client record."""
    repo = ClientRepository(db)
    client = await repo.get(client_id)
    if not client or client.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "CLIENT_NOT_FOUND", "message": "Client record not found"}},
        )

    await repo.soft_delete(client)

    audit_service = AuditService(db)
    await audit_service.log_event(
        event_type="CLIENT_DELETED",
        user_id=user.id,
        entity_type="client",
        entity_id=client.id,
        before_data={"first_name": client.first_name, "last_name": client.last_name, "status": client.status},
        ip_address=request.client.host if request.client else None,
    )

    await db.commit()
    return None


@router.post("/{client_id}/restore", response_model=ClientResponse)
async def restore_client(
    client_id: uuid.UUID,
    request: Request,
    user: User = Depends(require_any_permission(Permissions.CLIENT_DELETE, Permissions.CLIENT_UPDATE)),
    db: AsyncSession = Depends(get_db),
):
    """Restore a soft-deleted client record from the trash back to active service."""
    stmt = select(Client).where(Client.id == client_id)
    res = await db.execute(stmt)
    client = res.scalar_one_or_none()
    if not client or client.deleted_at is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "CLIENT_NOT_IN_TRASH", "message": "Client record is not in trash"}},
        )

    client.deleted_at = None

    audit_service = AuditService(db)
    await audit_service.log_event(
        event_type="CLIENT_RESTORED",
        user_id=user.id,
        entity_type="client",
        entity_id=client.id,
        after_data={"first_name": client.first_name, "last_name": client.last_name, "status": client.status},
        ip_address=request.client.host if request.client else None,
    )

    await db.commit()
    return _populate_client_response(client)


@router.delete("/{client_id}/permanent", status_code=status.HTTP_204_NO_CONTENT)
async def permanently_delete_client(
    client_id: uuid.UUID,
    request: Request,
    user: User = Depends(require_any_permission(Permissions.CLIENT_DELETE, Permissions.CLIENT_UPDATE)),
    db: AsyncSession = Depends(get_db),
):
    """Permanently delete a client record from the trash, purging it completely."""
    stmt = select(Client).where(Client.id == client_id)
    res = await db.execute(stmt)
    client = res.scalar_one_or_none()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "CLIENT_NOT_FOUND", "message": "Client record not found"}},
        )

    audit_service = AuditService(db)
    await audit_service.log_event(
        event_type="CLIENT_PURGED_PERMANENTLY",
        user_id=user.id,
        entity_type="client",
        entity_id=client.id,
        before_data={
            "first_name": client.first_name,
            "last_name": client.last_name,
            "deleted_at": client.deleted_at.isoformat() if client.deleted_at else None,
        },
        ip_address=request.client.host if request.client else None,
    )

    await db.delete(client)
    await db.commit()
    return None


