# R1 second-review report: provenance check

Date: 2026-10-08, checked at 16:44 Europe/Madrid. Read-only investigation.
Related [R1 receipt](2026-10-08_uah_r1_domain_pack_identity.md),
[R2 receipt](2026-10-08_uah_r2_catalog_semantic_fencing.md) and its
[exact pre-amendment round-close bytes](2026-10-08_uah_r2_catalog_round_close.md).

The R1 repair receipt names the second review document hash as
`d39502b9b65e03051925eb4cfe1596bf7cf725dfeb3763b26f8fe56a6e35f462`.
The retained report, R1 end manifest and later R2 start manifest agree instead
on `85a97f05f2ec16668acf7fc310277558908820bcd98d780416fc7ea469c6b284`.
Both values are retained; no historical receipt or review report was rewritten.

`rg --files --hidden /tmp` and the repository artifact inventory found no
retained original second-review document matching the earlier bytes. The R1
temporary review directory contains before-source and base-commit copies,
not the original report. The dashboard reviewer temporary copy already has
the later report hash. Removing or adding one final newline to the current
report produces neither the earlier hash:

| Read-only transformation | SHA-256 |
| --- | --- |
| Add one final newline | `578f4920442308e20b745f164654bcf6724389da3fa188c178bb2d1a1768ae1b` |
| Remove one final newline | `e1942e4869b79bfb665d4f5e2eb348eed83ab58d66250dc37f8a338449f020f7` |

These narrow checks do not reconstruct the original report. A byte comparison
cannot be completed without those bytes. The transformation and whether its
content was substantive remain unknown. Hook formatting is not established
as the cause and is not assumed harmless.

The report still records the same three reviewed runtime hashes as the repair
receipt, and current files retain those hashes. This limits the discrepancy to
retained report provenance as far as the available evidence shows; it does not
prove the report's wording was unchanged. Its later document hash identifies
the stored report, while the reviewed runtime hashes identify the repair scope.
No approval was rerun or inferred to conceal the discrepancy.
