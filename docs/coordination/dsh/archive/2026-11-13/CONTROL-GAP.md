# Verified cross-thread control gap — 13 November 2026

## Required outcome

A human asks GRILL here; GRILL wakes the actual registered CREATOR/VISUALS/RESEARCH parents, sends finite missions and receives results without human forwarding. Parents may manage local native Teams. Messaging availability remains until revoked; mission budgets do not require repeatedly bootstrapping transport. Explorer/UAH work is held until this control path is proved.

## What is actually working

Native Team communication works inside one Team. Actual CREATOR and GRILL also completed a warm filesystem bootstrap round-trip after human activation. A GRILL-owned notification job watches role outboxes; it is NOT an outbound Host session-control capability, cannot run a tool in another root, and cannot arm that root’s receiver. Standing availability is intended/documented, not a deployed durable recovery service.

## The existing Host primitive

The installed SessionController already publicly exposes resolveAgent(SessionId) for other Host domains. It resolves/resumes ordinary Sessions, deduplicates concurrent resumes, applies recorded preset composition and keeps subagent ownership fences. Thus a new cold-session runtime is unnecessary. Current source: installed dsh-api-session-controller public types line78 and implementation lines177–215,305–316,3877–3883. Source-level verification is not a new live integration test.

## Exactly missing

1. A reviewed Agent-facing role dispatch Tool installed into GRILL and approved role-parent contexts; the current GRILL SDK has no session prompt/resolve or dispatch_role binding.
2. A fixed owner-approved role→actualSessionId mapping and exact execution-caller guard BEFORE any target lookup/resume. Local Team membership/name is not cross-Team authority.
3. Binding the existing public preset-aware resolver to truthful native agent-origin message admission and reply delivery. Do not blindly forward as an owner/user-rpc prompt: the public Remote prompt method constructs that user source; native agent delivery/attribution must be preserved and verified.
4. Actual runtime proof: GRILL→inactive AND unloaded existing role→GRILL, no manual turn/paste, preserved target policy, denied helper/unknown targets, Host restart recovery.
5. For source acceptance, fresh different-model reviewer result/cancellation/model-effort routing still needs qualification; native Team tool names shadow legacy child controls and teammate spawn exposes no per-call model/effort selector. This is a review-control gap, not proof cross-thread messaging exists.

## PTC versus Standard: verified contributing constraint

The shipped [PTC preset](</home/juanbeck/.local/share/dsh-harness/app/node_modules/@deepseek-ai/dsh-web-app/presets/ptc.patch.yml#L106-L134>) disables workflow and Plugin Manager tools. [Standard](</home/juanbeck/.local/share/dsh-harness/app/node_modules/@deepseek-ai/dsh-web-app/presets/standard.patch.yml#L106-L127>) enables workflow and conditionally enables Plugin Manager when a profile context is present. Thus PTC limits GRILL’s ability to bootstrap installation directly; it is not irrelevant. Neither preset automatically supplies the missing registered-role dispatch binding. Live composition/overrides must be verified rather than inferred from the template. No session restart or mode change was performed; the current route uses CREATOR’s installation capability.

## Routes / decision

- **Native Team here:** works for its owned named members; does not adopt the existing independent role roots or automatically grant CREATOR-specific tooling/model permissions.
- **More filesystem/expiry glue:** rejected as the final unattended control plane. Useful bootstrap proof, but repeatedly asking the human to start receivers fails the stated outcome.
- **Small registered-role Host binding:** preferred. Reuse SessionController.resolveAgent plus existing native agent delivery, registered roles and supported Plugin Manager. No new bus/store/scheduler, arbitrary-session API, credential replay, preset override or forged human principal. Start with ordinary native send semantics; do not add stronger retry/exactly-once promises than the underlying runtime provides.

## Completion gate

The Tool is actually visible/callable in GRILL; GRILL starts the existing roles and gets correlated ACK/results without human messages; cold/idle/denial/recovery cases are recorded. Installation approval and standing scope are persistent owner configuration, not a per-task clock. Native helper source review remains independent. A same-named new helper is not proof the actual existing role was reached.

## Bootstrap boundary

Until that Tool is installed, GRILL cannot start CREATOR merely by writing a file. An initial owner-side installation/activation is still necessary: CREATOR can perform the reviewed install, or the owner explicitly grants an equivalent supported Tool capability to GRILL. Do not claim that arming GRILL’s inbound watcher removes this boundary. Do not ask the human to bootstrap VISUALS repeatedly as a substitute for implementing the missing binding.

[Operating model](<OPERATING-MODEL.md>) · [Current owner board](<grill.md>) · [Coordination policy](<README.md>). These owner coordination records are not product release evidence and are excluded from product PRs unless sanitized/reviewed.
