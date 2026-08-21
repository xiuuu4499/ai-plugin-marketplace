# Kilo Adapter

The Kilo runtime plugin enforces this policy in the `chat.params` hook before each matching model request.

## Installed Files

The installer copies owned files to the Kilo global config directory:

```text
~/.config/kilo/
├── plugin/qwen38-generation-policy.js
├── agents/*.md
└── skills/qwen38-generation-policy/
```

Use `KILO_TARGET_CONFIG_DIR` to install to another Kilo config root for tests or unusual environments. `KILO_CONFIG_DIR` is intentionally not used as the installer default because Kilo treats it as an additional config directory rather than always as the canonical user config root.

## Profile Overrides

The plugin keeps explicit overrides in Kilo plugin session state. Use one of:

```text
/qwen-profile coding-agent-medium
/qwen38-profile chat-reasoning-xhigh
/qwen-profile reset
```

Agent defaults apply when no session override exists.

## Provider Setup

The v1 installer does not rewrite `kilo.jsonc`. Configure a local OpenAI-compatible provider named `local-qwen` through Kilo settings or by adding an equivalent provider definition to global config. The policy applies only when the outgoing provider/model context matches configured Qwen3.8 aliases.
