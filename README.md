# Cryptography and Network Security Integrated Situation

ULK Polytechnic Institute - ETTCS801. This project includes the requested risk assessment, file encryption/integrity CLI, an authorised-lab firewall template, a transparent connection-test record, and the technical report source and PDF.

## Project structure

| File | Purpose |
|---|---|
| `risk_assessment.md` | Assets, vulnerabilities, ranked risks, reasons, and controls |
| `crypto_tool.py` | AES-256-GCM encrypt/decrypt and SHA-256 baseline/verification CLI |
| `crypto_tests.md` | Actual synthetic crypto test commands and observed outcomes |
| `requirements.txt` | Python dependency |
| `firewall.nft.template` | Routed nftables policy template requiring assessor values |
| `filter_tests.md` | Test procedure, expected results, and honest execution status |
| `technical_report.tex`, `technical_report.pdf` | Editable LaTeX report source and typeset PDF companion |
| `.gitignore` | Excludes key and generated sensitive data files |

## Install

Use Python 3.10 or newer. From this project directory, create and activate a virtual environment, then install the dependency:

```sh
python -m venv .venv
# macOS/Linux:
source .venv/bin/activate
# Windows PowerShell instead:
# .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Reproduce the crypto demonstration

Use only synthetic sample data. Put it outside this repository; for example, create `sample.txt` in a temporary working directory. Create the key in a secure location outside the repository. On macOS/Linux:

```sh
python /path/to/cryptography-network-security-exam/crypto_tool.py keygen --key "$HOME/.ulk-lab/records.key"
python /path/to/cryptography-network-security-exam/crypto_tool.py encrypt sample.txt sample.enc --key "$HOME/.ulk-lab/records.key"
python /path/to/cryptography-network-security-exam/crypto_tool.py decrypt sample.enc recovered.txt --key "$HOME/.ulk-lab/records.key"
python /path/to/cryptography-network-security-exam/crypto_tool.py hash sample.txt --out sample.sha256.json
python /path/to/cryptography-network-security-exam/crypto_tool.py verify sample.txt sample.sha256.json
```

For PowerShell, use the corresponding key location outside the repository, such as `$env:USERPROFILE\.ulk-lab\records.key`, and the same commands with that path. Outputs refuse to overwrite files; choose fresh output names for each run. AES-GCM authenticates ciphertext during decryption. The separate SHA-256 JSON baseline detects later changes only if the baseline itself is protected and trusted; a hash is not a digital signature.

The actual synthetic crypto checks and outcomes from this project build are recorded in `crypto_tests.md`. To demonstrate detection yourself, edit or copy the synthetic source after saving its baseline, then run `verify` on the changed file. Expected result: `MISMATCH` and exit status 1. Missing files, malformed key files, malformed encrypted data, invalid hash records, and attempts to overwrite outputs are reported as concise errors (exit status 2); they do not produce a traceback for expected input errors.

## Firewall configuration and reproduction

`firewall.nft.template` is intentionally not directly deployable. Obtain the server IP, staff and guest CIDRs, interface, and assessor-approved protocol/service/port from the authorised lab administrator. Replace every `__...__` placeholder, confirm the approved protocol is supported by the nftables `th` transport-header expression on the lab version, and have the administrator validate and review the policy before applying it. It is a Linux nftables **routed gateway** example; it is not suitable unchanged for a host firewall or a different firewall platform. Guest traffic must route through this gateway; if clients share a layer-2 segment with the server, an appropriate switch or host control is also required. Policy defaults to drop, denies guest-to-server traffic before established-flow acceptance, permits the approved staff-to-service flow, and denies other sources to that service.

Follow `filter_tests.md` only inside the authorised lab. It records expected results, not executed results. Add timestamped actual outcomes and evidence only after running the permitted and two blocked tests. Never probe production networks or addresses without explicit authorisation.

## Report and submission

The report source is `technical_report.tex`; the PDF companion is `technical_report.pdf`. The built-in LaTeX compiler could not start in this environment, so the provided PDF is a visually typeset rendering from the same report content, not a verified compilation of the `.tex` source. Compile the `.tex` source in a working LaTeX environment and replace the companion PDF before submission if the assessor requires a compiled PDF. Replace student-identifying fields if required by the course, and update the report only after real tests are complete. The PDF conclusion includes an explicit placeholder for the repository URL. Create the repository under the assignment's requested name `cryptography-network-security-exam`, review the final files, then commit and push using the student's own GitHub account. No repository has been created or pushed by this project build. Email the resulting URL to the address specified on the assignment sheet, and submit both report formats to the class representative.

Do not commit keys, real records, passwords, or credentials. `.gitignore` is a safeguard, not a substitute for checking staged files before pushing.
