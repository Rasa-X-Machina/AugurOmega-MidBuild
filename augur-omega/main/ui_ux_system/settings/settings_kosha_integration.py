"""
Augur Omega: Settings Integration for Koshas
Manages settings synchronization and integration across all koshas
"""
import json
import os
from typing import Dict, Any, List, Optional, Callable
from pathlib import Path
import logging
from dataclasses import dataclass
from enum import Enum


class SettingSyncStatus(Enum):
    """Status of setting synchronization"""
    SYNCED = "synced"
    PENDING = "pending"
    FAILED = "failed"
    OUT_OF_SYNC = "out_of_sync"


@dataclass
class SettingChange:
    """Represents a change to a setting"""
    kosha_id: str
    key: str
    old_value: Any
    new_value: Any
    timestamp: str
    applied: bool = False


class SettingsKoshaIntegration:
    """Manages settings integration across all koshas in the system"""
    
    def __init__(self, settings_dir: str = "settings", backup_dir: str = "settings/backups"):
        self.settings_dir = Path(settings_dir)
        self.backup_dir = Path(backup_dir)
        self.settings_dir.mkdir(exist_ok=True)
        self.backup_dir.mkdir(exist_ok=True)
        
        self.global_settings_file = self.settings_dir / "global_settings.json"
        self.kosha_settings_dir = self.settings_dir / "kosha_settings"
        self.kosha_settings_dir.mkdir(exist_ok=True)
        
        self.change_log_file = self.settings_dir / "change_log.json"
        
        # Initialize settings
        self.global_settings = self._load_global_settings()
        self.kosha_settings = self._load_all_kosha_settings()
        self.change_log = self._load_change_log()
        
        self.sync_callbacks: List[Callable] = []
    
    def _load_global_settings(self) -> Dict[str, Any]:
        """Load global settings from file or create defaults"""
        if self.global_settings_file.exists():
            try:
                with open(self.global_settings_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                logging.warning(f"Invalid JSON in {self.global_settings_file}, using defaults")
        
        # Default global settings
        default_settings = {
            "sync_enabled": True,
            "auto_backup": True,
            "backup_retention_days": 30,
            "global_theme": "dark",
            "performance_level": "high",
            "security_level": "high",
            "debug_mode": False
        }
        
        self._save_global_settings(default_settings)
        return default_settings
    
    def _save_global_settings(self, settings: Dict[str, Any]) -> None:
        """Save global settings to file"""
        with open(self.global_settings_file, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2)
    
    def _load_all_kosha_settings(self) -> Dict[str, Dict[str, Any]]:
        """Load settings for all koshas"""
        kosha_settings = {}
        
        for settings_file in self.kosha_settings_dir.glob("*.json"):
            kosha_id = settings_file.stem
            try:
                with open(settings_file, 'r', encoding='utf-8') as f:
                    kosha_settings[kosha_id] = json.load(f)
            except json.JSONDecodeError:
                logging.warning(f"Invalid JSON in {settings_file}, skipping")
                kosha_settings[kosha_id] = {}
        
        return kosha_settings
    
    def _load_change_log(self) -> List[SettingChange]:
        """Load the change log from file"""
        if self.change_log_file.exists():
            try:
                with open(self.change_log_file, 'r', encoding='utf-8') as f:
                    changes_data = json.load(f)
                # Convert to SettingChange objects
                return [
                    SettingChange(
                        kosha_id=change['kosha_id'],
                        key=change['key'],
                        old_value=change['old_value'],
                        new_value=change['new_value'],
                        timestamp=change['timestamp'],
                        applied=change.get('applied', False)
                    )
                    for change in changes_data
                ]
            except json.JSONDecodeError:
                logging.warning(f"Invalid JSON in {self.change_log_file}, starting fresh")
        
        return []
    
    def save_change_log(self) -> None:
        """Save the change log to file"""
        changes_data = [
            {
                'kosha_id': change.kosha_id,
                'key': change.key,
                'old_value': change.old_value,
                'new_value': change.new_value,
                'timestamp': change.timestamp,
                'applied': change.applied
            }
            for change in self.change_log
        ]
        
        with open(self.change_log_file, 'w', encoding='utf-8') as f:
            json.dump(changes_data, f, indent=2)
    
    def get_kosha_settings(self, kosha_id: str) -> Dict[str, Any]:
        """Get settings for a specific kosha"""
        if kosha_id not in self.kosha_settings:
            # Create default settings for new kosha
            self.kosha_settings[kosha_id] = self._create_default_kosha_settings(kosha_id)
            self._save_kosha_settings(kosha_id, self.kosha_settings[kosha_id])
        
        return self.kosha_settings[kosha_id]
    
    def _create_default_kosha_settings(self, kosha_id: str) -> Dict[str, Any]:
        """Create default settings for a new kosha"""
        return {
            "id": kosha_id,
            "enabled": True,
            "priority": 50,
            "theme": self.global_settings.get("global_theme", "dark"),
            "performance": self.global_settings.get("performance_level", "high"),
            "security": self.global_settings.get("security_level", "high"),
            "debug": self.global_settings.get("debug_mode", False),
            "custom_config": {}
        }
    
    def _save_kosha_settings(self, kosha_id: str, settings: Dict[str, Any]) -> None:
        """Save settings for a specific kosha"""
        settings_file = self.kosha_settings_dir / f"{kosha_id}.json"
        with open(settings_file, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2)
    
    def update_setting(self, kosha_id: str, key: str, value: Any) -> bool:
        """Update a setting for a specific kosha and log the change"""
        try:
            # Get current value before update
            current_settings = self.get_kosha_settings(kosha_id)
            keys = key.split('.')
            current_value = self._get_nested_value(current_settings, keys)
            
            # Update the setting
            self._set_nested_value(current_settings, keys, value)
            self.kosha_settings[kosha_id] = current_settings
            self._save_kosha_settings(kosha_id, current_settings)
            
            # Log the change
            from datetime import datetime
            change = SettingChange(
                kosha_id=kosha_id,
                key=key,
                old_value=current_value,
                new_value=value,
                timestamp=datetime.now().isoformat()
            )
            self.change_log.append(change)
            self.save_change_log()
            
            # Trigger sync if enabled
            if self.global_settings.get("sync_enabled", True):
                self.sync_settings(kosha_id, key)
            
            return True
        except Exception as e:
            logging.error(f"Error updating setting {key} for {kosha_id}: {str(e)}")
            return False
    
    def _get_nested_value(self, settings: Dict[str, Any], keys: List[str]) -> Any:
        """Get a value from nested settings using a list of keys"""
        current = settings
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        return current
    
    def _set_nested_value(self, settings: Dict[str, Any], keys: List[str], value: Any) -> None:
        """Set a value in nested settings using a list of keys"""
        current = settings
        for key in keys[:-1]:
            if key not in current or not isinstance(current[key], dict):
                current[key] = {}
            current = current[key]
        current[keys[-1]] = value
    
    def sync_settings(self, source_kosha: str = None, changed_key: str = None) -> Dict[str, SettingSyncStatus]:
        """Synchronize settings across all koshas based on global or source kosha settings"""
        sync_results = {}
        
        if source_kosha:
            # Sync from a specific source kosha to others
            source_settings = self.get_kosha_settings(source_kosha)
            for kosha_id in self.kosha_settings:
                if kosha_id != source_kosha:
                    if self._sync_kosha_to_source(kosha_id, source_settings, changed_key):
                        sync_results[kosha_id] = SettingSyncStatus.SYNCED
                    else:
                        sync_results[kosha_id] = SettingSyncStatus.FAILED
        else:
            # Apply global settings to all koshas
            for kosha_id in self.kosha_settings:
                if self._apply_global_settings_to_kosha(kosha_id):
                    sync_results[kosha_id] = SettingSyncStatus.SYNCED
                else:
                    sync_results[kosha_id] = SettingSyncStatus.FAILED
        
        # Trigger sync callbacks
        for callback in self.sync_callbacks:
            callback(sync_results, source_kosha, changed_key)
        
        return sync_results
    
    def _sync_kosha_to_source(self, target_kosha: str, source_settings: Dict[str, Any], changed_key: str = None) -> bool:
        """Sync a target kosha's settings to match the source settings"""
        try:
            target_settings = self.get_kosha_settings(target_kosha)
            
            if changed_key:
                # Only sync the changed key
                keys = changed_key.split('.')
                source_value = self._get_nested_value(source_settings, keys)
                if source_value is not None:
                    self._set_nested_value(target_settings, keys, source_value)
            else:
                # Sync all settings from source
                target_settings = self._merge_settings(target_settings, source_settings)
            
            # Save the updated settings
            self.kosha_settings[target_kosha] = target_settings
            self._save_kosha_settings(target_kosha, target_settings)
            
            return True
        except Exception as e:
            logging.error(f"Error syncing {target_kosha} to source: {str(e)}")
            return False
    
    def _apply_global_settings_to_kosha(self, kosha_id: str) -> bool:
        """Apply global settings to a specific kosha"""
        try:
            kosha_settings = self.get_kosha_settings(kosha_id)
            
            # Apply global settings to kosha settings
            for key, value in self.global_settings.items():
                if key in ['global_theme', 'performance_level', 'security_level', 'debug_mode']:
                    # Map global keys to kosha-specific keys
                    kosha_key = key.replace('global_', '')
                    kosha_settings[kosha_key] = value
            
            # Save the updated settings
            self.kosha_settings[kosha_id] = kosha_settings
            self._save_kosha_settings(kosha_id, kosha_settings)
            
            return True
        except Exception as e:
            logging.error(f"Error applying global settings to {kosha_id}: {str(e)}")
            return False
    
    def _merge_settings(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively merge two settings dictionaries"""
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_settings(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def add_sync_callback(self, callback: Callable) -> None:
        """Add a callback function to be called when settings are synchronized"""
        self.sync_callbacks.append(callback)
    
    def get_sync_status(self) -> Dict[str, SettingSyncStatus]:
        """Get synchronization status for all koshas"""
        # For this implementation, we'll consider all settings synced
        # In a real implementation, this would check for differences
        return {kosha_id: SettingSyncStatus.SYNCED for kosha_id in self.kosha_settings}
    
    def backup_settings(self) -> bool:
        """Create a backup of all settings"""
        try:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Backup global settings
            backup_global = self.backup_dir / f"global_settings_backup_{timestamp}.json"
            with open(backup_global, 'w') as f:
                json.dump(self.global_settings, f, indent=2)
            
            # Backup all kosha settings
            backup_koshas = self.backup_dir / f"kosha_settings_backup_{timestamp}"
            backup_koshas.mkdir(exist_ok=True)
            for kosha_id, settings in self.kosha_settings.items():
                backup_file = backup_koshas / f"{kosha_id}.json"
                with open(backup_file, 'w') as f:
                    json.dump(settings, f, indent=2)
            
            # Backup change log
            backup_log = self.backup_dir / f"change_log_backup_{timestamp}.json"
            with open(backup_log, 'w') as f:
                json.dump([{
                    'kosha_id': change.kosha_id,
                    'key': change.key,
                    'old_value': change.old_value,
                    'new_value': change.new_value,
                    'timestamp': change.timestamp,
                    'applied': change.applied
                } for change in self.change_log], f, indent=2)
            
            # Clean up old backups
            self.cleanup_old_backups()
            
            return True
        except Exception as e:
            logging.error(f"Error creating backup: {str(e)}")
            return False
    
    def cleanup_old_backups(self) -> None:
        """Remove backups older than retention period"""
        import time
        from datetime import datetime, timedelta
        
        retention_days = self.global_settings.get("backup_retention_days", 30)
        retention_period = timedelta(days=retention_days).total_seconds()
        
        current_time = time.time()
        
        # Clean up global settings backups
        for backup_file in self.backup_dir.glob("global_settings_backup_*.json"):
            file_time = backup_file.stat().st_mtime
            if current_time - file_time > retention_period:
                backup_file.unlink()
        
        # Clean up kosha settings backups
        for backup_dir in self.backup_dir.glob("kosha_settings_backup_*"):
            dir_time = backup_dir.stat().st_mtime
            if current_time - dir_time > retention_period:
                import shutil
                shutil.rmtree(backup_dir)
        
        # Clean up change log backups
        for backup_file in self.backup_dir.glob("change_log_backup_*.json"):
            file_time = backup_file.stat().st_mtime
            if current_time - file_time > retention_period:
                backup_file.unlink()
    
    def reset_kosha_settings(self, kosha_id: str) -> bool:
        """Reset a kosha's settings to defaults"""
        try:
            default_settings = self._create_default_kosha_settings(kosha_id)
            self.kosha_settings[kosha_id] = default_settings
            self._save_kosha_settings(kosha_id, default_settings)
            
            # Log the reset
            from datetime import datetime
            change = SettingChange(
                kosha_id=kosha_id,
                key="all_settings",
                old_value=self._get_nested_value(self.kosha_settings.get(kosha_id, {}), ["all"]),
                new_value=default_settings,
                timestamp=datetime.now().isoformat()
            )
            self.change_log.append(change)
            self.save_change_log()
            
            return True
        except Exception as e:
            logging.error(f"Error resetting settings for {kosha_id}: {str(e)}")
            return False


def demonstrate_settings_integration():
    """Demonstrate the settings integration system"""
    print("=== Augur Omega: Settings Integration for Koshas ===\n")
    
    # Initialize the settings integration system
    settings_integration = SettingsKoshaIntegration()
    
    # Add a sync callback for demonstration
    def sync_callback(sync_results, source_kosha, changed_key):
        print(f"Sync callback triggered: {sync_results} from {source_kosha} (changed key: {changed_key})")
    
    settings_integration.add_sync_callback(sync_callback)
    
    # Create some sample kosha IDs
    kosha_ids = [f"PRIME_{i:03d}" for i in range(1, 4)] + [f"DOMAIN_{i:03d}" for i in range(1, 4)]
    
    # Initialize settings for sample koshas
    print("Initializing settings for sample koshas:")
    for kosha_id in kosha_ids:
        settings = settings_integration.get_kosha_settings(kosha_id)
        print(f"  {kosha_id}: Theme={settings.get('theme')}, Performance={settings.get('performance')}")
    
    print(f"\nGlobal settings: {settings_integration.global_settings}")
    
    # Update a setting for one kosha (this will trigger sync if enabled)
    print(f"\nUpdating theme for {kosha_ids[0]} to 'light':")
    success = settings_integration.update_setting(kosha_ids[0], "theme", "light")
    print(f"  Update successful: {success}")
    
    new_settings = settings_integration.get_kosha_settings(kosha_ids[0])
    print(f"  New theme: {new_settings.get('theme')}")
    
    # Check sync status
    sync_status = settings_integration.get_sync_status()
    print(f"\nSync status: {sync_status}")
    
    # Perform a manual sync from the first kosha
    print(f"\nPerforming manual sync from {kosha_ids[0]}:")
    sync_results = settings_integration.sync_settings(source_kosha=kosha_ids[0], changed_key="theme")
    print(f"  Sync results: {sync_results}")
    
    # Check settings after sync
    print(f"\nSettings after sync:")
    for kosha_id in kosha_ids[:3]:  # Check first 3 koshas
        settings = settings_integration.get_kosha_settings(kosha_id)
        print(f"  {kosha_id}: Theme={settings.get('theme')}")
    
    # Create another change
    print(f"\nUpdating performance for {kosha_ids[1]} to 'medium':")
    success = settings_integration.update_setting(kosha_ids[1], "performance", "medium")
    print(f"  Update successful: {success}")
    
    # Perform global sync
    print(f"\nPerforming global sync:")
    global_sync_results = settings_integration.sync_settings()
    print(f"  Global sync results: {global_sync_results}")
    
    # Show change log
    print(f"\nRecent changes:")
    for change in settings_integration.change_log[-5:]:  # Show last 5 changes
        print(f"  {change.kosha_id}.{change.key}: {change.old_value} -> {change.new_value}")
    
    # Create backup
    print(f"\nCreating backup:")
    backup_success = settings_integration.backup_settings()
    print(f"  Backup successful: {backup_success}")
    
    print(f"\nSettings integration demonstration completed!")


if __name__ == "__main__":
    demonstrate_settings_integration()