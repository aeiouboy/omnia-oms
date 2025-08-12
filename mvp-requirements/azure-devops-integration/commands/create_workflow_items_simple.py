#!/usr/bin/env python3
"""
Create Workflow Work Items - Simple version with text-based acceptance criteria
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from azure_devops_manager import AzureDevOpsManager, ConfigManager, Epic, UserStory


def main():
    """Create all workflow epics and user stories"""
    
    print("🚀 Creating QC SMF workflow work items...")
    
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
    
    # Define the main epic
    epic = Epic(
        title="QC Small Format Order Management System",
        overview="""Implement complete Manhattan Active® Omni (MAO) integration for QC Small Format convenience stores, supporting all order types, operational processes, and delivery workflows to handle 300+ daily customers across 25+ stores with comprehensive order management capabilities.""",
        business_value="""
        <h3>Primary Goals</h3>
        <ul>
            <li><strong>Complete Order Coverage:</strong> Support all QC SMF order scenarios (Normal, Bundle, Pack, Bundle+Pack)</li>
            <li><strong>Operational Excellence:</strong> Full order lifecycle management from creation to delivery</li>
            <li><strong>System Integration:</strong> Seamless integration with Kafka, Slick, PMP, Grab, and T1 fulfillment centers</li>
            <li><strong>Customer Experience:</strong> Efficient order processing with real-time tracking and delivery confirmation</li>
        </ul>
        
        <h3>Success Metrics</h3>
        <ul>
            <li><strong>Technical Performance:</strong> 99.9% system uptime, &lt;200ms API response time</li>
            <li><strong>Business Metrics:</strong> &gt;99% order success rate, &gt;90% same-day delivery</li>
            <li><strong>Quality Standards:</strong> &gt;90% automated test coverage, 100% financial accuracy</li>
            <li><strong>Customer Satisfaction:</strong> &lt;1% order cancellation rate, +25% average order value from bundles</li>
        </ul>
        """,
        stakeholders="Product Manager, Solution Architect, QC SMF Operations Team, T1 Fulfillment Team",
        success_metrics=[
            "99.9% system uptime, <200ms API response time",
            ">99% order success rate, >90% same-day delivery", 
            ">90% automated test coverage, 100% financial accuracy",
            "<1% order cancellation rate, +25% average order value from bundles"
        ],
        risk_factors=[
            "Integration complexity with multiple external systems",
            "Financial calculation accuracy requirements",
            "Performance requirements for 300+ orders/day per store",
            "Atomic allocation requirements for bundle processing"
        ]
    )
    
    # Define all user stories with simple acceptance criteria
    stories = [
        UserStory(
            story_id="UC-001",
            title="Normal Order Processing - System Workflow",
            epic="QC Small Format Order Management System",
            priority="P0",
            story_points=13,
            as_a="QC Small Format store manager",
            i_want="to process normal individual product orders through Manhattan Active Omni",
            so_that="customers can purchase individual products with standard pricing and delivery",
            acceptance_criteria_structured=[
                {
                    "given": "Order received from Kafka Order Create topic",
                    "when_then": [
                        "System validates OrderID, ShipFromLocationID consistency, IsForceAllocation=True",
                        "Performs data enrichment for ShortDescription and ImageURL",
                        "Calculates SubTotal, TotalCharge, OrderTotal, TotalDiscount, TotalTaxes",
                        "Performs force allocation (status 2000) and COD payment (status 5000)",
                        "Creates single release (status 3000) and processes to fulfilled (7000) and delivered (7500)"
                    ]
                }
            ],
            dependencies="Kafka Order Create topic, T1 Fulfillment Center integration, Slick REST API",
            technical_notes="9-step workflow: Kafka → Validation → Allocation → Payment → Release → Delivery. Uses IsForceAllocation=True, COD payment only, single release policy, DECIMAL(18,4) financial precision."
        ),
        
        UserStory(
            story_id="UC-002", 
            title="Bundle Order Processing - System Workflow",
            epic="QC Small Format Order Management System",
            priority="P0",
            story_points=8,
            as_a="QC Small Format store manager",
            i_want="to process bundle orders with multiple products sold as a unit",
            so_that="customers can purchase product bundles with special pricing and atomic allocation",
            acceptance_criteria_structured=[
                {
                    "given": "Bundle order received with isBundle=True",
                    "when_then": [
                        "System validates standard rules plus 5 bundle-specific rules",
                        "Validates BundleRefId, PackUnitPrice, NumberOfPack, ProductNameTH, ProductNameEN",
                        "Expands bundle into component products with data enrichment",
                        "Performs atomic allocation (all components or none) with rollback capability",
                        "Applies bundle discount distribution across components"
                    ]
                }
            ],
            dependencies="UC-001 foundation, Bundle product catalog, Component pricing rules",
            technical_notes="Extends UC-001 with bundle-specific validation (5 additional rules), atomic allocation, component expansion, and discount distribution. Requires rollback mechanism for failed atomic allocation."
        ),
        
        UserStory(
            story_id="UC-003",
            title="Normal Order with Pack Processing - System Workflow", 
            epic="QC Small Format Order Management System",
            priority="P0",
            story_points=5,
            as_a="QC Small Format store manager",
            i_want="to process normal orders with pack quantities and pack-based pricing",
            so_that="customers can purchase products in pack quantities with appropriate pricing calculations",
            acceptance_criteria_structured=[
                {
                    "given": "Pack order received",
                    "when_then": [
                        "System validates 3 pack rules: PackUnitPrice, PackOrderedQty, NumberOfPack",
                        "Calculates total using PackUnitPrice × PackOrderedQty × NumberOfPack formula",
                        "Applies pack-specific pricing logic with DECIMAL(18,4) precision",
                        "Processes through standard workflow with pack quantity management"
                    ]
                }
            ],
            dependencies="UC-001 foundation, Pack pricing configuration",
            technical_notes="Extends UC-001 with pack-specific logic: 3 additional validation rules, pack-based pricing formula, pack quantity management."
        ),
        
        UserStory(
            story_id="UC-004",
            title="Bundle with Pack Processing - System Workflow",
            epic="QC Small Format Order Management System", 
            priority="P0",
            story_points=8,
            as_a="QC Small Format store manager",
            i_want="to process complex bundle orders that include pack quantities",
            so_that="customers can purchase bundled products in pack quantities with combined pricing logic",
            acceptance_criteria_structured=[
                {
                    "given": "Bundle+Pack order received (most complex scenario)",
                    "when_then": [
                        "System validates all bundle rules (5) plus pack rules (1) = 6 additional validations",
                        "Performs atomic allocation for all bundle components in pack quantities",
                        "Applies bundle discounts to pack-based pricing calculations",
                        "Maintains financial accuracy across all component calculations with rollback support"
                    ]
                }
            ],
            dependencies="UC-001, UC-002, UC-003 foundations, Complex pricing engine",
            technical_notes="Most complex scenario combining bundle logic (UC-002) with pack logic (UC-003). Requires atomic allocation, advanced financial calculations, and rollback mechanisms."
        ),
        
        UserStory(
            story_id="UC-005",
            title="Substitution Processing Workflow",
            epic="QC Small Format Order Management System",
            priority="P0", 
            story_points=5,
            as_a="QC Small Format store manager",
            i_want="to process product substitutions with customer confirmation",
            so_that="unavailable products can be replaced while maintaining customer satisfaction",
            acceptance_criteria_structured=[
                {
                    "given": "Product substitution required",
                    "when_then": [
                        "Slick platform requests customer confirmation for substitution",
                        "System enforces 20% price increment limit (unless merchant app override)",
                        "OMS edits order with substituted product upon customer approval",
                        "Processes payment adjustment if required and updates PMP",
                        "Bypasses release step for direct fulfillment processing"
                    ]
                }
            ],
            dependencies="Slick customer communication, PMP integration, Pricing validation rules",
            technical_notes="5-step customer-centric process: Slick Customer Confirmation → OMS Edit → Payment → PMP Update → Final Sync. Bypasses release step for direct fulfillment."
        ),
        
        UserStory(
            story_id="UC-006",
            title="Order Cancellation Workflow",
            epic="QC Small Format Order Management System",
            priority="P0",
            story_points=3, 
            as_a="QC Small Format store manager",
            i_want="to cancel orders before they are released for fulfillment",
            so_that="customers can cancel unwanted orders within the allowed timeframe",
            acceptance_criteria_structured=[
                {
                    "given": "Order cancellation requested via Slick API",
                    "when_then": [
                        "System validates order status is ≤3000 (Released)",
                        "Rejects cancellation if status is beyond Released",
                        "Updates order status to 9000 (Canceled) when validation passes",
                        "Processes any required refunds or payment reversals"
                    ]
                }
            ],
            dependencies="Slick REST API, Status validation rules, Payment reversal system",
            technical_notes="3-step REST API process: Slick API Call → Status Validation (≤3000) → OMS Update (9000). Full order cancellation only."
        ),
        
        UserStory(
            story_id="UC-007",
            title="Delivery Tracking Workflow", 
            epic="QC Small Format Order Management System",
            priority="P0",
            story_points=6,
            as_a="QC Small Format store manager",
            i_want="to track order delivery status with customer confirmation",
            so_that="customers receive real-time delivery updates and confirmation",
            acceptance_criteria_structured=[
                {
                    "given": "Order delivery tracking initiated",
                    "when_then": [
                        "Slick receives fulfilled update when order status reaches 7000",
                        "Customer confirms receipt via Grab app upon delivery completion",
                        "Confirmation flows through Grab → PMP → OMS chain",
                        "Order status updates to 7500 (Delivered) and delivery workflow completes"
                    ]
                }
            ],
            dependencies="Slick platform, Grab delivery integration, PMP coordination",
            technical_notes="2-step event-driven process: Slick Fulfilled Update → Customer Receipt Confirmation (Grab → PMP → OMS). Real-time tracking with customer confirmation."
        )
    ]
    
    print(f"\n📋 Creating 1 epic and {len(stories)} user stories...")
    
    # Create epic first
    print(f"\n🎯 Creating epic: {epic.title}")
    epic_id = manager.create_epic(epic)
    
    # Create all user stories and link to epic
    story_ids = {}
    for story in stories:
        print(f"\n📖 Creating story: {story.story_id} - {story.title}")
        story_id = manager.create_user_story(story, epic_id)
        story_ids[story.story_id] = story_id
    
    # Update work item mapping
    mapping = ConfigManager.load_work_item_mapping(config_dir)
    
    # Add new epic
    if 'epics' not in mapping:
        mapping['epics'] = {}
    mapping['epics'][epic.title] = epic_id
    
    # Add new stories
    if 'stories' not in mapping:
        mapping['stories'] = {}
    mapping['stories'].update(story_ids)
    
    # Update summary
    if 'summary' not in mapping:
        mapping['summary'] = {}
    mapping['summary']['total_epics_created'] = len(mapping['epics'])
    mapping['summary']['total_stories_created'] = len(mapping['stories'])
    mapping['summary']['workflow_items_created'] = len(story_ids)
    
    # Save updated mapping
    ConfigManager.save_work_item_mapping(config_dir, mapping)
    
    # Final summary
    print(f"\n🎉 Successfully created all workflow work items!")
    print(f"  ✅ Created 1 epic: {epic.title} (ID: {epic_id})")
    print(f"  ✅ Created {len(stories)} user stories")
    print(f"  📋 Story IDs: {list(story_ids.values())}")
    print(f"🔗 View project at: {org_url}/{project}/_backlogs/backlog/")
    

if __name__ == "__main__":
    main()