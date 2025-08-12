#!/usr/bin/env python3
"""
Verify User Story Format - Check that all user stories follow proper format
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from azure_devops_manager import AzureDevOpsManager, ConfigManager


def check_user_story_format(description: str, acceptance_criteria: str) -> dict:
    """Check if content follows proper user story format"""
    
    checks = {
        'has_as_a': 'As a' in description,
        'has_i_want': 'I want' in description,
        'has_so_that': 'So that' in description,
        'has_user_story_section': 'User Story' in description,
        'has_workflow_diagram': 'System Workflow' in description and 'language-mermaid' in description,
        'has_technical_section': 'Technical Implementation' in description,
        'has_given_when_then': 'Given' in acceptance_criteria and 'When' in acceptance_criteria and 'Then' in acceptance_criteria,
        'has_definition_of_done': 'Definition of Done' in acceptance_criteria,
        'proper_html_structure': '<h2>' in description and '<div' in description,
        'has_acceptance_criteria': len(acceptance_criteria.strip()) > 100
    }
    
    return checks


def main():
    """Verify proper user story format for all stories"""
    
    print("🔍 Verifying proper user story format...")
    
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
    
    print(f"\n🔍 Checking {len(story_ids)} user stories for proper format...")
    
    all_passed = True
    results = {}
    
    for story_id, work_item_id in story_ids.items():
        try:
            # Get work item
            work_item = manager.wit_client.get_work_item(work_item_id)
            description = work_item.fields.get('System.Description', '')
            acceptance_criteria = work_item.fields.get('Microsoft.VSTS.Common.AcceptanceCriteria', '')
            title = work_item.fields.get('System.Title', '')
            
            # Check format
            checks = check_user_story_format(description, acceptance_criteria)
            results[story_id] = checks
            
            # Count passed checks
            passed_checks = sum(1 for passed in checks.values() if passed)
            total_checks = len(checks)
            
            print(f"\n📋 {story_id} (ID: {work_item_id}): {title[:50]}...")
            print(f"   📊 Format Score: {passed_checks}/{total_checks} checks passed")
            
            # Show detailed results
            format_elements = [
                ("User Story Structure", checks['has_as_a'] and checks['has_i_want'] and checks['has_so_that']),
                ("Organized Sections", checks['has_user_story_section'] and checks['has_technical_section']),
                ("Workflow Diagram", checks['has_workflow_diagram']),
                ("Acceptance Criteria", checks['has_given_when_then'] and checks['has_definition_of_done']),
                ("HTML Formatting", checks['proper_html_structure']),
                ("Content Quality", checks['has_acceptance_criteria'])
            ]
            
            for element_name, element_passed in format_elements:
                status = "✅" if element_passed else "❌"
                print(f"     {status} {element_name}")
            
            if passed_checks < total_checks:
                all_passed = False
                
        except Exception as e:
            print(f"❌ Error checking {story_id}: {e}")
            all_passed = False
            results[story_id] = {}
    
    # Overall summary
    print(f"\n{'='*60}")
    print("📊 USER STORY FORMAT VERIFICATION SUMMARY")
    print(f"{'='*60}")
    
    # Calculate overall statistics
    total_stories = len(results)
    perfect_stories = sum(1 for checks in results.values() if all(checks.values()))
    
    # Check specific format elements across all stories
    format_stats = {
        'User Story Format': sum(1 for checks in results.values() if checks.get('has_as_a') and checks.get('has_i_want') and checks.get('has_so_that')),
        'Workflow Diagrams': sum(1 for checks in results.values() if checks.get('has_workflow_diagram')),
        'Proper Acceptance Criteria': sum(1 for checks in results.values() if checks.get('has_given_when_then') and checks.get('has_definition_of_done')),
        'HTML Structure': sum(1 for checks in results.values() if checks.get('proper_html_structure')),
        'Section Organization': sum(1 for checks in results.values() if checks.get('has_user_story_section'))
    }
    
    print(f"📋 Stories with Perfect Format: {perfect_stories}/{total_stories}")
    print(f"\n📊 Format Element Coverage:")
    for element, count in format_stats.items():
        percentage = (count / total_stories * 100) if total_stories > 0 else 0
        print(f"   {element}: {count}/{total_stories} ({percentage:.0f}%)")
    
    if all_passed and perfect_stories == total_stories:
        print(f"\n🎉 ALL USER STORIES PROPERLY FORMATTED!")
        print("✨ Every story includes:")
        print("   • Proper 'As a... I want... So that...' structure")
        print("   • Given/When/Then acceptance criteria with Definition of Done")
        print("   • System workflow diagrams")
        print("   • Technical implementation details")
        print("   • Professional HTML formatting")
        print("   • Clear section organization")
        
    elif perfect_stories > 0:
        print(f"\n⚠️  {perfect_stories}/{total_stories} stories have perfect format")
        print("📝 Some stories may need minor adjustments")
        
    else:
        print(f"\n❌ User story format needs improvement")
        print("📝 Review and fix format issues identified above")
    
    print(f"\n🔗 View stories at: {org_url}/{project}/_backlogs/backlog/")
    
    return all_passed and perfect_stories == total_stories


if __name__ == "__main__":
    main()