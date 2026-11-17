# DSH session coordination bundle

A Host-only Cordis bundle that binds four existing native session APIs to one owner-configured workspace and a finite hub/spoke role map. It does not add a transport, global session discovery, session creation, a command-line setup tool, or a Client bundle. It has no production dependencies or install scripts; tests use Node’s built-in test runner.

## Source, provenance, and local configuration

The package is `@local/dsh-session-coordination@0.1.0`. Its upstream lineage and the reviewed `@local/dsh-session-pair-pilot@0.2.0` base are recorded in [UPSTREAM.json](<UPSTREAM.json>); the original MIT license is retained in [LICENSE](<LICENSE>).

The shipped [cordis.patch.yml](<cordis.patch.yml>) is deliberately an **unconfigured template** (`config: {}`), and startup fails closed until the owner supplies a valid configuration. Do not edit the shared source package. First verify the pristine source manifest from the package root:

```sh
sha256sum -c SOURCE-SHA256SUMS
```

Then make an owner-local copy and edit only that copy’s `cordis.patch.yml` row before supported Plugin Manager installation. Example values below are placeholders, not a ready-to-install binding:

```yaml
config:
  workspacePath: /canonical/absolute/native/workspace
  hubRole: HUB
  roles:
    HUB: existing-owner-root-id
    DEV: existing-peer-root-id
  maxMessageBytes: 65536 # optional; defaults to 65536
```

`workspacePath` must already be a canonical absolute native path. `hubRole` must exactly name one role key. `roles` must be a finite plain label-to-root-ID mapping with unique IDs; runtime checks still require each configured ID to be the exact existing ordinary root in the configured workspace. `maxMessageBytes` is a positive safe integer no greater than 65536. Missing, duplicate, malformed, or unknown config fields fail before Tool registration or target I/O. The plugin snapshots and freezes a normalized copy; it never mutates Cordis’s raw input or offers a runtime binding setter.

The public source manifest includes the pristine patch template. Verify it **before** making the owner-local config edit. After that edit, the local patch hash is expected to differ; record it separately and preserve the pristine manifest. Runtime source hashes should remain unchanged. Do not rewrite the source manifest to make a private binding appear to be the reviewed source.

Before installation, inventory exact installed Tool provider IDs. If a provider conflict exists, stop and ask the owner before any supported replacement; preserve a rollback source before an explicitly approved remove/install. This package performs no install or uninstall itself.

## Native Tool contract

The package registers exactly these four existing Tools:

- `session_list`: read only this caller’s configured view; the hub sees configured roots and each spoke sees itself plus the hub.
- `session_preflight`: inspect only a caller-visible root, including self. Policy fields are named projections only; unavailable state remains unknown and the result is not proof of unchanged complete policy.
- `session_send_message`: only hub↔spoke edges are accepted. `steer` is default; `queue` must be explicit. Cold peers use exact persisted-header checks followed by the public native resolver inside `withoutInitiator`. Dispatch acceptance is not an ACK or result. Canonical post-dispatch `ABORTED` is reported as delivery-unknown; do not retry blindly.
- `session_wait_for_message`: passively observes only the caller’s current pending inbox for an exact native peer relay containing a literal marker. It does not read history, consume, send, or resume; abort, timeout, ownership change, and plugin disposal clean up the active listener.

Caller/root identity, workspace membership, headers, archive status, configured edges, and cancellation are checked before target work and again after asynchronous boundaries. Tool schemas do not enumerate configured IDs. The bundle never changes model, effort, preset, permission, or other session settings.

## Validation and limits

`node --test test/*.test.mjs` exercises public Tool bodies with synthetic owner bindings and fake Host services. It is not native/live-role qualification. Compatible DSH/Node/Team behavior, owner-local installation, actual roots, and real handshakes remain separate deployment gates; source bytes and public tests alone do not prove them. No claim is made for other hosts, operating systems, restart behavior, or source approval.

The distribution origin is `https://github.com/ieverythng/universal-agentic-harness.git`, package subdirectory `tools/dsh-session-coordination`. Retrieve a human-approved immutable published revision containing this package before following distribution instructions. If that approved revision is not available, stop for owner publication/distribution rather than substituting an unreviewed source.
