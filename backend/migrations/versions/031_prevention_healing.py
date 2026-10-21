"""Prevention & Healing Records Workspace — initial schema.

Revision ID: 031_prevention_healing
Revises: 030_backfill_permissions_and_role_mappings
Create Date: 2026-10-21

Tables created:
  - ph_pending_staff_profiles
  - ph_enhancement_programs
  - ph_family_support_records
  - ph_other_nations_support
  - ph_import_batches
  - ph_import_rows
  - ph_client_refs
"""
from __future__ import annotations

import uuid
from decimal import Decimal

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic
revision = "031_prevention_healing"
down_revision = "030_backfill_permissions_and_role_mappings"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── ph_import_batches (referenced by other tables) ────────────────────────
    op.create_table(
        "ph_import_batches",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("uploaded_by_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("original_filename", sa.String(500), nullable=False),
        sa.Column("worksheet_name", sa.String(200), nullable=False),
        sa.Column("file_hash", sa.String(64), nullable=True),
        sa.Column("record_type", sa.String(50), nullable=False),
        sa.Column("total_rows_analyzed", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("valid_rows", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("invalid_rows", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("imported_rows", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(50), nullable=False, server_default="PENDING"),
        sa.Column("approved_by_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_summary", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    op.create_index("ix_ph_import_batches_status", "ph_import_batches", ["status"])
    op.create_index("ix_ph_import_batches_uploaded_by", "ph_import_batches", ["uploaded_by_id"])
    op.create_index("ix_ph_import_batches_file_hash", "ph_import_batches", ["file_hash"])

    # ── ph_pending_staff_profiles ─────────────────────────────────────────────
    op.create_table(
        "ph_pending_staff_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("first_name", sa.String(100), nullable=False),
        sa.Column("last_name", sa.String(100), nullable=False),
        sa.Column("display_name_from_excel", sa.String(255), nullable=False),
        sa.Column("position", sa.String(100), nullable=True),
        sa.Column("department", sa.String(100), nullable=True),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("phone", sa.String(50), nullable=True),
        sa.Column("onboarding_status", sa.String(50), nullable=False, server_default="PENDING"),
        sa.Column("employee_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("employees.id", ondelete="SET NULL"), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("source_batch_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ph_import_batches.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
    )
    op.create_index("ix_ph_pending_staff_display_name", "ph_pending_staff_profiles", ["display_name_from_excel"])
    op.create_index("ix_ph_pending_staff_status", "ph_pending_staff_profiles", ["onboarding_status"])
    op.create_index("ix_ph_pending_staff_employee_id", "ph_pending_staff_profiles", ["employee_id"])
    op.create_index("ix_ph_pending_staff_source_batch_id", "ph_pending_staff_profiles", ["source_batch_id"])

    # ── ph_enhancement_programs ───────────────────────────────────────────────
    op.create_table(
        "ph_enhancement_programs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("employee_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("employees.id", ondelete="SET NULL"), nullable=True),
        sa.Column("pending_staff_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ph_pending_staff_profiles.id", ondelete="SET NULL"), nullable=True),
        sa.Column("employee_name_raw", sa.String(255), nullable=True),
        sa.Column("position_raw", sa.String(100), nullable=True),
        sa.Column("record_date", sa.Date(), nullable=True),
        sa.Column("program", sa.String(200), nullable=False),
        sa.Column("program_activity", sa.String(500), nullable=True),
        sa.Column("date_provided", sa.Date(), nullable=True),
        sa.Column("closing_date", sa.Date(), nullable=True),
        sa.Column("city", sa.String(100), nullable=True),
        sa.Column("province", sa.String(100), nullable=True),
        sa.Column("partners", sa.Text(), nullable=True),
        sa.Column("families_in_province", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("families_out_of_province", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("participants_children_0_12", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("participants_youth_13_17", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("participants_post_majority_18_26", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("participants_parents_caregivers", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("participants_family_members", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("participants_others", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("account_code", sa.String(50), nullable=True),
        sa.Column("subcode", sa.String(50), nullable=True),
        sa.Column("expense_gift_card", sa.Numeric(12, 2), nullable=False, server_default="0.00"),
        sa.Column("expense_purchase_order", sa.Numeric(12, 2), nullable=False, server_default="0.00"),
        sa.Column("expense_eft", sa.Numeric(12, 2), nullable=False, server_default="0.00"),
        sa.Column("expense_cheque", sa.Numeric(12, 2), nullable=False, server_default="0.00"),
        sa.Column("expense_credit_card", sa.Numeric(12, 2), nullable=False, server_default="0.00"),
        sa.Column("expense_courtesy_card", sa.Numeric(12, 2), nullable=False, server_default="0.00"),
        sa.Column("comments", sa.Text(), nullable=True),
        sa.Column("fiscal_year", sa.String(20), nullable=False, server_default="2026-2027"),
        sa.Column("import_batch_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ph_import_batches.id", ondelete="SET NULL"), nullable=True),
        sa.Column("source_row_number", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.CheckConstraint("families_in_province >= 0", name="ck_ep_families_in_province"),
        sa.CheckConstraint("families_out_of_province >= 0", name="ck_ep_families_out_of_province"),
    )
    op.create_index("ix_ph_ep_record_date", "ph_enhancement_programs", ["record_date"])
    op.create_index("ix_ph_ep_fiscal_year", "ph_enhancement_programs", ["fiscal_year"])
    op.create_index("ix_ph_ep_employee_id", "ph_enhancement_programs", ["employee_id"])
    op.create_index("ix_ph_ep_account_code", "ph_enhancement_programs", ["account_code"])

    # ── ph_family_support_records ─────────────────────────────────────────────
    op.create_table(
        "ph_family_support_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("employee_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("employees.id", ondelete="SET NULL"), nullable=True),
        sa.Column("pending_staff_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ph_pending_staff_profiles.id", ondelete="SET NULL"), nullable=True),
        sa.Column("employee_name_raw", sa.String(255), nullable=True),
        sa.Column("position_raw", sa.String(100), nullable=True),
        sa.Column("service_area", sa.String(100), nullable=True),
        sa.Column("record_date", sa.Date(), nullable=True),
        sa.Column("program", sa.String(200), nullable=False),
        sa.Column("support_type", sa.String(200), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("partners", sa.Text(), nullable=True),
        sa.Column("date_provided", sa.Date(), nullable=True),
        sa.Column("person_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("persons.id", ondelete="SET NULL"), nullable=True),
        sa.Column("client_ref_legacy_id", sa.String(50), nullable=True),
        sa.Column("city", sa.String(100), nullable=True),
        sa.Column("province", sa.String(100), nullable=True),
        sa.Column("participants_children_0_12", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("participants_youth_13_17", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("participants_post_majority_18_26", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("participants_adults_18_plus", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("account_code", sa.String(50), nullable=True),
        sa.Column("subcode", sa.String(50), nullable=True),
        sa.Column("project_code", sa.String(50), nullable=True),
        sa.Column("expense_gift_card", sa.Numeric(12, 2), nullable=False, server_default="0.00"),
        sa.Column("expense_purchase_order", sa.Numeric(12, 2), nullable=False, server_default="0.00"),
        sa.Column("expense_eft", sa.Numeric(12, 2), nullable=False, server_default="0.00"),
        sa.Column("expense_cheque", sa.Numeric(12, 2), nullable=False, server_default="0.00"),
        sa.Column("expense_credit_card", sa.Numeric(12, 2), nullable=False, server_default="0.00"),
        sa.Column("expense_petty_cash", sa.Numeric(12, 2), nullable=False, server_default="0.00"),
        sa.Column("expense_courtesy_card", sa.Numeric(12, 2), nullable=False, server_default="0.00"),
        sa.Column("comments", sa.Text(), nullable=True),
        sa.Column("fiscal_year", sa.String(20), nullable=False, server_default="2026-2027"),
        sa.Column("client_match_status", sa.String(50), nullable=False, server_default="UNRESOLVED"),
        sa.Column("import_batch_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ph_import_batches.id", ondelete="SET NULL"), nullable=True),
        sa.Column("source_row_number", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
    )
    op.create_index("ix_ph_fsr_record_date", "ph_family_support_records", ["record_date"])
    op.create_index("ix_ph_fsr_fiscal_year", "ph_family_support_records", ["fiscal_year"])
    op.create_index("ix_ph_fsr_employee_id", "ph_family_support_records", ["employee_id"])
    op.create_index("ix_ph_fsr_person_id", "ph_family_support_records", ["person_id"])
    op.create_index("ix_ph_fsr_client_ref_legacy_id", "ph_family_support_records", ["client_ref_legacy_id"])
    op.create_index("ix_ph_fsr_client_match_status", "ph_family_support_records", ["client_match_status"])
    op.create_index("ix_ph_fsr_account_code", "ph_family_support_records", ["account_code"])

    # ── ph_other_nations_support ──────────────────────────────────────────────
    op.create_table(
        "ph_other_nations_support",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("employee_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("employees.id", ondelete="SET NULL"), nullable=True),
        sa.Column("pending_staff_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ph_pending_staff_profiles.id", ondelete="SET NULL"), nullable=True),
        sa.Column("worker_name_raw", sa.String(255), nullable=True),
        sa.Column("record_date", sa.Date(), nullable=True),
        sa.Column("family_reference_raw", sa.String(255), nullable=True),
        sa.Column("service_type", sa.String(200), nullable=True),
        sa.Column("cost", sa.Numeric(12, 2), nullable=False, server_default="0.00"),
        sa.Column("on_reserve", sa.Boolean(), nullable=True),
        sa.Column("cowessess_connection", sa.String(200), nullable=True),
        sa.Column("other_community", sa.String(200), nullable=True),
        sa.Column("historical_reference_number", sa.String(100), nullable=True),
        sa.Column("comments", sa.Text(), nullable=True),
        sa.Column("person_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("persons.id", ondelete="SET NULL"), nullable=True),
        sa.Column("client_match_status", sa.String(50), nullable=False, server_default="UNRESOLVED"),
        sa.Column("fiscal_year", sa.String(20), nullable=False, server_default="2026-2027"),
        sa.Column("import_batch_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ph_import_batches.id", ondelete="SET NULL"), nullable=True),
        sa.Column("source_row_number", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
    )
    op.create_index("ix_ph_ons_record_date", "ph_other_nations_support", ["record_date"])
    op.create_index("ix_ph_ons_fiscal_year", "ph_other_nations_support", ["fiscal_year"])
    op.create_index("ix_ph_ons_employee_id", "ph_other_nations_support", ["employee_id"])
    op.create_index("ix_ph_ons_person_id", "ph_other_nations_support", ["person_id"])

    # ── ph_import_rows ────────────────────────────────────────────────────────
    op.create_table(
        "ph_import_rows",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("batch_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ph_import_batches.id", ondelete="CASCADE"), nullable=False),
        sa.Column("source_row_number", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="PENDING"),
        sa.Column("validation_errors", sa.Text(), nullable=True),
        sa.Column("imported_record_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("imported_record_type", sa.String(50), nullable=True),
        sa.Column("employee_name_raw", sa.String(255), nullable=True),
        sa.Column("employee_match_status", sa.String(50), nullable=False, server_default="UNRESOLVED"),
        sa.Column("resolved_employee_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("employees.id", ondelete="SET NULL"), nullable=True),
        sa.Column("resolved_pending_staff_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ph_pending_staff_profiles.id", ondelete="SET NULL"), nullable=True),
        sa.Column("client_ref_raw", sa.String(100), nullable=True),
        sa.Column("client_match_status", sa.String(50), nullable=False, server_default="UNRESOLVED"),
        sa.Column("resolved_person_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("persons.id", ondelete="SET NULL"), nullable=True),
        sa.Column("row_data", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    op.create_index("ix_ph_import_rows_batch_status", "ph_import_rows", ["batch_id", "status"])
    op.create_index("ix_ph_import_rows_employee_match", "ph_import_rows", ["employee_match_status"])
    op.create_index("ix_ph_import_rows_client_match", "ph_import_rows", ["client_match_status"])

    # ── ph_client_refs ────────────────────────────────────────────────────────
    op.create_table(
        "ph_client_refs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("legacy_id", sa.String(100), nullable=False),
        sa.Column("legacy_id_type", sa.String(50), nullable=False, server_default="REDMANE"),
        sa.Column("person_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("persons.id", ondelete="SET NULL"), nullable=True),
        sa.Column("confirmed_by_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("confirmed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="UNRESOLVED"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    op.create_index("ix_ph_client_refs_legacy_id_type", "ph_client_refs", ["legacy_id", "legacy_id_type"], unique=True)
    op.create_index("ix_ph_client_refs_status", "ph_client_refs", ["status"])
    op.create_index("ix_ph_client_refs_person_id", "ph_client_refs", ["person_id"])


def downgrade() -> None:
    op.drop_table("ph_client_refs")
    op.drop_table("ph_import_rows")
    op.drop_table("ph_other_nations_support")
    op.drop_table("ph_family_support_records")
    op.drop_table("ph_enhancement_programs")
    op.drop_table("ph_pending_staff_profiles")
    op.drop_table("ph_import_batches")
