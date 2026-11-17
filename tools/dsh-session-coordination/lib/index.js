import { createHash, randomUUID } from 'node:crypto'
import { isAbsolute, normalize, resolve } from 'node:path'

export const name = 'dsh-session-coordination'
export const inject = Object.freeze([
  'agents',
  'sessions',
  'sessionController',
  'sessionPersistence',
  'tools',
  'workspaceRegistry',
])

const LIST_TOOL = 'session_list'
const SEND_TOOL = 'session_send_message'
const PREFLIGHT_TOOL = 'session_preflight'
const WAIT_TOOL = 'session_wait_for_message'
const TOOL_NAMES = Object.freeze([LIST_TOOL, PREFLIGHT_TOOL, SEND_TOOL, WAIT_TOOL])
const MAX_BYTES = 65_536
const NULLABLE_STRING = Object.freeze({ oneOf: [{ type: 'string' }, { type: 'null' }] })

function fail(message) {
  throw new Error(message)
}

function dataValue(descriptors, key, required = false) {
  const descriptor = descriptors[key]
  if (!descriptor) {
    if (required) fail(`missing owner configuration field: ${key}`)
    return undefined
  }
  if (!Object.hasOwn(descriptor, 'value')) fail(`accessor configuration field is unsupported: ${key}`)
  return descriptor.value
}

function normalizeConfig(raw) {
  if (raw === null || typeof raw !== 'object' || Array.isArray(raw)) fail('owner startup configuration is required')
  const descriptors = Object.getOwnPropertyDescriptors(raw)
  const allowed = new Set(['workspacePath', 'hubRole', 'roles', 'maxMessageBytes'])
  if (Reflect.ownKeys(descriptors).some(key => typeof key !== 'string' || !allowed.has(key))) fail('unsupported owner configuration field')

  const workspacePath = dataValue(descriptors, 'workspacePath', true)
  if (typeof workspacePath !== 'string' || !workspacePath || workspacePath !== workspacePath.trim() || workspacePath.includes('\0') || !isAbsolute(workspacePath) || normalize(workspacePath) !== workspacePath || resolve(workspacePath) !== workspacePath) {
    fail('workspacePath must be a canonical absolute native path')
  }

  const hubRole = dataValue(descriptors, 'hubRole', true)
  if (typeof hubRole !== 'string' || !hubRole || hubRole !== hubRole.trim() || /[\u0000-\u001f\u007f]/u.test(hubRole)) fail('hubRole must be an exact role label')

  const inputRoles = dataValue(descriptors, 'roles', true)
  if (inputRoles === null || typeof inputRoles !== 'object' || Array.isArray(inputRoles) || ![Object.prototype, null].includes(Object.getPrototypeOf(inputRoles))) {
    fail('roles must be a plain label-to-root mapping')
  }
  const roleDescriptors = Object.getOwnPropertyDescriptors(inputRoles)
  const labels = Reflect.ownKeys(roleDescriptors)
  if (labels.length === 0) fail('roles must contain at least the hub role')
  const roles = Object.create(null)
  const roleById = Object.create(null)
  const rootIds = []
  for (const label of labels) {
    const descriptor = roleDescriptors[label]
    if (typeof label !== 'string' || !descriptor.enumerable || !Object.hasOwn(descriptor, 'value')) fail('roles must contain enumerable data fields only')
    const id = descriptor.value
    if (!label || label !== label.trim() || /[\u0000-\u001f\u007f]/u.test(label)) fail('role labels must be nonempty exact strings')
    if (typeof id !== 'string' || !id || id !== id.trim() || Buffer.byteLength(id, 'utf8') > 256 || /[\u0000-\u001f\u007f]/u.test(id)) fail('role roots must be nonempty exact root IDs')
    if (Object.hasOwn(roleById, id)) fail('each configured root ID must have exactly one role')
    roles[label] = id
    roleById[id] = label
    rootIds.push(id)
  }
  if (!Object.hasOwn(roles, hubRole)) fail('hubRole must name one configured role')

  const maxDescriptor = descriptors.maxMessageBytes
  const maxMessageBytes = maxDescriptor ? dataValue(descriptors, 'maxMessageBytes') : MAX_BYTES
  if (!Number.isSafeInteger(maxMessageBytes) || maxMessageBytes < 1 || maxMessageBytes > MAX_BYTES) fail('maxMessageBytes must be a positive safe integer at most 65536')

  Object.freeze(roles)
  Object.freeze(roleById)
  Object.freeze(rootIds)
  return Object.freeze({
    workspacePath,
    hubRole,
    hubId: roles[hubRole],
    roles,
    roleById,
    rootIds,
    maxMessageBytes,
  })
}

function visibleRoots(config, id) {
  if (!Object.hasOwn(config.roleById, id)) return []
  if (id === config.hubId) return [...config.rootIds]
  return [id, config.hubId]
}

function ordinary(header, id) {
  if (header?.id !== id || header.origin === 'subagent' || (header.delegationDepth ?? 0) !== 0) fail('an ordinary root session header is required')
}

function live(ctx, agent, id, config) {
  if (!Object.hasOwn(config.roleById, id) || agent?.id !== id || agent.session?.id !== id || ctx.agents.get(id) !== agent || !ctx.agents.roots().includes(agent)) {
    fail('the exact configured runtime root is unavailable')
  }
  ordinary(agent.session.header, id)
  return agent
}

function caller(ctx, exec, closed, config) {
  if (closed()) fail('coordination Tools are disposed')
  if (typeof exec?.signal?.throwIfAborted !== 'function' || typeof exec.signal.addEventListener !== 'function' || typeof exec.signal.removeEventListener !== 'function') {
    fail('native Tool cancellation context is required')
  }
  exec.signal.throwIfAborted()
  const id = exec?.agent?.id
  if (!Object.hasOwn(config.roleById, id)) fail('caller is not a configured owner role root')
  const agent = live(ctx, exec.agent, id, config)
  if (agent.session.header.cwd !== config.workspacePath) fail('caller is outside the configured workspace')
  return agent
}

function argsObject(args, keys) {
  if (!args || typeof args !== 'object' || Array.isArray(args) || Object.keys(args).some(key => !keys.includes(key))) fail('invalid Tool arguments')
}

function recipient(config, id, senderId, allowSelf = false) {
  if (!visibleRoots(config, senderId).includes(id) || (!allowSelf && id === senderId)) fail('recipient or edge is not approved by owner configuration')
}

function registry(ctx) {
  const value = ctx.get('workspaceRegistry')
  if (!value) fail('workspace registry unavailable')
  return value
}

function workspaceGuard(ctx, workspaceId, sessionIds, config) {
  const reg = registry(ctx)
  const workspace = reg.get(workspaceId)
  if (!workspace || workspace.path !== config.workspacePath || !Array.isArray(workspace.sessionIds) || !Array.isArray(reg.archivedSessionIds)) {
    fail('configured workspace metadata unavailable')
  }
  for (const id of sessionIds) {
    if (!workspace.sessionIds.includes(id) || reg.archivedSessionIds.includes(id)) fail('session is outside configured workspace membership or archived')
  }
  return workspace
}

function headerGuard(header, id, workspace) {
  ordinary(header, id)
  if (header.cwd !== workspace.path) fail('session header is outside the configured workspace')
}

function check(ctx, exec, closed, config, workspaceId, ids, expectedCaller) {
  const sender = caller(ctx, exec, closed, config)
  if (expectedCaller && sender !== expectedCaller) fail('calling root changed during admission')
  const workspace = workspaceGuard(ctx, workspaceId, [sender.id, ...ids], config)
  headerGuard(sender.session.header, sender.id, workspace)
  for (const id of ids) {
    const target = ctx.agents.get(id)
    if (target) {
      live(ctx, target, id, config)
      headerGuard(target.session.header, id, workspace)
    }
  }
  return { sender, workspace }
}

async function admit(ctx, exec, closed, config, ids) {
  const sender = caller(ctx, exec, closed, config)
  const found = await registry(ctx).resolveByPath(config.workspacePath)
  caller(ctx, exec, closed, config)
  if (!found?.id) fail('configured workspace is not registered')
  let state = check(ctx, exec, closed, config, found.id, ids, sender)
  const headers = new Map()
  for (const id of ids) {
    const attached = ctx.sessions.get(id)
    const header = attached?.header ?? (await ctx.sessionPersistence.stat(id, { signal: exec.signal }))?.header
    state = check(ctx, exec, closed, config, found.id, ids, sender)
    if (!header) fail('configured session metadata unavailable')
    headerGuard(header, id, state.workspace)
    headers.set(id, {
      id: header.id,
      cwd: header.cwd,
      origin: header.origin,
      delegationDepth: header.delegationDepth,
      agentPreset: header.agentPreset,
    })
  }
  check(ctx, exec, closed, config, found.id, ids, sender)
  return { sender, workspaceId: found.id, headers }
}

function policy(ctx, agent, header) {
  const selection = agent?.model?.current?.()
  const projectedPermission = agent
    ? ctx.get('sessionProjections')?.snapshot(agent.session, ['permissions']).values.permissions?.currentValue
    : undefined
  const presets = agent ? ctx.get('agentPresets') : undefined
  const selectedPreset = presets?.presetForSession(agent.session)
  const string = value => typeof value === 'string' ? value : null
  const permission = string(projectedPermission) ?? (agent ? string(presets?.serviceFor(agent, 'permissionPresets')?.current(agent.session)) : null)
  const preset = string(selectedPreset) ?? string(header.agentPreset)
  const fields = {
    agentPreset: preset,
    agentPresetSource: string(selectedPreset) ? 'live_selection' : string(header.agentPreset) ? 'creation_header' : 'unknown',
    provider: string(selection?.provider),
    model: string(selection?.model),
    reasoningEffort: string(selection?.reasoningEffort),
    reasoningEffortState: selection ? selection.reasoningEffort === undefined ? 'provider-default' : 'explicit' : 'unknown',
    permissions: permission,
  }
  return {
    ...fields,
    fingerprint: createHash('sha256').update(JSON.stringify(fields)).digest('hex'),
    limit: 'partial named model/preset/permission metadata only; null means unknown; not complete effective-policy or unchanged-policy proof',
  }
}

async function waitForMessage(ctx, config, args, exec, closed, pending) {
  const sender = caller(ctx, exec, closed, config)
  argsObject(args, ['session_id', 'literal', 'timeout_ms'])
  recipient(config, args.session_id, sender.id)
  if (typeof args.literal !== 'string' || !args.literal.trim() || Buffer.byteLength(args.literal, 'utf8') > 256 || !Number.isSafeInteger(args.timeout_ms) || args.timeout_ms < 1 || args.timeout_ms > 120_000) {
    fail('wait requires a nonempty literal at most 256 bytes and timeout_ms from 1 through 120000')
  }
  const admission = await admit(ctx, exec, closed, config, [args.session_id])
  check(ctx, exec, closed, config, admission.workspaceId, [args.session_id], sender)
  const session = sender.session
  if (typeof sender.ctx?.on !== 'function' || !Array.isArray(sender.inbox?.nextStep) || !Array.isArray(sender.inbox?.nextTurn)) fail('native own-inbox observation is unavailable')
  const guard = () => {
    check(ctx, exec, closed, config, admission.workspaceId, [args.session_id], sender)
    if (sender.session !== session) fail('calling session changed while waiting')
  }
  const result = await new Promise((resolvePromise, reject) => {
    let settled = false
    let stop
    let timer
    const finish = (error, value) => {
      if (settled) return
      settled = true
      clearTimeout(timer)
      exec.signal.removeEventListener('abort', abort)
      stop?.()
      pending.delete(cancel)
      if (error) reject(error)
      else resolvePromise(value)
    }
    const cancel = error => finish(error)
    const abort = () => finish(exec.signal.reason ?? new Error('wait aborted'))
    const inspectMessage = message => {
      if (settled || message?.source?.kind !== 'agent-message' || message.source.form !== 'relay' || message.source.senderSessionId !== args.session_id || typeof message.id !== 'string' || !Array.isArray(message.content)) return
      if (!message.content.some(block => block.type === 'text' && typeof block.text === 'string' && block.text.includes(args.literal))) return
      try {
        guard()
        finish(undefined, {
          sessionId: args.session_id,
          state: 'observed',
          messageId: message.id,
          observation: 'peer_inbox_message_only',
          note: 'Observed a native peer message containing the literal marker, not an ACK or task-completion judgment.',
        })
      } catch (error) {
        finish(error)
      }
    }

    pending.add(cancel)
    try {
      stop = sender.ctx.on('session/event', (observed, event) => {
        if (observed !== session || event.type !== 'agent/inbox/spliced' || !Array.isArray(event.data?.inserted)) return
        for (const message of event.data.inserted) inspectMessage(message)
      })
      // A synchronous arrival during subscription must release the returned listener.
      if (settled) {
        stop?.()
        return
      }
      exec.signal.addEventListener('abort', abort, { once: true })
      timer = setTimeout(() => {
        try {
          guard()
          finish(undefined, {
            sessionId: args.session_id,
            state: 'timeout',
            messageId: null,
            observation: 'not_observed',
            note: 'No matching pending peer message was observed within this Tool call; no delivery/completion conclusion.',
          })
        } catch (error) {
          finish(error)
        }
      }, args.timeout_ms)
      if (exec.signal.aborted) {
        abort()
        return
      }
      if (closed()) {
        cancel(new Error('coordination plugin disposed'))
        return
      }
      // Subscribe first, then inspect only the current inbox lists. Never read history or consume messages.
      for (const message of [...sender.inbox.nextStep, ...sender.inbox.nextTurn]) inspectMessage(message)
    } catch (error) {
      finish(error)
    }
  })
  guard()
  return result
}

function deepFreeze(value) {
  if (value && typeof value === 'object' && !Object.isFrozen(value)) {
    Object.freeze(value)
    for (const child of Object.values(value)) deepFreeze(child)
  }
  return value
}

function relayContent(sender, text) {
  const id = JSON.stringify(sender.id)
  return [
    { type: 'text', text: `Message from session ${id}. It was written by that session's agent, not by your user. To answer, call ${SEND_TOOL} with session_id ${id}; do not reply only to acknowledge it.\n\n` },
    { type: 'text', text },
  ]
}

async function send(ctx, config, args, exec, closed) {
  const sender = caller(ctx, exec, closed, config)
  argsObject(args, ['session_id', 'message', 'delivery'])
  recipient(config, args.session_id, sender.id)
  if (typeof args.message !== 'string' || !args.message.trim()) fail('message must contain non-whitespace text')
  const delivery = args.delivery ?? 'steer'
  if (delivery !== 'steer' && delivery !== 'queue') fail('delivery must be steer or queue')
  const content = relayContent(sender, args.message)
  if (Buffer.byteLength(JSON.stringify(content), 'utf8') > config.maxMessageBytes) fail('message exceeds owner-configured byte limit')

  const admission = await admit(ctx, exec, closed, config, [args.session_id])
  check(ctx, exec, closed, config, admission.workspaceId, [args.session_id], sender)
  const before = ctx.agents.get(args.session_id)
  const state = before ? before.status === 'running' ? 'running' : 'idle' : 'stored'
  if (typeof ctx.agents.withoutInitiator !== 'function' || typeof ctx.sessionController?.resolveAgent !== 'function') fail('native cold-root resolver unavailable')
  const resolved = await ctx.agents.withoutInitiator(() => ctx.sessionController.resolveAgent(args.session_id))
  check(ctx, exec, closed, config, admission.workspaceId, [args.session_id], sender)
  if (resolved?.error || !resolved?.agent) fail('native resolver refused; no inbox dispatch attempted')
  const target = live(ctx, resolved.agent, args.session_id, config)
  if (before && before !== target) fail('known live target changed during resolution')
  if (target.session.header.agentPreset !== admission.headers.get(args.session_id).agentPreset) fail('captured target preset changed during resolution')
  headerGuard(target.session.header, args.session_id, workspaceGuard(ctx, admission.workspaceId, [sender.id, args.session_id], config))

  const message = deepFreeze({
    id: randomUUID(),
    role: 'user',
    content,
    source: { kind: 'agent-message', form: 'relay', senderSessionId: sender.id },
  })
  let acceptance = 'unknown'
  let dispatchEntered = false
  try {
    ctx.agents.withoutInitiator(() => {
      check(ctx, exec, closed, config, admission.workspaceId, [args.session_id], sender)
      live(ctx, target, args.session_id, config)
      dispatchEntered = true
      if (delivery === 'queue') target.followup(message)
      else target.steer(message)
    })
    acceptance = 'accepted'
  } catch (error) {
    if (!dispatchEntered) throw error
    return {
      sessionId: args.session_id,
      messageId: message.id,
      state,
      delivery,
      acceptance: 'unknown',
      persistence: 'not_attempted',
      recipientResult: 'not_observed',
      note: 'Native dispatch threw; inbox acceptance is unknown. Do not retry blindly.',
    }
  }

  let persistence = 'flushed'
  try {
    if (await ctx.sessions.flush(target.session) !== true) persistence = 'no_durability_listener'
  } catch {
    persistence = 'flush_failed'
  }
  return {
    sessionId: args.session_id,
    messageId: message.id,
    state,
    delivery,
    acceptance,
    persistence,
    recipientResult: 'not_observed',
    note: 'Inbox acceptance is not an ACK/result or proof of task completion. Do not duplicate on flush failure.',
  }
}

function finalizeSendContent(_exec, result) {
  try {
    if (result?.isError !== true || result.error?.info?.code !== 'ABORTED' || !Array.isArray(result.content)) return undefined
    return [...result.content, {
      type: 'text',
      text: 'Delivery UNKNOWN: cancellation may have occurred after inbox acceptance or recipient execution. The aborted result does not provide a recoverable delivery receipt/message ID. Do not retry blindly; establish receipt through the approved peer channel first. This is not an ACK/result or proof of non-delivery.',
    }]
  } catch {
    return undefined
  }
}

async function inspect(ctx, config, args, exec, closed, list) {
  caller(ctx, exec, closed, config)
  argsObject(args, list ? [] : ['session_id'])
  if (!list) recipient(config, args.session_id, exec.agent.id, true)
  const ids = list ? visibleRoots(config, exec.agent.id) : [args.session_id]
  const admission = await admit(ctx, exec, closed, config, ids)
  check(ctx, exec, closed, config, admission.workspaceId, ids, admission.sender)
  return {
    workspaceId: admission.workspaceId,
    workspace: config.workspacePath,
    sessions: ids.map(id => {
      const agent = ctx.agents.get(id)
      return {
        sessionId: id,
        role: config.roleById[id],
        state: agent ? agent.status === 'running' ? 'running' : 'idle' : 'stored',
        runtimeRoot: agent ? true : null,
        policy: policy(ctx, agent, admission.headers.get(id)),
      }
    }),
    qualification: 'read-only metadata; no resume; stored runtime ownership and complete policy remain unknown',
  }
}

const policySchema = {
  type: 'object',
  additionalProperties: false,
  required: ['agentPreset', 'agentPresetSource', 'provider', 'model', 'reasoningEffort', 'reasoningEffortState', 'permissions', 'fingerprint', 'limit'],
  properties: {
    agentPreset: NULLABLE_STRING,
    agentPresetSource: { type: 'string' },
    provider: NULLABLE_STRING,
    model: NULLABLE_STRING,
    reasoningEffort: NULLABLE_STRING,
    reasoningEffortState: { type: 'string' },
    permissions: NULLABLE_STRING,
    fingerprint: { type: 'string' },
    limit: { type: 'string' },
  },
}
const inspectSchema = {
  type: 'object',
  additionalProperties: false,
  required: ['workspaceId', 'workspace', 'sessions', 'qualification'],
  properties: {
    workspaceId: { type: 'string' },
    workspace: { type: 'string' },
    qualification: { type: 'string' },
    sessions: {
      type: 'array',
      items: {
        type: 'object',
        additionalProperties: false,
        required: ['sessionId', 'role', 'state', 'runtimeRoot', 'policy'],
        properties: {
          sessionId: { type: 'string' },
          role: { type: 'string' },
          state: { type: 'string' },
          runtimeRoot: { oneOf: [{ type: 'boolean' }, { type: 'null' }] },
          policy: policySchema,
        },
      },
    },
  },
}

const waitSchema = {
  type: 'object',
  additionalProperties: false,
  required: ['sessionId', 'state', 'messageId', 'observation', 'note'],
  properties: {
    sessionId: { type: 'string' },
    state: { type: 'string', enum: ['observed', 'timeout'] },
    messageId: NULLABLE_STRING,
    observation: { type: 'string' },
    note: { type: 'string' },
  },
}

const sendSchema = {
  type: 'object',
  additionalProperties: false,
  required: ['sessionId', 'messageId', 'state', 'delivery', 'acceptance', 'persistence', 'recipientResult', 'note'],
  properties: Object.fromEntries(['sessionId', 'messageId', 'state', 'delivery', 'acceptance', 'persistence', 'recipientResult', 'note'].map(key => [key, { type: 'string' }])),
}

export function apply(ctx, rawConfig) {
  const config = normalizeConfig(rawConfig)
  let disposed = false
  const closed = () => disposed
  const pendingWaits = new Set()
  ctx.effect(() => () => {
    disposed = true
    for (const cancel of [...pendingWaits]) cancel(new Error('coordination plugin disposed'))
    pendingWaits.clear()
  })
  const when = ({ agent, signal }) => {
    try {
      caller(ctx, { agent, signal }, closed, config)
      return true
    } catch {
      return false
    }
  }
  const register = tool => ctx.tools.register(tool, { when })
  for (const [toolName, list] of [[LIST_TOOL, true], [PREFLIGHT_TOOL, false]]) {
    const properties = list ? {} : { session_id: { type: 'string', description: 'Exact session ID visible to this caller in session_list.' } }
    register({
      name: toolName,
      description: 'Read only this caller’s owner-configured hub/spoke identities and partial named policy metadata. No other sessions are enumerated or resumed; unknown policy remains unknown.',
      parameters: { type: 'object', additionalProperties: false, ...(list ? {} : { required: ['session_id'] }), properties },
      output: { schema: inspectSchema, render: (_args, value) => [{ type: 'text', text: JSON.stringify(value) }] },
      isConcurrencySafe: () => true,
      presentCall: () => ({ card: 'generic', kind: 'search', title: 'Configured role identity' }),
      execute: (args, exec) => inspect(ctx, config, args, exec, closed, list),
    })
  }
  register({
    name: SEND_TOOL,
    description: 'Send one attributed native message only along the caller’s owner-configured hub/spoke edge. STEER is the default; queue must be requested explicitly. Returns inbox acceptance, not an ACK/result; never changes session settings. Canonical ABORTED may discard a receipt after dispatch: delivery remains unknown, so never retry blindly.',
    parameters: {
      type: 'object',
      additionalProperties: false,
      required: ['session_id', 'message'],
      properties: {
        session_id: { type: 'string', description: 'Exact session ID visible to this caller in session_list.' },
        message: { type: 'string' },
        delivery: { type: 'string', enum: ['steer', 'queue'] },
      },
    },
    output: { schema: sendSchema, render: (_args, value) => [{ type: 'text', text: JSON.stringify(value) }] },
    finalizeContent: finalizeSendContent,
    presentCall: args => ({ card: 'generic', kind: 'other', title: 'Send approved peer message', rawInput: typeof args?.message === 'string' ? args.message : '' }),
    execute: (args, exec) => send(ctx, config, args, exec, closed),
  })
  register({
    name: WAIT_TOOL,
    description: 'Passively observe only this caller’s current inbox for one exact configured peer relay containing a literal marker. No send, resume, or history lookup; the observed message ID is not an ACK or task-completion judgment.',
    parameters: {
      type: 'object',
      additionalProperties: false,
      required: ['session_id', 'literal', 'timeout_ms'],
      properties: {
        session_id: { type: 'string', description: 'Exact session ID visible to this caller in session_list.' },
        literal: { type: 'string', description: 'A literal marker to match in native peer message text; at most 256 UTF-8 bytes.' },
        timeout_ms: { type: 'integer', description: 'Observation timeout from 1 through 120000 milliseconds.' },
      },
    },
    output: { schema: waitSchema, render: (_args, value) => [{ type: 'text', text: JSON.stringify(value) }] },
    presentCall: () => ({ card: 'generic', kind: 'other', title: 'Wait for configured peer inbox marker' }),
    execute: (args, exec) => waitForMessage(ctx, config, args, exec, closed, pendingWaits),
  })
}
