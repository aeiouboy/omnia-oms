#!/usr/bin/env python3
"""
Updates Azure DevOps work items with complete descriptions from the markdown file
This fixes the incomplete descriptions that were created initially
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


class ImprovedUserStoryParser:
    """Improved parser for extracting complete user stories from markdown file"""
    
    @staticmethod
    def parse_markdown_file(file_path: str) -> dict:
        """Parse the markdown file and extract complete user stories"""
        with open(file_path, 'r') as f:
            content = f.read()
        
        stories = {}
        
        # Split content by user story headers
        story_sections = re.split(r'#### ([A-Z]+-\d+): (.+)', content)
        
        # Process each story section
        for i in range(1, len(story_sections), 3):
            if i+2 < len(story_sections):
                story_id = story_sections[i]
                story_title = story_sections[i+1]
                story_content = story_sections[i+2]
                
                parsed_story = ImprovedUserStoryParser._parse_story_content(story_id, story_title, story_content)
                if parsed_story:
                    stories[story_id] = parsed_story
        
        return stories
    
    @staticmethod
    def _parse_story_content(story_id: str, title: str, content: str) -> dict:
        """Parse individual story content with all details"""
        story = {
            'id': story_id,
            'title': title,
            'priority': 'P1',
            'story_points': 5,
            'as_a': '',
            'i_want': '',
            'so_that': '',
            'acceptance_criteria': [],
            'dependencies': 'None',
            'technical_notes': ''
        }
        
        lines = content.strip().split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines and next story headers
            if not line or line.startswith('#### '):
                if line.startswith('#### '):
                    break
                continue
            
            # Parse priority and story points
            if line.startswith('**Priority:**'):
                story['priority'] = line.split('**Priority:**')[1].strip()
            elif line.startswith('**Story Points:**'):
                try:
                    story['story_points'] = int(line.split('**Story Points:**')[1].strip())
                except:
                    story['story_points'] = 5
            
            # Parse user story statement
            elif line.startswith('**As a**'):
                story['as_a'] = line.replace('**As a**', '').strip()
            elif line.startswith('**I want**'):
                story['i_want'] = line.replace('**I want**', '').strip()
            elif line.startswith('**So that**'):
                story['so_that'] = line.replace('**So that**', '').strip()
            
            # Identify sections
            elif line.startswith('**Acceptance Criteria:**'):
                current_section = 'acceptance'
            elif line.startswith('**Dependencies:**'):
                current_section = 'dependencies'
            elif line.startswith('**Technical Notes:**'):
                current_section = 'technical'
            
            # Parse section content
            elif current_section == 'acceptance':
                if line.startswith('-') and not line.startswith('**'):
                    criteria = line[1:].strip()
                    if criteria:
                        story['acceptance_criteria'].append(criteria)
            elif current_section == 'dependencies':
                if not line.startswith('**'):
                    deps = line.strip()
                    if deps:
                        story['dependencies'] = deps
            elif current_section == 'technical':
                if not line.startswith('**'):
                    if story['technical_notes']:
                        story['technical_notes'] += '\n'
                    story['technical_notes'] += line
        
        return story


def create_html_description(story: dict) -> str:
    """Create properly formatted HTML description for Azure DevOps"""
    
    # Format acceptance criteria as HTML list
    criteria_html = ""
    if story['acceptance_criteria']:
        criteria_html = "<ul>\n"
        for criteria in story['acceptance_criteria']:
            # Handle nested criteria (with indentation)
            if criteria.strip().startswith('-'):
                criteria_html += f"  <li><ul><li>{criteria.strip()[1:].strip()}</li></ul></li>\n"
            else:
                criteria_html += f"  <li>{criteria}</li>\n"
        criteria_html += "</ul>"
    else:
        criteria_html = "<p>To be defined during implementation</p>"
    
    # Format technical notes
    tech_notes_html = story['technical_notes'].replace('\n', '<br/>') if story['technical_notes'] else "None"
    
    # Create complete HTML description
    html_description = f"""
<h3>User Story</h3>
<p><strong>As a</strong> {story['as_a']}<br/>
<strong>I want</strong> {story['i_want']}<br/>
<strong>So that</strong> {story['so_that']}</p>

<h3>Acceptance Criteria</h3>
{criteria_html}

<h3>Dependencies</h3>
<p>{story['dependencies']}</p>

<h3>Technical Notes</h3>
<p>{tech_notes_html}</p>
"""
    
    return html_description.strip()


def main():
    """Main execution function"""
    
    # Load from .env file
    env_file = Path(__file__).parent / '.env'
    if env_file.exists():
        print("Loading configuration from .env file...")
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
    
    print(f"🔧 Configuration:")
    print(f"  Organization: {ORGANIZATION_URL}")
    print(f"  Project: {PROJECT_NAME}")
    
    # Load work item mapping
    mapping_file = Path(__file__).parent / "work_item_mapping.json"
    if not mapping_file.exists():
        print("❌ Error: work_item_mapping.json not found!")
        return
    
    with open(mapping_file, 'r') as f:
        mapping = json.load(f)
    
    story_mapping = mapping.get('stories', {})
    print(f"📊 Found {len(story_mapping)} stories to update")
    
    # Parse the markdown file with improved parser
    stories_file = "/Users/chongraktanaka/Projects/mao-docsite/mvp-requirements/user story/mvp-user-stories.md"
    print("📖 Parsing user stories with improved parser...")
    
    parser = ImprovedUserStoryParser()
    stories = parser.parse_markdown_file(stories_file)
    
    print(f"📋 Parsed {len(stories)} stories from markdown")
    
    # Initialize Azure DevOps client
    print("🔌 Connecting to Azure DevOps...")
    try:
        client = AzureDevOpsClient(ORGANIZATION_URL, PERSONAL_ACCESS_TOKEN)
        print("✅ Connected successfully!")
    except Exception as e:
        print(f"❌ Error connecting: {e}")
        return
    
    # Update work items
    print(f"🔄 Updating work item descriptions...")
    
    updated_count = 0
    failed_count = 0
    
    for story_id, work_item_id in story_mapping.items():
        if story_id in stories:
            story = stories[story_id]
            
            try:
                # Create HTML description
                html_description = create_html_description(story)
                
                # Create update document
                document = [
                    JsonPatchOperation(
                        op="replace",
                        path="/fields/System.Description",
                        value=html_description
                    ),
                    JsonPatchOperation(
                        op="replace",
                        path="/fields/Microsoft.VSTS.Scheduling.StoryPoints",
                        value=story['story_points']
                    )
                ]
                
                # Update the work item
                updated_work_item = client.wit_client.update_work_item(
                    document=document,
                    id=work_item_id
                )
                
                print(f"  ✅ Updated {story_id} (ID: {work_item_id})")
                updated_count += 1
                
            except Exception as e:
                print(f"  ❌ Failed to update {story_id}: {e}")
                failed_count += 1
        else:
            print(f"  ⚠️ Story {story_id} not found in markdown file")
            failed_count += 1
    
    print(f"\n📊 Update Summary:")
    print(f"  ✅ Successfully updated: {updated_count}")
    print(f"  ❌ Failed: {failed_count}")
    
    print(f"\n🔗 View updated work items:")
    print(f"  {ORGANIZATION_URL}/{PROJECT_NAME}/_backlogs/backlog")
    
    # Test a specific work item
    if story_mapping.get('ORD-002'):
        work_item_id = story_mapping['ORD-002']
        print(f"\n🔍 Check ORD-002 specifically:")
        print(f"  {ORGANIZATION_URL}/{PROJECT_NAME}/_workitems/edit/{work_item_id}")


if __name__ == "__main__":
    main()