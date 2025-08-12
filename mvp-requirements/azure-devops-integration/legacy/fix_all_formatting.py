#!/usr/bin/env python3
"""
Apply improved HTML formatting to all work items with proper Given/When/Then structure
"""

import sys
import os
import json
import re
from pathlib import Path

# Add the directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import the main components from the original script
from create_azure_work_items import AzureDevOpsClient
from azure.devops.v7_1.work_item_tracking.models import JsonPatchOperation


def extract_story_section(content: str, story_id: str) -> str:
    """Extract the complete section for a specific story"""
    pattern = rf'#### {re.escape(story_id)}:.*?(?=#### [A-Z]+-\d+:|$)'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        return match.group(0)
    return ""


def parse_story_simple(story_section: str) -> dict:
    """Parse story section in the simplest way possible"""
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
            if clean_line:
                acceptance_lines.append(clean_line)
        elif current_section == 'dependencies' and line and not line.startswith('**'):
            dep_lines.append(line)
        elif current_section == 'technical' and line and not line.startswith('**'):
            clean_line = line[2:] if line.startswith('- ') else line
            if clean_line:
                tech_lines.append(clean_line)
    
    # Join with HTML breaks for Azure DevOps
    story['acceptance_criteria'] = '<br/>'.join(acceptance_lines) if acceptance_lines else ''
    story['dependencies'] = '<br/>'.join(dep_lines) if dep_lines else 'None'
    story['technical_notes'] = '<br/>'.join(tech_lines) if tech_lines else ''
    
    return story


def create_html_description(story: dict) -> str:
    """Create HTML formatted description for Azure DevOps"""
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
    """Main execution function"""
    
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
    
    print(f"🔧 Applying improved HTML formatting to all work items...")
    print(f"   ✨ Given/When/Then structure with proper spacing")
    print(f"   ✨ Indented sub-bullets with circle bullets")
    print(f"   ✨ Bold headers for main sections")
    
    # Load work item mapping
    mapping_file = Path(__file__).parent / "work_item_mapping.json"
    with open(mapping_file, 'r') as f:
        mapping = json.load(f)
    
    story_mapping = mapping.get('stories', {})
    
    # Read the full markdown file
    stories_file = "/Users/chongraktanaka/Projects/mao-docsite/mvp-requirements/user story/mvp-user-stories.md"
    with open(stories_file, 'r') as f:
        full_content = f.read()
    
    # Initialize Azure DevOps client
    print("🔌 Connecting to Azure DevOps...")
    client = AzureDevOpsClient(ORGANIZATION_URL, PERSONAL_ACCESS_TOKEN)
    print("✅ Connected!")
    
    updated_count = 0
    failed_count = 0
    total_count = len(story_mapping)
    
    print(f"\n📊 Processing {total_count} work items...")
    
    # Update all work items
    for i, (story_id, work_item_id) in enumerate(story_mapping.items(), 1):
        print(f"  🔧 [{i:2d}/{total_count}] Updating {story_id}...")
        
        try:
            # Extract and parse the story
            story_section = extract_story_section(full_content, story_id)
            if not story_section:
                print(f"    ⚠️  Could not find section for {story_id}")
                failed_count += 1
                continue
                
            story = parse_story_simple(story_section)
            
            # Create improved HTML formatted content
            description = create_html_description(story)
            acceptance_criteria = create_html_acceptance_criteria(story)
            
            # Update the work item
            document = [
                JsonPatchOperation(
                    op="replace",
                    path="/fields/System.Description",
                    value=description
                ),
                JsonPatchOperation(
                    op="replace",
                    path="/fields/Microsoft.VSTS.Common.AcceptanceCriteria",
                    value=acceptance_criteria
                )
            ]
            
            updated_work_item = client.wit_client.update_work_item(
                document=document,
                id=work_item_id
            )
            
            print(f"    ✅ Updated {story_id} (ID: {work_item_id})")
            updated_count += 1
            
        except Exception as e:
            print(f"    ❌ Failed to update {story_id}: {e}")
            failed_count += 1
    
    print(f"\n📊 Final Summary:")
    print(f"  ✅ Successfully updated: {updated_count}")
    print(f"  ❌ Failed: {failed_count}")
    print(f"  📈 Success rate: {(updated_count/total_count)*100:.1f}%")
    
    print(f"\n✨ All work items now have:")
    print(f"  • Clean HTML formatting with proper paragraph breaks")
    print(f"  • Bold Given/When/Then headers with proper spacing")
    print(f"  • Indented sub-bullets with circle style")
    print(f"  • Clear visual hierarchy for easy scanning")
    print(f"  • Separated technical notes and dependencies")
    
    print(f"\n🔗 View all updated work items:")
    print(f"  {ORGANIZATION_URL}/{PROJECT_NAME}/_backlogs/backlog")
    
    # Show a few sample links
    print(f"\n🎯 Sample work items to check:")
    sample_stories = list(story_mapping.items())[:3]
    for story_id, work_item_id in sample_stories:
        print(f"  • {story_id}: {ORGANIZATION_URL}/{PROJECT_NAME}/_workitems/edit/{work_item_id}")


if __name__ == "__main__":
    main()