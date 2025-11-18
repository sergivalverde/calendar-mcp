# Calendar MCP Quick Start

## 3-Minute Setup

### Step 1: Install Dependencies (30 seconds)

```bash
cd /Users/s/dev/calendar-mcp
uv sync
```

### Step 2: Test It Works (30 seconds)

```bash
uv run python test_calendar_analysis.py
```

You should see: `✅ All tests passed!`

### Step 3: Configure Claude Desktop (1 minute)

Edit: `~/Library/Application Support/Claude/claude_desktop_config.json`

Add this:

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
    }
  }
}
```

### Step 4: Restart Claude Desktop (30 seconds)

Completely quit and reopen Claude Desktop.

### Step 5: Try It! (30 seconds)

Ask Claude:

```
Analyze my calendar for last week
```

## Done! 🎉

You can now ask Claude questions about your calendar:

- "Show time distribution for November"
- "What were my energy levels yesterday?"
- "How much time did I spend in meetings this month?"

## Customize (Optional)

### Select Specific Calendars

Edit `src/calendar_mcp/config.json`:

```json
{
  "calendar": {
    "calendars": ["Work", "Personal"]
  }
}
```

### Customize Your Company Domain

```json
{
  "classification": {
    "team_domains": ["yourcompany.com"]
  }
}
```

## Troubleshooting

**Issue**: Tests fail or imports don't work

**Fix**: 
```bash
rm -rf .venv uv.lock
uv sync
```

**Issue**: icalBuddy not found

**Fix**:
```bash
brew install ical-buddy
```

**Issue**: No calendars found

**Fix**:
```bash
icalBuddy calendars  # Check what's available
```

## Next Steps

- Read [INSTALL.md](INSTALL.md) for detailed installation
- Read [CLAUDE_SETUP.md](CLAUDE_SETUP.md) for Claude configuration details  
- Read [README.md](README.md) for full documentation








