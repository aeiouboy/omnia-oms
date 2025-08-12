#!/usr/bin/env python3
"""
Delete Old Epics - Remove the original epic duplicates (51656-51663)
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from azure_devops_manager import AzureDevOpsManager, ConfigManager


def main():
    """Delete the old epic work items that are still showing as duplicates"""
    
    # List of old epic IDs from COMPLETION_SUMMARY.md (51656-51663)
    old_epic_ids = [51656, 51657, 51658, 51659, 51660, 51661, 51662, 51663]
    
    print(f"🗑️  Preparing to delete {len(old_epic_ids)} old epic work items...")
    print("📋 Old Epic IDs:", old_epic_ids)
    
    # Load configuration
    config_dir = Path(__file__).parent.parent
    try:
        org_url, project, pat = ConfigManager.load_config(config_dir)
        print(f"🔧 Configuration loaded for project: {project}")
    except ValueError as e:
        print(f"❌ {e}")
        return
    
    # Initialize Azure DevOps manager
    print("🔌 Connecting to Azure DevOps...")
    try:
        manager = AzureDevOpsManager(org_url, pat, project)
        print("✅ Connected successfully!")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return
    
    # Load our current work item mapping to ensure we don't delete current items
    mapping = ConfigManager.load_work_item_mapping(config_dir)
    current_epics = set(mapping.get('epics', {}).values())
    
    print(f"✅ Current epics to keep: {sorted(current_epics)}")
    
    # Safety check - make sure we're not deleting any current epics
    conflicts = set(old_epic_ids) & current_epics
    if conflicts:
        print(f"🚨 SAFETY CHECK FAILED! These IDs are in both old and current lists:")
        print(f"   {conflicts}")
        print("❌ Aborting to prevent deleting current epics!")
        return
    
    print("✅ Safety check passed - no conflicts with current epics")
    
    # Try to fetch and display what we're about to delete
    print(f"\n🔍 Checking which old epics still exist:")
    existing_epics = []
    
    for epic_id in old_epic_ids:
        try:
            work_item = manager.wit_client.get_work_item(epic_id)
            title = work_item.fields.get('System.Title', 'No Title')
            state = work_item.fields.get('System.State', 'Unknown')
            print(f"  📋 {epic_id}: {title} ({state})")
            existing_epics.append(epic_id)
        except Exception as e:
            print(f"  ❌ {epic_id}: Does not exist or no access")
    
    if not existing_epics:
        print("✅ No old epics found - they may already be deleted!")
        return
    
    print(f"\n🗑️  Proceeding to delete {len(existing_epics)} existing old epics...")
    
    deleted_count = 0
    failed_count = 0
    
    for epic_id in existing_epics:
        try:
            # Delete the epic
            manager.wit_client.delete_work_item(epic_id, destroy=True)
            print(f"✅ Deleted epic {epic_id}")
            deleted_count += 1
            
        except Exception as e:
            print(f"❌ Failed to delete epic {epic_id}: {e}")
            failed_count += 1
            continue
    
    # Summary
    print(f"\n📊 Deletion Summary:")
    print(f"  ✅ Successfully deleted: {deleted_count}")
    print(f"  ❌ Failed to delete: {failed_count}")
    print(f"  📋 Current epics remaining: {len(current_epics)}")
    
    if deleted_count > 0:
        print(f"\n🎉 Successfully cleaned up {deleted_count} old epic duplicates!")
        print("✨ Your Azure DevOps board should now only show current epics.")


if __name__ == "__main__":
    main()