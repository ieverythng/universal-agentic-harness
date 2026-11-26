# Historical replay candidates — private custody, not publication approval

This exact four-retained-stream subset plus one explicitly new old-producer stream accompanies the public-seam
[regression tests](<../../test_historical_replay_regression.py>). These are
fake-owner test traces, not measured robot, hardware, provider, or H2 evidence.
Tests open scratch copies only. No archived session/configuration/review/log tree
is included.

## Exact original bytes

| Stream | Bytes | Events | SHA-256 |
| --- | ---: | ---: | --- |
| [H2EV](<baseline-public-ledger.jsonl>) | 2303 | 2 | 3fa6f142bc300f87b9653f8db7fadbdcae73223e7e29cd48e6880316ce91b5e5 |
| [HA](<base-accepted.jsonl>) | 12370 | 10 | 4c0b970c1d2d0687745e9f2acf84b028b885f82bfd29f51b12218e7ddfb4f0b9 |
| [HB](<base-nao-ledger.jsonl>) | 12372 | 10 | 1994743080033c29ec7e93f5714e30da83373c52d32e8e4d2fe509261c609de7 |
| [C11](<current-nao-ledger.jsonl>) | 16617 | 11 | dfef58c0a4827e2f584e9b23184ed4c458f717a0215ae68ec591e1b33baf43b3 |
| [N7 — NEW Nov11 pinned-old-producer failure](<new-nov11-pinned-old-execution-failed.jsonl>) | 8326 | 7 | f6e006bb49ff66537b550125ac6e1146ad203646ae7ef15b29e8fb113855a601 |

H2EV is the retained October 8 public start/compile stream. HA is the single
selected JSONL member of the retained October 9 Standards archive (34789 bytes,
SHA-256 3162296baddceaa619ae69ba3a15d604514839e08ae58215e7ed1a65a1ede517).
HB and C11 are the two selected JSONL members of the retained Spec archive
(21963 bytes, SHA-256 0888b20455157abaf8a3d3d0a54fbea71d5aa04b6e32d24195ea149e0c96e9e1).
Selected archive member names exactly match their destination basenames above.
Archive and selected member hashes were reverified before copying. No producer
was rerun to create those four retained streams. Exact local custody locations and source-cited evidence are retained
in the separate private preparation handoff, not embedded as host dependencies.

Historical producer pin: 06f5a29daef9bb877fb08b6c6ee47d870df94d71.
The original Spec receipt identifies its current producer snapshot as
0fd09174e95c536b44bcc22bace8f462cf5b58de. These producer records are not a claim
that their entire source snapshots are accepted product source. Tests were
prepared against merged base 5e6734173f2f755430f85e2fbe7d937bfbaa8b7d.

H2EV records environment `environment:review`, task `task:review`,
and the leap-day fixture clock 2024-02-29T23:59:00Z. HA/HB/C11 share environment
`environment-run:nao-recorded:001`, task `find_the_cup`,
and clock 2026-09-28T10:00:01Z. Recorded timestamps are fixture data, not asserted
generation times. HA evidence reference is `review://historical`;
HB/C11 use `probe:owner-evidence`. These identifiers and exact bytes remain
private candidates pending explicit owner review; no sanitization was applied.

HA original recorded digest is
`verified-trace-digest:sha256:c10fb8218a46f99184db39d0dd99dbb26c350a339a64836e57165f72ce501a3d`.
C11 recorded control digest is
`verified-trace-digest:sha256:c26202fdaa0218e3fcb85fade644a386596fad117b0282c8f0088544a12fec27`.
HB has recorded accepted-history provenance, but no independently pinned original
digest in this preparation; its test checks accepted replay and restart equality,
not an invented expected digest. Historical missing budget/failure policy stays
unavailable; no grants, actors, retry policy, or effect evidence may be fabricated.

## Contract and qualification boundaries

The [foundation](<../../../docs/architecture/universal_agentic_harness_foundation.md#L850-L861>)
requires historical readability without fresh compilation authority; trusted
runtime ledger-file custody remains an assumption. The
[H0-C2 crosswalk](<../../../docs/plans/universal_agentic_harness_masterplan.md#L473-L489>)
keeps authentic provenance and strict fresh-use qualification open. Public
LifecycleLedger construction, events, replay, registry require_start, budget
assessment/consumption and read-only Observatory are the tested seams.

Original streams are never mutated. Scratch prefix tests use complete original
commit boundaries and are explicitly partial inspections, not new historical
fixtures. Downgrade/corruption inputs are explicitly altered scratch adversaries;
the new current failure is generated through the current public ledger API,
not mislabeled recovered failed history. N7 was newly generated November 11
through unmodified public admission, leasing and deterministic fake-owner failure
on producer 06f5a29daef9bb877fb08b6c6ee47d870df94d71. It is NOT retained
October failure history. Its source receipt records two old-reader reopens, exact
bytes and consumed-lease rejection. Environment/task identifiers explicitly name
new-nov11-rerecord; the injected clock 2026-11-11T01:20:00Z is fixture data.
The operation failed, but the task remains OPEN and its digest is null; no retry
policy, terminal judgment, budget or effect evidence was supplied or inferred.
All seven events and their original lineage are retained. The retained-time
failure evidence gap remains open. Issuer containment for resume AND notify remains TODO pending
public rejection cases paired with legitimate admit controls. No source-risk
observation is promoted to an exploit claim. H0/H1/O1/H2 remain open.

## License, privacy, and transfer gate

The repository [license](<../../../LICENSE>) is BSD-3-Clause, copyright 2026
Universal Agentic Harness contributors; SHA-256
0734bd3f6d7070f18761eae9c47b92768439df54739e50b46d285be415d3d83c,
Git blob 5144774618aca761c3a3e2a967e98d734e5aa05a at both merged and historical
producer pins. Retain its copyright, conditions, and disclaimer on any approved
redistribution. Neither retained archive supplies a separate per-fixture license
or redistribution declaration. License continuity is NOT proof of permission to
publish quarantined private artifacts.

GRILL/owner must approve the exact subset, identifier/native-lineage/evidence-ref
privacy, original-custodian permission, and license/provenance notices before
transfer or publication. Whole private archives must not be vendored. These
candidates are unstaged, uncommitted, unpublished, and not accepted source.
Fresh exact Astra/medium plus Sol/high review remains required; a writer
checklist is not independent approval. Five exact ignore exceptions identify only
these curated JSONLs; they grant no publication or transfer rights. Private use
and proposal of this exact subset are authorized; external publication and
source transfer remain separate owner/review decisions.
