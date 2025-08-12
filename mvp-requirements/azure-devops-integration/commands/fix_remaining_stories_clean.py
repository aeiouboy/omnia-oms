#!/usr/bin/env python3
"""
Fix UC-002 through UC-007 with exact same clean format that worked for UC-001
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from azure_devops_manager import AzureDevOpsManager
from azure.devops.v7_1.work_item_tracking.models import JsonPatchOperation
import os


def get_clean_user_stories():
    """Define clean, simple user story format using exact same pattern that worked for UC-001"""
    
    return {
        "UC-002": {
            "title": "UC-002: Bundle Order Processing", 
            "description": """As a QC Small Format store manager
I want to process bundle orders that contain multiple products sold as a unit
So that customers can purchase promotional bundles and increase our average order value by 25%

BUSINESS VALUE:
• Enable promotional bundles to increase average order value
• Provide customers convenient product combinations
• Maintain accurate pricing across bundle components
• Support atomic fulfillment for bundle integrity

KEY WORKFLOW:
1. Bundle order received with multiple product components
2. System validates bundle composition and pricing
3. All bundle components allocated together (atomic operation)
4. Bundle discount distributed across components
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
• Bundle pricing calculations are accurate with DECIMAL(18,4) precision
• COD payment for complete bundle amount
• Single release created containing ALL bundle components
• All components fulfilled together maintaining bundle integrity

DEFINITION OF DONE:
• All bundle validation rules pass
• Atomic allocation working with rollback capability
• Bundle integrity maintained through delivery
• Integration with Kafka, T1, Slick, and Grab systems works"""
        },
        
        "UC-003": {
            "title": "UC-003: Pack Order Processing",
            "description": """As a QC Small Format store manager
I want to process orders with pack quantities and pack-based pricing
So that customers can purchase products in bulk quantities with accurate pack calculations

BUSINESS VALUE:
• Support bulk purchasing for customer convenience
• Accurate pack-based pricing calculations
• Improved inventory management for packaged goods
• Maintain pricing precision for pack quantities

KEY WORKFLOW:
1. Order received with pack quantities (PackOrderedQty, NumberOfPack)
2. System validates pack quantities and pricing
3. Pack-based calculations applied: PackUnitPrice × PackOrderedQty × NumberOfPack
4. Pack quantities allocated from inventory
5. Customer receives correct pack quantities as ordered""",
            
            "acceptance_criteria": """ACCEPTANCE CRITERIA:

✓ Pack Validation
• PackUnitPrice validation ensures value > 0 with DECIMAL(18,4) precision
• PackOrderedQty validation ensures quantity > 0
• NumberOfPack validation ensures pack count > 0

✓ Pack Calculations
• Pack pricing formula applied correctly
• DECIMAL(18,4) precision maintained throughout calculations
• Tax calculations applied to complete pack amounts
• Standard calculations (SubTotal, TotalCharge, OrderTotal) performed

✓ Inventory & Fulfillment
• Pack quantities properly allocated from inventory
• Pack availability verified at fulfillment location
• Pack handling instructions included in release
• Customer receives correct pack quantities as ordered

DEFINITION OF DONE:
• All pack validation rules pass
• Pack-based pricing formula working correctly
• Pack quantity coordination through fulfillment
• Integration with standard order processing workflow"""
        },
        
        "UC-004": {
            "title": "UC-004: Bundle with Pack Processing",
            "description": """As a QC Small Format store manager
I want to process complex bundle orders that include pack quantities
So that customers can purchase the most attractive offers combining bundles with pack pricing

BUSINESS VALUE:
• Support most complex and valuable promotional offers
• Combine bundle discounts with pack pricing advantages
• Maximize customer order value opportunities
• Maintain accuracy for complex pricing scenarios

KEY WORKFLOW:
1. Complex order received (bundle + pack quantities)
2. System validates both bundle and pack requirements
3. Advanced calculations: bundle discounts applied to pack pricing
4. Enhanced atomic allocation for bundle+pack combinations
5. Complete fulfillment with both bundle and pack coordination""",
            
            "acceptance_criteria": """ACCEPTANCE CRITERIA:

✓ Complex Validation
• All 5 bundle validation rules (BundleRefId, PackUnitPrice, NumberOfPack, ProductNameTH, ProductNameEN)
• Plus 1 pack validation rule (PackOrderedQty > 0)
• Combined validation logic for both bundle and pack requirements

✓ Advanced Processing
• Bundle expansion into individual components
• Pack quantity calculations for all bundle components
• Complex relationship mapping between bundle components and pack quantities

✓ Financial Calculations
• Bundle discount distribution across pack-based component pricing
• Complex formula: (PackUnitPrice × PackOrderedQty × NumberOfPack) with bundle discounts
• Multi-level pricing calculations with DECIMAL(18,4) precision

✓ Enhanced Fulfillment
• ALL bundle components with pack quantities allocated together or NONE
• Enhanced rollback mechanism for complex scenarios
• Complete bundle+pack coordination through fulfillment

DEFINITION OF DONE:
• Most complex validation scenario passes (5 bundle + 1 pack rules)
• Enhanced atomic allocation with complex rollback capability
• Multi-level pricing calculations accurate
• Complete bundle+pack coordination working"""
        },
        
        "UC-005": {
            "title": "UC-005: Substitution Processing",
            "description": """As a QC Small Format store manager
I want to handle product substitutions with customer approval
So that unavailable products can be replaced while maintaining customer satisfaction

BUSINESS VALUE:
• Maintain customer satisfaction when products unavailable
• Reduce order cancellations due to inventory issues
• Provide flexible fulfillment options
• Support customer choice in substitution decisions

KEY WORKFLOW:
1. Customer contacted via Slick for substitution approval
2. OMS processes order modification based on customer approval
3. Customer pays new price for modified order
4. Payment success confirmation sent to PMP
5. Final substitution confirmation and order completion""",
            
            "acceptance_criteria": """ACCEPTANCE CRITERIA:

✓ Customer Confirmation
• Slick platform contacts customer for substitution approval
• Customer receives substitution offer with price comparison
• Customer can approve, reject, or request alternatives

✓ Order Modification
• OMS processes order detail editing after customer approval
• Item details updated with substitute product information
• Promotional pricing recalculated for substitute items
• New order total calculated with substitution pricing

✓ Payment Processing
• Customer pays new price for modified order
• 20% increment limit enforced (merchant app can override)
• Payment methods support including COD
• Additional charges processed for price differences

✓ System Synchronization
• PMP sends final substitution confirmation to OMS
• Order status updated to reflect completed substitution
• Order bypasses release for direct fulfillment to Fulfilled status

DEFINITION OF DONE:
• Customer-centric approval workflow working
• 5-step substitution process complete
• 20% price increment validation working
• Direct fulfillment bypass implemented"""
        },
        
        "UC-006": {
            "title": "UC-006: Order Cancellation",
            "description": """As a QC Small Format store manager
I want to process order cancellations before fulfillment begins
So that customers have flexibility while protecting operational efficiency

BUSINESS VALUE:
• Provide customers flexibility for order management
• Protect operational efficiency with clear cancellation boundaries
• Reduce wasted fulfillment effort and costs
• Maintain inventory accuracy with proper allocation release

KEY WORKFLOW:
1. Slick platform calls REST API with cancellation request
2. System validates order status ≤ Released (3000)
3. Order status updated to Canceled and inventory released""",
            
            "acceptance_criteria": """ACCEPTANCE CRITERIA:

✓ API Integration
• Slick platform calls REST API with cancellation request
• Full order cancellation only (no partial line item cancellation)
• Standard REST API request/response pattern
• Real-time processing with immediate validation

✓ Status Validation
• System validates order status ≤ 3000 (Released)
• If status > 3000: Return error response (cannot cancel)
• If status ≤ 3000: Cancellation allowed, OMS responds success
• Clear business logic with automatic validation

✓ Order Processing
• Order status updated to 9000 (Canceled)
• ALL allocated inventory released back to available stock
• Inventory adjustments processed immediately
• Cancellation timestamp and audit trail recorded

DEFINITION OF DONE:
• Simple 3-step REST API workflow working
• Status validation with Released threshold functional
• Full order cancellation only
• Immediate inventory release implemented"""
        },
        
        "UC-007": {
            "title": "UC-007: Delivery Tracking",
            "description": """As a QC Small Format store manager
I want to provide customers real-time delivery tracking with confirmation
So that customers have delivery transparency and reduce delivery inquiries by 50%

BUSINESS VALUE:
• Improve customer experience through delivery transparency
• Reduce customer service inquiries about delivery status
• Build customer confidence in delivery service
• Enable customer-confirmed delivery completion

KEY WORKFLOW:
1. Slick updates order to Fulfilled with tracking information
2. Customer confirms receipt through Grab mobile app""",
            
            "acceptance_criteria": """ACCEPTANCE CRITERIA:

✓ Fulfilled Status Update
• Slick updates order to 7000 (Fulfilled) with tracking information
• Customer receives tracking details when order fulfilled
• Order officially handed off to delivery provider (Grab)
• Tracking information provided to customer automatically

✓ Customer Delivery Confirmation
• Customer confirms receipt through Grab mobile app
• Grab marks order as "Collected" by customer
• PMP sends final delivery confirmation to OMS
• Order status updated to 7500 (Delivered)

DEFINITION OF DONE:
• Simple 2-step event-driven workflow working
• Real-time tracking and status updates functional
• Customer confirmation through Grab app working
• Final status progression: Fulfilled → Delivered"""
        }
    }


def main():
    """Update user stories with clean format"""
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    org_url = os.getenv('AZURE_DEVOPS_ORG_URL')
    pat = os.getenv('AZURE_DEVOPS_PAT')  
    project = os.getenv('AZURE_DEVOPS_PROJECT')
    
    if not all([org_url, pat, project]):
        print("Error: Missing required environment variables")
        return
    
    # Work item mapping
    work_items = {
        "UC-002": 51816,
        "UC-003": 51817,
        "UC-004": 51818,
        "UC-005": 51819,
        "UC-006": 51820,
        "UC-007": 51821
    }
    
    # Initialize manager
    manager = AzureDevOpsManager(org_url, pat, project)
    
    # Get clean user stories
    user_stories = get_clean_user_stories()
    
    print("🔧 Fixing user story formatting with clean, simple format...")
    print("=" * 60)
    
    success_count = 0
    
    for uc_id, work_item_id in work_items.items():
        if uc_id in user_stories:
            story = user_stories[uc_id]
            
            print(f"\nUpdating {uc_id} (Work Item {work_item_id})...")
            
            # Create update operations
            updates = [
                JsonPatchOperation(
                    op="replace",
                    path="/fields/System.Title",
                    value=story["title"]
                ),
                JsonPatchOperation(
                    op="replace",
                    path="/fields/System.Description", 
                    value=story["description"]
                ),
                JsonPatchOperation(
                    op="replace",
                    path="/fields/Microsoft.VSTS.Common.AcceptanceCriteria",
                    value=story["acceptance_criteria"]
                )
            ]
            
            try:
                result = manager.update_work_item(work_item_id, updates)
                if result:
                    print(f"✅ Successfully updated {uc_id}")
                    success_count += 1
                else:
                    print(f"❌ Failed to update {uc_id}")
            except Exception as e:
                print(f"❌ Error updating {uc_id}: {str(e)}")
    
    print("\n" + "=" * 60)
    print(f"🎯 Format fix complete! Updated {success_count}/{len(work_items)} user stories")
    print("Format: Clean, simple user story format that renders properly in Azure DevOps")


if __name__ == "__main__":
    main()