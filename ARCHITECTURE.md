# Calendar MCP Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                   │
│                        YOUR MAC                                   │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    Calendar.app                           │   │
│  │  • Personal events                                        │   │
│  │  • Work meetings                                          │   │
│  │  • Energy markers (E1-E4)                                 │   │
│  └─────────────────────┬────────────────────────────────────┘   │
│                        │                                          │
│                        │ (Calendar Data)                          │
│                        ▼                                          │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              icalBuddy (CLI Tool)                         │   │
│  │  • Reads calendar database                               │   │
│  │  • Extracts events with full details                     │   │
│  │  • Requires calendar permissions                         │   │
│  └─────────────────────┬────────────────────────────────────┘   │
│                        │                                          │
│                        │ (Called by)                              │
│                        ▼                                          │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │           Terminal Process                                │   │
│  │  ✅ HAS calendar permissions                             │   │
│  │  • Runs: update_calendar_cache.sh                        │   │
│  │  • Fetches 30 days back + 30 forward                     │   │
│  └─────────────────────┬────────────────────────────────────┘   │
│                        │                                          │
│                        │ (Writes JSON)                            │
│                        ▼                                          │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │     ~/.calendar-mcp-cache/calendar_events.json           │   │
│  │  {                                                        │   │
│  │    "fetched_at": "2024-11-17",                           │   │
│  │    "event_count": 42,                                    │   │
│  │    "events": [...]                                       │   │
│  │  }                                                        │   │
│  └─────────────────────┬────────────────────────────────────┘   │
│                        │                                          │
│                        │ (Reads JSON - no permissions needed!)    │
│                        ▼                                          │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │           Calendar MCP Server                             │   │
│  │  ❌ NO calendar permissions needed                       │   │
│  │  • Reads cache file                                      │   │
│  │  • Classifies events                                     │   │
│  │  • Tracks energy levels                                  │   │
│  │  • Generates reports                                     │   │
│  └─────────────────────┬────────────────────────────────────┘   │
│                        │                                          │
│                        │ (MCP Protocol)                           │
│                        ▼                                          │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │           Claude Desktop                                  │   │
│  │  ❌ NO calendar permissions needed                       │   │
│  │  • Calls MCP tools                                       │   │
│  │  • Receives reports                                      │   │
│  │  • Presents to user                                      │   │
│  └─────────────────────┬────────────────────────────────────┘   │
│                        │                                          │
│                        │ (Natural language)                       │
│                        ▼                                          │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                       YOU!                                │   │
│  │  • Ask questions                                          │   │
│  │  • Get insights                                           │   │
│  │  • Make decisions                                         │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. Cache Update Flow

```
┌─────────┐    icalBuddy    ┌──────────┐    parse     ┌──────────┐
│Calendar │───────────────►│ Terminal │─────────────►│  Cache   │
│  .app   │                 │  (perms) │              │   JSON   │
└─────────┘                 └──────────┘              └──────────┘
    │                            │                          │
    │                            │                          │
    └────────────────────────────┴──────────────────────────┘
           User runs: ./update_calendar_cache.sh
```

### 2. Query Flow

```
┌──────┐  "analyze last   ┌────────┐  MCP call   ┌──────────┐
│ You  │──────week"──────►│ Claude │────────────►│ Calendar │
└──────┘                   └────────┘             │   MCP    │
    ▲                          │                  └─────┬────┘
    │                          │                        │
    │       Report             │                  read cache
    │                          │                        │
    └──────────────────────────┘                        ▼
                                                 ┌──────────┐
                                                 │  Cache   │
                                                 │   JSON   │
                                                 └──────────┘
```

## Component Architecture

### Calendar MCP Server

```
┌───────────────────────────────────────────────────────┐
│             calendar_mcp.server                       │
│  ┌─────────────────────────────────────────────────┐ │
│  │  MCP Server                                     │ │
│  │  • Registers tools                              │ │
│  │  • Handles queries                              │ │
│  │  • Orchestrates workflow                        │ │
│  └──────────────────┬──────────────────────────────┘ │
│                     │                                 │
│         ┌───────────┼───────────┐                     │
│         │           │           │                     │
│         ▼           ▼           ▼                     │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐             │
│  │Calendar  │ │Event     │ │Energy    │             │
│  │Extractor │ │Classifier│ │Tracker   │             │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘             │
│       │            │            │                     │
│       └────────────┼────────────┘                     │
│                    │                                  │
│                    ▼                                  │
│            ┌──────────────┐                           │
│            │Report        │                           │
│            │Generator     │                           │
│            └──────────────┘                           │
│                                                       │
└───────────────────────────────────────────────────────┘
```

### Cache System

```
┌───────────────────────────────────────────────────────┐
│             cache_calendar.py                         │
│                                                       │
│  ┌─────────────────────────────────────────────────┐ │
│  │  CalendarCache                                  │ │
│  │                                                 │ │
│  │  fetch_and_cache_events()                      │ │
│  │    ├─► Run icalBuddy                           │ │
│  │    ├─► Parse output                            │ │
│  │    └─► Save JSON                               │ │
│  │                                                 │ │
│  │  load_cached_events()                          │ │
│  │    └─► Read JSON file                          │ │
│  │                                                 │ │
│  │  get_events_for_range(start, end)             │ │
│  │    ├─► Load cache                              │ │
│  │    └─► Filter by date                          │ │
│  │                                                 │ │
│  └─────────────────────────────────────────────────┘ │
│                                                       │
└───────────────────────────────────────────────────────┘
```

## Permission Model

### The Problem

```
┌──────────────┐                    ┌──────────────┐
│   Claude     │───icalBuddy───X───►│   Calendar   │
│   Desktop    │                     │     .app     │
└──────────────┘                    └──────────────┘
                  ❌ Cannot grant permissions!
```

### The Solution

```
┌──────────────┐                    ┌──────────────┐
│   Terminal   │───icalBuddy───✓───►│   Calendar   │
└──────┬───────┘                     │     .app     │
       │                             └──────────────┘
       │ write
       ▼
┌──────────────┐
│    Cache     │
│     JSON     │
└──────┬───────┘
       │ read
       ▼
┌──────────────┐
│   Claude     │
│   Desktop    │
└──────────────┘
    ✅ Works!
```

## Event Processing Pipeline

```
1. Raw Events (from cache)
   ├─ title: "Team Meeting"
   ├─ datetime: "2024-11-17 10:00:00..."
   ├─ attendees: "Alice <alice@example.com>"
   └─ notes: "Q4 planning"

2. Event Classification
   └─► Classifier analyzes:
       ├─ Keywords in title
       ├─ Attendee domains
       ├─ Notes content
       └─► Assigns: "Team Meetings"

3. Energy Tracking
   └─► Finds "E2" events
       └─► Matches to main events
           └─► Assigns energy level

4. Report Generation
   └─► Groups by category
       └─► Creates tables & charts
           └─► Returns markdown

5. Final Report
   ├─ Raw events table
   ├─ Daily summaries
   ├─ Category distribution (pie chart)
   └─ Energy distribution (pie chart)
```

## File Structure

```
calendar-mcp/
│
├── src/calendar_mcp/
│   ├── server.py              # MCP server entry point
│   ├── calendar_extractor.py  # icalBuddy interface + cache
│   ├── cache_calendar.py      # Cache system (NEW!)
│   ├── classifier.py          # Event categorization
│   ├── energy_tracker.py      # Energy level matching
│   ├── report_generator.py    # Markdown report creation
│   ├── models.py              # Pydantic data models
│   ├── config.py              # Configuration management
│   └── config.json            # User-editable rules
│
├── ~/.calendar-mcp-cache/     # Cache directory (created)
│   └── calendar_events.json   # Cached events
│
├── Scripts/
│   ├── update_calendar_cache.sh  # Update cache
│   ├── verify_setup.sh           # Verify system
│   └── diagnose_calendar.py      # Diagnose issues
│
└── Documentation/
    ├── START_HERE.md             # Landing page
    ├── QUICK_START.md            # 5-min setup
    ├── CACHE_SOLUTION.md         # Cache details
    ├── TROUBLESHOOTING.md        # Problem solving
    ├── INDEX.md                  # Navigation
    └── [9 more guides...]
```

## Configuration Flow

```
┌────────────────────────────────────────────────────┐
│         src/calendar_mcp/config.json               │
│  {                                                 │
│    "calendar": {                                   │
│      "calendars": null  // or ["Work", "Personal"]│
│    },                                              │
│    "classification": {                             │
│      "categories": [...],                          │
│      "keywords": {...},                            │
│      "exclusions": [...]                           │
│    }                                               │
│  }                                                 │
└────────────────────┬───────────────────────────────┘
                     │
                     │ (loaded at startup)
                     ▼
          ┌─────────────────────┐
          │  config.py          │
          │  get_config()       │
          └──────────┬──────────┘
                     │
           ┌─────────┼─────────┐
           │                   │
           ▼                   ▼
    ┌──────────┐        ┌──────────┐
    │Extractor │        │Classifier│
    │(uses     │        │(uses     │
    │calendars)│        │rules)    │
    └──────────┘        └──────────┘
```

## Deployment Model

```
┌─────────────────────────────────────────────────────┐
│  Claude Desktop Config                              │
│  ~/Library/Application Support/Claude/              │
│     claude_desktop_config.json                      │
│                                                     │
│  {                                                  │
│    "mcpServers": {                                  │
│      "calendar-mcp": {                              │
│        "command": "arch",                           │
│        "args": [                                    │
│          "-arm64",                                  │
│          "/Users/s/.../python",                     │
│          "-m", "calendar_mcp.server"                │
│        ]                                            │
│      }                                              │
│    }                                                │
│  }                                                  │
└────────────────────┬────────────────────────────────┘
                     │
                     │ (launches on Claude startup)
                     ▼
          ┌─────────────────────┐
          │  Calendar MCP       │
          │  (stdio mode)       │
          │  Listens for calls  │
          └─────────────────────┘
```

## Security Model

```
┌──────────────────────────────────────────────────────┐
│  Security Boundaries                                 │
│                                                      │
│  ┌────────────────┐                                 │
│  │  Calendar.app  │                                 │
│  │  (Protected)   │                                 │
│  └───────┬────────┘                                 │
│          │ ✅ Terminal has permission                │
│          ▼                                           │
│  ┌────────────────┐                                 │
│  │    Cache       │                                 │
│  │  (JSON file)   │                                 │
│  │  - World       │                                 │
│  │    readable    │                                 │
│  │  - No perms    │                                 │
│  │    needed      │                                 │
│  └───────┬────────┘                                 │
│          │ ✅ Anyone can read                        │
│          ▼                                           │
│  ┌────────────────┐                                 │
│  │  Claude/MCP    │                                 │
│  │  (No perms)    │                                 │
│  └────────────────┘                                 │
│                                                      │
│  All data stays local on your Mac!                  │
└──────────────────────────────────────────────────────┘
```

## Summary

This architecture solves the permissions problem by:

1. **Separating Concerns**: Terminal handles privileged operations
2. **Using Intermediate Storage**: Cache as permission boundary
3. **Enabling Automation**: Easy to schedule cache updates
4. **Maintaining Security**: All data stays local
5. **Being User-Friendly**: Clear tools and documentation

The trade-off (manual cache updates) is acceptable because:
- Calendar analysis is typically retrospective
- Cache updates are fast (< 5 seconds)
- Easy to automate (cron)
- User has full control







