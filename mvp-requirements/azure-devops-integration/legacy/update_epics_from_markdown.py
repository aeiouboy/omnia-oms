#!/usr/bin/env python3
"""
Update epics with detailed content from the markdown file.
Extract epic descriptions, business value, stakeholders, metrics, and risks.
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


class EpicMarkdownParser:
    """Parser that extracts detailed epic information from markdown file"""
    
    @staticmethod
    def parse_epics_from_markdown(file_path: str) -> dict:
        """Parse epic information from markdown file"""
        with open(file_path, 'r') as f:
            content = f.read()
        
        epics = {}
        
        # Split content by epic headers
        epic_sections = re.split(r'## Epic \d+: (.+)', content)
        
        # Process each epic section
        for i in range(1, len(epic_sections), 2):
            if i+1 < len(epic_sections):
                epic_title = epic_sections[i].strip()
                epic_content = epic_sections[i+1]
                
                # Stop at the next epic or end of file
                next_epic_pos = epic_content.find('## Epic ')
                if next_epic_pos != -1:
                    epic_content = epic_content[:next_epic_pos]
                
                parsed_epic = EpicMarkdownParser._parse_epic_content(epic_title, epic_content)
                if parsed_epic:
                    epics[epic_title] = parsed_epic
        
        return epics
    
    @staticmethod
    def _parse_epic_content(title: str, content: str) -> dict:
        """Parse individual epic content"""
        epic = {
            'title': title,
            'overview': '',
            'business_value': '',
            'stakeholders': '',
            'success_metrics': [],
            'risk_factors': []
        }
        
        lines = content.strip().split('\n')
        current_section = None
        metrics_buffer = []
        risks_buffer = []
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines and user story sections
            if not line or line.startswith('#### ') or line.startswith('### User Stories'):
                if line.startswith('### User Stories'):
                    break  # Stop processing at user stories
                continue
            
            # Identify sections
            if line.startswith('### Epic Overview'):
                current_section = 'overview'
            elif line.startswith('**Business Value:**'):
                current_section = 'business_value'
                # Extract the value part after the colon
                value = line.replace('**Business Value:**', '').strip()
                if value:
                    epic['business_value'] = value
            elif line.startswith('**Key Stakeholders:**'):
                current_section = 'stakeholders'
                # Extract the stakeholders part after the colon
                stakeholders = line.replace('**Key Stakeholders:**', '').strip()
                if stakeholders:
                    epic['stakeholders'] = stakeholders
            elif line.startswith('**Success Metrics:**'):
                current_section = 'success_metrics'
            elif line.startswith('**Risk Factors:**'):
                current_section = 'risk_factors'
            
            # Parse content based on current section
            elif current_section == 'overview' and not line.startswith('**'):
                if epic['overview']:
                    epic['overview'] += ' ' + line
                else:
                    epic['overview'] = line
            elif current_section == 'business_value' and not epic['business_value'] and not line.startswith('**'):
                epic['business_value'] = line
            elif current_section == 'stakeholders' and not epic['stakeholders'] and not line.startswith('**'):
                epic['stakeholders'] = line
            elif current_section == 'success_metrics' and line.startswith('- '):
                metrics_buffer.append(line[2:].strip())
            elif current_section == 'risk_factors' and line.startswith('- '):
                risks_buffer.append(line[2:].strip())
        
        epic['success_metrics'] = metrics_buffer
        epic['risk_factors'] = risks_buffer
        
        return epic


def create_epic_html_description(epic: dict) -> str:
    """Create HTML description for epic based on markdown content"""
    
    # Format success metrics as HTML list
    metrics_html = ""
    if epic['success_metrics']:
        metrics_html = "<ul>\n"
        for metric in epic['success_metrics']:
            metrics_html += f"  <li>{metric}</li>\n"
        metrics_html += "</ul>"
    else:
        metrics_html = "<p>To be defined</p>"
    
    # Format risk factors as HTML list
    risks_html = ""
    if epic['risk_factors']:
        risks_html = "<ul>\n"
        for risk in epic['risk_factors']:
            risks_html += f"  <li>{risk}</li>\n"
        risks_html += "</ul>"
    else:
        risks_html = "<p>To be assessed</p>"
    
    # Create comprehensive HTML description
    html_description = f"""<h3>Epic Overview</h3>
<p>{epic['overview'] if epic['overview'] else 'Core functionality for the MAO MVP implementation'}</p>

<h3>Business Value</h3>
<p>{epic['business_value'] if epic['business_value'] else 'Delivers essential capabilities for the MVP launch'}</p>

<h3>Key Stakeholders</h3>
<p>{epic['stakeholders'] if epic['stakeholders'] else 'Development Team, Product Owner, End Users'}</p>

<h3>Success Metrics</h3>
{metrics_html}

<h3>Risk Factors</h3>
{risks_html}"""
    
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
    
    epic_mapping = mapping.get('epics', {})
    
    print(f"📊 Found {len(epic_mapping)} epics to update with markdown content")
    
    # Parse epics from markdown file
    markdown_file = "/Users/chongraktanaka/Projects/mao-docsite/mvp-requirements/user story/mvp-user-stories.md"
    print("📖 Parsing epic details from markdown...")
    
    parser = EpicMarkdownParser()
    epics_from_markdown = parser.parse_epics_from_markdown(markdown_file)
    
    print(f"📋 Parsed {len(epics_from_markdown)} epics from markdown:")
    for epic_title in epics_from_markdown:
        print(f"  - {epic_title}")
    
    # Initialize Azure DevOps client
    print("🔌 Connecting to Azure DevOps...")
    try:
        client = AzureDevOpsClient(ORGANIZATION_URL, PERSONAL_ACCESS_TOKEN)
        print("✅ Connected successfully!")
    except Exception as e:
        print(f"❌ Error connecting: {e}")
        return
    
    # Update epics with detailed content from markdown
    print(f"\n🎯 Updating epics with detailed markdown content...")
    
    updated_count = 0
    failed_count = 0
    
    for epic_name, work_item_id in epic_mapping.items():
        # Find matching epic in markdown (by partial name match)
        matching_epic = None
        for markdown_title, epic_data in epics_from_markdown.items():
            if epic_name.lower().replace(' & ', ' & ').replace('_', ' ') in markdown_title.lower() or \
               markdown_title.lower().replace(' & ', ' & ') in epic_name.lower():
                matching_epic = epic_data
                break
        
        if not matching_epic:
            print(f"  ⚠️  No matching markdown content found for: {epic_name}")
            continue
        
        try:
            # Create comprehensive HTML description from markdown content
            html_description = create_epic_html_description(matching_epic)
            
            print(f"\n--- Preview for {epic_name} ---")
            print(f"Overview: {matching_epic['overview'][:100]}...")
            print(f"Business Value: {matching_epic['business_value'][:100]}...")
            print(f"Stakeholders: {matching_epic['stakeholders']}")
            print(f"Success Metrics: {len(matching_epic['success_metrics'])} items")
            print(f"Risk Factors: {len(matching_epic['risk_factors'])} items")
            print("--- End Preview ---\n")
            
            # Create update document for epic
            document = [
                JsonPatchOperation(
                    op="replace",
                    path="/fields/System.Description",
                    value=html_description
                ),
                # Clear acceptance criteria field for epics
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
            
            print(f"  ✅ Updated Epic: {epic_name} (ID: {work_item_id}) with markdown content")
            updated_count += 1
            
        except Exception as e:
            print(f"  ❌ Failed to update epic {epic_name}: {e}")
            failed_count += 1
    
    print(f"\n📊 Epic Update Summary:")
    print(f"  ✅ Successfully updated: {updated_count}")
    print(f"  ❌ Failed: {failed_count}")
    
    if updated_count > 0:
        print(f"\n✨ All epics updated with rich markdown content!")
        print(f"  📄 Epic Overview from markdown")
        print(f"  💼 Business Value statements")
        print(f"  👥 Key Stakeholders identified")
        print(f"  🎯 Success Metrics listed")
        print(f"  ⚠️  Risk Factors documented")


if __name__ == "__main__":
    main()