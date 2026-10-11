"""End-to-end demo of the current pipeline.

Generates synthetic branches, runs DEA, and saves results to Postgres.
Run with: python scripts/demo_pipeline.py
"""
from __future__ import annotations

import sys
from pathlib import Path

# Add project root to sys.path so 'src' package is importable
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from datetime import date  # noqa: E402

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
    print("Bank Efficiency Platform — End-to-End Demo")
    print("=" * 60)

    # 1. Connect to Postgres
    print("\n[1/5] Connecting to Postgres...")
    engine = create_engine(
        "postgresql://bankuser:bankpass@localhost:5432/bank_efficiency"
    )
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)
    session = session_factory()
    print("      ✓ Connected")

    # 2. Generate synthetic branches
    print("\n[2/5] Generating 50 synthetic branches...")
    branches = generate_branches(n=50, seed=42)
    repo = PostgresBranchRepository(session)
    for b in branches:
        repo.save_branch(b)
    session.commit()
    print(f"      ✓ Saved {len(branches)} branches to Postgres")

    # 3. Generate observations
    print("\n[3/5] Generating 12 months of observations...")
    observations = generate_observations(
        branches, start_date=date(2025, 1, 1), months=12, seed=42
    )
    for o in observations:
        repo.save_observation(o)
    session.commit()
    print(f"      ✓ Saved {len(observations)} observations")

    # 4. Run DEA on the latest month
    print("\n[4/5] Running DEA efficiency analysis...")
    latest_date = date(2025, 12, 1)
    latest_obs = repo.get_observations_for_date(latest_date)
    inputs = [o.to_input_vector() for o in latest_obs]
    outputs = [o.to_output_vector() for o in latest_obs]

    dea_service = DEAService()
    scores = dea_service.calculate_efficiency(inputs, outputs)

    efficient = sum(1 for s in scores if s.value == 1.0)
    avg_efficiency = sum(s.value for s in scores) / len(scores)

    print(f"      ✓ Scored {len(scores)} branches")
    print(f"      ✓ Efficient (score = 1.0): {efficient}")
    print(f"      ✓ Average efficiency: {avg_efficiency:.4f}")

    # 5. Save scores
    print("\n[5/5] Saving scores to Postgres...")
    dea_repo = PostgresDEARepository(session)
    for obs, score in zip(latest_obs, scores):
        dea_repo.save_score(obs.branch_id, score, latest_date)
    session.commit()
    print(f"      ✓ Saved {len(scores)} DEA scores")

    # Summary
    print("\n" + "=" * 60)
    print("DEMO COMPLETE")
    print("=" * 60)
    print("\nView data:")
    print("  • pgAdmin:  http://localhost:5050")
    print("  • psql:     docker compose exec postgres psql -U bankuser -d bank_efficiency")

    session.close()


if __name__ == "__main__":
    main()
