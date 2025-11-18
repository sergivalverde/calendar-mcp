# 🚀 How to Add Calendar MCP to Claude Desktop

## Quick Steps

### 1. Open Claude Desktop Configuration

```bash
open ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

If the file doesn't exist, create it:
```bash
mkdir -p ~/Library/Application\ Support/Claude
touch ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

### 2. Add This Configuration

Copy and paste this **exact configuration**:

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

**Important Notes**:
- ✅ Uses `arch -arm64` to force ARM64 mode (required on Apple Silicon)
- ✅ Uses absolute path to the virtual environment Python
- ✅ No `cwd` parameter needed

### 3. Save the File

Save and close the editor.

### 4. Restart Claude Desktop

**Important**: You MUST fully quit Claude Desktop:

1. Press **Cmd+Q** (don't just close the window!)
2. Wait **10 seconds**
3. Reopen Claude Desktop

### 5. Verify It's Working

In Claude, you should see the Calendar MCP connected. Try asking:

```
Analyze my calendar for last week
```

---

## Detailed Instructions

### Option A: Using Terminal Editor (nano)

```bash
# Open config in nano
nano ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Paste the configuration above
# Press Ctrl+X, then Y, then Enter to save
```

### Option B: Using VS Code

```bash
# Open config in VS Code
code ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Paste the configuration above
# Save with Cmd+S
```

### Option C: Using TextEdit

```bash
# Open config in TextEdit
open -a TextEdit ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Paste the configuration above
# Save with Cmd+S
```

---

## Complete Configuration Example

If you already have other MCPs configured, add `calendar-mcp` to your existing config:

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
    },
    "other-mcp": {
      "command": "...",
      "args": ["..."]
    }
  }
}
```

---

## Before You Start

### ⚠️ CRITICAL: Update Your Calendar Cache First!

Claude **cannot** access your calendar directly. You must cache the data first:

```bash
cd /Users/s/dev/calendar-mcp
./update_calendar_cache.sh
```

Expected output:
```
✅ Successfully cached X events
   Date range: 2024-10-18 to 2024-12-17
```

If you see errors, you need to grant Terminal calendar permissions:
1. System Settings → Privacy & Security → Calendars
2. Enable **Terminal**
3. Restart Terminal
4. Try again

---

## Troubleshooting

### Problem: Claude doesn't show calendar-mcp

**Solution 1**: Check the config file format
```bash
# Validate JSON syntax
cat ~/Library/Application\ Support/Claude/claude_desktop_config.json | python -m json.tool
```

If you see errors, your JSON is malformed. Fix the syntax.

**Solution 2**: Check the Python path
```bash
# Verify the path exists
ls -la /Users/s/dev/calendar-mcp/.venv/bin/python
```

If the file doesn't exist:
```bash
cd /Users/s/dev/calendar-mcp
uv sync
```

**Solution 3**: Fully restart Claude
- Press **Cmd+Q** (not just close window!)
- Wait 10 seconds
- Reopen Claude

### Problem: "No events found" when querying

**Solution**: Update the cache first!
```bash
cd /Users/s/dev/calendar-mcp
./update_calendar_cache.sh
```

See [CACHE_SOLUTION.md](CACHE_SOLUTION.md) for details.

### Problem: ModuleNotFoundError or import errors

**Solution**: Reinstall dependencies
```bash
cd /Users/s/dev/calendar-mcp
uv sync --reinstall
```

Then restart Claude.

### Problem: Architecture mismatch errors

**Solution**: The config already uses `arch -arm64`. If you still see issues:
```bash
# Check your Mac's architecture
uname -m
# Should show: arm64
```

If it shows `x86_64`, your terminal is running in Rosetta mode. Start a native ARM64 terminal.

### Check Claude Logs

To see detailed error messages:
```bash
# View logs in real-time
tail -f ~/Library/Logs/Claude/mcp*.log

# Or view recent logs
ls -lt ~/Library/Logs/Claude/ | head -10
cat ~/Library/Logs/Claude/mcp-server-calendar-mcp.log
```

---

## Verify Everything is Working

### Quick Test Checklist

1. ✅ **Config file exists**:
   ```bash
   cat ~/Library/Application\ Support/Claude/claude_desktop_config.json
   ```

2. ✅ **Cache is created**:
   ```bash
   ls -lh ~/.calendar-mcp-cache/calendar_events.json
   ```

3. ✅ **Python path is correct**:
   ```bash
   /Users/s/dev/calendar-mcp/.venv/bin/python --version
   ```

4. ✅ **MCP server starts**:
   ```bash
   timeout 5 /Users/s/dev/calendar-mcp/.venv/bin/python -m calendar_mcp.server
   # Should start without errors (timeout is expected)
   ```

5. ✅ **Claude Desktop restarted**:
   - Quit with Cmd+Q
   - Wait 10 seconds
   - Reopen

6. ✅ **Ask Claude**:
   ```
   Analyze my calendar for last week
   ```

---

## Full System Check

Run the verification script:
```bash
cd /Users/s/dev/calendar-mcp
./verify_setup.sh
```

This checks everything and tells you exactly what needs fixing.

---

## What Claude Can Do

Once configured, ask Claude:

### Calendar Analysis
```
Analyze my calendar for last week
Show time distribution for November
What were my energy levels yesterday?
```

### Time Tracking
```
How much time did I spend on meetings this month?
Compare my deep work time this week vs last week
Show my busiest days in October
```

### Insights
```
What categories take up most of my time?
When am I most productive?
Analyze my meeting load
```

---

## Configuration File Location Reference

| OS | Config Path |
|----|-------------|
| **macOS** | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Windows | `%APPDATA%\Claude\claude_desktop_config.json` |
| Linux | `~/.config/Claude/claude_desktop_config.json` |

---

## Next Steps

1. ✅ **Add config** (copy the JSON above)
2. ✅ **Update cache**: `./update_calendar_cache.sh`
3. ✅ **Restart Claude** (Cmd+Q, wait, reopen)
4. ✅ **Test**: Ask "Analyze my calendar for last week"

---

## See Also

- **[QUICK_START.md](QUICK_START.md)** - Complete setup guide
- **[CACHE_SOLUTION.md](CACHE_SOLUTION.md)** - Why the cache is needed
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Fix common issues
- **[START_HERE.md](START_HERE.md)** - Overview

---

## Summary

```bash
# 1. Add config (copy JSON from above)
nano ~/Library/Application\ Support/Claude/claude_desktop_config.json

# 2. Update cache
cd /Users/s/dev/calendar-mcp && ./update_calendar_cache.sh

# 3. Restart Claude (Cmd+Q, wait, reopen)

# 4. Test with Claude: "Analyze my calendar for last week"
```

🎉 **That's it! Your Calendar MCP is now connected to Claude!**






