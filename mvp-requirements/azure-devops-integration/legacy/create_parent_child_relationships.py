#!/usr/bin/env python3
"""
Create parent-child relationships between epics and user stories
This will remove orphaned stories from appearing in the Epics view
"""

import sys
import os
import json
from pathlib import Path

# Add the directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import the main components from the original script
from create_azure_work_items import AzureDevOpsClient
from azure.devops.v7_1.work_item_tracking.models import JsonPatchOperation


def get_story_epic_mapping():
    """Define which stories belong to which epics based on story prefixes"""
    return {
        # Order Creation & Validation Epic (51656)
        'ORD': 51656,
        # Bundle Processing Epic (51657) 
        'BUN': 51657,
        # Payment Processing Epic (51658)
        'PAY': 51658,
        # Fulfillment Integration Epic (51659)
        'FUL': 51659,
        # Status Management Epic (51660)
        'STA': 51660,
        # Cancellation & Returns Epic (51661)
        'CAN': 51661,
        # API Integration Epic (51662)
        'API': 51662,
        # Data Management & Reporting Epic (51663)
        'DAT': 51663
    }


def main():
    """Main execution function"""
    
    # Load from .env file
    env_file = Path(__file__).parent / '.env'
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    if '=' in line:
                        key, value = line.strip().split('=', 1)
                        os.environ[key] = value
    
    # Configuration
    ORGANIZATION_URL = os.getenv('AZURE_DEVOPS_ORG_URL')
    PROJECT_NAME = os.getenv('AZURE_DEVOPS_PROJECT')
    PERSONAL_ACCESS_TOKEN = os.getenv('AZURE_DEVOPS_PAT')
    
    if not all([ORGANIZATION_URL, PROJECT_NAME, PERSONAL_ACCESS_TOKEN]):
        print("❌ Error: Missing configuration!")
        return
    
    print(f"🔗 Creating parent-child relationships...")
    print(f"   🎯 Linking user stories to their parent epics")
    print(f"   📊 This will organize the backlog properly")
    
    # Load work item mapping
    mapping_file = Path(__file__).parent / "work_item_mapping.json"
    with open(mapping_file, 'r') as f:
        mapping = json.load(f)
    
    story_mapping = mapping.get('stories', {})
    epic_mapping = mapping.get('epics', {})
    story_epic_mapping = get_story_epic_mapping()
    
    # Initialize Azure DevOps client
    print("🔌 Connecting to Azure DevOps...")
    client = AzureDevOpsClient(ORGANIZATION_URL, PERSONAL_ACCESS_TOKEN)
    print("✅ Connected!")
    
    created_relationships = 0
    failed_relationships = 0
    total_stories = len(story_mapping)
    
    print(f"\n📊 Processing {total_stories} user stories...")
    
    # Create parent-child relationships
    for i, (story_id, story_work_item_id) in enumerate(story_mapping.items(), 1):
        print(f"  🔗 [{i:2d}/{total_stories}] Linking {story_id}...")
        
        # Determine parent epic based on story prefix
        story_prefix = story_id.split('-')[0]  # ORD, BUN, PAY, etc.
        parent_epic_id = story_epic_mapping.get(story_prefix)
        
        if not parent_epic_id:
            print(f"    ⚠️  No parent epic found for prefix {story_prefix}")
            failed_relationships += 1
            continue
            
        try:
            # Create parent-child relationship
            # The child (user story) gets a "parent" relationship to the epic
            document = [
                JsonPatchOperation(
                    op="add",
                    path="/relations/-",
                    value={
                        "rel": "System.LinkTypes.Hierarchy-Reverse",
                        "url": f"{ORGANIZATION_URL}/{PROJECT_NAME}/_apis/wit/workItems/{parent_epic_id}",
                        "attributes": {
                            "comment": f"Linked to parent epic via automation"
                        }
                    }
                )
            ]
            
            updated_work_item = client.wit_client.update_work_item(
                document=document,
                id=story_work_item_id
            )
            
            print(f"    ✅ Linked {story_id} → Epic {parent_epic_id}")
            created_relationships += 1
            
        except Exception as e:
            print(f"    ❌ Failed to link {story_id}: {e}")
            failed_relationships += 1
    
    print(f"\n📊 Final Summary:")
    print(f"  ✅ Successfully linked: {created_relationships}")
    print(f"  ❌ Failed: {failed_relationships}")
    print(f"  📈 Success rate: {(created_relationships/total_stories)*100:.1f}%")
    
    print(f"\n✨ Parent-child relationships created:")
    for prefix, epic_id in story_epic_mapping.items():
        epic_name = None
        for name, id in epic_mapping.items():
            if id == epic_id:
                epic_name = name
                break
        story_count = len([s for s in story_mapping.keys() if s.startswith(prefix)])
        print(f"  • {epic_name} (Epic {epic_id}) ← {story_count} stories ({prefix}-xxx)")
    
    print(f"\n🔗 View organized backlog:")
    print(f"  📋 Backlog: {ORGANIZATION_URL}/{PROJECT_NAME}/_backlogs/backlog")
    print(f"  📊 Epic Board: {ORGANIZATION_URL}/{PROJECT_NAME}/_boards/board/t/Product%20-%20New%20OMS%20Team/Epics")
    
    print(f"\n💡 Expected result:")
    print(f"  • User stories will now appear under their parent epics")
    print(f"  • Epics view will only show actual epics (not orphaned stories)")
    print(f"  • Backlog hierarchy will be properly organized")


if __name__ == "__main__":
    main()