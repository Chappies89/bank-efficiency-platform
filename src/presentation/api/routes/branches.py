"""Branch and efficiency endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.infrastructure.database.dependencies import get_session
from src.infrastructure.database.models import (
    BranchModel,
    DEAResultModel,
)
from src.presentation.api.schemas import (
    BranchResponse,
    EfficiencyResponse,
)

router = APIRouter(prefix="/api/branches", tags=["branches"])


@router.get("", response_model=list[BranchResponse])
def list_branches(
    session: Session = Depends(get_session),
) -> list[BranchResponse]:
    """List all branches."""
    stmt = select(BranchModel).order_by(BranchModel.branch_id)
    rows = session.execute(stmt).scalars().all()
    return [
        BranchResponse(
            branch_id=r.branch_id,
            branch_name=r.branch_name,
            region=r.region,
            opened_date=r.opened_date,
            square_meters=r.square_meters,
        )
        for r in rows
    ]


@router.get("/{branch_id}/efficiency", response_model=EfficiencyResponse)
def get_latest_efficiency(
    branch_id: int,
    session: Session = Depends(get_session),
) -> EfficiencyResponse:
    """Get the most recent efficiency score for a branch."""
    stmt = (
        select(DEAResultModel)
        .where(DEAResultModel.branch_id == branch_id)
        .order_by(DEAResultModel.observation_date.desc())
        .limit(1)
    )
    row = session.execute(stmt).scalar_one_or_none()
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No efficiency score found for branch {branch_id}",
        )
    return EfficiencyResponse(
        branch_id=row.branch_id,
        observation_date=row.observation_date,
        efficiency_score=row.efficiency_score,
        is_efficient=row.efficiency_score == 1.0,
    )
