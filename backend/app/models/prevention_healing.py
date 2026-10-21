"""Prevention & Healing Records Workspace — SQLAlchemy models.

Covers:
  - PendingStaffProfile   — staff identified from Excel but not yet onboarded
  - EnhancementProgram    — program events recorded by P&H workers
  - FamilySupportRecord   — family support service records
  - OtherNationsSupport   — Eagle Nest / Other Nations support records
  - PHImportBatch         — tracks each Excel import attempt
  - PHImportRow           — per-row import ledger with reconciliation status
  - PHClientRef           — legacy identifier ↔ canonical Person link
"""

from __future__ import annotations

import uuid
from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import AuditMixin, Base, TimestampMixin


# ---------------------------------------------------------------------------
# 1.  Pending Staff Onboarding Profile
# ---------------------------------------------------------------------------

class PendingStaffProfile(Base, AuditMixin):
    """Staff member identified from Excel data who has not yet been fully onboarded.

    Intentionally kept separate from Employee until all required information
    (especially a valid email address) is confirmed and an authorized admin
    creates the canonical Employee + User account.
    """

    __tablename__ = "ph_pending_staff_profiles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Core identity
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    display_name_from_excel: Mapped[str] = mapped_column(String(255), nullable=False)
    position: Mapped[str | None] = mapped_column(String(100), nullable=True)
    department: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Contact — may be absent
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Onboarding state
    onboarding_status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="PENDING"
    )  # PENDING, EMAIL_NEEDED, VERIFIED, REJECTED, MERGED

    # Link to canonical Employee once created
    employee_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("employees.id", ondelete="SET NULL"), nullable=True, index=True
    )

    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_batch_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ph_import_batches.id", ondelete="SET NULL"), nullable=True, index=True
    )

    employee = relationship("Employee", foreign_keys=[employee_id], lazy="joined")

    __table_args__ = (
        Index("ix_ph_pending_staff_display_name", "display_name_from_excel"),
        Index("ix_ph_pending_staff_status", "onboarding_status"),
    )


# ---------------------------------------------------------------------------
# 2.  Enhancement Programs
# ---------------------------------------------------------------------------

class EnhancementProgram(Base, AuditMixin):
    """A single program event or activity record from the Enhancement Programs sheet."""

    __tablename__ = "ph_enhancement_programs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Employee attribution
    employee_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("employees.id", ondelete="SET NULL"), nullable=True, index=True
    )
    pending_staff_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ph_pending_staff_profiles.id", ondelete="SET NULL"), nullable=True
    )
    employee_name_raw: Mapped[str | None] = mapped_column(String(255), nullable=True)  # preserved from import
    position_raw: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Program details
    record_date: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    program: Mapped[str] = mapped_column(String(200), nullable=False)
    program_activity: Mapped[str | None] = mapped_column(String(500), nullable=True)
    date_provided: Mapped[date | None] = mapped_column(Date, nullable=True)
    closing_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    province: Mapped[str | None] = mapped_column(String(100), nullable=True)
    partners: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Family / participant counts
    families_in_province: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    families_out_of_province: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    # total_families is computed: families_in_province + families_out_of_province

    participants_children_0_12: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    participants_youth_13_17: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    participants_post_majority_18_26: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    participants_parents_caregivers: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    participants_family_members: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    participants_others: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    # total_participants is computed

    # Financial coding
    account_code: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    subcode: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Expense breakdown (decimal-safe)
    expense_gift_card: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    expense_purchase_order: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    expense_eft: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    expense_cheque: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    expense_credit_card: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    expense_courtesy_card: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    # total_cost is computed: sum of all expense_* columns

    comments: Mapped[str | None] = mapped_column(Text, nullable=True)
    fiscal_year: Mapped[str] = mapped_column(String(20), nullable=False, default="2026-2027", index=True)

    # Import audit
    import_batch_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ph_import_batches.id", ondelete="SET NULL"), nullable=True, index=True
    )
    source_row_number: Mapped[int | None] = mapped_column(Integer, nullable=True)

    employee = relationship("Employee", foreign_keys=[employee_id], lazy="joined")
    pending_staff = relationship("PendingStaffProfile", foreign_keys=[pending_staff_id], lazy="joined")

    __table_args__ = (
        CheckConstraint("families_in_province >= 0", name="ck_ep_families_in_province"),
        CheckConstraint("families_out_of_province >= 0", name="ck_ep_families_out_of_province"),
    )

    @property
    def total_families(self) -> int:
        return self.families_in_province + self.families_out_of_province

    @property
    def total_participants(self) -> int:
        return (
            self.participants_children_0_12
            + self.participants_youth_13_17
            + self.participants_post_majority_18_26
            + self.participants_parents_caregivers
            + self.participants_family_members
            + self.participants_others
        )

    @property
    def total_cost(self) -> Decimal:
        return (
            self.expense_gift_card
            + self.expense_purchase_order
            + self.expense_eft
            + self.expense_cheque
            + self.expense_credit_card
            + self.expense_courtesy_card
        )


# ---------------------------------------------------------------------------
# 3.  Family Support Records
# ---------------------------------------------------------------------------

class FamilySupportRecord(Base, AuditMixin):
    """A family support service event from the Family Support sheet."""

    __tablename__ = "ph_family_support_records"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Employee attribution
    employee_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("employees.id", ondelete="SET NULL"), nullable=True, index=True
    )
    pending_staff_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ph_pending_staff_profiles.id", ondelete="SET NULL"), nullable=True
    )
    employee_name_raw: Mapped[str | None] = mapped_column(String(255), nullable=True)
    position_raw: Mapped[str | None] = mapped_column(String(100), nullable=True)
    service_area: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Support details
    record_date: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    program: Mapped[str] = mapped_column(String(200), nullable=False)
    support_type: Mapped[str | None] = mapped_column(String(200), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    partners: Mapped[str | None] = mapped_column(Text, nullable=True)
    date_provided: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Client / family reference — linked to canonical Person where confirmed
    person_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("persons.id", ondelete="SET NULL"), nullable=True, index=True
    )
    client_ref_legacy_id: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    province: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Participant counts
    participants_children_0_12: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    participants_youth_13_17: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    participants_post_majority_18_26: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    participants_adults_18_plus: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Financial coding
    account_code: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    subcode: Mapped[str | None] = mapped_column(String(50), nullable=True)
    project_code: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Expense breakdown
    expense_gift_card: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    expense_purchase_order: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    expense_eft: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    expense_cheque: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    expense_credit_card: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    expense_petty_cash: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    expense_courtesy_card: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("0.00"))

    comments: Mapped[str | None] = mapped_column(Text, nullable=True)
    fiscal_year: Mapped[str] = mapped_column(String(20), nullable=False, default="2026-2027", index=True)

    # Client reconciliation status
    client_match_status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="UNRESOLVED", index=True
    )  # UNRESOLVED, MATCHED, CONFIRMED, NO_MATCH

    # Import audit
    import_batch_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ph_import_batches.id", ondelete="SET NULL"), nullable=True, index=True
    )
    source_row_number: Mapped[int | None] = mapped_column(Integer, nullable=True)

    employee = relationship("Employee", foreign_keys=[employee_id], lazy="joined")
    pending_staff = relationship("PendingStaffProfile", foreign_keys=[pending_staff_id], lazy="joined")
    person = relationship("Person", foreign_keys=[person_id], lazy="joined")


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


# ---------------------------------------------------------------------------
# 4.  Other Nations Support (Eagle Nest)
# ---------------------------------------------------------------------------

class OtherNationsSupport(Base, AuditMixin):
    """Eagle Nest / Other Nations support record from the secondary tracker."""

    __tablename__ = "ph_other_nations_support"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Worker attribution
    employee_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("employees.id", ondelete="SET NULL"), nullable=True, index=True
    )
    pending_staff_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ph_pending_staff_profiles.id", ondelete="SET NULL"), nullable=True
    )
    worker_name_raw: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Record
    record_date: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    family_reference_raw: Mapped[str | None] = mapped_column(String(255), nullable=True)
    service_type: Mapped[str | None] = mapped_column(String(200), nullable=True)
    cost: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("0.00"))

    # Community / jurisdiction
    on_reserve: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    cowessess_connection: Mapped[str | None] = mapped_column(String(200), nullable=True)
    other_community: Mapped[str | None] = mapped_column(String(200), nullable=True)
    historical_reference_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    comments: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Client link (optional, confirmed)
    person_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("persons.id", ondelete="SET NULL"), nullable=True, index=True
    )
    client_match_status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="UNRESOLVED", index=True
    )

    fiscal_year: Mapped[str] = mapped_column(String(20), nullable=False, default="2026-2027", index=True)

    # Import audit
    import_batch_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ph_import_batches.id", ondelete="SET NULL"), nullable=True, index=True
    )
    source_row_number: Mapped[int | None] = mapped_column(Integer, nullable=True)

    employee = relationship("Employee", foreign_keys=[employee_id], lazy="joined")
    pending_staff = relationship("PendingStaffProfile", foreign_keys=[pending_staff_id], lazy="joined")
    person = relationship("Person", foreign_keys=[person_id], lazy="joined")

    # End of OtherNationsSupport


# ---------------------------------------------------------------------------
# 5.  Excel Import Batch
# ---------------------------------------------------------------------------

class PHImportBatch(Base, TimestampMixin):
    """Tracks a single Excel import attempt — workbook-level audit."""

    __tablename__ = "ph_import_batches"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    uploaded_by_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    original_filename: Mapped[str] = mapped_column(String(500), nullable=False)
    worksheet_name: Mapped[str] = mapped_column(String(200), nullable=False)
    record_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # ENHANCEMENT_PROGRAMS | FAMILY_SUPPORT | OTHER_NATIONS

    # Counts
    total_rows_analyzed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    valid_rows: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    invalid_rows: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    imported_rows: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="PENDING", index=True
    )  # PENDING | ANALYZING | VALIDATED | AWAITING_APPROVAL | APPROVED | IMPORTING | COMPLETED | FAILED | CANCELLED

    approved_by_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    uploaded_by = relationship("User", foreign_keys=[uploaded_by_id], lazy="joined")
    approved_by = relationship("User", foreign_keys=[approved_by_id], lazy="joined")
    rows = relationship("PHImportRow", back_populates="batch", cascade="all, delete-orphan", lazy="noload")


# ---------------------------------------------------------------------------
# 6.  Import Row Ledger
# ---------------------------------------------------------------------------

class PHImportRow(Base, TimestampMixin):
    """Per-row import audit ledger entry."""

    __tablename__ = "ph_import_rows"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    batch_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ph_import_batches.id", ondelete="CASCADE"), nullable=False, index=True
    )
    source_row_number: Mapped[int] = mapped_column(Integer, nullable=False)

    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="PENDING", index=True
    )  # PENDING | VALID | INVALID | IMPORTED | SKIPPED | ERROR

    validation_errors: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Resolved IDs (set after import)
    imported_record_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    imported_record_type: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Employee reconciliation
    employee_name_raw: Mapped[str | None] = mapped_column(String(255), nullable=True)
    employee_match_status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="UNRESOLVED"
    )  # UNRESOLVED | MATCHED | CONFIRMED | AMBIGUOUS | NO_MATCH
    resolved_employee_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("employees.id", ondelete="SET NULL"), nullable=True
    )
    resolved_pending_staff_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ph_pending_staff_profiles.id", ondelete="SET NULL"), nullable=True
    )

    # Client reconciliation
    client_ref_raw: Mapped[str | None] = mapped_column(String(100), nullable=True)
    client_match_status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="UNRESOLVED"
    )  # UNRESOLVED | MATCHED | CONFIRMED | NO_MATCH
    resolved_person_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("persons.id", ondelete="SET NULL"), nullable=True
    )
    row_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    batch = relationship("PHImportBatch", back_populates="rows")

    __table_args__ = (
        Index("ix_ph_import_rows_batch_status", "batch_id", "status"),
        Index("ix_ph_import_rows_employee_match", "employee_match_status"),
        Index("ix_ph_import_rows_client_match", "client_match_status"),
    )


# ---------------------------------------------------------------------------
# 7.  Legacy Client Reference (reconciliation registry)
# ---------------------------------------------------------------------------

class PHClientRef(Base, TimestampMixin):
    """Maps a legacy identifier (e.g. RedMane ID) to a canonical CRBCL Person.

    Only populated after an authorized administrator confirms the link.
    """

    __tablename__ = "ph_client_refs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    legacy_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    legacy_id_type: Mapped[str] = mapped_column(String(50), nullable=False, default="REDMANE")
    person_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("persons.id", ondelete="SET NULL"), nullable=True, index=True
    )
    confirmed_by_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="UNRESOLVED", index=True
    )  # UNRESOLVED | CONFIRMED | REJECTED | DUPLICATE

    person = relationship("Person", foreign_keys=[person_id], lazy="joined")
    confirmed_by = relationship("User", foreign_keys=[confirmed_by_id], lazy="joined")

    __table_args__ = (
        Index("ix_ph_client_refs_legacy_id_type", "legacy_id", "legacy_id_type", unique=True),
    )
