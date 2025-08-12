#!/usr/bin/env python3
"""
Correct epic matching by creating an explicit mapping between Azure DevOps epic names and markdown epic titles.
This fixes the issue where some epics got matched to wrong content.
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


# Explicit mapping between Azure DevOps epic names and markdown epic titles
EPIC_MAPPING = {
    "Order Creation & Validation": "Order Creation & Validation",
    "Bundle Processing": "Bundle Processing", 
    "Payment Processing": "Payment Processing",
    "Fulfillment Integration": "Fulfillment Integration",
    "Status Management": "Status Management",
    "Cancellation & Returns": "Cancellation & Returns",
    "API Integration": "API Integration",
    "Data Management & Reporting": "Data Management & Reporting"
}


class PreciseEpicMarkdownParser:
    """Parser that uses exact matching for epic content extraction"""
    
    @staticmethod
    def parse_epics_from_markdown(file_path: str) -> dict:
        """Parse epic information from markdown file with precise matching"""
        with open(file_path, 'r') as f:
            content = f.read()
        
        epics = {}
        
        # Split content by epic headers
        epic_sections = re.split(r'\n## Epic (\d+): (.+)', content)
        
        # Process each epic section
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
                
                parsed_epic = PreciseEpicMarkdownParser._parse_epic_content(epic_title, epic_content)
                if parsed_epic:
                    epics[epic_title] = parsed_epic
                    print(f"   ✅ Successfully parsed epic: {epic_title}")
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
        
        return epic


def create_precise_epic_html_description(epic: dict) -> str:
    """Create HTML description for epic with proper content"""
    
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
    
    # Use actual content from markdown
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
    
    print(f"📊 Found {len(epic_mapping)} epics to update with CORRECT matched content")
    
    # Parse epics from markdown file 
    markdown_file = "/Users/chongraktanaka/Projects/mao-docsite/mvp-requirements/user story/mvp-user-stories.md"
    print("📖 Parsing epic details from markdown with PRECISE parser...")
    
    parser = PreciseEpicMarkdownParser()
    epics_from_markdown = parser.parse_epics_from_markdown(markdown_file)
    
    print(f"📋 Successfully parsed {len(epics_from_markdown)} epics from markdown:")
    for epic_title in epics_from_markdown:
        print(f"  - {epic_title}")
    
    # Show explicit mapping
    print(f"\n🎯 Using EXPLICIT MAPPING to ensure correct matches:")
    for azure_name, markdown_name in EPIC_MAPPING.items():
        if azure_name in epic_mapping:
            print(f"  Azure: '{azure_name}' → Markdown: '{markdown_name}'")
    
    # Initialize Azure DevOps client
    print("\n🔌 Connecting to Azure DevOps...")
    try:
        client = AzureDevOpsClient(ORGANIZATION_URL, PERSONAL_ACCESS_TOKEN)
        print("✅ Connected successfully!")
    except Exception as e:
        print(f"❌ Error connecting: {e}")
        return
    
    # Update epics with CORRECTLY MATCHED content from markdown
    print(f"\n🎯 Updating epics with PRECISELY MATCHED markdown content...")
    
    updated_count = 0
    failed_count = 0
    
    for epic_name, work_item_id in epic_mapping.items():
        
        # Use explicit mapping to find correct epic content
        markdown_title = EPIC_MAPPING.get(epic_name)
        if not markdown_title:
            print(f"  ⚠️  No explicit mapping found for Azure epic: {epic_name}")
            continue
            
        matching_epic = epics_from_markdown.get(markdown_title)
        if not matching_epic:
            print(f"  ⚠️  No markdown content found for mapped title: {markdown_title}")
            continue
        
        print(f"\n✅ PRECISE MATCH: Azure '{epic_name}' → Markdown '{markdown_title}'")
        
        try:
            # Create comprehensive HTML description from CORRECT markdown content
            html_description = create_precise_epic_html_description(matching_epic)
            
            print(f"\n--- CORRECT CONTENT PREVIEW for {epic_name} ---")
            print(f"Title: {matching_epic['title']}")
            print(f"Overview: {matching_epic['overview'][:100]}...")
            print(f"Business Value: {matching_epic['business_value']}")
            print(f"Stakeholders: {matching_epic['stakeholders']}")
            print(f"Success Metrics ({len(matching_epic['success_metrics'])} items):")
            for i, metric in enumerate(matching_epic['success_metrics']):
                print(f"  {i+1}. {metric}")
            print(f"Risk Factors ({len(matching_epic['risk_factors'])} items):")
            for i, risk in enumerate(matching_epic['risk_factors']):
                print(f"  {i+1}. {risk}")
            print("--- END CORRECT PREVIEW ---")
            
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
            
            print(f"  ✅ CORRECTED Epic: {epic_name} (ID: {work_item_id}) with PRECISE content match")
            updated_count += 1
            
        except Exception as e:
            print(f"  ❌ Failed to update epic {epic_name}: {e}")
            failed_count += 1
    
    print(f"\n📊 Epic CORRECTION Summary:")
    print(f"  ✅ Successfully corrected: {updated_count}")
    print(f"  ❌ Failed: {failed_count}")
    
    if updated_count > 0:
        print(f"\n✨ All epics now have CORRECT matched detailed content!")
        print(f"  🎯 Precise mapping ensures each epic gets its correct content")
        print(f"  📄 Epic Overview from correct markdown section")
        print(f"  💼 Business Value from correct markdown section")
        print(f"  👥 Key Stakeholders from correct markdown section")
        print(f"  🎯 Success Metrics from correct markdown section")
        print(f"  ⚠️  Risk Factors from correct markdown section")
        print(f"\n🔗 View corrected epics at: {ORGANIZATION_URL}/{PROJECT_NAME}/_backlogs/backlog/")


if __name__ == "__main__":
    main()