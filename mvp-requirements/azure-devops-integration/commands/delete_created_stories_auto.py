#!/usr/bin/env python3
"""
Delete Created User Stories - Remove all user stories created by our scripts (AUTOMATED)
Leaves epics and other work items intact
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from azure_devops_manager import AzureDevOpsManager, ConfigManager


def main():
    """Delete only the user stories created by our scripts (automated)"""
    
    print("🗑️  Preparing to delete created user stories...")
    
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
    
    # Load work item mapping to get the story IDs we created
    mapping = ConfigManager.load_work_item_mapping(config_dir)
    story_ids = list(mapping.get('stories', {}).values())
    
    if not story_ids:
        print("ℹ️  No user stories found in mapping file to delete")
        return
    
    print(f"📋 Found {len(story_ids)} user stories to delete:")
    print(f"   Story IDs: {story_ids}")
    
    print(f"\n🗑️  Proceeding with deletion of {len(story_ids)} user stories...")
    
    deleted_count = 0
    failed_count = 0
    
    for story_id in story_ids:
        try:
            # Delete the work item (destroy=True for permanent deletion)
            manager.wit_client.delete_work_item(story_id, destroy=True)
            print(f"✅ Deleted user story {story_id}")
            deleted_count += 1
            
        except Exception as e:
            print(f"❌ Failed to delete user story {story_id}: {e}")
            failed_count += 1
            continue
    
    # Summary
    print(f"\n📊 Deletion Summary:")
    print(f"  ✅ Successfully deleted: {deleted_count} user stories")
    print(f"  ❌ Failed to delete: {failed_count} user stories")
    
    if deleted_count > 0:
        print(f"\n🎉 Successfully deleted {deleted_count} user stories!")
        print("ℹ️  Epics and other work items were left intact")
        print(f"🔗 View project at: {org_url}/{project}/_backlogs/backlog/")
        
        # Clear the work item mapping automatically
        print("🧹 Clearing user stories from mapping file...")
        mapping['stories'] = {}
        mapping['summary']['total_stories_created'] = 0
        ConfigManager.save_work_item_mapping(config_dir, mapping)
        print("✅ Cleared user stories from mapping file")


if __name__ == "__main__":
    main()