#!/usr/bin/env python3
"""
Azure DevOps Manager - Unified toolkit for managing Azure DevOps work items
Combines all functionality into a clean, reusable interface.
"""

import sys
import os
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from azure.devops.connection import Connection
from azure.devops.v7_1.work_item_tracking.models import JsonPatchOperation
from msrest.authentication import BasicAuthentication


@dataclass
class UserStory:
    """Represents a user story from markdown"""
    story_id: str
    title: str
    epic: str
    priority: str
    story_points: int
    as_a: str
    i_want: str
    so_that: str
    acceptance_criteria_structured: List[Dict]
    dependencies: str
    technical_notes: str


@dataclass
class Epic:
    """Represents an epic from markdown"""
    title: str
    overview: str
    business_value: str
    stakeholders: str
    success_metrics: List[str]
    risk_factors: List[str]


class AzureDevOpsManager:
    """Main manager class for Azure DevOps operations"""
    
    def __init__(self, organization_url: str, personal_access_token: str, project_name: str):
        """Initialize Azure DevOps manager"""
        credentials = BasicAuthentication('', personal_access_token)
        self.connection = Connection(base_url=organization_url, creds=credentials)
        self.wit_client = self.connection.clients.get_work_item_tracking_client()
        self.project_name = project_name
        self.organization_url = organization_url
    
    def create_epic(self, epic: Epic) -> int:
        """Create an epic work item"""
        html_description = self._create_epic_html_description(epic)
        
        document = [
            JsonPatchOperation(op="add", path="/fields/System.Title", value=f"MAO MVP - {epic.title}"),
            JsonPatchOperation(op="add", path="/fields/System.Description", value=html_description),
            JsonPatchOperation(op="add", path="/fields/System.WorkItemType", value="Epic")
        ]
        
        work_item = self.wit_client.create_work_item(
            document=document, project=self.project_name, type="Epic"
        )
        
        print(f"✅ Created Epic: {epic.title} (ID: {work_item.id})")
        return work_item.id
    
    def create_user_story(self, story: UserStory, parent_id: Optional[int] = None) -> int:
        """Create a user story work item"""
        clean_description = self._create_story_html_description(story)
        html_acceptance_criteria = self._create_html_acceptance_criteria(story)
        
        priority_map = {"P0": 1, "P1": 2, "P2": 3}
        priority_value = priority_map.get(story.priority, 2)
        
        document = [
            JsonPatchOperation(op="add", path="/fields/System.Title", value=f"{story.story_id}: {story.title}"),
            JsonPatchOperation(op="add", path="/fields/System.Description", value=clean_description),
            JsonPatchOperation(op="add", path="/fields/Microsoft.VSTS.Common.AcceptanceCriteria", value=html_acceptance_criteria),
            JsonPatchOperation(op="add", path="/fields/Microsoft.VSTS.Common.Priority", value=priority_value),
            JsonPatchOperation(op="add", path="/fields/Microsoft.VSTS.Scheduling.StoryPoints", value=story.story_points),
            JsonPatchOperation(op="add", path="/fields/System.Tags", value=f"MVP;{story.epic.replace(' ', '')};{story.story_id}")
        ]
        
        if parent_id:
            document.append(JsonPatchOperation(
                op="add", path="/relations/-",
                value={"rel": "System.LinkTypes.Hierarchy-Reverse", "url": f"{self.organization_url}/_apis/wit/workItems/{parent_id}"}
            ))
        
        work_item = self.wit_client.create_work_item(
            document=document, project=self.project_name, type="User Story"
        )
        
        print(f"✅ Created User Story: {story.story_id} - {story.title} (ID: {work_item.id})")
        return work_item.id
    
    def update_work_item(self, work_item_id: int, updates: List[JsonPatchOperation]) -> bool:
        """Update a work item with given operations"""
        try:
            self.wit_client.update_work_item(document=updates, id=work_item_id)
            return True
        except Exception as e:
            print(f"❌ Failed to update work item {work_item_id}: {e}")
            return False
    
    def update_epic_from_data(self, work_item_id: int, epic: Epic) -> bool:
        """Update an epic with rich data from Epic object"""
        html_description = self._create_epic_html_description(epic)
        
        updates = [
            JsonPatchOperation(op="replace", path="/fields/System.Description", value=html_description),
            JsonPatchOperation(op="replace", path="/fields/Microsoft.VSTS.Common.AcceptanceCriteria", value="")
        ]
        
        return self.update_work_item(work_item_id, updates)
    
    def update_story_from_data(self, work_item_id: int, story: UserStory) -> bool:
        """Update a user story with data from UserStory object"""
        clean_description = self._create_story_html_description(story)
        html_acceptance_criteria = self._create_html_acceptance_criteria(story)
        
        updates = [
            JsonPatchOperation(op="replace", path="/fields/System.Description", value=clean_description),
            JsonPatchOperation(op="replace", path="/fields/Microsoft.VSTS.Common.AcceptanceCriteria", value=html_acceptance_criteria)
        ]
        
        return self.update_work_item(work_item_id, updates)
    
    def _create_epic_html_description(self, epic: Epic) -> str:
        """Create HTML description for epic"""
        metrics_html = "<ul>\n" + "\n".join(f"  <li>{metric}</li>" for metric in epic.success_metrics) + "\n</ul>" if epic.success_metrics else "<p>To be defined</p>"
        risks_html = "<ul>\n" + "\n".join(f"  <li>{risk}</li>" for risk in epic.risk_factors) + "\n</ul>" if epic.risk_factors else "<p>To be assessed</p>"
        
        return f"""<h3>Epic Overview</h3>
<p>{epic.overview or f'Core functionality for {epic.title} in the MAO MVP implementation'}</p>

<h3>Business Value</h3>
<p>{epic.business_value or 'Delivers essential capabilities for the MVP launch'}</p>

<h3>Key Stakeholders</h3>
<p>{epic.stakeholders or 'Development Team, Product Owner, End Users'}</p>

<h3>Success Metrics</h3>
{metrics_html}

<h3>Risk Factors</h3>
{risks_html}"""
    
    def _create_story_html_description(self, story: UserStory) -> str:
        """Create clean HTML description for user story (no acceptance criteria)"""
        tech_notes = story.technical_notes or "None"
        if tech_notes != "None":
            tech_notes = re.sub(r'```(\w+)?\n(.*?)```', r'<pre><code>\2</code></pre>', tech_notes, flags=re.DOTALL)
            tech_notes = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', tech_notes)
            tech_notes = tech_notes.replace('\n', '<br/>')
        
        return f"""<h3>User Story</h3>
<p><strong>As a</strong> {story.as_a}<br/>
<strong>I want</strong> {story.i_want}<br/>
<strong>So that</strong> {story.so_that}</p>

<h3>Dependencies</h3>
<p>{story.dependencies}</p>

<h3>Technical Notes</h3>
<p>{tech_notes}</p>"""
    
    def _create_html_acceptance_criteria(self, story: UserStory) -> str:
        """Create HTML acceptance criteria for dedicated field"""
        if not story.acceptance_criteria_structured:
            return "To be defined during implementation"
        
        html = "<ul>\n"
        for scenario in story.acceptance_criteria_structured:
            html += f'  <li><strong>{scenario["given"]}</strong>\n'
            if scenario.get('when_then'):
                html += '    <ul>\n'
                for sub_criteria in scenario['when_then']:
                    html += f'      <li>{sub_criteria}</li>\n'
                html += '    </ul>\n'
            html += '  </li>\n'
        html += "</ul>"
        
        return html


class MarkdownParser:
    """Parser for extracting user stories and epics from markdown files"""
    
    @staticmethod
    def parse_user_stories(file_path: str) -> Dict[str, UserStory]:
        """Parse user stories from markdown file"""
        with open(file_path, 'r') as f:
            content = f.read()
        
        stories = {}
        story_sections = re.split(r'#### ([A-Z]+-\d+): (.+)', content)
        
        for i in range(1, len(story_sections), 3):
            if i+2 < len(story_sections):
                story_id = story_sections[i]
                story_title = story_sections[i+1]
                story_content = story_sections[i+2]
                
                parsed_story = MarkdownParser._parse_story_content(story_id, story_title, story_content)
                if parsed_story:
                    stories[story_id] = parsed_story
        
        return stories
    
    @staticmethod
    def parse_epics(file_path: str) -> Dict[str, Epic]:
        """Parse epics from markdown file"""
        with open(file_path, 'r') as f:
            content = f.read()
        
        epics = {}
        epic_sections = re.split(r'\n## Epic \d+: (.+)', content)
        
        for i in range(1, len(epic_sections), 2):
            if i+1 < len(epic_sections):
                epic_title = epic_sections[i].strip()
                epic_content = epic_sections[i+1]
                
                next_epic_pos = epic_content.find('\n## Epic ')
                if next_epic_pos != -1:
                    epic_content = epic_content[:next_epic_pos]
                
                parsed_epic = MarkdownParser._parse_epic_content(epic_title, epic_content)
                if parsed_epic:
                    epics[epic_title] = parsed_epic
        
        return epics
    
    @staticmethod
    def _parse_story_content(story_id: str, title: str, content: str) -> Optional[UserStory]:
        """Parse individual story content"""
        story_data = {
            'story_id': story_id, 'title': title, 'epic': '', 'priority': 'P1', 'story_points': 5,
            'as_a': '', 'i_want': '', 'so_that': '', 'acceptance_criteria_structured': [],
            'dependencies': 'None', 'technical_notes': ''
        }
        
        lines = content.strip().split('\n')
        current_section = None
        acceptance_buffer = []
        technical_buffer = []
        dependencies_buffer = []
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Stop at next story
            if line.startswith('#### '):
                break
            
            # Skip empty lines
            if not line:
                i += 1
                continue
            
            # Parse basic fields
            if line.startswith('**Priority:**'):
                story_data['priority'] = line.split('**Priority:**')[1].strip()
            elif line.startswith('**Story Points:**'):
                try:
                    story_data['story_points'] = int(line.split('**Story Points:**')[1].strip())
                except:
                    story_data['story_points'] = 5
            elif line.startswith('**As a**'):
                story_data['as_a'] = line.replace('**As a**', '').strip()
            elif line.startswith('**I want**'):
                story_data['i_want'] = line.replace('**I want**', '').strip()
            elif line.startswith('**So that**'):
                story_data['so_that'] = line.replace('**So that**', '').strip()
                
            # Parse section headers
            elif line.startswith('**Acceptance Criteria:**'):
                current_section = 'acceptance'
            elif line.startswith('**Dependencies:**'):
                current_section = 'dependencies'
                # Check if dependencies are on the same line
                deps_content = line.replace('**Dependencies:**', '').strip()
                if deps_content:
                    dependencies_buffer.append(deps_content)
            elif line.startswith('**Technical Notes:**'):
                current_section = 'technical'
                
            # Parse section content
            elif current_section == 'acceptance':
                if line.startswith('-') or line.startswith('  -'):
                    criteria = line.lstrip('- ').strip()
                    if criteria:
                        acceptance_buffer.append(criteria)
                elif line and not line.startswith('**'):
                    # Handle multi-line acceptance criteria
                    if acceptance_buffer:
                        acceptance_buffer[-1] += ' ' + line
                        
            elif current_section == 'dependencies':
                if line and not line.startswith('**'):
                    dependencies_buffer.append(line)
                    
            elif current_section == 'technical':
                if line and not line.startswith('**'):
                    # Handle code blocks properly
                    if line.startswith('```'):
                        # Start of code block - collect until end
                        technical_buffer.append(line)
                        i += 1
                        while i < len(lines):
                            code_line = lines[i].strip() if lines[i].strip() else lines[i]
                            technical_buffer.append(code_line)
                            if code_line.strip().endswith('```'):
                                break
                            i += 1
                    else:
                        technical_buffer.append(line)
            
            i += 1
        
        # Process dependencies
        if dependencies_buffer:
            story_data['dependencies'] = ' '.join(dependencies_buffer).strip()
            if not story_data['dependencies']:
                story_data['dependencies'] = 'None'
        
        # Process acceptance criteria
        story_data['acceptance_criteria_structured'] = MarkdownParser._structure_acceptance_criteria(acceptance_buffer)
        
        # Process technical notes
        if technical_buffer:
            story_data['technical_notes'] = '\n'.join(technical_buffer)
        
        return UserStory(**story_data)
    
    @staticmethod
    def _parse_epic_content(title: str, content: str) -> Optional[Epic]:
        """Parse individual epic content"""
        epic_data = {
            'title': title, 'overview': '', 'business_value': '', 'stakeholders': '',
            'success_metrics': [], 'risk_factors': []
        }
        
        lines = content.strip().split('\n')
        current_section = None
        overview_lines = []
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('### User Stories'):
                if line.startswith('### User Stories'):
                    break
                continue
            
            if line == '### Epic Overview':
                current_section = 'overview'
            elif line.startswith('**Business Value:**'):
                current_section = 'business_value'
                value = line.replace('**Business Value:**', '').strip()
                if value:
                    epic_data['business_value'] = value
            elif line.startswith('**Key Stakeholders:**'):
                current_section = 'stakeholders'
                stakeholders = line.replace('**Key Stakeholders:**', '').strip()
                if stakeholders:
                    epic_data['stakeholders'] = stakeholders
            elif line == '**Success Metrics:**':
                current_section = 'success_metrics'
            elif line == '**Risk Factors:**':
                current_section = 'risk_factors'
            elif current_section == 'overview' and not line.startswith('**'):
                overview_lines.append(line)
            elif current_section == 'success_metrics' and line.startswith('- '):
                epic_data['success_metrics'].append(line[2:].strip())
            elif current_section == 'risk_factors' and line.startswith('- '):
                epic_data['risk_factors'].append(line[2:].strip())
        
        if overview_lines:
            epic_data['overview'] = ' '.join(overview_lines)
        
        return Epic(**epic_data)
    
    @staticmethod
    def _structure_acceptance_criteria(criteria_list: List[str]) -> List[Dict]:
        """Structure acceptance criteria into Given/When/Then groups"""
        structured = []
        current_scenario = None
        
        for criteria in criteria_list:
            criteria_lower = criteria.lower()
            
            if criteria_lower.startswith('given'):
                current_scenario = {'given': criteria, 'when_then': []}
                structured.append(current_scenario)
            elif criteria_lower.startswith(('when', 'then', 'and')):
                if current_scenario:
                    current_scenario['when_then'].append(criteria)
                else:
                    structured.append({'given': criteria, 'when_then': []})
        
        if not structured and criteria_list:
            for criteria in criteria_list:
                structured.append({'given': criteria, 'when_then': []})
        
        return structured


class ConfigManager:
    """Manages configuration and environment setup"""
    
    @staticmethod
    def load_config(config_dir: Path) -> Tuple[str, str, str]:
        """Load configuration from .env file"""
        env_file = config_dir / '.env'
        if env_file.exists():
            with open(env_file) as f:
                for line in f:
                    if line.strip() and not line.startswith('#') and '=' in line:
                        key, value = line.strip().split('=', 1)
                        os.environ[key] = value
        
        org_url = os.getenv('AZURE_DEVOPS_ORG_URL')
        project = os.getenv('AZURE_DEVOPS_PROJECT')
        pat = os.getenv('AZURE_DEVOPS_PAT')
        
        if not all([org_url, project, pat]):
            raise ValueError("Missing required configuration. Check your .env file.")
        
        return org_url, project, pat
    
    @staticmethod
    def load_work_item_mapping(config_dir: Path) -> Dict:
        """Load existing work item mapping"""
        mapping_file = config_dir / "work_item_mapping.json"
        if mapping_file.exists():
            with open(mapping_file, 'r') as f:
                return json.load(f)
        return {'epics': {}, 'stories': {}}
    
    @staticmethod
    def save_work_item_mapping(config_dir: Path, mapping: Dict):
        """Save work item mapping to JSON file"""
        mapping_file = config_dir / "work_item_mapping.json"
        with open(mapping_file, 'w') as f:
            json.dump(mapping, f, indent=2)


if __name__ == "__main__":
    print("Azure DevOps Manager - Unified toolkit")
    print("Use this as a library import in your automation scripts.")