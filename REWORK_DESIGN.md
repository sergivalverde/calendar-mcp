# Calendar-MCP Rework Design Document

**Branch**: `rework-unified-cache`  
**Date**: November 18, 2025  
**Status**: In Development

## Executive Summary

Complete architectural rework of calendar-mcp to use a unified icalBuddy-powered cache as the single source of truth for calendar data. This eliminates complexity, improves reliability, and provides consistent real-time access.

## Key Findings: calendar-cli Evaluation

**Result**: ❌ **Not suitable for this project**

**Why**: calendar-cli is a **CalDAV remote server client**, not a local macOS Calendar.app reader. It:
- Cannot read from local macOS Calendar.app databases
- Requires CalDAV server connection (iCloud, Nextcloud, etc.)
- Works over network, not local file system
- Would add complexity rather than reduce it

**Decision**: Continue with **icalBuddy for reads** + **AppleScript for writes**

## Architecture Changes

### Current Architecture (Multi-Layer Fallback)
```
┌─────────────────────────────────────────────┐
│           macOS Calendar.app                │
└──────────────┬─────────────┬────────────────┘
               │             │
    Direct .ics│             │icalBuddy (perms)
               │             │
         ┌─────▼──────┐  ┌───▼──────────┐
         │ics_reader  │  │simple_cache  │
         │(primary)   │  │(fallback)    │
         └─────┬──────┘  └───┬──────────┘
               │             │
               └──────┬──────┘
                      ▼
            ┌──────────────────┐
            │calendar_extractor│
            └─────────┬────────┘
                      │
                [rest of pipeline]
```

**Problems**:
- Complex fallback logic
- Inconsistent data sources
- Permission issues with direct .ics reading
- Manual cache management
- Stale data (5-minute TTL)

### New Architecture (Unified Cache)
```
┌─────────────────────────────────────────────┐
│           macOS Calendar.app                │
└──────────────┬──────────────────────────────┘
               │
               │icalBuddy (with permissions)
               │
         ┌─────▼──────────────────────┐
         │  UnifiedCache               │
         │  - Auto-refresh on startup  │
         │  - Background refresh       │
         │  - 2mo back + 2mo forward   │
         │  - Health monitoring        │
         │  - Manual refresh tool      │
         └─────┬──────────────────────┘
               │ SINGLE SOURCE OF TRUTH
               ▼
       ┌────────────────┐
       │calendar_manager│ (simplified)
       └────────┬───────┘
                │
       [rest of pipeline]
```

**Benefits**:
- Single, reliable data source
- Predictable behavior
- Simpler codebase
- Built-in cache management
- Always fresh on startup

## Detailed Design

### 1. Enhanced Cache System (`unified_cache.py`)

**New file** replacing `simple_cache.py` with enhanced features:

```python
class UnifiedCache:
    """
    Single source of truth for all calendar data.
    Uses icalBuddy exclusively for reliable calendar access.
    """
    
    # Configuration
    CACHE_FILE = Path.home() / ".cache" / "calendar-mcp" / "unified_cache.json"
    DEFAULT_TTL = 300  # 5 minutes
    DATE_RANGE_PAST = 60  # 2 months back
    DATE_RANGE_FUTURE = 60  # 2 months forward
    
    def __init__(self, config: Config):
        """Initialize cache with configuration."""
        self.config = config
        self.cache_file = self.CACHE_FILE
        self.ttl = config.get("cache_ttl", self.DEFAULT_TTL)
        self.date_range_past = config.get("cache_days_past", self.DATE_RANGE_PAST)
        self.date_range_future = config.get("cache_days_future", self.DATE_RANGE_FUTURE)
        self._background_thread = None
        
    def initialize(self) -> bool:
        """
        Initialize cache on startup.
        - Creates cache directory if needed
        - Performs initial fetch if cache missing/expired
        - Starts background refresh thread
        - Returns True if successful, False if failed
        """
        
    def refresh(self, force: bool = False) -> dict:
        """
        Manually refresh cache.
        - Calls icalBuddy with configured date range
        - Parses output into CalendarEvent objects
        - Writes to cache file with metadata
        - Returns cache statistics
        """
        
    def get_events(self, start_date: date, end_date: date) -> list[CalendarEvent]:
        """
        Retrieve events from cache.
        - Auto-refreshes if cache expired (TTL check)
        - Filters events by requested date range
        - Returns list of CalendarEvent objects
        """
        
    def get_status(self) -> dict:
        """
        Get cache health status.
        Returns:
        {
            "cache_file": path,
            "exists": bool,
            "age_seconds": int,
            "is_expired": bool,
            "ttl": int,
            "event_count": int,
            "date_range": {
                "start": "YYYY-MM-DD",
                "end": "YYYY-MM-DD"
            },
            "last_refresh": "ISO timestamp",
            "next_refresh": "ISO timestamp",
            "background_refresh": bool
        }
        """
        
    def start_background_refresh(self):
        """
        Start background thread that refreshes cache periodically.
        - Runs every TTL seconds
        - Silent failures logged but not raised
        - Thread is daemon (exits when main program exits)
        """
        
    def stop_background_refresh(self):
        """Stop background refresh thread gracefully."""
        
    def _run_icalbuddy(self, start_date: date, end_date: date) -> str:
        """
        Execute icalBuddy command.
        - Uses configured calendar names
        - Handles errors gracefully
        - Returns raw output or raises exception
        """
        
    def _parse_icalbuddy_output(self, output: str) -> list[CalendarEvent]:
        """
        Parse icalBuddy output into CalendarEvent objects.
        - Handles various date formats
        - Extracts all event properties
        - Returns structured data
        """
```

**Key Features**:
1. **Startup Initialization**: Auto-refresh on MCP server start
2. **Configurable Date Range**: 2 months back + 2 months forward (configurable)
3. **Background Refresh**: Optional daemon thread for auto-refresh
4. **Health Monitoring**: Expose cache status via MCP tool
5. **Manual Refresh**: Explicit tool to force cache update
6. **Graceful Degradation**: Clear error messages when icalBuddy fails

### 2. Simplified Calendar Manager (`calendar_manager.py`)

**Rename** `calendar_extractor.py` → `calendar_manager.py` and simplify:

```python
class CalendarManager:
    """
    Simplified calendar data manager.
    Uses UnifiedCache as single source of truth.
    """
    
    def __init__(self, config: Config):
        self.config = config
        self.cache = UnifiedCache(config)
        self.classifier = EventClassifier(config)
        self.energy_tracker = EnergyTracker()
        
    def initialize(self) -> bool:
        """Initialize cache on startup."""
        return self.cache.initialize()
        
    def get_events(self, start_date: date, end_date: date) -> list[CalendarEvent]:
        """Get events from cache (automatically refreshes if needed)."""
        return self.cache.get_events(start_date, end_date)
        
    def refresh_cache(self, force: bool = False) -> dict:
        """Manually refresh cache."""
        return self.cache.refresh(force=force)
        
    def get_cache_status(self) -> dict:
        """Get cache health status."""
        return self.cache.get_status()
```

**Removed**:
- `ICSReader` integration
- Fallback logic
- Direct file system access
- Complex error handling chains

### 3. Enhanced MCP Server (`server.py`)

**Add new tools**:

```python
@mcp.tool()
async def refresh_cache() -> str:
    """
    Manually refresh the calendar cache.
    
    Use this when:
    - You need the latest calendar data immediately
    - Cache seems stale or out of sync
    - After adding/modifying events in Calendar.app
    
    Returns cache statistics.
    """
    
@mcp.tool()
async def get_cache_status() -> str:
    """
    Get calendar cache health status.
    
    Returns information about:
    - Cache age and expiration
    - Number of cached events
    - Date range coverage
    - Last/next refresh times
    - Background refresh status
    """
```

**Modify existing tools**:
- `query_calendar`: Add cache status to response
- `create_*` tools: Auto-refresh cache after event creation
- All tools: Handle cache initialization errors gracefully

**Startup sequence**:
```python
async def main():
    # Initialize config
    config = Config.load()
    
    # Initialize calendar manager
    calendar_manager = CalendarManager(config)
    
    # Initialize cache (may take a few seconds)
    logger.info("Initializing calendar cache...")
    if not calendar_manager.initialize():
        logger.error("Failed to initialize cache - check icalBuddy permissions")
    else:
        logger.info("Cache initialized successfully")
    
    # Start MCP server
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        # ... rest of server setup
```

### 4. Updated Configuration (`config.json`)

**Add cache settings**:
```json
{
  "cache": {
    "ttl_seconds": 300,
    "days_past": 60,
    "days_future": 60,
    "background_refresh": true,
    "cache_directory": "~/.cache/calendar-mcp"
  },
  "icalbuddy": {
    "command": "icalBuddy",
    "date_format": "%Y-%m-%d %H:%M:%S",
    "time_format": "%H:%M"
  },
  "calendars": {
    "include": ["Work", "Personal"],
    "exclude": [],
    "default_calendar": "Work"
  },
  "classification": {
    // ... existing classification config
  },
  "event_creation": {
    // ... existing event creation config
  }
}
```

**Remove obsolete settings**:
- Direct .ics file paths
- Fallback priorities
- ICSReader-specific options

### 5. Write Operations (No Change)

**Keep AppleScript** for event creation:
- `applescript_writer.py` remains unchanged
- Reliable, native macOS integration
- Well-tested and working
- No need to change what works

**After event creation**:
- Auto-refresh cache to include new events
- Or wait for next TTL-based refresh

### 6. Automated Setup Script (`setup.sh`)

**New comprehensive setup script**:

```bash
#!/bin/bash
# Calendar-MCP Unified Setup Script

set -e

echo "🗓️  Calendar-MCP Setup"
echo "====================="

# 1. Check macOS version
echo "✓ Checking macOS version..."
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ This tool requires macOS"
    exit 1
fi

# 2. Install icalBuddy
echo "✓ Installing icalBuddy..."
if ! command -v icalBuddy &> /dev/null; then
    brew install ical-buddy
else
    echo "  icalBuddy already installed"
fi

# 3. Check calendar permissions
echo "✓ Checking calendar permissions..."
if icalBuddy eventsToday > /dev/null 2>&1; then
    echo "  ✓ Calendar permissions granted"
else
    echo "  ⚠️  Calendar permissions needed"
    echo "  Please grant calendar access to Terminal in System Settings"
    echo "  System Settings → Privacy & Security → Calendars → Terminal"
    read -p "Press Enter after granting permissions..."
fi

# 4. Install Python dependencies
echo "✓ Installing Python dependencies..."
pip install -e .

# 5. Initialize cache
echo "✓ Initializing calendar cache..."
python -c "
from src.calendar_mcp.unified_cache import UnifiedCache
from src.calendar_mcp.config import Config
cache = UnifiedCache(Config.load())
cache.initialize()
print('Cache initialized with', cache.get_status()['event_count'], 'events')
"

# 6. Validate setup
echo "✓ Validating setup..."
python -c "
from src.calendar_mcp.unified_cache import UnifiedCache
from src.calendar_mcp.config import Config
cache = UnifiedCache(Config.load())
status = cache.get_status()
assert status['exists'], 'Cache file not found'
assert status['event_count'] >= 0, 'Invalid event count'
print('✓ Setup validation passed')
"

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Configure Claude Desktop (see README.md)"
echo "2. Test: python -m src.calendar_mcp.server"
echo "3. Use: Ask Claude to analyze your calendar"
```

### 7. Testing Strategy

**New test structure**:
```
tests/
  unit/
    test_unified_cache.py
    test_calendar_manager.py
    test_classifier.py
    test_energy_tracker.py
  integration/
    test_icalbuddy_integration.py
    test_applescript_integration.py
    test_mcp_server.py
  e2e/
    test_full_workflow.py
```

**Key test scenarios**:
1. Cache initialization from empty state
2. Cache refresh with various date ranges
3. TTL expiration and auto-refresh
4. Background refresh thread lifecycle
5. Error handling (icalBuddy failures)
6. Event filtering and classification
7. MCP tool invocations
8. Permission issues simulation

### 8. Documentation Consolidation

**Merge 14+ docs into 4 core files**:

1. **README.md** (User Guide)
   - Quick start (one-command setup)
   - Configuration
   - Usage examples
   - FAQ
   - Troubleshooting common issues

2. **ARCHITECTURE.md** (Technical Design)
   - System architecture
   - Cache design
   - Data flow
   - Component interactions
   - Extension points

3. **DEVELOPMENT.md** (Developer Guide)
   - Setup development environment
   - Running tests
   - Code structure
   - Contributing guidelines
   - Release process

4. **TROUBLESHOOTING.md** (Problem Solving)
   - Permission issues
   - Cache problems
   - icalBuddy errors
   - Debug procedures
   - Known limitations

**Remove**:
- ADD_TO_CLAUDE.md
- CLAUDE_SETUP.md
- EVENT_CREATION.md
- INDEX.md
- INSTALL.md
- QUICK_FIX.md
- QUICK_START.md
- QUICKSTART.md
- SOLUTION_SUMMARY.md
- START_HERE.md
- WORKING_SOLUTION.md
- calendar_tasks_needed.md
- All mcp-config-*.json except mcp-config.json

### 9. File Cleanup

**Remove obsolete files**:
```
src/calendar_mcp/ics_reader.py          # Replaced by unified_cache.py
src/calendar_mcp/simple_cache.py        # Replaced by unified_cache.py
calendar_wrapper.sh                      # Obsolete
get_calendar_data.sh                     # Obsolete
configure_claude.sh                      # Replaced by setup.sh
verify_setup.sh                          # Replaced by setup.sh
diagnose_calendar_issues.py             # Functionality in unified_cache
test_calendar_access.py                 # Replaced by tests/
test_calendar_analysis.py               # Replaced by tests/
test_final_setup.py                     # Replaced by tests/
update_cache_now.py                     # Functionality in MCP tool
week46_analysis.py                      # Example/temporary
```

**Rename**:
```
src/calendar_mcp/calendar_extractor.py → src/calendar_mcp/calendar_manager.py
src/calendar_mcp/simple_cache.py → src/calendar_mcp/unified_cache.py (rewrite)
```

## Implementation Plan

### Phase 1: Core Cache System ✅ Design Complete
- [x] Research calendar-cli
- [x] Design unified cache architecture
- [ ] Implement `unified_cache.py`
- [ ] Unit tests for cache

### Phase 2: Integration
- [ ] Simplify `calendar_manager.py`
- [ ] Remove `ics_reader.py`
- [ ] Update `server.py` with new tools
- [ ] Integration tests

### Phase 3: Configuration & Setup
- [ ] Update `config.json` structure
- [ ] Create `setup.sh` script
- [ ] Test setup process

### Phase 4: Documentation
- [ ] Consolidate docs into 4 files
- [ ] Update README with new architecture
- [ ] Write migration guide

### Phase 5: Testing & Validation
- [ ] Full test suite
- [ ] End-to-end testing
- [ ] Performance testing
- [ ] Permission scenarios

### Phase 6: Cleanup
- [ ] Remove obsolete files
- [ ] Remove obsolete config files
- [ ] Clean up dependencies
- [ ] Final validation

## Migration Guide (for existing users)

**What changes**:
- Single cache file location
- No more direct .ics reading
- New cache management tools
- Updated configuration format

**What stays the same**:
- Event classification
- Energy tracking
- Report generation
- Event creation via AppleScript
- MCP tool interfaces (mostly)

**Migration steps**:
1. Backup existing config
2. Pull latest code
3. Run new `setup.sh`
4. Test with `python -m src.calendar_mcp.server`
5. Update Claude Desktop config if needed

## Success Criteria

✅ Single source of truth for calendar data  
✅ Auto-refresh on startup  
✅ Manual refresh tool available  
✅ Cache covers 2 months back + 2 months forward  
✅ Background refresh optional  
✅ Health monitoring via MCP tool  
✅ Simpler codebase (fewer files, less complexity)  
✅ Better documentation (4 core docs vs 14+)  
✅ Automated setup script  
✅ Comprehensive test suite  
✅ No regression in functionality  

## Timeline

- **Phase 1-2**: 2-3 days (core implementation)
- **Phase 3-4**: 1-2 days (config & docs)
- **Phase 5-6**: 1-2 days (testing & cleanup)
- **Total**: ~1 week for complete rework

## Risk Mitigation

**Risk**: icalBuddy permissions issues  
**Mitigation**: Clear error messages, setup script validation, troubleshooting guide

**Risk**: Background refresh causing issues  
**Mitigation**: Make optional, add graceful shutdown, daemon thread

**Risk**: Breaking changes for existing users  
**Mitigation**: Migration guide, backward compatibility where possible

**Risk**: Performance degradation  
**Mitigation**: Performance tests, TTL tuning, async operations

## Next Steps

1. Begin implementation of `unified_cache.py`
2. Write unit tests alongside implementation
3. Iterate on design based on testing
4. Proceed to Phase 2 once Phase 1 validated
