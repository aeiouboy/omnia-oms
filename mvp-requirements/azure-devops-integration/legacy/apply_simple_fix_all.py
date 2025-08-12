#!/usr/bin/env python3
"""
Apply simple formatting fix to all work items
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
    # Find the story section
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
            # Just add the line as-is, removing the leading dash if present
            clean_line = line[2:] if line.startswith('- ') else line
            if clean_line:
                acceptance_lines.append(clean_line)
        elif current_section == 'dependencies' and line and not line.startswith('**'):
            dep_lines.append(line)
        elif current_section == 'technical' and line and not line.startswith('**'):
            clean_line = line[2:] if line.startswith('- ') else line
            if clean_line:
                tech_lines.append(clean_line)
    
    # Join with line breaks
    story['acceptance_criteria'] = '\n'.join(acceptance_lines)
    story['dependencies'] = '\n'.join(dep_lines) or 'None'
    story['technical_notes'] = '\n'.join(tech_lines)
    
    return story


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
    
    print(f"🔧 Applying simple formatting to all work items...")
    
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
    
    # Update all work items
    for story_id, work_item_id in story_mapping.items():
        print(f"  🔧 Updating {story_id}...")
        
        try:
            # Extract and parse the story
            story_section = extract_story_section(full_content, story_id)
            if not story_section:
                print(f"    ⚠️ Could not find section for {story_id}")
                continue
                
            story = parse_story_simple(story_section)
            
            # Create simple, readable content
            description = f"As a {story['as_a']}, I want {story['i_want']}, so that {story['so_that']}."
            
            if story['dependencies'] and story['dependencies'] != 'None':
                description += f"\n\nDependencies:\n{story['dependencies']}"
            
            if story['technical_notes']:
                description += f"\n\nTechnical Notes:\n{story['technical_notes']}"
            
            acceptance_criteria = story['acceptance_criteria'] if story['acceptance_criteria'] else "To be defined during implementation"
            
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
    
    print(f"\n✨ All work items now have:")
    print(f"  • Clean, readable descriptions")
    print(f"  • Proper line breaks")
    print(f"  • Separate acceptance criteria section")
    print(f"  • Clear technical notes")
    
    print(f"\n🔗 View all work items:")
    print(f"  {ORGANIZATION_URL}/{PROJECT_NAME}/_backlogs/backlog")


if __name__ == "__main__":
    main()