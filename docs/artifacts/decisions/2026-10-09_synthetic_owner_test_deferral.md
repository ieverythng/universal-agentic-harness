# Synthetic notes-owner test deferral

Date: 2026-10-09 (Europe/Madrid). Decision owner: human, relayed by GRILL under
CHECK-AUDIT-03, request AUDIT03-SYNTHETIC.

The human selected: "Defer the orphan synthetic test; keep NAO-first
(Recommended)". The checkpoint commits tests/test_synthetic_notes_owner.py but
does not commit the ab_harness_synthetic package it imports. Strict committed-
tree execution fails test collection. The earlier 724-test pass used the
shared interpreter's editable installation and is not committed-tree evidence.

This change removes only the orphan test from active collection. It does not
skip, xfail, ignore collection errors, or import source from the working tree.
The exact original test remains in Git history at
`0fd09174e95c536b44bcc22bace8f462cf5b58de:tests/test_synthetic_notes_owner.py`.
Original Git blob: `3552e377c06d1218d9d4e1a804213b947b4b374a`.
Original SHA256: `2391e2273d9c97cf43871025fbcee4e0b1c2df35ec460e0453a005cbe6391e36`.
Recover its unchanged bytes with:

```bash
git show 0fd09174e95c536b44bcc22bace8f462cf5b58de:tests/test_synthetic_notes_owner.py
```

The shared untracked synthetic package is untouched and remains unreviewed.
The original checkpoint is still the frozen independent-audit target; this
deferral cannot make that original commit clean retroactively.

## Re-enable condition

Reintroduce the exact preserved test when the synthetic domain package and its
native-owner boundaries have completed owner repair and fresh independent
high-risk review, and all imported source is committed together. Freeze the
source/test identity, execute without editable fallbacks, and pass the normal
hooks against that complete committed tree. If accepted contracts require a
changed test, review that behavioral change separately rather than weakening
the oracle to follow the implementation.

H0/H1 synthetic conformance and release exit requirements remain open and
unchanged. NAO-first is an implementation priority, not an exemption from those
requirements. This deferral neither qualifies H2 parity nor approves the
synthetic source. Refer to the canonical
[masterplan](../../plans/universal_agentic_harness_masterplan.md) for release
criteria and [REVIEW.md](../../../REVIEW.md) for independent-review gates.
