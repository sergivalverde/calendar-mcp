# Calendar Analysis MCP Server

> **🚀 New here? Start with [START_HERE.md](START_HERE.md) for a 5-minute quick start!**

An MCP (Model Context Protocol) server that acts as an executive assistant for calendar management. It can read calendar events, analyze them with productivity insights, and create new events through natural language commands.

## Features

- **📊 Calendar Analysis**: Analyze calendar events, classify them into productivity categories, track energy levels, and generate comprehensive markdown reports with tables and charts
- **📅 Event Creation**: Create calendar events using natural language commands
- **🔒 Direct Access**: Reads calendar data directly from macOS Calendar files (no external tools required)
- **🎯 Smart Scheduling**: Block time for focused work, propose meetings, find available slots
- **🔄 Real-time**: Always reads current calendar data, no caching delays
- **🤖 Natural Language**: Intuitive commands like "Block two mornings next week to work on the presentation"

**📚 Full Documentation**: See [INDEX.md](INDEX.md) for all guides and documentation.

## Installation

### Quick Start

1. **Prerequisites**:
   - Python 3.10+ (3.11 recommended)
   - [uv](https://github.com/astral-sh/uv): `curl -LsSf https://astral.sh/uv/install.sh | sh`

2. **Install**:
   ```bash
   cd calendar-mcp
   uv sync
   ```

3. **Grant Calendar Permissions** (for event creation):
   - Open **System Settings → Privacy & Security → Calendars**
   - Enable your MCP client (Raycast, Claude Desktop, etc.)
   - This allows creating events via AppleScript

4. **Configure MCP Client**:
   - Add the Calendar MCP to your MCP client
   - See [ADD_TO_CLAUDE.md](ADD_TO_CLAUDE.md) for Claude Desktop
   - See [RAYCAST_FIX.md](RAYCAST_FIX.md) for Raycast

5. **Test**:
   ```bash
   uv run python test_calendar_analysis.py
   ```

See detailed guides:
- [QUICK_START.md](QUICK_START.md) - Complete setup guide
- [INSTALL.md](INSTALL.md) - Detailed installation instructions
- [ADD_TO_CLAUDE.md](ADD_TO_CLAUDE.md) - Adding to Claude Desktop

## Usage

### Calendar Analysis

The MCP server provides tools for both reading and creating calendar events:

#### Reading Events
```python
# Analyze last week
"Analyze my calendar for last week"

# Check yesterday's energy levels
"What were my energy levels yesterday?"

# Monthly overview
"Show time distribution for November"

# Recent activity
"Analyze my calendar for the last 3 days"
```

#### Creating Events

**Block Time for Focused Work:**
```
"Block two mornings next week to work on the presentation"
```

**Schedule Meetings:**
```
"Propose a meeting with Joe in two weeks, afternoon preferred"
```

**Quick Event Creation:**
```
"Add 'Dentist appointment' tomorrow at 2pm for 1 hour"
```

#### Available Tools

- `query_calendar` - Analyze calendar events and generate productivity reports
- `create_event` - Create a single calendar event with specific date/time
- `create_blocking_time` - Block multiple time slots for focused work
- `propose_meeting` - Intelligently schedule meetings with attendee management
- `list_calendars` - Show available calendar names
- `find_free_time` - Find available time slots in your schedule

### Date Range Parsing

The server automatically parses date ranges from natural language:

- **Today**: "today", "this day"
- **Yesterday**: "yesterday"
- **This week**: "this week", "current week" (Monday to today)
- **Last week**: "last week", "previous week" (previous Monday to Sunday)
- **This month**: "this month", "current month" (1st to today)
- **Last month**: "last month", "previous month"
- **Last N days**: "last 7 days", "past 3 days"
- **Last N weeks**: "last 2 weeks"
- **Last N months**: "last 3 months"
- **Specific months**: "November", "last year November"
- **Default**: Last 7 days (if no date range detected)

## Calendar Access

The MCP server reads calendar data directly from macOS Calendar files and creates events via AppleScript.

### Reading Events

- **Direct Access**: Reads .ics files from `~/Library/Calendars/` (no external tools needed)
- **Real-time**: Always shows current calendar data
- **No Permissions Required**: Just file system access to your home directory

### Creating Events

- **AppleScript**: Uses macOS-native AppleScript to create events in Calendar.app
- **Permission Required**: Grant calendar access to your MCP client (Raycast, Claude Desktop, etc.)
- **One-time Setup**: Permissions only need to be granted once

### How Calendar Access Works

1. **Reading**: Direct file access to .ics files in your Calendars folder
2. **Writing**: AppleScript integration with Calendar.app
3. **Security**: Same permissions as Calendar.app itself
4. **Compatibility**: Works with any MCP client that can run AppleScript

### Checking Available Calendars

You can list your available calendars:

```bash
icalBuddy calendars
```

### Configuring Specific Calendars

Edit `src/calendar_mcp/config.json` to limit analysis to specific calendars:

```json
{
  "calendar": {
    "calendars": ["Work", "Personal Projects"]
  },
  "classification": {
    ...
  }
}
```

If `calendars` is `null` or omitted, all calendars are used.

## Event Classification Configuration

The server uses a `config.json` file for customizable classification rules. The file is located at `src/calendar_mcp/config.json`.

### Configuration Options

```json
{
  "calendar": {
    "calendars": null
  },
  "classification": {
    "excluded_titles": ["Blocked ✋", "Blocked", "Busy", "Tentative"],
    "personal_patterns": ["Helena", "Lunch - Helena"],
    "all_day_exclusion": true,
    "team_domains": ["tensormedical.ai"],
  "information_processing_keywords": ["email", "processing"],
  "recruiting_keywords": ["interview", "hiring"],
  "reading_keywords": ["reading", "anki", "study"],
  "team_keywords": ["1:1", "sync", "weekly"],
  "investor_relations_keywords": ["investment", "investor", "deck"],
  "strategy_keywords": ["strategy", "planning", "roadmap"],
  "sales_marketing_keywords": ["demo", "proposal", "pitch"],
  "engineering_keywords": ["review", "integration", "code"],
  "operations_keywords": ["audit", "legal", "HR"],
  "exercise_keywords": ["exercise", "workout", "run"],
  "meditation_keywords": ["meditation", "mindfulness"],
  "github_repos_engineering": ["research", "brain"],
  "github_repos_strategy": ["brain"]
}
```

### Customizing Classification

- **Team Domains**: Add your company domains to properly classify team meetings
- **Exclusion Patterns**: Add personal event titles or patterns to exclude
- **Category Keywords**: Customize keywords for each category
- **GitHub Repos**: Specify which repositories indicate engineering vs strategy work

## Event Classification

Events are classified into 13 categories using a priority-based system:

### Priority Order

1. **Explicit Category Match**: Event title matches category name
2. **External Clients**: Events with non-team attendees → Sales/Network
3. **Investors**: Investment/fundraising keywords → Investor Relations
4. **Recruiting**: Hiring/interview keywords → Recruiting
5. **Team Meetings**: @team-domain attendees → Team
6. **Technical Work**: Code/product keywords → Engineering
7. **GitHub Links**: Repository-based classification
8. **Strategy**: Planning/roadmap keywords → Strategy
9. **Other Categories**: Keyword matching for remaining categories

### Categories

- **Information Processing**: Email processing, communication tasks
- **Recruiting**: Interviews, hiring activities
- **Reading**: Study sessions, paper reading
- **Team**: Meetings with colleagues (@team-domain)
- **Investor Relations**: Fundraising, investor meetings
- **Strategy**: Long-term planning, roadmaps
- **Sales and Marketing**: Demos, proposals, client meetings
- **Network**: External connections, events
- **Engineering**: Code reviews, technical work
- **Operations**: Administrative, legal, HR tasks
- **Exercise**: Physical activities, workouts
- **Meditation**: Mindfulness activities
- **Other**: Unclassified productive work

## Energy Level Tracking

Energy levels are tracked using special "E" events that overlap with main events:

- **E1/L1**: Very low energy
- **E2/L2**: Low energy
- **E3/L3**: High energy
- **E4/L4**: Zone of Genius

Energy markers can include descriptive text: "E4 - this conversation was energizing"

## Report Format

The server generates comprehensive markdown reports with:

### 1. Raw Events Table
Shows all classified events with timing, category, and energy level.

### 2. Daily Summary Table
Top 3 categories per day with time spent and energy level percentages.

### 3. Category Distribution
Time breakdown by category with mermaid pie chart.

### 4. Energy Distribution
Time breakdown by energy level with mermaid pie chart.

## Output Formatting

- **Hours**: Decimal format with comma separator (1,5 not 1.5)
- **Dates**: dd/mm/yyyy format
- **Times**: HH:MM 24-hour format
- **Percentages**: Rounded to 1 decimal place
- **Charts**: Mermaid pie chart syntax

## Troubleshooting

### icalBuddy Issues

**Error**: `icalBuddy not found`
- Install icalBuddy: `brew install ical-buddy`

**No events found**
- Check Calendar app permissions
- Ensure calendars are enabled in icalBuddy
- Try running `icalBuddy eventsToday` manually

### Classification Issues

**Events in wrong category**
- Check `config.json` keyword lists
- Add custom keywords for your work patterns
- Update team domains if company email format changed

**Personal events included**
- Add exclusion patterns to `personal_patterns` in config
- Check `excluded_titles` list

### Configuration Issues

**Config not loading**
- Ensure `config.json` is valid JSON
- Check file permissions
- File is automatically created with defaults if missing

## Development

### Project Structure

```
calendar-mcp/
├── pyproject.toml          # uv configuration
├── src/calendar_mcp/
│   ├── __init__.py
│   ├── server.py           # MCP server
│   ├── models.py           # Data models
│   ├── calendar_extractor.py # icalBuddy integration
│   ├── classifier.py       # Event classification
│   ├── energy_tracker.py   # Energy level matching
│   ├── report_generator.py # Markdown report generation
│   ├── config.py           # Configuration management
│   └── config.json         # Default configuration
└── README.md
```

### Running Tests

```bash
uv run pytest
```

### Building

```bash
uv build
```

## License

This project is open source. See LICENSE file for details.
