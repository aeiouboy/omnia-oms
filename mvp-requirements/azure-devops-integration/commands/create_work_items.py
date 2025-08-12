#!/usr/bin/env python3
"""
Create Work Items Command - Clean implementation for creating epics and stories from markdown
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from azure_devops_manager import AzureDevOpsManager, MarkdownParser, ConfigManager


def main():
    """Create all work items from markdown file"""
    
    # Load configuration
    config_dir = Path(__file__).parent.parent
    try:
        org_url, project, pat = ConfigManager.load_config(config_dir)
        print(f"🔧 Configuration loaded for project: {project}")
    except ValueError as e:
        print(f"❌ {e}")
        return
    
    # Path to markdown file
    markdown_file = "/Users/chongraktanaka/Projects/mao-docsite/mvp-requirements/user story/mvp-user-stories.md"
    if not Path(markdown_file).exists():
        print(f"❌ Markdown file not found: {markdown_file}")
        return
    
    # Parse markdown content
    print("📖 Parsing markdown content...")
    epics = MarkdownParser.parse_epics(markdown_file)
    stories = MarkdownParser.parse_user_stories(markdown_file)
    
    print(f"📋 Found {len(epics)} epics and {len(stories)} user stories")
    
    # Confirm creation
    response = input("\nDo you want to create these work items in Azure DevOps? (yes/no): ")
    if response.lower() != 'yes':
        print("Cancelled.")
        return
    
    # Initialize Azure DevOps manager
    print("🔌 Connecting to Azure DevOps...")
    try:
        manager = AzureDevOpsManager(org_url, pat, project)
        print("✅ Connected successfully!")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return
    
    # Create work items
    print("\n🚀 Creating work items...")
    epic_ids = {}
    story_ids = {}
    
    try:
        # Create epics first
        for epic_name, epic in epics.items():
            epic_id = manager.create_epic(epic)
            epic_ids[epic_name] = epic_id
        
        # Group stories by epic and create them
        stories_by_epic = {}
        for story in stories.values():
            epic_name = story.epic
            if epic_name not in stories_by_epic:
                stories_by_epic[epic_name] = []
            stories_by_epic[epic_name].append(story)
        
        # Create stories under their epics
        for epic_name, epic_stories in stories_by_epic.items():
            parent_id = epic_ids.get(epic_name)
            for story in epic_stories:
                story_id = manager.create_user_story(story, parent_id)
                story_ids[story.story_id] = story_id
        
        # Save mapping
        mapping = {"epics": epic_ids, "stories": story_ids}
        ConfigManager.save_work_item_mapping(config_dir, mapping)
        
        print(f"\n✅ Successfully created {len(epic_ids)} epics and {len(story_ids)} user stories!")
        print(f"📄 Work item mapping saved to work_item_mapping.json")
        
    except Exception as e:
        print(f"❌ Error creating work items: {e}")


if __name__ == "__main__":
    main()