# DSH coordination bootstrap

Use this standalone procedure to bind existing ordinary DSH roots to one
owner-approved hub in one registered workspace, using a local Cordis plugin.
It is not a new CLI, a global session directory or permission to create roots.
No companion project guide or private operational directory is required.

**Package pin:** use `@local/dsh-session-coordination@0.1.0` from an owner-approved
immutable published commit containing the package. Its `SOURCE-SHA256SUMS` digest is
`6522c0cf657c3f63a563d3e37590f7a47705d4343d6a86da9d9223d56bc2a83a`.
A digest identifies bytes, not approval. The owner must supply the reviewed source
commit and local startup inputs; if that revision is not published/retrievable,
stop rather than invent a pin or substitute an older/different package.

## 1. Collect the one-time owner inputs

Before touching an installed provider, record:

- The actual Host's DSH and Node versions, supported Plugin Manager access, and
  compatibility with the reviewed package's declared peers/engines. The source
  Host used DSH `0.2.2-rc.1` / Node `v24.22.2`; that is not another-machine,
  operating-system or restart qualification. Do not grant version exemptions or
  run unrelated install scripts to bypass incompatibility.
- A canonical absolute **registered workspace** path and the exact existing
  ordinary root IDs the owner approves there. Obtain selected identities through
  supported owner/Host metadata or UI, not fuzzy title search, transcript scans,
  global model enumeration, credentials or raw user/owner RPC.
- A finite plain-object role-label → root-ID mapping, its one `hubRole`, and any
  smaller message-byte limit. Role names/presets are labels, not identity. Current
  exact registry-instance/root ownership, Session placement, workspace membership
  and archive state must agree. Mutable working directory is not enrollment.
- The selected model, optional effort, preset and named permissions for each
  root; retain missing/unknown values honestly. Configured next-step metadata is
  not backend serving identity/effort or a complete effective-policy attestation.
- Exact reviewed source commit, package manifest/digests and installation approval,
  plus the conflict/backup/rollback decision in section 4.

Do not change existing model/effort/preset/permissions just to satisfy this setup.
Standard and PTC are compositions, not role identities or a requirement to
replace the user's choice. Missing inputs or incompatible roots mean **STOP**.
No bridge Tool creates Sessions, changes startup bindings or selects settings.

## 2. Retrieve and pin the public source

Code-distribution locator only:
[public source repository](<https://github.com/ieverythng/universal-agentic-harness.git>).
The independently reusable package subdirectory is
`tools/dsh-session-coordination`. The repository name is not a semantic dependency
of this procedure; the plugin is Host-only DSH/Cordis functionality.

The owner chooses a **full immutable published commit containing that package**,
not an unpinned branch, the newest tag, this document's future commit, or a local
private source path. Example Git commands, after replacing the value:

```sh
SOURCE_COMMIT='REPLACE_WITH_OWNER_APPROVED_FULL_PUBLISHED_COMMIT'
git clone --no-checkout https://github.com/ieverythng/universal-agentic-harness.git dsh-coordination-source
git -C dsh-coordination-source checkout --detach "$SOURCE_COMMIT"
git -C dsh-coordination-source rev-parse HEAD
```

Confirm the output is the chosen commit and the package directory exists there.
If the ref/package is not publicly retrievable, stop and request publication or
a separately owner-approved reviewed distribution; do not substitute an
inaccessible private directory. These are source-retrieval examples, not a setup
CLI or a claim that the commands were run on a second computer.

Verify `SOURCE-SHA256SUMS` against the digest above, then verify every listed
package/code file, license/upstream notice and patch **before modification**.
For example, run `sha256sum -c SOURCE-SHA256SUMS` from the pristine package root
on a Host with that checksum utility; otherwise use an owner-approved SHA-256
verifier. If the manifest or required verifier cannot be supplied, stop. A hash computed from unreviewed downloaded bytes
is an identity observation, not source approval. The proposed package has no
production dependency or install script; unexpected build/dependency requirements
need an owner decision rather than manual runtime repairs.

## 3. Make one private configured copy

Copy the **complete verified package directory**, preserving all shipped files,
to an owner-controlled private location outside repositories that may be
committed. Keep the public checkout pristine. No real root IDs, workspace paths
or private binding file should be committed to the distribution.

In that private copy only, edit the **existing** `cordis.patch.yml` insertion row
with ID `local-session-coordination`, changing only its `config`. Do not add a
second row, edit the implementation, alter the package name or rewrite a source
manifest to hide the configuration difference. There is no new setup command.

This is the shape of that existing row after private configuration. **Every
angle-bracket value is a FAKE placeholder to replace, not a usable identity/path.**
The YAML `roles` value is a mapping/plain object, **not an array**:

```yaml
- insert:
    - id: local-session-coordination
      name: '@local/dsh-session-coordination'
      config:
        workspacePath: '<CANONICAL_ABSOLUTE_REGISTERED_WORKSPACE>'
        hubRole: HUB
        roles:
          HUB: '<EXACT_EXISTING_HUB_ROOT_ID>'
          WRITER: '<EXACT_EXISTING_WRITER_ROOT_ID>'
          ANALYST: '<EXACT_EXISTING_ANALYST_ROOT_ID>'
        maxMessageBytes: 65536
```

`workspacePath`, `hubRole` and `roles` are required. The finite labels and IDs must
be unique, and the hub label must name one of those IDs. `maxMessageBytes` is
optional, defaults to 65536 and may only narrow that ceiling. It limits UTF-8 bytes
of the serialized attributed content, not just the raw message text; a very small
cap can reject even a short message. Missing, duplicate,
malformed or unknown configuration fails closed; the shipped unconfigured
template is deliberately not an all-roots fallback. Runtime Tool arguments do
not modify this configuration. Do not fill unused slots with invented roots.

Recheck that implementation/code hashes still match the reviewed source.
Preserve the original template/manifest, and separately record the owner-bound
patch/config digest and the exact intended mapping privately. The configured
patch legitimately differs from the public template; do not call it an unchanged
package digest. Retain the selected-settings snapshot and owner approval.

## 4. Inventory conflicts, then use supported Plugin Manager

1. Through the Host's supported Plugin Manager UI or exposed Manager Tool, list
   installed bundles and plugins (`list_bundles` / `list_plugins`). Record exact
   installed IDs, package versions, enabled state, source/config custody and which
   provider currently owns the four names below. Include legacy/community
   session-messaging providers: matching names do not mean matching contracts.
2. If any provider overlaps, **stop for explicit owner-approved replacement**.
   Do not stack both, silently remove unrelated plugins or enable every session.
   A profile-wide removal may affect other roots; disclose that scope.
3. **Before disabling/removing anything**, retain a recoverable copy/pin of the
   current provider's actual source/package, private configuration, supported
   installation target, enabled state and selected-settings metadata. If that
   rollback material cannot be recovered, do not proceed with replacement.
4. With approval, use supported Manager disable/remove operations for the exact
   conflicting provider; verify its effective Tools are withdrawn. Some Managers
   require remove/install rather than an in-place replacement. Never run duplicate
   providers during the transition. An absent Manager capability is a setup gap,
   not permission for credential/RPC replay, a replacement server or a new CLI.
5. Install the configured **private package-copy directory** through Manager
   `install_bundle` using that directory as its local installation target; enable
   only the intended bundle/entry if required. Do not request a nonexistent public
   registry release merely because the package has an `@local` name. Capture the
   actual applied/error/warning receipt and resolve compatibility failures before
   claiming installation. Do not assume a fiber marked active proves model Tools.
6. Verify the four Tools in the **actual intended existing roots' effective
   model-facing catalog**, not just the global plugin list. If unavailable, stop
   and use supported owner-approved lifecycle recovery; do not replace those roots
   with same-named substitutes or claim automatic hotload/restart success.

The private copy may be live-linked by the installation. Freeze and retain it
while installed; do not edit, delete or relocate it or its rollback evidence.
Changed bindings require a new explicit owner-reviewed configuration/install
cycle, not a per-mission lease or Tool-side setter.

## 5. Preflight and prove each intended edge

The extension supplies exactly these four Tools:

| Tool | Use / limitation |
|---|---|
| `session_list` | Hub sees configured roots; each spoke sees only itself and hub. Never global discovery. |
| `session_preflight({session_id})` | Narrow approved metadata only; self metadata is allowed, cold/selected-policy unknowns stay unknown. No proof of processing. |
| `session_send_message({session_id,message,delivery?})` | Only hub↔spoke; no spoke-peer, self-send or root creation. Default steer. Receipt is inbox acceptance, not ACK/result. |
| `session_wait_for_message({session_id,literal,timeout_ms})` | Bounded passive caller-own-inbox observation for an approved peer relay/literal marker; no self-wait, history receiver or result judgment. |

The bridge validates exact caller/root and edge before target I/O, then exact
workspace/header/archive/ownership and post-await state before dispatch. A role,
title, preset or old ordinary-looking header cannot waive current root ownership.

From the actual hub, inspect the finite list and preflight each intended spoke.
From each actual spoke, confirm only self+hub visibility and the intended hub
metadata. Failure is a failed preflight, not an invitation to broaden the map.
Do not mark all configured roles enrolled merely because one edge works.

For each approved edge, issue a **new finite canary** with a fresh nonce, scope,
budget and expected literal ACK plus terminal result. Use steer in **both**
directions: the peer explicitly acknowledges the selected scope and returns its
result through the native channel, with no human paste in that peer. Validate the
actual `agent-message` / `relay` source, exact peer ID and nonce. A wait marker is
only pending-message observation; allow normal message claim and examine the
actual ACK/result. Capture message receipts separately from that result.

For Team-backed operation, inventory the actual Host's official Agent Teams bundle
with Manager `list_bundles`. On the tested Host its catalog name is
`@deepseek-ai/dsh-experimental-agent-team-profile`; confirm the target's own entry
and compatible version rather than assuming that example exists everywhere.
Only with explicit owner approval, use Manager `set_bundle` with that exact target
and `enabled: true`. This is profile-wide and can override legacy subagent Tools;
record that impact. If absent/incompatible or approval is missing, stop that setup
branch. Then verify effective Tools; an enable receipt alone is not Team proof.

If local delegation is required, first verify that the **actual peer parent**
has the optional native Agent Teams Tools. A role/preset does not guarantee the
bundle is enabled. If absent, report that capability gap; leave Team qualification
unproved. Do not silently enable plugins, change settings, use legacy children or
adopt the independent peer into the hub's Team to make a canary pass.

With owner approval and available Team capability, ask that peer to perform one
bounded local flat-Team PONG task, collect its member's explicit result and report
the task/member outcome upstream. The hub's receipt of a parent's Team report is
parent-issued evidence, not an independently captured raw child-Tool trace. An
inactive continuable member is not necessarily complete or unassigned; collect
owned work and native task state. Missing Team capability need not invalidate a
separately proved root-transport edge unless the mission requires delegation.

Compare approved named settings before/after without printing secrets. Record
source review, configured-copy installation, actual root Tool visibility, each
edge's ACK/result and any Team canary separately. Private fake-runtime checks are
not actual provider, other-machine, GUI or cold Host-restart qualification.

## 6. Use the installed channel safely

Record target governing instructions and owner-approved role guides/board locations.
The hub owns cross-parent decisions; each parent owns any local flat Team,
children, board, integration and cleanup; children report upward.
Each mission names objective, inputs/exact base, write scope, non-goals, finite
budget, checks, evidence and an explicit terminal-result/acceptance contract.
Native task claims and write scopes are advisory, not locks or isolation.
A channel/role grants no repository-write, execution or publication authority.
Board writes do not wake a parent, extend scope/budget or prove completion.
The human retains staging, commits, pushes, PRs and merges unless explicitly
delegating the exact actions/scope; no default release/tag authority follows.
Use fresh nonwriter review under the target's rules; writer checks are not approval.

- **Steer is the default both ways** for mission dispatch and ACK/result replies.
  It reaches the next safe step, not mid-Tool preemption. Queue needs an explicit
  request or reason and its normal next-turn claim. Do not resend an already
  accepted queued item merely to change delivery mode.
- Native post-effect `ABORTED` remains an error and may discard the receipt:
  **delivery unknown; do not retry blindly**. Do not invent a message ID, success
  value, exactly-once guarantee, non-delivery or independent-worker cancellation.
  Known before-dispatch refusal is distinct. Correlate authorized peer evidence
  before any owner-approved recovery or resend.
- Passive wait subscribes before checking current pending entries, matches only
  the approved peer source plus marker, preserves entries and cleans subscription,
  timer/abort listener on observation, timeout, abort or disposal. Timeout, idle,
  a local Team wait and `whenIdle` do not prove unrelated-root completion.
- Standing availability lasts until owner revocation or a real setup/lifetime
  change; each work mission still has its finite budget and stop/cleanup. No
  receiver renewal, message bus, watcher, per-task transport lease, idle model
  polling or endlessly continuing Goal is required or authorized.
- A peer message is not a human instruction or permission to spoof Goal intent.
  Complete Goal bookkeeping only in a legitimate driver/direct-human context.
  After Host restart/unload, changed identities or unavailable Tools, mark the
  path unverified until supported recovery and a fresh actual handshake prove it.

## 7. Failure, rollback and handoff

On installation/preflight/canary failure, stop new dispatch and preserve exact
source/config/receipt evidence. Unknown delivery is not repaired by reinstalling
or replaying accepted work. Settle owned jobs/children under their actual owner;
an uninstall is not a guarantee that independent work or effects were canceled.

If the owner authorizes rollback, use Manager to withdraw/remove the new provider
first, then restore the captured reviewed prior package/config/enabled state
through supported operations. Never restore it alongside overlapping new Tools.
Recheck the actual catalogs, approved settings and a fresh authorized handshake;
if rollback source/state is missing or restoration fails, leave the path
unverified and return the concrete owner decision. Do not erase receipts or claim
that rollback undid already delivered messages or effects.

Successful handoff states exactly: installed source/owner-config identities,
qualified roots/edges, actual canary outcomes, optional Team capability/collection,
settings observations, rollback location/owner and unproved boundaries. No broad
platform, restart, security or serving-identity claim follows from this document.
