# ARCH-02 bounded repair controls

Start: 2026-10-08 19:07:29 UTC. Hard stop: 19:27:29 UTC.
Base and HEAD: 864c6d3d6eb7b978c426327f877059e956a9e882.
Root captured the complete dirty status, exact before bytes and hashes in
`/tmp/uah-arch02-before`. Source ownership is restricted to observatory.py and
one new test_observatory_provenance.py file. No Git mutation is authorized.

This is the O1/H0-H1 read-only projection boundary. Observatory owns truthful
projection labels; measurement and independent gate owners remain outside O1.
The human selected rejection of unsupported measured/reviewed requests.

Agreed public seams: project_observatory and render_observatory. First red gate:
an ordinary raw event tuple requesting measured must raise ValueError rather
than produce an upgraded projection. Implement one local shared-seam check,
then expand controls without adding an evidence interface or store.

The rejection matrix covers measured/reviewed, enum/string form, ledger/raw
tuple/raw generator, empty/nonempty input, and project/render consumer.
Protected controls retain ledger recorded defaults/explicit recorded, explicit
conceptual/synthetic on both routes, raw synthetic defaults and raw recorded
rejection. Existing falsey-default and invalid-enum behavior remain unchanged.
Read-only controls compare file bytes, event payloads, graph JSON and projected
lineage across successful/rejected calls and ledger restart. Source identity,
versioned shape, detachment and O1 whitespace hygiene are not changed.

Acceptance requires the intended red failure, protected controls and rejection
matrix passing, focused/full tests, both current O1 freshness checks,
canonical-document synchronization and normal repository hooks. Independent
review is a separate root-owned gate. Green implementation tests do not close
the O1/H0/H1/H2 release exits.
