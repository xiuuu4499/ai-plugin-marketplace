# llama.cpp Mapping

Keep task-specific generation settings out of the `llama-server` command line. Server flags should cover model paths, alias, host, port, context size, GPU/runtime behavior, Jinja/chat-template support, and reasoning support.

The plugin maps canonical policy fields to an OpenAI-compatible llama.cpp request:

| Canonical | Request field |
| --- | --- |
| `sampling.temperature` | `temperature` |
| `sampling.top_p` | `top_p` |
| `sampling.top_k` | `top_k` |
| `sampling.min_p` | `min_p` |
| `sampling.presence_penalty` | `presence_penalty` |
| `sampling.frequency_penalty` | `frequency_penalty` |
| `sampling.repetition_penalty` | `repeat_penalty` |
| `thinking.reasoning_effort` | `reasoning_effort` |
| `thinking.enabled` | `chat_template_kwargs.enable_thinking` |
| `thinking.preserve_thinking` | `chat_template_kwargs.preserve_thinking` |

Verify wire output against the actual llama.cpp or mock OpenAI-compatible endpoint after Kilo upgrades.
