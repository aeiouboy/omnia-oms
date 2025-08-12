#!/usr/bin/env python3
"""
Verify All Stories - Systematically check all 39 user stories for content quality
"""

import sys
import time
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from azure_devops_manager import AzureDevOpsManager, ConfigManager


def analyze_story_content(work_item):
    """Analyze a story for potential issues"""
    issues = []
    warnings = []
    
    # Get field values safely
    description = work_item.fields.get('System.Description', '') or ''
    acceptance_criteria = work_item.fields.get('Microsoft.VSTS.Common.AcceptanceCriteria', '') or ''
    title = work_item.fields.get('System.Title', '')
    
    # Check for missing content
    if not description or len(description.strip()) < 50:
        issues.append("Description too short or missing")
    
    if not acceptance_criteria or len(acceptance_criteria.strip()) < 30:
        issues.append("Acceptance criteria missing or too short")
    
    # Check for corruption indicators (like DAT-004 had)
    corruption_indicators = [
        "## Implementation Phases",
        "### Phase 1 (Sprint",
        "## Success Criteria", 
        "### Technical Metrics",
        "### Business Metrics",
        "## Risk Mitigation"
    ]
    
    for indicator in corruption_indicators:
        if indicator in description or indicator in acceptance_criteria:
            issues.append(f"Potential corruption detected: contains '{indicator}'")
    
    # Check for proper HTML structure in acceptance criteria
    if acceptance_criteria and not ('<ul>' in acceptance_criteria or '<li>' in acceptance_criteria):
        if len(acceptance_criteria) > 100:  # Only flag if substantial content
            warnings.append("Acceptance criteria may not be properly HTML formatted")
    
    # Check for proper user story format
    required_phrases = ['<strong>As a', '<strong>I want', '<strong>So that']
    missing_phrases = []
    for phrase in required_phrases:
        if phrase not in description:
            missing_phrases.append(phrase.replace('<strong>', '').replace('</strong>', ''))
    
    if missing_phrases:
        issues.append(f"Missing user story elements: {', '.join(missing_phrases)}")
    
    # Check for technical notes
    if 'Technical Notes' not in description:
        warnings.append("Technical Notes section may be missing")
    
    # Check for dependencies
    if 'Dependencies' not in description:
        warnings.append("Dependencies section may be missing")
    
    return issues, warnings


def main():
    """Verify all user stories systematically"""
    
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
    
    # Load our current work item mapping
    mapping = ConfigManager.load_work_item_mapping(config_dir)
    user_stories = mapping.get('stories', {})
    
    if not user_stories:
        print("❌ No user stories found in mapping")
        return
    
    print(f"📋 Analyzing {len(user_stories)} user stories...")
    print("=" * 80)
    
    # Track results
    total_stories = len(user_stories)
    clean_stories = 0
    stories_with_warnings = 0
    stories_with_issues = 0
    all_issues = []
    
    # Check each story
    for story_id, work_item_id in sorted(user_stories.items()):
        try:
            print(f"\n🔍 Checking {story_id} (ID: {work_item_id})...")
            
            # Get work item details
            work_item = manager.wit_client.get_work_item(work_item_id)
            
            # Analyze content
            issues, warnings = analyze_story_content(work_item)
            
            # Report results
            if issues:
                print(f"  🚨 ISSUES FOUND:")
                for issue in issues:
                    print(f"    - {issue}")
                stories_with_issues += 1
                all_issues.append({
                    'story_id': story_id,
                    'work_item_id': work_item_id,
                    'issues': issues,
                    'warnings': warnings
                })
            elif warnings:
                print(f"  ⚠️  WARNINGS:")
                for warning in warnings:
                    print(f"    - {warning}")
                stories_with_warnings += 1
            else:
                print(f"  ✅ Clean - no issues detected")
                clean_stories += 1
            
            # Rate limiting
            time.sleep(0.5)
            
        except Exception as e:
            print(f"  ❌ Error checking {story_id}: {e}")
            stories_with_issues += 1
            all_issues.append({
                'story_id': story_id,
                'work_item_id': work_item_id,
                'issues': [f"Failed to retrieve: {e}"],
                'warnings': []
            })
            continue
    
    # Final summary
    print("\n" + "=" * 80)
    print(f"📊 VERIFICATION SUMMARY:")
    print(f"  📋 Total stories analyzed: {total_stories}")
    print(f"  ✅ Clean stories: {clean_stories}")
    print(f"  ⚠️  Stories with warnings: {stories_with_warnings}")
    print(f"  🚨 Stories with issues: {stories_with_issues}")
    
    if stories_with_issues > 0:
        print(f"\n🚨 CRITICAL ISSUES REQUIRING FIXES:")
        for item in all_issues:
            if item['issues']:
                print(f"\n  {item['story_id']} (ID: {item['work_item_id']}):")
                for issue in item['issues']:
                    print(f"    - {issue}")
                print(f"    🔗 {org_url}/{project}/_workitems/edit/{item['work_item_id']}")
    
    # Success rate
    success_rate = (clean_stories / total_stories) * 100
    print(f"\n📈 Success rate: {success_rate:.1f}%")
    
    if success_rate >= 90:
        print("🎉 Excellent! Most stories are in good condition.")
    elif success_rate >= 75:
        print("👍 Good overall, but some stories need attention.")
    else:
        print("⚠️  Significant issues detected. Manual fixes recommended.")
    
    return all_issues


if __name__ == "__main__":
    main()