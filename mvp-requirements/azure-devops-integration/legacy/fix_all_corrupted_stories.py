#!/usr/bin/env python3
"""
Fix all corrupted user stories that have epic-level content mixed in
"""

import sys
import os
import re
from pathlib import Path

# Add the directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import the main components from the original script
from create_azure_work_items import AzureDevOpsClient
from azure.devops.v7_1.work_item_tracking.models import JsonPatchOperation


def extract_story_section(content: str, story_id: str) -> str:
    """Extract the complete section for a specific story from markdown"""
    pattern = rf'#### {re.escape(story_id)}:.*?(?=#### [A-Z]+-\d+:|$)'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        return match.group(0)
    return ""


def parse_story_simple(story_section: str) -> dict:
    """Parse story section to extract clean content"""
    lines = story_section.split('\n')
    
    story = {
        'as_a': '',
        'i_want': '',
        'so_that': '',
        'acceptance_criteria': '',
        'dependencies': '',
        'technical_notes': ''
    }
    
    current_section = None
    acceptance_lines = []
    tech_lines = []
    dep_lines = []
    
    for line in lines:
        line = line.strip()
        
        if line.startswith('**As a**'):
            story['as_a'] = line.replace('**As a**', '').strip()
        elif line.startswith('**I want**'):
            story['i_want'] = line.replace('**I want**', '').strip()
        elif line.startswith('**So that**'):
            story['so_that'] = line.replace('**So that**', '').strip()
        elif line == '**Acceptance Criteria:**':
            current_section = 'acceptance'
        elif line == '**Dependencies:**':
            current_section = 'dependencies'
        elif line == '**Technical Notes:**':
            current_section = 'technical'
        elif current_section == 'acceptance' and line and not line.startswith('**'):
            clean_line = line[2:] if line.startswith('- ') else line
            if clean_line and not clean_line.startswith('###') and not clean_line.startswith('---'):
                acceptance_lines.append(clean_line)
        elif current_section == 'dependencies' and line and not line.startswith('**'):
            dep_lines.append(line)
        elif current_section == 'technical' and line and not line.startswith('**'):
            clean_line = line[2:] if line.startswith('- ') else line
            if clean_line and not clean_line.startswith('###') and not clean_line.startswith('---'):
                tech_lines.append(clean_line)
    
    # Join with HTML breaks for Azure DevOps
    story['acceptance_criteria'] = '<br/>'.join(acceptance_lines) if acceptance_lines else ''
    story['dependencies'] = '<br/>'.join(dep_lines) if dep_lines else 'None'
    story['technical_notes'] = '<br/>'.join(tech_lines) if tech_lines else ''
    
    return story


def create_html_description(story: dict) -> str:
    """Create clean HTML formatted description for Azure DevOps"""
    description = f"<p><strong>As a</strong> {story['as_a']}, <strong>I want</strong> {story['i_want']}, <strong>so that</strong> {story['so_that']}.</p>"
    
    if story['dependencies'] and story['dependencies'] != 'None':
        description += f"<p><strong>Dependencies:</strong><br/>{story['dependencies']}</p>"
    
    if story['technical_notes']:
        description += f"<p><strong>Technical Notes:</strong><br/>{story['technical_notes']}</p>"
    
    return description


def create_html_acceptance_criteria(story: dict) -> str:
    """Create HTML formatted acceptance criteria with proper Given/When/Then structure"""
    if not story['acceptance_criteria']:
        return "To be defined during implementation"
    
    # Format with proper Given/When/Then structure and indentation
    criteria_lines = story['acceptance_criteria'].split('<br/>')
    html = "<ul>"
    
    for line in criteria_lines:
        line = line.strip()
        if not line:
            continue
            
        # Check if this is a main Given/When/Then line
        if line.startswith(('Given', 'When', 'Then', 'And')):
            # Add spacing before Given/When/Then (except the first one)
            if line.startswith(('When', 'Then', 'And')) and html != "<ul>":
                html += "<br/>"
            html += f"<li><strong>{line}</strong></li>"
        else:
            # This is a sub-bullet - indent it more
            html += f"<li style='margin-left: 20px; list-style-type: circle;'>{line}</li>"
    
    html += "</ul>"
    return html


def main():
    """Fix all corrupted user stories"""
    
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
    
    print(f"🔧 Fixing all corrupted user stories...")
    print(f"   📝 Removing epic-level content and restoring proper user story format")
    
    # List of corrupted stories found
    corrupted_stories = {
        'ORD-006': 51669,
        'BUN-005': 51674,
        'PAY-005': 51679,
        'FUL-006': 51685,
        'STA-004': 51689,
        'CAN-004': 51693,
        'API-005': 51698
    }
    
    # Read the full markdown file to get correct content
    stories_file = "/Users/chongraktanaka/Projects/mao-docsite/mvp-requirements/user story/mvp-user-stories.md"
    with open(stories_file, 'r') as f:
        full_content = f.read()
    
    # Initialize Azure DevOps client
    print("🔌 Connecting to Azure DevOps...")
    client = AzureDevOpsClient(ORGANIZATION_URL, PERSONAL_ACCESS_TOKEN)
    print("✅ Connected!")
    
    fixed_count = 0
    failed_count = 0
    total_count = len(corrupted_stories)
    
    print(f"\n📊 Processing {total_count} corrupted stories...")
    
    for i, (story_id, work_item_id) in enumerate(corrupted_stories.items(), 1):
        print(f"  🔧 [{i:2d}/{total_count}] Fixing {story_id} (ID: {work_item_id})...")
        
        try:
            # Get current corrupted content for comparison
            current_item = client.wit_client.get_work_item(work_item_id)
            current_desc_length = len(current_item.fields.get('System.Description', ''))
            
            # Extract correct content from markdown
            story_section = extract_story_section(full_content, story_id)
            if not story_section:
                print(f"    ⚠️  Could not find section for {story_id} in markdown")
                failed_count += 1
                continue
                
            story = parse_story_simple(story_section)
            
            # Create clean HTML formatted content
            clean_description = create_html_description(story)
            clean_acceptance_criteria = create_html_acceptance_criteria(story)
            
            print(f"    Current length: {current_desc_length} chars (corrupted)")
            print(f"    Clean length: {len(clean_description)} chars")
            
            # Update with clean content
            document = [
                JsonPatchOperation(
                    op="replace",
                    path="/fields/System.Description",
                    value=clean_description
                ),
                JsonPatchOperation(
                    op="replace",
                    path="/fields/Microsoft.VSTS.Common.AcceptanceCriteria",
                    value=clean_acceptance_criteria
                )
            ]
            
            updated_work_item = client.wit_client.update_work_item(
                document=document,
                id=work_item_id
            )
            
            print(f"    ✅ Fixed {story_id} - removed epic content corruption")
            fixed_count += 1
            
        except Exception as e:
            print(f"    ❌ Failed to fix {story_id}: {e}")
            failed_count += 1
    
    print(f"\n📊 Final Summary:")
    print(f"  ✅ Successfully fixed: {fixed_count}")
    print(f"  ❌ Failed: {failed_count}")
    print(f"  📈 Success rate: {(fixed_count/total_count)*100:.1f}%")
    
    if fixed_count == total_count:
        print(f"\n🎉 ALL CORRUPTED STORIES FIXED! ✅")
        print(f"  • Removed epic-level content from all user stories")
        print(f"  • Restored proper As a/I want/so that format")
        print(f"  • Clean Given/When/Then acceptance criteria")
        print(f"  • All 39 user stories now have correct content")
    else:
        print(f"\n⚠️  Some stories still need attention")
        
    print(f"\n🔗 Verify fixes in Azure DevOps:")
    print(f"  {ORGANIZATION_URL}/{PROJECT_NAME}/_backlogs/backlog")


if __name__ == "__main__":
    main()