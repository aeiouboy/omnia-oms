#!/usr/bin/env python3
"""
Verify Story Updates - Check that all user stories were updated with latest content
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from azure_devops_manager import AzureDevOpsManager, ConfigManager


def main():
    """Verify that user stories were updated with latest content"""
    
    print("🔍 Verifying user story updates...")
    
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
    
    print(f"\n🔍 Checking {len(story_ids)} user stories for updated content...")
    
    updated_count = 0
    missing_content_count = 0
    
    # Check each story for updated content indicators
    for story_id, work_item_id in story_ids.items():
        try:
            # Get work item
            work_item = manager.wit_client.get_work_item(work_item_id)
            description = work_item.fields.get('System.Description', '')
            acceptance_criteria = work_item.fields.get('Microsoft.VSTS.Common.AcceptanceCriteria', '')
            
            # Check for enhanced content indicators
            has_enhanced_content = (
                'System Workflow Diagram' in description and
                'Process Steps' in description and
                'language-mermaid' in description and
                'Integration Points:' in description
            )
            
            has_updated_criteria = (
                acceptance_criteria and
                len(acceptance_criteria.strip()) > 50  # Has substantial content
            )
            
            if has_enhanced_content and has_updated_criteria:
                print(f"✅ {story_id} (ID: {work_item_id}) - Enhanced content and criteria present")
                updated_count += 1
            else:
                missing_items = []
                if not has_enhanced_content:
                    missing_items.append("enhanced description")
                if not has_updated_criteria:
                    missing_items.append("updated criteria")
                print(f"❌ {story_id} (ID: {work_item_id}) - Missing: {', '.join(missing_items)}")
                missing_content_count += 1
                
        except Exception as e:
            print(f"❌ Error checking {story_id} (ID: {work_item_id}): {e}")
            missing_content_count += 1
    
    # Summary
    print(f"\n📊 Verification Summary:")
    print(f"  ✅ Stories with enhanced content: {updated_count}")
    print(f"  ❌ Stories missing content: {missing_content_count}")
    print(f"  📋 Total stories checked: {len(story_ids)}")
    
    # Detailed content check for one story
    if updated_count > 0:
        print(f"\n🔍 Detailed content check for UC-001...")
        try:
            uc001_id = story_ids.get("UC-001")
            if uc001_id:
                work_item = manager.wit_client.get_work_item(uc001_id)
                description = work_item.fields.get('System.Description', '')
                
                content_elements = [
                    ("Mermaid Diagram", "language-mermaid" in description),
                    ("Process Steps Section", "Process Steps" in description),
                    ("Key Features Section", "Key Features" in description or "Key Processing" in description),
                    ("Business Rules Section", "Business Rules" in description or "Rules" in description),
                    ("Integration Points", "Integration Points:" in description),
                    ("HTML Formatting", "<h2>" in description and "<div" in description)
                ]
                
                for element, present in content_elements:
                    status = "✅" if present else "❌"
                    print(f"     {status} {element}")
                    
        except Exception as e:
            print(f"❌ Error checking detailed content: {e}")
    
    if updated_count == len(story_ids):
        print(f"\n🎉 All {len(story_ids)} user stories successfully updated!")
        print("📊 Enhanced content includes:")
        print("   • Improved Mermaid diagrams with latest workflow changes")
        print("   • Detailed process steps from updated workflow files")
        print("   • Key features and capabilities sections")
        print("   • Comprehensive business rules")
        print("   • Updated acceptance criteria")
        print("   • Enhanced HTML formatting for better readability")
    elif updated_count > 0:
        print(f"\n⚠️  {updated_count}/{len(story_ids)} stories successfully updated")
        print(f"   {missing_content_count} stories may need manual review")
    else:
        print(f"\n❌ No user stories appear to have enhanced content")
    
    print(f"\n🔗 View updated project at: {org_url}/{project}/_backlogs/backlog/")


if __name__ == "__main__":
    main()