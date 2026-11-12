# Scoring Methodology

This page explains, in my own words, how `src/sprs.py` scores an assessment. It summarizes the DoD's rules; it does not replace them. For anything that matters, read the official sources linked at the bottom.

*Last checked: November 2026.*

## Which standard is scored

The tool scores against **NIST SP 800-171 Revision 2**: 110 security requirements in 14 families.

- NIST published Rev 3 in May 2024 and withdrew Rev 2 that same day.
- The DoD still uses Rev 2. 32 CFR Part 170 incorporates Rev 2 by reference, CMMC Level 2 requirements are defined as identical to Rev 2, and DFARS class deviations keep contractors on Rev 2 for DFARS 252.204-7012.
- The DoD has said it will move to Rev 3 only through future rulemaking. Rev 3 (97 requirements, 17 families) is **not** scored by this tool.

## How the score works

The DoD's NIST SP 800-171 Assessment Methodology (Version 1.2.1, June 2020) uses the scoring system below. The same weights appear in the CMMC rule at 32 CFR 170.24.

1. **Start at 110**, one point per requirement.
2. **Subtract a weight for each requirement that is not met.** Weights reflect how much a gap affects the security of the network and its CUI:

   | Weight | Count | Meaning |
   |---|---|---|
   | 5 points | 42 (+2 variable) | A gap could directly lead to exploitation or exfiltration of CUI |
   | 3 points | 14 | A gap has a specific, more limited effect |
   | 1 point | 51 | A gap has a limited or indirect effect |
   | No value | 1 | 3.12.4, the system security plan (see below) |

3. **Two requirements give partial credit.**
   - **3.5.3, multifactor authentication:** subtract 5 if MFA isn't used at all. Subtract 3 if it covers remote and privileged access but not general users.
   - **3.13.11, FIPS-validated cryptography:** subtract 5 if CUI isn't encrypted. Subtract 3 if it is encrypted but the cryptography isn't FIPS-validated.

   No other requirement gives partial credit. In this tool, `partial` on any other requirement deducts the full weight.
4. **Some access requirements don't apply when that access isn't allowed.** The methodology says not to subtract points for 3.1.12 and 3.1.13 when remote access isn't permitted, for 3.1.16 and 3.1.17 when wireless isn't permitted, or for 3.1.18 when mobile devices can't connect. This tool accepts `n/a` for only those five.
5. **No SSP, no score.** Requirement 3.12.4 has no point value. Without a system security plan the assessment can't be completed, which also means noncompliance with DFARS 252.204-7012. The tool returns no score in that case.
6. **Plans of action don't earn points.** A requirement with an open POA&M item is still scored as not implemented.

## Range

| Situation | Score |
|---|---|
| Everything met | **110** |
| Everything not met (SSP present) | **−203** |

Why −203: the weights add up to 313 when 3.5.3 and 3.13.11 both take their full 5 points (42×5 + 2×5 + 14×3 + 51×1 = 313), and 110 − 313 = −203. The methodology itself only says a score can go negative; −203 is the arithmetic floor.

## Assessment levels (context)

The methodology describes three confidence levels:

- **Basic:** a contractor self-assessment. It gives "Low" confidence and is what this tool helps practice.
- **Medium:** a DoD review of the SSP.
- **High:** DoD verification on site or virtually.

Basic scores are reported to the Supplier Performance Risk System (SPRS) under DFARS 252.204-7019 and 7020. **This tool does not submit anything to SPRS.**

## Inputs this tool expects

`examples/acme_assessment.csv` needs one row per requirement with the columns `id,status[,notes]`. Valid statuses are `met`, `not met`, `partial` and `n/a`; case, underscores and hyphens are ignored. The tool rejects the file if any of the following is true:

- a requirement ID is unknown
- an ID appears twice
- any of the 110 rows is missing
- a status isn't one of the four above
- `n/a` is used on a requirement where it isn't allowed

## Official sources

- [NIST SP 800-171 DoD Assessment Methodology, Version 1.2.1 (DoD PDF)](https://www.acq.osd.mil/asda/dpc/cp/cyber/docs/safeguarding/NIST-SP-800-171-Assessment-Methodology-Version-1.2.1-6.24.2020.pdf). The scoring template is in Annex A.
- [32 CFR 170.24, CMMC scoring methodology (eCFR)](https://www.ecfr.gov/current/title-32/subtitle-A/chapter-I/subchapter-G/part-170/subpart-D/section-170.24)
- [32 CFR Part 170, CMMC Program (eCFR)](https://www.ecfr.gov/current/title-32/subtitle-A/chapter-I/subchapter-G/part-170)
- [NIST SP 800-171 Rev 2 (NIST CSRC, withdrawn by NIST but still the DoD baseline)](https://csrc.nist.gov/pubs/sp/800/171/r2/upd1/final)
- [NIST SP 800-171A, assessment procedures for Rev 2 (NIST CSRC)](https://csrc.nist.gov/pubs/sp/800/171/a/final)
- [NIST SP 800-171 Rev 3 (NIST CSRC)](https://csrc.nist.gov/pubs/sp/800/171/r3/final)
- [DoD CIO, CMMC Resources & Documentation](https://dodcio.defense.gov/CMMC/Resources-Documentation/)
- [DoD Procurement: Cybersecurity / Safeguarding](https://www.acq.osd.mil/asda/dpc/cp/cyber/safeguarding.html)
