# 📚 Calendar MCP Documentation Index

Quick navigation to all documentation files.

## 🚀 Getting Started

Start here if you're new:

1. **[QUICK_START.md](QUICK_START.md)** ⭐  
   Get up and running in 5 minutes

2. **[SOLUTION_SUMMARY.md](SOLUTION_SUMMARY.md)**  
   Understand the cache-based approach

3. **[verify_setup.sh](verify_setup.sh)**  
   Check if everything is configured correctly

## 📖 Main Documentation

- **[README.md](README.md)**  
  Complete project documentation, features, architecture

- **[CACHE_SOLUTION.md](CACHE_SOLUTION.md)**  
  Deep dive into the calendar cache system (why Claude can't access calendars directly)

## 🔧 Setup & Configuration

- **[INSTALL.md](INSTALL.md)**  
  Detailed installation instructions

- **[CLAUDE_SETUP.md](CLAUDE_SETUP.md)**  
  How to configure Claude Desktop to use the MCP

## 🆘 Help & Troubleshooting

- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)**  
  Common problems and solutions

- **[WORKING_SOLUTION.md](WORKING_SOLUTION.md)**  
  Complete debugging history and technical details

## 🛠️ Tools & Scripts

### Main Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `update_calendar_cache.sh` | Update calendar cache | `./update_calendar_cache.sh` |
| `verify_setup.sh` | Check system status | `./verify_setup.sh` |
| `diagnose_calendar.py` | Diagnose calendar access | `uv run python diagnose_calendar.py` |
| `test_calendar_analysis.py` | Test core functionality | `uv run python test_calendar_analysis.py` |

### Configuration Files

| File | Purpose |
|------|---------|
| `src/calendar_mcp/config.json` | Category rules, exclusions, calendars |
| `pyproject.toml` | Python dependencies and project config |
| `claude_desktop_config.json` | Claude Desktop MCP configuration |

## 📊 Project Structure

```
calendar-mcp/
├── src/calendar_mcp/          # Main source code
│   ├── server.py              # MCP server
│   ├── calendar_extractor.py  # icalBuddy integration
│   ├── cache_calendar.py      # Cache system
│   ├── classifier.py          # Event classification
│   ├── energy_tracker.py      # Energy level tracking
│   ├── report_generator.py    # Report generation
│   ├── models.py              # Data models
│   └── config.py              # Configuration management
│
├── docs/                      # Documentation (this folder!)
│   ├── QUICK_START.md
│   ├── CACHE_SOLUTION.md
│   ├── TROUBLESHOOTING.md
│   └── ...
│
├── scripts/                   # Utility scripts
│   ├── update_calendar_cache.sh
│   ├── verify_setup.sh
│   └── diagnose_calendar.py
│
└── tests/
    └── test_calendar_analysis.py
```

## 🎯 Common Tasks

### First Time Setup
1. Read [QUICK_START.md](QUICK_START.md)
2. Run `./verify_setup.sh`
3. Follow instructions to fix any issues

### Daily Usage
1. Update cache: `./update_calendar_cache.sh`
2. Ask Claude: "Analyze my calendar for last week"

### When Something Breaks
1. Run `./verify_setup.sh` to see what's wrong
2. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
3. Review logs: `tail -f ~/Library/Logs/Claude/mcp*.log`

### Customization
1. Edit `src/calendar_mcp/config.json` for categories
2. Restart Claude to apply changes

## 🔑 Key Concepts

### The Cache Approach

**Problem**: Claude Desktop can't get calendar permissions  
**Solution**: Terminal caches calendar data → Claude reads cache

```
Terminal (with perms) → icalBuddy → Cache File → Claude MCP → Reports
```

### Event Classification

Events are automatically categorized into:
- 🤝 Team Meetings
- 💻 Deep Work  
- 🚀 Client Work
- 📚 Learning
- And 9 more categories...

See [calendar_tasks_needed.md](calendar_tasks_needed.md) for full list.

### Energy Tracking

Special events like "E2" or "L3" mark your energy level:
- E1-E4: Energy levels (high to low)
- L1-L4: Energy loss levels

The system matches these to your main events for insights.

## 📝 Specifications

- **[calendar_tasks_needed.md](calendar_tasks_needed.md)**  
  Original requirements and specifications

## 🔍 Quick Reference

### Update Cache
```bash
cd /Users/s/dev/calendar-mcp
./update_calendar_cache.sh
```

### Check Status
```bash
./verify_setup.sh
```

### Test MCP
```bash
uv run python -m calendar_mcp.server
```

### View Cache
```bash
cat ~/.calendar-mcp-cache/calendar_events.json | jq .
```

### Configure Claude
```bash
nano ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

### Example Questions
```
Analyze my calendar for last week
What were my energy levels yesterday?
Show time distribution for November
How much time did I spend on meetings?
```

## 🎓 Learning Path

### Beginner
1. QUICK_START.md - Get it working
2. SOLUTION_SUMMARY.md - Understand why
3. Use it with Claude!

### Intermediate
1. CACHE_SOLUTION.md - Deep dive on cache
2. Edit config.json - Customize categories
3. Set up automation - Cron jobs

### Advanced
1. WORKING_SOLUTION.md - Technical details
2. Read source code - Understand implementation
3. Extend functionality - Add your features

## 💡 Tips

- **Update cache regularly**: Set up daily cron job
- **Check cache age**: Before important Claude sessions
- **Customize categories**: Edit config.json for your workflow
- **Use energy markers**: Add E1-E4 events to track productivity
- **Verify setup**: Run `./verify_setup.sh` after system changes

## 🔗 External Resources

- [MCP Documentation](https://modelcontextprotocol.io/)
- [icalBuddy Homepage](https://github.com/DavidKaluta/icalBuddy)
- [uv Documentation](https://github.com/astral-sh/uv)

---

**Need help?** Start with [TROUBLESHOOTING.md](TROUBLESHOOTING.md) or run `./verify_setup.sh`







