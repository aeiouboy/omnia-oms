#!/usr/bin/env python3
"""
Move acceptance criteria back to Description field with proper HTML formatting
This will provide better readability and proper indentation for Given/When/Then structure.
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


class DescriptionWithCriteriaParser:
    """Parser that creates complete descriptions including properly formatted acceptance criteria"""
    
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
                
                parsed_story = DescriptionWithCriteriaParser._parse_story_content(story_id, story_title, story_content)
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
        story['acceptance_criteria_structured'] = DescriptionWithCriteriaParser._structure_acceptance_criteria(acceptance_buffer)
        
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


def create_complete_description_with_criteria(story: dict) -> str:
    """Create complete HTML description including properly formatted acceptance criteria"""
    
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
    
    # Create properly formatted acceptance criteria HTML with indentation
    criteria_html = ""
    if story['acceptance_criteria_structured']:
        criteria_html = "<ul>\n"
        for scenario in story['acceptance_criteria_structured']:
            # Add the Given as main bullet with proper indentation
            criteria_html += f'  <li><strong>{scenario["given"]}</strong>\n'
            
            # Add When/Then as nested sub-bullets with proper indentation
            if scenario['when_then']:
                criteria_html += '    <ul>\n'
                for sub_criteria in scenario['when_then']:
                    criteria_html += f'      <li>{sub_criteria}</li>\n'
                criteria_html += '    </ul>\n'
            
            criteria_html += '  </li>\n'
        criteria_html += "</ul>"
    else:
        criteria_html = "<p>To be defined during implementation</p>"
    
    # Create complete HTML description with acceptance criteria included
    html_description = f"""<h3>User Story</h3>
<p><strong>As a</strong> {story['as_a']}<br/>
<strong>I want</strong> {story['i_want']}<br/>
<strong>So that</strong> {story['so_that']}</p>

<h3>Acceptance Criteria</h3>
{criteria_html}

<h3>Dependencies</h3>
<p>{story['dependencies']}</p>

<h3>Technical Notes</h3>
<p>{tech_notes}</p>"""
    
    return html_description


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
    
    # Parse the markdown file
    stories_file = "/Users/chongraktanaka/Projects/mao-docsite/mvp-requirements/user story/mvp-user-stories.md"
    print("📖 Parsing user stories...")
    
    parser = DescriptionWithCriteriaParser()
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
    
    # Update work items with complete descriptions including criteria
    print(f"🔄 Moving acceptance criteria to Description field with proper HTML formatting...")
    
    fixed_count = 0
    failed_count = 0
    
    # Test with just ORD-002 first
    test_story_id = 'ORD-002'
    if test_story_id in story_mapping and test_story_id in stories:
        work_item_id = story_mapping[test_story_id]
        story = stories[test_story_id]
        
        try:
            # Create complete description with properly formatted acceptance criteria
            complete_description = create_complete_description_with_criteria(story)
            
            print(f"\n--- Preview for {test_story_id} ---")
            print("Complete Description with Acceptance Criteria:")
            print(complete_description[:400] + "..." if len(complete_description) > 400 else complete_description)
            print("--- End Preview ---\n")
            
            # Create update document - clear the separate Acceptance Criteria field
            document = [
                JsonPatchOperation(
                    op="replace",
                    path="/fields/System.Description",
                    value=complete_description
                ),
                JsonPatchOperation(
                    op="replace",
                    path="/fields/Microsoft.VSTS.Common.AcceptanceCriteria",
                    value=""  # Clear the separate field
                )
            ]
            
            # Update the work item
            updated_work_item = client.wit_client.update_work_item(
                document=document,
                id=work_item_id
            )
            
            print(f"  ✅ Updated {test_story_id} (ID: {work_item_id}) with complete description")
            fixed_count += 1
            
        except Exception as e:
            print(f"  ❌ Failed to update {test_story_id}: {e}")
            failed_count += 1
    
    print(f"\n📊 Test Summary:")
    print(f"  ✅ Successfully updated: {fixed_count}")
    print(f"  ❌ Failed: {failed_count}")
    
    print(f"\n🔗 View updated work item:")
    print(f"  {ORGANIZATION_URL}/{PROJECT_NAME}/_workitems/edit/{story_mapping[test_story_id]}")
    
    if fixed_count > 0:
        print("\nTest successful! Applying to all stories...")
        for story_id, work_item_id in story_mapping.items():
            if story_id != test_story_id and story_id in stories:  # Skip the test one we already did
                story = stories[story_id]
                try:
                    complete_description = create_complete_description_with_criteria(story)
                    
                    document = [
                        JsonPatchOperation(
                            op="replace",
                            path="/fields/System.Description",
                            value=complete_description
                        ),
                        JsonPatchOperation(
                            op="replace",
                            path="/fields/Microsoft.VSTS.Common.AcceptanceCriteria",
                            value=""  # Clear the separate field
                        )
                    ]
                    updated_work_item = client.wit_client.update_work_item(
                        document=document,
                        id=work_item_id
                    )
                    print(f"  ✅ Updated {story_id} (ID: {work_item_id})")
                    fixed_count += 1
                except Exception as e:
                    print(f"  ❌ Failed to update {story_id}: {e}")
                    failed_count += 1
        
        print(f"\n📊 Final Summary:")
        print(f"  ✅ Successfully updated: {fixed_count}")
        print(f"  ❌ Failed: {failed_count}")
        print(f"\n✨ All acceptance criteria have been moved to Description field!")
        print(f"  • Proper HTML formatting with nested bullet points")
        print(f"  • Clear Given/When/Then structure with indentation")
        print(f"  • Better readability in Azure DevOps interface")
        print(f"  • Separate Acceptance Criteria field cleared to avoid duplication")


if __name__ == "__main__":
    main()