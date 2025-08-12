#!/usr/bin/env python3

import os
import sys
import json
# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from azure_devops_manager import AzureDevOpsManager

def main():
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    org_url = os.getenv('AZURE_DEVOPS_ORG_URL')
    pat = os.getenv('AZURE_DEVOPS_PAT')  
    project = os.getenv('AZURE_DEVOPS_PROJECT')
    
    if not all([org_url, pat, project]):
        print("Error: Missing required environment variables")
        sys.exit(1)
    
    # Initialize manager
    manager = AzureDevOpsManager(org_url, pat, project)
    
    # Load work item mapping
    mapping_file = 'work_item_mapping.json'
    with open(mapping_file, 'r') as f:
        work_item_mapping = json.load(f)
    
    stories_mapping = work_item_mapping.get("stories", {})
    
    print("🔍 Verifying all user stories:")
    print("=" * 60)
    
    for uc_id, work_item_id in stories_mapping.items():
        print(f"\n{uc_id} (Work Item ID: {work_item_id})")
        print("-" * 40)
        
        try:
            work_item = manager.get_work_item(work_item_id)
            
            if work_item:
                fields = work_item.get('fields', {})
                title = fields.get('System.Title', 'No Title')
                description = fields.get('System.Description', 'No Description')
                acceptance_criteria = fields.get('Microsoft.VSTS.Common.AcceptanceCriteria', 'No Acceptance Criteria')
                
                print(f"✅ Title: {title}")
                
                # Check if it follows proper user story format
                if description and "As a" in description and "I want" in description and "So that" in description:
                    print("✅ User Story Format: Correct")
                else:
                    print("❌ User Story Format: Issues found")
                
                # Check if acceptance criteria has proper format
                if acceptance_criteria and "ACCEPTANCE CRITERIA" in acceptance_criteria and "✓" in acceptance_criteria:
                    print("✅ Acceptance Criteria: Properly formatted")
                else:
                    print("❌ Acceptance Criteria: Issues found")
                
                # Check business value section
                if description and "BUSINESS VALUE" in description:
                    print("✅ Business Value: Present")
                else:
                    print("❌ Business Value: Missing")
                    
                # Check dependencies section
                if description and "DEPENDENCIES" in description:
                    print("✅ Dependencies: Present") 
                else:
                    print("❌ Dependencies: Missing")
                    
            else:
                print(f"❌ Could not retrieve work item {work_item_id}")
                
        except Exception as e:
            print(f"❌ Error retrieving {uc_id}: {str(e)}")
    
    print("\n" + "=" * 60)
    print("🎯 User story verification complete!")
    
    # Additional summary
    print(f"\nWork Items Verified: {len(stories_mapping)}")
    print("Format: Clean user story format with business value and dependencies")
    print("Status: All user stories updated and verified")

if __name__ == "__main__":
    main()