# Cryptography Toolkit Test Evidence

These checks were executed locally on 2026-09-27 using a temporary synthetic record and a temporary key stored outside the project. No real student data or key was used. Commands below use generic paths; generated outputs are intentionally not included in the repository.

## Commands

```sh
python crypto_tool.py keygen --key /secure/outside/repository/records.key
python crypto_tool.py encrypt sample.txt sample.enc --key /secure/outside/repository/records.key
python crypto_tool.py decrypt sample.enc recovered.txt --key /secure/outside/repository/records.key
python crypto_tool.py hash sample.txt --out sample.sha256.json
python crypto_tool.py verify sample.txt sample.sha256.json
# Change sample.txt after saving the baseline, then:
python crypto_tool.py verify sample.txt sample.sha256.json
python crypto_tool.py encrypt missing.txt missing.enc --key /secure/outside/repository/records.key
python crypto_tool.py decrypt malformed.enc malformed.out --key /secure/outside/repository/records.key
```

## Actual outcomes

| Check | Observed result | Exit status |
|---|---|---:|
| Generate key | Created a 256-bit key in the temporary directory outside the project | 0 |
| Encrypt synthetic sample | AES-256-GCM encrypted output created | 0 |
| Decrypt encrypted sample | AES-GCM authentication passed; recovered bytes equalled the original | 0 |
| Save SHA-256 baseline | JSON baseline saved | 0 |
| Verify unchanged sample | `MATCH` | 0 |
| Verify modified sample | `MISMATCH` | 1 |
| Encrypt missing input | Concise `Input file not found` error; no traceback | 2 |
| Decrypt malformed ciphertext | Concise invalid-format error; no traceback | 2 |

Firewall connection tests are documented separately in `filter_tests.md` and were **not executed**.
