# ADR 0001: Keep AB Objects Semantic and Integrate Through Reviewed Bindings

**Status:** Accepted  
**Date:** 2026-07-30

## Context

The UAH must attach to environments whose same semantic capability may appear
as a Python method, ROS topic, service, HTTP endpoint, MCP tool, fake handler, or
future implementation. Automatically turning every discovered method into an
AB object would make the registry track private code structure, churn whenever
helpers are refactored, and confuse discovery with authority.

The current NAO stack demonstrates the issue. `/planner/request` has a chatbot
publisher, a shared normalization contract, and a planner consumer. These are
different implementations of one interface, not three new semantic
capabilities.

## Decision

1. AB objects remain stable, frame-relative semantic objects.
2. `ABImplementationBinding` records replaceable environment pointers.
3. A binding records its implementation owner separately from the registry's
   semantic owner.
4. Discovery or a future method-to-AB tool may generate only `candidate`
   bindings.
5. Only explicitly `approved` bindings resolve for runtime use.
6. AB0 bindings may describe publishers, contracts, and consumers, but are not
   directly dispatchable.
7. Executable AB1 effect evidence is accepted only from a binding implemented
   by the registry-declared effect owner.
8. The first NAO integration is ROS-free and shadow-first: recorded
   chatbot/planner outputs, deterministic gates, an in-process fake owner, and
   evidence closure. Live coupling remains an H2 promotion step.

## Consequences

- Environment endpoints can change without redefining the semantic registry.
- Multiple environments can mount the same AB object and remain comparable.
- Candidate discovery is useful without becoming authorization.
- Binding promotion needs source revision, schema, owner, replay, holdout, and
  rollback evidence.
- The harness core stays independent of ROS, NAO packages, provider SDKs, and
  runtime products.
- Initial integration requires explicit binding declarations rather than
  assuming runtime discovery is trustworthy.

## Rejected alternatives

### Promote every method to an AB object

Rejected because method granularity is an implementation detail and would make
semantic identity unstable.

### Import NAO or ROS packages into `ab_harness`

Rejected because it violates portability and moves environment policy into the
kernel.

### Begin with live autonomous coupling

Rejected for the first slice because no parity, failure-attribution, or rollback
record exists yet. The shadow-first path produces those counterexamples before
authority moves.
