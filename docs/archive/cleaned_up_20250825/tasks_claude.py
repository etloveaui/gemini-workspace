#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Claude Code Invoke Tasks for Multi-Agent Workspace
Created: 2025-08-17

Extends the existing task system with Claude-specific tasks for seamless
integration into the Gemini + Codex workflow.
"""

from invoke import task, Collection
import os
import json
import sys
from pathlib import Path
from datetime import datetime

# Add workspace to path
WORKSPACE_ROOT = Path(__file__).parent
sys.path.insert(0, str(WORKSPACE_ROOT))

try:
    from scripts.claude_integration import ClaudeIntegration
except ImportError:
    print("Warning: Could not import claude_integration module")
    ClaudeIntegration = None

@task
def status(c):
    """Show Claude Code integration status"""
    print("🤖 Claude Code Integration Status")
    print("=" * 50)
    
    if ClaudeIntegration:
        integration = ClaudeIntegration()
        print(integration.get_context_summary())
    else:
        print("❌ Claude integration module not available")

@task
def setup(c):
    """Setup Claude Code integration"""
    print("⚙️ Setting up Claude Code integration...")
    
    if ClaudeIntegration:
        integration = ClaudeIntegration()
        
        # Set Claude as active agent
        integration.set_active_agent("claude")
        
        # Create necessary directories
        required_dirs = [
            ".agents",
            "agents_hub/queue", 
            "agents_hub/processing/claude",
            "agents_hub/archive",
            "terminal_logs"
        ]
        
        for dir_path in required_dirs:
            full_path = WORKSPACE_ROOT / dir_path
            full_path.mkdir(parents=True, exist_ok=True)
            print(f"📁 Ensured directory: {dir_path}")
        
        # Log session start
        integration.log_session_start()
        
        print("✅ Claude Code integration setup complete!")
    else:
        print("❌ Claude integration module not available")

@task
def activate(c):
    """Activate Claude as the current agent"""
    print("🎯 Activating Claude agent...")
    
    if ClaudeIntegration:
        integration = ClaudeIntegration()
        success = integration.set_active_agent("claude")
        if success:
            print("✅ Claude is now the active agent")
        else:
            print("❌ Failed to activate Claude agent")
    else:
        print("❌ Claude integration module not available")

@task
def deactivate(c):
    """Deactivate Claude and restore default agent"""
    print("🔄 Deactivating Claude agent...")
    
    if ClaudeIntegration:
        integration = ClaudeIntegration()
        success = integration.set_active_agent("gemini")  # Default back to Gemini
        if success:
            print("✅ Restored to default agent (Gemini)")
        else:
            print("❌ Failed to deactivate Claude agent")
    else:
        print("❌ Claude integration module not available")

@task
def message(c, to_agent, title, body, msg_type="info"):
    """Send a message to another agent
    
    Args:
        to_agent: Target agent (gemini, codex)
        title: Message title
        body: Message body
        msg_type: Message type (info, task, notification)
    """
    print(f"📤 Sending message to {to_agent}...")
    
    if ClaudeIntegration:
        integration = ClaudeIntegration()
        success = integration.send_hub_message(to_agent, title, body, msg_type)
        if success:
            print(f"✅ Message sent to {to_agent}")
        else:
            print(f"❌ Failed to send message to {to_agent}")
    else:
        print("❌ Claude integration module not available")

@task
def inbox(c):
    """Check Claude's inbox for messages"""
    print("📥 Checking Claude inbox...")
    
    # Check for messages in the queue directory
    queue_dir = WORKSPACE_ROOT / "agents_hub" / "queue"
    if not queue_dir.exists():
        print("📭 No messages (queue directory doesn't exist)")
        return
    
    claude_messages = []
    for file_path in queue_dir.glob("*.json"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                message = json.load(f)
                if message.get('to') == 'claude':
                    claude_messages.append((file_path, message))
        except Exception as e:
            print(f"⚠️ Could not read {file_path}: {e}")
    
    if claude_messages:
        print(f"📬 Found {len(claude_messages)} message(s) for Claude:")
        for file_path, message in claude_messages:
            print(f"  • From: {message.get('sender', 'unknown')}")
            print(f"    Title: {message.get('title', 'No title')}")
            print(f"    Created: {message.get('created_at', 'Unknown')}")
            print(f"    File: {file_path.name}")
            print()
    else:
        print("📭 No messages for Claude")

@task
def claim(c, message_id=None):
    """Claim a message from the queue
    
    Args:
        message_id: Specific message ID to claim (optional)
    """
    print("🏷️ Claiming message...")
    
    queue_dir = WORKSPACE_ROOT / "agents_hub" / "queue"
    processing_dir = WORKSPACE_ROOT / "agents_hub" / "processing" / "claude"
    processing_dir.mkdir(parents=True, exist_ok=True)
    
    if message_id:
        message_file = queue_dir / f"{message_id}.json"
        if not message_file.exists():
            print(f"❌ Message {message_id} not found")
            return
        message_files = [message_file]
    else:
        # Find all Claude messages
        message_files = []
        for file_path in queue_dir.glob("*.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    message = json.load(f)
                    if message.get('to') == 'claude':
                        message_files.append(file_path)
            except Exception:
                continue
    
    if not message_files:
        print("📭 No messages to claim")
        return
    
    for message_file in message_files:
        try:
            # Read message
            with open(message_file, 'r', encoding='utf-8') as f:
                message = json.load(f)
            
            # Update status
            message['status'] = 'processing'
            message['claimed_at'] = datetime.now().isoformat()
            
            # Move to processing
            new_path = processing_dir / message_file.name
            with open(new_path, 'w', encoding='utf-8') as f:
                json.dump(message, f, indent=2, ensure_ascii=False)
            
            # Remove from queue
            message_file.unlink()
            
            print(f"✅ Claimed message: {message.get('title', 'No title')}")
            
        except Exception as e:
            print(f"❌ Failed to claim {message_file.name}: {e}")

@task
def complete(c, message_id, status="success", result=""):
    """Complete a claimed message
    
    Args:
        message_id: Message ID to complete
        status: Completion status (success, failed)
        result: Completion result/notes
    """
    print(f"✅ Completing message {message_id}...")
    
    processing_dir = WORKSPACE_ROOT / "agents_hub" / "processing" / "claude"
    archive_dir = WORKSPACE_ROOT / "agents_hub" / "archive" / datetime.now().strftime('%Y%m%d') / status
    archive_dir.mkdir(parents=True, exist_ok=True)
    
    message_file = processing_dir / f"{message_id}.json"
    if not message_file.exists():
        print(f"❌ Message {message_id} not found in processing")
        return
    
    try:
        # Read message
        with open(message_file, 'r', encoding='utf-8') as f:
            message = json.load(f)
        
        # Update completion info
        message['status'] = status
        message['completed_at'] = datetime.now().isoformat()
        message['result'] = result
        
        # Move to archive
        archive_path = archive_dir / message_file.name
        with open(archive_path, 'w', encoding='utf-8') as f:
            json.dump(message, f, indent=2, ensure_ascii=False)
        
        # Remove from processing
        message_file.unlink()
        
        print(f"✅ Message completed with status: {status}")
        
    except Exception as e:
        print(f"❌ Failed to complete message: {e}")

@task
def sync_hub(c):
    """Sync with the HUB_ENHANCED.md file"""
    print("🔄 Syncing with HUB...")
    
    hub_file = WORKSPACE_ROOT / "docs" / "HUB_ENHANCED.md"
    if not hub_file.exists():
        print("❌ HUB_ENHANCED.md not found")
        return
    
    try:
        content = hub_file.read_text(encoding='utf-8')
        
        # Parse current active tasks
        lines = content.split('\n')
        active_tasks = []
        in_active = False
        
        for line in lines:
            if '## Active' in line or '## 진행 중인' in line:
                in_active = True
                continue
            elif line.startswith('##') and in_active:
                break
            elif in_active and line.strip().startswith('-'):
                active_tasks.append(line.strip())
        
        print(f"📋 Found {len(active_tasks)} active tasks")
        for task in active_tasks:
            if 'claude' in task.lower():
                print(f"  🎯 {task}")
            else:
                print(f"    {task}")
                
    except Exception as e:
        print(f"❌ Failed to sync HUB: {e}")

# Create Claude collection
claude = Collection('claude')
claude.add_task(status)
claude.add_task(setup) 
claude.add_task(activate)
claude.add_task(deactivate)
claude.add_task(message)
claude.add_task(inbox)
claude.add_task(claim)
claude.add_task(complete)
claude.add_task(sync_hub, 'sync-hub')

# Export for use in main tasks.py
__all__ = ['claude']