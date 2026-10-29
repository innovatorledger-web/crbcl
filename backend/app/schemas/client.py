"""Client schemas matching the CRBCL case management platform."""

from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, EmailStr, Field, model_validator

from app.schemas.person import PersonCreate


class ClientBase(BaseModel):
    first_name: str = Field(min_length=1, max_length=200)
    last_name: str = Field(min_length=1, max_length=200)
    date_of_birth: date | None = None
    gender: str | None = None
    status: str = Field(default="Pending Intake", max_length=50)
    risk_level: str = Field(default="Low", max_length=20)
    phone: str | None = None
    email: EmailStr | str | None = None
    address: str | None = None
    city: str | None = None
    province: str = Field(default="Saskatchewan", max_length=100)
    indigenous_identity: str | None = None
    band_nation: str | None = None
    assigned_team_id: uuid.UUID | None = None
    primary_worker_id: uuid.UUID | None = None
    family_id: uuid.UUID | None = None
    notes: str | None = None


class ClientCreate(ClientBase):
    pass


class ClientUpdate(BaseModel):
    first_name: str | None = Field(default=None, min_length=1, max_length=200)
    last_name: str | None = Field(default=None, min_length=1, max_length=200)
    date_of_birth: date | None = None
    gender: str | None = None
    status: str | None = Field(default=None, max_length=50)
    risk_level: str | None = Field(default=None, max_length=20)
    phone: str | None = None
    email: EmailStr | str | None = None
    address: str | None = None
    city: str | None = None
    province: str | None = Field(default=None, max_length=100)
    indigenous_identity: str | None = None
    band_nation: str | None = None
    assigned_team_id: uuid.UUID | None = None
    primary_worker_id: uuid.UUID | None = None
    family_id: uuid.UUID | None = None
    notes: str | None = None


class ClientResponse(ClientBase):
    id: uuid.UUID
    person_id: uuid.UUID | None = None
    person_id_number: str | None = None
    photo_url: str | None = None
    approval_status: str = "PENDING_APPROVAL"
    submitted_by: uuid.UUID | None = None
    submitted_by_name: str | None = None
    submitted_at: datetime | None = None
    submission_notes: str | None = None
    decided_by: uuid.UUID | None = None
    decided_by_name: str | None = None
    decided_at: datetime | None = None
    decision_reason: str | None = None
    is_deleted: bool = False
    deleted_at: datetime | None = None
    days_until_purge: int | None = None

    created_at: datetime
    updated_at: datetime
    created_by: uuid.UUID | None = None
    updated_by: uuid.UUID | None = None
    version: int = 1

    # Compatibility alias for frontend that expects created_date
    @property
    def created_date(self) -> str:
        return self.created_at.isoformat()

    model_config = {"from_attributes": True}


# ── Approval Workflow Schemas ──────────────────────────────────────────


class ClientSubmitExistingRequest(BaseModel):
    """Payload to propose an existing canonical Person as a Client."""

    person_id: uuid.UUID
    submission_notes: str | None = None
    risk_level: str = "Low"
    assigned_team_id: uuid.UUID | None = None


class ClientSubmitNewRequest(BaseModel):
    """Payload to create a new canonical Person and propose as a Client in unified flow."""

    person: PersonCreate
    submission_notes: str | None = None
    risk_level: str = "Low"
    assigned_team_id: uuid.UUID | None = None

    @model_validator(mode="before")
    @classmethod
    def assemble_person(cls, data: Any) -> Any:
        if isinstance(data, dict) and "person" not in data:
            person_fields = {
                k: v for k, v in data.items()
                if k not in ("submission_notes", "risk_level", "assigned_team_id")
            }
            client_fields = {
                k: v for k, v in data.items()
                if k in ("submission_notes", "risk_level", "assigned_team_id")
            }
            client_fields["person"] = person_fields
            return client_fields
        return data


class ClientDecisionRequest(BaseModel):
    """Payload for supervisor/director decision on client proposal."""

    reason: str | None = None
    notes: str | None = None


class ClientApprovalHistoryResponse(BaseModel):
    """Historical audit entry for client proposal lifecycle transitions."""

    id: uuid.UUID
    client_id: uuid.UUID
    person_id: uuid.UUID
    action: str
    from_status: str | None = None
    to_status: str
    actor_id: uuid.UUID | None = None
    actor_name: str | None = None
    notes: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ClientApprovalItemResponse(BaseModel):
    """Dashboard item schema for pending client approval queue."""

    client_id: uuid.UUID
    person_id: uuid.UUID
    person_id_number: str
    first_name: str
    middle_name: str | None = None
    last_name: str
    preferred_name: str | None = None
    date_of_birth: date | None = None
    gender: str | None = None
    photo_url: str | None = None
    band_nation: str | None = None
    city: str | None = None
    province: str | None = None
    risk_level: str
    approval_status: str
    submitted_by: uuid.UUID | None = None
    submitted_by_name: str | None = None
    submitted_at: datetime | None = None
    submission_notes: str | None = None

    model_config = {"from_attributes": True}


class ClientReviewResponse(BaseModel):
    """Comprehensive client review payload for supervisor/director decision."""

    client: ClientResponse
    person: dict[str, Any]
    approval_history: list[ClientApprovalHistoryResponse]
