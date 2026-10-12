"""Seed the database with synthetic branches, observations, and DEA scores."""
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402

from src.application.services.dea_service import DEAService  # noqa: E402
from src.infrastructure.database.models import Base  # noqa: E402
from src.infrastructure.database.repositories import (  # noqa: E402
    PostgresBranchRepository,
    PostgresDEARepository,
)
from src.infrastructure.external.synthetic_data_generator import (  # noqa: E402
    generate_branches,
    generate_observations,
)


def main() -> None:
    print("=" * 60)
    print("Seed Database — Bank Efficiency Platform")
    print("=" * 60)

    db_url = "postgresql://bankuser:bankpass@localhost:5432/bank_efficiency"

    print(f"\n[1/4] Connecting to {db_url[:40]}...")
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)
    session = session_factory()
    print("      ✓ Connected, tables verified")

    print("\n[2/4] Generating 100 synthetic branches...")
    branches = generate_branches(n=100, seed=42)
    repo = PostgresBranchRepository(session)
    for b in branches:
        repo.save_branch(b)
    session.commit()
    print(f"      ✓ Saved {len(branches)} branches")

    print("\n[3/4] Generating 12 months of observations per branch...")
    observations = generate_observations(branches, start_date=date(2025, 1, 1), months=12, seed=42)
    for o in observations:
        repo.save_observation(o)
    session.commit()
    print(f"      ✓ Saved {len(observations)} observations")

    print("\n[4/4] Running DEA on the latest month...")
    latest_date = date(2025, 12, 1)
    latest_obs = repo.get_observations_for_date(latest_date)
    inputs = [o.to_input_vector() for o in latest_obs]
    outputs = [o.to_output_vector() for o in latest_obs]

    dea_service = DEAService()
    scores = dea_service.calculate_efficiency(inputs, outputs)

    dea_repo = PostgresDEARepository(session)
    for obs, score in zip(latest_obs, scores, strict=False):
        dea_repo.save_score(obs.branch_id, score, latest_date)
    session.commit()

    efficient = sum(1 for s in scores if s.value == 1.0)
    avg = sum(s.value for s in scores) / len(scores)
    print(f"      ✓ Scored {len(scores)} branches")
    print(f"      ✓ Efficient (1.0): {efficient}")
    print(f"      ✓ Average: {avg:.4f}")

    print("\n" + "=" * 60)
    print("SEED COMPLETE")
    print("=" * 60)

    session.close()


if __name__ == "__main__":
    main()
