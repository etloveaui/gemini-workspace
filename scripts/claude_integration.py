#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Claude Code Integration for Multi-Agent Workspace
Created: 2025-08-17

This module provides integration utilities for Claude Code to work seamlessly
within the Multi-Agent Workspace environment alongside Gemini and Codex.
"""

import os
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Add the workspace root to Python path
WORKSPACE_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(WORKSPACE_ROOT))
try:
    from scripts.usage_logging import record_event  # when executed as module
except Exception:
    try:
        from usage_logging import record_event  # when executed as script
    except Exception:
        def record_event(*args, **kwargs):
            pass

class ClaudeIntegration:
    """Claude Code integration utilities for the Multi-Agent Workspace"""
    
    def __init__(self):
        self.workspace_root = WORKSPACE_ROOT
        self.agent_name = "claude"
        self.active_agent_config = self.workspace_root / ".agents" / "config.json"
        
    def get_active_agent(self) -> str:
        """Get the currently active agent from config"""
        try:
            if self.active_agent_config.exists():
                with open(self.active_agent_config, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    return config.get('active', 'gemini')
        except Exception as e:
            print(f"Warning: Could not read agent config: {e}")
        return 'gemini'  # Default fallback
    
    def set_active_agent(self, agent_name: str = "claude") -> bool:
        """Set Claude as the active agent"""
        try:
            # Ensure .agents directory exists
            self.active_agent_config.parent.mkdir(exist_ok=True)
            
            config = {"active": agent_name}
            with open(self.active_agent_config, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
            
            print(f"Active agent set to: {agent_name}")
            return True
        except Exception as e:
            print(f"Failed to set active agent: {e}")
            return False
    
    def check_hub_status(self) -> Dict[str, Any]:
        """Check the current HUB status and active tasks"""
        hub_file = self.workspace_root / "docs" / "HUB_ENHANCED.md"
        
        status = {
            "hub_exists": hub_file.exists(),
            "active_tasks": [],
            "claude_tasks": [],
            "last_updated": None
        }
        
        if hub_file.exists():
            try:
                content = hub_file.read_text(encoding='utf-8')
                status["last_updated"] = datetime.now().isoformat()
                
                # Parse active tasks (simplified)
                lines = content.split('\n')
                in_active_section = False
                
                for line in lines:
                    if '## Active Tasks' in line or '## 진행 중인 작업' in line:
                        in_active_section = True
                        continue
                    elif line.startswith('##') and in_active_section:
                        break
                    elif in_active_section and line.strip().startswith('-'):
                        task = line.strip()
                        status["active_tasks"].append(task)
                        if 'claude' in task.lower():
                            status["claude_tasks"].append(task)
                            
            except Exception as e:
                print(f"Warning: Could not parse HUB_ENHANCED.md: {e}")
        
        return status
    
    def send_hub_message(self, to_agent: str, title: str, body: str, 
                        message_type: str = "info") -> bool:
        """Send a message to another agent via the hub system"""
        try:
            # This would integrate with the existing hub system
            # For now, create a simple message in the queue
            queue_dir = self.workspace_root / "agents_hub" / "queue"
            queue_dir.mkdir(parents=True, exist_ok=True)
            
            message_id = f"claude_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            message = {
                "id": message_id,
                "sender": "claude",
                "to": to_agent,
                "title": title,
                "body": body,
                "tags": [message_type],
                "status": "queued",
                "created_at": datetime.now().isoformat()
            }
            
            message_file = queue_dir / f"{message_id}.json"
            with open(message_file, 'w', encoding='utf-8') as f:
                json.dump(message, f, indent=2, ensure_ascii=False)
            
            print(f"Message sent to {to_agent}: {title}")
            return True
            
        except Exception as e:
            print(f"Failed to send hub message: {e}")
            return False
    
    def log_session_start(self) -> None:
        """Log Claude session start"""
        try:
            # Create session log entry
            terminal_logs_dir = self.workspace_root / "terminal_logs" / datetime.now().strftime('%Y-%m-%d')
            terminal_logs_dir.mkdir(parents=True, exist_ok=True)
            
            session_info = {
                "agent": "claude",
                "session_start": datetime.now().isoformat(),
                "workspace_root": str(self.workspace_root),
                "claude_integration_version": "1.0"
            }
            
            session_file = terminal_logs_dir / f"claude_session_{datetime.now().strftime('%H%M%S')}.json"
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session_info, f, indent=2, ensure_ascii=False)
                
            print(f"Claude session logged: {session_file}")
            
        except Exception as e:
            print(f"Warning: Could not log session: {e}")
    
    def get_context_summary(self) -> str:
        """Get a summary of the current workspace context"""
        try:
            context_files = []
            
            # Check key context files
            key_files = [
                "docs/CORE/HUB_ENHANCED.md",
                "README.md", 
                "GEMINI.md",
                ".agents/config.json"
            ]
            
            for file_path in key_files:
                full_path = self.workspace_root / file_path
                if full_path.exists():
                    context_files.append(f"[OK] {file_path}")
                else:
                    context_files.append(f"[MISSING] {file_path}")
            
            # Check active agent
            active_agent = self.get_active_agent()
            hub_status = self.check_hub_status()
            
            summary = f"""
Multi-Agent Workspace Status

Workspace: {self.workspace_root}
Active Agent: {active_agent}
Active Tasks: {len(hub_status['active_tasks'])}
Claude Tasks: {len(hub_status['claude_tasks'])}

Key Files:
{chr(10).join(context_files)}

Ready for Claude Code integration!
"""
            return summary.strip()
            
        except Exception as e:
            return f"Error generating context summary: {e}"

def main():
    """Main function for testing Claude integration"""
    print("Claude Code Integration Test")
    print("=" * 50)

    integration = ClaudeIntegration()
    # Log start
    record_event(task_name="claude_integration", event_type="start", command="claude_integration.main")
    
    # Test integration features
    print("\n1. Setting Claude as active agent...")
    integration.set_active_agent("claude")
    
    print("\n2. Checking HUB status...")
    hub_status = integration.check_hub_status()
    print(f"   Hub exists: {hub_status['hub_exists']}")
    print(f"   Active tasks: {len(hub_status['active_tasks'])}")
    
    print("\n3. Logging session start...")
    integration.log_session_start()
    
    print("\n4. Context Summary:")
    print(integration.get_context_summary())
    
    print("\n5. Test message to Gemini...")
    integration.send_hub_message(
        to_agent="gemini",
        title="Claude Integration Complete",
        body="Claude Code has been successfully integrated into the Multi-Agent Workspace. Ready for collaboration!",
        message_type="notification"
    )
    
    print("\nClaude integration test completed!")
    # Log complete
    record_event(task_name="claude_integration", event_type="complete", command="claude_integration.main")

if __name__ == "__main__":
    main()
