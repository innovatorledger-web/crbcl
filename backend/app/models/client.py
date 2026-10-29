"""Client model — individuals receiving services linked to canonical Person."""

from __future__ import annotations

import uuid
from datetime import UTC, date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Index, String, Text, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import AuditMixin, Base, SoftDeleteMixin


class Client(Base, AuditMixin, SoftDeleteMixin):
    __tablename__ = "clients"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    person_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("persons.id", ondelete="SET NULL"), nullable=True, index=True
    )
    first_name: Mapped[str] = mapped_column(String(200), nullable=False)
    last_name: Mapped[str] = mapped_column(String(200), nullable=False)
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    gender: Mapped[str | None] = mapped_column(String(50), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="Pending Intake", nullable=False)
    risk_level: Mapped[str] = mapped_column(String(20), default="Low", nullable=False)

    # Durable Approval Lifecycle
    approval_status: Mapped[str] = mapped_column(
        String(50), default="APPROVED", nullable=False, index=True
    )  # PENDING_APPROVAL, APPROVED, RETURNED, DECLINED
    submitted_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    submission_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    decided_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    decision_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    email: Mapped[str | None] = mapped_column(String(320), nullable=True)
    address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    city: Mapped[str | None] = mapped_column(String(200), nullable=True)
    province: Mapped[str] = mapped_column(String(100), default="Saskatchewan", nullable=False)

    indigenous_identity: Mapped[str | None] = mapped_column(String(100), nullable=True)
    band_nation: Mapped[str | None] = mapped_column(String(200), nullable=True)

    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Team assignment for scoped access
    assigned_team_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True, index=True)

    # Relationships
    person: Mapped[Person | None] = relationship("Person", lazy="selectin")  # noqa: F821
    submitter: Mapped[User | None] = relationship("User", foreign_keys=[submitted_by], lazy="selectin")  # noqa: F821
    decider: Mapped[User | None] = relationship("User", foreign_keys=[decided_by], lazy="selectin")  # noqa: F821
    approval_history: Mapped[list[ClientApprovalHistory]] = relationship(
        "ClientApprovalHistory",
        back_populates="client",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
        order_by="ClientApprovalHistory.created_at.desc()",
    )
    medical_profile: Mapped[ClientMedicalProfile | None] = relationship(  # noqa: F821
        "ClientMedicalProfile",
        back_populates=None,
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )
    allergies: Mapped[list[ClientAllergy]] = relationship(  # noqa: F821
        "ClientAllergy", cascade="all, delete-orphan", passive_deletes=True, lazy="selectin"
    )
    conditions: Mapped[list[ClientMedicalCondition]] = relationship(  # noqa: F821
        "ClientMedicalCondition", cascade="all, delete-orphan", passive_deletes=True, lazy="selectin"
    )
    medications: Mapped[list[ClientMedication]] = relationship(  # noqa: F821
        "ClientMedication", cascade="all, delete-orphan", passive_deletes=True, lazy="selectin"
    )
    providers: Mapped[list[ClientProvider]] = relationship(  # noqa: F821
        "ClientProvider", cascade="all, delete-orphan", passive_deletes=True, lazy="selectin"
    )
    school_enrolments: Mapped[list[ClientSchoolEnrolment]] = relationship(  # noqa: F821
        "ClientSchoolEnrolment", cascade="all, delete-orphan", passive_deletes=True, lazy="selectin"
    )

    __table_args__ = (
        Index("ix_clients_name_trgm", "first_name", "last_name"),
        Index("ix_clients_status", "status"),
        Index("ix_clients_risk_level", "risk_level"),
        Index(
            "uq_clients_person_active_pending",
            "person_id",
            unique=True,
            postgresql_where=text("deleted_at IS NULL AND approval_status IN ('PENDING_APPROVAL', 'APPROVED')"),
            sqlite_where=text("deleted_at IS NULL AND approval_status IN ('PENDING_APPROVAL', 'APPROVED')"),
        ),
    )


class ClientApprovalHistory(Base):
    """Append-only audit trail for client lifecycle submission and approval decisions."""

    __tablename__ = "client_approvals"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("clients.id", ondelete="CASCADE"), nullable=False, index=True
    )
    person_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("persons.id", ondelete="CASCADE"), nullable=False, index=True
    )
    action: Mapped[str] = mapped_column(String(50), nullable=False)  # SUBMITTED, APPROVED, RETURNED, DECLINED
    from_status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    to_status: Mapped[str] = mapped_column(String(50), nullable=False)
    actor_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), server_default=func.now(), nullable=False
    )

    client: Mapped[Client] = relationship("Client", back_populates="approval_history")
    person: Mapped[Person] = relationship("Person", lazy="selectin")  # noqa: F821
    actor: Mapped[User | None] = relationship("User", foreign_keys=[actor_id], lazy="selectin")  # noqa: F821
