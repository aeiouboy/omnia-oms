#!/usr/bin/env python3
"""
Delete Old Epics - Remove old epics while preserving QC Small Format Order Management System epic
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from azure_devops_manager import AzureDevOpsManager, ConfigManager


def main():
    """Delete old epics while preserving the new QC SMF epic and user stories"""
    
    print("🗑️  Preparing to delete old epics...")
    
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
    
    # Load work item mapping
    mapping = ConfigManager.load_work_item_mapping(config_dir)
    all_epics = mapping.get('epics', {})
    
    # Identify old epics to delete (exclude the new QC SMF epic)
    new_epic_name = "QC Small Format Order Management System"
    old_epics = {name: epic_id for name, epic_id in all_epics.items() 
                 if name != new_epic_name}
    
    if not old_epics:
        print("ℹ️  No old epics found to delete")
        return
    
    print(f"📋 Found {len(old_epics)} old epics to delete:")
    for name, epic_id in old_epics.items():
        print(f"   • {name} (ID: {epic_id})")
    
    print(f"✅ Preserving: {new_epic_name} (ID: {all_epics[new_epic_name]})")
    
    print(f"\n🗑️  Proceeding with deletion of {len(old_epics)} old epics...")
    
    deleted_count = 0
    failed_count = 0
    
    for epic_name, epic_id in old_epics.items():
        try:
            # Delete the epic (destroy=True for permanent deletion)
            manager.wit_client.delete_work_item(epic_id, destroy=True)
            print(f"✅ Deleted epic: {epic_name} (ID: {epic_id})")
            deleted_count += 1
            
        except Exception as e:
            print(f"❌ Failed to delete epic {epic_name} (ID: {epic_id}): {e}")
            failed_count += 1
            continue
    
    # Update work item mapping - remove deleted epics
    if deleted_count > 0:
        print(f"\n🧹 Updating work item mapping file...")
        
        # Keep only the new epic
        mapping['epics'] = {new_epic_name: all_epics[new_epic_name]}
        
        # Update summary
        mapping['summary']['total_epics_created'] = 1
        mapping['summary']['old_epics_deleted'] = deleted_count
        
        # Save updated mapping
        ConfigManager.save_work_item_mapping(config_dir, mapping)
        print("✅ Updated work item mapping file")
    
    # Summary
    print(f"\n📊 Deletion Summary:")
    print(f"  ✅ Successfully deleted: {deleted_count} old epics")
    print(f"  ❌ Failed to delete: {failed_count} old epics")
    print(f"  🎯 Preserved: 1 new epic ({new_epic_name})")
    print(f"  📖 Preserved: {len(mapping.get('stories', {}))} user stories")
    
    if deleted_count > 0:
        print(f"\n🎉 Successfully cleaned up {deleted_count} old epics!")
        print("✨ Your Azure DevOps project now contains only the QC Small Format Order Management System")
        print(f"🔗 View cleaned project at: {org_url}/{project}/_backlogs/backlog/")


if __name__ == "__main__":
    main()