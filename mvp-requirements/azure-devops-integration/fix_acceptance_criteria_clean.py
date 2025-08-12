#!/usr/bin/env python3
"""
Clean Acceptance Criteria Formatter for Azure DevOps
Generates simple, readable acceptance criteria that render perfectly in Azure DevOps interface.
Based on the workflow technical requirements analysis.
"""

import os
import sys
from typing import Dict, List
from azure.devops.v7_1.work_item_tracking.models import JsonPatchOperation

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from azure_devops_manager import AzureDevOpsManager
import json

def load_config():
    """Load configuration from environment or .env file"""
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    
    org_url = os.getenv('AZURE_DEVOPS_ORG_URL')
    pat = os.getenv('AZURE_DEVOPS_PAT')
    project = os.getenv('AZURE_DEVOPS_PROJECT')
    
    if not all([org_url, pat, project]):
        print("❌ Missing Azure DevOps configuration. Please set:")
        print("   AZURE_DEVOPS_ORG_URL")
        print("   AZURE_DEVOPS_PAT") 
        print("   AZURE_DEVOPS_PROJECT")
        sys.exit(1)
    
    return org_url, pat, project

def create_clean_acceptance_criteria() -> Dict[str, str]:
    """
    Create clean, simple acceptance criteria based on workflow analysis.
    Uses simple text format that renders perfectly in Azure DevOps.
    """
    
    criteria = {
        "UC-001": """• Order Processing Workflow Validation
  ◦ Given a customer places an order with individual products via Kafka Order Create topic
  ◦ When the 9-step workflow processes the order (Order Check → Validation → Allocation → Payment → Release → Fulfillment)
  ◦ Then all required fields are validated (OrderID, ShipFromLocationID, IsForceAllocation=True)
  ◦ And payment status progresses to 5000 (Paid) using COD processing
  ◦ And force allocation bypasses stock validation using specified ShipFromLocationID

• Financial Calculations and Precision
  ◦ Given order items with pricing information
  ◦ When financial calculations are performed
  ◦ Then all amounts are stored with DECIMAL(18,4) precision
  ◦ And customer displays show 2-digit formatting
  ◦ And calculations include SubTotal, TotalCharge, OrderTotal, TotalDiscount, TotalTaxes

• Status Management and Integration
  ◦ Given order progression through workflow stages
  ◦ When status updates occur
  ◦ Then status follows hierarchy: 1000 Open → 2000 Allocated → 3000 Released → 7000 Fulfilled → 7500 Delivered
  ◦ And single release policy enforced per order
  ◦ And Slick REST API integration handles Ship/Short events
  ◦ And delivery tracking coordinates with Grab through PMP platform""",

        "UC-002": """• Bundle Order Validation and Processing
  ◦ Given a customer selects a promotional bundle with isBundle=True flag
  ◦ When bundle validation occurs
  ◦ Then all bundle fields are validated (BundleRefId, PackUnitPrice, NumberOfPack, ProductNameTH, ProductNameEN)
  ◦ And isBundle=True flag is confirmed in validation layer
  ◦ And bundle components are expanded into individual items

• Atomic Bundle Allocation
  ◦ Given bundle components require inventory allocation
  ◦ When allocation processing begins
  ◦ Then ALL bundle components are allocated together OR none are allocated
  ◦ And automatic rollback occurs if any component fails allocation
  ◦ And bundle integrity is maintained throughout the workflow

• Bundle Financial Processing
  ◦ Given bundle pricing and component costs
  ◦ When financial calculations occur
  ◦ Then bundle discounts are distributed proportionally across components
  ◦ And individual component prices are calculated within bundle structure
  ◦ And DECIMAL(18,4) precision is maintained for all bundle calculations
  ◦ And single COD payment covers complete bundle amount""",

        "UC-003": """• Pack Order Validation
  ◦ Given a customer orders products with pack quantities
  ◦ When pack validation occurs  
  ◦ Then PackUnitPrice is validated with DECIMAL(18,4) precision
  ◦ And PackOrderedQty must be greater than 0
  ◦ And NumberOfPack must be greater than 0
  ◦ And pack quantity relationships are logically consistent

• Pack-Based Pricing Calculations
  ◦ Given pack pricing parameters
  ◦ When pricing calculations are performed
  ◦ Then total is calculated using formula: PackUnitPrice × PackOrderedQty × NumberOfPack
  ◦ And financial precision is maintained throughout calculations
  ◦ And tax calculations apply to complete pack amounts

• Pack Allocation and Fulfillment
  ◦ Given pack inventory requirements
  ◦ When allocation and fulfillment occur
  ◦ Then allocation considers pack quantities for inventory management
  ◦ And pack availability is verified at fulfillment location
  ◦ And pack quantity relationships are maintained through delivery
  ◦ And single release includes complete pack quantity information""",

        "UC-004": """• Complex Bundle+Pack Validation
  ◦ Given a customer selects bundle promotions containing pack-based products
  ◦ When comprehensive validation occurs
  ◦ Then ALL bundle fields are validated (BundleRefId, ProductNameTH/EN, PackUnitPrice, NumberOfPack)
  ◦ And PackOrderedQty is validated for pack quantities
  ◦ And isBundle=True flag is confirmed with pack constraints

• Enhanced Atomic Processing
  ◦ Given bundle components with pack quantities require allocation
  ◦ When allocation processing begins
  ◦ Then ALL bundle components with pack quantities are allocated together OR none
  ◦ And enhanced rollback mechanism handles complex scenarios
  ◦ And both bundle relationships and pack quantities are preserved

• Advanced Financial Calculations
  ◦ Given bundle discounts and pack-based pricing
  ◦ When complex pricing calculations occur
  ◦ Then bundle discounts are applied to pack pricing formula: (PackUnitPrice × PackOrderedQty × NumberOfPack) with bundle savings
  ◦ And DECIMAL(18,4) precision is maintained for maximum complexity scenarios
  ◦ And single COD payment covers entire bundle+pack amount
  ◦ And component pricing distribution maintains both bundle and pack relationships""",

        "UC-005": """• Customer Substitution Processing
  ◦ Given a customer requires item substitution due to unavailability
  ◦ When the 5-step substitution process executes
  ◦ Then Slick contacts customer for substitution approval with price comparison
  ◦ And OMS processes order detail editing based on customer approval
  ◦ And customer pays new price with 20% increment limit validation
  ◦ And PMP receives payment confirmation and updates OMS
  ◦ And order progresses directly to Fulfilled status bypassing Release

• Order Cancellation Management
  ◦ Given a cancellation request via Slick REST API
  ◦ When cancellation validation occurs
  ◦ Then only orders with status ≤ 3000 (Released) can be canceled
  ◦ And only full order cancellation is supported (no partial line items)
  ◦ And order status updates to 9000 (Canceled) with immediate inventory release

• Delivery Tracking Coordination
  ◦ Given order fulfillment and delivery requirements
  ◦ When delivery tracking activates
  ◦ Then Slick updates order to 7000 (Fulfilled) with tracking information
  ◦ And customer receives tracking details automatically
  ◦ And customer confirms receipt through Grab mobile app
  ◦ And Grab "Collected" status triggers PMP notification to OMS
  ◦ And final status progresses to 7500 (Delivered) upon confirmation""",

        "UC-006": """• Cancellation Request Processing
  ◦ Given a customer requests order cancellation through Slick platform
  ◦ When cancellation request is received via REST API
  ◦ Then system validates order status is ≤ 3000 (Released threshold)
  ◦ And full order cancellation only is supported (no partial line items)
  ◦ And real-time processing provides immediate validation response

• Status Validation Logic
  ◦ Given order status validation requirements
  ◦ When status check occurs
  ◦ Then if status > 3000: return error response (cannot cancel)
  ◦ And if status ≤ 3000: cancellation allowed, OMS responds success
  ◦ And clear business logic with automatic validation rules applied

• Cancellation Processing
  ◦ Given approved cancellation request
  ◦ When cancellation processing begins
  ◦ Then order status updated to 9000 (Canceled)
  ◦ And ALL allocated inventory released back to available stock
  ◦ And inventory adjustments processed immediately
  ◦ And cancellation timestamp and complete audit trail recorded""",

        "UC-007": """• Delivery Status Updates
  ◦ Given an order ready for delivery tracking
  ◦ When Slick updates order to Fulfilled status
  ◦ Then order marked as 7000 (Fulfilled) with tracking information
  ◦ And customer receives tracking details automatically
  ◦ And order officially handed off to delivery provider (Grab)

• Customer Delivery Confirmation
  ◦ Given customer receives delivered order
  ◦ When customer confirms receipt through Grab mobile app
  ◦ Then Grab marks order as "Collected" by customer
  ◦ And PMP sends final delivery confirmation to OMS
  ◦ And order status updated to 7500 (Delivered)

• Event-Driven Coordination
  ◦ Given real-time tracking requirements
  ◦ When status updates occur across systems
  ◦ Then event-driven processing ensures immediate status changes
  ◦ And complete delivery tracking history is maintained
  ◦ And customer notifications sent at each status progression
  ◦ And integration coordination between Slick, Grab, PMP, and OMS"""
    }
    
    return criteria

def load_work_item_mapping() -> Dict:
    """Load work item mapping from JSON file"""
    mapping_file = "work_item_mapping.json"
    try:
        with open(mapping_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Work item mapping file not found: {mapping_file}")
        sys.exit(1)

def update_acceptance_criteria():
    """Update acceptance criteria for all user stories with clean format"""
    print("🔧 Clean Acceptance Criteria Formatter for Azure DevOps")
    print("=" * 60)
    
    # Load configuration
    org_url, pat, project = load_config()
    
    # Initialize Azure DevOps manager
    manager = AzureDevOpsManager(org_url, pat, project)
    
    # Load work item mapping
    mapping = load_work_item_mapping()
    
    # Load clean acceptance criteria
    clean_criteria = create_clean_acceptance_criteria()
    
    print(f"\n📋 Updating acceptance criteria for {len(clean_criteria)} user stories...")
    
    successful_updates = 0
    total_updates = len(clean_criteria)
    
    for story_id, work_item_id in mapping["stories"].items():
        if story_id in clean_criteria:
            print(f"\n🔄 Updating {story_id} (Work Item {work_item_id})...")
            
            # Create update operation for acceptance criteria field only
            updates = [
                JsonPatchOperation(
                    op="replace", 
                    path="/fields/Microsoft.VSTS.Common.AcceptanceCriteria", 
                    value=clean_criteria[story_id]
                )
            ]
            
            # Perform update
            try:
                success = manager.update_work_item(work_item_id, updates)
                
                if success:
                    print(f"✅ Successfully updated acceptance criteria for {story_id}")
                    successful_updates += 1
                else:
                    print(f"❌ Failed to update {story_id}")
            except Exception as e:
                print(f"❌ Error updating {story_id}: {str(e)}")
        else:
            print(f"⚠️  No clean criteria defined for {story_id}")
    
    # Summary
    print(f"\n📊 Update Summary:")
    print(f"   Successfully updated: {successful_updates}/{total_updates}")
    print(f"   Success rate: {(successful_updates/total_updates)*100:.1f}%")
    
    if successful_updates == total_updates:
        print("🎉 All acceptance criteria updated successfully!")
        print("\n🎯 Key improvements:")
        print("   • Simple bullet format for better Azure DevOps rendering")
        print("   • Clear Given/When/Then structure")
        print("   • Technical requirements from workflow analysis")
        print("   • No complex HTML formatting")
        print("   • Easy to read in Azure DevOps interface")
    else:
        print("⚠️  Some updates failed. Please check the error messages above.")

if __name__ == "__main__":
    update_acceptance_criteria()