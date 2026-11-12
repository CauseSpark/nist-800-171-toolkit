"""Tests for the NIST SP 800-171 Rev 2 scoring tool."""

import csv
from pathlib import Path

import pytest

import sprs
from sprs import ValidationError

REPO = Path(__file__).resolve().parent.parent
EXAMPLE = REPO / "examples" / "acme_assessment.csv"


@pytest.fixture(scope="module")
def reqs():
    return sprs.load_requirements()


def all_status(reqs, status):
    return {rid: status for rid in reqs}


def write_assessment(path, statuses, header=("id", "status")):
    with path.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(header)
        for rid, status in statuses.items():
            w.writerow([rid, status])
    return path


# --- Catalog integrity -------------------------------------------------------

def test_catalog_has_110_rows(reqs):
    assert len(reqs) == 110


def test_catalog_has_14_families(reqs):
    assert {r.family for r in reqs.values()} == sprs.EXPECTED_FAMILIES


def test_catalog_weight_distribution(reqs):
    weights = [r.weight for r in reqs.values()]
    assert weights.count(5) == 44  # 42 fixed 5-pointers + 3.5.3 and 3.13.11
    assert weights.count(3) == 14
    assert weights.count(1) == 51
    assert reqs["3.12.4"].weight == 0


def test_family_counts(reqs):
    expected = {"AC": 22, "AT": 3, "AU": 9, "CM": 9, "IA": 11, "IR": 3, "MA": 6,
                "MP": 9, "PS": 2, "PE": 6, "RA": 3, "CA": 4, "SC": 16, "SI": 7}
    counts = {}
    for r in reqs.values():
        counts[r.family] = counts.get(r.family, 0) + 1
    assert counts == expected


# --- Score boundaries --------------------------------------------------------

def test_all_met_scores_110(reqs):
    assert sprs.compute_score(reqs, all_status(reqs, "met")).score == 110


def test_nothing_met_scores_minus_203(reqs):
    statuses = all_status(reqs, "not met")
    statuses["3.12.4"] = "met"  # an SSP is required to produce any score
    result = sprs.compute_score(reqs, statuses)
    assert result.score == -203


# --- Known deductions --------------------------------------------------------

@pytest.mark.parametrize("rid, expected", [
    ("3.1.1", 105),   # 5-point
    ("3.1.5", 107),   # 3-point
    ("3.1.8", 109),   # 1-point
    ("3.5.3", 105),   # MFA not implemented at all
    ("3.13.11", 105), # no encryption at all
])
def test_single_not_met(reqs, rid, expected):
    statuses = all_status(reqs, "met")
    statuses[rid] = "not met"
    assert sprs.compute_score(reqs, statuses).score == expected


@pytest.mark.parametrize("rid", ["3.5.3", "3.13.11"])
def test_partial_credit_deducts_3(reqs, rid):
    statuses = all_status(reqs, "met")
    statuses[rid] = "partial"
    assert sprs.compute_score(reqs, statuses).score == 107


def test_partial_without_partial_credit_deducts_full_weight(reqs):
    statuses = all_status(reqs, "met")
    statuses["3.14.6"] = "partial"
    assert sprs.compute_score(reqs, statuses).score == 105


def test_na_allowed_for_wireless(reqs):
    statuses = all_status(reqs, "met")
    statuses["3.1.16"] = statuses["3.1.17"] = "n/a"
    assert sprs.compute_score(reqs, statuses).score == 110


def test_na_rejected_where_not_allowed(reqs):
    statuses = all_status(reqs, "met")
    statuses["3.1.1"] = "n/a"
    with pytest.raises(ValidationError, match="cannot be marked n/a"):
        sprs.compute_score(reqs, statuses)


def test_missing_ssp_produces_no_score(reqs):
    statuses = all_status(reqs, "met")
    statuses["3.12.4"] = "not met"
    result = sprs.compute_score(reqs, statuses)
    assert result.score is None
    assert not result.completed
    assert "3.12.4" in result.message


def test_acme_example_scores_72():
    result = sprs.score_file(EXAMPLE)
    assert result.score == 72
    assert len(result.deductions) == 12


# --- Bad input ---------------------------------------------------------------

def test_status_spellings_are_normalized(tmp_path, reqs):
    statuses = all_status(reqs, "Met")
    statuses["3.1.1"] = "NOT_MET"
    statuses["3.1.16"] = "N/A"
    path = write_assessment(tmp_path / "a.csv", statuses)
    loaded = sprs.load_assessment(path, reqs)
    assert loaded["3.1.1"] == "not met"
    assert loaded["3.1.16"] == "n/a"


def test_invalid_status_rejected(tmp_path, reqs):
    statuses = all_status(reqs, "met")
    statuses["3.1.1"] = "mostly"
    path = write_assessment(tmp_path / "a.csv", statuses)
    with pytest.raises(ValidationError, match="must be one of"):
        sprs.load_assessment(path, reqs)


def test_unknown_id_rejected(tmp_path, reqs):
    statuses = all_status(reqs, "met")
    statuses["3.99.1"] = "met"
    path = write_assessment(tmp_path / "a.csv", statuses)
    with pytest.raises(ValidationError, match="unknown requirement id"):
        sprs.load_assessment(path, reqs)


def test_missing_rows_rejected(tmp_path, reqs):
    statuses = all_status(reqs, "met")
    del statuses["3.14.7"]
    path = write_assessment(tmp_path / "a.csv", statuses)
    with pytest.raises(ValidationError, match="missing status for: 3.14.7"):
        sprs.load_assessment(path, reqs)


def test_duplicate_id_rejected(tmp_path, reqs):
    path = write_assessment(tmp_path / "a.csv", all_status(reqs, "met"))
    with path.open("a", newline="") as fh:
        csv.writer(fh).writerow(["3.1.1", "met"])
    with pytest.raises(ValidationError, match="duplicate id 3.1.1"):
        sprs.load_assessment(path, reqs)


def test_missing_column_rejected(tmp_path, reqs):
    path = write_assessment(tmp_path / "a.csv", all_status(reqs, "met"), header=("id", "state"))
    with pytest.raises(ValidationError, match="missing column"):
        sprs.load_assessment(path, reqs)


def test_empty_file_rejected(tmp_path, reqs):
    path = tmp_path / "empty.csv"
    path.write_text("")
    with pytest.raises(ValidationError, match="empty"):
        sprs.load_assessment(path, reqs)


def test_missing_file_rejected(tmp_path, reqs):
    with pytest.raises(ValidationError, match="not found"):
        sprs.load_assessment(tmp_path / "nope.csv", reqs)


def test_catalog_with_wrong_row_count_rejected(tmp_path):
    src = (REPO / "data" / "requirements.csv").read_text().splitlines()
    bad = tmp_path / "reqs.csv"
    bad.write_text("\n".join(src[:-1]) + "\n")  # drop last requirement
    with pytest.raises(ValidationError, match="expected 110 requirements, found 109"):
        sprs.load_requirements(bad)


def test_catalog_with_bad_weight_rejected(tmp_path):
    text = (REPO / "data" / "requirements.csv").read_text()
    bad = tmp_path / "reqs.csv"
    bad.write_text(text.replace("3.1.1,AC,Limit system access to authorized users and devices,5",
                                "3.1.1,AC,Limit system access to authorized users and devices,4"))
    with pytest.raises(ValidationError, match="weight 4"):
        sprs.load_requirements(bad)


# --- CLI ---------------------------------------------------------------------

def test_cli_prints_score(capsys):
    assert sprs.main([str(EXAMPLE)]) == 0
    assert "Score: 72 / 110" in capsys.readouterr().out


def test_cli_returns_2_on_bad_input(tmp_path, capsys):
    bad = tmp_path / "bad.csv"
    bad.write_text("id,status\n3.1.1,maybe\n")
    assert sprs.main([str(bad)]) == 2
    assert "Validation error" in capsys.readouterr().err
