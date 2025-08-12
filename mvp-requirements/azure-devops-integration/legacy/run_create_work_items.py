#!/usr/bin/env python3
"""
Non-interactive version of the Azure DevOps work item creator
Automatically creates work items without requiring user input
"""

import sys
import os
from pathlib import Path

# Add the directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import the main components from the original script
from create_azure_work_items import AzureDevOpsClient, UserStoryParser

def main():
    """Main execution function - non-interactive version"""
    
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
        print("\nPlease ensure your .env file contains:")
        print("  - AZURE_DEVOPS_ORG_URL")
        print("  - AZURE_DEVOPS_PROJECT")
        print("  - AZURE_DEVOPS_PAT")
        return
    
    print(f"\n🔧 Configuration:")
    print(f"  Organization: {ORGANIZATION_URL}")
    print(f"  Project: {PROJECT_NAME}")
    print(f"  Token: ***{PERSONAL_ACCESS_TOKEN[-4:] if len(PERSONAL_ACCESS_TOKEN) > 4 else '****'}")
    
    # Path to the user stories markdown file
    stories_file = "/Users/chongraktanaka/Projects/mao-docsite/mvp-requirements/user story/mvp-user-stories.md"
    
    # Check if file exists
    if not os.path.exists(stories_file):
        print(f"❌ Error: File not found at {stories_file}")
        return
    
    # Parse the user stories
    print("\n📖 Parsing user stories from markdown file...")
    parser = UserStoryParser()
    epics_with_stories = parser.parse_markdown_file(stories_file)
    
    print(f"\n📊 Found {len(epics_with_stories)} epics with stories:")
    total_stories = 0
    for epic_name, stories in epics_with_stories.items():
        print(f"  - {epic_name}: {len(stories)} stories")
        total_stories += len(stories)
    print(f"\n  Total: {total_stories} user stories")
    
    # Initialize Azure DevOps client
    print("\n🔌 Connecting to Azure DevOps...")
    try:
        client = AzureDevOpsClient(ORGANIZATION_URL, PERSONAL_ACCESS_TOKEN)
        print("✅ Connected successfully!")
    except Exception as e:
        print(f"❌ Error connecting to Azure DevOps: {e}")
        print("\nPlease check:")
        print("1. Your PAT token is valid and not expired")
        print("2. The token has Work Items (Read, Write) permissions")
        print("3. The organization URL is correct")
        print("4. You have access to the project")
        return
    
    # Create work items
    print("\n🚀 Creating work items in Azure DevOps...")
    print("This may take a few minutes...")
    
    epic_ids = {}
    story_ids = {}
    
    try:
        # Create epics first
        print("\n📘 Creating Epics...")
        for epic_name in epics_with_stories.keys():
            epic_description = f"Epic for {epic_name} functionality in the MAO MVP implementation"
            try:
                epic_id = client.create_epic(PROJECT_NAME, f"MAO MVP - {epic_name}", epic_description)
                epic_ids[epic_name] = epic_id
            except Exception as e:
                print(f"  ⚠️ Warning: Could not create epic '{epic_name}': {e}")
        
        print(f"\n✅ Created {len(epic_ids)} epics")
        
        # Create user stories under their respective epics
        print("\n📗 Creating User Stories...")
        for epic_name, stories in epics_with_stories.items():
            parent_id = epic_ids.get(epic_name)
            print(f"\n  Processing {epic_name}...")
            for story in stories:
                try:
                    story_id = client.create_user_story(PROJECT_NAME, story, parent_id)
                    story_ids[story.story_id] = story_id
                except Exception as e:
                    print(f"    ⚠️ Warning: Could not create story '{story.story_id}': {e}")
        
        print(f"\n✅ Successfully created work items!")
        print(f"  - {len(epic_ids)} epics")
        print(f"  - {len(story_ids)} user stories")
        
        if len(story_ids) < total_stories:
            print(f"\n⚠️ Note: {total_stories - len(story_ids)} stories could not be created")
        
        # Save the mapping for reference
        import json
        mapping = {
            "organization": ORGANIZATION_URL,
            "project": PROJECT_NAME,
            "epics": epic_ids,
            "stories": story_ids,
            "summary": {
                "total_epics_created": len(epic_ids),
                "total_stories_created": len(story_ids),
                "total_stories_in_file": total_stories
            }
        }
        
        mapping_file = Path(__file__).parent / "work_item_mapping.json"
        
        with open(mapping_file, 'w') as f:
            json.dump(mapping, f, indent=2)
        
        print(f"\n💾 Work item ID mapping saved to: {mapping_file}")
        
        # Print Azure DevOps links
        print(f"\n🔗 View your work items in Azure DevOps:")
        print(f"  Boards: {ORGANIZATION_URL}/{PROJECT_NAME}/_boards/board")
        print(f"  Backlogs: {ORGANIZATION_URL}/{PROJECT_NAME}/_backlogs/backlog")
        print(f"  Queries: {ORGANIZATION_URL}/{PROJECT_NAME}/_queries")
        
    except Exception as e:
        print(f"\n❌ Error creating work items: {e}")
        import traceback
        traceback.print_exc()
        print("\nPossible issues:")
        print("1. Work item type 'Epic' or 'User Story' may not exist in your project")
        print("2. Your project may use different work item types (e.g., 'Feature' instead of 'Epic')")
        print("3. Check your project's process template at:")
        print(f"   {ORGANIZATION_URL}/{PROJECT_NAME}/_settings/work/process")


if __name__ == "__main__":
    main()