# Executable review counterexamples

These scripts preserve independent reviewer probes for the 2026-10-05 H0/H1
review. They exercise synthetic inputs and temporary files. They do not call a
provider, mutate a real environment, or edit this repository's runtime code.
The cache probe creates and commits only inside its own temporary Git repository.

Run from the repository root with its existing virtual environment:

```bash
PYTHONPATH=src .venv/bin/python docs/artifacts/reviews/2026-10-05_uah_review_repros/standards_domain_tamper.py
PYTHONPATH=src .venv/bin/python docs/artifacts/reviews/2026-10-05_uah_review_repros/standards_push_cache.py "$PWD"
PYTHONPATH=src .venv/bin/python docs/artifacts/reviews/2026-10-05_uah_review_repros/standards_event_tamper.py
PYTHONPATH=src .venv/bin/python docs/artifacts/reviews/2026-10-05_uah_review_repros/spec_probes.py
PYTHONPATH=src .venv/bin/python docs/artifacts/reviews/2026-10-05_uah_review_repros/observatory_probes.py
PYTHONPATH=src .venv/bin/python docs/artifacts/reviews/2026-10-05_uah_review_repros/prompt_scope_probe.py
```

A zero script exit code means the diagnostic ran. It does not mean the behavior
passed its acceptance gate. The scripts print counterexamples rather than
asserting corrected behavior. Convert the relevant counterexample into a red
regression test when its fix is authorized.

## Dependencies and adaptations

The compiler and admission probes use existing test fixture builders for setup,
then call the public compiler, admission, owner, and ledger interfaces. The
budget probe reads the fixture registry's ledger solely to recover setup state;
the altered value is an event returned through public `LifecycleLedger.events()`.
The prompt probe substitutes fixture constructors to construct a new legitimate
AB object and task prohibition. It does not patch production methods.

Saved copies were formatted and, where necessary, their fixture paths were made
repository-relative. Imports in the Spec probe use `runpy` instead of modifying
`sys.path`. The parent reran the adapted copies and observed the same failures.
Inputs and owning production paths remain unchanged.

## Expected observations at the reviewed snapshot

| Probe | Expected gate | Actual snapshot result |
|---|---|---|
| Domain policy mutation | Reject stale revision/content | Retryable obligation under unchanged revision |
| Raw task start | Reject unadmitted lineage | Fabricated start and compiled task survive reload |
| Binding catalog drift | Reject object outside compiled semantics | Prohibited `direct_speech` observed, terminal accepted |
| Returned event mutation | Reject stale content ID | O1 shows recorded acceptance; budget permits 4 against 3 |
| Push cache | Reject untested outgoing tree | Broken committed Python, cache check exits 0 |
| Prompt operation scope | Expose only semantically eligible operations | Prompt exposes operation rejected for prohibited observable effect |
| Observatory label probe | Preserve distinction between evidence classes | Raw iterable accepts `measured` and `reviewed` labels |

These outcomes apply to the content hashes in the review scope, not to a future
fixed tree. The base archive has no equivalent compiler, common ledger, H1
prompt compiler, O1 renderer, or cache interface. Missing interfaces are reported
as unavailable, not as successful parity tests.
