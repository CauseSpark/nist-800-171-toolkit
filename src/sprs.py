"""Compute a NIST SP 800-171 (Rev 2) DoD Assessment Methodology score.

Personal study tool. It is not an official DoD or SPRS product, and the score
it produces is not a submission to SPRS.

Scoring rules (see docs/methodology.md for sources):
  * Start at 110 and subtract each unmet requirement's weight (5, 3, or 1).
  * 3.5.3 (MFA) and 3.13.11 (FIPS crypto) may be "partial", which deducts 3
    instead of 5. "partial" on any other requirement deducts the full weight,
    because the methodology gives no other partial credit.
  * A few access-related requirements (3.1.12, 3.1.13, 3.1.16, 3.1.17,
    3.1.18) may be "n/a" when that type of access is not permitted.
  * 3.12.4 (system security plan) has no point value. If it is not met the
    assessment cannot be completed, so no score is returned.
  * Range: -203 (nothing met) to 110 (everything met).

Usage:
    python src/sprs.py examples/acme_assessment.csv
"""

from __future__ import annotations

import argparse
import csv
import sys
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_REQUIREMENTS = REPO_ROOT / "data" / "requirements.csv"

MAX_SCORE = 110
EXPECTED_COUNT = 110
EXPECTED_FAMILIES = {
    "AC", "AT", "AU", "CM", "IA", "IR", "MA",
    "MP", "PS", "PE", "RA", "CA", "SC", "SI",
}
VALID_WEIGHTS = {0, 1, 3, 5}

MET, NOT_MET, PARTIAL, NA = "met", "not met", "partial", "n/a"
VALID_STATUSES = {MET, NOT_MET, PARTIAL, NA}

PARTIAL_CREDIT_IDS = {"3.5.3", "3.13.11"}  # partial deducts 3 instead of 5
PARTIAL_DEDUCTION = 3
NA_ALLOWED_IDS = {"3.1.12", "3.1.13", "3.1.16", "3.1.17", "3.1.18"}
SSP_ID = "3.12.4"

REQUIREMENT_COLUMNS = ["id", "family", "title", "weight", "notes"]
ASSESSMENT_COLUMNS = ["id", "status"]


class ValidationError(ValueError):
    """Raised when an input CSV is malformed or inconsistent."""


@dataclass(frozen=True)
class Requirement:
    id: str
    family: str
    title: str
    weight: int
    notes: str = ""


@dataclass
class Deduction:
    id: str
    title: str
    status: str
    points: int


@dataclass
class ScoreResult:
    score: int | None
    deductions: list[Deduction] = field(default_factory=list)
    message: str = ""

    @property
    def completed(self) -> bool:
        return self.score is not None


def _normalize_status(raw: str) -> str:
    """Accept common spellings: 'Not Met', 'not_met', 'NA', 'Not Applicable'."""
    s = " ".join(raw.strip().lower().replace("_", " ").replace("-", " ").split())
    aliases = {"notmet": NOT_MET, "na": NA, "n/a": NA, "notapplicable": NA}
    return aliases.get(s.replace(" ", ""), s)


def _read_csv(path: Path, required_columns: list[str]) -> list[dict[str, str]]:
    path = Path(path)
    if not path.is_file():
        raise ValidationError(f"{path}: file not found")
    with path.open(newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            raise ValidationError(f"{path}: file is empty")
        header = [h.strip().lower() for h in reader.fieldnames]
        missing = [c for c in required_columns if c not in header]
        if missing:
            raise ValidationError(f"{path}: missing column(s): {', '.join(missing)}")
        rows = []
        for raw in reader:
            row = {k.strip().lower(): (v or "").strip() for k, v in raw.items() if k}
            if any(row.values()):
                rows.append(row)
    return rows


def load_requirements(path: Path = DEFAULT_REQUIREMENTS) -> dict[str, Requirement]:
    """Load and validate the requirements catalog."""
    rows = _read_csv(path, REQUIREMENT_COLUMNS)
    reqs: dict[str, Requirement] = {}
    for line, row in enumerate(rows, start=2):
        rid = row["id"]
        if not rid:
            raise ValidationError(f"{path}:{line}: missing id")
        if rid in reqs:
            raise ValidationError(f"{path}:{line}: duplicate id {rid}")
        if row["family"] not in EXPECTED_FAMILIES:
            raise ValidationError(f"{path}:{line}: unknown family {row['family']!r}")
        try:
            weight = int(row["weight"])
        except ValueError:
            raise ValidationError(f"{path}:{line}: weight must be an integer") from None
        if weight not in VALID_WEIGHTS:
            raise ValidationError(f"{path}:{line}: weight {weight} not in {sorted(VALID_WEIGHTS)}")
        reqs[rid] = Requirement(rid, row["family"], row["title"], weight, row.get("notes", ""))

    if len(reqs) != EXPECTED_COUNT:
        raise ValidationError(f"{path}: expected {EXPECTED_COUNT} requirements, found {len(reqs)}")
    if {r.family for r in reqs.values()} != EXPECTED_FAMILIES:
        raise ValidationError(f"{path}: expected all 14 requirement families")
    return reqs


def load_assessment(path: Path, requirements: dict[str, Requirement]) -> dict[str, str]:
    """Load an assessment CSV (columns: id, status[, notes]) and validate it."""
    rows = _read_csv(path, ASSESSMENT_COLUMNS)
    statuses: dict[str, str] = {}
    for line, row in enumerate(rows, start=2):
        rid = row["id"]
        if rid not in requirements:
            raise ValidationError(f"{path}:{line}: unknown requirement id {rid!r}")
        if rid in statuses:
            raise ValidationError(f"{path}:{line}: duplicate id {rid}")
        status = _normalize_status(row["status"])
        if status not in VALID_STATUSES:
            raise ValidationError(
                f"{path}:{line}: status {row['status']!r} for {rid} must be one of "
                f"met, not met, partial, n/a"
            )
        statuses[rid] = status

    missing = sorted(set(requirements) - set(statuses), key=_sort_key)
    if missing:
        raise ValidationError(f"{path}: missing status for: {', '.join(missing)}")
    return statuses


def _sort_key(rid: str) -> tuple[int, ...]:
    return tuple(int(p) for p in rid.split("."))


def deduction_for(req: Requirement, status: str) -> int:
    """Points to subtract for one requirement given its status."""
    if status not in VALID_STATUSES:
        raise ValidationError(f"invalid status {status!r} for {req.id}")
    if status == MET:
        return 0
    if status == NA:
        if req.id not in NA_ALLOWED_IDS:
            raise ValidationError(f"{req.id} cannot be marked n/a")
        return 0
    if status == PARTIAL and req.id in PARTIAL_CREDIT_IDS:
        return PARTIAL_DEDUCTION
    return req.weight  # not met, or partial with no partial credit


def compute_score(requirements: dict[str, Requirement], statuses: dict[str, str]) -> ScoreResult:
    """Score an assessment. Returns score=None if the SSP (3.12.4) is not met."""
    missing = set(requirements) - set(statuses)
    if missing:
        raise ValidationError(f"missing status for {len(missing)} requirement(s)")

    if statuses.get(SSP_ID) != MET:
        return ScoreResult(
            score=None,
            message=(
                f"{SSP_ID} (system security plan) is not met: the assessment "
                "cannot be completed, so no score is produced."
            ),
        )

    deductions = []
    for rid in sorted(requirements, key=_sort_key):
        req = requirements[rid]
        pts = deduction_for(req, statuses[rid])
        if pts:
            deductions.append(Deduction(rid, req.title, statuses[rid], pts))

    score = MAX_SCORE - sum(d.points for d in deductions)
    return ScoreResult(score=score, deductions=deductions, message="Assessment scored.")


def score_file(assessment: Path, requirements_path: Path = DEFAULT_REQUIREMENTS) -> ScoreResult:
    reqs = load_requirements(requirements_path)
    return compute_score(reqs, load_assessment(assessment, reqs))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="NIST SP 800-171 Rev 2 score calculator (study tool)")
    parser.add_argument("assessment", type=Path, help="assessment CSV with id,status columns")
    parser.add_argument("--requirements", type=Path, default=DEFAULT_REQUIREMENTS)
    args = parser.parse_args(argv)

    try:
        result = score_file(args.assessment, args.requirements)
    except ValidationError as exc:
        print(f"Validation error: {exc}", file=sys.stderr)
        return 2

    if not result.completed:
        print(result.message)
        return 1

    print(f"Score: {result.score} / {MAX_SCORE}  (range -203 to 110)")
    if result.deductions:
        print(f"\nDeductions ({len(result.deductions)} requirements, -{MAX_SCORE - result.score} points):")
        for d in sorted(result.deductions, key=lambda d: (-d.points, _sort_key(d.id))):
            print(f"  -{d.points}  {d.id:<8} {d.status:<8} {d.title}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
