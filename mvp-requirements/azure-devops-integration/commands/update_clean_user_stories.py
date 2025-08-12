#!/usr/bin/env python3
"""
Update Azure DevOps User Stories with Clean Professional Format
Based on Product Owner specifications and Context7 best practices
"""

import sys
from pathlib import Path
import os

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from azure_devops_manager import AzureDevOpsManager
from azure.devops.v7_1.work_item_tracking.models import JsonPatchOperation


def get_clean_professional_user_stories():
    """Professional user stories with clean HTML formatting for Azure DevOps"""
    
    return {
        "UC-002": {
            "title": "UC-002: Bundle Order Processing",
            "description": """<p><strong>As a</strong> QC Small Format customer<br/>
<strong>I want to</strong> purchase promotional bundles containing multiple products<br/>
<strong>So that</strong> I get attractive product combinations with discounted pricing and atomic fulfillment</p>

<h3>Business Value</h3>
<ul>
<li>Enable promotional bundles to increase average order value by 25%</li>
<li>Provide customers convenient product combinations</li>
<li>Maintain atomic fulfillment to ensure bundle integrity</li>
<li>Support complex bundle pricing with discount distribution</li>
</ul>

<h3>Dependencies</h3>
<ul>
<li>All UC-001 dependencies (Kafka, T1, Slick, Grab, PMP)</li>
<li>Bundle product catalog and pricing engine</li>
<li>Enhanced atomic allocation system with rollback capability</li>
</ul>

<h3>Technical Notes</h3>
<ul>
<li>Extends UC-001 workflow with 5 additional bundle validation rules</li>
<li>Atomic allocation: all bundle components allocated together or none</li>
<li>Enhanced rollback mechanism for component allocation failures</li>
<li>Bundle discount distribution across all components</li>
</ul>""",
            
            "acceptance_criteria": """Given I am a QC Small Format customer placing a bundle order
When the order contains multiple products marked as isBundle=True
Then the system processes the bundle following enhanced workflow:

• Bundle Validation
  ◦ isBundle flag properly identified and validated
  ◦ BundleRefId unique bundle identifier validation passes
  ◦ PackUnitPrice bundle pricing validation (DECIMAL 18,4) completed
  ◦ ProductNameTH (Thai product name) validation passes
  ◦ ProductNameEN (English product name) validation passes

• Bundle Processing
  ◦ Bundle expands into individual product components
  ◦ Component relationships and dependencies established
  ◦ All components verified for atomic allocation availability

• Financial Calculations
  ◦ Bundle discount distributed across all components proportionally
  ◦ DECIMAL(18,4) precision maintained for complex bundle pricing
  ◦ Standard calculations (SubTotal, TotalCharge, OrderTotal) performed

• Atomic Allocation
  ◦ ALL bundle components allocated together (atomic operation)
  ◦ Enhanced rollback mechanism triggered if any component unavailable
  ◦ Bundle integrity maintained throughout allocation process
  ◦ Order status updated to Allocated only when complete

• Bundle Fulfillment
  ◦ Single release created containing ALL bundle components
  ◦ All components released together maintaining bundle integrity
  ◦ Complete bundle fulfilled as single atomic unit
  ◦ Customer receives complete bundle with all components

• System Integration
  ◦ Bundle tracking and delivery coordination through Slick/Grab
  ◦ Bundle components maintain relationship through entire workflow
  ◦ Status progression follows same hierarchy as normal orders"""
        },
        
        "UC-003": {
            "title": "UC-003: Pack Order Processing",
            "description": """<p><strong>As a</strong> QC Small Format customer<br/>
<strong>I want to</strong> order products with pack quantities and pack-based pricing<br/>
<strong>So that</strong> I can purchase products in bulk quantities with accurate pack calculations</p>

<h3>Business Value</h3>
<ul>
<li>Support bulk purchasing for customer convenience</li>
<li>Provide accurate pack-based pricing calculations</li>
<li>Enable improved inventory management for packaged goods</li>
<li>Maintain pricing precision for all pack quantity scenarios</li>
</ul>

<h3>Dependencies</h3>
<ul>
<li>All UC-001 dependencies (Kafka, T1, Slick, Grab, PMP)</li>
<li>Pack pricing configuration engine</li>
<li>Enhanced inventory management for pack quantities</li>
</ul>

<h3>Technical Notes</h3>
<ul>
<li>Extends UC-001 workflow with 3 additional pack validation rules</li>
<li>Pack-based pricing formula: PackUnitPrice × PackOrderedQty × NumberOfPack</li>
<li>Pack quantity coordination through fulfillment process</li>
<li>DECIMAL(18,4) precision for all pack calculations</li>
</ul>""",
            
            "acceptance_criteria": """Given I am a QC Small Format customer placing a pack order
When the order contains pack quantities (PackOrderedQty, NumberOfPack)
Then the system processes the pack order following enhanced workflow:

• Pack Validation
  ◦ PackUnitPrice validation ensures value > 0 with DECIMAL(18,4) precision
  ◦ PackOrderedQty validation ensures quantity > 0
  ◦ NumberOfPack validation ensures pack count > 0

• Pack Data Processing
  ◦ Standard data enrichment (ShortDescription, ImageURL) completed
  ◦ Pack quantity calculations and validation performed
  ◦ Pack dimension and weight calculations if applicable

• Pack-Based Financial Calculations
  ◦ Pack pricing formula applied: PackUnitPrice × PackOrderedQty × NumberOfPack
  ◦ DECIMAL(18,4) precision maintained throughout pack calculations
  ◦ Tax calculations applied to complete pack amounts
  ◦ Standard calculations (SubTotal, TotalCharge, OrderTotal) performed

• Pack Allocation
  ◦ Pack quantities properly allocated from inventory
  ◦ Pack availability verified at fulfillment location
  ◦ Pack quantity relationships maintained through allocation
  ◦ Order status updated to Allocated

• Pack Payment & Release
  ◦ COD payment for complete pack total amount processed
  ◦ Single release created with pack quantity information included
  ◦ Pack handling instructions included in release

• Pack Fulfillment
  ◦ Pack quantities coordinated through fulfillment process
  ◦ Pack handling instructions provided to fulfillment team
  ◦ Customer receives correct pack quantities as ordered
  ◦ Pack coordination maintained through delivery"""
        },
        
        "UC-004": {
            "title": "UC-004: Bundle with Pack Processing",
            "description": """<p><strong>As a</strong> QC Small Format customer<br/>
<strong>I want to</strong> purchase complex bundle orders that include pack quantities<br/>
<strong>So that</strong> I can access the most attractive promotional offers combining bundle discounts with pack-based products</p>

<h3>Business Value</h3>
<ul>
<li>Support most complex and valuable promotional offers</li>
<li>Combine bundle discounts with pack pricing advantages</li>
<li>Maximize customer order value opportunities</li>
<li>Maintain accuracy for complex pricing scenarios</li>
</ul>

<h3>Dependencies</h3>
<ul>
<li>All dependencies from UC-001, UC-002, and UC-003</li>
<li>Enhanced pricing engine for complex bundle+pack calculations</li>
<li>Advanced atomic allocation with enhanced rollback mechanisms</li>
</ul>

<h3>Technical Notes</h3>
<ul>
<li>Most complex scenario combining all validation rules (5 bundle + 1 pack)</li>
<li>Enhanced atomic allocation with complex rollback capability</li>
<li>Multi-level pricing calculations with bundle and pack integration</li>
<li>Complete bundle+pack coordination through fulfillment</li>
</ul>""",
            
            "acceptance_criteria": """Given I am a QC Small Format customer placing a bundle+pack order
When the order combines bundle products with pack quantities (most complex scenario)
Then the system processes following comprehensive workflow:

• Complex Validation
  ◦ All 5 bundle validation rules (BundleRefId, PackUnitPrice, NumberOfPack, ProductNameTH, ProductNameEN)
  ◦ Plus 1 pack validation rule (PackOrderedQty > 0)
  ◦ Combined validation logic for both bundle and pack requirements

• Enhanced Data Processing
  ◦ Bundle expansion into individual product components
  ◦ Pack quantity calculations for all bundle components
  ◦ Complex relationship mapping between bundle components and pack quantities

• Advanced Financial Calculations
  ◦ Bundle discount distribution across pack-based component pricing
  ◦ Complex formula: (PackUnitPrice × PackOrderedQty × NumberOfPack) with bundle discounts
  ◦ Multi-level pricing calculations with DECIMAL(18,4) precision
  ◦ Advanced discount allocation across complex product structures

• Enhanced Atomic Allocation
  ◦ ALL bundle components with pack quantities allocated together or NONE
  ◦ Enhanced rollback mechanism for complex bundle+pack scenarios
  ◦ Component+pack integrity maintained throughout process
  ◦ Most complex allocation scenario supported

• Complex Payment & Release
  ◦ COD payment for entire bundle+pack total amount
  ◦ Single release coordinating bundle components with pack quantities
  ◦ Complete bundle+pack coordination information included

• Comprehensive Fulfillment
  ◦ All bundle components with pack quantities fulfilled as atomic unit
  ◦ Complex coordination between bundle relationships and pack handling
  ◦ Customer receives complete bundle with all pack quantities correct
  ◦ Bundle+pack integrity maintained through entire delivery process"""
        },
        
        "UC-005": {
            "title": "UC-005: Substitution Processing",
            "description": """<p><strong>As a</strong> QC SMF operations manager<br/>
<strong>I want to</strong> process customer-approved product substitutions efficiently<br/>
<strong>So that</strong> I maintain high order fulfillment rates while ensuring customer satisfaction</p>

<h3>Business Value</h3>
<ul>
<li>Maintain customer satisfaction when products unavailable</li>
<li>Reduce order cancellations due to inventory issues</li>
<li>Provide flexible fulfillment options with customer choice</li>
<li>Support customer decision-making in substitution scenarios</li>
</ul>

<h3>Dependencies</h3>
<ul>
<li>Slick platform for customer communication and approval</li>
<li>PMP (Partner Management Platform) integration</li>
<li>Payment processing system for price adjustments</li>
<li>Enhanced order editing capabilities in OMS</li>
</ul>

<h3>Technical Notes</h3>
<ul>
<li>5-step customer-centric workflow with approval gates</li>
<li>Direct fulfillment bypass (bypasses release stage)</li>
<li>20% price increment limit with merchant override capability</li>
<li>Compatible with all order types (normal, bundle, pack, bundle+pack)</li>
</ul>""",
            
            "acceptance_criteria": """Given I am a QC SMF operations manager handling unavailable products
When a customer order requires product substitution
Then the system processes substitution following customer-centric workflow:

• Customer Confirmation
  ◦ Slick platform contacts customer for substitution approval
  ◦ Customer receives substitution offer with clear price comparison
  ◦ Formal confirmation process with contract approval mechanism
  ◦ Customer can approve, reject, or request alternative substitutions

• Order Modification
  ◦ OMS processes order detail editing based on customer approval
  ◦ Item details updated with substitute product information
  ◦ Promotional pricing recalculated for substitute items
  ◦ New order total calculated with substitution pricing

• Payment Processing
  ◦ Customer pays new price for modified order amount
  ◦ 20% increment limit enforced (merchant app can override)
  ◦ Payment methods support including COD processing
  ◦ Additional charges processed for price differences

• Payment Confirmation
  ◦ Payment success confirmation sent to PMP
  ◦ Partner Management Platform notified of successful payment
  ◦ Payment status updated across all integrated systems
  ◦ Integration synchronization between OMS and PMP

• System Synchronization
  ◦ PMP sends final substitution confirmation to OMS
  ◦ Order status updated to reflect completed substitution
  ◦ All systems synchronized with final substitution state
  ◦ Order bypasses release for direct fulfillment to Fulfilled status

• Audit and Tracking
  ◦ Complete substitution approval audit trail maintained
  ◦ Customer communication history preserved
  ◦ Substitution workflow compatible with all order types
  ◦ Full traceability from initial request to final confirmation"""
        },
        
        "UC-006": {
            "title": "UC-006: Order Cancellation",
            "description": """<p><strong>As a</strong> QC SMF operations manager<br/>
<strong>I want to</strong> process order cancellations efficiently before fulfillment begins<br/>
<strong>So that</strong> customers have flexibility while protecting operational efficiency</p>

<h3>Business Value</h3>
<ul>
<li>Provide customers flexibility for order management</li>
<li>Protect operational efficiency with clear cancellation boundaries</li>
<li>Reduce wasted fulfillment effort and operational costs</li>
<li>Maintain inventory accuracy with proper allocation release</li>
</ul>

<h3>Dependencies</h3>
<ul>
<li>Slick REST API integration for cancellation requests</li>
<li>Inventory management system for allocation release</li>
<li>Order status validation system</li>
</ul>

<h3>Technical Notes</h3>
<ul>
<li>Simple 3-step REST API workflow</li>
<li>Status validation with Released (3000) threshold</li>
<li>Full order cancellation only (no partial line items)</li>
<li>Immediate inventory release and system updates</li>
</ul>""",
            
            "acceptance_criteria": """Given I am a QC SMF operations manager processing cancellation requests
When a customer requests order cancellation via Slick platform
Then the system processes cancellation following validation workflow:

• API Integration
  ◦ Slick platform calls REST API with cancellation request
  ◦ Full order cancellation only (no partial line item cancellation)
  ◦ Standard REST API request/response pattern implemented
  ◦ Real-time processing with immediate validation response

• Status Validation
  ◦ System validates order status ≤ 3000 (Released threshold)
  ◦ If status > 3000: Return error response (cannot cancel)
  ◦ If status ≤ 3000: Cancellation allowed, OMS responds success
  ◦ Clear business logic with automatic validation rules

• Order Processing
  ◦ Order status updated to 9000 (Canceled)
  ◦ ALL allocated inventory released back to available stock
  ◦ Inventory adjustments processed immediately
  ◦ Cancellation timestamp and complete audit trail recorded

• System Response
  ◦ Success response provided when cancellation allowed
  ◦ Clear error messages when cancellation not permitted
  ◦ Current order status communicated in response
  ◦ Integration compatibility with all order types

• Audit and Compliance
  ◦ Complete cancellation event logging maintained
  ◦ Inventory release transactions recorded
  ◦ Customer notification through Slick platform
  ◦ Cancellation workflow compatible across all order scenarios"""
        },
        
        "UC-007": {
            "title": "UC-007: Delivery Tracking",
            "description": """<p><strong>As a</strong> QC Small Format customer<br/>
<strong>I want to</strong> track my delivery progress with real-time updates and confirmation<br/>
<strong>So that</strong> I have complete delivery transparency and can monitor receipt</p>

<h3>Business Value</h3>
<ul>
<li>Improve customer experience through delivery transparency</li>
<li>Reduce customer service inquiries about delivery status by 50%</li>
<li>Build customer confidence in delivery service reliability</li>
<li>Enable customer-confirmed delivery completion</li>
</ul>

<h3>Dependencies</h3>
<ul>
<li>Slick platform for fulfilled status and tracking information</li>
<li>Grab delivery system for customer confirmation</li>
<li>PMP coordination for final delivery confirmation</li>
<li>Real-time status update capabilities across all systems</li>
</ul>

<h3>Technical Notes</h3>
<ul>
<li>Simple 2-step event-driven workflow</li>
<li>Real-time tracking and status updates</li>
<li>Customer confirmation through Grab mobile app</li>
<li>Final status progression: Fulfilled (7000) → Delivered (7500)</li>
</ul>""",
            
            "acceptance_criteria": """Given I am a QC Small Format customer with an order ready for delivery
When my order reaches fulfilled status and needs delivery tracking
Then the system coordinates tracking following event-driven workflow:

• Fulfilled Status Update
  ◦ Slick updates order to 7000 (Fulfilled) with tracking information
  ◦ Customer receives tracking details when order fulfilled
  ◦ Order officially handed off to delivery provider (Grab)
  ◦ Tracking information provided to customer automatically

• Customer Delivery Confirmation
  ◦ Customer confirms receipt through Grab mobile app
  ◦ Grab marks order as "Collected" by customer
  ◦ PMP sends final delivery confirmation to OMS
  ◦ Order status updated to 7500 (Delivered)

• Tracking Integration
  ◦ Real-time status updates across all integrated systems
  ◦ Event-driven processing for immediate status changes
  ◦ Complete delivery tracking history maintained
  ◦ Customer notification at each status progression

• System Coordination
  ◦ Slick platform integration for fulfilled status and tracking
  ◦ Grab delivery system integration for customer confirmation
  ◦ PMP coordination for final delivery confirmation management
  ◦ Order management system status updates

• Customer Experience
  ◦ Clear delivery status visibility throughout process
  ◦ Mobile app integration for easy confirmation
  ◦ Tracking information accessible and understandable
  ◦ Delivery transparency reduces support inquiries significantly"""
        }
    }


def main():
    """Update user stories with clean professional format"""
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    org_url = os.getenv('AZURE_DEVOPS_ORG_URL')
    pat = os.getenv('AZURE_DEVOPS_PAT')  
    project = os.getenv('AZURE_DEVOPS_PROJECT')
    
    if not all([org_url, pat, project]):
        print("❌ Error: Missing required environment variables")
        print("Please ensure AZURE_DEVOPS_ORG_URL, AZURE_DEVOPS_PAT, and AZURE_DEVOPS_PROJECT are set")
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
    try:
        manager = AzureDevOpsManager(org_url, pat, project)
        print("🔗 Connected to Azure DevOps successfully")
    except Exception as e:
        print(f"❌ Error connecting to Azure DevOps: {str(e)}")
        return
    
    # Get clean user stories
    user_stories = get_clean_professional_user_stories()
    
    print("\n🎯 Updating Azure DevOps User Stories with Professional Format")
    print("=" * 70)
    print("📋 Based on Product Owner specifications and Context7 best practices")
    print("🎨 Clean HTML formatting optimized for Azure DevOps rendering")
    
    success_count = 0
    
    for uc_id, work_item_id in work_items.items():
        if uc_id in user_stories:
            story = user_stories[uc_id]
            
            print(f"\n🔧 Updating {uc_id} (Work Item {work_item_id})...")
            print(f"   Title: {story['title']}")
            
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
                    print(f"   ✅ Successfully updated {uc_id}")
                    success_count += 1
                else:
                    print(f"   ❌ Failed to update {uc_id}")
            except Exception as e:
                print(f"   ❌ Error updating {uc_id}: {str(e)}")
        else:
            print(f"⚠️ {uc_id} not found in user story definitions")
    
    print("\n" + "=" * 70)
    print(f"🎯 Professional Format Update Complete!")
    print(f"📊 Successfully updated {success_count}/{len(work_items)} user stories")
    
    if success_count == len(work_items):
        print("🎉 All user stories updated successfully!")
        print("✨ Format: Professional user stories with clean HTML rendering")
        print("📱 Each work item now displays with structured sections:")
        print("   • Clear As a/I want/So that user story format")
        print("   • Business Value section with bullet points")
        print("   • Dependencies clearly listed")
        print("   • Structured Acceptance Criteria with Given/When/Then format")
        print("   • Professional HTML formatting optimized for Azure DevOps")
    else:
        print(f"⚠️ {len(work_items) - success_count} user stories had issues")
        print("Please check the error messages above and retry if needed")


if __name__ == "__main__":
    main()