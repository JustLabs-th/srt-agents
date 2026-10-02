"""Compare flat and namespaced tool calls against the configured local provider."""

import json
from pathlib import Path
import tomllib
import urllib.request

from local_codex import prepare_runtime


def main():
    _, env = prepare_runtime()
    repo = Path(__file__).resolve().parents[2]
    config = tomllib.loads((repo / "company/llama-cpp.config.toml").read_text())
    provider = config["model_providers"][config["model_provider"]]
    function = {"type": "function", "name": "baseline_ping",
                "description": "Return a baseline ping marker",
                "parameters": {"type": "object", "properties": {}, "required": []}}
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    for kind in ("flat", "namespace"):
        tools = [function] if kind == "flat" else [{"type": "namespace",
            "name": "baseline", "description": "Baseline checks", "tools": [function]}]
        body = {"model": config["model"], "stream": False, "max_output_tokens": 256,
                "tools": tools, "tool_choice": "required",
                "input": "Call baseline_ping now, with no arguments. Do not answer in text."}
        request = urllib.request.Request(provider["base_url"].rstrip("/") + "/responses",
            data=json.dumps(body).encode(), headers={"Content-Type": "application/json",
                "Authorization": "Bearer " + env["LLAMA_API_KEY"]})
        try:
            with opener.open(request, timeout=60) as response:
                result = json.load(response)
            calls = [{k: item[k] for k in ("type", "name", "namespace") if k in item}
                     for item in result.get("output", []) if item.get("type") == "function_call"]
            print(json.dumps({"kind": kind, "function_calls": calls,
                              "status": result.get("status")}), flush=True)
        except urllib.error.HTTPError as error:
            print(json.dumps({"kind": kind, "http_status": error.code}), flush=True)

    content = [{"type": "input_text", "text": "Reply exactly ITEM_OK"}]
    for kind, item in (
        ("standard_message", {"type": "message", "role": "user", "content": content}),
        ("agent_message", {"type": "agent_message", "author": "/root",
                           "recipient": "/root/baseline_check", "content": content}),
    ):
        body = {"model": config["model"], "stream": False,
                "max_output_tokens": 32, "input": [item]}
        request = urllib.request.Request(provider["base_url"].rstrip("/") + "/responses",
            data=json.dumps(body).encode(), headers={"Content-Type": "application/json",
                "Authorization": "Bearer " + env["LLAMA_API_KEY"]})
        try:
            with opener.open(request, timeout=60) as response:
                result = json.load(response)
            print(json.dumps({"kind": kind, "status": result.get("status")}), flush=True)
        except urllib.error.HTTPError as error:
            print(json.dumps({"kind": kind, "http_status": error.code}), flush=True)


if __name__ == "__main__":
    main()
