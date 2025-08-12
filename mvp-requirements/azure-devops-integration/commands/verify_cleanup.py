#!/usr/bin/env python3
"""
Verify Cleanup - Confirm old epics removed and new epic with stories preserved
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from azure_devops_manager import AzureDevOpsManager, ConfigManager


def main():
    """Verify cleanup was successful"""
    
    print("🔍 Verifying epic cleanup and preservation...")
    
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
    
    print(f"\n📊 Current Azure DevOps State:")
    
    # Check epic
    epics = mapping.get('epics', {})
    print(f"\n🎯 Epics ({len(epics)}):")
    for epic_name, epic_id in epics.items():
        try:
            work_item = manager.wit_client.get_work_item(epic_id)
            status = work_item.fields.get('System.State', 'Unknown')
            print(f"  ✅ {epic_name} (ID: {epic_id}) - Status: {status}")
        except Exception as e:
            print(f"  ❌ {epic_name} (ID: {epic_id}) - Error: {e}")
    
    # Check user stories
    stories = mapping.get('stories', {})
    print(f"\n📖 User Stories ({len(stories)}):")
    story_count = 0
    for story_id, work_item_id in stories.items():
        try:
            work_item = manager.wit_client.get_work_item(work_item_id)
            title = work_item.fields.get('System.Title', 'Unknown')
            status = work_item.fields.get('System.State', 'Unknown')
            print(f"  ✅ {story_id} (ID: {work_item_id}) - {title[:50]}... - Status: {status}")
            story_count += 1
        except Exception as e:
            print(f"  ❌ {story_id} (ID: {work_item_id}) - Error: {e}")
    
    # Summary
    print(f"\n📊 Verification Summary:")
    print(f"  🎯 Active Epics: {len(epics)} (expected: 1)")
    print(f"  📖 Active User Stories: {story_count} (expected: 7)")
    print(f"  🗑️  Old Epics Deleted: {mapping.get('summary', {}).get('old_epics_deleted', 0)}")
    
    if len(epics) == 1 and story_count == 7:
        print(f"\n🎉 Cleanup verification successful!")
        print("✨ Azure DevOps project contains only QC Small Format Order Management System")
    else:
        print(f"\n⚠️  Verification found issues - please check Azure DevOps manually")
    
    print(f"\n🔗 View project at: {org_url}/{project}/_backlogs/backlog/")


if __name__ == "__main__":
    main()