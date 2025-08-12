#!/usr/bin/env python3
"""
Assign all user stories to Natajrak Phuphatsirikorn
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
    
    print(f"🔧 Assigning all user stories...")
    print(f"   👤 Assignee: Natajrak Phuphatsirikorn")
    
    # Load work item mapping
    mapping_file = Path(__file__).parent / "work_item_mapping.json"
    with open(mapping_file, 'r') as f:
        mapping = json.load(f)
    
    story_mapping = mapping.get('stories', {})
    
    # Initialize Azure DevOps client
    print("🔌 Connecting to Azure DevOps...")
    client = AzureDevOpsClient(ORGANIZATION_URL, PERSONAL_ACCESS_TOKEN)
    print("✅ Connected!")
    
    updated_count = 0
    failed_count = 0
    total_count = len(story_mapping)
    
    print(f"\n📊 Processing {total_count} work items...")
    
    # Update all work items
    for i, (story_id, work_item_id) in enumerate(story_mapping.items(), 1):
        print(f"  🔧 [{i:2d}/{total_count}] Assigning {story_id}...")
        
        try:
            # Update the work item assignee
            # The assigned to field expects either the display name or email
            document = [
                JsonPatchOperation(
                    op="replace",
                    path="/fields/System.AssignedTo",
                    value="Natajrak Phuphatsirikorn"
                )
            ]
            
            updated_work_item = client.wit_client.update_work_item(
                document=document,
                id=work_item_id
            )
            
            print(f"    ✅ Assigned {story_id} (ID: {work_item_id})")
            updated_count += 1
            
        except Exception as e:
            print(f"    ❌ Failed to assign {story_id}: {e}")
            failed_count += 1
    
    print(f"\n📊 Final Summary:")
    print(f"  ✅ Successfully assigned: {updated_count}")
    print(f"  ❌ Failed: {failed_count}")
    print(f"  📈 Success rate: {(updated_count/total_count)*100:.1f}%")
    
    print(f"\n✨ All work items now have:")
    print(f"  • Assigned To: Natajrak Phuphatsirikorn")
    print(f"  • Ready for development work")
    
    print(f"\n🔗 View assigned work items:")
    print(f"  {ORGANIZATION_URL}/{PROJECT_NAME}/_backlogs/backlog")
    
    # Show a few sample links
    print(f"\n🎯 Sample work items to check:")
    sample_stories = list(story_mapping.items())[:3]
    for story_id, work_item_id in sample_stories:
        print(f"  • {story_id}: {ORGANIZATION_URL}/{PROJECT_NAME}/_workitems/edit/{work_item_id}")


if __name__ == "__main__":
    main()