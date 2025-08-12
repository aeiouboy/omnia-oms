#!/usr/bin/env python3
"""
Fix Acceptance Criteria with Proper HTML Formatting for Azure DevOps
This script creates properly formatted HTML lists that render correctly in Azure DevOps interface.
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

def create_html_acceptance_criteria() -> Dict[str, str]:
    """
    Create properly formatted HTML acceptance criteria that render correctly in Azure DevOps.
    Uses proper HTML <ul> and <li> tags for clean formatting.
    """
    
    criteria = {
        "UC-001": """<ul>
<li><strong>Order Processing Workflow Validation</strong>
<ul>
<li>Given a customer places an order with individual products via Kafka Order Create topic</li>
<li>When the 9-step workflow processes the order (Order Check → Validation → Allocation → Payment → Release → Fulfillment)</li>
<li>Then all required fields are validated (OrderID, ShipFromLocationID, IsForceAllocation=True)</li>
<li>And payment status progresses to 5000 (Paid) using COD processing</li>
<li>And force allocation bypasses stock validation using specified ShipFromLocationID</li>
</ul>
</li>
<li><strong>Financial Calculations and Precision</strong>
<ul>
<li>Given order items with pricing information</li>
<li>When financial calculations are performed</li>
<li>Then all amounts are stored with DECIMAL(18,4) precision</li>
<li>And customer displays show 2-digit formatting</li>
<li>And calculations include SubTotal, TotalCharge, OrderTotal, TotalDiscount, TotalTaxes</li>
</ul>
</li>
<li><strong>Status Management and Integration</strong>
<ul>
<li>Given order progression through workflow stages</li>
<li>When status updates occur</li>
<li>Then status follows hierarchy: 1000 Open → 2000 Allocated → 3000 Released → 7000 Fulfilled → 7500 Delivered</li>
<li>And single release policy enforced per order</li>
<li>And Slick REST API integration handles Ship/Short events</li>
<li>And delivery tracking coordinates with Grab through PMP platform</li>
</ul>
</li>
</ul>""",

        "UC-002": """<ul>
<li><strong>Bundle Order Validation and Processing</strong>
<ul>
<li>Given a customer selects a promotional bundle with isBundle=True flag</li>
<li>When bundle validation occurs</li>
<li>Then all bundle fields are validated (BundleRefId, PackUnitPrice, NumberOfPack, ProductNameTH, ProductNameEN)</li>
<li>And isBundle=True flag is confirmed in validation layer</li>
<li>And bundle components are expanded into individual items</li>
</ul>
</li>
<li><strong>Atomic Bundle Allocation</strong>
<ul>
<li>Given bundle components require inventory allocation</li>
<li>When allocation processing begins</li>
<li>Then ALL bundle components are allocated together OR none are allocated</li>
<li>And automatic rollback occurs if any component fails allocation</li>
<li>And bundle integrity is maintained throughout the workflow</li>
</ul>
</li>
<li><strong>Bundle Financial Processing</strong>
<ul>
<li>Given bundle pricing and component costs</li>
<li>When financial calculations occur</li>
<li>Then bundle discounts are distributed proportionally across components</li>
<li>And individual component prices are calculated within bundle structure</li>
<li>And DECIMAL(18,4) precision is maintained for all bundle calculations</li>
<li>And single COD payment covers complete bundle amount</li>
</ul>
</li>
</ul>""",

        "UC-003": """<ul>
<li><strong>Pack Order Validation</strong>
<ul>
<li>Given a customer orders products with pack quantities</li>
<li>When pack validation occurs</li>
<li>Then PackUnitPrice is validated with DECIMAL(18,4) precision</li>
<li>And PackOrderedQty must be greater than 0</li>
<li>And NumberOfPack must be greater than 0</li>
<li>And pack quantity relationships are logically consistent</li>
</ul>
</li>
<li><strong>Pack-Based Pricing Calculations</strong>
<ul>
<li>Given pack pricing parameters</li>
<li>When pricing calculations are performed</li>
<li>Then total is calculated using formula: PackUnitPrice × PackOrderedQty × NumberOfPack</li>
<li>And financial precision is maintained throughout calculations</li>
<li>And tax calculations apply to complete pack amounts</li>
</ul>
</li>
<li><strong>Pack Allocation and Fulfillment</strong>
<ul>
<li>Given pack inventory requirements</li>
<li>When allocation and fulfillment occur</li>
<li>Then allocation considers pack quantities for inventory management</li>
<li>And pack availability is verified at fulfillment location</li>
<li>And pack quantity relationships are maintained through delivery</li>
<li>And single release includes complete pack quantity information</li>
</ul>
</li>
</ul>""",

        "UC-004": """<ul>
<li><strong>Complex Bundle+Pack Validation</strong>
<ul>
<li>Given a customer selects bundle promotions containing pack-based products</li>
<li>When comprehensive validation occurs</li>
<li>Then ALL bundle fields are validated (BundleRefId, ProductNameTH/EN, PackUnitPrice, NumberOfPack)</li>
<li>And PackOrderedQty is validated for pack quantities</li>
<li>And isBundle=True flag is confirmed with pack constraints</li>
</ul>
</li>
<li><strong>Enhanced Atomic Processing</strong>
<ul>
<li>Given bundle components with pack quantities require allocation</li>
<li>When allocation processing begins</li>
<li>Then ALL bundle components with pack quantities are allocated together OR none</li>
<li>And enhanced rollback mechanism handles complex scenarios</li>
<li>And both bundle relationships and pack quantities are preserved</li>
</ul>
</li>
<li><strong>Advanced Financial Calculations</strong>
<ul>
<li>Given bundle discounts and pack-based pricing</li>
<li>When complex pricing calculations occur</li>
<li>Then bundle discounts are applied to pack pricing formula: (PackUnitPrice × PackOrderedQty × NumberOfPack) with bundle savings</li>
<li>And DECIMAL(18,4) precision is maintained for maximum complexity scenarios</li>
<li>And single COD payment covers entire bundle+pack amount</li>
<li>And component pricing distribution maintains both bundle and pack relationships</li>
</ul>
</li>
</ul>""",

        "UC-005": """<ul>
<li><strong>Customer Substitution Processing</strong>
<ul>
<li>Given a customer requires item substitution due to unavailability</li>
<li>When the 5-step substitution process executes</li>
<li>Then Slick contacts customer for substitution approval with price comparison</li>
<li>And OMS processes order detail editing based on customer approval</li>
<li>And customer pays new price with 20% increment limit validation</li>
<li>And PMP receives payment confirmation and updates OMS</li>
<li>And order progresses directly to Fulfilled status bypassing Release</li>
</ul>
</li>
<li><strong>Order Cancellation Management</strong>
<ul>
<li>Given a cancellation request via Slick REST API</li>
<li>When cancellation validation occurs</li>
<li>Then only orders with status ≤ 3000 (Released) can be canceled</li>
<li>And only full order cancellation is supported (no partial line items)</li>
<li>And order status updates to 9000 (Canceled) with immediate inventory release</li>
</ul>
</li>
<li><strong>Delivery Tracking Coordination</strong>
<ul>
<li>Given order fulfillment and delivery requirements</li>
<li>When delivery tracking activates</li>
<li>Then Slick updates order to 7000 (Fulfilled) with tracking information</li>
<li>And customer receives tracking details automatically</li>
<li>And customer confirms receipt through Grab mobile app</li>
<li>And Grab "Collected" status triggers PMP notification to OMS</li>
<li>And final status progresses to 7500 (Delivered) upon confirmation</li>
</ul>
</li>
</ul>""",

        "UC-006": """<ul>
<li><strong>Cancellation Request Processing</strong>
<ul>
<li>Given a customer requests order cancellation through Slick platform</li>
<li>When cancellation request is received via REST API</li>
<li>Then system validates order status is ≤ 3000 (Released threshold)</li>
<li>And full order cancellation only is supported (no partial line items)</li>
<li>And real-time processing provides immediate validation response</li>
</ul>
</li>
<li><strong>Status Validation Logic</strong>
<ul>
<li>Given order status validation requirements</li>
<li>When status check occurs</li>
<li>Then if status > 3000: return error response (cannot cancel)</li>
<li>And if status ≤ 3000: cancellation allowed, OMS responds success</li>
<li>And clear business logic with automatic validation rules applied</li>
</ul>
</li>
<li><strong>Cancellation Processing</strong>
<ul>
<li>Given approved cancellation request</li>
<li>When cancellation processing begins</li>
<li>Then order status updated to 9000 (Canceled)</li>
<li>And ALL allocated inventory released back to available stock</li>
<li>And inventory adjustments processed immediately</li>
<li>And cancellation timestamp and complete audit trail recorded</li>
</ul>
</li>
</ul>""",

        "UC-007": """<ul>
<li><strong>Delivery Status Updates</strong>
<ul>
<li>Given an order ready for delivery tracking</li>
<li>When Slick updates order to Fulfilled status</li>
<li>Then order marked as 7000 (Fulfilled) with tracking information</li>
<li>And customer receives tracking details automatically</li>
<li>And order officially handed off to delivery provider (Grab)</li>
</ul>
</li>
<li><strong>Customer Delivery Confirmation</strong>
<ul>
<li>Given customer receives delivered order</li>
<li>When customer confirms receipt through Grab mobile app</li>
<li>Then Grab marks order as "Collected" by customer</li>
<li>And PMP sends final delivery confirmation to OMS</li>
<li>And order status updated to 7500 (Delivered)</li>
</ul>
</li>
<li><strong>Event-Driven Coordination</strong>
<ul>
<li>Given real-time tracking requirements</li>
<li>When status updates occur across systems</li>
<li>Then event-driven processing ensures immediate status changes</li>
<li>And complete delivery tracking history is maintained</li>
<li>And customer notifications sent at each status progression</li>
<li>And integration coordination between Slick, Grab, PMP, and OMS</li>
</ul>
</li>
</ul>"""
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

def update_acceptance_criteria_html():
    """Update acceptance criteria for all user stories with proper HTML formatting"""
    print("🔧 Fixing Acceptance Criteria with Proper HTML Lists")
    print("=" * 60)
    
    # Load configuration
    org_url, pat, project = load_config()
    
    # Initialize Azure DevOps manager
    manager = AzureDevOpsManager(org_url, pat, project)
    
    # Load work item mapping
    mapping = load_work_item_mapping()
    
    # Load HTML formatted acceptance criteria
    html_criteria = create_html_acceptance_criteria()
    
    print(f"\n📋 Updating acceptance criteria with proper HTML formatting for {len(html_criteria)} user stories...")
    
    successful_updates = 0
    total_updates = len(html_criteria)
    
    for story_id, work_item_id in mapping["stories"].items():
        if story_id in html_criteria:
            print(f"\n🔄 Updating {story_id} (Work Item {work_item_id}) with proper HTML lists...")
            
            # Create update operation for acceptance criteria field only
            updates = [
                JsonPatchOperation(
                    op="replace", 
                    path="/fields/Microsoft.VSTS.Common.AcceptanceCriteria", 
                    value=html_criteria[story_id]
                )
            ]
            
            # Perform update
            try:
                success = manager.update_work_item(work_item_id, updates)
                
                if success:
                    print(f"✅ Successfully updated {story_id} with proper HTML formatting")
                    successful_updates += 1
                else:
                    print(f"❌ Failed to update {story_id}")
            except Exception as e:
                print(f"❌ Error updating {story_id}: {str(e)}")
        else:
            print(f"⚠️  No HTML criteria defined for {story_id}")
    
    # Summary
    print(f"\n📊 Update Summary:")
    print(f"   Successfully updated: {successful_updates}/{total_updates}")
    print(f"   Success rate: {(successful_updates/total_updates)*100:.1f}%")
    
    if successful_updates == total_updates:
        print("🎉 All acceptance criteria updated with proper HTML formatting!")
        print("\n🎯 Key improvements:")
        print("   • Proper HTML <ul> and <li> lists for clean Azure DevOps rendering")
        print("   • Structured bullet points with proper indentation")
        print("   • Clear Given/When/Then structure with bold headings")
        print("   • Technical requirements properly formatted")
        print("   • No more text wall - clean user story format")
    else:
        print("⚠️  Some updates failed. Please check the error messages above.")

if __name__ == "__main__":
    update_acceptance_criteria_html()