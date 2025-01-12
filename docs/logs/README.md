# Logs Directory Structure

This directory contains all logs for the RogueAsteroid project, organized by type and purpose.

## Directory Structure

- `/runtime/` - Contains game runtime logs
  - Performance metrics
  - Game state changes
  - User interactions
  - System events

- `/debug/` - Contains debug and development logs
  - Error traces
  - Debug output
  - Development diagnostics
  - Test results

- `/archive/` - Contains historical log files
  - Old development logs
  - Historical records
  - Archived documentation

## Log Format Standards

1. Runtime Logs:
   - Filename format: `game_log_YYYYMMDD_HHMMSS.log`
   - Contains timestamped entries
   - JSON-formatted for easy parsing

2. Debug Logs:
   - Filename format: `debug_YYYYMMDD_HHMMSS.log`
   - Detailed error information
   - Stack traces when available

3. Archive:
   - Original filenames preserved
   - Moved here when no longer actively referenced

## Retention Policy

- Runtime logs: 30 days
- Debug logs: 7 days
- Archive: Indefinite (cleared during major versions) 