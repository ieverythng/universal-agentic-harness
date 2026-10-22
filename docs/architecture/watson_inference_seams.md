# Watson and local-inference seams

The Universal Agentic Harness should guide local-model research without
absorbing llama.cpp, Headroom, Hermes, ZeroTier, or repository execution into
the semantic kernel.

## Adapter boundary

| Existing system | Harness-facing seam | Evidence to record |
| --- | --- | --- |
| llama.cpp server | OpenAI-compatible provider adapter | build/model/quant identity, context, batch and KV settings, cache state |
| Headroom | context/memory adapter | injected headers, project/user scope, compression or retrieval events |
| Hermes / Discord | persistent-agent worker adapter | session lineage, active tools, memory scope, request/response timing |
| ZeroTier proxy | endpoint/runtime adapter | route identity, health, transport failures, upstream selection |
| Repository and shell | environment adapter | commands, exit codes, file artifacts, tests, diffs |
| Reviewer/evaluator | evaluation adapter | milestone, minefield, quality, and terminal-acceptance results |

## Provider capability record

Before routing a task, probe and version:

- protocol and exact served model identifier;
- advertised and effective context/output limits;
- structured-output and tool-schema behavior;
- streaming format and timeout behavior;
- prompt-cache behavior;
- cold/warm prefill rate, time to first token, decode rate, and concurrency;
- memory headroom and failure thresholds.

This avoids model-name conditionals and prevents a proxy’s advertised context
from silently overriding the effective server configuration.

## Model evaluation unit

Treat the complete configuration as the experimental unit:

```text
model revision + quantization + inference-engine build + server flags
+ harness version + adapter version + prompt-pack hash + registry hash
+ memory policy + environment identity + frozen task suite
```

Compare the current Watson model and challengers using paired tasks:

1. cold and warm prefill at fixed token lengths;
2. sustained decode with enough output tokens to reduce timing noise;
3. structured JSON and tool adherence;
4. long-context evidence retrieval and instruction retention;
5. style, concision, correction, uncertainty, and refusal behavior;
6. full Hermes/Discord workflow and memory-scope checks;
7. failure recovery, cancellation, and false-completion minefields.

Stable harness instructions and schemas should lead the prompt so prefix
caching can reuse them. Fresh task state and evidence should remain late and
bounded. Prefix caching improves shared-prefix prefill, not decode.

## Orchestrator and worker swarms

A stronger orchestrator plus smaller workers fits the H5 adapter model when
authority stays explicit:

- the orchestrator receives only task-level routing and review capabilities;
- workers receive narrow `InteractionModuleSpec` projections;
- each worker has its own budgets, environment identity, and trace lineage;
- worker output is a proposal or artifact, never self-certified effect truth;
- an independent gate/evaluator closes acceptance;
- parallelism is accepted only when aggregate latency, VRAM, quality, and
  failure isolation beat the single-model baseline.

The first experiment should use recorded worker proposals and replay before
live concurrent execution.
