#!/usr/bin/env python3
"""
Upload Workflow Diagrams to Azure DevOps User Stories
Adds workflow diagrams to each user story description for visual reference.
"""

import os
import sys
import base64
import mimetypes
from typing import Dict, List
from azure.devops.v7_1.work_item_tracking.models import JsonPatchOperation

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from azure_devops_manager import AzureDevOpsManager
import json

def load_config():
    """Load configuration from environment or .env file"""
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    
    org_url = os.getenv('AZURE_DEVOPS_ORG_URL')
    pat = os.getenv('AZURE_DEVOPS_PAT')
    project = os.getenv('AZURE_DEVOPS_PROJECT')
    
    if not all([org_url, pat, project]):
        print("❌ Missing Azure DevOps configuration. Please set:")
        print("   AZURE_DEVOPS_ORG_URL")
        print("   AZURE_DEVOPS_PAT") 
        print("   AZURE_DEVOPS_PROJECT")
        sys.exit(1)
    
    return org_url, pat, project

def get_diagram_mappings() -> Dict[str, str]:
    """Get mapping of user stories to their diagram files"""
    base_path = "/Users/chongraktanaka/Projects/mao-docsite/final_hq_diagrams"
    
    diagrams = {
        "UC-001": f"{base_path}/UC-001-System-Workflow_standard.png",
        "UC-002": f"{base_path}/UC-002-Bundle-Order-Workflow_standard.png", 
        "UC-003": f"{base_path}/UC-003-Pack-Order-Workflow_standard.png",
        "UC-004": f"{base_path}/UC-004-Bundle-Pack-Workflow_standard.png",
        "UC-005": f"{base_path}/UC-005-Substitution-Processing-Workflow_standard.png",
        "UC-006": f"{base_path}/UC-006-Order-Cancellation-Workflow_standard.png",
        "UC-007": f"{base_path}/UC-007-Delivery-Tracking-Workflow_standard.png"
    }
    
    # Verify files exist
    for story_id, file_path in diagrams.items():
        if not os.path.exists(file_path):
            print(f"⚠️  Warning: Diagram file not found for {story_id}: {file_path}")
    
    return diagrams

def upload_attachment_to_azure_devops(manager: AzureDevOpsManager, file_path: str) -> str:
    """Upload file as attachment to Azure DevOps and return attachment URL"""
    try:
        # Read file content
        with open(file_path, 'rb') as file:
            file_content = file.read()
        
        # Get file info
        file_name = os.path.basename(file_path)
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type is None:
            mime_type = 'application/octet-stream'
        
        # Upload attachment using Azure DevOps REST API
        attachment_client = manager.connection.clients.get_work_item_tracking_client()
        
        # Upload the attachment
        attachment = attachment_client.create_attachment(
            upload_stream=file_content,
            project=manager.project_name,
            file_name=file_name,
            area_path=None
        )
        
        print(f"   📎 Uploaded attachment: {file_name}")
        return attachment.url
        
    except Exception as e:
        print(f"   ❌ Failed to upload attachment {file_path}: {str(e)}")
        return None

def get_current_description(manager: AzureDevOpsManager, work_item_id: int) -> str:
    """Get current description of a work item"""
    try:
        work_item = manager.wit_client.get_work_item(work_item_id)
        return work_item.fields.get('System.Description', '')
    except Exception as e:
        print(f"   ❌ Failed to get current description for work item {work_item_id}: {str(e)}")
        return ''

def update_description_with_diagram(manager: AzureDevOpsManager, work_item_id: int, diagram_path: str, story_id: str) -> bool:
    """Update work item description to include workflow diagram"""
    try:
        # Upload the diagram as attachment
        attachment_url = upload_attachment_to_azure_devops(manager, diagram_path)
        if not attachment_url:
            return False
        
        # Get current description
        current_description = get_current_description(manager, work_item_id)
        
        # Add workflow diagram section to description
        diagram_section = f"""

<h3>Workflow Diagram</h3>
<p><strong>{story_id} System Workflow</strong></p>
<img src="{attachment_url}" alt="{story_id} Workflow Diagram" style="max-width: 100%; height: auto;" />
<p><em>Visual representation of the {story_id} workflow process showing all system interactions and data flow.</em></p>"""

        # Combine current description with diagram section
        updated_description = current_description + diagram_section
        
        # Update the work item
        updates = [
            JsonPatchOperation(
                op="replace",
                path="/fields/System.Description",
                value=updated_description
            )
        ]
        
        return manager.update_work_item(work_item_id, updates)
        
    except Exception as e:
        print(f"   ❌ Failed to update description with diagram: {str(e)}")
        return False

def load_work_item_mapping() -> Dict:
    """Load work item mapping from JSON file"""
    mapping_file = "work_item_mapping.json"
    try:
        with open(mapping_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Work item mapping file not found: {mapping_file}")
        sys.exit(1)

def upload_all_workflow_diagrams():
    """Upload workflow diagrams to all Azure DevOps user stories"""
    print("🖼️  Uploading Workflow Diagrams to Azure DevOps User Stories")
    print("=" * 70)
    
    # Load configuration
    org_url, pat, project = load_config()
    
    # Initialize Azure DevOps manager
    manager = AzureDevOpsManager(org_url, pat, project)
    
    # Load work item mapping
    mapping = load_work_item_mapping()
    
    # Get diagram mappings
    diagrams = get_diagram_mappings()
    
    print(f"\n📋 Uploading workflow diagrams for {len(diagrams)} user stories...")
    
    successful_updates = 0
    total_updates = len(diagrams)
    
    for story_id, diagram_path in diagrams.items():
        if story_id in mapping["stories"]:
            work_item_id = mapping["stories"][story_id]
            print(f"\n🔄 Uploading diagram for {story_id} (Work Item {work_item_id})...")
            
            if os.path.exists(diagram_path):
                success = update_description_with_diagram(manager, work_item_id, diagram_path, story_id)
                
                if success:
                    print(f"   ✅ Successfully added workflow diagram to {story_id}")
                    successful_updates += 1
                else:
                    print(f"   ❌ Failed to add diagram to {story_id}")
            else:
                print(f"   ❌ Diagram file not found: {diagram_path}")
        else:
            print(f"   ⚠️  No work item mapping found for {story_id}")
    
    # Summary
    print(f"\n📊 Upload Summary:")
    print(f"   Successfully updated: {successful_updates}/{total_updates}")
    print(f"   Success rate: {(successful_updates/total_updates)*100:.1f}%")
    
    if successful_updates == total_updates:
        print("🎉 All workflow diagrams uploaded successfully!")
        print("\n🎯 Key benefits:")
        print("   • Visual workflow representation in each user story")
        print("   • Clear system process documentation")
        print("   • Enhanced developer understanding")
        print("   • Professional user story presentation")
        print("   • Complete workflow traceability")
    else:
        print("⚠️  Some uploads failed. Please check the error messages above.")
    
    print(f"\n🔗 Verify diagrams at:")
    for story_id, work_item_id in mapping["stories"].items():
        print(f"   {story_id}: https://dev.azure.com/centralgroup/Product%20-%20New%20OMS/_workitems/edit/{work_item_id}")

if __name__ == "__main__":
    upload_all_workflow_diagrams()