# AgentLint mapping to UAH guardrails and review effort

Date: 2026-10-08. Research-only pass began approximately 21:02 Madrid
(19:02 UTC); hard stop 21:22 Madrid (19:22 UTC). First clock receipt:
19:04:13 UTC. Measurements use a worktree copy made around 19:05 UTC.
Status: source-inspected assessment and measured Python-native static pilot.
No AgentLint installation/execution, hook adoption, skill mutation, REVIEW
change, independent implementation approval or release qualification.

Owner: DEV owns development tooling; the human owns exceptions and any review
policy change. This supports H0/H1/H2 development checks without changing their
exits. AgentLint must stay outside the portable runtime. No H3 promotion follows.

## Recommendation

Use automatic hard checks for mechanically decidable constraints and a separate
review-obligation queue for risky changes. Keep complexity/deslop suggestions
advisory until calibrated. Start with Python-native tooling already available;
evaluate AgentLint itself later for one language-agnostic change obligation.

AgentLint provides a useful standard/detector/binding model and exact-evidence
decision records. It does not supply a UAH rule pack, Python syntax analysis or
an independent reviewer. A clear queue can reduce repeated triage, but no human
review-time reduction is measured here. Runtime evidence/replay controls and
fresh independent REVIEW gates remain mandatory.

## Upstream identity and capability

Authenticated GitHub `user/starred` identified
[aurelienbobenrieth/agentlint](https://github.com/aurelienbobenrieth/agentlint).
Primary-source audit pins main to
`4d933d3e18a2907c3914006054973745de98fceb`.
The observed release is [v0.7.0](https://github.com/aurelienbobenrieth/agentlint/releases/tag/v0.7.0),
tag commit `593155254a4df3a19dda501460edc5bfbdc3442b`.
Main is two documentation/demo-oriented commits ahead; source comparison found
the inspected engine/action bytes unchanged. npm installation, published bytes
and release-asset digest were not independently verified.

| Property | Source-confirmed behavior | UAH consequence |
| --- | --- | --- |
| Runtime/license | MIT; Node >=22.19.0; TypeScript configuration; Git change evidence | Development dependency only; local Node v22.22.2 meets the declared minimum |
| Rules | No bundled production rules; demo rules illustrate queries, payments, focused tests, eval, privacy, migration and privilege changes | Every UAH standard, detector, scope and fixture must be authored and reviewed |
| State parsing | JS/TS/TSX/JSON grammars, not Python; unsupported extensions are skipped | A Python glob can yield zero findings without Python validation |
| Change rules | Synchronous imperative TypeScript detector over before/after Git changes | Can trigger on Python paths/text; does not establish Python AST/type semantics |
| Gate | Configured current findings require compatible recorded decisions | Zero unresolved findings means scoped decision completeness, not semantic correctness |
| Fixtures | Positive/silent cases replay twice; zero-fixture rules are skipped and may exit 0 | Require nonempty positive/negative fixtures and declared coverage separately |
| Records | Standard revision, detector version, binding digest, fingerprint, epoch and sufficient authority | Useful explicit review debt/invalidation; no automatic transitive dependency coverage |
| Check writes | Full check updates cache and can migrate/prune acceptances and proposals | Never call it read-only; disposable pilot repository required |

Sources: [package manifest][manifest], [empty starter rules][init],
[language map][language], [scan omission][scan], [fixture gate][fixtures],
[rule authoring][rules], [acceptance identity][acceptance], [check writes][check].

Matching needs no model or provider key. The engine has no network evaluation
path, but TS config and imperative detectors are trusted code evaluated
in-process. They can perform side effects themselves. Installs and optional PR
integrations contact external services. Detached review artifacts contain full
source and reasons without sanitization; do not publish them merely because the
engine is local. Acceptance timestamps and lock/server operations use time or
randomness; deterministic findings/expiry do not depend on wall-clock age.
Sources: [security model][security], [guarantees][guarantees].

## Authority and enforcement limits

Local `approve` checks a `human:` actor prefix; `AGENTLINT_ACTOR` overrides
inference. Repository writers can edit the acceptance store or policy. Upstream
documents local authority as accountability, not authenticated identity. The
GitHub integration checks commenter write permission, not independence from the
change author. Neither substitutes for UAH's fresh reviewer or second-model
high-risk gate. Sources: [actor override][actor], [approval check][approve],
[security][security], [GitHub permission checks][ghpermission].

Hard runtime invariants must not become agent-acceptable exceptions. Keep
mechanical failures in pytest/Ruff even if AgentLint later records a separate
review reason. A reviewer acceptance cannot authorize model effects, widen a
role, approve a candidate binding or certify measurement provenance. Rules,
binding scope, epochs, ignore patterns and acceptance files are themselves
review-sensitive inputs.

No upstream pre-commit manifest was found. A local hook would need an explicit
CLI wrapper. Its full working-tree/change scan is not equivalent to the exact
staged commit; pass explicit comparison identity and distinguish working tree,
index and committed bodies. Partial scopes cannot imply complete review.

The advertised Stop adapter is feedback: missing package skips the gate, an
already-blocked stop can end, and shell edits are not recognized. Current app
compatibility was not tested. The GitHub action does not itself run fixture
tests, and a repository-installed engine can override the requested package
version with a warning. A future pilot must verify actual binary/dependency
identity, not merely action SHA. Sources: [CI guide][ci], [Stop adapter][stop],
[action scan][actionscan], [installed-engine precedence][engineprecedence].

The existing [CI workflow](../../../.github/workflows/ci.yml) runs Ruff, pytest
and generated-document checks on Python 3.10/3.12/3.13. The
[pre-commit configuration](../../../.pre-commit-config.yaml) already runs hygiene,
default Ruff, source tests and document synchronization. The pre-push cache
compares current file bytes/modes, not reviewer coverage or a commit-only scope.

At 19:09 UTC read-only GitHub API queries returned no repository rulesets and
`main.protected=false`, with required checks disabled. This is an observed
remote configuration, not a change request executed here. Local pre-commit can
be bypassed with `--no-verify`; enforce-at-merge requires separately authorized
required checks/protected policy. Source: [Git hook documentation](https://git-scm.com/docs/githooks#_pre_commit).
Do not weaken or replace existing hooks to add another layer.

## Mapping the skills to automatable obligations

The named [guardrails](../../../.codex/skills/uah-guardrails/SKILL.md) own semantic
authority; [deslop](../../../.codex/skills/deslop-refactor/SKILL.md) and its
[manual](../../../.codex/skills/deslop-refactor/references/deslop-operating-manual.md)
favor behavior preservation and concept-local simplification. The following is
a proposed mapping, not accepted policy:

| Obligation | Useful automatic layer | Still requires deeper evidence |
| --- | --- | --- |
| No ROS/NAO/provider/runtime imports in core | Expanded Python AST import boundary, with aliases/nested imports and explicit dependency policy | Dynamic/transitive imports, unknown SDK roots and clean-install/runtime conformance |
| Core lifecycle owns writes; registry/O1 remain projections | Changed-path triggers and direct forbidden-call shapes where stable | Actual writer authority, aliasing, lock/reload/append/fsync transaction and no second store |
| Reverify concrete/nested authority artifacts | Trigger changes to identity, normalization, admission and consumer seams | Forged verifier methods, self-consistent fabricated hashes, nested mutation and active/replay counterexamples |
| Proposal/admission/lease/effect/acceptance separation | Route sensitive changes to Spec and owner reviewers | Lease-only owner calls, zero shadow dispatch, correct evidence and terminal closure |
| Registration never invokes a model | Local direct-call checks as limited signals | Hidden helper/provider paths, capacity/readiness ownership and invocation accounting tests |
| AB coordinates remain frame-relative | Schema/enum invariants and API-change triggers | Cross-frame semantic equivalence and allowed delegation |
| O1 labels/evidence claims stay truthful | Enum-consumer/risk triggers plus targeted label tests | Evaluator/gate scope, mixed populations, historical versus current qualification |
| Adaptive structures stay quarantined | Changes to promotion/binding/evaluator policy trigger owner review | Held-out replay, provenance, rollback and candidate nonauthority |
| KISS/cognitive load/fail-fast | Ruff complexity/branch/statement diagnostics; existing error checks | Whether simplifying moves or duplicates domain authority |
| DRY/YAGNI/separation of concerns | Optional duplicate/dead-code suggestions | Same concept versus similar syntax; no shared codec solely because hashes resemble each other |
| No churn in generated/vendor/nested repos | Explicit detector scopes and excluded suggestion surfaces | Source/docs consistency and legitimate owner-local exceptions |
| Review coverage and current bytes agree | Exact manifests/comparison IDs; changes to policy/acceptances trigger review | Fresh independent Standards/Spec verdicts and high-risk second-model coverage |

Recommended layers: hard deterministic failure, review-required signal, and
advisory maintainability suggestion. None is a capability/intelligence score.
A risk trigger nominates review scope; it does not automatically issue APPROVE.

Exclusions must be per detector. Complexity suggestions should normally cover
first-party `src/ab_harness` and `src/ab_harness_nao`, not tests, generated HTML,
dated receipts, vendored skills, build/cache/venv outputs or independent NAO/
Workbench repositories. Hard core import checks still cover all core source,
including nested imports. Test/policy deletions must remain visible to change
rules; exclusions must not hide authority-rule changes. The deferred synthetic
adapter is not qualified by its inclusion in this measurement.

## Measured Python-native baseline

These are newly executed static measurements, not AgentLint results. Source
was copied into `/tmp/uah-agentlint-measure-epv03i` while DEV changed the shared
tree. The snapshot is internally fixed for these probes, not an atomic whole-
repository freeze or independently reviewed candidate. Later observed shared
HEAD was `864c6d3d6eb7b978c426327f877059e956a9e882`; that does not identify every
copied dirty byte. Scope: 31 core files, 39 source files, 13,433 source lines.
Hashes for the exact scanned source appear in the appendix.

The existing [boundary test](../../../tests/test_package_boundaries.py) scans
Python Import/ImportFrom nodes only for `ab_harness_nao`. Its frozen public test
passed (1 test, 0.14 seconds). A temporary expanded literal-root detector used
Python stdlib AST and did not import/execute any scanned module.

| Control family | Existing test shape | Temporary expanded detector |
| --- | --- | --- |
| Three permitted snippets (stdlib, import text literal, relative core import) | 3 silent | 3 silent |
| Three adapter imports (direct, alias, from-import) | 3 caught | 3 caught |
| Four prohibited ROS/provider/robot imports (direct, alias, TYPE_CHECKING, nested function) | 0 caught | 4 caught |
| Four documented limits (dynamic __import__, importlib, unknown provider root, relative transitive import) | Not qualified | 0 caught |

This is seven deliberate violations and three permitted controls, not an
independently selected holdout or real-world precision/recall estimate. The
candidate matched all ten expected control outcomes but missed all four explicit
limitation examples. Both detectors found zero direct violations in the frozen
core. A finite forbidden-root catalog cannot establish universal portability.

Ruff 0.15.22, `--isolated --select C901,PLR0912,PLR0915`, scanned source only:

| Rule | Signals |
| --- | --- |
| C901 (complexity >10) | 23 |
| PLR0912 (branches >12) | 11 |
| PLR0915 (statements >50) | 5 |
| Total | 39 signals at 23 distinct function locations across 12 files |

The first invocation took 0.0605 seconds and a repeat took 0.0384 seconds,
including subprocess overhead. Findings/source hashes were identical. This is
two local observations, not a hardware-scalability benchmark or measured review
saving. A simple-function control was silent; a fifteen-if control raised
C901/PLR0912. Default Ruff on copied src/tests/scripts passed.

`apply_agent_event` scored complexity 37; `_event_specs` scored 32. Reading their
bodies shows event-family dispatch and lineage/authority validation. These
signals are not confirmed slop defects. Moving checks to satisfy thresholds can
scatter one owner's transaction or duplicate policy. Deduplicate diagnostics
by function and inspect changed sensitive functions first. Do not create 39
automatic blocking demands or refactor historical complexity indiscriminately.
Sources for rule meaning: [Ruff C901](https://docs.astral.sh/ruff/rules/complex-structure/),
[Ruff branches](https://docs.astral.sh/ruff/rules/too-many-branches/).

No actual AgentLint latency, RSS, throughput, full detector cost, rule-noise
precision or manual reviewer time is measured. Local engine use needs no model
tokens/GPU; configuration/rule/package trust and Node maintenance remain costs.

## Smallest separately authorized adoption

First unit: extend the existing Python boundary test rather than introduce a
Node-based runtime-policy framework. Freeze one reviewed forbidden dependency
policy; test direct/aliased/from/nested imports, comments/text controls, and
explicit handling or declared limits for dynamic imports. Add a fail-closed
syntax/input error path, keep approved portability controls, and retain existing
CI/pre-commit commands. Owner DEV; independent review still required. No generic
waiver store is needed for this invariant.

Second, separate unit: one advisory/report-only sensitive-path change trigger
plus opt-in Ruff complexity report. Protect identity/admission/lease/ledger/
acceptance/invocation/O1/promotion seams, REVIEW, skills, hooks, detector config,
ignore patterns and acceptance records. State the required reviewer/owner and
protected public controls. Base policy and comparison bytes must be trusted;
a changed branch config must not erase its own review requirement.

If the UI/exception workflow is useful, a subsequent disposable AgentLint pilot
can author one change rule for those review obligations, with explicit positive,
negative, deletion, rename, scope and evidence-invalidation fixtures. Verify
nonempty coverage and actual installed engine identity. Do not execute arbitrary
PR configuration with secrets/write tokens, or enable its auto-commit approval
action incidentally. Do not modify REVIEW or skill wording in these units.

Before claiming less human effort, compare representative tasks under current
instructions, explicit surfaced standards, and the new triage/gate. Record useful
interceptions, escaped concerns, unnecessary review, authoring/maintenance time,
human minutes and invalidation churn. Proposed small pilot: five comparable
owner-local changes, no live effects, preserve full independent review, report
all misses. Keep/refine/remove based on observed net effort and safety, not lint
counts. Upstream [pilot worksheet][pilot] makes the same measurement distinction.

## Validation and handoff

Executed on the isolated copy: default Ruff passed; the existing import-boundary
test passed; renderer --check passed (12 metadata records); static controls and
repeat findings above are measured. Full repository hook validation for this
new artifact passed in a disposable local clone overlaid with the frozen source,
tests and docs, including this note. Hygiene, Ruff, source tests and generated-doc
synchronization passed; only that clone's pre-commit cache/index were changed.
A separate timed diagnostic replay on the same copy reported 549 passed in
12.02 seconds. These are snapshot-specific results, not current staged-tree
approval. No shared hooks or index writes ran. The shared worktree/index and all
earlier research notes are preserved. No runtime/hook/review-policy implementation
or external GitHub configuration change is part of this research.

One upstream primary-source leaf wrote a temporary audit; root integrated this
single dated repository note. GRILL and DEV received material findings. The
existing independent-review contract and release gates are unchanged.

After the historical HEAD observation above, DEV's separately directed commit
correction returned the shared HEAD to06f5a29 and retained an exact13-file staged
selection. This research does not certify that selection or ARCH-02 closure.
Shared writes were held during the correction and resumed only after GRILL
explicitly released the boundary. The new human coordination rule reserves all
subsequent inter-chat orchestration to GRILL; earlier DEV messages are historical.

## Reproduction and frozen source appendix

Temporary probe source SHA-256:
`a857ba28ec493b9431d30f2678d73f3dd92bac85e3d7bbfa815969d63ad5dc98`.

Commands executed:

```sh
/home/juanbeck/universal-agentic-harness/.venv/bin/python /tmp/uah-agentlint-measure-epv03i/measure_static_signals.py
/home/juanbeck/universal-agentic-harness/.venv/bin/python -m ruff check --isolated src tests scripts
/home/juanbeck/universal-agentic-harness/.venv/bin/python -m pytest -q tests/test_package_boundaries.py::test_kernel_does_not_import_the_nao_adapter_package
/home/juanbeck/universal-agentic-harness/.venv/bin/python scripts/render_agentic_harness_docs.py --check
```

The last three commands used the isolated-copy working directory. Frozen source
manifest, not current committed-source certification:

```json
{
  "src/ab_harness/__init__.py": "b474e909cc3f1ca5265c0478c5cd23702e58bc58b8af88b05f5892f9d0e7e044",
  "src/ab_harness/acceptance.py": "0d26d594f073ef1fc89061703b3149ce670ac8b3e58350d10b15e9f66961ac4a",
  "src/ab_harness/agent_configuration.py": "52e8954f458405ac11414a20003a04044e0756f279416e5b9c287aa1a7e3ab32",
  "src/ab_harness/agent_identity.py": "8b5f37bf37bc6207d3138645b469bc14c755bb137b0c86fd133404c03fc074b5",
  "src/ab_harness/agent_lifecycle.py": "dba37f9b3d2b7ac89ac25234a22ae2ed6cd8a54fd485b52b5d81222991292e36",
  "src/ab_harness/bindings.py": "1492eb91866ed67b1691ecdbe95c5307efcaefdfd3bd8daa595c53af90fca33d",
  "src/ab_harness/configuration.py": "28ea7d1a6b204436d50f9886531d9da99ca6d932def246f142ea48c71c732942",
  "src/ab_harness/contracts.py": "bacb7c0098851ffd4235000005a86dc3d519cf099ee9f9e86633f29e0419047d",
  "src/ab_harness/domain_contracts.py": "b47e522c1184786170df1d9f3bbbfb7398c340e44a7b44a514312a8da17baf1c",
  "src/ab_harness/domain_lifecycle.py": "48de0478d577b58567483f5fa22334f641a32855f32a240944b91346906dff6f",
  "src/ab_harness/environment.py": "9fd718a1d663dcc2bfe844a4b289f4191aaa90f520fe36215df5331e52047248",
  "src/ab_harness/environment_ingress.py": "34cf1d9afd8c31f3f677292f8e0454e804d6897ead0d64393ca29817dc38fdfc",
  "src/ab_harness/environment_profiles.py": "9f63227dbe37c0421e3d76bd8581d245e89176dbcbb1fa68e1841eb053784584",
  "src/ab_harness/environment_runs.py": "261d0a75ad94e286be19722dacdc15c4fdc6f0340c529779b66ddeaa78ce556c",
  "src/ab_harness/gate.py": "bbd8d08bb57085d5f8cfcc7a9b53f2ff05390ed7f3355557c3322dd61316d229",
  "src/ab_harness/lifecycle.py": "528907e7e8fe02d83c62adec6670dc3d6893e21449e6610368a6c04e684c1ca4",
  "src/ab_harness/model_allocator.py": "10587715ea2e1c65c8dd37e3f6bb4665090330a900966bc84fe656e45dd91afa",
  "src/ab_harness/model_invocation.py": "1d26890f50a5a9c325a08a71325eff4dec5c35165a043796c7ea636475d067a5",
  "src/ab_harness/observatory.py": "244cea9c9f9929931d4c10712ad44495feb2e5f983d340287558a0fca7c9cd64",
  "src/ab_harness/operation_edges.py": "6ae23907e8b4a8745b3a64817d80d0e6721516e5476b33a3f133a4b4d44d0045",
  "src/ab_harness/projection.py": "cdb976fcec562de60d3fd42b3767f2aab7b9dcf3b3bec80c62a539bbb4817650",
  "src/ab_harness/prompt_compiler.py": "9caaf597a1d08983f53f27672e425ba7971cc2b47e9ce0b099f0fa9ba5121ae1",
  "src/ab_harness/proposal_admission.py": "033ba785928c9019b76711ed27c603b6f3f30a2e3110443875bdfea6af019888",
  "src/ab_harness/registry.py": "1ef67aeffc32ae902ea1f5acdaaecb6525be7a6adee3006766979526566ec7a1",
  "src/ab_harness/runtime_controls.py": "ddf5a85a0722606ddb1e6622f74dbfbaba7eea112f74322600be4c797fea6aa7",
  "src/ab_harness/schema_validation.py": "525de170c7327b7576fbc0e7f6d88fd18a20e3eb71daf4741f275358e65c7b90",
  "src/ab_harness/task_compiler.py": "b11625e4cb5a64f74327e2112a6e182b48e45ce9821135a5af39a9f36f92e9bf",
  "src/ab_harness/task_ingress_authority.py": "d38a56709c6b93b61750abb717dedfa72dcabeab94c3cc0039d48dc2fd48dc7a",
  "src/ab_harness/task_registry.py": "e0cd048a2752387846477f18eb26ae3f2b3a23d81e11b8e36acb6aaa230800ef",
  "src/ab_harness/workbench.py": "b71d5377e6c0bad2a9659f5299f67173b57d1873d11df91631c8b791f3e441b3",
  "src/ab_harness/workbench_protocol.py": "44606ca712e20b6555e8ecea17cb20b138469be70656188bf1c9a10990089c6e",
  "src/ab_harness_nao/__init__.py": "3c3c3f4406a66b2daef9b3d4b9339199d847eccf1556ab62543f2a39c47fe73e",
  "src/ab_harness_nao/__main__.py": "e61befb3227e1b54de6c3bbdcd4a5d3030522d57f66bd21dfa0aa85cd7fa5b27",
  "src/ab_harness_nao/cli.py": "256caa09ec48a26ee2e31f64191394ad04e4331ba21255badd19c845e40fe715",
  "src/ab_harness_nao/contracts.py": "a0f8d0e2878b1d3309f24ae039a36c3899d1ef6459aa431ab5cefbba791e338b",
  "src/ab_harness_nao/qualification.py": "9d94f9192723bc4e2ed2b7fbab8c49fd1281b77775f63f9330d004ea634fbddb",
  "src/ab_harness_nao/smoke.py": "e38ac70b90793c02b2c2d2494908dbbef35ec5e1e66c3615a8e24d82e5fabaab",
  "src/ab_harness_synthetic/__init__.py": "14f9b4c6a84029250aa9c1602f320c167e51f7eb1bc4932cf479ec300ddab83d",
  "src/ab_harness_synthetic/notes.py": "bed451276c769cacb10befaac54c8347932ac9c70471f834e1d878c5b3277642"
}
```

Exact research probe source (never installed as a hook):

```python
"""Research-only static controls; never imports or executes scanned source."""

import ast
import hashlib
import json
import subprocess
import time
from pathlib import Path


ROOT = Path(__file__).parent
PYTHON = "/home/juanbeck/universal-agentic-harness/.venv/bin/python"
FORBIDDEN = {
    "ab_harness_nao", "rclpy", "rospy", "qi", "naoqi", "openai",
    "anthropic", "ollama", "transformers", "torch", "skill_common",
}


def forbidden_imports(source, expanded):
    matches = []
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            names = [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom) and node.module:
            names = [node.module] if node.level == 0 else []
        else:
            continue
        roots = FORBIDDEN if expanded else {"ab_harness_nao"}
        for name in names:
            if name.split(".", 1)[0] in roots:
                matches.append({"line": node.lineno, "module": name})
    return matches


def main():
    started = time.perf_counter()
    core = sorted((ROOT / "src/ab_harness").rglob("*.py"))
    scans = {}
    for expanded in (False, True):
        hits = []
        for path in core:
            for match in forbidden_imports(path.read_text(), expanded):
                hits.append({"file": str(path.relative_to(ROOT)), **match})
        scans["candidate" if expanded else "existing_policy_shape"] = hits

    controls = [
        ("portable_stdlib", "import json\nfrom pathlib import Path\n", False),
        ("domain_word_in_text", "message = 'import rclpy'\n", False),
        ("relative_core_module", "from . import environment\n", False),
        ("direct_adapter", "import ab_harness_nao\n", True),
        ("aliased_adapter", "import ab_harness_nao.smoke as s\n", True),
        ("from_adapter", "from ab_harness_nao import smoke\n", True),
        ("direct_ros", "import rclpy\n", True),
        ("aliased_provider", "from openai import OpenAI as Client\n", True),
        ("type_checking_provider", "from typing import TYPE_CHECKING\nif TYPE_CHECKING:\n    import anthropic\n", True),
        ("nested_robot", "def load():\n    import qi\n", True),
    ]
    results = []
    for name, body, expected in controls:
        before = bool(forbidden_imports(body, False))
        after = bool(forbidden_imports(body, True))
        results.append({"name": name, "expected": expected, "existing": before, "candidate": after})
    misses = [
        ("literal_dynamic", "__import__('rclpy')\n"),
        ("dynamic_importlib", "import importlib\nimportlib.import_module('openai')\n"),
        ("unknown_provider", "import cohere\n"),
        ("local_transitive", "from .gateway import provider\n"),
    ]
    limits = [{"name": name, "caught": bool(forbidden_imports(body, True))} for name, body in misses]

    ruff_started = time.perf_counter()
    ruff = subprocess.run(
        [PYTHON, "-m", "ruff", "check", "--isolated", "--select", "C901,PLR0912,PLR0915",
         "--output-format", "json", str(ROOT / "src")],
        capture_output=True, text=True, check=False,
    )
    if ruff.returncode not in (0, 1):
        raise RuntimeError(ruff.stderr)
    findings = json.loads(ruff.stdout)
    ruff_elapsed = time.perf_counter() - ruff_started
    simple = "def simple(value):\n    return value + 1\n"
    complex_body = "def branched(value):\n" + "".join(
        f"    if value == {i}:\n        value += 1\n" for i in range(15)
    ) + "    return value\n"
    complexity_controls = []
    for name, body in (("simple", simple), ("fifteen_branches", complex_body)):
        control = subprocess.run(
            [PYTHON, "-m", "ruff", "check", "--isolated", "--select", "C901,PLR0912,PLR0915",
             "--output-format", "json", "--stdin-filename", "control.py", "-"],
            input=body, capture_output=True, text=True, check=False,
        )
        if control.returncode not in (0, 1):
            raise RuntimeError(control.stderr)
        complexity_controls.append({"name": name, "returncode": control.returncode,
                                    "codes": [f["code"] for f in json.loads(control.stdout)]})
    counts = {}
    for finding in findings:
        counts[finding["code"]] = counts.get(finding["code"], 0) + 1
    all_python = sorted((ROOT / "src").rglob("*.py"))
    output = {
        "scope": {"core_files": len(core), "src_files": len(all_python),
                  "src_lines": sum(len(p.read_text().splitlines()) for p in all_python)},
        "core_imports": scans,
        "controls": results,
        "limitations": limits,
        "ruff": {"returncode": ruff.returncode, "elapsed_seconds": round(ruff_elapsed, 4),
                 "counts": counts, "distinct_paths": len({f["filename"] for f in findings}),
                 "distinct_locations": len({(f["filename"], f["location"]["row"]) for f in findings}),
                 "findings": [{"code": f["code"], "file": str(Path(f["filename"]).relative_to(ROOT)),
                               "line": f["location"]["row"], "message": f["message"]} for f in findings]},
        "complexity_controls": complexity_controls,
        "elapsed_seconds": round(time.perf_counter() - started, 4),
        "snapshot_hashes": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                            for p in all_python},
    }
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
```

[manifest]: https://github.com/aurelienbobenrieth/agentlint/blob/4d933d3e18a2907c3914006054973745de98fceb/packages/agentlint/package.json
[init]: https://github.com/aurelienbobenrieth/agentlint/blob/4d933d3e18a2907c3914006054973745de98fceb/packages/agentlint/src/features/init/handler.ts#L10-L16
[language]: https://github.com/aurelienbobenrieth/agentlint/blob/4d933d3e18a2907c3914006054973745de98fceb/packages/agentlint/src/shared/pipeline/language-map.ts
[scan]: https://github.com/aurelienbobenrieth/agentlint/blob/4d933d3e18a2907c3914006054973745de98fceb/packages/agentlint/src/shared/pipeline/collect-findings.ts#L271-L284
[fixtures]: https://github.com/aurelienbobenrieth/agentlint/blob/4d933d3e18a2907c3914006054973745de98fceb/packages/agentlint/src/features/rules/handler.ts#L63-L94
[rules]: https://github.com/aurelienbobenrieth/agentlint/blob/4d933d3e18a2907c3914006054973745de98fceb/docs/guide/writing-rules.md
[acceptance]: https://github.com/aurelienbobenrieth/agentlint/blob/4d933d3e18a2907c3914006054973745de98fceb/docs/guide/acceptance.md
[check]: https://github.com/aurelienbobenrieth/agentlint/blob/4d933d3e18a2907c3914006054973745de98fceb/packages/agentlint/src/features/check/handler.ts#L79-L98
[security]: https://github.com/aurelienbobenrieth/agentlint/blob/4d933d3e18a2907c3914006054973745de98fceb/docs/security-model.md
[guarantees]: https://github.com/aurelienbobenrieth/agentlint/blob/4d933d3e18a2907c3914006054973745de98fceb/docs/guide/guarantees.md
[actor]: https://github.com/aurelienbobenrieth/agentlint/blob/4d933d3e18a2907c3914006054973745de98fceb/packages/agentlint/src/config/env.ts#L85-L92
[approve]: https://github.com/aurelienbobenrieth/agentlint/blob/4d933d3e18a2907c3914006054973745de98fceb/packages/agentlint/src/features/accept/handler.ts#L50-L66
[ghpermission]: https://github.com/aurelienbobenrieth/agentlint/blob/4d933d3e18a2907c3914006054973745de98fceb/action/src/commands.mjs#L371-L397
[ci]: https://github.com/aurelienbobenrieth/agentlint/blob/4d933d3e18a2907c3914006054973745de98fceb/docs/guide/ci.md
[stop]: https://github.com/aurelienbobenrieth/agentlint/blob/4d933d3e18a2907c3914006054973745de98fceb/packages/agentlint/skills/agentlint/setup/agentlint-gate.mjs#L59-L95
[actionscan]: https://github.com/aurelienbobenrieth/agentlint/blob/4d933d3e18a2907c3914006054973745de98fceb/action/src/gate.mjs#L179-L198
[engineprecedence]: https://github.com/aurelienbobenrieth/agentlint/blob/4d933d3e18a2907c3914006054973745de98fceb/action/src/main.mjs#L119-L132
[pilot]: https://github.com/aurelienbobenrieth/agentlint/blob/4d933d3e18a2907c3914006054973745de98fceb/docs/review-pilot.md
