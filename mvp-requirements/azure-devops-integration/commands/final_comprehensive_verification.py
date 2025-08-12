#!/usr/bin/env python3
"""
Final Comprehensive Verification - Check ALL 39 user stories for corruption using Azure DevOps API
"""

import sys
import json
import time
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from azure_devops_manager import AzureDevOpsManager, ConfigManager


def analyze_content_for_corruption(description, acceptance_criteria, story_id):
    """Analyze content for corruption indicators"""
    issues = []
    warnings = []
    
    # Check for corruption patterns (like the DAT-004 issue we fixed)
    corruption_indicators = [
        "## Implementation Phases",
        "### Phase 1 (Sprint",
        "## Success Criteria", 
        "### Technical Metrics",
        "### Business Metrics",
        "## Risk Mitigation",
        "### Assumptions",
        "## Acceptance Criteria"  # This shouldn't be in Description field
    ]
    
    # Check description field for corruption
    for indicator in corruption_indicators:
        if indicator in description:
            issues.append(f"CORRUPTION: '{indicator}' found in Description")
    
    # Check acceptance criteria field for corruption  
    for indicator in corruption_indicators:
        if indicator in acceptance_criteria:
            issues.append(f"CORRUPTION: '{indicator}' found in Acceptance Criteria")
    
    # Check for proper user story structure
    required_elements = ['<strong>As a', '<strong>I want', '<strong>So that']
    missing_elements = []
    for element in required_elements:
        if element not in description:
            missing_elements.append(element.replace('<strong>', '').replace('</strong>', ''))
    
    if missing_elements:
        issues.append(f"MISSING: User story elements: {', '.join(missing_elements)}")
    
    # Check for empty or very short content
    if not description or len(description.strip()) < 50:
        issues.append("MISSING: Description too short or empty")
    
    if not acceptance_criteria or len(acceptance_criteria.strip()) < 30:
        issues.append("MISSING: Acceptance criteria too short or empty")
    
    # Check for technical notes and dependencies
    if 'Dependencies' not in description:
        warnings.append("Dependencies section missing")
    
    if 'Technical Notes' not in description:
        warnings.append("Technical Notes section missing")
    
    return issues, warnings


def main():
    """Verify all user stories for corruption and completeness"""
    
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
    user_stories = mapping.get('stories', {})
    
    if not user_stories:
        print("❌ No user stories found in mapping")
        return
    
    print(f"📋 Verifying {len(user_stories)} user stories for corruption and completeness...")
    print("=" * 80)
    
    # Track results
    total_stories = len(user_stories)
    clean_stories = 0
    stories_with_warnings = 0
    stories_with_issues = 0
    all_problems = []
    
    # Process each story
    for story_id, work_item_id in sorted(user_stories.items()):
        try:
            print(f"🔍 Checking {story_id} (ID: {work_item_id})...", end=" ")
            
            # Get work item details
            work_item = manager.wit_client.get_work_item(work_item_id)
            
            # Extract fields
            description = work_item.fields.get('System.Description', '') or ''
            acceptance_criteria = work_item.fields.get('Microsoft.VSTS.Common.AcceptanceCriteria', '') or ''
            title = work_item.fields.get('System.Title', '')
            # Analyze content
            issues, warnings = analyze_content_for_corruption(description, acceptance_criteria, story_id)
            
            # Report results
            if issues:
                print(f"🚨 ISSUES DETECTED")
                for issue in issues:
                    print(f"    - {issue}")
                stories_with_issues += 1
                all_problems.append({
                    'story_id': story_id,
                    'work_item_id': work_item_id,
                    'title': title,
                    'issues': issues,
                    'warnings': warnings,
                    'url': f"{org_url}/{project}/_workitems/edit/{work_item_id}"
                })
            elif warnings:
                print(f"⚠️  WARNINGS")
                for warning in warnings:
                    print(f"    - {warning}")
                stories_with_warnings += 1
            else:
                print("✅ Clean")
                clean_stories += 1
            
            # Rate limiting
            time.sleep(0.3)
            
        except Exception as e:
            print(f"❌ ERROR: {e}")
            stories_with_issues += 1
            all_problems.append({
                'story_id': story_id,
                'work_item_id': work_item_id,
                'title': f"Error retrieving {story_id}",
                'issues': [f"API Error: {e}"],
                'warnings': [],
                'url': f"{org_url}/{project}/_workitems/edit/{work_item_id}"
            })
    
    # Generate comprehensive summary
    print("\\n" + "=" * 80)
    print("📊 FINAL VERIFICATION RESULTS:")
    print("=" * 80)
    print(f"📋 Total stories verified: {total_stories}")
    print(f"✅ Clean stories: {clean_stories}")
    print(f"⚠️  Stories with warnings: {stories_with_warnings}")
    print(f"🚨 Stories with critical issues: {stories_with_issues}")
    
    # Calculate success rate
    success_rate = ((clean_stories + stories_with_warnings) / total_stories) * 100
    critical_success_rate = (clean_stories / total_stories) * 100
    
    print(f"\\n📈 Overall success rate: {success_rate:.1f}%")
    print(f"📈 Critical success rate (no issues): {critical_success_rate:.1f}%")
    
    # Report critical issues that need fixing
    if stories_with_issues > 0:
        print(f"\\n🚨 CRITICAL ISSUES REQUIRING IMMEDIATE FIXES:")
        print("=" * 60)
        for problem in all_problems:
            if problem['issues']:
                print(f"\\n📋 {problem['story_id']} (ID: {problem['work_item_id']})")
                print(f"    Title: {problem['title']}")
                for issue in problem['issues']:
                    print(f"    🚨 {issue}")
                print(f"    🔗 {problem['url']}")
        
        print(f"\\n⚠️  {stories_with_issues} stories require immediate attention!")
        return all_problems
    else:
        print("\\n🎉 ALL STORIES VERIFIED CLEAN!")
        print("✅ No corruption detected in any user story")
        print("✅ All stories have proper user story structure")
        print("✅ All stories have adequate content length")
        print("\\n🚀 Project is ready for MVP Sprint 1 development!")
        return []


if __name__ == "__main__":
    problems = main()
    if problems:
        print(f"\\n📄 Run individual fixes for the {len(problems)} problematic stories identified above.")
    else:
        print("\\n🏆 Verification complete - All user stories are in excellent condition!")