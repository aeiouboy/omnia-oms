#!/usr/bin/env python3
"""
Fix DAT-004 with correct user story content instead of corrupted epic-level content
"""

import sys
import os
from pathlib import Path

# Add the directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import the main components from the original script
from create_azure_work_items import AzureDevOpsClient
from azure.devops.v7_1.work_item_tracking.models import JsonPatchOperation


def main():
    """Fix DAT-004 with correct content"""
    
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
    
    print(f"🔧 Fixing DAT-004 content corruption...")
    print(f"   📝 Replacing epic-level content with proper user story content")
    
    # Correct content for DAT-004 based on original markdown
    correct_description = """<p><strong>As a</strong> system administrator, <strong>I want</strong> automated data archival, <strong>so that</strong> system performance is maintained.</p><p><strong>Technical Notes:</strong><br/>Use cloud storage for archives<br/>Implement restoration testing</p>"""
    
    correct_acceptance_criteria = """<ul><li><strong>Given data retention policies</strong></li><br/><li><strong>When archiving data</strong></li><br/><li><strong>Then:</strong></li><li style='margin-left: 20px; list-style-type: circle;'>Archive orders older than 1 year</li><li style='margin-left: 20px; list-style-type: circle;'>Maintain archived data accessibility</li><li style='margin-left: 20px; list-style-type: circle;'>Compress archived data</li><li style='margin-left: 20px; list-style-type: circle;'>Ensure compliance requirements</li><li style='margin-left: 20px; list-style-type: circle;'>Automate archival process</li><li style='margin-left: 20px; list-style-type: circle;'>Provide restoration capability</li><li><strong>And run without impacting operations</strong></li></ul>"""
    
    # Initialize Azure DevOps client
    print("🔌 Connecting to Azure DevOps...")
    client = AzureDevOpsClient(ORGANIZATION_URL, PERSONAL_ACCESS_TOKEN)
    print("✅ Connected!")
    
    work_item_id = 51702  # DAT-004
    
    try:
        print(f"🔧 Fixing DAT-004 (ID: {work_item_id})...")
        
        # First check current content
        current_item = client.wit_client.get_work_item(work_item_id)
        current_desc_length = len(current_item.fields.get('System.Description', ''))
        
        print(f"   Current description length: {current_desc_length} chars (corrupted)")
        print(f"   New description length: {len(correct_description)} chars (correct)")
        
        # Update with correct content
        document = [
            JsonPatchOperation(
                op="replace",
                path="/fields/System.Description",
                value=correct_description
            ),
            JsonPatchOperation(
                op="replace", 
                path="/fields/Microsoft.VSTS.Common.AcceptanceCriteria",
                value=correct_acceptance_criteria
            )
        ]
        
        updated_work_item = client.wit_client.update_work_item(
            document=document,
            id=work_item_id
        )
        
        print(f"✅ Successfully fixed DAT-004!")
        print(f"   ✅ Restored proper user story description")
        print(f"   ✅ Restored proper acceptance criteria")
        print(f"   ✅ Removed epic-level content corruption")
        
        print(f"\n🔗 Verify fix:")
        print(f"   {ORGANIZATION_URL}/{PROJECT_NAME}/_workitems/edit/{work_item_id}")
        
        print(f"\n💡 Expected result:")
        print(f"   • DAT-004 now has simple user story content")
        print(f"   • No more epic-level implementation phases, success criteria, etc.")
        print(f"   • Proper Given/When/Then acceptance criteria")
        
    except Exception as e:
        print(f"❌ Failed to fix DAT-004: {e}")


if __name__ == "__main__":
    main()