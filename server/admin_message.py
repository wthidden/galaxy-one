"""
Admin Message System - Watches admin_message.txt for changes and broadcasts to players
"""

import asyncio
import os
from pathlib import Path


class AdminMessageWatcher:
    def __init__(self, message_file="admin_message.txt"):
        self.message_file = Path(message_file)
        self.last_modified = 0
        self.current_message = ""
        self.check_interval = 5  # Check every 5 seconds
        self.running = False

    def read_message(self):
        """Read the current admin message from file"""
        try:
            if self.message_file.exists():
                with open(self.message_file, 'r', encoding='utf-8') as f:
                    return f.read().strip()
            return ""
        except Exception as e:
            print(f"Error reading admin message: {e}")
            return ""

    def has_changed(self):
        """Check if the message file has been modified"""
        try:
            if not self.message_file.exists():
                return False

            stat = os.stat(self.message_file)
            modified_time = stat.st_mtime

            if modified_time > self.last_modified:
                self.last_modified = modified_time
                return True
            return False
        except Exception as e:
            print(f"Error checking file modification: {e}")
            return False

    async def watch(self, on_change_callback):
        """
        Watch the admin message file for changes.

        Args:
            on_change_callback: Async function to call when message changes
                               Should accept (new_message: str) as argument
        """
        self.running = True

        # Read initial message
        self.current_message = self.read_message()
        self.last_modified = os.stat(self.message_file).st_mtime if self.message_file.exists() else 0

        print(f"Admin message watcher started. Monitoring: {self.message_file}")

        while self.running:
            try:
                if self.has_changed():
                    new_message = self.read_message()
                    if new_message != self.current_message:
                        self.current_message = new_message
                        print(f"Admin message updated: {new_message[:50]}...")

                        # Call the callback with new message
                        await on_change_callback(new_message)

                # Wait before checking again
                await asyncio.sleep(self.check_interval)

            except Exception as e:
                print(f"Error in admin message watcher: {e}")
                await asyncio.sleep(self.check_interval)

    def stop(self):
        """Stop watching the file"""
        self.running = False
        print("Admin message watcher stopped")

    def get_current_message(self):
        """Get the current admin message"""
        return self.current_message


# Global instance
_admin_watcher = None

def get_admin_watcher():
    """Get the global admin message watcher instance"""
    global _admin_watcher
    if _admin_watcher is None:
        _admin_watcher = AdminMessageWatcher()
    return _admin_watcher
