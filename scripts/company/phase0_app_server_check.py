"""Verification client for native app-server; not a company orchestration layer.

Run from the Windows host account with a host-owned disposable workspace.
Answers and declines are synthetic test inputs, not company user/admin decisions.
"""

import argparse
import json
import os
from pathlib import Path
import queue
import subprocess
import threading
import time

from local_codex import prepare_runtime


class CheckClient:
    def __init__(self, cwd, accepted_commands=()):
        binary, env = prepare_runtime()
        env["GIT_AUTHOR_NAME"] = env["GIT_COMMITTER_NAME"] = "Baseline Verification"
        env["GIT_AUTHOR_EMAIL"] = env["GIT_COMMITTER_EMAIL"] = "baseline@example.invalid"
        self.cwd = cwd
        self.accepted_commands = set(accepted_commands)
        self.accepts = 0
        self.secret = env.get("LLAMA_API_KEY", "")
        self.process = subprocess.Popen(
            [str(binary), "app-server", "--stdio"],
            cwd=cwd, env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL, text=True, encoding="utf-8",
        )
        self.messages = queue.Queue()
        self.events = []
        self.next_id = 0
        self.answers = 0
        self.declines = 0
        self.resolved = 0
        self.active_thread = None
        threading.Thread(target=self.read, daemon=True).start()

    def read(self):
        for line in self.process.stdout:
            try:
                self.messages.put(json.loads(line))
            except ValueError:
                continue
        self.messages.put(None)

    def send(self, value):
        self.process.stdin.write(json.dumps(value) + "\n")
        self.process.stdin.flush()

    def record(self, value):
        clean = json.loads(json.dumps(value).replace(self.secret, "<REDACTED>"))
        self.events.append(clean)
        print(json.dumps(clean), flush=True)

    def receive(self, deadline):
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError("app-server scenario timed out")
        message = self.messages.get(timeout=remaining)
        if message is None:
            raise RuntimeError("app-server closed stdout")
        method = message.get("method", "")
        params = message.get("params", {})
        if "id" in message and method:
            if method == "item/tool/requestUserInput":
                assert params["threadId"] == self.active_thread
                questions = params["questions"]
                assert len(questions) == 1 and questions[0]["id"] == "calc_policy"
                assert any(o["label"] == "Subtract" for o in questions[0]["options"])
                self.record({"event": "synthetic_answer", "threadId": params["threadId"],
                             "turnId": params["turnId"], "answer": "Subtract",
                             "isBlocking": params.get("isBlocking")})
                self.send({"id": message["id"], "result": {
                    "answers": {"calc_policy": {"answers": ["Subtract"]}}}})
                self.answers += 1
            elif method == "item/commandExecution/requestApproval":
                assert params["threadId"] == self.active_thread
                command = params.get("command", "")
                # Accept only an exact literal command in the expected PowerShell wrapper.
                # Parsed commandActions alone are best-effort and cannot authorize execution.
                shell = str(Path(os.environ["SystemRoot"]) / "System32/WindowsPowerShell/v1.0/powershell.exe")
                normalized = command.replace("\\\\", "\\")
                expected = {f'"{shell}" -Command {quote}{cmd}{quote}'
                            for cmd in self.accepted_commands for quote in ("'", '"')}
                accepted = (Path(params.get("cwd", "")).resolve() == self.cwd
                            and normalized.casefold() in {c.casefold() for c in expected})
                decision = "accept" if accepted else "decline"
                self.record({"event": "synthetic_" + decision, "threadId": params["threadId"],
                             "turnId": params["turnId"]})
                self.send({"id": message["id"], "result": {"decision": decision}})
                self.accepts += int(accepted)
                self.declines += int(not accepted)
            else:
                self.send({"id": message["id"], "error": {
                    "code": -32601, "message": "Unsupported verification request"}})
                raise RuntimeError(f"Unexpected server request: {method}")
        if method == "serverRequest/resolved":
            self.resolved += 1
            self.record({"event": "request_resolved", "threadId": params["threadId"]})
        if method == "item/completed":
            item = params["item"]
            if item["type"] in ("agentMessage", "commandExecution", "collabAgentToolCall"):
                self.record({"event": "item_completed", "threadId": params["threadId"],
                             "item": item})
        if method == "turn/completed":
            self.record({"event": "turn_completed", "threadId": params["threadId"],
                         "turn": params["turn"]})
        return message

    def call(self, method, params):
        self.next_id += 1
        request_id = self.next_id
        self.send({"id": request_id, "method": method, "params": params})
        deadline = time.monotonic() + 60
        while True:
            result = self.receive(deadline)
            if result.get("id") == request_id and "method" not in result:
                if "error" in result:
                    raise RuntimeError(str(result["error"]))
                return result["result"]

    def turn(self, thread_id, prompt, collaboration=None):
        self.active_thread = thread_id
        start = len(self.events)
        params = {"threadId": thread_id, "input": [{"type": "text", "text": prompt}]}
        if collaboration:
            params["collaborationMode"] = collaboration
        turn_id = self.call("turn/start", params)["turn"]["id"]
        deadline = time.monotonic() + 240
        while True:
            message = self.receive(deadline)
            if (message.get("method") == "turn/completed"
                    and message["params"]["threadId"] == thread_id
                    and message["params"]["turn"]["id"] == turn_id):
                assert message["params"]["turn"]["status"] == "completed"
                return self.events[start:]

    def close(self):
        self.process.stdin.close()
        try:
            self.process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            self.process.terminate()
            self.process.wait(timeout=10)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("scenario", choices=["human", "approval", "approval-accept", "subagent", "git"])
    parser.add_argument("--cwd", type=Path, required=True)
    args = parser.parse_args()
    cwd = args.cwd.resolve(strict=True)
    assert cwd.name.startswith("srt-agents-phase0-"), "Disposable Phase 0 fixture required"
    git_commands = ["git switch -c phase0/local-fix", "git add -- calculator.py",
                    "git commit -m phase0-local-calculator-fix"]
    accepted_commands = (git_commands if args.scenario == "git" else
                         ["Write-Output PHASE0_APPROVAL_OK"] if args.scenario == "approval-accept" else [])
    if args.scenario == "git":
        previous = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=cwd, text=True).strip()
        assert subprocess.check_output(["git", "diff", "--name-only"], cwd=cwd, text=True).strip() == "calculator.py"
        assert not subprocess.check_output(["git", "diff", "--cached", "--name-only"], cwd=cwd, text=True).strip()
    client = CheckClient(cwd, accepted_commands)
    try:
        client.call("initialize", {"clientInfo": {"name": "phase0_check", "version": "0.1"},
                                   "capabilities": {"experimentalApi": True}})
        client.send({"method": "initialized", "params": {}})
        config = {"features.multi_agent_v2.enabled": False,
                  "features.multi_agent": True,
                  "features.flat_multi_agent_tools": True} if args.scenario == "subagent" else {}
        start = client.call("thread/start", {"cwd": str(cwd), "sandbox": "read-only",
            "approvalPolicy": "on-request", "approvalsReviewer": "user", "config": config})
        thread_id = start["thread"]["id"]
        client.record({"event": "thread_started", "threadId": thread_id, "scenario": args.scenario})
        if args.scenario == "human":
            mode = {"mode": "plan", "settings": {"model": start["model"],
                     "reasoning_effort": None, "developer_instructions": None}}
            events = client.turn(thread_id,
                "This is a native user-input smoke test, not a coding task. Do not use shell or "
                "modify files. Call request_user_input exactly once with one question id "
                "calc_policy, header Policy, question 'Choose the calculator policy', and options "
                "labeled exactly Add and Subtract (each with a description). Wait for the answer, "
                "then state the selected label. Do not assume an answer.", mode)
            assert client.answers == 1 and client.resolved >= 1
            assert any(e.get("item", {}).get("type") == "agentMessage"
                       and "Subtract" in e["item"].get("text", "") for e in events)
            followup = client.turn(thread_id,
                "Without tools or another question, state the calculator policy selected on "
                "the previous turn. Do not modify anything.")
            assert any("Subtract" in e.get("item", {}).get("text", "") for e in followup)
        elif args.scenario in ("approval", "approval-accept"):
            events = client.turn(thread_id,
                "Native approval smoke test. Call exec_command exactly once with command "
                "Write-Output PHASE0_APPROVAL_OK, sandbox_permissions require_escalated, and "
                "justification 'Phase 0 approval round-trip test'. This is harmless output only. "
                "After the approval response, report the result and stop; do not retry or use "
                "alternative tools, create files, or change permissions.")
            commands = [e["item"] for e in events if e.get("item", {}).get("type") == "commandExecution"]
            assert len(commands) == 1 and client.resolved >= 1
            if args.scenario == "approval":
                assert client.declines == 1 and commands[0]["status"] == "declined"
                assert not commands[0].get("aggregatedOutput") and commands[0].get("exitCode") is None
            else:
                assert client.accepts == 1 and client.declines == 0
                assert commands[0]["exitCode"] == 0
                assert "PHASE0_APPROVAL_OK" in commands[0]["aggregatedOutput"]
        elif args.scenario == "git":
            client.turn(thread_id,
                "Native Git workflow smoke test in this disposable fixture. Inspect git diff first. "
                "Do not edit any files. Then call exec_command for each of these EXACT commands, "
                "in order, one command per call, with sandbox_permissions require_escalated and "
                "justification 'Phase 0 fixture Git workflow': " + "; then ".join(git_commands) +
                ". Do not append any other shell command to those calls. Stop if any is denied or "
                "fails. After commit, show the commit hash. Do not push, use network, change "
                "configuration, or touch any other repository.")
            assert client.accepts == 3 and client.declines == 0
            result = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=cwd, text=True).strip()
            assert result != previous
            assert subprocess.check_output(["git", "branch", "--show-current"], cwd=cwd, text=True).strip() == "phase0/local-fix"
            assert subprocess.check_output(["git", "show", "--format=", "--name-only", "HEAD"], cwd=cwd, text=True).strip() == "calculator.py"
            assert not subprocess.check_output(["git", "diff", "--name-only", "HEAD"], cwd=cwd, text=True).strip()
            client.record({"event": "fixture_commit", "commit": result, "previous": previous})
        else:
            events = client.turn(thread_id,
                "Native V1 sub-agent smoke test. Explicitly call spawn_agent once with message "
                "'Reply exactly CHILD_BASELINE_OK; do not use tools or modify files', and "
                "fork_context false. Do not override its model. Wait for "
                "the child to finish using native collaboration tools, then report its exact "
                "reply. Do not use shell, modify files, or spawn further agents.")
            collab = [e["item"] for e in events if e.get("item", {}).get("type") == "collabAgentToolCall"]
            assert collab, "Missing native parent/child linkage"
            assert any(c["tool"] == "spawnAgent" and c["status"] == "completed"
                       and c["senderThreadId"] == thread_id and len(c["receiverThreadIds"]) == 1 for c in collab)
            assert any(s["status"] == "completed" and s.get("message") == "CHILD_BASELINE_OK"
                       for c in collab for s in c.get("agentsStates", {}).values())
            assert any("CHILD_BASELINE_OK" in e.get("item", {}).get("text", "") for e in events)
        client.record({"event": "scenario_passed", "scenario": args.scenario, "threadId": thread_id})
    finally:
        client.close()


if __name__ == "__main__":
    main()
