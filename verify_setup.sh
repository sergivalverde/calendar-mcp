#!/bin/bash
#
# Verify Calendar MCP Setup
# This script checks if everything is configured correctly
#

echo "=== Calendar MCP Setup Verification ==="
echo ""

SUCCESS=0
FAILURES=0

# Check 1: Python version
echo "1. Checking Python version..."
PYTHON_VERSION=$(python --version 2>&1 | grep -oE '[0-9]+\.[0-9]+' | head -1)
MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$MAJOR" -ge 3 ] && [ "$MINOR" -ge 10 ]; then
    echo "   ✅ Python $PYTHON_VERSION (OK)"
    ((SUCCESS++))
else
    echo "   ❌ Python $PYTHON_VERSION (Need 3.10+)"
    ((FAILURES++))
fi

# Check 2: uv installed
echo ""
echo "2. Checking uv installation..."
if command -v uv &> /dev/null; then
    UV_VERSION=$(uv --version | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
    echo "   ✅ uv $UV_VERSION installed"
    ((SUCCESS++))
else
    echo "   ❌ uv not found"
    echo "      Install: curl -LsSf https://astral.sh/uv/install.sh | sh"
    ((FAILURES++))
fi

# Check 3: icalBuddy installed
echo ""
echo "3. Checking icalBuddy..."
if command -v icalBuddy &> /dev/null; then
    ICALBUDDY_VERSION=$(icalBuddy -V 2>&1)
    echo "   ✅ icalBuddy installed: $ICALBUDDY_VERSION"
    ((SUCCESS++))
else
    echo "   ❌ icalBuddy not found"
    echo "      Install: brew install ical-buddy"
    ((FAILURES++))
fi

# Check 4: Calendar access
echo ""
echo "4. Checking calendar access..."
CALENDARS=$(icalBuddy calendars 2>&1)
if [[ "$CALENDARS" == *"error: No calendars"* ]] || [ -z "$CALENDARS" ]; then
    echo "   ❌ No calendar access"
    echo "      Fix: System Settings → Privacy & Security → Calendars"
    echo "           Enable Terminal, then restart Terminal"
    ((FAILURES++))
else
    echo "   ✅ Calendar access granted"
    ((SUCCESS++))
fi

# Check 5: Virtual environment
echo ""
echo "5. Checking virtual environment..."
if [ -d "/Users/s/dev/calendar-mcp/.venv" ]; then
    echo "   ✅ Virtual environment exists"
    ((SUCCESS++))
else
    echo "   ❌ Virtual environment not found"
    echo "      Run: cd /Users/s/dev/calendar-mcp && uv sync"
    ((FAILURES++))
fi

# Check 6: Dependencies installed
echo ""
echo "6. Checking dependencies..."
if [ -f "/Users/s/dev/calendar-mcp/.venv/bin/python" ]; then
    MCP_INSTALLED=$(/Users/s/dev/calendar-mcp/.venv/bin/python -c "import mcp; print('ok')" 2>/dev/null)
    if [ "$MCP_INSTALLED" = "ok" ]; then
        echo "   ✅ Dependencies installed"
        ((SUCCESS++))
    else
        echo "   ❌ Dependencies not installed"
        echo "      Run: cd /Users/s/dev/calendar-mcp && uv sync"
        ((FAILURES++))
    fi
else
    echo "   ⚠️  Cannot verify (venv missing)"
    ((FAILURES++))
fi

# Check 7: Cache exists
echo ""
echo "7. Checking calendar cache..."
if [ -f "$HOME/.calendar-mcp-cache/calendar_events.json" ]; then
    CACHE_DATE=$(grep -o '"fetched_at": "[^"]*"' "$HOME/.calendar-mcp-cache/calendar_events.json" | cut -d'"' -f4)
    EVENT_COUNT=$(grep -o '"event_count": [0-9]*' "$HOME/.calendar-mcp-cache/calendar_events.json" | grep -o '[0-9]*')
    echo "   ✅ Cache exists"
    echo "      Last updated: $CACHE_DATE"
    echo "      Events cached: $EVENT_COUNT"
    ((SUCCESS++))
else
    echo "   ❌ Cache not found"
    echo "      Run: cd /Users/s/dev/calendar-mcp && ./update_calendar_cache.sh"
    ((FAILURES++))
fi

# Check 8: Claude Desktop config
echo ""
echo "8. Checking Claude Desktop configuration..."
CLAUDE_CONFIG="$HOME/Library/Application Support/Claude/claude_desktop_config.json"
if [ -f "$CLAUDE_CONFIG" ]; then
    if grep -q "calendar-mcp" "$CLAUDE_CONFIG"; then
        echo "   ✅ Claude config includes calendar-mcp"
        ((SUCCESS++))
    else
        echo "   ⚠️  Claude config exists but no calendar-mcp entry"
        echo "      See: CLAUDE_SETUP.md"
        ((FAILURES++))
    fi
else
    echo "   ⚠️  Claude Desktop config not found"
    echo "      (OK if not using Claude Desktop)"
fi

# Summary
echo ""
echo "=== Summary ==="
echo "✅ Passed: $SUCCESS"
echo "❌ Failed: $FAILURES"
echo ""

if [ $FAILURES -eq 0 ]; then
    echo "🎉 All checks passed! Your Calendar MCP is ready to use."
    echo ""
    echo "Next steps:"
    echo "1. Update cache: ./update_calendar_cache.sh"
    echo "2. Ask Claude: 'Analyze my calendar for last week'"
    echo ""
    exit 0
else
    echo "⚠️  Some checks failed. Please fix the issues above."
    echo ""
    echo "Quick fixes:"
    echo "- Install missing tools: brew install ical-buddy"
    echo "- Grant calendar access: System Settings → Calendars → Terminal"
    echo "- Install dependencies: cd /Users/s/dev/calendar-mcp && uv sync"
    echo "- Create cache: ./update_calendar_cache.sh"
    echo ""
    echo "See TROUBLESHOOTING.md for detailed help."
    exit 1
fi







