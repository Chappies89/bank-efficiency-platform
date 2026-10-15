"""Unit tests for the Branch entity."""
from datetime import date

import pytest

from src.domain.entities.branch import Branch


class TestBranch:
    def setup_method(self) -> None:
        self.branch = Branch(
            branch_id=1,
            branch_name="Sandton",
            region="Gauteng",
            opened_date=date(2010, 3, 1),
            square_meters=1200,
        )

    def test_branch_is_immutable(self):
        with pytest.raises(AttributeError):
            self.branch.branch_name = "Rosebank"

    def test_branch_equality_by_attributes(self):
        b2 = Branch(1, "Sandton", "Gauteng", date(2010, 3, 1), 1200)
        assert self.branch == b2

    def test_branch_inequality(self):
        b2 = Branch(2, "Rosebank", "Gauteng", date(2015, 6, 1), 800)
        assert self.branch != b2

    def test_branch_has_expected_attributes(self):
        assert self.branch.branch_id == 1
        assert self.branch.region == "Gauteng"
        assert self.branch.square_meters == 1200
