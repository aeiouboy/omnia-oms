#!/usr/bin/env python3
"""
Set Iterations - Update all user stories to use MVP - Sprint 1 iteration
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from azure_devops_manager import AzureDevOpsManager, ConfigManager
from azure.devops.v7_1.work_item_tracking.models import JsonPatchOperation


def main():
    """Set iteration for all user stories to MVP - Sprint 1"""
    
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
    
    # Load our current work item mapping
    mapping = ConfigManager.load_work_item_mapping(config_dir)
    user_stories = mapping.get('stories', {})
    
    if not user_stories:
        print("❌ No user stories found in mapping")
        return
    
    print(f"📋 Found {len(user_stories)} user stories to update")
    
    # Target iteration path
    target_iteration = "Product - New OMS\\MVP - Sprint 1"
    
    print(f"🎯 Setting iteration to: {target_iteration}")
    print(f"\n🔄 Updating user stories...")
    
    updated_count = 0
    failed_count = 0
    
    # Update each user story
    for story_id, work_item_id in user_stories.items():
        try:
            # Create update operation for iteration path
            updates = [
                JsonPatchOperation(
                    op="replace",
                    path="/fields/System.IterationPath",
                    value=target_iteration
                )
            ]
            
            # Update the work item
            success = manager.update_work_item(work_item_id, updates)
            
            if success:
                print(f"✅ Updated {story_id} (ID: {work_item_id})")
                updated_count += 1
            else:
                print(f"❌ Failed to update {story_id} (ID: {work_item_id})")
                failed_count += 1
                
        except Exception as e:
            print(f"❌ Error updating {story_id} (ID: {work_item_id}): {e}")
            failed_count += 1
            continue
    
    # Summary
    print(f"\n📊 Iteration Update Summary:")
    print(f"  ✅ Successfully updated: {updated_count}")
    print(f"  ❌ Failed to update: {failed_count}")
    print(f"  📋 Total user stories: {len(user_stories)}")
    
    if updated_count > 0:
        print(f"\n🎉 Successfully set {updated_count} user stories to iteration '{target_iteration}'!")
        print(f"🔗 View updated backlog: {org_url}/{project}/_backlogs/backlog/")
        print(f"🏃‍♂️ View sprint: {org_url}/{project}/_sprints/backlog/Product%20-%20New%20OMS%20Team/Product%20-%20New%20OMS/MVP%20-%20Sprint%201")


if __name__ == "__main__":
    main()