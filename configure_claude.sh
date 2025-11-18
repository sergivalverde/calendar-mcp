#!/bin/bash
#
# Configure Claude Desktop for Calendar MCP
# This script adds the Calendar MCP configuration to Claude Desktop
#

set -e

echo "🔧 Configuring Claude Desktop for Calendar MCP..."
echo ""

CLAUDE_CONFIG_DIR="$HOME/Library/Application Support/Claude"
CLAUDE_CONFIG="$CLAUDE_CONFIG_DIR/claude_desktop_config.json"
PROJECT_DIR="/Users/s/dev/calendar-mcp"

# Create Claude config directory if it doesn't exist
if [ ! -d "$CLAUDE_CONFIG_DIR" ]; then
    echo "📁 Creating Claude config directory..."
    mkdir -p "$CLAUDE_CONFIG_DIR"
fi

# Backup existing config if it exists
if [ -f "$CLAUDE_CONFIG" ]; then
    BACKUP="$CLAUDE_CONFIG.backup.$(date +%Y%m%d_%H%M%S)"
    echo "💾 Backing up existing config to:"
    echo "   $BACKUP"
    cp "$CLAUDE_CONFIG" "$BACKUP"
fi

# Check if config already has calendar-mcp
if [ -f "$CLAUDE_CONFIG" ]; then
    if grep -q "calendar-mcp" "$CLAUDE_CONFIG"; then
        echo ""
        echo "⚠️  Calendar MCP already configured in Claude Desktop!"
        echo ""
        echo "Current configuration:"
        cat "$CLAUDE_CONFIG"
        echo ""
        echo "If you want to reconfigure, delete the existing entry first."
        exit 0
    fi
fi

# Create the configuration
echo "✍️  Writing Calendar MCP configuration..."

cat > "$CLAUDE_CONFIG" << 'EOF'
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
EOF

echo "✅ Configuration written successfully!"
echo ""

# Validate JSON
if command -v python3 &> /dev/null; then
    if python3 -m json.tool "$CLAUDE_CONFIG" > /dev/null 2>&1; then
        echo "✅ JSON syntax is valid"
    else
        echo "❌ JSON syntax error! Please check the config file."
        exit 1
    fi
fi

# Show the configuration
echo ""
echo "📄 Configuration file location:"
echo "   $CLAUDE_CONFIG"
echo ""
echo "📋 Configuration content:"
cat "$CLAUDE_CONFIG"
echo ""

# Check if virtual environment exists
if [ ! -f "$PROJECT_DIR/.venv/bin/python" ]; then
    echo "⚠️  Virtual environment not found!"
    echo "   Run: cd $PROJECT_DIR && uv sync"
    echo ""
fi

# Check if cache exists
if [ ! -f "$HOME/.calendar-mcp-cache/calendar_events.json" ]; then
    echo "⚠️  Calendar cache not found!"
    echo "   Run: cd $PROJECT_DIR && ./update_calendar_cache.sh"
    echo ""
fi

# Final instructions
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "✅ Claude Desktop Configuration Complete!"
echo ""
echo "📝 Next Steps:"
echo ""
echo "1. 🔄 Restart Claude Desktop (IMPORTANT!):"
echo "   • Press Cmd+Q to fully quit (not just close window)"
echo "   • Wait 10 seconds"
echo "   • Reopen Claude Desktop"
echo ""
echo "2. 📅 Update calendar cache (if you haven't already):"
echo "   cd $PROJECT_DIR"
echo "   ./update_calendar_cache.sh"
echo ""
echo "3. 🧪 Test with Claude:"
echo "   Ask: \"Analyze my calendar for last week\""
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📚 Documentation:"
echo "   • Quick Start: $PROJECT_DIR/QUICK_START.md"
echo "   • Add to Claude: $PROJECT_DIR/ADD_TO_CLAUDE.md"
echo "   • Troubleshooting: $PROJECT_DIR/TROUBLESHOOTING.md"
echo ""
echo "🔍 Verify setup: $PROJECT_DIR/verify_setup.sh"
echo ""






