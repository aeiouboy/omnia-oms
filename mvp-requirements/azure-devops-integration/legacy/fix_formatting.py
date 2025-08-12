#!/usr/bin/env python3
"""
Fix the formatting of work item descriptions to display properly in Azure DevOps
Uses Azure DevOps's preferred HTML formatting and acceptance criteria field
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


class StoryFormatter:
    """Format stories for Azure DevOps display"""
    
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
    def create_clean_description(story: dict) -> str:
        """Create a clean, simple description for Azure DevOps"""
        description = f"As a {story['as_a']}, I want {story['i_want']}, so that {story['so_that']}."
        
        # Add dependencies if not None
        if story['dependencies'] and story['dependencies'].lower() != 'none':
            description += f"\n\nDependencies: {story['dependencies']}"
        
        # Add technical notes if present
        if story['technical_notes']:
            description += f"\n\nTechnical Notes:\n{story['technical_notes']}"
        
        return description
    
    @staticmethod
    def create_acceptance_criteria_text(story: dict) -> str:
        """Create formatted acceptance criteria text"""
        if not story['acceptance_criteria']:
            return "To be defined during implementation"
        
        criteria_text = ""
        for criteria in story['acceptance_criteria']:
            criteria_text += f"• {criteria}\n"
        
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
            
            story = StoryFormatter.parse_story_from_markdown(story_id, story_content)
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
    
    print(f"🔧 Fixing formatting for Azure DevOps work items...")
    
    # Load work item mapping
    mapping_file = Path(__file__).parent / "work_item_mapping.json"
    if not mapping_file.exists():
        print("❌ Error: work_item_mapping.json not found!")
        return
    
    with open(mapping_file, 'r') as f:
        mapping = json.load(f)
    
    story_mapping = mapping.get('stories', {})
    print(f"📊 Found {len(story_mapping)} stories to fix")
    
    # Parse stories from markdown
    stories_file = "/Users/chongraktanaka/Projects/mao-docsite/mvp-requirements/user story/mvp-user-stories.md"
    print("📖 Parsing stories with improved formatting...")
    
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
    
    # Fix formatting for each work item
    print(f"🎨 Fixing formatting for work items...")
    
    updated_count = 0
    failed_count = 0
    
    for story_id, work_item_id in story_mapping.items():
        if story_id in stories:
            story = stories[story_id]
            
            try:
                # Create clean description and separate acceptance criteria
                description = StoryFormatter.create_clean_description(story)
                acceptance_criteria = StoryFormatter.create_acceptance_criteria_text(story)
                
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
                    ),
                    JsonPatchOperation(
                        op="replace",
                        path="/fields/Microsoft.VSTS.Scheduling.StoryPoints",
                        value=story['story_points']
                    )
                ]
                
                # Map priority to Azure DevOps priority field
                priority_map = {"P0": 1, "P1": 2, "P2": 3}
                priority_value = priority_map.get(story['priority'], 2)
                
                document.append(JsonPatchOperation(
                    op="replace",
                    path="/fields/Microsoft.VSTS.Common.Priority",
                    value=priority_value
                ))
                
                # Update the work item
                updated_work_item = client.wit_client.update_work_item(
                    document=document,
                    id=work_item_id
                )
                
                print(f"  ✅ Fixed {story_id} (ID: {work_item_id})")
                updated_count += 1
                
            except Exception as e:
                print(f"  ❌ Failed to fix {story_id}: {e}")
                failed_count += 1
        else:
            print(f"  ⚠️ Story {story_id} not found in markdown")
            failed_count += 1
    
    print(f"\n📊 Formatting Fix Summary:")
    print(f"  ✅ Successfully fixed: {updated_count}")
    print(f"  ❌ Failed: {failed_count}")
    
    print(f"\n🎨 Improvements Made:")
    print(f"  • Clean, readable Description field")
    print(f"  • Proper Acceptance Criteria in dedicated field")
    print(f"  • Correct Story Points values")
    print(f"  • Mapped Priority values (P0→1, P1→2, P2→3)")
    
    print(f"\n🔗 View improved work items:")
    print(f"  {ORGANIZATION_URL}/{PROJECT_NAME}/_backlogs/backlog")
    
    if story_mapping.get('ORD-005'):
        work_item_id = story_mapping['ORD-005']
        print(f"\n🔍 Check ORD-005 (the one from your screenshot):")
        print(f"  {ORGANIZATION_URL}/{PROJECT_NAME}/_workitems/edit/{work_item_id}")


if __name__ == "__main__":
    main()