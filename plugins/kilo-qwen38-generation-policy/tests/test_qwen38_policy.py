import json
import threading
import subprocess
import tempfile
import textwrap
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "kilo" / "plugin" / "qwen38-generation-policy.js"


def run_node(script):
    with tempfile.TemporaryDirectory() as tmp:
        module = Path(tmp) / "plugin.mjs"
        module.write_text(PLUGIN.read_text(), encoding="utf-8")
        runner = Path(tmp) / "runner.mjs"
        runner.write_text(script.replace("__PLUGIN__", module.as_posix()), encoding="utf-8")
        result = subprocess.run(["node", runner.as_posix()], check=True, text=True, capture_output=True)
        return json.loads(result.stdout)


class Qwen38PolicyTests(unittest.TestCase):
    def test_agent_profile_resolution(self):
        data = run_node(
            textwrap.dedent(
                """
                import { resolveProfile } from "__PLUGIN__"
                const input = { sessionID: "s1", agent: "chat-reasoning" }
                console.log(JSON.stringify(resolveProfile(input)))
                """
            )
        )
        self.assertEqual(data["name"], "chat-reasoning-medium")
        self.assertEqual(data["values"]["reasoningEffort"], "medium")

    def test_model_gating(self):
        data = run_node(
            textwrap.dedent(
                """
                import { isManagedQwenModel } from "__PLUGIN__"
                const qwen = { model: { id: "qwen3.8-27b" }, provider: { info: { id: "local-qwen" } } }
                const claude = { model: { id: "claude-sonnet-4" }, provider: { info: { id: "anthropic" } } }
                console.log(JSON.stringify({ qwen: isManagedQwenModel(qwen), claude: isManagedQwenModel(claude) }))
                """
            )
        )
        self.assertTrue(data["qwen"])
        self.assertFalse(data["claude"])

    def test_resolved_request_profiles(self):
        data = run_node(
            textwrap.dedent(
                """
                import { applyProfile, resolveProfile } from "__PLUGIN__"
                function outputFor(agent) {
                  const resolved = resolveProfile({ sessionID: agent, agent })
                  const output = { temperature: 0, topP: 0, topK: 0, options: {} }
                  applyProfile(output, resolved.values)
                  return output
                }
                console.log(JSON.stringify({
                  plan: outputFor("plan"),
                  routine: (() => {
                    const resolved = resolveProfile({ sessionID: "s2", agent: "code" }, { agentProfiles: { code: "coding-agent-medium" } })
                    const output = { options: {} }
                    applyProfile(output, resolved.values)
                    return output
                  })(),
                  chat: outputFor("chat"),
                  media: outputFor("media-prompt-reasoning")
                }))
                """
            )
        )
        self.assertEqual(data["plan"]["temperature"], 1.0)
        self.assertEqual(data["plan"]["topP"], 0.95)
        self.assertEqual(data["plan"]["topK"], 20)
        self.assertEqual(data["plan"]["options"]["reasoning_effort"], "xhigh")
        self.assertEqual(data["routine"]["options"]["reasoning_effort"], "medium")
        self.assertEqual(data["chat"]["temperature"], 0.7)
        self.assertEqual(data["chat"]["options"]["presence_penalty"], 1.5)
        self.assertFalse(data["chat"]["options"]["chat_template_kwargs"]["enable_thinking"])
        self.assertEqual(data["media"]["options"]["reasoning_effort"], "medium")

    def test_hook_leaves_non_qwen_unchanged(self):
        data = run_node(
            textwrap.dedent(
                """
                import plugin from "__PLUGIN__"
                const hooks = await plugin.server({ client: {} })
                const output = { temperature: 0.2, topP: 0.3, topK: 4, options: { untouched: true } }
                await hooks["chat.params"]({
                  sessionID: "s1",
                  agent: "chat",
                  model: { id: "claude-sonnet-4" },
                  provider: { info: { id: "anthropic" } },
                  message: {}
                }, output)
                console.log(JSON.stringify(output))
                """
            )
        )
        self.assertEqual(data, {"temperature": 0.2, "topP": 0.3, "topK": 4, "options": {"untouched": True}})

    def test_mock_openai_endpoint_captures_managed_request_bodies(self):
        captured = []

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                length = int(self.headers.get("content-length", "0"))
                captured.append(json.loads(self.rfile.read(length)))
                self.send_response(200)
                self.send_header("content-type", "application/json")
                self.end_headers()
                self.wfile.write(b'{"id":"test","choices":[{"message":{"role":"assistant","content":"ok"}}]}')

            def log_message(self, *_args):
                return

        server = HTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            data = run_node(
                textwrap.dedent(
                    f"""
                    import plugin from "__PLUGIN__"
                    const hooks = await plugin.server({{ client: {{}} }})
                    async function send(agent, sessionID) {{
                      const output = {{ options: {{}} }}
                      await hooks["chat.params"]({{
                        sessionID,
                        agent,
                        model: {{ id: "qwen3.8-27b" }},
                        provider: {{ info: {{ id: "local-qwen" }} }},
                        message: {{}}
                      }}, output)
                      const body = {{
                        model: "qwen3.8-27b",
                        messages: [{{ role: "user", content: "ping" }}],
                        temperature: output.temperature,
                        top_p: output.topP,
                        top_k: output.topK,
                        ...output.options
                      }}
                      await fetch("http://127.0.0.1:{server.server_port}/v1/chat/completions", {{
                        method: "POST",
                        headers: {{ "content-type": "application/json" }},
                        body: JSON.stringify(body)
                      }})
                    }}
                    await send("plan", "xhigh")
                    await hooks["command.execute.before"]({{ command: "qwen-profile", arguments: "think-medium", sessionID: "medium" }}, {{ parts: [] }})
                    await send("chat", "medium")
                    await hooks["command.execute.before"]({{ command: "qwen-profile", arguments: "think-low", sessionID: "low" }}, {{ parts: [] }})
                    await send("chat", "low")
                    await send("chat", "instruct")
                    console.log(JSON.stringify({{ ok: true }}))
                    """
                )
            )
            self.assertTrue(data["ok"])
        finally:
            server.shutdown()
            thread.join(timeout=2)
            server.server_close()

        self.assertEqual([body["reasoning_effort"] for body in captured], ["xhigh", "medium", "low", "none"])
        self.assertEqual(captured[0]["temperature"], 1.0)
        self.assertEqual(captured[0]["top_p"], 0.95)
        self.assertEqual(captured[0]["top_k"], 20)
        self.assertEqual(captured[0]["min_p"], 0.0)
        self.assertEqual(captured[0]["presence_penalty"], 0.0)
        self.assertEqual(captured[0]["frequency_penalty"], 0.0)
        self.assertEqual(captured[0]["repeat_penalty"], 1.0)
        self.assertEqual(captured[0]["chat_template_kwargs"], {"enable_thinking": True, "preserve_thinking": True})
        self.assertEqual(captured[3]["temperature"], 0.7)
        self.assertEqual(captured[3]["top_p"], 0.8)
        self.assertEqual(captured[3]["presence_penalty"], 1.5)
        self.assertEqual(captured[3]["chat_template_kwargs"], {"enable_thinking": False, "preserve_thinking": False})


if __name__ == "__main__":
    unittest.main()
