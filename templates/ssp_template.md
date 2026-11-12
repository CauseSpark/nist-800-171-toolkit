# System Security Plan (SSP) — Template

> **Study template.** This is an original practice template, not an official DoD, NIST, or CMMC form. Replace every `[bracketed]` placeholder. Do not put real CUI in a public repository.

| Field | Value |
|---|---|
| Organization | [Acme Defense Fabrication (fictional)] |
| System name | [e.g., Acme CUI Enclave] |
| System owner | [Name, title] |
| SSP version / date | [1.0 / YYYY-MM-DD] |
| Baseline | NIST SP 800-171 Rev 2 (110 requirements) |
| Next review | [YYYY-MM-DD] |

---

## 1. System description

### 1.1 Purpose
[What the system does and why it handles CUI. One paragraph.]

### 1.2 CUI handled
[CUI categories from the [CUI Registry](https://www.archives.gov/cui/registry/category-list), and where they come from (e.g., customer drawings received under DFARS 252.204-7012).]

### 1.3 Assessment scope and boundary
| Asset category | Examples | Count |
|---|---|---|
| CUI assets | [file server, CAD workstations] | [ ] |
| Security protection assets | [firewall, IdP, log server] | [ ] |
| Contractor risk managed assets | [ ] | [ ] |
| Specialized assets | [CNC machines, test equipment] | [ ] |
| Out-of-scope assets | [guest Wi-Fi] | [ ] |

Asset categories follow 32 CFR 170.19 — see the [CMMC Scoping Guide – Level 2](https://dodcio.defense.gov/CMMC/Resources-Documentation/).

### 1.4 Network diagram
[Insert or link a diagram showing the boundary, data flows, and external connections.]

### 1.5 External connections and service providers
| Provider / system | Purpose | CUI exchanged? | FedRAMP Moderate or equivalent? |
|---|---|---|---|
| [ ] | [ ] | [Y/N] | [Y/N/NA] |

### 1.6 Roles and responsibilities
| Role | Name | Responsibility |
|---|---|---|
| System owner | [ ] | [ ] |
| ISSM / security lead | [ ] | [ ] |
| System administrator | [ ] | [ ] |

---

## 2. Requirement implementation

Repeat one block per requirement (110 total). Status values match `examples/acme_assessment.csv`: `met`, `not met`, `partial`, `n/a`.

### Example block

#### 3.5.3 — Use multifactor authentication
- **Status:** [met / not met / partial]
- **Implementation:** [How the requirement is met: tools, settings, scope. Be specific enough that an assessor can test it.]
- **Responsible role:** [ ]
- **Evidence:** [Policy section, config screenshot, export file name]
- **POA&M ID (if not met):** [POAM-0001]

### Family checklist

| Family | Requirements | Section complete? |
|---|---|---|
| AC — Access Control | 3.1.1 – 3.1.22 | [ ] |
| AT — Awareness and Training | 3.2.1 – 3.2.3 | [ ] |
| AU — Audit and Accountability | 3.3.1 – 3.3.9 | [ ] |
| CM — Configuration Management | 3.4.1 – 3.4.9 | [ ] |
| IA — Identification and Authentication | 3.5.1 – 3.5.11 | [ ] |
| IR — Incident Response | 3.6.1 – 3.6.3 | [ ] |
| MA — Maintenance | 3.7.1 – 3.7.6 | [ ] |
| MP — Media Protection | 3.8.1 – 3.8.9 | [ ] |
| PS — Personnel Security | 3.9.1 – 3.9.2 | [ ] |
| PE — Physical Protection | 3.10.1 – 3.10.6 | [ ] |
| RA — Risk Assessment | 3.11.1 – 3.11.3 | [ ] |
| CA — Security Assessment | 3.12.1 – 3.12.4 | [ ] |
| SC — System and Communications Protection | 3.13.1 – 3.13.16 | [ ] |
| SI — System and Information Integrity | 3.14.1 – 3.14.7 | [ ] |

For the full requirement text and assessment objectives, use the official sources: [NIST SP 800-171 Rev 2](https://csrc.nist.gov/pubs/sp/800/171/r2/upd1/final) and [NIST SP 800-171A](https://csrc.nist.gov/pubs/sp/800/171/a/final).

---

## 3. Plan maintenance
- Requirement 3.12.4 is the SSP itself. Under the DoD Assessment Methodology, a missing SSP means the assessment cannot be completed.
- Review this plan at least [annually] and after significant system changes.
- Open gaps are tracked in the POA&M (`templates/poam_template.csv`), which supports requirement 3.12.2.

## 4. Approval
| Name | Title | Signature | Date |
|---|---|---|---|
| [ ] | [ ] | [ ] | [ ] |
