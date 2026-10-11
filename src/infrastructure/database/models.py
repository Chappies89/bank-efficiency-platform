"""SQLAlchemy ORM models.

These map domain entities to database tables. The domain objects
(Branch, BranchObservation) do NOT know about SQLAlchemy — these
models are the database representation.
"""

from __future__ import annotations

from datetime import date

from sqlalchemy import (
    Date,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all ORM models."""


class BranchModel(Base):
    """Permanent identity of a bank branch."""

    __tablename__ = "branches"

    branch_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    branch_name: Mapped[str] = mapped_column(String(100), nullable=False)
    region: Mapped[str] = mapped_column(String(50), nullable=False)
    opened_date: Mapped[date] = mapped_column(Date, nullable=False)
    square_meters: Mapped[int] = mapped_column(Integer, nullable=False)


class BranchObservationModel(Base):
    """Time-series snapshot of a branch's performance."""

    __tablename__ = "branch_observations"
    __table_args__ = (UniqueConstraint("branch_id", "observation_date", name="uq_branch_date"),)

    observation_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    branch_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("branches.branch_id"), nullable=False
    )
    observation_date: Mapped[date] = mapped_column(Date, nullable=False)
    fte_count: Mapped[int] = mapped_column(Integer, nullable=False)
    operational_expense: Mapped[float] = mapped_column(Float, nullable=False)
    deposit_volume: Mapped[float] = mapped_column(Float, nullable=False)
    loan_volume: Mapped[float] = mapped_column(Float, nullable=False)
    new_accounts: Mapped[int] = mapped_column(Integer, nullable=False)
    digital_transaction_ratio: Mapped[float] = mapped_column(Float, nullable=False)


class DEAResultModel(Base):
    """A DEA efficiency score for a branch at a specific date."""

    __tablename__ = "dea_results"

    result_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    branch_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("branches.branch_id"), nullable=False
    )
    observation_date: Mapped[date] = mapped_column(Date, nullable=False)
    efficiency_score: Mapped[float] = mapped_column(Float, nullable=False)
