# Development Workflow

## Branches

| Branch | Purpose | Protection |
|--------|---------|-----------|
| `main` | Production-ready code | ✅ Full protection, PR required |
| `qa` | Staging — tested but unreleased | ⚠️ Light protection |
| `feature/US-XXX-*` | Individual user stories | None (short-lived) |

## Process for Every User Story

1. Create a GitHub Issue (US-XXX) using the user story template
2. `git checkout qa && git pull`
3. `git checkout -b feature/US-XXX-description`
4. Write failing tests (TDD Red phase)
5. Implement code (Green phase)
6. Refactor, run lint + type-check + tests
7. Commit: `feat(US-XXX): description`
8. Push: `git push -u origin feature/US-XXX-description`
9. Open PR targeting `qa`
10. Wait for CI (Stage 1 + Stage 2) to pass
11. Squash-merge to `qa`
12. QA validation on `qa`
13. Merge `qa` → `main`
14. Close the issue

## Commit Message Convention

- `feat(US-XXX): ...` — new feature
- `fix(US-XXX): ...` — bug fix
- `test(US-XXX): ...` — tests only
- `docs(US-XXX): ...` — documentation
- `chore: ...` — maintenance

## CI Pipeline

| Stage | Trigger | Runs |
|-------|---------|------|
| Stage 1 | Every push/PR | Ruff, MyPy, unit tests |
| Stage 2 | Every push/PR | Integration tests (Postgres service) |
| Stage 3 | Merge to qa | E2E, security, performance |
| Stage 4 | Merge to qa | Business verification |
| Stage 5 | Merge to main | Smoke tests |

## Quality Gates

Before any merge:
- ✅ Ruff passes
- ✅ MyPy passes
- ✅ Unit tests pass
- ✅ Integration tests pass
- ✅ Coverage ≥ 85%

## Definition of Done

A user story is "done" when:
- [ ] Code written and follows DDD layering
- [ ] Unit tests written (TDD cycle completed)
- [ ] Integration tests written (if applicable)
- [ ] All linters and type checkers pass
- [ ] Coverage target met
- [ ] PR reviewed (self-review if solo)
- [ ] Merged to `qa` with green CI
- [ ] Manually verified on `qa`
- [ ] Merged to `main`
- [ ] GitHub Issue closed
