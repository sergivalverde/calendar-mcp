# ✅ Calendar MCP - Working Solution

## Problem Solved

The Calendar MCP is now fully working with `uv` on ARM64 Mac (Apple Silicon).

### The Issue

The problem was a Python architecture mismatch - when running scripts, Python was defaulting to x86_64 (Rosetta) mode while the compiled dependencies (rpds-py) were built for ARM64.

### The Solution

Use `arch -arm64` to force native ARM64 execution.

## Working Configuration

### Step 1: Install Dependencies

```bash
cd /Users/s/dev/calendar-mcp
uv sync
```

### Step 2: Test Installation

```bash
# Run tests
uv run python test_calendar_analysis.py

# Should show: ✅ All tests passed!
```

### Step 3: Configure Claude Desktop

Edit: `~/Library/Application Support/Claude/claude_desktop_config.json`

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

### Step 4: Restart Claude Desktop

Completely quit and reopen Claude Desktop.

### Step 5: Test

Ask Claude:
```
Analyze my calendar for last week
```

## Verification Commands

### Test MCP imports work:
```bash
cd /Users/s/dev/calendar-mcp
.venv/bin/python -c "from calendar_mcp.server import main; print('✅ Works')"
```

### Test server starts:
```bash
arch -arm64 .venv/bin/python -m calendar_mcp.server
# Should start and wait for input (press Ctrl+C to stop)
```

### Test full system:
```bash
uv run python test_calendar_analysis.py
# Should show all tests passing
```

## Key Technical Details

1. **MCP API**: Updated to use `@server.list_tools()` and `@server.call_tool()` decorators
2. **Architecture**: Forces ARM64 execution with `arch -arm64`
3. **Dependencies**: All installed correctly via `uv sync`
4. **Python Version**: 3.11 (required for MCP >=1.0)

## Files Modified

- `src/calendar_mcp/server.py` - Updated MCP API usage
- `pyproject.toml` - Set Python >=3.10 requirement
- `claude_desktop_config.json` - Working configuration

## What Was Fixed

1. ✅ Updated MCP server implementation to use correct API
2. ✅ Fixed import structure (CalendarAnalysisConfig moved to config.py)  
3. ✅ Resolved ARM64/x86_64 architecture conflict
4. ✅ All tests pass
5. ✅ Server starts correctly
6. ✅ Works with Claude Desktop

## Alternative Configurations

If the arch command doesn't work, try:

```json
{
  "mcpServers": {
    "calendar-mcp": {
      "command": "/usr/bin/arch",
      "args": [
        "-arm64",
        "/Users/s/dev/calendar-mcp/.venv/bin/python3",
        "-m",
        "calendar_mcp.server"
      ]
    }
  }
}
```

## Troubleshooting

### Issue: "No events found" or "No calendars accessible"

**This is the most common issue!**

icalBuddy needs calendar permissions. Fix it:

```bash
# 1. Test if icalBuddy has access
icalBuddy calendars

# If you see "error: No calendars" - you need to grant permissions
```

**Solution**:
1. Open System Settings → Privacy & Security → Calendars
2. Enable access for:
   - Terminal (if testing from terminal)
   - Claude (if using Claude Desktop)
   - Your IDE (if running from VS Code/Cursor)
3. Restart the application completely
4. Test again: `icalBuddy calendars`

**Detailed guide**: See [CALENDAR_PERMISSIONS.md](./CALENDAR_PERMISSIONS.md)

**Quick diagnostic**: Run `uv run python diagnose_calendar.py`

### Issue: "arch: command not found"
Use full path: `/usr/bin/arch`

### Issue: "No module named 'mcp'"
Run: `uv sync` to reinstall dependencies

### Issue: Architecture errors
Ensure you're using `arch -arm64` prefix

### Issue: icalBuddy not found
Install: `brew install ical-buddy`

## Success Indicators

✅ `uv run python test_calendar_analysis.py` passes
✅ Server starts without import errors
✅ Claude Desktop shows MCP tool available
✅ Calendar queries return formatted reports

## Next Steps

1. Customize `src/calendar_mcp/config.json` for your needs
2. Set team domains, exclusion patterns, etc.
3. Ask Claude calendar questions!

## Example Queries

```
Analyze my calendar for last week
Show time distribution for November
What were my energy levels yesterday?
How much time did I spend in meetings this month?
Show my most productive days
```
