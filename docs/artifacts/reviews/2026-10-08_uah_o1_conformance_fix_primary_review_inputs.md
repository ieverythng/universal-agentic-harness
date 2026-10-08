# O1 fix review: independently predeclared inputs

Declared before reading the changed implementation, test, diff, or writer evidence.

1. Initial public control: execute the original Observatory public suite against exact-before and current implementations, with the same immutable lifecycle dependency.
2. Genuine v1 actor and scope fields: mutate each excluded field separately, then both together, and preserve the covered v1 identity.
3. Valid v1 and v2 task-scoped, agent-scoped, and mixed-schema histories, including incomplete synthetic histories.
4. Covered identity staleness: mutate each covered public field while retaining its old identity.
5. Alternative public input forms: raw tuples and single-use generators; projection and render consumers; actor, status, and grouping output agreement.
6. Aliasing: mutate original mappings and nested payloads after projection and verify that retained projections do not change.
7. Invalid input shapes: invalid scalar and container types, duplicate sequences and identifiers, unknown schema, and foreign formats.

Expected boundary: validate only lifecycle-owner shape and content identity. Do not infer causal completeness, freshness, or new label policy. ARCH-02 is outside scope. Other concurrent files are outside O1 attribution.

Requested reviewer model/effort: sol/max. Backend identity is unobservable through the available tools.
