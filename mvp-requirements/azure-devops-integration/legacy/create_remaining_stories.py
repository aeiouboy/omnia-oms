#!/usr/bin/env python3
"""
Creates the remaining user stories that weren't created in the first run
Continues from where the previous script left off
"""

import sys
import os
import json
from pathlib import Path

# Add the directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import the main components from the original script
from create_azure_work_items import AzureDevOpsClient, UserStoryParser

def main():
    """Main execution function - creates remaining stories"""
    
    # Load from .env file
    env_file = Path(__file__).parent / '.env'
    if env_file.exists():
        print("Loading configuration from .env file...")
        with open(env_file) as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    if '=' in line:
                        key, value = line.strip().split('=', 1)
                        os.environ[key] = value
    
    # Configuration - Check environment variables
    ORGANIZATION_URL = os.getenv('AZURE_DEVOPS_ORG_URL')
    PROJECT_NAME = os.getenv('AZURE_DEVOPS_PROJECT')
    PERSONAL_ACCESS_TOKEN = os.getenv('AZURE_DEVOPS_PAT')
    
    # Validate configuration
    if not all([ORGANIZATION_URL, PROJECT_NAME, PERSONAL_ACCESS_TOKEN]):
        print("❌ Error: Missing configuration!")
        return
    
    print(f"\n🔧 Configuration:")
    print(f"  Organization: {ORGANIZATION_URL}")
    print(f"  Project: {PROJECT_NAME}")
    print(f"  Token: ***{PERSONAL_ACCESS_TOKEN[-4:] if len(PERSONAL_ACCESS_TOKEN) > 4 else '****'}")
    
    # Load existing mapping
    mapping_file = Path(__file__).parent / "work_item_mapping.json"
    if mapping_file.exists():
        with open(mapping_file, 'r') as f:
            existing_mapping = json.load(f)
        print(f"\n📊 Found existing work items:")
        print(f"  - {len(existing_mapping.get('epics', {}))} epics already created")
        print(f"  - {len(existing_mapping.get('stories', {}))} stories already created")
        
        existing_story_ids = set(existing_mapping.get('stories', {}).keys())
        epic_ids = existing_mapping.get('epics', {})
    else:
        print("⚠️ No existing mapping found. Starting fresh...")
        existing_story_ids = set()
        epic_ids = {}
        existing_mapping = {"epics": {}, "stories": {}}
    
    # Path to the user stories markdown file
    stories_file = "/Users/chongraktanaka/Projects/mao-docsite/mvp-requirements/user story/mvp-user-stories.md"
    
    # Parse the user stories
    print("\n📖 Parsing user stories from markdown file...")
    parser = UserStoryParser()
    epics_with_stories = parser.parse_markdown_file(stories_file)
    
    # Count remaining stories
    remaining_stories = []
    for epic_name, stories in epics_with_stories.items():
        for story in stories:
            if story.story_id not in existing_story_ids:
                remaining_stories.append((epic_name, story))
    
    print(f"\n📋 Remaining stories to create: {len(remaining_stories)}")
    
    if not remaining_stories:
        print("✅ All stories have already been created!")
        return
    
    # Initialize Azure DevOps client
    print("\n🔌 Connecting to Azure DevOps...")
    try:
        client = AzureDevOpsClient(ORGANIZATION_URL, PERSONAL_ACCESS_TOKEN)
        print("✅ Connected successfully!")
    except Exception as e:
        print(f"❌ Error connecting to Azure DevOps: {e}")
        return
    
    # Create remaining user stories
    print(f"\n🚀 Creating {len(remaining_stories)} remaining user stories...")
    
    created_count = 0
    failed_stories = []
    
    # Group by epic for better organization
    stories_by_epic = {}
    for epic_name, story in remaining_stories:
        if epic_name not in stories_by_epic:
            stories_by_epic[epic_name] = []
        stories_by_epic[epic_name].append(story)
    
    # Create stories epic by epic
    for epic_name, stories in stories_by_epic.items():
        print(f"\n  📗 Processing {epic_name} ({len(stories)} stories)...")
        parent_id = epic_ids.get(epic_name)
        
        if not parent_id:
            print(f"    ⚠️ Warning: Epic not found for '{epic_name}', creating stories without parent")
        
        for story in stories:
            try:
                story_id = client.create_user_story(PROJECT_NAME, story, parent_id)
                existing_mapping['stories'][story.story_id] = story_id
                created_count += 1
                
                # Save progress after each successful creation
                with open(mapping_file, 'w') as f:
                    json.dump(existing_mapping, f, indent=2)
                    
            except Exception as e:
                error_msg = str(e)
                if "authentication" in error_msg.lower():
                    print(f"\n❌ Authentication error. Stopping here.")
                    print(f"Created {created_count} stories before error.")
                    break
                else:
                    print(f"    ⚠️ Failed to create '{story.story_id}': {e}")
                    failed_stories.append(story.story_id)
        else:
            continue
        break  # Break outer loop if inner loop was broken
    
    # Final summary
    print(f"\n📊 Summary:")
    print(f"  ✅ Successfully created: {created_count} stories")
    if failed_stories:
        print(f"  ❌ Failed: {len(failed_stories)} stories")
        print(f"     Failed IDs: {', '.join(failed_stories)}")
    
    # Update summary in mapping
    existing_mapping['summary'] = {
        "total_epics_created": len(existing_mapping.get('epics', {})),
        "total_stories_created": len(existing_mapping.get('stories', {})),
        "total_stories_in_file": sum(len(stories) for stories in epics_with_stories.values()),
        "last_update": str(Path(__file__).stat().st_mtime)
    }
    
    with open(mapping_file, 'w') as f:
        json.dump(existing_mapping, f, indent=2)
    
    print(f"\n💾 Updated mapping saved to: {mapping_file}")
    
    # Print Azure DevOps links
    print(f"\n🔗 View your work items in Azure DevOps:")
    print(f"  Boards: {ORGANIZATION_URL}/{PROJECT_NAME}/_boards/board")
    print(f"  Backlogs: {ORGANIZATION_URL}/{PROJECT_NAME}/_backlogs/backlog")
    
    remaining_count = len(remaining_stories) - created_count
    if remaining_count > 0:
        print(f"\n📝 Note: {remaining_count} stories still need to be created.")
        print("You can run this script again to continue where it left off.")


if __name__ == "__main__":
    main()