# 🤖 Claude Code Integration Guide

## Overview

Claude Code has been successfully integrated into the Multi-Agent Workspace (Gemini + Codex + Claude) system. This document provides a comprehensive guide for using Claude Code within the existing workflow.

## 🏗️ Architecture Integration

### Multi-Agent System Structure
```
Multi-Agent Workspace
├── Gemini (General conversation & planning)
├── Codex (Code generation & modification) 
└── Claude (Analysis, documentation & complex reasoning)
```

### File-Based Messaging System
- **Queue**: `agents_hub/queue/` - New messages
- **Processing**: `agents_hub/processing/claude/` - Messages being handled
- **Archive**: `agents_hub/archive/YYYYMMDD/` - Completed messages

### Context Management
- **HUB**: `docs/CORE/HUB_ENHANCED.md` - Central task coordination
- **Messages**: `context/messages.jsonl` - Cross-agent communication  
- **Logs**: `terminal_logs/` - Session recordings

## 🚀 Quick Start

### 1. Initial Setup
```powershell
# Run setup script
.\claude.ps1 -Setup

# Or use Invoke tasks
invoke claude.setup
```

### 2. Check Integration Status
```powershell
# PowerShell method
.\claude.ps1 -Status

# Invoke method  
invoke claude.status
```

### 3. Activate Claude Agent
```powershell
# Set Claude as active agent
invoke claude.activate

# Check current agent
invoke agent.status
```

## 🔧 Available Commands

### PowerShell Interface (`claude.ps1`)
```powershell
# Claude Code commands (future integration)
.\claude.ps1 /think "Analyze this codebase structure"
.\claude.ps1 /code "Implement error handling" 
.\claude.ps1 /long "Write comprehensive documentation"
.\claude.ps1 /fast "Quick code review"

# Management commands
.\claude.ps1 -Status    # Show integration status
.\claude.ps1 -Setup     # Run initial setup  
.\claude.ps1 -Test      # Test integration
.\claude.ps1 -Help      # Show help
```

### Invoke Tasks (`invoke claude.*`)
```bash
# Agent management
invoke claude.activate      # Set Claude as active agent
invoke claude.deactivate    # Restore default agent  
invoke claude.status        # Show integration status

# Message system
invoke claude.inbox         # Check messages for Claude
invoke claude.claim         # Claim a message from queue
invoke claude.complete MSG_ID --status=success --result="Done"
invoke claude.message gemini "Task Complete" "Analysis finished"

# Hub integration  
invoke claude.sync-hub      # Sync with HUB_ENHANCED.md
```

## 📨 Inter-Agent Communication

### Sending Messages
```python
# Send task to Gemini
invoke claude.message gemini "Code Review Request" "Please review the new authentication module" --msg-type=task

# Send notification to Codex
invoke claude.message codex "Bug Fix Complete" "Fixed the memory leak in parser.py" --msg-type=notification
```

### Receiving Messages
```python
# Check inbox
invoke claude.inbox

# Claim messages  
invoke claude.claim

# Complete work
invoke claude.complete MSG_ID --status=success --result="Analysis complete"
```

## 🔄 Workflow Integration

### 1. Session Management
```python
# Start Claude session (auto-logged)
invoke claude.activate

# Work on tasks...

# End session
invoke claude.deactivate
```

### 2. Task Coordination via HUB_ENHANCED.md
```markdown
## Active Tasks

- [Claude] Document API integration patterns - Due: 2025-08-20
- [Gemini] Plan database migration - Due: 2025-08-18  
- [Codex] Implement user authentication - Due: 2025-08-19
```

### 3. Context Sharing
- All agents share `context/messages.jsonl` for cross-reference
- Context policies in `.gemini/context_policy.yaml` control information access
- Session logs in `terminal_logs/` provide complete audit trail

## 📁 File Structure

```
multi-agent-workspace/
├── CLAUDE.md                    # Claude-specific guidelines
├── claude.ps1                   # PowerShell integration script
├── tasks_claude.py              # Invoke task definitions
├── scripts/
│   └── claude_integration.py    # Core integration utilities
├── .agents/
│   └── config.json             # Active agent configuration
├── agents_hub/                 # Message queue system
│   ├── queue/                  # New messages
│   ├── processing/claude/      # Claude's active messages  
│   └── archive/                # Completed messages
├── docs/
│   └── HUB_ENHANCED.md                  # Central coordination hub
├── terminal_logs/              # Session recordings
└── context/
    └── messages.jsonl          # Cross-agent messages
```

## 🛠️ Advanced Features

### 1. Automatic Session Recording
- Set `$env:AI_REC_AUTO=1` for automatic transcript logging
- Sessions saved to `terminal_logs/YYYY-MM-DD/claude_session_*.txt`
- Includes full command history and output

### 2. Context Policy Integration
```yaml
# .gemini/context_policy.yaml
claude_analysis:
  sources:
    - doc_tag: "active_tasks"
    - file_pattern: "docs/CORE/HUB_ENHANCED.md"
  max_tokens: 4000
  summary_threshold: 2000
```

### 3. Usage Tracking
- All Claude activities logged to `usage.db` SQLite database
- Integration with existing usage tracking system
- Analytics via `scripts/usage_tracker.py`

## 🔍 Troubleshooting

### Common Issues

1. **Agent Not Switching**
   ```powershell
   # Force reset agent config
   invoke claude.activate
   invoke agent.status
   ```

2. **Messages Not Appearing**
   ```powershell
   # Check queue permissions
   invoke claude.inbox
   ls agents_hub/queue/
   ```

3. **Integration Test Fails**
   ```powershell
   # Run comprehensive test
   .\claude.ps1 -Test
   python scripts/claude_integration.py
   ```

### Environment Variables
```powershell
$env:ACTIVE_AGENT = "claude"           # Current agent
$env:PYTHONIOENCODING = "utf-8"        # Encoding fix
$env:AI_REC_AUTO = "1"                 # Auto-recording
```

## 📈 Best Practices

### 1. Agent Coordination
- Always check `docs/CORE/HUB_ENHANCED.md` before starting major tasks
- Use message system for cross-agent communication
- Update task status in HUB when work is complete

### 2. Session Management  
- Activate Claude agent at session start
- Use descriptive commit messages referencing agent work
- Deactivate when switching to other agents

### 3. Documentation
- Update `docs/CORE/HUB_ENHANCED.md` with Claude-specific tasks
- Log complex analyses in `docs/tasks/*/log.md`
- Use meaningful message titles in agent communication

## 🔗 Integration Points

### With Existing Systems
- **Gemini**: Strategic planning and user interaction
- **Codex**: Code implementation and debugging  
- **PowerShell**: Windows environment optimization
- **Invoke**: Task automation and workflow management
- **Git**: Version control with agent attribution

### Future Enhancements
- Direct Claude Code CLI integration
- Enhanced context sharing protocols
- Automated task distribution based on agent strengths
- Real-time collaboration dashboards

---

💡 **Ready to collaborate!** Claude Code is now fully integrated and ready to work alongside Gemini and Codex in your Multi-Agent Workspace.