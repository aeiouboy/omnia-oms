#!/usr/bin/env python3
"""
Fix the acceptance criteria formatting with proper Given/When/Then indentation
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


class AcceptanceCriteriaParser:
    """Parser that handles proper Given/When/Then formatting"""
    
    @staticmethod
    def parse_markdown_file(file_path: str) -> dict:
        """Parse the markdown file with focus on acceptance criteria"""
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
                
                parsed_story = AcceptanceCriteriaParser._parse_story_content(story_id, story_title, story_content)
                if parsed_story:
                    stories[story_id] = parsed_story
        
        return stories
    
    @staticmethod
    def _parse_story_content(story_id: str, title: str, content: str) -> dict:
        """Parse individual story content with proper acceptance criteria handling"""
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
            
            # Parse acceptance criteria with proper indentation handling
            elif in_acceptance and current_section == 'acceptance':
                if line.startswith('-') and not line.startswith('**'):
                    # Determine indentation level
                    indent_level = len(original_line) - len(original_line.lstrip())
                    criteria = line[1:].strip()
                    if criteria:
                        acceptance_buffer.append({
                            'text': criteria,
                            'indent': indent_level
                        })
            elif current_section == 'dependencies' and not in_acceptance and not in_technical:
                if not line.startswith('**') and line:
                    story['dependencies'] = line
            elif in_technical and current_section == 'technical':
                if not line.startswith('**') and not line.startswith('---'):
                    technical_buffer.append(line)
        
        # Process acceptance criteria with proper indentation
        story['acceptance_criteria'] = acceptance_buffer
        
        # Clean up technical notes
        if technical_buffer:
            story['technical_notes'] = '\n'.join(technical_buffer)
        
        return story


def create_proper_acceptance_criteria_html(acceptance_criteria) -> str:
    """Create properly formatted HTML for acceptance criteria with indentation"""
    
    if not acceptance_criteria:
        return "<p>To be defined during implementation</p>"
    
    html = "<ul>\n"
    
    for criteria in acceptance_criteria:
        text = criteria['text'] if isinstance(criteria, dict) else criteria
        indent = criteria.get('indent', 0) if isinstance(criteria, dict) else 0
        
        # Handle indentation - convert to nested lists for sub-items
        if indent > 2:  # This is a sub-item
            html += f'    <li style="margin-left: 20px; list-style-type: circle;">{text}</li>\n'
        else:  # This is a main item
            html += f'  <li>{text}</li>\n'
    
    html += "</ul>"
    return html


def create_proper_description(story: dict) -> str:
    """Create properly formatted description for Azure DevOps"""
    
    # Format acceptance criteria with proper indentation
    criteria_html = create_proper_acceptance_criteria_html(story['acceptance_criteria'])
    
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
    
    # Create clean HTML description
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
    print(f"📊 Found {len(story_mapping)} stories to fix")
    
    # Parse the markdown file with focus on acceptance criteria
    stories_file = "/Users/chongraktanaka/Projects/mao-docsite/mvp-requirements/user story/mvp-user-stories.md"
    print("📖 Parsing user stories with acceptance criteria parser...")
    
    parser = AcceptanceCriteriaParser()
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
    
    # Fix work items with proper acceptance criteria formatting
    print(f"🛠️  Fixing acceptance criteria formatting...")
    
    fixed_count = 0
    failed_count = 0
    
    for story_id, work_item_id in story_mapping.items():
        if story_id in stories:
            story = stories[story_id]
            
            try:
                # Create proper HTML description with fixed acceptance criteria
                html_description = create_proper_description(story)
                
                # Create update document
                document = [
                    JsonPatchOperation(
                        op="replace",
                        path="/fields/System.Description",
                        value=html_description
                    )
                ]
                
                # Update the work item
                updated_work_item = client.wit_client.update_work_item(
                    document=document,
                    id=work_item_id
                )
                
                print(f"  ✅ Fixed acceptance criteria for {story_id} (ID: {work_item_id})")
                fixed_count += 1
                
            except Exception as e:
                print(f"  ❌ Failed to fix {story_id}: {e}")
                failed_count += 1
        else:
            print(f"  ⚠️ Story {story_id} not found in markdown file")
            failed_count += 1
    
    print(f"\n📊 Fix Summary:")
    print(f"  ✅ Successfully fixed: {fixed_count}")
    print(f"  ❌ Failed: {failed_count}")
    
    print(f"\n🔗 View fixed work items:")
    print(f"  {ORGANIZATION_URL}/{PROJECT_NAME}/_backlogs/backlog")
    
    print(f"\n✨ Acceptance criteria now have proper formatting:")
    print(f"  • Main items (Given, When, Then) are primary bullet points")
    print(f"  • Sub-items are indented with circle bullet points")


if __name__ == "__main__":
    main()