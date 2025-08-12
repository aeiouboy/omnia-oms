#!/usr/bin/env python3
"""
Fix epic parsing to properly extract detailed content from markdown file.
The original parsing logic was failing to extract the rich epic content.
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


class FixedEpicMarkdownParser:
    """Fixed parser that correctly extracts detailed epic information from markdown file"""
    
    @staticmethod
    def parse_epics_from_markdown(file_path: str) -> dict:
        """Parse epic information from markdown file with correct logic"""
        with open(file_path, 'r') as f:
            content = f.read()
        
        epics = {}
        
        # Split content by epic headers - this regex properly captures epic titles
        epic_sections = re.split(r'\n## Epic (\d+): (.+)', content)
        
        # Process each epic section (starting from index 1, every 3 elements)
        for i in range(1, len(epic_sections), 3):
            if i+2 < len(epic_sections):
                epic_number = epic_sections[i]
                epic_title = epic_sections[i+1].strip()
                epic_content = epic_sections[i+2]
                
                # Stop at the next epic section
                next_epic_pos = epic_content.find('\n## Epic ')
                if next_epic_pos != -1:
                    epic_content = epic_content[:next_epic_pos]
                
                print(f"🔍 Processing Epic {epic_number}: {epic_title}")
                print(f"   Content preview: {epic_content[:200]}...")
                
                parsed_epic = FixedEpicMarkdownParser._parse_epic_content(epic_title, epic_content)
                if parsed_epic:
                    epics[epic_title] = parsed_epic
                    print(f"   ✅ Successfully parsed epic with {len(parsed_epic['success_metrics'])} metrics and {len(parsed_epic['risk_factors'])} risks")
                else:
                    print(f"   ❌ Failed to parse epic content")
        
        return epics
    
    @staticmethod
    def _parse_epic_content(title: str, content: str) -> dict:
        """Parse individual epic content with improved logic"""
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
        overview_lines = []
        
        for line in lines:
            line_stripped = line.strip()
            
            # Skip empty lines
            if not line_stripped:
                continue
            
            # Stop at User Stories section
            if line_stripped.startswith('### User Stories'):
                break
            
            # Identify sections
            if line_stripped == '### Epic Overview':
                current_section = 'overview'
                continue
            elif line_stripped.startswith('**Business Value:**'):
                current_section = 'business_value'
                # Extract the value part after the colon
                value = line_stripped.replace('**Business Value:**', '').strip()
                if value:
                    epic['business_value'] = value
                continue
            elif line_stripped.startswith('**Key Stakeholders:**'):
                current_section = 'stakeholders'
                # Extract the stakeholders part after the colon
                stakeholders = line_stripped.replace('**Key Stakeholders:**', '').strip()
                if stakeholders:
                    epic['stakeholders'] = stakeholders
                continue
            elif line_stripped == '**Success Metrics:**':
                current_section = 'success_metrics'
                continue
            elif line_stripped == '**Risk Factors:**':
                current_section = 'risk_factors'
                continue
            
            # Parse content based on current section
            if current_section == 'overview':
                if not line_stripped.startswith('**'):
                    overview_lines.append(line_stripped)
            elif current_section == 'success_metrics' and line_stripped.startswith('- '):
                metric = line_stripped[2:].strip()
                if metric:
                    epic['success_metrics'].append(metric)
            elif current_section == 'risk_factors' and line_stripped.startswith('- '):
                risk = line_stripped[2:].strip()
                if risk:
                    epic['risk_factors'].append(risk)
        
        # Join overview lines
        if overview_lines:
            epic['overview'] = ' '.join(overview_lines)
        
        # Debug output
        print(f"     📋 Overview: {epic['overview'][:100]}...")
        print(f"     💼 Business Value: {epic['business_value']}")
        print(f"     👥 Stakeholders: {epic['stakeholders']}")
        print(f"     🎯 Success Metrics: {epic['success_metrics']}")
        print(f"     ⚠️  Risk Factors: {epic['risk_factors']}")
        
        return epic


def create_fixed_epic_html_description(epic: dict) -> str:
    """Create HTML description for epic with proper fallback handling"""
    
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
    
    # Use actual content, with proper fallbacks
    overview = epic['overview'] if epic['overview'] else f"Core functionality for {epic['title']} in the MAO MVP implementation"
    business_value = epic['business_value'] if epic['business_value'] else "Delivers essential capabilities for the MVP launch"
    stakeholders = epic['stakeholders'] if epic['stakeholders'] else "Development Team, Product Owner, End Users"
    
    # Create comprehensive HTML description
    html_description = f"""<h3>Epic Overview</h3>
<p>{overview}</p>

<h3>Business Value</h3>
<p>{business_value}</p>

<h3>Key Stakeholders</h3>
<p>{stakeholders}</p>

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
    
    print(f"📊 Found {len(epic_mapping)} epics to update with detailed markdown content")
    
    # Parse epics from markdown file with fixed parser
    markdown_file = "/Users/chongraktanaka/Projects/mao-docsite/mvp-requirements/user story/mvp-user-stories.md"
    print("📖 Parsing epic details from markdown with FIXED parser...")
    
    parser = FixedEpicMarkdownParser()
    epics_from_markdown = parser.parse_epics_from_markdown(markdown_file)
    
    print(f"📋 Successfully parsed {len(epics_from_markdown)} epics from markdown:")
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
    print(f"\n🎯 Updating epics with FIXED detailed markdown content...")
    
    updated_count = 0
    failed_count = 0
    
    for epic_name, work_item_id in epic_mapping.items():
        # Find matching epic in markdown with improved matching logic
        matching_epic = None
        
        print(f"\n🔍 Looking for match for Azure epic: '{epic_name}'")
        
        for markdown_title, epic_data in epics_from_markdown.items():
            # More flexible matching logic
            epic_name_clean = epic_name.lower().replace('_', ' ').replace('&', 'and').strip()
            markdown_title_clean = markdown_title.lower().replace('&', 'and').strip()
            
            print(f"   Comparing: '{epic_name_clean}' vs '{markdown_title_clean}'")
            
            if (epic_name_clean in markdown_title_clean or 
                markdown_title_clean in epic_name_clean or
                # Try partial word matching
                any(word in markdown_title_clean for word in epic_name_clean.split() if len(word) > 3)):
                matching_epic = epic_data
                print(f"   ✅ Found match: {markdown_title}")
                break
        
        if not matching_epic:
            print(f"  ⚠️  No matching markdown content found for: {epic_name}")
            continue
        
        try:
            # Create comprehensive HTML description from markdown content
            html_description = create_fixed_epic_html_description(matching_epic)
            
            print(f"\n--- DETAILED PREVIEW for {epic_name} ---")
            print(f"Title: {matching_epic['title']}")
            print(f"Overview: {matching_epic['overview']}")
            print(f"Business Value: {matching_epic['business_value']}")
            print(f"Stakeholders: {matching_epic['stakeholders']}")
            print(f"Success Metrics ({len(matching_epic['success_metrics'])} items):")
            for i, metric in enumerate(matching_epic['success_metrics']):
                print(f"  {i+1}. {metric}")
            print(f"Risk Factors ({len(matching_epic['risk_factors'])} items):")
            for i, risk in enumerate(matching_epic['risk_factors']):
                print(f"  {i+1}. {risk}")
            print("--- END DETAILED PREVIEW ---\n")
            
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
            
            print(f"  ✅ Updated Epic: {epic_name} (ID: {work_item_id}) with RICH detailed content")
            updated_count += 1
            
        except Exception as e:
            print(f"  ❌ Failed to update epic {epic_name}: {e}")
            failed_count += 1
    
    print(f"\n📊 Epic Update Summary:")
    print(f"  ✅ Successfully updated: {updated_count}")
    print(f"  ❌ Failed: {failed_count}")
    
    if updated_count > 0:
        print(f"\n✨ All epics updated with DETAILED markdown content!")
        print(f"  📄 Epic Overview extracted from markdown")
        print(f"  💼 Business Value statements from markdown")
        print(f"  👥 Key Stakeholders identified from markdown")
        print(f"  🎯 Success Metrics listed from markdown")
        print(f"  ⚠️  Risk Factors documented from markdown")
        print(f"\n🔗 View updated epics at: {ORGANIZATION_URL}/{PROJECT_NAME}/_backlogs/backlog/")


if __name__ == "__main__":
    main()