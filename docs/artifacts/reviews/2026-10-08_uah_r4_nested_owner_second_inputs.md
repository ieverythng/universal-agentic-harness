# Independent nested-owner review inputs

Recorded before reading the five candidate files or their diff. The baseline is
the four exact-before files supplied by the parent; all unaffected dependencies
and test fixtures will be copied once, then used unchanged in both environments.

## Public controls and attacks

1. Run the public typed-proposal, two-stage lease, exact environment-owner
   execution, and common-ledger accepted restart controls on both trees before
   implementation inspection.
2. Round-trip a current admitted artifact and its lease. The reconstructed
   value, dispatch arguments, receipt binding and evidence owner must agree.
3. Change each nested binding field, object snapshot field, obligation field,
   and proposal argument or lineage field while preserving the old outer ID.
   Include two-field combinations and overridden instance serializers/verifiers.
   No altered authority may obtain execution or accepted evidence.
4. Supply missing, stale, mismatched, and incomplete admitted-object snapshots;
   reject current authority rather than inferring omitted information.
5. Mutate the caller's supplied admitted object inside the native handler.
   Either reject before dispatch or preserve one coherent canonical admitted
   value for dispatch, receipt issuance, evidence validation and replay.
6. Exercise an old concrete admitted object and fully marker-stripped historical
   metadata. Historical inspection may remain readable, but it must not acquire
   fresh lease, execution, receipt or accepted-evidence authority.
7. Exercise native-result failure/evidence rejection, duplicates, restart, and
   ordering controls through existing public tests. Units and dates are unchanged
   by this candidate; nested sequences include empty and multiple entries.

## Review boundaries

The scope permits mutations of concrete supplied object instances and their
fields or methods. It excludes arbitrary replacement of module symbols, class
methods, process memory or trusted runtime code. No source repairs, staging,
commits, provider calls or writer receipts are permitted.

Standards and specification will be reported separately. All five REVIEW.md
principles will be assessed. Missing evidence remains incomplete. Backend model
identity cannot be independently observed; any distinct-model designation is
the parent's requested configuration, not a verified runtime fact.
