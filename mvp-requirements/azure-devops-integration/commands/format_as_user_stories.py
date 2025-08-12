#!/usr/bin/env python3
"""
Format as User Stories - Reformat work items into proper user story format
"""

import sys
import re
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from azure_devops_manager import AzureDevOpsManager, ConfigManager
from azure.devops.v7_1.work_item_tracking.models import JsonPatchOperation


def create_proper_user_story_description(story_data) -> str:
    """Create proper user story description with As a... I want... So that..."""
    
    description = f"""
    <h2>📋 User Story</h2>
    <div style="background-color: #e3f2fd; padding: 15px; border-left: 4px solid #1976d2; margin: 10px 0;">
        <p><strong>As a</strong> {story_data['as_a']}</p>
        <p><strong>I want</strong> {story_data['i_want']}</p>
        <p><strong>So that</strong> {story_data['so_that']}</p>
    </div>

    <h2>📊 System Workflow</h2>
    <div style="background-color: #f8f9fa; padding: 15px; border: 1px solid #dee2e6; margin: 10px 0;">
        <pre><code class="language-mermaid">
{story_data['mermaid']}
        </code></pre>
    </div>

    <h2>🔧 Technical Implementation</h2>
    <div style="background-color: #fff3e0; padding: 15px; border-left: 4px solid #ff9800; margin: 10px 0;">
        <p><strong>Integration Points:</strong> {story_data['dependencies']}</p>
        <p><strong>Technical Notes:</strong> {story_data['technical_notes']}</p>
    </div>

    <h2>📚 Additional Resources</h2>
    <div style="background-color: #f3e5f5; padding: 10px; border: 1px solid #9c27b0; margin: 10px 0;">
        <p><em>Detailed technical specifications and business rules available in linked documentation</em></p>
    </div>
    """
    
    return description


def create_proper_acceptance_criteria(story_data) -> str:
    """Create proper Given/When/Then acceptance criteria"""
    
    criteria = f"""Given I am a {story_data['persona']} using the Manhattan Active Omni system
When {story_data['when_condition']}
Then {story_data['then_result']}

{story_data['detailed_criteria']}

Definition of Done:
• All technical validations pass
• Integration with external systems works correctly
• System handles error conditions gracefully
• Performance meets specified requirements
• Documentation is complete and accurate"""
    
    return criteria


def get_story_definitions():
    """Define proper user story content for each UC"""
    
    return {
        "UC-001": {
            "as_a": "QC Small Format store manager",
            "i_want": "to process normal individual product orders through the system",
            "so_that": "customers can purchase individual products with standard pricing and receive them efficiently",
            "persona": "QC Small Format store manager",
            "when_condition": "I receive a normal order from a customer through Kafka",
            "then_result": "the system validates, processes, and fulfills the order following the complete 9-step workflow",
            "detailed_criteria": """• Order received via Kafka is validated for OrderID, ShipFromLocationID, and IsForceAllocation=True
• Data enrichment completes for ShortDescription and ImageURL
• Financial calculations (SubTotal, TotalCharge, OrderTotal, TotalDiscount, TotalTaxes) maintain DECIMAL(18,4) precision
• Force allocation processes with status 2000 (Allocated)
• COD payment status set to 5000 (Paid)
• Single release created with status 3000 (Released)
• Slick API updates order to 7000 (Fulfilled)
• Order progresses to 7500 (Delivered) upon customer confirmation""",
            "dependencies": "Kafka Order Create topic, T1 Fulfillment Centers, Slick REST API, Grab delivery integration, PMP coordination",
            "technical_notes": "9-step workflow with IsForceAllocation=True, COD payment only, single release policy, DECIMAL(18,4) financial precision"
        },
        
        "UC-002": {
            "as_a": "QC Small Format store manager",
            "i_want": "to process bundle orders containing multiple products sold as a unit",
            "so_that": "customers can purchase product bundles with special pricing and atomic fulfillment",
            "persona": "QC Small Format store manager",
            "when_condition": "I receive a bundle order (isBundle=True) from a customer",
            "then_result": "the system validates all bundle fields, expands components, and processes atomically",
            "detailed_criteria": """• Bundle order validation includes isBundle=True and 5 bundle-specific rules
• Bundle fields validated: BundleRefId, PackUnitPrice, NumberOfPack, ProductNameTH, ProductNameEN
• Bundle expansion into individual components completes successfully
• Atomic allocation processes - all components allocated or none (with rollback)
• Bundle discount distribution applied across all components
• Single release contains all bundle components
• All components fulfilled together as a complete bundle""",
            "dependencies": "UC-001 foundation, Bundle product catalog, Component pricing engine",
            "technical_notes": "Extends UC-001 with bundle validation (5 additional rules), atomic allocation with rollback, component expansion"
        },
        
        "UC-003": {
            "as_a": "QC Small Format store manager", 
            "i_want": "to process orders with pack quantities and pack-based pricing",
            "so_that": "customers can purchase products in pack quantities with correct pricing calculations",
            "persona": "QC Small Format store manager",
            "when_condition": "I receive an order containing pack quantities (PackOrderedQty, NumberOfPack)",
            "then_result": "the system validates pack fields and calculates pricing using pack formula",
            "detailed_criteria": """• Pack validation rules pass: PackUnitPrice, PackOrderedQty > 0, NumberOfPack > 0
• Pack pricing calculation: PackUnitPrice × PackOrderedQty × NumberOfPack
• Pack-based allocation logic processes correctly
• DECIMAL(18,4) precision maintained for all pack calculations
• Pack quantity information included in release
• Pack handling coordinated through fulfillment""",
            "dependencies": "UC-001 foundation, Pack pricing configuration engine",
            "technical_notes": "Extends UC-001 with 3 additional pack validation rules and pack-based pricing formula"
        },
        
        "UC-004": {
            "as_a": "QC Small Format store manager",
            "i_want": "to process complex bundle orders that include pack quantities", 
            "so_that": "customers can purchase bundled products in pack quantities with combined pricing",
            "persona": "QC Small Format store manager",
            "when_condition": "I receive a bundle+pack order (most complex scenario)",
            "then_result": "the system handles complex validation, atomic allocation, and advanced pricing",
            "detailed_criteria": """• Complex validation: 5 bundle rules + 1 pack rule = 6 additional validations
• Bundle expansion with pack quantity calculations for all components
• Enhanced atomic allocation: all bundle components with pack quantities or none
• Complex pricing: bundle discounts applied to pack-based calculations
• Single release coordinates bundle components with pack quantities
• Complete bundle with pack handling through fulfillment""",
            "dependencies": "UC-001, UC-002, UC-003 foundations, Complex pricing engine",
            "technical_notes": "Most complex scenario combining bundle logic with pack processing, requires enhanced rollback mechanisms"
        },
        
        "UC-005": {
            "as_a": "QC Small Format store manager",
            "i_want": "to process product substitutions with customer approval",
            "so_that": "unavailable products can be replaced while maintaining customer satisfaction",
            "persona": "QC Small Format store manager", 
            "when_condition": "a product substitution is needed due to availability issues",
            "then_result": "the system facilitates customer approval and processes the substitution",
            "detailed_criteria": """• Slick platform contacts customer for substitution confirmation
• 20% price increment limit enforced (merchant app can override)
• Customer approval required before any substitution processing
• OMS edits order details with substituted product
• Payment adjustment processed if required
• PMP receives payment success confirmation
• Order bypasses release for direct fulfillment""",
            "dependencies": "Slick customer communication platform, PMP integration, Payment processing system",
            "technical_notes": "5-step customer-centric process with direct fulfillment bypass, 20% increment limit with merchant override"
        },
        
        "UC-006": {
            "as_a": "QC Small Format store manager",
            "i_want": "to cancel orders before they are released for fulfillment",
            "so_that": "customers can cancel unwanted orders within the allowed timeframe",
            "persona": "QC Small Format store manager",
            "when_condition": "a cancellation request is received via Slick API for an eligible order",
            "then_result": "the system validates eligibility and processes the cancellation",
            "detailed_criteria": """• Slick calls REST API with cancellation request
• System validates order status ≤ 3000 (Released)
• Cancellation rejected if order status beyond Released
• Order status updated to 9000 (Canceled) when eligible
• All allocated inventory released back to available stock
• Full order cancellation only (no partial line item cancellation)""",
            "dependencies": "Slick REST API, Inventory management system, Order status validation",
            "technical_notes": "3-step REST API process with status validation, full order cancellation only"
        },
        
        "UC-007": {
            "as_a": "QC Small Format store manager",
            "i_want": "to track order delivery status with customer confirmation",
            "so_that": "customers receive accurate delivery updates and confirm receipt",
            "persona": "QC Small Format store manager",
            "when_condition": "an order reaches fulfilled status and needs delivery tracking",
            "then_result": "the system coordinates delivery tracking and customer confirmation",
            "detailed_criteria": """• Slick updates order to 7000 (Fulfilled) with tracking information
• Customer receives tracking details when order fulfilled
• Customer confirms receipt through Grab app
• Grab marks order as "Collected" by customer
• PMP sends final delivery confirmation to OMS
• Order status updates to 7500 (Delivered)""",
            "dependencies": "Slick platform, Grab delivery system, PMP coordination",
            "technical_notes": "2-step event-driven process with real-time tracking and customer confirmation through Grab app"
        }
    }


def extract_mermaid_from_file(file_path: Path) -> str:
    """Extract mermaid diagram from workflow file"""
    try:
        content = file_path.read_text(encoding='utf-8')
        pattern = r'```mermaid\n(.*?)\n```'
        match = re.search(pattern, content, re.DOTALL)
        return match.group(1).strip() if match else ""
    except Exception:
        return ""


def main():
    """Reformat all user stories into proper user story format"""
    
    print("📝 Reformatting user stories into proper format...")
    
    # Load configuration
    config_dir = Path(__file__).parent.parent
    try:
        org_url, project, pat = ConfigManager.load_config(config_dir)
        print(f"🔧 Configuration loaded for project: {project}")
    except ValueError as e:
        print(f"❌ {e}")
        return
    
    # Initialize Azure DevOps manager
    print("🔌 Connecting to Azure DevOps...")
    try:
        manager = AzureDevOpsManager(org_url, pat, project)
        print("✅ Connected successfully!")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return
    
    # Load work item mapping
    mapping = ConfigManager.load_work_item_mapping(config_dir)
    story_ids = mapping.get('stories', {})
    
    if not story_ids:
        print("❌ No user stories found in mapping file")
        return
    
    # Get story definitions
    story_definitions = get_story_definitions()
    
    # Workflow files for mermaid extraction
    workflow_files = {
        "UC-001": "UC-001-System-Workflow.md",
        "UC-002": "UC-002-Bundle-Order-Workflow.md", 
        "UC-003": "UC-003-Pack-Order-Workflow.md",
        "UC-004": "UC-004-Bundle-Pack-Workflow.md",
        "UC-005": "UC-005-Substitution-Processing-Workflow.md",
        "UC-006": "UC-006-Order-Cancellation-Workflow.md",
        "UC-007": "UC-007-Delivery-Tracking-Workflow.md"
    }
    
    user_story_dir = Path(__file__).parent.parent.parent / "user story"
    
    print(f"\n📋 Reformatting {len(story_ids)} user stories...")
    
    updated_count = 0
    failed_count = 0
    
    for story_id, work_item_id in story_ids.items():
        if story_id not in story_definitions:
            print(f"⚠️  No definition found for {story_id}, skipping")
            continue
            
        print(f"\n📝 Reformatting {story_id} (Work Item {work_item_id})")
        
        try:
            # Get story definition
            story_def = story_definitions[story_id]
            
            # Extract mermaid diagram from file
            if story_id in workflow_files:
                file_path = user_story_dir / workflow_files[story_id]
                mermaid = extract_mermaid_from_file(file_path)
            else:
                mermaid = ""
            
            # Add mermaid to story data
            story_data = {**story_def, 'mermaid': mermaid}
            
            # Create proper user story description
            description = create_proper_user_story_description(story_data)
            
            # Create proper acceptance criteria  
            acceptance_criteria = create_proper_acceptance_criteria(story_data)
            
            # Update work item
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
            
            manager.wit_client.update_work_item(
                document=document,
                id=work_item_id,
                project=project
            )
            
            print(f"✅ Reformatted {story_id} into proper user story format")
            updated_count += 1
            
        except Exception as e:
            print(f"❌ Failed to reformat {story_id}: {e}")
            failed_count += 1
            continue
    
    # Summary
    print(f"\n📊 Reformatting Summary:")
    print(f"  ✅ Successfully reformatted: {updated_count} user stories")
    print(f"  ❌ Failed to reformat: {failed_count} user stories")
    
    if updated_count > 0:
        print(f"\n🎉 Successfully reformatted {updated_count} user stories!")
        print("📝 All user stories now include:")
        print("   • Proper 'As a... I want... So that...' format")
        print("   • Given/When/Then acceptance criteria")
        print("   • Clear persona definitions")
        print("   • Business value statements")
        print("   • Technical implementation details")
        print("   • System workflow diagrams")
        print(f"🔗 View reformatted project at: {org_url}/{project}/_backlogs/backlog/")


if __name__ == "__main__":
    main()