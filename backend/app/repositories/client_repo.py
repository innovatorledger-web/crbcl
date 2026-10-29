"""Client repository with trigram text search, team scoping, and approval workflow queries."""

from __future__ import annotations

import uuid

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.client import Client, ClientApprovalHistory
from app.models.person import Person
from app.repositories.base import BaseRepository


class ClientRepository(BaseRepository[Client]):
    def __init__(self, db: AsyncSession):
        super().__init__(Client, db)

    async def search(
        self,
        query_text: str | None = None,
        status: str | None = None,
        approval_status: str | None = None,
        risk_level: str | None = None,
        team_id: uuid.UUID | None = None,
        accessible_team_ids: set[uuid.UUID] | None = None,
        offset: int = 0,
        limit: int = 50,
        sort_by: str | None = None,
        trash: bool = False,
    ) -> tuple[list[Client], int]:
        """Search clients with team access scoping, approval status filter, text search, and trash filter."""
        if trash:
            query = select(Client).where(Client.deleted_at.is_not(None))
        else:
            query = select(Client).where(Client.deleted_at.is_(None))

        # Team scoping: if accessible_team_ids is provided, restrict to those teams or unassigned
        if accessible_team_ids is not None:
            query = query.where(
                or_(
                    Client.assigned_team_id.in_(accessible_team_ids),
                    Client.assigned_team_id.is_(None),
                )
            )

        if team_id is not None:
            query = query.where(Client.assigned_team_id == team_id)

        if status:
            query = query.where(Client.status == status)

        if approval_status:
            query = query.where(Client.approval_status == approval_status)

        if risk_level:
            query = query.where(Client.risk_level == risk_level)

        if query_text:
            search_pattern = f"%{query_text}%"
            # Also allow searching by linked person's numeric ID or aliases
            query = query.outerjoin(Person, Client.person_id == Person.id).where(
                or_(
                    Client.first_name.ilike(search_pattern),
                    Client.last_name.ilike(search_pattern),
                    Client.email.ilike(search_pattern),
                    Client.phone.ilike(search_pattern),
                    Client.band_nation.ilike(search_pattern),
                    Person.person_id_number.ilike(search_pattern),
                    Person.preferred_name.ilike(search_pattern),
                    Person.aliases.ilike(search_pattern),
                )
            )

        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.db.execute(count_query)).scalar_one()

        if sort_by:
            is_desc = sort_by.startswith("-")
            field = sort_by[1:] if is_desc else sort_by
            if hasattr(Client, field):
                col = getattr(Client, field)
                query = query.order_by(col.desc() if is_desc else col.asc())
        else:
            query = query.order_by(Client.created_at.desc())

        query = query.offset(offset).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all()), total

    async def get_by_person_id(self, person_id: uuid.UUID) -> Client | None:
        """Find active/pending client context linked to a canonical Person."""
        stmt = (
            select(Client)
            .where(Client.person_id == person_id, Client.deleted_at.is_(None))
            .order_by(Client.created_at.desc())
        )
        res = await self.db.execute(stmt)
        return res.scalars().first()

    async def get_pending_approvals(
        self,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[list[Client], int]:
        """Fetch all client submissions currently awaiting supervisor/director review."""
        query = (
            select(Client)
            .options(
                selectinload(Client.person),
                selectinload(Client.submitter),
            )
            .where(
                Client.approval_status == "PENDING_APPROVAL",
                Client.deleted_at.is_(None),
            )
        )

        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.db.execute(count_query)).scalar_one()

        query = query.order_by(Client.submitted_at.desc().nullslast(), Client.created_at.desc()).offset(offset).limit(limit)
        res = await self.db.execute(query)
        return list(res.scalars().all()), total

    async def add_approval_history(self, history_entry: ClientApprovalHistory) -> None:
        """Append an immutable audit entry for client proposal lifecycle transition."""
        self.db.add(history_entry)
        await self.db.flush()

    async def get_approval_history(self, client_id: uuid.UUID) -> list[ClientApprovalHistory]:
        """Fetch complete chronological decision history for a client."""
        stmt = (
            select(ClientApprovalHistory)
            .options(selectinload(ClientApprovalHistory.actor))
            .where(ClientApprovalHistory.client_id == client_id)
            .order_by(ClientApprovalHistory.created_at.desc())
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def get_status_counts(
        self,
        accessible_team_ids: set[uuid.UUID] | None = None,
    ) -> dict[str, int]:
        """Return counts for All, Approved, Pending, Returned, and Trash tabs."""
        base = select(Client)
        if accessible_team_ids is not None:
            base = base.where(
                or_(
                    Client.assigned_team_id.in_(accessible_team_ids),
                    Client.assigned_team_id.is_(None),
                )
            )

        all_q = select(func.count()).select_from(base.where(Client.deleted_at.is_(None)).subquery())
        approved_q = select(func.count()).select_from(base.where(Client.deleted_at.is_(None), Client.approval_status == "APPROVED").subquery())
        pending_q = select(func.count()).select_from(base.where(Client.deleted_at.is_(None), Client.approval_status == "PENDING_APPROVAL").subquery())
        returned_q = select(func.count()).select_from(base.where(Client.deleted_at.is_(None), Client.approval_status == "RETURNED").subquery())
        trash_q = select(func.count()).select_from(base.where(Client.deleted_at.is_not(None)).subquery())

        all_c = (await self.db.execute(all_q)).scalar_one()
        approved_c = (await self.db.execute(approved_q)).scalar_one()
        pending_c = (await self.db.execute(pending_q)).scalar_one()
        returned_c = (await self.db.execute(returned_q)).scalar_one()
        trash_c = (await self.db.execute(trash_q)).scalar_one()

        return {
            "all": all_c,
            "approved": approved_c,
            "pending": pending_c,
            "returned": returned_c,
            "trash": trash_c,
        }
