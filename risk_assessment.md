# Risk Assessment

**Project:** ULK Polytechnic Institute - Cryptography and Network Security integrated situation  
**Scope:** Student-record storage and inter-campus file transfer, as described in the assignment. No real student data or production network was accessed.

## Assets, vulnerabilities, and consequences

| Asset | Vulnerability / threat | Possible consequence |
|---|---|---|
| Student records and the central records server | Guest network can reach the records server; repeated attempts have also come from an unfamiliar external address | Unauthorised disclosure, alteration, or loss of student records; service disruption; privacy and institutional harm |
| Staff accounts and systems | Weak staff passwords and outdated software | Account compromise, malware or exploitation, and unauthorised access to records |
| Inter-campus record files and transfer service | Unencrypted file transfers | Interception or modification of records in transit, with loss of confidentiality and integrity |

## Ranked risks

Scale: likelihood and impact are Low, Medium, or High. Ranking reflects the scenario in the assignment, not measured incident data.

| Rank | Risk | Likelihood | Impact | Reasoning | Recommended control |
|---|---|---:|---:|---|---|
| 1 | Guest or external access to the records server | High | High | Guest reachability is stated as observed, and repeated external attempts are reported. Successful compromise could expose a high-value records asset. | Default-deny network policy; allow only the assessor-approved staff source network to the specified service; deny guest and other inbound sources; log and review denied attempts. Replace all network placeholders with authorised lab values before applying. |
| 2 | Staff account compromise through weak passwords or outdated software | Medium | High | Weak passwords and outdated software are confirmed weaknesses, but no successful account compromise is stated. Privileged or staff access could expose many records. | Enforce unique strong passwords with MFA where available; patch supported software on a tracked schedule; limit account privilege and review access. |
| 3 | Interception or tampering during file transfer | Medium | High | Transfers are explicitly unencrypted; an attacker with a suitable network position could read or modify files. No interception is reported. | Use authenticated encrypted transfer (for example, an institution-approved SFTP or TLS service); verify file integrity with SHA-256 over a trusted channel and manage keys/secrets outside source control. |

## Assumptions and items to confirm

- The assignment gives no server address, staff subnet, guest subnet, interface, or assessor-specified service and port. Those values remain placeholders in the firewall materials and must be supplied by the assessor or authorised lab administrator.
- The report does not assert a successful breach, test, or deployment. Likelihood ratings are reasoned estimates based only on the stated scenario.
- Do not use real student records, production addresses, passwords, or encryption keys in the repository.
