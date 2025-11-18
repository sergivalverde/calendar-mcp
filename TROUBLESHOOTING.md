# Troubleshooting Guide

## Problem: Claude says "No events found"

### Solution 1: Update the Calendar Cache

Claude Desktop **cannot** access icalBuddy directly. You must cache your calendar data first:

```bash
cd /Users/s/dev/calendar-mcp
./update_calendar_cache.sh
```

This creates a cache that Claude can read without needing calendar permissions.

**See [CACHE_SOLUTION.md](CACHE_SOLUTION.md) for full details.**

---

## Problem: Update cache script fails with "No calendars"

### Solution: Grant Terminal Calendar Permissions

1. Open **System Settings → Privacy & Security → Calendars**
2. Find and enable **Terminal** (or iTerm, if you use it)
3. **Restart Terminal completely** (Cmd+Q, not just close window)
4. Try the update script again:
   ```bash
   ./update_calendar_cache.sh
   ```

---

## Problem: icalBuddy not found

### Solution: Install icalBuddy

```bash
brew install ical-buddy
```

Verify installation:
```bash
icalBuddy -V
```

---

## Problem: Python version error

### Solution: Use Python 3.10+

The MCP package requires Python 3.10 or higher.

Check your version:
```bash
python --version
```

If you need to upgrade:
```bash
# Using pyenv
pyenv install 3.11
pyenv local 3.11

# Or specify in .python-version
echo "3.11" > .python-version
```

Then rebuild:
```bash
uv sync --reinstall
```

---

## Problem: ModuleNotFoundError: No module named 'mcp'

### Solution: Sync Dependencies

```bash
cd /Users/s/dev/calendar-mcp
uv sync
```

Make sure you're using the virtual environment's Python:
```bash
# Use uv run
uv run python -m calendar_mcp.server

# Or activate venv first
source .venv/bin/activate
python -m calendar_mcp.server
```

---

## Problem: Architecture mismatch error (arm64/x86_64)

### Solution: Force ARM64 on Apple Silicon

If you see errors about architecture mismatches, use this Claude Desktop config:

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

See [WORKING_SOLUTION.md](WORKING_SOLUTION.md) for details.

---

## Problem: Cache is outdated

### Solution: Re-run Update Script

The cache doesn't auto-update. Update it whenever you need fresh data:

```bash
cd /Users/s/dev/calendar-mcp
./update_calendar_cache.sh
```

**Tip**: Set up a daily cron job:
```bash
crontab -e
# Add: 0 9 * * * /Users/s/dev/calendar-mcp/update_calendar_cache.sh
```

---

## Problem: How do I know if cache is working?

### Solution: Check Cache Status

```bash
# See when cache was last updated
cat ~/.calendar-mcp-cache/calendar_events.json | grep fetched_at

# Count events
cat ~/.calendar-mcp-cache/calendar_events.json | grep event_count

# View cache file
cat ~/.calendar-mcp-cache/calendar_events.json | jq .
```

Test cache access:
```bash
cd /Users/s/dev/calendar-mcp
uv run python -c "
from calendar_mcp.cache_calendar import CalendarCache
from datetime import date, timedelta

cache = CalendarCache()
today = date.today()
events = cache.get_events_for_range(today, today)
print(f'Events today: {len(events)}')
for e in events:
    print(f'  - {e[\"title\"]}')
"
```

---

## Problem: Tests fail

### Solution 1: Run with uv

```bash
cd /Users/s/dev/calendar-mcp
uv run python test_calendar_analysis.py
```

### Solution 2: Check Python Path

Make sure you're in the project directory:
```bash
cd /Users/s/dev/calendar-mcp
export PYTHONPATH="${PWD}/src:${PYTHONPATH}"
python test_calendar_analysis.py
```

---

## Problem: Claude Desktop doesn't see the MCP

### Solution: Check Configuration

1. Verify your Claude Desktop config at:
   ```
   ~/Library/Application Support/Claude/claude_desktop_config.json
   ```

2. Should contain:
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

3. **Restart Claude completely** (Cmd+Q, wait 10 seconds, reopen)

4. Check Claude's logs:
   ```bash
   tail -f ~/Library/Logs/Claude/mcp*.log
   ```

See [CLAUDE_SETUP.md](CLAUDE_SETUP.md) for detailed setup.

---

## Problem: Want to test without Claude

### Solution: Run MCP Server Directly

```bash
cd /Users/s/dev/calendar-mcp
uv run python -m calendar_mcp.server
```

The server should start and show:
```
MCP Server running on stdio
```

Press Ctrl+C to stop.

---

## Diagnostic Tools

### Full System Check

```bash
cd /Users/s/dev/calendar-mcp
./diagnose_calendar.py
```

This checks:
- ✅ icalBuddy installation
- ✅ Calendar access
- ✅ Events availability
- ✅ Cache status

### Check Everything

```bash
# 1. Python version
python --version

# 2. icalBuddy installed
icalBuddy -V

# 3. Calendar access
icalBuddy calendars

# 4. Today's events
icalBuddy eventsToday

# 5. Cache exists
ls -lh ~/.calendar-mcp-cache/

# 6. Dependencies installed
uv sync --check

# 7. MCP server starts
timeout 5 uv run python -m calendar_mcp.server || echo "Server started OK"
```

---

## Still Having Issues?

1. **Read the guides**:
   - [CACHE_SOLUTION.md](CACHE_SOLUTION.md) - How to use the cache (RECOMMENDED)
   - [WORKING_SOLUTION.md](WORKING_SOLUTION.md) - Complete debugging history
   - [CLAUDE_SETUP.md](CLAUDE_SETUP.md) - Claude Desktop setup

2. **Check logs**:
   ```bash
   tail -f ~/Library/Logs/Claude/mcp*.log
   ```

3. **Try clean reinstall**:
   ```bash
   cd /Users/s/dev/calendar-mcp
   rm -rf .venv
   uv sync
   ./update_calendar_cache.sh
   ```

4. **Verify permissions**:
   - System Settings → Privacy & Security → Calendars
   - Terminal should be checked
   - Restart Terminal after granting permissions







