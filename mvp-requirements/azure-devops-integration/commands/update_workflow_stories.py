#!/usr/bin/env python3
"""
Update Workflow User Stories - Update Azure DevOps user stories with latest workflow content
"""

import sys
import re
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from azure_devops_manager import AzureDevOpsManager, ConfigManager
from azure.devops.v7_1.work_item_tracking.models import JsonPatchOperation


def extract_mermaid_diagram(file_content: str) -> str:
    """Extract Mermaid diagram from file content"""
    pattern = r'```mermaid\n(.*?)\n```'
    match = re.search(pattern, file_content, re.DOTALL)
    return match.group(1).strip() if match else ""


def extract_process_steps(file_content: str) -> str:
    """Extract process steps section from file content"""
    # Find the Process Steps section
    pattern = r'## Process Steps\n(.*?)(?=\n## |$)'
    match = re.search(pattern, file_content, re.DOTALL)
    return match.group(1).strip() if match else ""


def extract_business_rules(file_content: str) -> str:
    """Extract business rules sections from file content"""
    # Look for various business rules sections
    sections = []
    
    # Find all sections that contain "Rules" or "Business"
    pattern = r'## (.+(?:Rules|Business).+)\n(.*?)(?=\n## |$)'
    matches = re.findall(pattern, file_content, re.DOTALL)
    
    for section_title, section_content in matches:
        sections.append(f"<h3>{section_title}</h3>\n{section_content.strip()}")
    
    return "\n\n".join(sections) if sections else ""


def extract_key_features(file_content: str) -> str:
    """Extract key features section from file content"""
    # Look for "Key ... Features" sections
    pattern = r'## (Key .+ Features)\n(.*?)(?=\n## |$)'
    match = re.search(pattern, file_content, re.DOTALL)
    
    if match:
        section_title, section_content = match.groups()
        return f"<h3>{section_title}</h3>\n{section_content.strip()}"
    return ""


def create_enhanced_html_description(story_id: str, file_content: str) -> str:
    """Create enhanced HTML description with all workflow content"""
    
    # Extract all sections
    mermaid_diagram = extract_mermaid_diagram(file_content)
    process_steps = extract_process_steps(file_content)
    key_features = extract_key_features(file_content)
    business_rules = extract_business_rules(file_content)
    
    # Convert markdown to HTML for better display
    def markdown_to_html(text: str) -> str:
        """Convert basic markdown formatting to HTML"""
        # Bold
        text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
        # Code blocks
        text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
        # Line breaks
        text = text.replace('\n', '<br/>\n')
        return text
    
    html_description = f"""
    <h2>📊 System Workflow Diagram</h2>
    <div style="background-color: #f8f9fa; padding: 15px; border-left: 4px solid #007acc; margin: 10px 0;">
    <pre><code class="language-mermaid">
{mermaid_diagram}
    </code></pre>
    </div>
    
    <hr/>
    
    <h2>🔄 Process Steps</h2>
    <div style="background-color: #fff; padding: 15px; border: 1px solid #ddd; margin: 10px 0;">
    {markdown_to_html(process_steps)}
    </div>
    
    <hr/>
    
    {f'''
    <h2>⚡ Key Features</h2>
    <div style="background-color: #f0f8ff; padding: 15px; border: 1px solid #007acc; margin: 10px 0;">
    {markdown_to_html(key_features)}
    </div>
    <hr/>
    ''' if key_features else ''}
    
    {f'''
    <h2>📋 Business Rules</h2>
    <div style="background-color: #fff8dc; padding: 15px; border: 1px solid #ffa500; margin: 10px 0;">
    {markdown_to_html(business_rules)}
    </div>
    <hr/>
    ''' if business_rules else ''}
    
    <div style="background-color: #e8f5e8; padding: 10px; border-radius: 5px; margin-top: 20px;">
    <strong>Integration Points:</strong> Kafka Order Create topic, Manhattan Active® Omni, T1 Fulfillment Centers, Slick REST API, Grab delivery, PMP coordination
    </div>
    """
    
    return html_description


def create_acceptance_criteria_from_content(file_content: str) -> str:
    """Create acceptance criteria from workflow content"""
    
    process_steps = extract_process_steps(file_content)
    
    # Extract key validation points and workflow steps
    criteria_points = []
    
    # Parse process steps for acceptance criteria
    lines = process_steps.split('\n')
    current_step = ""
    
    for line in lines:
        line = line.strip()
        if line.startswith('### '):
            # New step header
            current_step = line.replace('### ', '').replace('#', '')
            if current_step:
                criteria_points.append(f"• {current_step}")
        elif line.startswith('- **') and current_step:
            # Key point within step
            key_point = re.sub(r'- \*\*(.+?)\*\*', r'  ◦ \1', line)
            criteria_points.append(key_point)
    
    # Format as bullet-pointed text for Azure DevOps
    acceptance_criteria = "\n".join(criteria_points[:10])  # Limit to prevent overflow
    
    if not acceptance_criteria:
        acceptance_criteria = """• System receives order from Kafka Order Create topic
• Order validation passes all required field checks
• Data enrichment completes successfully
• Financial calculations maintain DECIMAL(18,4) precision
• Force allocation processes correctly
• Payment status updates to COD/Paid
• Release event publishes successfully
• Slick API integration functions properly
• Order status progresses through complete workflow
• All integration points respond correctly"""

    return acceptance_criteria


def main():
    """Update all workflow user stories with latest content"""
    
    print("🔄 Updating workflow user stories with latest content...")
    
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
    
    print(f"\n📋 Updating {len(workflow_files)} user stories with latest content...")
    
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
        
        print(f"\n📖 Updating {story_id}: {filename}")
        
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                file_content = f.read()
            
            # Create enhanced HTML description
            enhanced_description = create_enhanced_html_description(story_id, file_content)
            
            # Create updated acceptance criteria
            acceptance_criteria = create_acceptance_criteria_from_content(file_content)
            
            # Update work item with new content
            document = [
                JsonPatchOperation(
                    op="replace",
                    path="/fields/System.Description", 
                    value=enhanced_description
                ),
                JsonPatchOperation(
                    op="replace",
                    path="/fields/Microsoft.VSTS.Common.AcceptanceCriteria",
                    value=acceptance_criteria
                )
            ]
            
            manager.wit_client.update_work_item(
                document=document,
                id=work_item_id,
                project=project
            )
            
            print(f"✅ Updated {story_id} (Work Item {work_item_id}) with latest content")
            updated_count += 1
            
        except Exception as e:
            print(f"❌ Failed to update {story_id} (Work Item {work_item_id}): {e}")
            failed_count += 1
            continue
    
    # Summary
    print(f"\n📊 Update Summary:")
    print(f"  ✅ Successfully updated: {updated_count} user stories")
    print(f"  ❌ Failed to update: {failed_count} user stories")
    
    if updated_count > 0:
        print(f"\n🎉 Successfully updated {updated_count} user stories with latest content!")
        print("📊 All workflow user stories now include:")
        print("   • Enhanced Mermaid diagrams with improved formatting")
        print("   • Detailed process steps from workflow files")
        print("   • Key features and capabilities")
        print("   • Comprehensive business rules")
        print("   • Updated acceptance criteria")
        print(f"🔗 View updated project at: {org_url}/{project}/_backlogs/backlog/")


if __name__ == "__main__":
    main()