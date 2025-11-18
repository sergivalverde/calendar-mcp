# Claude Desktop Setup for Calendar MCP

## The Working Configuration (ARM64 Mac)

Add this to your Claude Desktop configuration file:

**File**: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "calendar-mcp": {
      "command": "arch",
      "args": [
        "-arm64",
        "/Users/s/dev/calendar-mcp/.venv/bin/python",
        "-m",
        "calendar_mcp.server"
      ]
    }
  }
}
```

**Note**: The `arch -arm64` prefix is needed to ensure Python runs in native ARM64 mode on Apple Silicon Macs.

## Why This Works

This configuration uses `uv run` which:
- ✅ Automatically activates the virtual environment
- ✅ Uses the correct Python version (3.11)
- ✅ Has all dependencies already installed
- ✅ No need to set PYTHONPATH or cwd
- ✅ Works reliably every time

## Complete Configuration Example

If you have other MCP servers, your config might look like:

```json
{
  "mcpServers": {
    "calendar-mcp": {
      "command": "uv",
      "args": [
        "--directory",
        "/Users/s/dev/calendar-mcp",
        "run",
        "calendar-mcp"
      ]
    },
    "other-mcp-server": {
      "command": "other-command",
      "args": ["..."]
    }
  }
}
```

## How to Apply the Configuration

1. **Open the Claude Desktop config file**:
   ```bash
   code ~/Library/Application\ Support/Claude/claude_desktop_config.json
   ```
   
   Or using any editor:
   ```bash
   nano ~/Library/Application\ Support/Claude/claude_desktop_config.json
   ```

2. **Add the calendar-mcp configuration** (shown above)

3. **Restart Claude Desktop** completely (Quit and reopen)

4. **Verify it's working**:
   - Open Claude Desktop
   - Look for a hammer/tools icon or MCP indicator
   - Ask: "What MCP tools are available?"
   - You should see the calendar-mcp server listed

## Testing Before Adding to Claude

Test the configuration works:

```bash
cd /Users/s/dev/calendar-mcp
uv run calendar-mcp
```

The server should start (will wait for input - press Ctrl+C to stop).

## Usage Examples in Claude

Once configured, ask Claude questions like:

```
Analyze my calendar for last week
```

```
Show me my time distribution for November
```

```
What were my energy levels yesterday?
```

```
How many hours did I spend in team meetings this month?
```

```
Show me my most productive days based on energy levels
```

## Troubleshooting

### Server doesn't start

Check the Claude Desktop logs:
```bash
tail -f ~/Library/Logs/Claude/mcp*.log
```

### Calendar not accessible

Make sure icalBuddy works:
```bash
icalBuddy calendars
```

### Wrong calendar data

Configure which calendars to use in:
```bash
nano /Users/s/dev/calendar-mcp/src/calendar_mcp/config.json
```

## Alternative Configuration (Direct Python)

If the uv method doesn't work, use this fallback:

```json
{
  "mcpServers": {
    "calendar-mcp": {
      "command": "/Users/s/dev/calendar-mcp/.venv/bin/python",
      "args": ["-m", "calendar_mcp.server"]
    }
  }
}
```

This directly uses the virtual environment Python.

## Customizing Calendar Analysis

Edit `/Users/s/dev/calendar-mcp/src/calendar_mcp/config.json`:

```json
{
  "calendar": {
    "calendars": ["Work", "Personal"]  // Or null for all calendars
  },
  "classification": {
    "team_domains": ["yourcompany.com"],
    "excluded_titles": ["Blocked", "Busy", "Tentative"],
    // ... more customization options
  }
}
```

After editing, restart Claude Desktop to apply changes.

## Verification

Once configured, you can verify it's working by asking Claude:

```
What calendar analysis tools do you have available?
```

Claude should respond that it has access to the calendar-mcp server with the `query_calendar` tool.
