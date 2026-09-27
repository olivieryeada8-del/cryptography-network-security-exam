# Firewall Test Plan and Evidence

## Status

**Not executed.** This package contains a template and reproducible test plan only. The assignment supplies no lab addresses, interface, or approved service/port, and this workspace is not connected to the authorised lab. No actual pass/fail results are claimed.

## Values required before testing

Obtain these from the assessor or lab administrator and fill the placeholders in `firewall.nft.template` and the commands below:

- Records server IPv4 address: `__RECORDS_SERVER_IP__`
- Staff source subnet: `__STAFF_CIDR__`
- Guest source subnet: `__GUEST_CIDR__`
- Laboratory gateway interface: `__LAB_INTERFACE__`
- Assessor-approved service and transport protocol: `__ASSESSOR_APPROVED_PROTOCOL__`
- Assessor-approved service port: `__ASSESSOR_APPROVED_PORT__`
- Lab client addresses within staff and guest subnets: `__STAFF_CLIENT_IP__`, `__GUEST_CLIENT_IP__`
- Address of the authorised third test client outside the staff subnet: `__OTHER_CLIENT_IP__`

## Safe execution procedure

1. Confirm written authorisation and use only the isolated laboratory network.
2. Have the lab administrator replace all placeholders, validate the resulting file with `sudo nft -c -f firewall.nft`, review the current ruleset, and apply only the reviewed file with `sudo nft -f firewall.nft`.
3. Confirm the loaded rules with `sudo nft list table inet ulk_lab_filter`. Prepare a listener for the assessor-approved service on the records server.
4. Run each connection test from the named client. Use the exact protocol/client utility that matches the service specified by the assessor (the TCP examples below do not apply if the approved service uses another transport).
5. Record timestamp, client/subnet, command, observed result, and relevant server/firewall log evidence in the actual-results column. Restore the lab state as instructed by its administrator.

## Required connection tests

Substitute literal approved values before execution. `nc -vz -w 3` is a TCP example only and must be replaced with a suitable client command if the assessor specifies another transport protocol.

| Test | Source | Command template | Expected result | Actual result |
|---|---|---|---|---|
| Permitted | Authorised staff client | `nc -vz -w 3 __RECORDS_SERVER_IP__ __ASSESSOR_APPROVED_PORT__` | Connection succeeds while the approved service is listening. | **Not executed - pending authorised lab access and values.** |
| Blocked 1 | Guest client | `nc -vz -w 3 __RECORDS_SERVER_IP__ __ASSESSOR_APPROVED_PORT__` | Connection fails or times out; firewall counter/log evidence confirms guest denial. | **Not executed - pending authorised lab access and values.** |
| Blocked 2 | Client outside the authorised staff subnet | `nc -vz -w 3 __RECORDS_SERVER_IP__ __ASSESSOR_APPROVED_PORT__` | Connection fails or times out; firewall counter/log evidence confirms denial. | **Not executed - pending authorised lab access and values.** |

Do not convert expected outcomes into actual results until the tests have been run and evidence recorded.
