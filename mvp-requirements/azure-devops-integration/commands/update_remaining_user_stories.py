#!/usr/bin/env python3

import os
import sys
import json
import requests
# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from azure_devops_manager import AzureDevOpsManager

def get_user_stories():
    """Get clean user stories for UC-002 through UC-007 based on workflow files"""
    
    return {
        "UC-002": {
            "title": "UC-002: Bundle Order Processing",
            "description": """As a QC Small Format store manager
I want to process bundle orders containing multiple products sold as promotional units
So that customers can purchase attractive product combinations while increasing our average order value by 25%

BUSINESS VALUE:
• Enable promotional bundles to boost average order value
• Provide customers convenient product combinations  
• Maintain atomic fulfillment for bundle integrity
• Support complex pricing with bundle discounts

DEPENDENCIES:
• All UC-001 dependencies (Kafka, T1, Slick, Grab, PMP)
• Bundle product catalog and pricing engine
• Enhanced atomic allocation system with rollback capability""",
            "acceptance_criteria": """ACCEPTANCE CRITERIA:

✓ Bundle Validation (5 Additional Rules)
• isBundle = True flag properly identified and validated
• BundleRefId unique bundle identifier validation passes
• PackUnitPrice bundle pricing validation (DECIMAL 18,4) completed
• ProductNameTH (Thai product name) validation passes
• ProductNameEN (English product name) validation passes

✓ Bundle Data Processing
• Standard data enrichment (ShortDescription, ImageURL) completed
• Bundle expansion into individual components processed
• Component relationships and dependencies established

✓ Bundle Financial Calculations
• Standard calculations (SubTotal, TotalCharge, OrderTotal) performed
• Bundle discount distribution calculated across all components
• DECIMAL(18,4) precision maintained for complex bundle pricing

✓ Atomic Bundle Allocation
• ALL bundle components allocated together or NONE (atomic operation)
• Enhanced rollback mechanism for failed component allocation
• Bundle integrity maintained throughout allocation process
• Order status updated to 2000 (Allocated) only when complete

✓ Bundle Payment & Release
• COD payment for complete bundle amount processed
• Single release created containing ALL bundle components
• All components released together maintaining bundle integrity

✓ Bundle Fulfillment
• All bundle components fulfilled as single atomic unit
• Bundle tracking and delivery coordination through Slick/Grab
• Customer receives complete bundle with all components"""
        },
        
        "UC-003": {
            "title": "UC-003: Pack Order Processing",
            "description": """As a QC Small Format store manager
I want to process orders with pack quantities and pack-based pricing
So that customers can purchase products in bulk quantities with accurate pack pricing calculations

BUSINESS VALUE:
• Support bulk purchasing for customer convenience
• Accurate pack-based pricing calculations
• Improved inventory management for packaged goods
• Maintain pricing precision for pack quantities

DEPENDENCIES:
• All UC-001 dependencies (Kafka, T1, Slick, Grab, PMP)
• Pack pricing configuration engine
• Enhanced inventory management for pack quantities""",
            "acceptance_criteria": """ACCEPTANCE CRITERIA:

✓ Pack Validation (3 Additional Rules)
• PackUnitPrice validation ensures value > 0 with DECIMAL(18,4) precision
• PackOrderedQty validation ensures quantity > 0
• NumberOfPack validation ensures pack count > 0

✓ Pack Data Processing
• Standard data enrichment (ShortDescription, ImageURL) completed
• Pack quantity calculations and validation performed
• Pack dimension and weight calculations if applicable

✓ Pack-Based Financial Calculations
• Standard calculations (SubTotal, TotalCharge, OrderTotal) performed
• Pack pricing formula applied: PackUnitPrice × PackOrderedQty × NumberOfPack
• DECIMAL(18,4) precision maintained throughout pack calculations
• Tax calculations applied to complete pack amounts

✓ Pack Allocation
• Pack quantities properly allocated from inventory
• Pack availability verified at fulfillment location
• Pack quantity relationships maintained through allocation
• Order status updated to 2000 (Allocated)

✓ Pack Payment & Release
• COD payment for complete pack total amount processed
• Single release created with pack quantity information included
• Pack handling instructions included in release

✓ Pack Fulfillment
• Pack quantities coordinated through fulfillment process
• Pack handling instructions provided to fulfillment team
• Customer receives correct pack quantities as ordered"""
        },
        
        "UC-004": {
            "title": "UC-004: Bundle with Pack Processing",
            "description": """As a QC Small Format store manager
I want to process complex bundle orders that include pack quantities
So that customers can purchase the most attractive promotional offers combining bundle discounts with pack-based products

BUSINESS VALUE:
• Support most complex and valuable promotional offers
• Combine bundle discounts with pack pricing advantages
• Maximize customer order value opportunities
• Maintain accuracy for complex pricing scenarios

DEPENDENCIES:
• All dependencies from UC-001, UC-002, and UC-003
• Enhanced pricing engine for complex bundle+pack calculations
• Advanced atomic allocation with enhanced rollback mechanisms""",
            "acceptance_criteria": """ACCEPTANCE CRITERIA:

✓ Complex Validation (6 Total Additional Rules)
• All 5 bundle validation rules (BundleRefId, PackUnitPrice, NumberOfPack, ProductNameTH, ProductNameEN)
• Plus 1 pack validation rule (PackOrderedQty > 0)
• Combined validation logic for both bundle and pack requirements

✓ Enhanced Data Processing
• Standard data enrichment completed
• Bundle expansion into individual components
• Pack quantity calculations for all bundle components
• Complex relationship mapping between bundle components and pack quantities

✓ Advanced Financial Calculations
• Bundle discount distribution across pack-based component pricing
• Complex formula: (PackUnitPrice × PackOrderedQty × NumberOfPack) with bundle discounts
• Multi-level pricing calculations with DECIMAL(18,4) precision
• Advanced discount allocation across complex product structures

✓ Enhanced Atomic Allocation
• ALL bundle components with pack quantities allocated together or NONE
• Enhanced rollback mechanism for complex bundle+pack scenarios
• Component+pack integrity maintained throughout process
• Most complex allocation scenario supported

✓ Complex Payment & Release
• COD payment for entire bundle+pack total amount
• Single release coordinating bundle components with pack quantities
• Complete bundle+pack coordination information included

✓ Comprehensive Fulfillment
• All bundle components with pack quantities fulfilled as atomic unit
• Complex coordination between bundle relationships and pack handling
• Customer receives complete bundle with all pack quantities correct"""
        },
        
        "UC-005": {
            "title": "UC-005: Substitution Processing",
            "description": """As a QC Small Format store manager
I want to handle product substitutions with customer approval
So that unavailable products can be replaced while maintaining customer satisfaction and reducing order cancellations

BUSINESS VALUE:
• Maintain customer satisfaction when products unavailable
• Reduce order cancellations due to inventory issues
• Provide flexible fulfillment options
• Support customer choice in substitution decisions

DEPENDENCIES:
• Slick platform for customer communication
• PMP (Partner Management Platform) integration
• Payment processing system for price adjustments
• Enhanced order editing capabilities in OMS""",
            "acceptance_criteria": """ACCEPTANCE CRITERIA:

✓ Customer Confirmation (Step A)
• Slick platform contacts customer for substitution approval
• Customer receives substitution offer with price comparison
• Formal confirmation process with contract approval
• Customer can approve, reject, or request alternatives

✓ Order Modification (Step B)
• OMS processes order detail editing based on customer approval
• Item details updated with substitute product information
• Promotional pricing recalculated for substitute items
• New order total calculated with substitution pricing

✓ Payment Processing (Step C)
• Customer pays new price for modified order
• Additional charges processed for price differences
• Payment methods support including COD
• 20% increment limit enforced (merchant app can override)

✓ Payment Confirmation (Step D)
• Payment success confirmation sent to PMP
• Partner Management Platform notified of successful payment
• Payment status updated across all integrated systems
• Integration synchronization between OMS and PMP

✓ System Synchronization (Step E)
• PMP sends final substitution confirmation to OMS
• Order status updated to reflect completed substitution
• All systems synchronized with final substitution state
• Order bypasses release for direct fulfillment to 7000 (Fulfilled)"""
        },
        
        "UC-006": {
            "title": "UC-006: Order Cancellation",
            "description": """As a QC Small Format store manager
I want to process order cancellations before fulfillment begins
So that customers have flexibility to cancel unwanted orders while protecting operational efficiency

BUSINESS VALUE:
• Provide customers flexibility for order management
• Protect operational efficiency with clear cancellation boundaries
• Reduce wasted fulfillment effort and costs
• Maintain inventory accuracy with proper allocation release

DEPENDENCIES:
• Slick REST API integration
• Inventory management system for allocation release
• Order status validation system""",
            "acceptance_criteria": """ACCEPTANCE CRITERIA:

✓ API Integration (Step A)
• Slick platform calls REST API with cancellation request
• Full order cancellation only (no partial line item cancellation)
• Standard REST API request/response pattern
• Real-time processing with immediate validation

✓ Status Validation (Step B)
• System validates order status ≤ 3000 (Released)
• If status > 3000: Return error response (cannot cancel)
• If status ≤ 3000: Cancellation allowed, OMS responds success
• Clear business logic with automatic validation

✓ Order Processing (Step C)
• Order status updated to 9000 (Canceled)
• ALL allocated inventory released back to available stock
• Inventory adjustments processed immediately
• Cancellation timestamp and audit trail recorded"""
        },
        
        "UC-007": {
            "title": "UC-007: Delivery Tracking",
            "description": """As a QC Small Format store manager
I want to provide customers real-time delivery tracking with confirmation
So that customers have delivery transparency and our store reduces delivery inquiries by 50%

BUSINESS VALUE:
• Improve customer experience through delivery transparency
• Reduce customer service inquiries about delivery status
• Build customer confidence in delivery service
• Enable customer-confirmed delivery completion

DEPENDENCIES:
• Slick platform for fulfilled status and tracking
• Grab delivery system for customer confirmation
• PMP coordination for final delivery confirmation
• Real-time status update capabilities""",
            "acceptance_criteria": """ACCEPTANCE CRITERIA:

✓ Fulfilled Status Update (Step A)
• Slick updates order to 7000 (Fulfilled) with tracking information
• Customer receives tracking details when order fulfilled
• Order officially handed off to delivery provider (Grab)
• Tracking information provided to customer automatically

✓ Customer Delivery Confirmation (Step B)
• Customer confirms receipt through Grab mobile app
• Grab marks order as "Collected" by customer
• PMP sends final delivery confirmation to OMS
• Order status updated to 7500 (Delivered)"""
        }
    }

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
    
    # Get user stories
    user_stories = get_user_stories()
    
    # Use the stories mapping from the JSON file
    stories_mapping = work_item_mapping.get("stories", {})
    
    print(f"Found {len(stories_mapping)} work items in mapping:")
    for uc, item_id in stories_mapping.items():
        print(f"  {uc}: {item_id}")
    print()
    
    # Update each user story
    success_count = 0
    for uc_id, story_data in user_stories.items():
        if uc_id in stories_mapping:
            work_item_id = stories_mapping[uc_id]
            
            print(f"Updating {uc_id} (Work Item {work_item_id})...")
            
            # Prepare update data
            patch_data = [
                {
                    "op": "replace",
                    "path": "/fields/System.Title",
                    "value": story_data["title"]
                },
                {
                    "op": "replace", 
                    "path": "/fields/System.Description",
                    "value": story_data["description"]
                },
                {
                    "op": "replace",
                    "path": "/fields/Microsoft.VSTS.Common.AcceptanceCriteria", 
                    "value": story_data["acceptance_criteria"]
                }
            ]
            
            try:
                result = manager.update_work_item(work_item_id, patch_data)
                if result:
                    print(f"✅ Successfully updated {uc_id}")
                    success_count += 1
                else:
                    print(f"❌ Failed to update {uc_id}")
            except Exception as e:
                print(f"❌ Error updating {uc_id}: {str(e)}")
        else:
            print(f"⚠️ {uc_id} not found in work item mapping")
    
    print(f"\n🎯 User story updates complete! Updated {success_count}/{len(user_stories)} stories.")

if __name__ == "__main__":
    main()