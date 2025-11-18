# 🚨 Quick Fix: "No Events Found"

## The Problem

When you ask Claude about your calendar, it says "No events found."

## The Cause

icalBuddy doesn't have permission to access your calendars.

## The 3-Step Fix

### 1. Grant Calendar Permissions

**macOS System Settings → Privacy & Security → Calendars**

Enable for:
- ✅ Terminal (if testing from command line)
- ✅ Claude (if using Claude Desktop)

### 2. Restart the App

- For Claude: Cmd+Q then reopen
- For Terminal: Completely quit and reopen

### 3. Verify It Works

```bash
icalBuddy calendars
```

You should see your calendars listed. If you see "error: No calendars" - permissions didn't apply yet.

## Visual Guide

```
1. Open System Settings
   ↓
2. Click "Privacy & Security"
   ↓
3. Click "Calendars"
   ↓
4. Find "Claude" (or "Terminal")
   ↓
5. Toggle it ON ✅
   ↓
6. Completely restart Claude
   ↓
7. Try again!
```

## Test Commands

```bash
# Test 1: Can icalBuddy see calendars?
icalBuddy calendars

# Test 2: Can icalBuddy see events?
icalBuddy eventsToday

# Test 3: Run full diagnostic
cd /Users/s/dev/calendar-mcp
uv run python diagnose_calendar.py
```

## Still Not Working?

1. **Remove and re-add permissions**
   - Go to System Settings → Privacy → Calendars
   - Remove Claude/Terminal
   - Add it back
   - Restart

2. **Check you restarted properly**
   - Cmd+Q (not just close window)
   - Wait 10 seconds
   - Reopen

3. **Try Terminal first**
   - Grant permissions to Terminal
   - Run `icalBuddy calendars`
   - If this works, the issue is Claude-specific permissions

4. **Restart your Mac**
   - Sometimes macOS needs a full restart for permissions to apply

## For Claude Desktop Specifically

1. **Quit Claude completely** (Cmd+Q)
2. **Open System Settings**
3. **Privacy & Security → Calendars**
4. **Add Claude.app** (if not there, click + and navigate to Applications)
5. **Toggle Claude ON**
6. **Wait 30 seconds**
7. **Open Claude**
8. **Test**: Ask "what's on my calendar today?"

## Need More Help?

See the full guide: [CALENDAR_PERMISSIONS.md](./CALENDAR_PERMISSIONS.md)








