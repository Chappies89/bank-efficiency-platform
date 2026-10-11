"""Concrete repository implementations backed by PostgreSQL."""

from __future__ import annotations

from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.application.interfaces.dea_repository import DEARepository
from src.domain.entities.branch import Branch
from src.domain.entities.branch_observation import BranchObservation
from src.domain.value_objects.efficiency_score import EfficiencyScore
from src.infrastructure.database.models import (
    BranchModel,
    BranchObservationModel,
    DEAResultModel,
)


class PostgresBranchRepository:
    """Persists and retrieves Branch and BranchObservation entities."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def save_branch(self, branch: Branch) -> None:
        model = BranchModel(
            branch_id=branch.branch_id,
            branch_name=branch.branch_name,
            region=branch.region,
            opened_date=branch.opened_date,
            square_meters=branch.square_meters,
        )
        self._session.merge(model)

    def save_observation(self, observation: BranchObservation) -> None:
        model = BranchObservationModel(
            branch_id=observation.branch_id,
            observation_date=observation.observation_date,
            fte_count=observation.fte_count,
            operational_expense=observation.operational_expense,
            deposit_volume=observation.deposit_volume,
            loan_volume=observation.loan_volume,
            new_accounts=observation.new_accounts,
            digital_transaction_ratio=observation.digital_transaction_ratio,
        )
        self._session.add(model)

    def get_observations_for_date(self, observation_date: date) -> list[BranchObservation]:
        stmt = select(BranchObservationModel).where(
            BranchObservationModel.observation_date == observation_date
        )
        rows = self._session.execute(stmt).scalars().all()
        return [
            BranchObservation(
                branch_id=r.branch_id,
                observation_date=r.observation_date,
                fte_count=r.fte_count,
                operational_expense=r.operational_expense,
                deposit_volume=r.deposit_volume,
                loan_volume=r.loan_volume,
                new_accounts=r.new_accounts,
                digital_transaction_ratio=r.digital_transaction_ratio,
            )
            for r in rows
        ]


class PostgresDEARepository(DEARepository):
    """PostgreSQL implementation of the DEA repository interface."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def save_score(
        self,
        branch_id: int,
        score: EfficiencyScore,
        observation_date: date,
    ) -> None:
        model = DEAResultModel(
            branch_id=branch_id,
            observation_date=observation_date,
            efficiency_score=score.value,
        )
        self._session.add(model)

    def get_score(self, branch_id: int) -> EfficiencyScore | None:
        stmt = (
            select(DEAResultModel)
            .where(DEAResultModel.branch_id == branch_id)
            .order_by(DEAResultModel.observation_date.desc())
            .limit(1)
        )
        row = self._session.execute(stmt).scalar_one_or_none()
        return EfficiencyScore(row.efficiency_score) if row else None
