#!/bin/bash
#
# Calendar Wrapper Script
# This script runs icalBuddy with the current user's permissions
# and passes the data to the MCP server via stdin/stdout
#

# Export environment to ensure icalBuddy runs with user permissions
export PATH="/usr/local/bin:$PATH"

# Run the Python server with the wrapper
exec arch -arm64 /Users/s/dev/calendar-mcp/.venv/bin/python -m calendar_mcp.server "$@"








