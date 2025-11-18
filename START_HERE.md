# 👋 Welcome to Calendar MCP!

> **An AI-powered calendar analysis assistant for Claude Desktop**

## 🎯 What Does This Do?

Ask Claude questions about your calendar, get detailed reports with:
- 📊 Time distribution by category (meetings, deep work, learning, etc.)
- 📈 Daily summaries and trends
- ⚡ Energy level tracking
- 📉 Beautiful charts and tables

## ⚡ Quick Start (5 Minutes)

### 1. Grant Permissions
```
System Settings → Privacy & Security → Calendars → Enable Terminal
```
Then **restart Terminal**.

### 2. Create Cache
```bash
cd /Users/s/dev/calendar-mcp
./update_calendar_cache.sh
```

### 3. Configure Claude
See **[QUICK_START.md](QUICK_START.md)** for Claude Desktop setup.

### 4. Ask Claude!
```
Analyze my calendar for last week
```

## 📚 Documentation

**New users**: Read [QUICK_START.md](QUICK_START.md)  
**Full index**: See [INDEX.md](INDEX.md)  
**Problems?**: Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

## 🔑 Key Insight

**Claude Desktop cannot access your calendar directly** due to macOS permissions.

**Solution**: You cache calendar data (from Terminal), Claude reads the cache.

```
You → Update Cache → Claude Analyzes → You Get Insights
    (1 command)      (automatically)   (amazing reports!)
```

## ✅ Verify Your Setup

```bash
./verify_setup.sh
```

This checks everything and tells you exactly what to fix.

## 🆘 Need Help?

1. Run `./verify_setup.sh` - Shows what's wrong
2. Read [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common fixes
3. Check logs: `tail -f ~/Library/Logs/Claude/mcp*.log`

## 📖 Complete Documentation

| Guide | What It Covers |
|-------|----------------|
| **[QUICK_START.md](QUICK_START.md)** | 5-minute setup |
| **[CACHE_SOLUTION.md](CACHE_SOLUTION.md)** | How the cache works |
| **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** | Fix common issues |
| **[SOLUTION_SUMMARY.md](SOLUTION_SUMMARY.md)** | Complete overview |
| **[INDEX.md](INDEX.md)** | All documentation |

## 🎉 That's It!

You're ready to analyze your calendar with AI.

**Next step**: [QUICK_START.md](QUICK_START.md) → Get started in 5 minutes!







