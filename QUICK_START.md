# 🚀 Quick Start Guide

Get your Calendar MCP working with Raycast/Claude Desktop in 5 minutes!

## Why This Works

**Smart Access**: Tries direct calendar file reading first, falls back to automatic caching if needed.

**Real-time**: Always shows current calendar data with automatic background updates.

**Event Creation**: Create events with natural language commands like "Block two mornings next week to work on the presentation".

**Permission-Aware**: Works whether you grant calendar permissions or not.

## Step-by-Step Setup

### 1. Install Prerequisites

```bash
# Install uv (Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Verify installation
uv --version
```

### 2. Install Calendar MCP

```bash
cd /Users/s/dev/calendar-mcp
uv sync
```

Wait for dependencies to install (~30 seconds).

### 3. Grant Calendar Permissions (Required)

**Calendar access requires Terminal permissions**:

1. Open **System Settings**
2. Go to **Privacy & Security → Calendars**
3. Find and enable **Terminal** (check the box)
4. **Completely restart Terminal**:
   - Press **Cmd+Q** to quit ALL Terminal windows
   - Wait **10 seconds**
   - Open a **fresh** Terminal window

**Test permissions:**
```bash
icalBuddy calendars
```
Should show your calendar names (like "• Calendar", "• Work").

**Important**: Permissions are session-specific. If icalBuddy doesn't work, restart Terminal again.

### 4. Configure Your MCP Client

#### For Claude Desktop:

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

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

Save and restart Claude Desktop (Cmd+Q, wait, reopen).

#### For Raycast:

### 5. Test Everything

Run the comprehensive test to verify everything works:

```bash
cd /Users/s/dev/calendar-mcp
python test_final_setup.py
```

This will:
- ✅ Update your calendar cache with fresh data
- ✅ Check for today's events
- ✅ Verify MCP server works

**Expected output:**
```
Cache updated: X events found
📅 Found X events for today
✅ SUCCESS: Calendar MCP is ready!
```

### 6. Configure MCP Client

Now configure your MCP client with the Calendar MCP.

### 7. Test It!

Ask your MCP client:

#### Reading Events:
```
Analyze my calendar for this week
```

#### Creating Events:
```
Block two mornings next week to work on the presentation
```

Your MCP client should respond with calendar analysis or event creation confirmation!

## 🎉 Success!

If you can analyze your calendar and create events, you're all set!

## Usage Examples

### Calendar Analysis
```
Analyze my calendar for last week
What were my energy levels yesterday?
Show time distribution for November
How much time did I spend on meetings this month?
```

### Event Creation
```
Block two mornings next week to work on the presentation
Propose a meeting with Julia in two weeks, afternoon preferred
Add 'Dentist appointment' tomorrow at 2pm for 1 hour
```

## Troubleshooting

### Problem: "No events found" in your MCP client

**Solution**: Calendar files may not be accessible. Check:
```bash
ls -la ~/Library/Calendars/
```
Should show your calendar folders.

### Problem: Can't create events

**Solution**: Grant calendar permissions to your MCP client:
1. System Settings → Privacy & Security → Calendars
2. Enable your MCP client (Raycast/Claude)
3. Restart the client

### Problem: MCP client doesn't show calendar tools

**Solution**:
1. Check MCP logs: `tail -f ~/Library/Logs/Claude/mcp*.log`
2. Verify config file syntax
3. Restart MCP client completely

### Problem: Want to verify everything

**Solution**: Run the verification script:
```bash
cd /Users/s/dev/calendar-mcp
./verify_setup.sh
```

## How It Works

```
┌─────────────────────────────────┐
│ macOS Calendar.app              │
│ (.ics files in ~/Library/)      │
└─────────────┬───────────────────┘
              │
              │ Direct file read
              ▼
┌─────────────────────────────────┐
│ Calendar MCP                    │
│ - Reads .ics files              │
│ - Parses events                 │
│ - Creates AppleScript events    │
└─────────────┬───────────────────┘
              │
              │ MCP Protocol
              ▼
┌─────────────────────────────────┐
│ Raycast/Claude Desktop         │
│ - Natural language queries     │
│ - Event creation commands      │
└─────────────────────────────────┘
```

## Important Notes

✅ **Reading works immediately** - no permissions needed  
✅ **Creating needs permissions** - grant once to your MCP client  
✅ **Real-time data** - always reads current calendar  
✅ **Works with any MCP client** - Raycast, Claude, etc.  

## Next Steps

1. ✅ Test reading: "Analyze my calendar for last week"
2. ✅ Test creating: "Block two mornings next week to work on X"
3. ✅ Customize categories in `src/calendar_mcp/config.json`
4. ✅ Read documentation for advanced features

## Documentation

- **[EVENT_CREATION.md](EVENT_CREATION.md)** - Natural language event creation guide
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Fix common issues
- **[ADD_TO_CLAUDE.md](ADD_TO_CLAUDE.md)** - Adding to Claude Desktop
- **[README.md](README.md)** - Full project documentation

Happy calendar managing! 📅✨

