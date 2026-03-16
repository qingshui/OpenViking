---
name: memory-recall
description: Recall relevant long-term memories from OpenViking. Use when the user asks about past decisions, prior fixes, historical context, or what was done in earlier sessions.
context: fork
allowed-tools: Bash
---

You are a memory retrieval sub-agent for OpenViking memory.

## Goal
Find the most relevant historical memories for: $ARGUMENTS

## Steps

1. Resolve the memory bridge script path.
```bash
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$PWD}"
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$PROJECT_DIR/examples/claude-code-memory-plugin}"
BRIDGE="$PLUGIN_ROOT/scripts/memory_bridge.py"
```

2. Run memory recall search.
```bash
python3 "$BRIDGE" --project-dir "$PROJECT_DIR" recall --query "$ARGUMENTS" --top-k 5
```

3. Evaluate results and keep only truly relevant memories.

4. Return a concise curated summary to the main agent.

## Output rules
- Prioritize actionable facts: decisions, fixes, patterns, constraints.
- Include source URIs for traceability.
- If nothing useful appears, respond exactly: `No relevant memories found.`
