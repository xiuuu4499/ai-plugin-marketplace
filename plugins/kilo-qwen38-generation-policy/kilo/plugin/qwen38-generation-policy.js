const THINKING_BASELINE = {
  thinking: true,
  reasoningEffort: "xhigh",
  preserveThinking: true,
  temperature: 1.0,
  topP: 0.95,
  topK: 20,
  minP: 0.0,
  presencePenalty: 0.0,
  frequencyPenalty: 0.0,
  repetitionPenalty: 1.0,
}

const INSTRUCT_BASELINE = {
  thinking: false,
  reasoningEffort: "none",
  preserveThinking: false,
  temperature: 0.7,
  topP: 0.8,
  topK: 20,
  minP: 0.0,
  presencePenalty: 1.5,
  frequencyPenalty: 0.0,
  repetitionPenalty: 1.0,
}

const PROFILES = {
  "coding-plan-xhigh": { ...THINKING_BASELINE, reasoningEffort: "xhigh" },
  "coding-agent-xhigh": { ...THINKING_BASELINE, reasoningEffort: "xhigh" },
  "coding-agent-medium": { ...THINKING_BASELINE, reasoningEffort: "medium" },
  "chat-direct": { ...INSTRUCT_BASELINE },
  "chat-reasoning-medium": { ...THINKING_BASELINE, reasoningEffort: "medium" },
  "chat-reasoning-xhigh": { ...THINKING_BASELINE, reasoningEffort: "xhigh" },
  "prose-plan-medium": { ...THINKING_BASELINE, reasoningEffort: "medium" },
  "prose-write-direct": { ...INSTRUCT_BASELINE },
  "media-prompt-direct": { ...INSTRUCT_BASELINE },
  "media-prompt-reasoning-medium": { ...THINKING_BASELINE, reasoningEffort: "medium" },
  "think-xhigh": { ...THINKING_BASELINE, reasoningEffort: "xhigh" },
  "think-medium": { ...THINKING_BASELINE, reasoningEffort: "medium" },
  "think-low": { ...THINKING_BASELINE, reasoningEffort: "low" },
  instruct: { ...INSTRUCT_BASELINE },
}

const AGENT_PROFILES = {
  plan: "coding-plan-xhigh",
  code: "coding-agent-xhigh",
  chat: "chat-direct",
  "chat-reasoning": "chat-reasoning-medium",
  prose: "prose-write-direct",
  "media-prompt": "media-prompt-direct",
  "media-prompt-reasoning": "media-prompt-reasoning-medium",
}

const DEFAULT_MODEL_PATTERNS = ["qwen3.8-27b", "qwen3-8-27b", "qwen3.8", "qwen38"]
const sessionOverrides = new Map()

function normalize(value) {
  return String(value || "").trim().toLowerCase()
}

export function isManagedQwenModel(input, options = {}) {
  const patterns = Array.isArray(options.modelAliases) && options.modelAliases.length > 0
    ? options.modelAliases
    : DEFAULT_MODEL_PATTERNS
  const haystack = [
    input?.model?.id,
    input?.model?.modelID,
    input?.model?.name,
    input?.provider?.info?.id,
    input?.provider?.info?.name,
  ].map(normalize).join(" ")
  return patterns.map(normalize).some((pattern) => pattern && haystack.includes(pattern))
}

export function profileForAgent(agent, options = {}) {
  const mapping = { ...AGENT_PROFILES, ...(options.agentProfiles || {}) }
  return mapping[agent] || options.defaultProfile || "coding-agent-xhigh"
}

export function resolveProfile(input, options = {}) {
  const sessionProfile = sessionOverrides.get(input.sessionID)
  const selected = sessionProfile || profileForAgent(input.agent, options)
  const profile = PROFILES[selected]
  if (!profile) {
    throw new Error(`unknown Qwen3.8 generation profile: ${selected}`)
  }
  return { name: selected, values: profile, source: sessionProfile ? "session-override" : "agent-default" }
}

export function applyProfile(output, profile) {
  output.temperature = profile.temperature
  output.topP = profile.topP
  output.topK = profile.topK
  output.options = {
    ...(output.options || {}),
    min_p: profile.minP,
    presence_penalty: profile.presencePenalty,
    frequency_penalty: profile.frequencyPenalty,
    repeat_penalty: profile.repetitionPenalty,
    reasoning_effort: profile.reasoningEffort,
    chat_template_kwargs: {
      ...((output.options || {}).chat_template_kwargs || {}),
      enable_thinking: profile.thinking,
      preserve_thinking: profile.preserveThinking,
    },
  }
}

function parseProfileCommand(command, args) {
  if (!["qwen-profile", "qwen38-profile", "qwen-policy-profile"].includes(command)) return null
  const requested = String(args || "").trim()
  if (requested === "auto" || requested === "reset" || requested === "default") return { reset: true }
  if (!PROFILES[requested]) {
    throw new Error(`unknown Qwen3.8 profile '${requested}'. Known profiles: ${Object.keys(PROFILES).sort().join(", ")}`)
  }
  return { profile: requested }
}

const server = async ({ client }, options = {}) => ({
  "command.execute.before": async (input, output) => {
    const parsed = parseProfileCommand(input.command, input.arguments)
    if (!parsed) return
    if (parsed.reset) {
      sessionOverrides.delete(input.sessionID)
      output.parts = [{ type: "text", text: "Qwen3.8 profile override reset to automatic agent defaults." }]
      return
    }
    sessionOverrides.set(input.sessionID, parsed.profile)
    output.parts = [{ type: "text", text: `Qwen3.8 profile override set to ${parsed.profile} for this session.` }]
  },
  "chat.params": async (input, output) => {
    if (!isManagedQwenModel(input, options)) return
    const resolved = resolveProfile(input, options)
    applyProfile(output, resolved.values)
    if (client?.app?.log) {
      await client.app.log({
        body: {
          service: "qwen38-generation-policy",
          level: "info",
          message: "applied Qwen3.8 generation profile",
          extra: {
            sessionID: input.sessionID,
            agent: input.agent,
            profile: resolved.name,
            source: resolved.source,
          },
        },
      })
    }
  },
})

export default { id: "qwen38-generation-policy", server }
