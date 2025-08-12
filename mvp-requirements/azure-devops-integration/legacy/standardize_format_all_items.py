#!/usr/bin/env python3
"""
Standardize format for all work items (epics and stories):
- Clean Description field: User Story, Dependencies, Technical Notes only
- Acceptance Criteria field: Properly formatted HTML with nested bullets
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


class StandardFormatProcessor:
    """Processor that standardizes format for all work items"""
    
    @staticmethod
    def parse_markdown_file(file_path: str) -> dict:
        """Parse the markdown file and extract user stories"""
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
                
                parsed_story = StandardFormatProcessor._parse_story_content(story_id, story_title, story_content)
                if parsed_story:
                    stories[story_id] = parsed_story
        
        return stories
    
    @staticmethod
    def _parse_story_content(story_id: str, title: str, content: str) -> dict:
        """Parse individual story content"""
        story = {
            'id': story_id,
            'title': title,
            'priority': 'P1',
            'story_points': 5,
            'as_a': '',
            'i_want': '',
            'so_that': '',
            'acceptance_criteria_structured': [],
            'dependencies': 'None',
            'technical_notes': ''
        }
        
        lines = content.strip().split('\n')
        current_section = None
        in_acceptance = False
        in_technical = False
        acceptance_buffer = []
        technical_buffer = []
        
        for line in lines:
            original_line = line
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
                in_acceptance = True
                in_technical = False
                current_section = 'acceptance'
            elif line.startswith('**Dependencies:**'):
                in_acceptance = False
                in_technical = False
                current_section = 'dependencies'
            elif line.startswith('**Technical Notes:**'):
                in_acceptance = False
                in_technical = True
                current_section = 'technical'
            
            # Parse acceptance criteria
            elif in_acceptance and current_section == 'acceptance':
                if line.startswith('-') and not line.startswith('**'):
                    criteria = line[1:].strip()
                    if criteria:
                        acceptance_buffer.append(criteria)
            elif current_section == 'dependencies' and not in_acceptance and not in_technical:
                if not line.startswith('**') and line:
                    story['dependencies'] = line
            elif in_technical and current_section == 'technical':
                if not line.startswith('**') and not line.startswith('---'):
                    technical_buffer.append(line)
        
        # Structure acceptance criteria
        story['acceptance_criteria_structured'] = StandardFormatProcessor._structure_acceptance_criteria(acceptance_buffer)
        
        # Clean up technical notes
        if technical_buffer:
            story['technical_notes'] = '\n'.join(technical_buffer)
        
        return story
    
    @staticmethod
    def _structure_acceptance_criteria(criteria_list):
        """Structure acceptance criteria into proper Given/When/Then groups"""
        structured = []
        current_scenario = None
        
        for criteria in criteria_list:
            criteria_lower = criteria.lower()
            
            if criteria_lower.startswith('given'):
                # Start a new scenario
                current_scenario = {
                    'given': criteria,
                    'when_then': []
                }
                structured.append(current_scenario)
            elif criteria_lower.startswith('when') or criteria_lower.startswith('then') or criteria_lower.startswith('and'):
                # Add to current scenario
                if current_scenario:
                    current_scenario['when_then'].append(criteria)
                else:
                    # If no Given found, create a simple item
                    structured.append({
                        'given': criteria,
                        'when_then': []
                    })
        
        # If no Given/When/Then structure found, treat as simple criteria
        if not structured and criteria_list:
            for criteria in criteria_list:
                structured.append({
                    'given': criteria,
                    'when_then': []
                })
        
        return structured


def create_clean_description(story: dict) -> str:
    """Create clean HTML description WITHOUT acceptance criteria"""
    
    # Format technical notes (convert markdown-like formatting to HTML)
    tech_notes = story['technical_notes']
    if tech_notes:
        # Convert code blocks
        tech_notes = re.sub(r'```(\w+)?\n(.*?)```', r'<pre><code>\2</code></pre>', tech_notes, flags=re.DOTALL)
        # Convert bold text  
        tech_notes = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', tech_notes)
        # Convert line breaks
        tech_notes = tech_notes.replace('\n', '<br/>')
    else:
        tech_notes = "None"
    
    # Create clean HTML description WITHOUT acceptance criteria
    html_description = f"""<h3>User Story</h3>
<p><strong>As a</strong> {story['as_a']}<br/>
<strong>I want</strong> {story['i_want']}<br/>
<strong>So that</strong> {story['so_that']}</p>

<h3>Dependencies</h3>
<p>{story['dependencies']}</p>

<h3>Technical Notes</h3>
<p>{tech_notes}</p>"""
    
    return html_description


def create_html_acceptance_criteria(story: dict) -> str:
    """Create properly formatted HTML acceptance criteria for the dedicated field"""
    
    if not story['acceptance_criteria_structured']:
        return "To be defined during implementation"
    
    html = "<ul>\n"
    
    for scenario in story['acceptance_criteria_structured']:
        # Add the Given as main bullet (bold)
        html += f'  <li><strong>{scenario["given"]}</strong>\n'
        
        # Add When/Then as nested sub-bullets if they exist
        if scenario['when_then']:
            html += '    <ul>\n'
            for sub_criteria in scenario['when_then']:
                html += f'      <li>{sub_criteria}</li>\n'
            html += '    </ul>\n'
        
        html += '  </li>\n'
    
    html += "</ul>"
    return html


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
    epic_mapping = mapping.get('epics', {})
    
    print(f"📊 Found {len(story_mapping)} stories and {len(epic_mapping)} epics to standardize")
    
    # Parse the markdown file
    stories_file = "/Users/chongraktanaka/Projects/mao-docsite/mvp-requirements/user story/mvp-user-stories.md"
    print("📖 Parsing user stories...")
    
    processor = StandardFormatProcessor()
    stories = processor.parse_markdown_file(stories_file)
    
    print(f"📋 Parsed {len(stories)} stories from markdown")
    
    # Initialize Azure DevOps client
    print("🔌 Connecting to Azure DevOps...")
    try:
        client = AzureDevOpsClient(ORGANIZATION_URL, PERSONAL_ACCESS_TOKEN)
        print("✅ Connected successfully!")
    except Exception as e:
        print(f"❌ Error connecting: {e}")
        return
    
    # Standardize format for all work items
    print(f"🔄 Standardizing format for all work items...")
    
    updated_count = 0
    failed_count = 0
    
    # Update user stories
    print(f"\n📝 Updating {len(story_mapping)} user stories...")
    for story_id, work_item_id in story_mapping.items():
        if story_id in stories:
            story = stories[story_id]
            try:
                # Create clean description without acceptance criteria
                clean_description = create_clean_description(story)
                
                # Create HTML formatted acceptance criteria for dedicated field
                html_acceptance_criteria = create_html_acceptance_criteria(story)
                
                # Create update document
                document = [
                    JsonPatchOperation(
                        op="replace",
                        path="/fields/System.Description",
                        value=clean_description
                    ),
                    JsonPatchOperation(
                        op="replace",
                        path="/fields/Microsoft.VSTS.Common.AcceptanceCriteria",
                        value=html_acceptance_criteria
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
    
    # Update epics (they may not have acceptance criteria, but we'll standardize the description format)
    print(f"\n🎯 Updating {len(epic_mapping)} epics...")
    for epic_name, work_item_id in epic_mapping.items():
        try:
            # For epics, create a simple clean description
            epic_description = f"""<h3>Epic Overview</h3>
<p>{epic_name} functionality for the MAO MVP implementation</p>

<h3>Scope</h3>
<p>This epic encompasses all user stories and features related to {epic_name.lower()} in the Manhattan Active Omni system.</p>

<h3>Business Value</h3>
<p>Delivers core {epic_name.lower()} capabilities essential for the MVP launch.</p>"""
            
            # Create update document for epic
            document = [
                JsonPatchOperation(
                    op="replace",
                    path="/fields/System.Description",
                    value=epic_description
                ),
                # Clear acceptance criteria field for epics (they typically don't have detailed criteria)
                JsonPatchOperation(
                    op="replace",
                    path="/fields/Microsoft.VSTS.Common.AcceptanceCriteria",
                    value=""
                )
            ]
            
            # Update the epic
            updated_work_item = client.wit_client.update_work_item(
                document=document,
                id=work_item_id
            )
            
            print(f"  ✅ Updated Epic: {epic_name} (ID: {work_item_id})")
            updated_count += 1
            
        except Exception as e:
            print(f"  ❌ Failed to update epic {epic_name}: {e}")
            failed_count += 1
    
    print(f"\n📊 Final Summary:")
    print(f"  ✅ Successfully updated: {updated_count}")
    print(f"  ❌ Failed: {failed_count}")
    print(f"\n✨ All work items now have standardized format!")
    print(f"  📄 Stories: Clean Description + HTML Acceptance Criteria in dedicated field")
    print(f"  🎯 Epics: Structured Description with business context")
    print(f"  🎨 Consistent HTML formatting throughout")
    print(f"  📱 Proper nested bullet points for Given/When/Then structure")


if __name__ == "__main__":
    main()