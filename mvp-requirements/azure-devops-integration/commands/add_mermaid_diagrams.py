#!/usr/bin/env python3
"""
Add Mermaid Diagrams to User Stories - Update existing user stories with Mermaid flowcharts
"""

import sys
import re
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from azure_devops_manager import AzureDevOpsManager, ConfigManager
from azure.devops.v7_1.work_item_tracking.models import JsonPatchOperation


def extract_mermaid_diagram(file_path: Path) -> str:
    """Extract Mermaid diagram from markdown file"""
    try:
        content = file_path.read_text(encoding='utf-8')
        
        # Find mermaid code block
        pattern = r'```mermaid\n(.*?)\n```'
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            return match.group(1).strip()
        else:
            print(f"⚠️  No Mermaid diagram found in {file_path.name}")
            return ""
    except Exception as e:
        print(f"❌ Error reading {file_path.name}: {e}")
        return ""


def create_html_with_mermaid(original_description: str, mermaid_diagram: str) -> str:
    """Create HTML description that includes the Mermaid diagram"""
    if not mermaid_diagram:
        return original_description
    
    # Add Mermaid diagram at the beginning of the description
    mermaid_html = f"""
    <h3>📊 System Workflow Diagram</h3>
    <div class="mermaid-diagram">
    <pre><code class="language-mermaid">
{mermaid_diagram}
    </code></pre>
    </div>
    <hr/>
    
    {original_description}
    """
    
    return mermaid_html


def main():
    """Add Mermaid diagrams to all workflow user stories"""
    
    print("📊 Adding Mermaid diagrams to user stories...")
    
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
    
    # Load work item mapping to get story IDs
    mapping = ConfigManager.load_work_item_mapping(config_dir)
    story_ids = mapping.get('stories', {})
    
    if not story_ids:
        print("❌ No user stories found in mapping file")
        return
    
    # Define workflow files and their corresponding user story IDs
    workflow_files = {
        "UC-001": "UC-001-System-Workflow.md",
        "UC-002": "UC-002-Bundle-Order-Workflow.md", 
        "UC-003": "UC-003-Pack-Order-Workflow.md",
        "UC-004": "UC-004-Bundle-Pack-Workflow.md",
        "UC-005": "UC-005-Substitution-Processing-Workflow.md",
        "UC-006": "UC-006-Order-Cancellation-Workflow.md",
        "UC-007": "UC-007-Delivery-Tracking-Workflow.md"
    }
    
    user_story_dir = Path(__file__).parent.parent.parent / "user story"
    
    print(f"\n📋 Processing {len(workflow_files)} user stories with Mermaid diagrams...")
    
    updated_count = 0
    failed_count = 0
    
    for story_id, filename in workflow_files.items():
        if story_id not in story_ids:
            print(f"⚠️  Story ID {story_id} not found in mapping, skipping")
            continue
            
        work_item_id = story_ids[story_id]
        file_path = user_story_dir / filename
        
        if not file_path.exists():
            print(f"⚠️  File not found: {filename}, skipping")
            failed_count += 1
            continue
        
        print(f"\n📖 Processing {story_id}: {filename}")
        
        # Extract Mermaid diagram
        mermaid_diagram = extract_mermaid_diagram(file_path)
        
        if not mermaid_diagram:
            print(f"⚠️  No Mermaid diagram found for {story_id}, skipping")
            failed_count += 1
            continue
        
        try:
            # Get current work item
            work_item = manager.wit_client.get_work_item(work_item_id)
            current_description = work_item.fields.get('System.Description', '')
            
            # Check if Mermaid diagram already exists
            if 'mermaid-diagram' in current_description or 'System Workflow Diagram' in current_description:
                print(f"ℹ️  Mermaid diagram already exists for {story_id}, skipping")
                continue
            
            # Create updated description with Mermaid diagram
            updated_description = create_html_with_mermaid(current_description, mermaid_diagram)
            
            # Update work item
            document = [
                JsonPatchOperation(
                    op="replace",
                    path="/fields/System.Description", 
                    value=updated_description
                )
            ]
            
            manager.wit_client.update_work_item(
                document=document,
                id=work_item_id,
                project=project
            )
            
            print(f"✅ Added Mermaid diagram to {story_id} (Work Item {work_item_id})")
            updated_count += 1
            
        except Exception as e:
            print(f"❌ Failed to update {story_id} (Work Item {work_item_id}): {e}")
            failed_count += 1
            continue
    
    # Summary
    print(f"\n📊 Mermaid Diagram Update Summary:")
    print(f"  ✅ Successfully updated: {updated_count} user stories")
    print(f"  ❌ Failed to update: {failed_count} user stories")
    
    if updated_count > 0:
        print(f"\n🎉 Successfully added Mermaid diagrams to {updated_count} user stories!")
        print("📊 All workflow diagrams are now included in the user story descriptions")
        print(f"🔗 View project at: {org_url}/{project}/_backlogs/backlog/")


if __name__ == "__main__":
    main()