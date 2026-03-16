---
description: Memory plugin - automatic memory storage when reading code files
allowed-tools: [Read, Write, Edit, Exec, Search, Message, WebFetch, Bash]
---

# Memory Plugin - Automatic Memory Storage

The Memory Plugin automatically stores memories to the remote OpenViking service when you use Claude Code tools.

## Automatic Memory Storage

### When Reading Code Files

When you use the `Read` command to read code files, the plugin automatically:

1. **Analyzes the code** - Extracts functions, classes, and imports
2. **Stores as memory** - Saves the analysis to OpenViking
3. **Shows feedback** - Displays confirmation message

**Example**:
```
Read openviking/core/context.py

✅ 已自动存储代码记忆 (main 分支):
📁 viking://resources/memories/code_file/main/contextpy
📊 函数：9, 类：2
```

### When Using Tools

When you use tools like `Write`, `Edit`, `Exec`, etc., the plugin automatically records the tool calls.

**Example**:
```
✅ 已记录工具调用：Write
📁 viking://resources/api_interface/api_interfacewrite
```

### Session Management

- **Session Start**: When a new session begins, the plugin initializes memory tracking
- **Session End**: When the session ends, all memories are committed

## Memory Types

The plugin automatically stores the following types of memories:

| Type | Trigger | Description |
|------|---------|-------------|
| CODE_FILE | Read command | Code file analysis (functions, classes, imports) |
| CODE_MODULE | Directory analysis | Module/package overview |
| API_INTERFACE | Tool calls | Tool call records |
| SESSION | Session start/end | Session context tracking |

## Configuration

The plugin reads configuration from `~/.claude/code-memory-config.json`:

```json
{
  "openviking_url": "http://localhost:1933",
  "api_key": "",
  "search_limit": 5,
  "install_dir": "/root/.claude/claude-code-memory-plugin"
}
```

## Python API Usage

For advanced usage, you can use the Python API directly:

```python
from memory_plugin import RemoteMemoryPlugin

plugin = RemoteMemoryPlugin(
    openviking_url="http://localhost:1933",
    api_key="your-api-key",
    user_id="claude-user"
)

# Store user email
plugin.store_email("qshuihu@gmail.com", description="User email")

# Store phone number
plugin.store_phone("+86-138-0013-8000")

# Store address
plugin.store_address("北京市海淀区中关村大街 1 号")

# Get user info
entry = plugin.get_user_info("email")
```

## User Information Storage

You can store personal information using the Python API:

```python
# Email
plugin.store_email("your@email.com")

# Phone
plugin.store_phone("+1234567890")

# Address
plugin.store_address("Your Address")
```

## Notes

- All memories are automatically stored to the remote OpenViking service
- No manual commands needed - just use Claude Code normally
- Memories are stored with branch information for multi-branch projects
- User information is stored in `viking://resources/memories/user_info/`
