#!/usr/bin/env python3
"""
Verify Mermaid Update Script
Verifies that all UC workflow files have been updated with correct format:
1. Flowcharts moved below Process Steps
2. Numeric characters removed from Mermaid diagrams
3. Azure DevOps compatible formatting
4. Check Azure DevOps work items for Mermaid diagrams
"""

import sys
import re
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from azure_devops_manager import AzureDevOpsManager, ConfigManager


def check_workflow_format(file_path):
    """Check if a workflow file follows the correct format"""
    issues = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check 1: Flowchart should come after Process Steps
        sections = re.findall(r'^## (.+)$', content, re.MULTILINE)
        if sections:
            process_steps_index = None
            diagram_index = None
            
            for i, section in enumerate(sections):
                if 'Process Steps' in section:
                    process_steps_index = i
                elif 'System Workflow Diagram' in section or 'Workflow Diagram' in section:
                    diagram_index = i
                    
            if process_steps_index is not None and diagram_index is not None:
                if diagram_index < process_steps_index:
                    issues.append("❌ Flowchart appears before Process Steps section")
                else:
                    issues.append("✅ Flowchart correctly positioned after Process Steps")
            elif diagram_index is None:
                issues.append("⚠️  No System Workflow Diagram section found")
            else:
                issues.append("✅ Flowchart positioning OK")
        
        # Check 2: Look for numeric characters in Mermaid diagrams
        mermaid_blocks = re.findall(r'```mermaid\n(.*?)```', content, re.DOTALL)
        if mermaid_blocks:
            for block in mermaid_blocks:
                # Check for problematic numeric patterns
                numeric_issues = []
                
                # Check for "Rule 1:", "Cal 1:", etc.
                if re.search(r'Rule \d+:', block):
                    numeric_issues.append("Rule [number]:")
                if re.search(r'Cal \d+:', block):
                    numeric_issues.append("Cal [number]:")
                if re.search(r'Status: \d+', block):
                    numeric_issues.append("Status: [number]")
                if re.search(r'subGraph\d+', block):
                    numeric_issues.append("subGraph[number]")
                
                if numeric_issues:
                    issues.append(f"❌ Numeric patterns found in Mermaid: {', '.join(numeric_issues)}")
                else:
                    issues.append("✅ No problematic numeric patterns in Mermaid")
        else:
            issues.append("⚠️  No Mermaid diagrams found")
        
        # Check 3: Verify proper section structure
        required_sections = ['Process Steps']
        missing_sections = []
        
        for section in required_sections:
            if section not in content:
                missing_sections.append(section)
                
        if missing_sections:
            issues.append(f"❌ Missing required sections: {', '.join(missing_sections)}")
        else:
            issues.append("✅ All required sections present")
            
        # Check 4: Azure DevOps compatibility
        azure_issues = []
        
        # Check for unsupported characters or patterns
        if '→' in content:
            azure_issues.append("Unicode arrows (→)")
        if re.search(r'[^\x00-\x7F]', content):
            # Count non-ASCII characters (excluding common ones we want)
            non_ascii = re.findall(r'[^\x00-\x7F•×]', content)
            if non_ascii:
                unique_chars = list(set(non_ascii))
                if len(unique_chars) > 5:  # Allow some special chars
                    azure_issues.append(f"Many non-ASCII characters: {unique_chars[:5]}...")
                    
        if azure_issues:
            issues.append(f"⚠️  Potential Azure DevOps issues: {', '.join(azure_issues)}")
        else:
            issues.append("✅ Azure DevOps compatible formatting")
            
    except Exception as e:
        issues.append(f"❌ Error reading file: {str(e)}")
        
    return issues


def verify_local_workflows():
    """Verify local workflow files format"""
    print("🔍 Verifying Local Workflow Files Format")
    print("=" * 60)
    
    # Define workflow files to check
    workflow_files = [
        "UC-001-System-Workflow.md",
        "UC-002-Bundle-Order-Workflow.md", 
        "UC-003-Pack-Order-Workflow.md",
        "UC-004-Bundle-Pack-Workflow.md",
        "UC-005-Substitution-Processing-Workflow.md",
        "UC-006-Order-Cancellation-Workflow.md",
        "UC-007-Delivery-Tracking-Workflow.md"
    ]
    
    base_path = Path(__file__).parent.parent.parent / "user story"
    
    total_files = len(workflow_files)
    passed_files = 0
    
    for filename in workflow_files:
        file_path = base_path / filename
        
        print(f"\n📄 Checking: {filename}")
        print("-" * 40)
        
        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            continue
            
        issues = check_workflow_format(file_path)
        
        # Count passed checks
        passed_checks = sum(1 for issue in issues if issue.startswith("✅"))
        total_checks = len([i for i in issues if i.startswith(("✅", "❌"))])
        
        for issue in issues:
            print(f"   {issue}")
            
        if all(not issue.startswith("❌") for issue in issues):
            passed_files += 1
            print(f"   📊 Status: PASSED ({passed_checks}/{total_checks} checks)")
        else:
            print(f"   📊 Status: NEEDS ATTENTION ({passed_checks}/{total_checks} checks)")
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 LOCAL WORKFLOW VERIFICATION SUMMARY")
    print("=" * 60)
    print(f"✅ Files Passed: {passed_files}/{total_files}")
    print(f"⚠️  Files Need Attention: {total_files - passed_files}/{total_files}")
    
    if passed_files == total_files:
        print("\n🎉 ALL LOCAL WORKFLOWS READY FOR AZURE DEVOPS!")
        print("   • Flowcharts positioned correctly")
        print("   • No problematic numeric characters")
        print("   • Azure DevOps compatible formatting")
    else:
        print(f"\n⚠️  {total_files - passed_files} files need updates before Azure DevOps deployment")
    
    return passed_files == total_files


def verify_azure_devops_stories():
    """Verify Mermaid diagrams were added to user stories in Azure DevOps"""
    
    print("\n🔍 Verifying Azure DevOps User Stories")
    print("=" * 60)
    
    # Load configuration
    config_dir = Path(__file__).parent.parent
    try:
        org_url, project, pat = ConfigManager.load_config(config_dir)
        print(f"🔧 Configuration loaded for project: {project}")
    except ValueError as e:
        print(f"❌ {e}")
        return False
    
    # Initialize Azure DevOps manager
    print("🔌 Connecting to Azure DevOps...")
    try:
        manager = AzureDevOpsManager(org_url, pat, project)
        print("✅ Connected successfully!")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False
    
    # Load work item mapping
    mapping = ConfigManager.load_work_item_mapping(config_dir)
    story_ids = mapping.get('stories', {})
    
    if not story_ids:
        print("⚠️  No user stories found in mapping file")
        return False
    
    print(f"\n🔍 Checking {len(story_ids)} user stories for Mermaid diagrams...")
    
    mermaid_count = 0
    no_mermaid_count = 0
    
    for story_id, work_item_id in story_ids.items():
        try:
            # Get work item
            work_item = manager.wit_client.get_work_item(work_item_id)
            description = work_item.fields.get('System.Description', '')
            
            # Check for Mermaid diagram indicators
            has_mermaid = ('mermaid-diagram' in description or 
                          'System Workflow Diagram' in description or
                          'language-mermaid' in description or
                          'flowchart TD' in description)
            
            if has_mermaid:
                print(f"✅ {story_id} (ID: {work_item_id}) - Mermaid diagram present")
                mermaid_count += 1
            else:
                print(f"❌ {story_id} (ID: {work_item_id}) - No Mermaid diagram found")
                no_mermaid_count += 1
                
        except Exception as e:
            print(f"❌ Error checking {story_id} (ID: {work_item_id}): {e}")
            no_mermaid_count += 1
    
    # Summary
    print(f"\n📊 Azure DevOps Verification Summary:")
    print(f"  ✅ Stories with Mermaid diagrams: {mermaid_count}")
    print(f"  ❌ Stories without Mermaid diagrams: {no_mermaid_count}")
    print(f"  📋 Total stories checked: {len(story_ids)}")
    
    if mermaid_count == len(story_ids):
        print(f"\n🎉 All {len(story_ids)} user stories have Mermaid diagrams!")
        print(f"🔗 View project at: {org_url}/{project}/_backlogs/backlog/")
        return True
    elif mermaid_count > 0:
        print(f"\n⚠️  {mermaid_count}/{len(story_ids)} stories have Mermaid diagrams")
        print(f"🔗 View project at: {org_url}/{project}/_backlogs/backlog/")
        return False
    else:
        print(f"\n❌ No Mermaid diagrams found in any stories")
        return False


def main():
    """Main verification function - checks both local files and Azure DevOps"""
    
    print("🚀 MERMAID UPDATE VERIFICATION")
    print("🚀" * 30)
    print("Comprehensive verification of Mermaid updates for Azure DevOps")
    print("=" * 80)
    
    # Step 1: Verify local workflow files
    local_workflows_ready = verify_local_workflows()
    
    # Step 2: Check Azure DevOps user stories format 
    azure_stories_ready = check_azure_devops_story_format()
    
    # Step 3: Verify Azure DevOps work items (if configured)
    azure_workitems_ready = False
    try:
        azure_workitems_ready = verify_azure_devops_stories()
    except Exception as e:
        print(f"\n⚠️  Azure DevOps verification skipped: {e}")
    
    # Final summary
    print("\n" + "🚀" * 30)
    print("FINAL VERIFICATION RESULTS")
    print("🚀" * 30)
    
    print(f"✅ Local Workflows Ready: {'YES' if local_workflows_ready else 'NO'}")
    print(f"✅ Azure Stories Format Ready: {'YES' if azure_stories_ready else 'NO'}")
    print(f"✅ Azure Work Items Updated: {'YES' if azure_workitems_ready else 'SKIPPED/NO'}")
    
    all_ready = local_workflows_ready and azure_stories_ready
    
    if all_ready:
        print("\n🎉 ALL SYSTEMS GO FOR AZURE DEVOPS!")
        print("   • Local workflow files properly formatted")
        print("   • Azure DevOps user stories ready")
        print("   • No problematic numeric characters")
        print("   • Flowcharts positioned correctly")
        
        print("\n📝 NEXT STEPS:")
        print("   1. Import user stories to Azure DevOps")
        print("   2. Test Mermaid rendering in Azure DevOps")
        print("   3. Create work item relationships")
        print("   4. Assign to appropriate iterations")
        
    else:
        print("\n⚠️  SOME ISSUES NEED ATTENTION")
        if not local_workflows_ready:
            print("   - Fix local workflow file formatting")
        if not azure_stories_ready:
            print("   - Fix Azure DevOps user stories format")
            
        print("\n📝 RECOMMENDED ACTIONS:")
        print("   1. Review and fix flagged issues above")
        print("   2. Re-run this script to verify fixes")
        print("   3. Test with a single work item import first")
    
    return all_ready


def check_azure_devops_story_format():
    """Check the Azure DevOps User Stories format"""
    print("\n🔍 Checking Azure DevOps User Stories Format")
    print("=" * 60)
    
    story_file = Path(__file__).parent.parent.parent / "user story" / "Azure-DevOps-User-Stories.md"
    
    if not story_file.exists():
        print("❌ Azure-DevOps-User-Stories.md not found")
        return False
        
    try:
        with open(story_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        checks = []
        
        # Check for required Azure DevOps elements
        if re.search(r'\*\*Story ID:\*\*', content):
            checks.append("✅ Story ID format present")
        else:
            checks.append("❌ Missing Story ID format")
            
        if re.search(r'\*\*Priority:\*\*', content):
            checks.append("✅ Priority format present")
        else:
            checks.append("❌ Missing Priority format")
            
        if re.search(r'\*\*Story Points:\*\*', content):
            checks.append("✅ Story Points format present")
        else:
            checks.append("❌ Missing Story Points format")
            
        if re.search(r'As a .+ I want .+ so that', content, re.IGNORECASE):
            checks.append("✅ User Story format (As a... I want... so that...)")
        else:
            checks.append("❌ Missing proper User Story format")
            
        if re.search(r'### Acceptance Criteria', content):
            checks.append("✅ Acceptance Criteria sections present")
        else:
            checks.append("❌ Missing Acceptance Criteria sections")
            
        # Count user stories
        story_count = len(re.findall(r'## User Story \d+:', content))
        checks.append(f"📊 Found {story_count} user stories")
        
        for check in checks:
            print(f"   {check}")
            
        passed = all(not check.startswith("❌") for check in checks)
        
        if passed:
            print("   🎉 Azure DevOps User Stories format is READY!")
        else:
            print("   ⚠️  User Stories format needs attention")
            
        return passed
        
    except Exception as e:
        print(f"❌ Error checking user stories: {str(e)}")
        return False


if __name__ == "__main__":
    main()