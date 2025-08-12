#!/usr/bin/env python3
"""
Update From Markdown Command - Update existing work items with latest markdown content
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from azure_devops_manager import AzureDevOpsManager, MarkdownParser, ConfigManager


# Explicit mapping for precise epic matching
EPIC_MAPPING = {
    "Order Creation & Validation": "Order Creation & Validation",
    "Bundle Processing": "Bundle Processing", 
    "Payment Processing": "Payment Processing",
    "Fulfillment Integration": "Fulfillment Integration",
    "Status Management": "Status Management",
    "Cancellation & Returns": "Cancellation & Returns",
    "API Integration": "API Integration",
    "Data Management & Reporting": "Data Management & Reporting"
}


def main():
    """Update existing work items from markdown content"""
    
    # Load configuration
    config_dir = Path(__file__).parent.parent
    try:
        org_url, project, pat = ConfigManager.load_config(config_dir)
        print(f"🔧 Configuration loaded for project: {project}")
    except ValueError as e:
        print(f"❌ {e}")
        return
    
    # Load work item mapping
    mapping = ConfigManager.load_work_item_mapping(config_dir)
    if not mapping.get('epics') and not mapping.get('stories'):
        print("❌ No work item mapping found. Run create_work_items.py first.")
        return
    
    # Path to markdown file
    markdown_file = "/Users/chongraktanaka/Projects/mao-docsite/mvp-requirements/user story/mvp-user-stories.md"
    if not Path(markdown_file).exists():
        print(f"❌ Markdown file not found: {markdown_file}")
        return
    
    # Parse markdown content
    print("📖 Parsing latest markdown content...")
    epics = MarkdownParser.parse_epics(markdown_file)
    stories = MarkdownParser.parse_user_stories(markdown_file)
    
    print(f"📋 Found {len(epics)} epics and {len(stories)} user stories in markdown")
    print(f"🎯 Found {len(mapping.get('epics', {}))} epics and {len(mapping.get('stories', {}))} stories to update")
    
    # Initialize Azure DevOps manager
    print("🔌 Connecting to Azure DevOps...")
    try:
        manager = AzureDevOpsManager(org_url, pat, project)
        print("✅ Connected successfully!")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return
    
    # Update work items
    print("\n🔄 Updating work items with latest markdown content...")
    
    updated_epics = 0
    updated_stories = 0
    failed_updates = 0
    
    # Update epics with precise matching
    for epic_name, work_item_id in mapping.get('epics', {}).items():
        markdown_title = EPIC_MAPPING.get(epic_name)
        if not markdown_title:
            print(f"⚠️  No mapping found for epic: {epic_name}")
            continue
            
        epic_data = epics.get(markdown_title)
        if not epic_data:
            print(f"⚠️  No markdown content found for: {markdown_title}")
            continue
        
        print(f"✅ Updating Epic: {epic_name} → {markdown_title}")
        if manager.update_epic_from_data(work_item_id, epic_data):
            updated_epics += 1
        else:
            failed_updates += 1
    
    # Update user stories
    for story_id, work_item_id in mapping.get('stories', {}).items():
        story_data = stories.get(story_id)
        if not story_data:
            print(f"⚠️  No markdown content found for story: {story_id}")
            continue
        
        print(f"✅ Updating Story: {story_id}")
        if manager.update_story_from_data(work_item_id, story_data):
            updated_stories += 1
        else:
            failed_updates += 1
    
    # Summary
    print(f"\n📊 Update Summary:")
    print(f"  ✅ Epics updated: {updated_epics}")
    print(f"  ✅ Stories updated: {updated_stories}")
    print(f"  ❌ Failed updates: {failed_updates}")
    
    if updated_epics > 0 or updated_stories > 0:
        print(f"\n🎉 Successfully updated {updated_epics + updated_stories} work items!")
        print(f"🔗 View at: {org_url}/{project}/_backlogs/backlog/")


if __name__ == "__main__":
    main()