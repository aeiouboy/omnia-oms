#!/usr/bin/env python3
"""
Delete Duplicate Work Items - Remove old duplicate work items, keeping only current updated ones
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from azure_devops_manager import AzureDevOpsManager, ConfigManager


def main():
    """Delete duplicate work items safely"""
    
    # List of duplicate work item IDs to delete (older versions)
    duplicate_ids = [
        51664, 51665, 51666, 51667, 51668, 51669,  # ORD stories
        51670, 51671, 51672, 51673, 51674,         # BUN stories
        51675, 51676, 51677, 51678, 51679,         # PAY stories
        51680, 51681, 51682, 51683, 51684, 51685,  # FUL stories  
        51686, 51687, 51688, 51689,                # STA stories
        51690, 51691, 51692, 51693,                # CAN stories
        51694, 51695, 51696, 51697, 51698,         # API stories
        51699, 51700, 51701, 51702                 # DAT stories
    ]
    
    print(f"🗑️  Preparing to delete {len(duplicate_ids)} duplicate work items...")
    print("📋 Duplicate IDs:", duplicate_ids)
    
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
    
    # Load our current work item mapping to double-check we're not deleting current items
    mapping = ConfigManager.load_work_item_mapping(config_dir)
    current_work_items = set(mapping.get('stories', {}).values())
    current_epics = set(mapping.get('epics', {}).values())
    
    print(f"✅ Current work items to keep: {sorted(current_work_items)}")
    print(f"✅ Current epics to keep: {sorted(current_epics)}")
    
    # Safety check - make sure we're not deleting any current work items
    conflicts = set(duplicate_ids) & (current_work_items | current_epics)
    if conflicts:
        print(f"🚨 SAFETY CHECK FAILED! These IDs are in both duplicate and current lists:")
        print(f"   {conflicts}")
        print("❌ Aborting to prevent deleting current work items!")
        return
    
    print("✅ Safety check passed - no conflicts with current work items")
    
    # Confirm deletion
    print(f"\n⚠️  About to delete {len(duplicate_ids)} duplicate work items")
    print("   This action cannot be undone!")
    
    # For safety, let's do a dry run first to show what would be deleted
    print(f"\n🔍 DRY RUN - Fetching details of items to delete:")
    
    try:
        work_items = manager.wit_client.get_work_items(duplicate_ids[:5])  # Just check first 5
        for work_item in work_items:
            print(f"  - {work_item.id}: {work_item.fields['System.Title']} (Created: {work_item.fields['System.CreatedDate']})")
    except Exception as e:
        print(f"⚠️  Error fetching work item details: {e}")
    
    # Ask for confirmation
    response = input(f"\n❓ Are you sure you want to delete {len(duplicate_ids)} duplicate work items? (yes/no): ")
    if response.lower() != 'yes':
        print("❌ Deletion cancelled by user")
        return
    
    # Proceed with deletion
    print(f"\n🗑️  Proceeding with deletion of {len(duplicate_ids)} work items...")
    
    deleted_count = 0
    failed_count = 0
    
    for work_item_id in duplicate_ids:
        try:
            # Delete the work item
            manager.wit_client.delete_work_item(work_item_id, destroy=True)
            print(f"✅ Deleted work item {work_item_id}")
            deleted_count += 1
            
        except Exception as e:
            print(f"❌ Failed to delete work item {work_item_id}: {e}")
            failed_count += 1
            continue
    
    # Summary
    print(f"\n📊 Deletion Summary:")
    print(f"  ✅ Successfully deleted: {deleted_count}")
    print(f"  ❌ Failed to delete: {failed_count}")
    print(f"  📋 Remaining current work items: {len(current_work_items)} stories + {len(current_epics)} epics")
    
    if deleted_count > 0:
        print(f"\n🎉 Successfully cleaned up {deleted_count} duplicate work items!")
        print("✨ Your Azure DevOps project now only contains the updated work items with complete technical details.")


if __name__ == "__main__":
    main()