import assert from 'node:assert/strict'
import test from 'node:test'
import { apply } from '../lib/index.js'

const LIST_TOOL = 'session_list'

function makeAgent(id, workspacePath) {
  const received = []
  const listeners = new Set()
  const agent = {
    id,
    status: 'running',
    session: { id, header: { id, cwd: workspacePath, agentPreset: 'fixture-preset' } },
    model: { current: () => ({ provider: 'fixture-provider', model: 'fixture-model', reasoningEffort: 'high', credential: 'not-a-real-secret' }) },
    inbox: { nextStep: [], nextTurn: [] },
    ctx: {
      on(name, callback) {
        if (name !== 'session/event') throw new Error('only native session events are supported')
        listeners.add(callback)
        return () => listeners.delete(callback)
      },
    },
    listeners,
    emitSplice(messages, session = agent.session) {
      for (const callback of [...listeners]) callback(session, { type: 'agent/inbox/spliced', data: { inserted: messages } })
    },
    received,
    steer(message) { received.push({ via: 'steer', message }) },
    followup(message) { received.push({ via: 'followup', message }) },
  }
  return agent
}

function peerMessage(id, senderSessionId, text, source = {}) {
  return {
    id,
    role: 'user',
    content: [{ type: 'text', text }],
    source: { kind: 'agent-message', form: 'relay', senderSessionId, ...source },
  }
}

function hostFor(config, suffix, { liveIds = Object.values(config.roles) } = {}) {
  const workspacePath = config.workspacePath
  const roleBindings = { ...config.roles }
  const ids = Object.values(roleBindings)
  const workspace = { id: `workspace-${suffix}`, path: workspacePath, sessionIds: [...ids] }
  const registered = liveIds.map(id => makeAgent(id, workspacePath))
  const foreign = makeAgent(`foreign-root-${suffix}`, workspacePath)
  const agents = new Map([...registered, foreign].map(agent => [agent.id, agent]))
  const headers = new Map(ids.map(id => [id, { id, cwd: workspacePath, agentPreset: 'fixture-preset' }]))
  const tools = new Map()
  const hooks = {}
  const disposers = []
  const counts = { workspaceResolve: 0, persistenceStat: 0, globalEnumerations: 0, resolver: 0, resolverWithoutInitiator: 0, withoutInitiator: 0, flush: 0 }
  let withoutInitiatorDepth = 0
  const registry = {
    archivedSessionIds: [],
    get: id => id === workspace.id ? workspace : undefined,
    async resolveByPath(path) {
      counts.workspaceResolve++
      await hooks.workspaceResolve?.()
      return path === workspacePath ? workspace : undefined
    },
  }
  const ctx = {
    logger: { warn() {} },
    effect(factory) { const dispose = factory(); disposers.push(dispose); return dispose },
    get: name => name === 'workspaceRegistry' ? registry : undefined,
    tools: { register(tool, options) { tools.set(tool.name, { tool, options }); return () => tools.delete(tool.name) } },
    agents: {
      get: id => agents.get(id),
      roots: () => [...agents.values()],
      list() { counts.globalEnumerations++; throw new Error('global agent enumeration forbidden') },
      withoutInitiator(callback) {
        counts.withoutInitiator++
        withoutInitiatorDepth++
        try {
          const result = callback()
          if (result && typeof result.then === 'function') return result.finally(() => { withoutInitiatorDepth-- })
          withoutInitiatorDepth--
          return result
        } catch (error) {
          withoutInitiatorDepth--
          throw error
        }
      },
    },
    sessions: {
      get: id => agents.get(id)?.session,
      async flush() { counts.flush++; await hooks.flush?.(); return hooks.flushResult ?? true },
    },
    sessionPersistence: {
      async stat(id, { signal } = {}) {
        counts.persistenceStat++
        signal?.throwIfAborted()
        await hooks.persistenceStat?.(id)
        return headers.has(id) ? { header: headers.get(id) } : undefined
      },
      list() { counts.globalEnumerations++; throw new Error('global session listing forbidden') },
    },
    sessionController: {
      async resolveAgent(id) {
        counts.resolver++
        if (withoutInitiatorDepth > 0) counts.resolverWithoutInitiator++
        await hooks.resolveAgent?.(id)
        if (agents.has(id)) return { agent: agents.get(id) }
        if (!headers.has(id)) return { error: 'not found' }
        const resumed = makeAgent(id, workspacePath)
        resumed.session.header = { ...headers.get(id) }
        agents.set(id, resumed)
        return { agent: resumed }
      },
      list() { counts.globalEnumerations++; throw new Error('global controller listing forbidden') },
      create() { throw new Error('session creation forbidden') },
    },
  }
  apply(ctx, config)
  return { agents, counts, disposers, foreign, registered, tools, workspace, registry, headers, hooks, ctx }
}

const ownerBindings = [
  {
    suffix: 'alpha',
    config: {
      workspacePath: '/workspaces/alpha',
      hubRole: 'HUB',
      roles: { HUB: 'root-hub-alpha', DEV: 'root-dev-alpha', QA: 'root-qa-alpha' },
    },
    expectedHub: [['root-hub-alpha', 'HUB'], ['root-dev-alpha', 'DEV'], ['root-qa-alpha', 'QA']],
    expectedSpoke: [['root-dev-alpha', 'DEV'], ['root-hub-alpha', 'HUB']],
    spokeId: 'root-dev-alpha',
  },
  {
    suffix: 'beta',
    config: {
      workspacePath: '/srv/workspaces/beta',
      hubRole: 'COORDINATOR',
      roles: { COORDINATOR: 'root-coordinator-beta', WRITER: 'root-writer-beta', REVIEWER: 'root-reviewer-beta' },
    },
    expectedHub: [['root-coordinator-beta', 'COORDINATOR'], ['root-writer-beta', 'WRITER'], ['root-reviewer-beta', 'REVIEWER']],
    expectedSpoke: [['root-writer-beta', 'WRITER'], ['root-coordinator-beta', 'COORDINATOR']],
    spokeId: 'root-writer-beta',
  },
]

for (const binding of ownerBindings) {
  test(`configured ${binding.suffix} hub/spoke listing stays inside its workspace and roles`, async () => {
    const host = hostFor(binding.config, binding.suffix)
    const entry = host.tools.get(LIST_TOOL)
    assert.ok(entry, 'the native session_list Tool is registered')
    const hub = host.agents.get(binding.config.roles[binding.config.hubRole])
    const spoke = host.agents.get(binding.spokeId)
    const signal = () => new AbortController().signal

    assert.equal(entry.options.when({ agent: hub, signal: signal() }), true)
    assert.equal(entry.options.when({ agent: spoke, signal: signal() }), true)
    assert.equal(entry.options.when({ agent: host.foreign, signal: signal() }), false)

    const hubResult = await entry.tool.execute({}, { agent: hub, signal: signal() })
    const spokeResult = await entry.tool.execute({}, { agent: spoke, signal: signal() })
    assert.deepEqual(hubResult.sessions.map(({ sessionId, role }) => [sessionId, role]), binding.expectedHub)
    assert.deepEqual(spokeResult.sessions.map(({ sessionId, role }) => [sessionId, role]), binding.expectedSpoke)
    assert.equal(hubResult.workspace, binding.config.workspacePath)
    assert.equal(spokeResult.workspace, binding.config.workspacePath)
    assert.equal(host.counts.workspaceResolve, 2)
    assert.equal(host.counts.globalEnumerations, 0)
    assert.equal(JSON.stringify(entry.tool.parameters).includes(host.foreign.id), false)

    await assert.rejects(() => entry.tool.execute({}, { agent: host.foreign, signal: signal() }))
    assert.equal(host.counts.workspaceResolve, 2, 'foreign caller is denied before workspace I/O')
  })
}

test('a spoke can preflight itself and its hub while cold metadata stays unknown', async () => {
  const config = ownerBindings[0].config
  const host = hostFor(config, 'preflight', { liveIds: ['root-dev-alpha'] })
  const entry = host.tools.get('session_preflight')
  assert.ok(entry, 'the native session_preflight Tool is registered')
  const caller = host.agents.get('root-dev-alpha')
  const signal = new AbortController().signal

  assert.equal(entry.options.when({ agent: caller, signal }), true)
  const hub = await entry.tool.execute({ session_id: 'root-hub-alpha' }, { agent: caller, signal })
  assert.deepEqual(hub.sessions.map(({ sessionId, role }) => [sessionId, role]), [['root-hub-alpha', 'HUB']])
  assert.equal(hub.sessions[0].state, 'stored')
  assert.equal(hub.sessions[0].runtimeRoot, null)
  assert.equal(hub.sessions[0].policy.provider, null)
  assert.equal(hub.sessions[0].policy.model, null)
  assert.equal(hub.sessions[0].policy.reasoningEffort, null)
  assert.equal(hub.sessions[0].policy.reasoningEffortState, 'unknown')
  assert.equal(hub.sessions[0].policy.permissions, null)
  assert.equal(hub.sessions[0].policy.limit.includes('not complete effective-policy'), true)

  const self = await entry.tool.execute({ session_id: 'root-dev-alpha' }, { agent: caller, signal })
  assert.deepEqual(self.sessions.map(({ sessionId, role }) => [sessionId, role]), [['root-dev-alpha', 'DEV']])
  assert.equal(host.counts.persistenceStat, 1, 'cold hub is checked through exact header metadata without resolving it')
  const beforeDeniedPeer = host.counts.workspaceResolve
  await assert.rejects(() => entry.tool.execute({ session_id: 'root-qa-alpha' }, { agent: caller, signal }))
  assert.equal(host.counts.workspaceResolve, beforeDeniedPeer, 'spoke-to-spoke preflight is denied before target I/O')
  assert.equal(JSON.stringify(entry.tool.parameters).includes('root-qa-alpha'), false)
  assert.equal(JSON.stringify(hub).includes('roles'), false)
  assert.equal(JSON.stringify(hub).includes('not-a-real-secret'), false, 'unrelated runtime settings and credentials are not projected')
})

test('owner configuration is snapshotted without mutating Cordis input', async () => {
  const config = {
    workspacePath: '/workspaces/alpha',
    hubRole: 'HUB',
    roles: { HUB: 'root-hub-alpha', DEV: 'root-dev-alpha' },
  }
  const host = hostFor(config, 'snapshot')
  assert.equal(Object.isFrozen(config), false)
  assert.equal(Object.isFrozen(config.roles), false)
  config.workspacePath = '/workspaces/changed'
  config.roles.HUB = 'root-hub-changed'
  config.roles.DEV = 'root-dev-changed'

  const entry = host.tools.get(LIST_TOOL)
  const hub = host.agents.get('root-hub-alpha')
  const result = await entry.tool.execute({}, { agent: hub, signal: new AbortController().signal })
  assert.equal(result.workspace, '/workspaces/alpha')
  assert.deepEqual(result.sessions.map(({ sessionId, role }) => [sessionId, role]), [
    ['root-hub-alpha', 'HUB'],
    ['root-dev-alpha', 'DEV'],
  ])
})

test('malformed or duplicate owner configuration fails before activation side effects', () => {
  const base = { workspacePath: '/workspaces/alpha', hubRole: 'HUB', roles: { HUB: 'root-hub', DEV: 'root-dev' } }
  const invalid = [
    undefined,
    null,
    {},
    { ...base, workspacePath: 'relative/workspace' },
    { ...base, workspacePath: '/workspaces/../alpha' },
    { ...base, workspacePath: '/workspaces/alpha/' },
    { ...base, hubRole: 'MISSING' },
    { ...base, roles: { HUB: 'same-root', DEV: 'same-root' } },
    { ...base, roles: ['root-hub', 'root-dev'] },
    { ...base, maxMessageBytes: 0 },
    { ...base, maxMessageBytes: 65_537 },
    { ...base, maxMessageBytes: Number.NaN },
    { ...base, maxMessageBytes: null },
    { ...base, unrelatedRuntimeMode: true },
  ]
  let effects = 0
  let registrations = 0
  const ctx = {
    effect() { effects++ },
    tools: { register() { registrations++ } },
  }
  for (const candidate of invalid) assert.throws(() => apply(ctx, candidate))
  const accessorConfig = { ...base }
  Object.defineProperty(accessorConfig, 'roles', { enumerable: true, get() { return base.roles } })
  assert.throws(() => apply(ctx, accessorConfig))
  assert.equal(effects, 0)
  assert.equal(registrations, 0)
})

for (const binding of ownerBindings) {
  test(`configured ${binding.suffix} hub/spoke messages preserve native STEER and explicit queue`, async () => {
    const host = hostFor(binding.config, `send-${binding.suffix}`)
    const entry = host.tools.get('session_send_message')
    assert.ok(entry, 'the native session_send_message Tool is registered')
    const hubId = binding.config.roles[binding.config.hubRole]
    const spokeIds = Object.values(binding.config.roles).filter(id => id !== hubId)
    const hub = host.agents.get(hubId)
    const spoke = host.agents.get(spokeIds[0])
    const signal = () => new AbortController().signal

    assert.equal(entry.options.when({ agent: hub, signal: signal() }), true)
    const sent = await entry.tool.execute({ session_id: spoke.id, message: 'hello from configured hub' }, { agent: hub, signal: signal() })
    assert.equal(sent.state, 'running')
    assert.equal(sent.delivery, 'steer')
    assert.equal(sent.acceptance, 'accepted')
    assert.equal(sent.persistence, 'flushed')
    assert.equal(spoke.received.length, 1)
    assert.equal(spoke.received[0].via, 'steer')
    assert.equal(Object.isFrozen(spoke.received[0].message), true)
    assert.equal(spoke.received[0].message.role, 'user')
    assert.equal(spoke.received[0].message.source.senderSessionId, hub.id)
    assert.match(spoke.received[0].message.content[1].text, /hello from configured hub/)
    assert.match(spoke.received[0].message.content[0].text, /Message from session/)

    const queued = await entry.tool.execute({ session_id: hub.id, message: 'explicit queue', delivery: 'queue' }, { agent: spoke, signal: signal() })
    assert.equal(queued.delivery, 'queue')
    assert.equal(queued.acceptance, 'accepted')
    assert.equal(hub.received.length, 1)
    assert.equal(hub.received[0].via, 'followup')
    assert.equal(host.counts.withoutInitiator, 4, 'resolution and inbox dispatch both use withoutInitiator')
    assert.equal(host.counts.resolver, 2)
    assert.equal(host.counts.flush, 2)

    const otherSpoke = host.agents.get(spokeIds[1])
    const before = { workspace: host.counts.workspaceResolve, resolves: host.counts.resolver, deliveries: otherSpoke.received.length }
    await assert.rejects(() => entry.tool.execute({ session_id: otherSpoke.id, message: 'forbidden spoke edge' }, { agent: spoke, signal: signal() }))
    assert.deepEqual({ workspace: host.counts.workspaceResolve, resolves: host.counts.resolver, deliveries: otherSpoke.received.length }, before)
    assert.equal(JSON.stringify(entry.tool.parameters).includes(otherSpoke.id), false)
  })
}

test('send denies self, peer spokes, foreign targets, malformed and oversized input before target I/O', async () => {
  const config = { ...ownerBindings[0].config, maxMessageBytes: 512 }
  const host = hostFor(config, 'send-denials')
  const entry = host.tools.get('session_send_message')
  assert.ok(entry)
  const hub = host.agents.get('root-hub-alpha')
  const spoke = host.agents.get('root-dev-alpha')
  const otherSpoke = host.agents.get('root-qa-alpha')
  const signal = () => new AbortController().signal
  const invalid = [
    [hub, { session_id: hub.id, message: 'self is not an edge' }],
    [spoke, { session_id: otherSpoke.id, message: 'spoke-to-spoke is not an edge' }],
    [hub, { session_id: host.foreign.id, message: 'foreign target' }],
    [hub, { session_id: spoke.id, message: '   ' }],
    [hub, { session_id: spoke.id, message: '🧪'.repeat(150) }],
    [hub, { session_id: spoke.id, message: 'wrong keys', extra: true }],
    [hub, { session_id: spoke.id, message: 'wrong mode', delivery: 'followup' }],
  ]
  for (const [caller, args] of invalid) await assert.rejects(() => entry.tool.execute(args, { agent: caller, signal: signal() }))
  const aborted = new AbortController()
  aborted.abort()
  await assert.rejects(() => entry.tool.execute({ session_id: spoke.id, message: 'cancelled first' }, { agent: hub, signal: aborted.signal }))
  assert.equal(host.counts.workspaceResolve, 0)
  assert.equal(host.counts.persistenceStat, 0)
  assert.equal(host.counts.resolver, 0)
  assert.equal(host.counts.flush, 0)
  assert.equal(spoke.received.length + hub.received.length + otherSpoke.received.length, 0)
})

test('cold configured target uses exact header then native resolver inside withoutInitiator', async () => {
  const config = ownerBindings[0].config
  const host = hostFor(config, 'cold-target', { liveIds: ['root-hub-alpha', 'root-qa-alpha'] })
  const hub = host.agents.get('root-hub-alpha')
  const targetId = 'root-dev-alpha'
  const entry = host.tools.get('session_send_message')
  assert.equal(host.agents.has(targetId), false)

  const result = await entry.tool.execute({ session_id: targetId, message: 'cold target' }, { agent: hub, signal: new AbortController().signal })
  assert.equal(result.state, 'stored')
  assert.equal(result.acceptance, 'accepted')
  assert.equal(host.counts.persistenceStat, 1)
  assert.equal(host.counts.resolver, 1)
  assert.equal(host.counts.resolverWithoutInitiator, 1)
  assert.equal(host.agents.get(targetId).received.length, 1)
  assert.equal(host.agents.get(targetId).received[0].via, 'steer')
  assert.equal(host.counts.globalEnumerations, 0)
})

test('helper, wrong header, archive, membership and registry mismatches deny before native resolution', async () => {
  const config = ownerBindings[0].config
  const targetId = 'root-dev-alpha'
  const mutate = [
    host => { host.agents.get(targetId).session.header.origin = 'subagent' },
    host => { host.agents.get(targetId).session.header.cwd = '/workspace/other' },
    host => { host.registry.archivedSessionIds.push(targetId) },
    host => { host.workspace.sessionIds = host.workspace.sessionIds.filter(id => id !== targetId) },
    host => { host.registry.get = () => ({ ...host.workspace, path: '/workspace/other' }) },
  ]
  for (const [index, change] of mutate.entries()) {
    const host = hostFor(config, `invalid-root-${index}`)
    change(host)
    const hub = host.agents.get('root-hub-alpha')
    await assert.rejects(() => host.tools.get('session_send_message').tool.execute({ session_id: targetId, message: 'must not dispatch' }, { agent: hub, signal: new AbortController().signal }))
    assert.equal(host.counts.resolver, 0)
    assert.equal(host.counts.flush, 0)
    assert.equal(host.agents.get(targetId).received.length, 0)
  }

  const cold = hostFor(config, 'cold-bad-header', { liveIds: ['root-hub-alpha', 'root-qa-alpha'] })
  cold.headers.get(targetId).cwd = '/workspace/other'
  await assert.rejects(() => cold.tools.get('session_send_message').tool.execute({ session_id: targetId, message: 'bad stored header' }, { agent: cold.agents.get('root-hub-alpha'), signal: new AbortController().signal }))
  assert.equal(cold.counts.persistenceStat, 1)
  assert.equal(cold.counts.resolver, 0)
})

test('caller, target, workspace and abort races after native resolution prevent inbox dispatch', async () => {
  const targetId = 'root-dev-alpha'
  const modes = ['caller-owned', 'target-replaced', 'caller-header', 'abort']
  for (const mode of modes) {
    const host = hostFor(ownerBindings[0].config, `race-${mode}`)
    const hub = host.agents.get('root-hub-alpha')
    const target = host.agents.get(targetId)
    const controller = new AbortController()
    host.hooks.resolveAgent = async () => {
      if (mode === 'caller-owned') host.agents.delete(hub.id)
      if (mode === 'target-replaced') host.agents.delete(targetId)
      if (mode === 'caller-header') hub.session.header.cwd = '/workspace/other'
      if (mode === 'abort') controller.abort()
    }
    const signal = controller.signal
    await assert.rejects(() => host.tools.get('session_send_message').tool.execute({ session_id: targetId, message: 'race must not dispatch' }, { agent: hub, signal }))
    assert.equal(host.counts.resolver, 1)
    assert.equal(target.received.length, 0)
  }

  const disposed = hostFor(ownerBindings[0].config, 'race-dispose')
  const sender = disposed.agents.get('root-hub-alpha')
  disposed.hooks.resolveAgent = async () => { disposed.disposers.forEach(dispose => dispose?.()) }
  await assert.rejects(() => disposed.tools.get('session_send_message').tool.execute({ session_id: targetId, message: 'dispose race' }, { agent: sender, signal: new AbortController().signal }))
  assert.equal(disposed.agents.get(targetId).received.length, 0)
})

test('SEND finalizer preserves canonical ABORTED and labels only delivery uncertainty', () => {
  const host = hostFor(ownerBindings[0].config, 'aborted-finalizer')
  const finalize = host.tools.get('session_send_message').tool.finalizeContent
  assert.equal(typeof finalize, 'function')
  const block = Object.freeze({ type: 'text', text: 'Error: tool call aborted' })
  const content = Object.freeze([block])
  const result = Object.freeze({ isError: true, error: Object.freeze({ info: Object.freeze({ code: 'ABORTED' }) }), content, meta: Object.freeze({ fixture: 'unchanged' }) })
  const output = finalize(Object.freeze({}), result)
  assert.equal(output[0], block)
  assert.match(output[1].text, /Delivery UNKNOWN/)
  assert.match(output[1].text, /Do not retry blindly/)
  assert.equal(result.isError, true)
  assert.equal(result.error.info.code, 'ABORTED')
  assert.equal(result.content.length, 1)
  for (const code of ['ABORTED_BEFORE_DISPATCH', 'CANCELLED', 'OUTPUT_INVALID']) {
    assert.equal(finalize({}, { ...result, error: { info: { code } } }), undefined)
  }
})

for (const binding of ownerBindings) {
  test(`configured ${binding.suffix} passive wait observes a native peer marker without consuming it`, async () => {
    const host = hostFor(binding.config, `wait-${binding.suffix}`)
    const entry = host.tools.get('session_wait_for_message')
    assert.ok(entry, 'the native session_wait_for_message Tool is registered')
    const spoke = host.agents.get(binding.spokeId)
    const hubId = binding.config.roles[binding.config.hubRole]
    const marker = {
      id: `native-marker-${binding.suffix}`,
      role: 'user',
      content: [{ type: 'text', text: `reply nonce=${binding.suffix}-fixture` }],
      source: { kind: 'agent-message', form: 'relay', senderSessionId: hubId },
    }
    spoke.inbox.nextTurn.push(marker)

    const result = await entry.tool.execute({ session_id: hubId, literal: `nonce=${binding.suffix}-fixture`, timeout_ms: 1_000 }, { agent: spoke, signal: new AbortController().signal })
    assert.equal(result.state, 'observed')
    assert.equal(result.messageId, marker.id)
    assert.equal(result.observation, 'peer_inbox_message_only')
    assert.equal(spoke.inbox.nextTurn.length, 1, 'current inbox is observed but not consumed')
    assert.equal(spoke.listeners.size, 0, 'observation subscription is removed')
    assert.equal(host.counts.resolver, 0, 'wait never resumes or resolves its peer')
    assert.equal(host.counts.globalEnumerations, 0)
  })
}

test('wait subscribes before scanning and matches only exact native peer source plus literal marker', async () => {
  const host = hostFor(ownerBindings[0].config, 'wait-source')
  const spoke = host.agents.get('root-dev-alpha')
  const hub = host.agents.get('root-hub-alpha')
  const entry = host.tools.get('session_wait_for_message')
  const marker = peerMessage('valid-message', hub.id, 'reply nonce=exact-77')
  const originalOn = spoke.ctx.on.bind(spoke.ctx)
  spoke.ctx.on = (name, callback) => {
    const stop = originalOn(name, callback)
    spoke.emitSplice([marker])
    return stop
  }
  const gapResult = await entry.tool.execute({ session_id: hub.id, literal: 'nonce=exact-77', timeout_ms: 100 }, { agent: spoke, signal: new AbortController().signal })
  assert.equal(gapResult.messageId, marker.id)
  assert.equal(spoke.listeners.size, 0)

  let subscribed
  const ready = new Promise(resolvePromise => { subscribed = resolvePromise })
  spoke.ctx.on = (name, callback) => { const stop = originalOn(name, callback); subscribed(); return stop }
  const pending = entry.tool.execute({ session_id: hub.id, literal: 'nonce=exact-88', timeout_ms: 1_000 }, { agent: spoke, signal: new AbortController().signal })
  await ready
  spoke.emitSplice([peerMessage('wrong-form', hub.id, 'nonce=exact-88', { form: 'plain' })])
  spoke.emitSplice([peerMessage('wrong-sender', 'root-qa-alpha', 'nonce=exact-88')])
  spoke.emitSplice([peerMessage('wrong-literal', hub.id, 'different marker')])
  spoke.emitSplice([peerMessage('wrong-kind', hub.id, 'nonce=exact-88', { kind: 'user' })])
  spoke.emitSplice([peerMessage(undefined, hub.id, 'nonce=exact-88')])
  spoke.emitSplice([marker], hub.session)
  assert.equal(spoke.listeners.size, 1, 'unattributed, malformed, wrong-session, or nonmatching messages do not settle the wait')
  const valid = peerMessage('valid-after-subscribe', hub.id, 'nonce=exact-88')
  spoke.emitSplice([valid])
  const result = await pending
  assert.equal(result.messageId, valid.id)
  assert.equal(spoke.listeners.size, 0)
  assert.equal(host.counts.resolver, 0)
})

test('wait timeout, abort, disposal and invalid bounds clean up before leaks or target work', async () => {
  const host = hostFor(ownerBindings[0].config, 'wait-cleanup')
  const spoke = host.agents.get('root-dev-alpha')
  const hubId = 'root-hub-alpha'
  const entry = host.tools.get('session_wait_for_message')
  const timeout = await entry.tool.execute({ session_id: hubId, literal: 'absent-nonce', timeout_ms: 2 }, { agent: spoke, signal: new AbortController().signal })
  assert.equal(timeout.state, 'timeout')
  assert.equal(spoke.listeners.size, 0)

  async function subscribePending(signal) {
    let subscribed
    const ready = new Promise(resolvePromise => { subscribed = resolvePromise })
    const originalOn = spoke.ctx.on.bind(spoke.ctx)
    spoke.ctx.on = (name, callback) => { const stop = originalOn(name, callback); subscribed(); return stop }
    const pending = entry.tool.execute({ session_id: hubId, literal: 'never-arrives', timeout_ms: 1_000 }, { agent: spoke, signal })
    await ready
    return { pending }
  }

  const controller = new AbortController()
  const { pending: aborted } = await subscribePending(controller.signal)
  controller.abort()
  await assert.rejects(() => aborted)
  assert.equal(spoke.listeners.size, 0)

  const before = host.counts.workspaceResolve
  const invalid = [
    { session_id: hubId, literal: '', timeout_ms: 1 },
    { session_id: hubId, literal: '🧪'.repeat(65), timeout_ms: 1 },
    { session_id: hubId, literal: 'nonce', timeout_ms: 0 },
    { session_id: hubId, literal: 'nonce', timeout_ms: 120_001 },
    { session_id: hubId, literal: 'nonce', timeout_ms: 1.5 },
    { session_id: 'root-qa-alpha', literal: 'nonce', timeout_ms: 1 },
  ]
  for (const args of invalid) await assert.rejects(() => entry.tool.execute(args, { agent: spoke, signal: new AbortController().signal }))
  const preAborted = new AbortController()
  preAborted.abort()
  await assert.rejects(() => entry.tool.execute({ session_id: hubId, literal: 'nonce', timeout_ms: 1 }, { agent: spoke, signal: preAborted.signal }))
  assert.equal(host.counts.workspaceResolve, before)
  assert.equal(spoke.listeners.size, 0)
  assert.equal(host.counts.resolver, 0)

  const disposedHost = hostFor(ownerBindings[0].config, 'wait-disposal')
  const disposedSpoke = disposedHost.agents.get('root-dev-alpha')
  const disposedEntry = disposedHost.tools.get('session_wait_for_message')
  let subscribed
  const ready = new Promise(resolvePromise => { subscribed = resolvePromise })
  const originalOn = disposedSpoke.ctx.on.bind(disposedSpoke.ctx)
  disposedSpoke.ctx.on = (name, callback) => { const stop = originalOn(name, callback); subscribed(); return stop }
  const pending = disposedEntry.tool.execute({ session_id: hubId, literal: 'disposal-marker', timeout_ms: 1_000 }, { agent: disposedSpoke, signal: new AbortController().signal })
  await ready
  disposedHost.disposers.forEach(disposer => disposer?.())
  await assert.rejects(() => pending)
  assert.equal(disposedSpoke.listeners.size, 0)
})

test('package exposes exactly the four confirmed native coordination Tools', () => {
  const host = hostFor(ownerBindings[0].config, 'tool-inventory')
  assert.deepEqual([...host.tools.keys()].sort(), [
    'session_list',
    'session_preflight',
    'session_send_message',
    'session_wait_for_message',
  ].sort())
  const privateValues = [ownerBindings[0].config.workspacePath, ...Object.values(ownerBindings[0].config.roles)]
  for (const { tool } of host.tools.values()) {
    const schema = JSON.stringify(tool.parameters)
    for (const value of privateValues) assert.equal(schema.includes(value), false)
  }
})
