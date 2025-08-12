#!/usr/bin/env python3
"""
Fix line breaks in Acceptance Criteria field to properly display Given/When/Then structure.
Each bullet point should be on its own line for better readability.
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


class AcceptanceCriteriaFormatter:
    """Formatter that creates properly formatted acceptance criteria with line breaks"""
    
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
                
                parsed_story = AcceptanceCriteriaFormatter._parse_story_content(story_id, story_title, story_content)
                if parsed_story:
                    stories[story_id] = parsed_story
        
        return stories
    
    @staticmethod
    def _parse_story_content(story_id: str, title: str, content: str) -> dict:
        """Parse individual story content"""
        story = {
            'id': story_id,
            'title': title,
            'acceptance_criteria_structured': []
        }
        
        lines = content.strip().split('\n')
        current_section = None
        in_acceptance = False
        acceptance_buffer = []
        
        for line in lines:
            original_line = line
            line = line.strip()
            
            # Skip empty lines and next story headers
            if not line or line.startswith('#### '):
                if line.startswith('#### '):
                    break
                continue
            
            # Identify sections
            if line.startswith('**Acceptance Criteria:**'):
                in_acceptance = True
                current_section = 'acceptance'
            elif line.startswith('**Dependencies:**'):
                in_acceptance = False
                current_section = 'dependencies'
            elif line.startswith('**Technical Notes:**'):
                in_acceptance = False
                current_section = 'technical'
            
            # Parse acceptance criteria
            elif in_acceptance and current_section == 'acceptance':
                if line.startswith('-') and not line.startswith('**'):
                    criteria = line[1:].strip()
                    if criteria:
                        acceptance_buffer.append(criteria)
        
        # Structure acceptance criteria
        story['acceptance_criteria_structured'] = AcceptanceCriteriaFormatter._structure_acceptance_criteria(acceptance_buffer)
        
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


def create_properly_formatted_acceptance_criteria(story: dict) -> str:
    """Create properly formatted acceptance criteria with line breaks for readability"""
    
    criteria_text = ""
    
    if story['acceptance_criteria_structured']:
        for i, scenario in enumerate(story['acceptance_criteria_structured']):
            # Add the Given as main item with line break
            criteria_text += f"• {scenario['given']}\n"
            
            # Add When/Then as sub-items with proper indentation and line breaks
            if scenario['when_then']:
                for sub_criteria in scenario['when_then']:
                    criteria_text += f"  ◦ {sub_criteria}\n"
            
            # Add spacing between scenarios (but not after the last one)
            if i < len(story['acceptance_criteria_structured']) - 1:
                criteria_text += "\n"
    else:
        criteria_text = "To be defined during implementation"
    
    return criteria_text.strip()


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
    
    # Parse the markdown file
    stories_file = "/Users/chongraktanaka/Projects/mao-docsite/mvp-requirements/user story/mvp-user-stories.md"
    print("📖 Parsing user stories...")
    
    formatter = AcceptanceCriteriaFormatter()
    stories = formatter.parse_markdown_file(stories_file)
    
    print(f"📋 Parsed {len(stories)} stories from markdown")
    
    # Initialize Azure DevOps client
    print("🔌 Connecting to Azure DevOps...")
    try:
        client = AzureDevOpsClient(ORGANIZATION_URL, PERSONAL_ACCESS_TOKEN)
        print("✅ Connected successfully!")
    except Exception as e:
        print(f"❌ Error connecting: {e}")
        return
    
    # Fix acceptance criteria line breaks
    print(f"🔧 Fixing Acceptance Criteria line breaks...")
    
    fixed_count = 0
    failed_count = 0
    
    # Test with just ORD-002 first
    test_story_id = 'ORD-002'
    if test_story_id in story_mapping and test_story_id in stories:
        work_item_id = story_mapping[test_story_id]
        story = stories[test_story_id]
        
        try:
            # Create properly formatted acceptance criteria with line breaks
            formatted_criteria = create_properly_formatted_acceptance_criteria(story)
            
            print(f"\n--- Preview for {test_story_id} ---")
            print("Properly formatted Acceptance Criteria:")
            print(formatted_criteria)
            print("--- End Preview ---\n")
            
            # Create update document
            document = [
                JsonPatchOperation(
                    op="replace",
                    path="/fields/Microsoft.VSTS.Common.AcceptanceCriteria",
                    value=formatted_criteria
                )
            ]
            
            # Update the work item
            updated_work_item = client.wit_client.update_work_item(
                document=document,
                id=work_item_id
            )
            
            print(f"  ✅ Fixed line breaks for {test_story_id} (ID: {work_item_id})")
            fixed_count += 1
            
        except Exception as e:
            print(f"  ❌ Failed to fix {test_story_id}: {e}")
            failed_count += 1
    
    print(f"\n📊 Test Summary:")
    print(f"  ✅ Successfully fixed: {fixed_count}")
    print(f"  ❌ Failed: {failed_count}")
    
    print(f"\n🔗 View fixed work item:")
    print(f"  {ORGANIZATION_URL}/{PROJECT_NAME}/_workitems/edit/{story_mapping[test_story_id]}")
    
    if fixed_count > 0:
        print("\nTest successful! Applying to all stories...")
        for story_id, work_item_id in story_mapping.items():
            if story_id != test_story_id and story_id in stories:  # Skip the test one we already did
                story = stories[story_id]
                try:
                    formatted_criteria = create_properly_formatted_acceptance_criteria(story)
                    
                    document = [
                        JsonPatchOperation(
                            op="replace",
                            path="/fields/Microsoft.VSTS.Common.AcceptanceCriteria",
                            value=formatted_criteria
                        )
                    ]
                    updated_work_item = client.wit_client.update_work_item(
                        document=document,
                        id=work_item_id
                    )
                    print(f"  ✅ Fixed line breaks for {story_id} (ID: {work_item_id})")
                    fixed_count += 1
                except Exception as e:
                    print(f"  ❌ Failed to fix {story_id}: {e}")
                    failed_count += 1
        
        print(f"\n📊 Final Summary:")
        print(f"  ✅ Successfully fixed: {fixed_count}")
        print(f"  ❌ Failed: {failed_count}")
        print(f"\n✨ Acceptance Criteria now have proper line breaks!")
        print(f"  • Each bullet point is on its own line")
        print(f"  • Proper indentation maintained with sub-bullets")
        print(f"  • Better readability in Azure DevOps interface")


if __name__ == "__main__":
    main()