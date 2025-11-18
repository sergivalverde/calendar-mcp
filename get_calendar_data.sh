#!/bin/bash
# Calendar data retrieval script
# This runs in the proper shell environment to access calendar data

set -e  # Exit on error

# Function to get calendars
get_calendars() {
    output=$(icalBuddy calendars 2>&1)
    if [ $? -eq 0 ] && [ -n "$output" ]; then
        echo "$output"
    else
        echo "Error: Cannot access calendars" >&2
        exit 1
    fi
}

# Function to get events for date range
get_events() {
    local start_date=$1
    local end_date=$2

    # Use icalBuddy with proper formatting
    output=$(icalBuddy \
        -nc \
        -iep "title,datetime,location,notes,attendees" \
        -df "%Y-%m-%d %H:%M:%S" \
        -tf "%H:%M" \
        "eventsFrom:${start_date}" \
        "to:${end_date}" \
        2>&1)

    if [ $? -eq 0 ] && [ -n "$output" ]; then
        echo "$output"
    else
        echo "Error: Cannot retrieve events" >&2
        exit 1
    fi
}

# Main logic
case "$1" in
    "calendars")
        get_calendars
        ;;
    "events")
        if [ $# -ne 3 ]; then
            echo "Usage: $0 events <start_date> <end_date>"
            echo "Date format: YYYY-MM-DD"
            exit 1
        fi
        get_events "$2" "$3"
        ;;
    *)
        echo "Usage: $0 {calendars|events}"
        echo "  calendars - list available calendars"
        echo "  events <start> <end> - get events between dates"
        exit 1
        ;;
esac
