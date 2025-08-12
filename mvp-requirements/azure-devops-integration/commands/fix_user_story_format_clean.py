#!/usr/bin/env python3
"""
Fix User Story Format - Clean, simple format that renders properly in Azure DevOps
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from azure_devops_manager import AzureDevOpsManager, ConfigManager
from azure.devops.v7_1.work_item_tracking.models import JsonPatchOperation


def get_clean_user_stories():
    """Define clean, simple user story format that renders properly in Azure DevOps"""
    
    return {
        "UC-001": {
            "title": "UC-001: Normal Order Processing",
            "description": """As a QC Small Format store manager
I want to process normal customer orders efficiently through the system
So that customers receive their products on time and our store meets daily sales targets

BUSINESS VALUE:
• Process 300+ daily orders per store with 99.9% accuracy
• Reduce order processing time from 5 minutes to under 2 minutes
• Ensure same-day fulfillment for 90% of orders

KEY WORKFLOW:
1. Order received from customer through mobile app
2. System validates order details and inventory
3. Payment processed (Cash on Delivery)
4. Order allocated and released for fulfillment
5. Customer receives tracking and delivery confirmation""",
            
            "acceptance_criteria": """ACCEPTANCE CRITERIA:

✓ Order Processing
• Order received via Kafka is validated within 30 seconds
• OrderID and ShipFromLocationID are properly validated
• Force allocation setting (IsForceAllocation=True) is applied

✓ Data Management  
• ShortDescription and ImageURL are enriched for display
• Financial calculations maintain DECIMAL(18,4) precision
• SubTotal, TotalCharge, OrderTotal calculated correctly

✓ Fulfillment Flow
• COD payment status set to "Paid" 
• Single release created with status "Released"
• Slick API updates order to "Fulfilled" status
• Customer receives delivery confirmation

✓ Performance Standards
• Order processing completes within 2 minutes
• System handles 300+ orders per hour per store
• 99.9% uptime during business hours

DEFINITION OF DONE:
• All technical validations pass
• Integration with external systems works correctly  
• Performance meets specified requirements
• Documentation is complete"""
        },
        
        "UC-002": {
            "title": "UC-002: Bundle Order Processing", 
            "description": """As a QC Small Format store manager
I want to process bundle orders that contain multiple products sold as a unit
So that customers can purchase promotional bundles and increase our average order value by 25%

BUSINESS VALUE:
• Enable promotional bundles to increase average order value
• Provide customers convenient product combinations
• Maintain accurate pricing across bundle components

KEY WORKFLOW:
1. Bundle order received with multiple product components
2. System validates bundle composition and pricing
3. All bundle components allocated together (atomic operation)
4. Special bundle pricing applied across components
5. Complete bundle fulfilled as single unit""",
            
            "acceptance_criteria": """ACCEPTANCE CRITERIA:

✓ Bundle Validation
• Bundle flag (isBundle=True) is properly identified
• BundleRefId, PackUnitPrice, NumberOfPack validated
• ProductNameTH and ProductNameEN are present

✓ Component Processing
• Bundle expands into individual product components
• All components must be available for atomic allocation
• Bundle discount distributed across all components
• Rollback occurs if any component unavailable

✓ Pricing & Fulfillment
• Bundle pricing calculations are accurate
• All components included in single release
• Complete bundle fulfilled together
• Customer receives consolidated tracking

✓ Business Rules
• Minimum 2 products required for bundle
• Maximum 10 products per bundle
• Bundle discounts up to 30% supported

DEFINITION OF DONE:
• Bundle validation rules pass completely
• Atomic allocation works with proper rollback
• Bundle pricing calculations are accurate
• Complete bundle fulfilled as unit"""
        },
        
        "UC-003": {
            "title": "UC-003: Pack Order Processing",
            "description": """As a QC Small Format store manager  
I want to process orders with pack quantities and pack-based pricing
So that customers can purchase products in bulk quantities with accurate pricing

BUSINESS VALUE:
• Support bulk purchasing for customer convenience
• Accurate pack-based pricing calculations
• Improved inventory management for packaged goods

KEY WORKFLOW:
1. Order received with pack quantity specifications
2. System validates pack pricing and quantities
3. Pack-based calculations applied (PackUnitPrice × PackOrderedQty × NumberOfPack)
4. Pack quantities allocated correctly
5. Pack information included in fulfillment""",
            
            "acceptance_criteria": """ACCEPTANCE CRITERIA:

✓ Pack Validation
• PackUnitPrice is greater than 0
• PackOrderedQty is greater than 0  
• NumberOfPack is greater than 0
• Pack dimensions and weight calculated

✓ Pricing Calculations
• Pack formula: PackUnitPrice × PackOrderedQty × NumberOfPack
• DECIMAL(18,4) precision maintained for all calculations
• Pack discounts applied when applicable
• Total pack cost calculated correctly

✓ Allocation & Fulfillment
• Pack quantities properly allocated from inventory
• Pack handling instructions included in release
• Fulfillment coordinated for pack quantities
• Pack information visible to customer

✓ Business Rules
• Maximum 100 packs per order line
• Pack size validation against product catalog
• Pack pricing must match catalog rates

DEFINITION OF DONE:
• Pack validation rules pass completely
• Pricing calculations are accurate
• Pack quantities allocated correctly
• Pack handling coordinated through fulfillment"""
        },
        
        "UC-004": {
            "title": "UC-004: Bundle with Pack Processing",
            "description": """As a QC Small Format store manager
I want to process complex bundle orders that include pack quantities
So that customers can purchase the most attractive promotional offers while maintaining pricing accuracy

BUSINESS VALUE:
• Support most complex and attractive promotional offers
• Combine bundle discounts with pack pricing
• Maximize customer order value opportunities

KEY WORKFLOW:
1. Complex order received (bundle + pack combination)
2. System validates both bundle and pack rules
3. Enhanced atomic allocation for all components with pack quantities
4. Complex pricing applied (bundle discounts + pack calculations)
5. Complete bundle with pack quantities fulfilled together""",
            
            "acceptance_criteria": """ACCEPTANCE CRITERIA:

✓ Complex Validation
• All 5 bundle validation rules pass
• All 3 pack validation rules pass
• Combined validation (6 total rules) completed
• Component availability verified for pack quantities

✓ Enhanced Allocation
• Atomic allocation for all bundle components with pack quantities
• Enhanced rollback mechanism if any component unavailable
• Pack quantities calculated for each bundle component
• Inventory reserved for complete bundle with packs

✓ Complex Pricing
• Bundle discounts applied to pack-based calculations
• Multi-level pricing: (PackPrice × PackQty × NumberOfPacks) × BundleDiscount
• DECIMAL(18,4) precision maintained throughout
• Final pricing validation against business rules

✓ Fulfillment Coordination
• Single release contains all bundle components with pack quantities
• Pack handling instructions for each component
• Complete bundle with packs coordinated through fulfillment
• Customer receives consolidated tracking for entire bundle

DEFINITION OF DONE:
• Most complex validation scenario passes
• Enhanced atomic allocation works correctly
• Complex pricing calculations are accurate  
• Complete bundle with packs fulfilled successfully"""
        },
        
        "UC-005": {
            "title": "UC-005: Substitution Processing",
            "description": """As a QC Small Format store manager
I want to handle product substitutions with customer approval
So that unavailable products can be replaced while maintaining customer satisfaction

BUSINESS VALUE:
• Maintain customer satisfaction when products unavailable
• Reduce order cancellations due to stock issues
• Provide flexible fulfillment options

KEY WORKFLOW:
1. Substitution needed due to inventory shortage
2. Slick platform contacts customer for approval
3. Customer approves or rejects substitution
4. If approved, order updated with substitute product
5. Order processed with substitution""",
            
            "acceptance_criteria": """ACCEPTANCE CRITERIA:

✓ Substitution Detection
• System identifies when product substitution needed
• Alternative products identified from catalog
• Price variance calculated (max 20% increase allowed)
• Merchant override capability for price limits

✓ Customer Approval Process  
• Slick platform contacts customer automatically
• Customer receives substitution offer with price difference
• Customer can approve, reject, or request alternatives
• Approval captured and recorded

✓ Order Processing
• Order details updated with substituted product
• Payment adjustment processed if required
• PMP receives payment confirmation
• Order bypasses standard release process

✓ Business Rules
• Maximum 20% price increase without merchant approval
• Customer approval required for all substitutions
• Substitution must be from same product category
• Maximum 1 substitution per order line

DEFINITION OF DONE:
• Substitution detection works automatically
• Customer approval process functions correctly
• Order processing handles substitutions properly
• Payment adjustments processed accurately"""
        },
        
        "UC-006": {
            "title": "UC-006: Order Cancellation",
            "description": """As a QC Small Format store manager
I want to process order cancellations before fulfillment begins
So that customers have flexibility while protecting operational efficiency

BUSINESS VALUE:
• Provide customers flexibility to cancel unwanted orders
• Protect operational efficiency by limiting cancellation window
• Reduce wasted fulfillment effort and costs

KEY WORKFLOW:
1. Customer requests cancellation through Slick platform
2. System validates order eligibility for cancellation
3. If eligible, order status updated to "Canceled"
4. Allocated inventory released back to available stock
5. Customer receives cancellation confirmation""",
            
            "acceptance_criteria": """ACCEPTANCE CRITERIA:

✓ Cancellation Eligibility
• Slick calls REST API with cancellation request
• System validates order status ≤ 3000 (Released)
• Orders beyond "Released" status cannot be canceled
• Cancellation window clearly communicated to customer

✓ Cancellation Processing
• Order status updated to 9000 (Canceled) when eligible
• All allocated inventory released back to available stock
• Inventory adjustments processed immediately
• Cancellation timestamp recorded

✓ Business Rules
• Full order cancellation only (no partial line cancellation)
• Cancellation must occur before fulfillment begins
• Payment reversal initiated for prepaid orders
• Customer notification sent automatically

✓ System Integration
• Slick REST API handles cancellation requests
• Inventory management system updated immediately
• Order status validation prevents invalid cancellations
• Customer receives confirmation within 5 minutes

DEFINITION OF DONE:
• Cancellation eligibility validation works correctly
• Inventory released back to stock properly
• Full order cancellation processed successfully
• Customer receives timely confirmation"""
        },
        
        "UC-007": {
            "title": "UC-007: Delivery Tracking",
            "description": """As a QC Small Format store manager
I want to provide customers with real-time delivery tracking
So that customers have transparency and our store reduces delivery inquiries by 50%

BUSINESS VALUE:
• Improve customer experience through delivery transparency
• Reduce customer service inquiries about delivery status
• Build customer confidence in delivery service

KEY WORKFLOW:
1. Order reaches fulfilled status with tracking information
2. Customer receives tracking details automatically
3. Customer tracks delivery through Grab app
4. Customer confirms receipt in Grab app
5. Order status updated to delivered""",
            
            "acceptance_criteria": """ACCEPTANCE CRITERIA:

✓ Tracking Initiation
• Slick updates order to 7000 (Fulfilled) with tracking information
• Customer receives tracking details when order fulfilled
• Tracking number and delivery partner information provided
• Estimated delivery time communicated

✓ Real-time Tracking
• Customer accesses tracking through Grab app
• Real-time location and status updates provided
• Delivery progress visible throughout journey
• Delivery partner contact information available

✓ Delivery Confirmation
• Customer confirms receipt through Grab app
• Grab marks order as "Collected" by customer
• PMP sends final delivery confirmation to OMS
• Order status updates to 7500 (Delivered)

✓ Customer Experience
• Tracking information clear and accurate
• Updates provided at key delivery milestones
• Customer can contact delivery partner if needed
• Delivery confirmation process is simple

DEFINITION OF DONE:
• Tracking information provided automatically
• Real-time tracking works through customer app
• Delivery confirmation process functions properly
• Customer experience meets quality standards"""
        }
    }


def main():
    """Update all user stories with clean, readable format"""
    
    print("🔧 Fixing user story format with clean, professional presentation...")
    
    # Load configuration
    config_dir = Path(__file__).parent.parent
    try:
        org_url, project, pat = ConfigManager.load_config(config_dir)
        print(f"✅ Configuration loaded for project: {project}")
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
    
    # Get clean user story definitions
    clean_stories = get_clean_user_stories()
    
    print(f"\n📝 Updating {len(story_ids)} user stories with clean format...")
    
    updated_count = 0
    failed_count = 0
    
    for story_id, work_item_id in story_ids.items():
        if story_id not in clean_stories:
            print(f"⚠️  No clean format definition found for {story_id}, skipping")
            continue
            
        print(f"\n🔧 Fixing {story_id} (Work Item {work_item_id})")
        
        try:
            story_data = clean_stories[story_id]
            
            # Update work item with clean format
            document = [
                JsonPatchOperation(
                    op="replace",
                    path="/fields/System.Title", 
                    value=story_data['title']
                ),
                JsonPatchOperation(
                    op="replace",
                    path="/fields/System.Description", 
                    value=story_data['description']
                ),
                JsonPatchOperation(
                    op="replace",
                    path="/fields/Microsoft.VSTS.Common.AcceptanceCriteria",
                    value=story_data['acceptance_criteria']
                )
            ]
            
            manager.wit_client.update_work_item(
                document=document,
                id=work_item_id,
                project=project
            )
            
            print(f"✅ Fixed {story_id} with clean, professional format")
            updated_count += 1
            
        except Exception as e:
            print(f"❌ Failed to fix {story_id}: {e}")
            failed_count += 1
            continue
    
    # Summary
    print(f"\n📊 Fix Summary:")
    print(f"  ✅ Successfully fixed: {updated_count} user stories")
    print(f"  ❌ Failed to fix: {failed_count} user stories")
    
    if updated_count > 0:
        print(f"\n🎉 Successfully fixed {updated_count} user stories!")
        print("📋 All user stories now have:")
        print("   • Clean, readable 'As a... I want... So that...' format")
        print("   • Clear business value statements")
        print("   • Scannable bullet-point acceptance criteria")
        print("   • Professional presentation without technical clutter")
        print("   • Simple formatting that renders properly in Azure DevOps")
        print(f"🔗 View fixed stories at: {org_url}/{project}/_backlogs/backlog/")


if __name__ == "__main__":
    main()