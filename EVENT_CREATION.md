# 📅 Event Creation Guide

Learn how to create calendar events using natural language commands with the Calendar MCP.

## Overview

The Calendar MCP can create events in your macOS Calendar using intuitive natural language commands. It supports:

- **Block time** for focused work sessions
- **Schedule meetings** with intelligent time selection
- **Quick event creation** with specific dates and times
- **Automatic calendar selection** (configurable)

## Commands

### 1. Block Time for Focused Work

**Purpose**: Reserve time blocks for deep work, meetings, or specific activities.

**Examples:**
```
"Block two mornings next week to work on the presentation"
"Block afternoon tomorrow for client calls"
"Block 3 hours this morning for coding"
```

**What happens:**
- Parses the time slots ("mornings", "afternoons", "evenings")
- Calculates dates ("next week", "tomorrow", etc.)
- Creates multiple events across the specified dates
- Uses default duration (3 hours) or specified duration

**Configuration:**
- Default morning: 9:00-12:00
- Default afternoon: 14:00-17:00
- Default evening: 18:00-21:00
- Configurable in `src/calendar_mcp/config.json`

### 2. Schedule Meetings

**Purpose**: Intelligently propose meetings with attendee management.

**Examples:**
```
"Propose a meeting with Joe in two weeks, afternoon preferred"
"Schedule call with Sarah tomorrow morning"
"Set up 1-hour meeting with team next Monday"
```

**Features:**
- **Attendee parsing**: Recognizes "with [name]" patterns
- **Time preferences**: "morning", "afternoon", "evening"
- **Duration**: Defaults to 1 hour, can specify "30 minutes", "2 hours"
- **Date calculation**: "tomorrow", "next week", "in two weeks", "next Monday"

### 3. Quick Event Creation

**Purpose**: Create single events with specific details.

**Examples:**
```
"Add 'Dentist appointment' tomorrow at 2pm for 1 hour"
"Create 'Team meeting' on Friday at 10am"
"Schedule 'Doctor visit' next Tuesday at 3:30pm for 30 minutes"
```

**Supported formats:**
- Date: "tomorrow", "next Monday", "on Friday", specific dates
- Time: "at 2pm", "at 10am", "at 3:30pm"
- Duration: "for 1 hour", "for 30 minutes", "for 2 hours"

## Technical Implementation

### AppleScript Integration

Events are created using AppleScript to interact with Calendar.app:

```applescript
tell application "Calendar"
    tell calendar "Calendar"
        make new event with properties {
            summary:"Meeting Title",
            start date:date "11/25/2025 2:00:00 PM",
            end date:date "11/25/2025 3:00:00 PM"
        }
    end tell
end tell
```

### Permission Requirements

**For event creation:**
- Grant calendar access to your MCP client (Raycast/Claude Desktop)
- One-time permission grant in System Settings
- Permissions are per-application

**For reading events:**
- No permissions required (file system access)

### Calendar Selection

- **Default**: Uses calendar specified in config (`default_calendar`)
- **Auto-detection**: Lists available calendars via `list_calendars` tool
- **Manual**: Can specify calendar in natural language (future feature)

## MCP Tools

### create_event

**Purpose**: Create a single event with full control

**Parameters:**
- `title` (required): Event title
- `start_date`: YYYY-MM-DD
- `start_time`: HH:MM
- `end_date`: YYYY-MM-DD (optional, defaults to start_date)
- `end_time`: HH:MM (optional, defaults to start_time + 1 hour)
- `calendar`: Calendar name (optional)
- `location`: Event location (optional)
- `notes`: Event description (optional)

### create_blocking_time

**Purpose**: Block multiple time slots for focused work

**Parameters:**
- `purpose`: What the blocked time is for
- `time_slots`: "mornings", "afternoons", "evenings"
- `dates`: Date range description ("next week", "tomorrow", etc.)
- `duration_hours`: Hours per session (default: 3)

### propose_meeting

**Purpose**: Intelligent meeting scheduling

**Parameters:**
- `title`: Meeting title
- `attendees`: Comma-separated attendee names
- `relative_date`: When ("tomorrow", "next week", "in two weeks")
- `time_preference`: "morning", "afternoon", "evening"
- `duration_minutes`: Meeting length in minutes

### find_free_time

**Purpose**: Find available time slots

**Parameters:**
- `start_date`: Search start date
- `end_date`: Search end date
- `duration_minutes`: Required slot length
- `time_preference`: Preferred time of day

## Configuration

### Event Creation Settings

Edit `src/calendar_mcp/config.json`:

```json
{
  "calendar": {
    "default_calendar": "Calendar",
    "event_creation": {
      "default_duration_minutes": 60,
      "default_morning_start": "09:00",
      "default_afternoon_start": "14:00",
      "default_evening_start": "18:00",
      "work_hours_start": "09:00",
      "work_hours_end": "17:00"
    }
  }
}
```

### Natural Language Patterns

The system recognizes these patterns:

**Time slots:**
- Morning: 9:00-12:00 (configurable)
- Afternoon: 14:00-17:00 (configurable)
- Evening: 18:00-21:00 (configurable)

**Relative dates:**
- "tomorrow", "today"
- "next week", "in two weeks"
- "next Monday", "this Friday"
- Month names: "November", "next December"

**Durations:**
- "for 1 hour", "for 30 minutes"
- "2 hours", "45 minutes"

## Examples

### Blocking Time

**Input:** "Block two mornings next week to work on the Q4 presentation"

**Process:**
1. Parse: 2 sessions, mornings, next week, purpose="Q4 presentation"
2. Calculate dates: Next Monday + Tuesday
3. Create events: 9:00-12:00 on both days
4. Result: Two "Blocked: Q4 presentation" events

### Meeting Scheduling

**Input:** "Propose a meeting with Julia in two weeks, afternoon preferred"

**Process:**
1. Parse: Meeting with Julia, 2 weeks from now, afternoon, 1 hour
2. Calculate date: Today + 14 days
3. Find afternoon slot: 2:00-3:00 PM
4. Create event: "Meeting with Julia" at calculated time
5. Result: Meeting scheduled

### Quick Events

**Input:** "Add dentist appointment tomorrow at 2pm for 1 hour"

**Process:**
1. Parse: Title="dentist appointment", tomorrow at 14:00, 1 hour
2. Calculate date/time: Tomorrow 14:00-15:00
3. Create event in default calendar
4. Result: Event created

## Error Handling

### Permission Issues

**Error:** "Failed to create event: AppleScript permission denied"

**Solution:**
1. System Settings → Privacy & Security → Calendars
2. Grant access to your MCP client
3. Restart the MCP client
4. Try again

### Invalid Dates

**Error:** "Could not parse date/time from request"

**Solution:** Use clearer date/time formats:
- "tomorrow at 2pm" ✅
- "next week morning" ✅
- "sometime this week" ❌ (too vague)

### Calendar Not Found

**Error:** "Calendar 'Work' not found"

**Solution:**
1. Use `list_calendars` tool to see available calendars
2. Check spelling in request
3. Update default calendar in config

## Advanced Features

### Recurring Events

**Future feature:** Support for recurring event creation
- "Block mornings every weekday for the next month"
- "Schedule weekly team meeting every Monday at 10am"

### Attendee Management

**Future feature:** Enhanced attendee handling
- Email address validation
- Attendee availability checking
- Meeting invitation sending

### Smart Scheduling

**Future feature:** AI-powered scheduling
- Conflict detection
- Optimal time suggestions
- Attendee preference learning

## Troubleshooting

### Events Don't Appear

**Check:**
1. Calendar permissions granted to MCP client
2. Default calendar exists and is accessible
3. MCP client restarted after permission grant

### Wrong Calendar

**Solution:**
- Check `default_calendar` in config.json
- Use `list_calendars` tool to verify available calendars
- Specify calendar explicitly in requests (future feature)

### Time Zone Issues

**Note:** All times are interpreted in your system time zone. AppleScript uses macOS system time zone settings.

### Parsing Errors

**Tip:** Be specific with dates and times:
- ✅ "tomorrow at 2pm"
- ✅ "next Monday morning"
- ❌ "sometime next week"

## Integration with Analysis

Event creation works seamlessly with calendar analysis:

1. **Create events** using natural language
2. **Analyze calendar** to see time distribution
3. **Adjust** based on insights
4. **Repeat** for continuous optimization

## Security & Privacy

- **Local processing**: All data stays on your Mac
- **No uploads**: Events are created locally in Calendar.app
- **Permission-based**: Only accesses calendars you explicitly allow
- **Audit trail**: All events appear in Calendar.app with full visibility

## Future Enhancements

- **Conflict detection**: Warn about overlapping events
- **Smart suggestions**: Learn your preferences and suggest optimal times
- **Bulk operations**: Create multiple related events at once
- **Calendar sync**: Work with multiple calendar accounts
- **Reminder integration**: Set up notifications and reminders

---

**Try it now:** "Block two mornings next week to work on this documentation"






