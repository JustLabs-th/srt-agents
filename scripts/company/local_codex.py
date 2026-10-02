"""Run the source-built CLI with an isolated llama.cpp configuration."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tomllib
from urllib.parse import urlsplit


def prepare_runtime():
    repo = Path(__file__).resolve().parents[2]
    config_path = repo / "company" / "llama-cpp.config.toml"
    if not config_path.is_file():
        raise RuntimeError("Create company/llama-cpp.config.toml from the example first")
    config = tomllib.loads(config_path.read_text(encoding="utf-8"))
    provider = config["model_providers"][config["model_provider"]]
    if provider.get("requires_openai_auth", True):
        raise RuntimeError("Local provider must disable OpenAI authentication")
    if provider.get("env_key") != "LLAMA_API_KEY":
        raise RuntimeError("Provider env_key must reference LLAMA_API_KEY")
    if config["model"] == "REPLACE_WITH_SERVER_MODEL_ID":
        raise RuntimeError("Set the model ID from the worker's model list first")

    task_env = os.environ.copy()
    secret_path = repo / "company" / ".env"
    if not task_env.get("LLAMA_API_KEY") and secret_path.is_file():
        for line in secret_path.read_text(encoding="utf-8").splitlines():
            name, separator, value = line.partition("=")
            if separator and name.strip() == "LLAMA_API_KEY":
                value = value.strip()
                task_env["LLAMA_API_KEY"] = (
                    json.loads(value) if value.startswith('"') else value
                )
                break
    if not task_env.get("LLAMA_API_KEY"):
        raise RuntimeError("Set LLAMA_API_KEY or provide it in ignored company/.env")

    binary = repo / "codex-rs" / "target" / "debug" / (
        "codex.exe" if os.name == "nt" else "codex"
    )
    if not binary.is_file():
        raise RuntimeError("Build codex-cli before running the local provider")
    task_home = repo / "codex-rs" / "target" / "phase0-local-home"
    task_home.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(config_path, task_home / "config.toml")
    task_env["CODEX_HOME"] = str(task_home)
    host = urlsplit(provider["base_url"]).hostname
    no_proxy = task_env.get("NO_PROXY", task_env.get("no_proxy", ""))
    entries = [entry.strip() for entry in no_proxy.split(",") if entry.strip()]
    for entry in (host, "localhost", "127.0.0.1"):
        if entry and entry not in entries:
            entries.append(entry)
    task_env["NO_PROXY"] = task_env["no_proxy"] = ",".join(entries)
    return binary, task_env


def main():
    binary, task_env = prepare_runtime()
    return subprocess.run([str(binary), *sys.argv[1:]], env=task_env).returncode


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, RuntimeError, ValueError) as error:
        print(f"Local Codex setup failed: {error}", file=sys.stderr)
        sys.exit(1)
