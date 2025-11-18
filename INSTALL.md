# Calendar MCP Installation Guide

## Quick Start (5 minutes)

### Prerequisites

1. **Python 3.10+** (Python 3.11 recommended)
2. **uv** package manager: `curl -LsSf https://astral.sh/uv/install.sh | sh`
3. **icalBuddy**: `brew install ical-buddy`

### Installation Steps

```bash
# 1. Navigate to the project directory
cd /Users/s/dev/calendar-mcp

# 2. Install dependencies (uv handles everything automatically)
uv sync

# 3. Test the installation
uv run python test_calendar_analysis.py
```

You should see: `✅ All tests passed!`

## Claude Desktop Configuration

### Method 1: Using uv (Recommended)

Add this to `~/Library/Application Support/Claude/claude_desktop_config.json`:

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

**Advantages:**
- ✅ Always uses the correct Python version and dependencies
- ✅ No manual environment setup needed
- ✅ Works even if you update dependencies
- ✅ Portable - works on any machine with uv installed

### Method 2: Direct Virtual Environment

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

## Verify Installation

### Test 1: Import Test
```bash
uv run python -c "from calendar_mcp.server import CalendarAnalysisServer; print('✅ Success')"
```

### Test 2: Full Test Suite
```bash
uv run python test_calendar_analysis.py
```

### Test 3: Check Available Calendars
```bash
uv run python list_calendars.py
```

### Test 4: Server Start (manual test)
```bash
# Server should start and wait for input
uv run calendar-mcp
# Press Ctrl+C to stop
```

## Configuration

### Calendar Selection

Edit `src/calendar_mcp/config.json`:

```json
{
  "calendar": {
    "calendars": null  // Use all calendars, or ["Work", "Personal"] for specific ones
  },
  "classification": {
    ...
  }
}
```

### Customizing Classification Rules

Modify keyword lists in `src/calendar_mcp/config.json`:

```json
{
  "classification": {
    "team_domains": ["yourcompany.com"],
    "excluded_titles": ["Blocked", "Busy"],
    "personal_patterns": ["Family", "Personal"],
    ...
  }
}
```

## Usage Examples

Once configured in Claude Desktop, you can ask:

```
Analyze my calendar for last week
```

```
Show time distribution for November
```

```
What were my energy levels yesterday?
```

```
How much time did I spend in team meetings this month?
```

## Troubleshooting

### Issue: "No module named 'mcp'"

**Solution**: Run `uv sync` to install dependencies

```bash
cd /Users/s/dev/calendar-mcp
uv sync
```

### Issue: "icalBuddy not found"

**Solution**: Install icalBuddy

```bash
brew install ical-buddy
```

### Issue: "No calendars found"

**Solution**: Check Calendar.app permissions and run:

```bash
icalBuddy calendars
```

### Issue: Claude Desktop can't connect

**Solution**: Check the logs at:
```bash
tail -f ~/Library/Logs/Claude/mcp*.log
```

## Development

### Run Tests
```bash
uv run pytest
```

### Format Code
```bash
uv run ruff check --fix src/
```

### Add Dependencies
```bash
uv add package-name
```

## Updating

```bash
cd /Users/s/dev/calendar-mcp
git pull  # if using git
uv sync   # update dependencies
```

## Uninstall

```bash
# Remove from Claude Desktop config
# Then delete the directory
rm -rf /Users/s/dev/calendar-mcp
```

## Support

- Check README.md for detailed documentation
- Review config.json for customization options
- Run test suite to verify functionality








