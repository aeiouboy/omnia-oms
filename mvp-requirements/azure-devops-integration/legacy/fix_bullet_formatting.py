#!/usr/bin/env python3
"""
Fix bullet point formatting - each bullet should be on its own line
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


class BulletFormatter:
    """Format stories with proper bullet point line breaks"""
    
    @staticmethod
    def parse_story_from_markdown(story_id: str, content: str) -> dict:
        """Parse a single story from markdown content"""
        story = {
            'id': story_id,
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
    
    @staticmethod
    def create_readable_description(story: dict) -> str:
        """Create a well-formatted, readable description"""
        # Main user story with line breaks
        description = f"As a {story['as_a']}, I want {story['i_want']}, so that {story['so_that']}."
        
        # Add dependencies section if present
        if story['dependencies'] and story['dependencies'].lower() != 'none':
            description += f"\n\n--- DEPENDENCIES ---\n{story['dependencies']}"
        
        # Add technical notes section if present with proper line breaks
        if story['technical_notes']:
            # Split technical notes by lines and add proper formatting
            tech_lines = story['technical_notes'].strip().split('\n')
            formatted_tech = ""
            for line in tech_lines:
                line = line.strip()
                if line.startswith('-'):
                    # Each bullet point gets its own line
                    if formatted_tech:
                        formatted_tech += "\n"
                    formatted_tech += f"• {line[1:].strip()}"
                elif line:
                    # Regular text
                    if formatted_tech and not formatted_tech.endswith('\n'):
                        formatted_tech += "\n"
                    formatted_tech += line
            
            description += f"\n\n--- TECHNICAL NOTES ---\n{formatted_tech}"
        
        return description
    
    @staticmethod
    def create_readable_acceptance_criteria(story: dict) -> str:
        """Create well-formatted acceptance criteria with proper line breaks"""
        if not story['acceptance_criteria']:
            return "To be defined during implementation"
        
        criteria_text = ""
        for criteria in story['acceptance_criteria']:
            # Each criteria gets its own line with bullet
            criteria_text += f"• {criteria}\n\n"
        
        return criteria_text.strip()


def parse_all_stories(file_path: str) -> dict:
    """Parse all stories from the markdown file"""
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
            
            story = BulletFormatter.parse_story_from_markdown(story_id, story_content)
            story['title'] = story_title
            stories[story_id] = story
    
    return stories


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
    
    print(f"🔧 Fixing bullet point formatting...")
    
    # Load work item mapping
    mapping_file = Path(__file__).parent / "work_item_mapping.json"
    if not mapping_file.exists():
        print("❌ Error: work_item_mapping.json not found!")
        return
    
    with open(mapping_file, 'r') as f:
        mapping = json.load(f)
    
    story_mapping = mapping.get('stories', {})
    print(f"📊 Found {len(story_mapping)} stories to fix bullet formatting")
    
    # Parse stories from markdown
    stories_file = "/Users/chongraktanaka/Projects/mao-docsite/mvp-requirements/user story/mvp-user-stories.md"
    print("📖 Parsing stories with proper bullet formatting...")
    
    stories = parse_all_stories(stories_file)
    print(f"📋 Parsed {len(stories)} stories")
    
    # Initialize Azure DevOps client
    print("🔌 Connecting to Azure DevOps...")
    try:
        client = AzureDevOpsClient(ORGANIZATION_URL, PERSONAL_ACCESS_TOKEN)
        print("✅ Connected successfully!")
    except Exception as e:
        print(f"❌ Error connecting: {e}")
        return
    
    # Fix bullet formatting for each work item
    print(f"• Fixing bullet point formatting...")
    
    updated_count = 0
    failed_count = 0
    
    for story_id, work_item_id in story_mapping.items():
        if story_id in stories:
            story = stories[story_id]
            
            try:
                # Create properly formatted description and acceptance criteria
                description = BulletFormatter.create_readable_description(story)
                acceptance_criteria = BulletFormatter.create_readable_acceptance_criteria(story)
                
                # Create update document
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
                
                # Update the work item
                updated_work_item = client.wit_client.update_work_item(
                    document=document,
                    id=work_item_id
                )
                
                print(f"  ✅ Fixed bullets: {story_id} (ID: {work_item_id})")
                updated_count += 1
                
            except Exception as e:
                print(f"  ❌ Failed to fix {story_id}: {e}")
                failed_count += 1
        else:
            print(f"  ⚠️ Story {story_id} not found")
            failed_count += 1
    
    print(f"\n📊 Bullet Formatting Fix Summary:")
    print(f"  ✅ Successfully fixed: {updated_count}")
    print(f"  ❌ Failed: {failed_count}")
    
    print(f"\n🔧 Bullet Point Improvements:")
    print(f"  • Each bullet point now on separate line")
    print(f"  • Proper spacing between bullet points")
    print(f"  • Clean bullet symbols (•)")
    print(f"  • Better readability in Azure DevOps")
    
    print(f"\n🔗 View improved work items:")
    print(f"  {ORGANIZATION_URL}/{PROJECT_NAME}/_backlogs/backlog")
    
    if story_mapping.get('ORD-005'):
        work_item_id = story_mapping['ORD-005']
        print(f"\n🔍 Check the improved ORD-005:")
        print(f"  {ORGANIZATION_URL}/{PROJECT_NAME}/_workitems/edit/{work_item_id}")


if __name__ == "__main__":
    main()