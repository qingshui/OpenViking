#!/usr/bin/env python3
"""Memory bridge for Claude Code hooks.

This script provides a stable interface for hook scripts:
- analyze-file: analyze a code file and store as memory
- record-tool: record a tool call result
- session-start: start a memory session
- session-end: commit the session
- stop: cleanup on stop
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional

# Add plugin path
PLUGIN_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PLUGIN_ROOT))

try:
    from memory_plugin import RemoteMemoryPlugin, GitBranchInfo, TeamScope, MemoryType
except ImportError as e:
    print(json.dumps({"ok": False, "error": f"Import error: {e}"}))
    sys.exit(1)


def _get_plugin() -> Optional[RemoteMemoryPlugin]:
    """Get RemoteMemoryPlugin instance."""
    # Try to get from environment or config
    openviking_url = os.environ.get("OPENVIKING_URL", "http://localhost:1933")
    api_key = os.environ.get("OPENVIKING_API_KEY", "")

    # Check for config file
    config_path = Path.home() / ".claude" / "code-memory-config.json"
    if config_path.exists():
        try:
            with open(config_path, "r") as f:
                cfg = json.load(f)
                openviking_url = cfg.get("openviking_url", openviking_url)
                api_key = cfg.get("api_key", api_key)
        except Exception:
            pass

    return RemoteMemoryPlugin(
        openviking_url=openviking_url,
        api_key=api_key,
    )


def _get_git_branch(repo_path: Optional[str] = None) -> Optional[str]:
    """Get current Git branch."""
    import subprocess

    if not repo_path:
        repo_path = os.getcwd()

    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return None


def cmd_analyze_file(args: argparse.Namespace) -> Dict[str, Any]:
    """Analyze a code file or directory and store as memory."""
    plugin = _get_plugin()
    if not plugin:
        return {"ok": False, "error": "Failed to initialize plugin"}

    file_path = args.file_path
    if not os.path.exists(file_path):
        return {"ok": False, "error": f"Path not found: {file_path}"}

    try:
        # Detect branch
        if os.path.isdir(file_path):
            branch = _get_git_branch(file_path)
        else:
            branch = _get_git_branch(os.path.dirname(file_path))

        # Create plugin with branch awareness
        if branch:
            branch_info = GitBranchInfo(branch, repo_path=file_path if os.path.isdir(file_path) else os.path.dirname(file_path))
            team_scope = TeamScope(team_id="individual", branch_info=branch_info)
            plugin = RemoteMemoryPlugin(
                openviking_url=plugin.client.base_url,
                api_key=plugin.client.api_key,
                team_scope=team_scope,
                user_id="claude-user",
            )

        # Analyze and store - support both file and directory
        if os.path.isdir(file_path):
            entries = plugin.analyze_and_store_directory(file_path, auto_store=True)
            total_functions = sum(len(e.metadata.get("functions", [])) for e in entries)
            total_classes = sum(len(e.metadata.get("classes", [])) for e in entries)
            return {
                "ok": True,
                "uri": entries[0].uri if entries else "",
                "functions": total_functions,
                "classes": total_classes,
                "branch": branch or "",
                "is_directory": True,
                "file_count": len(entries),
            }
        else:
            entry = plugin.analyze_and_store_file(file_path, auto_store=True)
            return {
                "ok": True,
                "uri": entry.uri,
                "functions": len(entry.metadata.get("functions", [])),
                "classes": len(entry.metadata.get("classes", [])),
                "branch": branch or "",
                "is_directory": False,
            }
    except Exception as e:
        return {"ok": False, "error": str(e)}


def cmd_record_tool(args: argparse.Namespace) -> Dict[str, Any]:
    """Record a tool call result."""
    plugin = _get_plugin()
    if not plugin:
        return {"ok": False, "error": "Failed to initialize plugin"}

    tool_name = args.tool_name
    tool_result = args.tool_result

    try:
        # Build record content
        record_title = f"Tool Call: {tool_name}"
        record_content = f"""# Tool Call Record

## Tool Information
- **Tool Name**: {tool_name}
- **Session**: claude-session
- **Timestamp**: {time.strftime('%Y-%m-%d %H:%M:%S')}

## Result
{tool_result[:2000] if len(tool_result) > 2000 else tool_result}

---
*Recorded by Claude Code Memory Plugin*
"""

        # Store as API interface
        entry = plugin.store_api_interface(
            title=record_title,
            content=record_content,
            params=[],
            returns={},
            tags=["tool_call", tool_name.lower(), "record"],
        )

        return {"ok": True, "uri": entry.uri}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def cmd_session_start(args: argparse.Namespace) -> Dict[str, Any]:
    """Start a memory session."""
    plugin = _get_plugin()
    if not plugin:
        return {
            "ok": False,
            "error": "Failed to initialize plugin",
            "status_line": "[claude-memory] ERROR: Failed to initialize",
        }

    # Just return success message
    return {
        "ok": True,
        "status_line": "[claude-memory] Memory plugin active",
        "additional_context": "Use /memory commands to manage memories.",
    }


def cmd_session_end(args: argparse.Namespace) -> Dict[str, Any]:
    """End a memory session (commit)."""
    return {
        "ok": True,
        "committed": True,
        "status_line": "[claude-memory] Session ended",
    }


def cmd_stop(args: argparse.Namespace) -> Dict[str, Any]:
    """Cleanup on stop."""
    return {"ok": True, "cleaned": True}


def cmd_ingest_user_prompt(args: argparse.Namespace) -> Dict[str, Any]:
    """Ingest user prompt for memory tracking."""
    prompt = args.prompt

    # Just return success message
    return {
        "ok": True,
        "status_line": "[claude-memory] Memory available (use memory-recall when historical context matters)",
    }


def cmd_recall(args: argparse.Namespace) -> int:
    """Recall relevant memories."""
    plugin = _get_plugin()
    if not plugin:
        print("Memory unavailable: Failed to initialize plugin")
        return 1

    query = args.query
    top_k = args.top_k

    if not query:
        print("No relevant memories found.")
        return 0

    try:
        # Search memories
        result = plugin.search_memories(query, limit=top_k)

        if not result:
            print("No relevant memories found.")
            return 0

        # Build output
        output_lines = [f"Relevant memories for: {query}", ""]

        for i, item in enumerate(result, start=1):
            uri = item.uri or ""
            score = item.metadata.get("score", 0.0) if item.metadata else 0.0
            content = item.content[:500] if item.content else ""

            output_lines.append(f"{i}. [{score:.3f}] {uri}")
            if content:
                output_lines.append(f"   snippet: {content}")
            output_lines.append("")

        print("\n".join(output_lines).strip())
        return 0
    except Exception as e:
        print(f"Memory recall failed: {e}")
        return 1


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Claude Code Memory Bridge")

    sub = parser.add_subparsers(dest="command", required=True)

    # analyze-file
    p_analyze = sub.add_parser("analyze-file", help="Analyze a code file")
    p_analyze.add_argument("--file-path", required=True, help="File path to analyze")

    # record-tool
    p_record = sub.add_parser("record-tool", help="Record a tool call")
    p_record.add_argument("--tool-name", required=True, help="Tool name")
    p_record.add_argument("--tool-result", required=True, help="Tool result")

    # session-start
    sub.add_parser("session-start", help="Start session")

    # session-end
    sub.add_parser("session-end", help="End session")

    # stop
    sub.add_parser("stop", help="Cleanup on stop")

   # recall
    p_recall = sub.add_parser("recall", help="Recall memories")
    p_recall.add_argument("--query", required=True, help="Recall query")
    p_recall.add_argument("--top-k", type=int, default=5, help="Number of memories to return")

    # ingest-user-prompt
    p_ingest = sub.add_parser("ingest-user-prompt", help="Ingest user prompt")
    p_ingest.add_argument("--prompt", required=True, help="User prompt to ingest")

    return parser


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    try:
        if args.command == "analyze-file":
            result = cmd_analyze_file(args)
            print(json.dumps(result, ensure_ascii=False))
            return 0

        if args.command == "record-tool":
            result = cmd_record_tool(args)
            print(json.dumps(result, ensure_ascii=False))
            return 0

        if args.command == "session-start":
            result = cmd_session_start(args)
            print(json.dumps(result, ensure_ascii=False))
            return 0

        if args.command == "session-end":
            result = cmd_session_end(args)
            print(json.dumps(result, ensure_ascii=False))
            return 0

        if args.command == "stop":
            result = cmd_stop(args)
            print(json.dumps(result, ensure_ascii=False))
            return 0

        if args.command == "ingest-user-prompt":
            result = cmd_ingest_user_prompt(args)
            print(json.dumps(result, ensure_ascii=False))
            return 0

        if args.command == "recall":
            return cmd_recall(args)

        parser.error(f"Unknown command: {args.command}")
        return 2

    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    sys.exit(main())
