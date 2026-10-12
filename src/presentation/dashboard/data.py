"""Data loading and formatting for the dashboard."""

from __future__ import annotations

from datetime import date

import pandas as pd
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from src.config.settings import settings
from src.infrastructure.database.models import (
    BranchModel,
    BranchObservationModel,
    DEAResultModel,
)


def get_engine():
    """Get the database engine."""
    return create_engine(settings.database_url)


def load_branches() -> pd.DataFrame:
    """Load all branches as a DataFrame."""
    engine = get_engine()
    with Session(engine) as session:
        stmt = select(BranchModel).order_by(BranchModel.branch_id)
        rows = session.execute(stmt).scalars().all()
        return pd.DataFrame(
            [
                {
                    "branch_id": r.branch_id,
                    "branch_name": r.branch_name,
                    "region": r.region,
                    "opened_date": r.opened_date,
                    "square_meters": r.square_meters,
                }
                for r in rows
            ]
        )


def load_latest_efficiency() -> pd.DataFrame:
    """Load the latest efficiency score for each branch."""
    engine = get_engine()
    with Session(engine) as session:
        stmt = select(DEAResultModel).order_by(
            DEAResultModel.branch_id,
            DEAResultModel.observation_date.desc(),
        )
        rows = session.execute(stmt).scalars().all()

        # Keep only the most recent score per branch
        seen: set[int] = set()
        latest: list[dict] = []
        for r in rows:
            if r.branch_id in seen:
                continue
            seen.add(r.branch_id)
            latest.append(
                {
                    "branch_id": r.branch_id,
                    "observation_date": r.observation_date,
                    "efficiency_score": r.efficiency_score,
                }
            )
        return pd.DataFrame(latest)


def load_branches_with_efficiency() -> pd.DataFrame:
    """Combine branch info with latest efficiency score."""
    branches = load_branches()
    efficiency = load_latest_efficiency()
    if efficiency.empty:
        branches["efficiency_score"] = None
        branches["observation_date"] = None
        return branches
    merged = branches.merge(efficiency, on="branch_id", how="left")
    return merged
