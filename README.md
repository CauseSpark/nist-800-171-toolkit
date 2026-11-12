# nist-800-171-toolkit

![tests](https://github.com/CauseSpark/nist-800-171-toolkit/actions/workflows/tests.yml/badge.svg)

A small, tested toolkit for practicing a **NIST SP 800-171 self-assessment** the way the DoD scores it. It includes a 110-requirement catalog with DoD point weights, a scoring calculator, SSP and POA&M templates, and a worked example for a fictional company, **Acme Defense Fabrication**.

> **Personal study material.** This is not an official DoD, NIST, CMMC, or Cyber AB product. It does not grant certification, and its output is not an SPRS submission. All company data is fictional, and the repository contains no CUI.

## Purpose

I built this while moving from network defense into GRC and CMMC work. I wanted to turn the DoD Assessment Methodology into something I could run, test and explain: how a gap becomes a point deduction, why MFA and FIPS cryptography get partial credit, and why a missing SSP stops the assessment entirely.

## Baseline (as of November 2026)

| | |
|---|---|
| **Scored standard** | NIST SP 800-171 **Rev 2**: **110 requirements, 14 families** |
| **Scoring rules** | NIST SP 800-171 DoD Assessment Methodology v1.2.1 (weights also in 32 CFR 170.24) |
| **Score range** | **−203 to 110** |
| **CMMC Level 2** | Requirements are identical to NIST SP 800-171 Rev 2 (32 CFR 170.14) |

**Rev 3 note:** NIST published SP 800-171 Rev 3 (97 requirements, 17 families) in May 2024 and withdrew Rev 2 the same day. The DoD has not adopted Rev 3. 32 CFR Part 170 incorporates Rev 2 by reference, DFARS class deviations keep DFARS 252.204-7012 on Rev 2, and the DoD says any move to Rev 3 will come through future rulemaking. This toolkit scores Rev 2 only.

**Program status note:** In July 2026 the Department of War suspended CMMC Phase 2 (C3PAO certification requirements) pending a program review. Level 1 and Level 2 self-assessments and DFARS 252.204-7012 obligations remain in effect, so self-assessment scoring is still current. Check the official sources before relying on this note; it may be out of date.

## Quick start

```bash
git clone https://github.com/CauseSpark/nist-800-171-toolkit.git
cd nist-800-171-toolkit
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt

# Score the fictional Acme assessment
python src/sprs.py examples/acme_assessment.csv

# Run the tests
pytest
```

Sample output:

```
Score: 72 / 110  (range -203 to 110)

Deductions (12 requirements, -38 points):
  -5  3.3.5    not met  Correlate audit review and reporting processes
  -5  3.4.8    not met  Apply allowlisting or denylisting for software
  ...
  -3  3.5.3    partial  Use multifactor authentication
  -3  3.13.11  partial  Use FIPS-validated cryptography for CUI
  ...
```

To score your own practice assessment, copy `examples/acme_assessment.csv` and change the `status` column. Valid statuses are `met`, `not met`, `partial` and `n/a`. Keep real assessment data out of public repos; `.gitignore` excludes `private/` and `*.real.csv`.

## What's in the repo

| Path | What it is |
|---|---|
| `data/requirements.csv` | All 110 Rev 2 requirements: ID, family, my own short title, DoD point weight, scoring notes |
| `src/sprs.py` | Validates input CSVs and computes the score; also a CLI |
| `tests/test_sprs.py` | 30 pytest cases: 110 for all met, −203 for none met, known deductions, partial credit, SSP rule, bad input, CLI |
| `examples/acme_assessment.csv` | Fictional sample assessment that scores 72 |
| `templates/ssp_template.md` | System Security Plan practice template |
| `templates/poam_template.csv` | Plan of Action & Milestones practice template |
| `docs/methodology.md` | How the scoring works, with links to the official sources |
| `.github/workflows/tests.yml` | CI that runs the tests on Python 3.10–3.12 |

## What this demonstrates

- **GRC domain knowledge:**
  - The NIST SP 800-171 Rev 2 control families
  - DoD scoring weights and the partial-credit rules for MFA and FIPS cryptography
  - Why the SSP (3.12.4) and POA&Ms (3.12.2) matter
  - How CMMC Level 2 relates to DFARS 252.204-7012 and 7019/7020
- **Source discipline:** weights were taken from the DoD methodology and cross-checked line by line against 32 CFR 170.24. The repository links to the official text instead of copying it.
- **Translating policy into testable logic:** each scoring rule is code with a test that proves it, including the −203 to 110 boundaries.
- **Engineering hygiene:** input validation with clear error messages, a CLI with meaningful exit codes, CI, and small, focused commits.

## Official sources

- [NIST SP 800-171 DoD Assessment Methodology v1.2.1](https://www.acq.osd.mil/asda/dpc/cp/cyber/docs/safeguarding/NIST-SP-800-171-Assessment-Methodology-Version-1.2.1-6.24.2020.pdf)
- [32 CFR Part 170, CMMC Program](https://www.ecfr.gov/current/title-32/subtitle-A/chapter-I/subchapter-G/part-170)
- [NIST SP 800-171 Rev 2](https://csrc.nist.gov/pubs/sp/800/171/r2/upd1/final) and [Rev 3](https://csrc.nist.gov/pubs/sp/800/171/r3/final)
- [DoD CIO CMMC Resources & Documentation](https://dodcio.defense.gov/CMMC/Resources-Documentation/)

## Disclaimer

This repository is personal study material created for learning and portfolio purposes:

- It is **not** affiliated with or endorsed by the DoD, NIST, the Cyber AB, or any employer or client.
- It does **not** represent a certification, an official assessment, or legal or compliance advice.
- "Acme Defense Fabrication" and all sample data are fictional. No CUI, mission, employer or client information is included.

Requirement titles are my own short paraphrases. Always use the official publications for the authoritative requirement text.

## License

[MIT](LICENSE) © 2026 Peyton Seay
