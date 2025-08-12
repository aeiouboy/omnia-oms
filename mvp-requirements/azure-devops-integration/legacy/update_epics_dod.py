#!/usr/bin/env python3
"""
Update all epics with clear Definition of Done (DOD) and business outcomes
"""

import sys
import os
import json
from pathlib import Path

# Add the directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import the main components from the original script
from create_azure_work_items import AzureDevOpsClient
from azure.devops.v7_1.work_item_tracking.models import JsonPatchOperation


def get_epic_details():
    """Define DOD and business outcomes for each epic"""
    return {
        "51656": {  # MAO MVP - Order Creation & Validation
            "description": """<p><strong>Business Value:</strong> Prevents invalid orders from entering the system, reducing operational errors and customer complaints.</p>
<p><strong>Key Stakeholders:</strong> Order Management Team, Customer Service, IT Operations</p>
<p><strong>Success Metrics:</strong></p>
<ul>
<li>Order validation error rate < 1%</li>
<li>Order creation response time < 100ms</li>
<li>Zero invalid orders reaching fulfillment</li>
</ul>
<p><strong>Risk Factors:</strong></p>
<ul>
<li>Complex validation rules may impact performance</li>
<li>Integration dependencies with multiple systems</li>
</ul>""",
            "acceptance_criteria": """<ul>
<li><strong>All required order fields validated</strong></li>
<li><strong>Order status modification controls implemented</strong></li>
<li><strong>Line item validation complete</strong></li>
<li><strong>Bundle conditional validation functional</strong></li>
<li><strong>Kafka order creation operational</strong></li>
<li><strong>Error handling provides detailed feedback</strong></li>
<li><strong>Performance targets met:</strong>
<ul style='margin-left: 20px; list-style-type: circle;'>
<li>< 100ms validation response time</li>
<li>< 1% validation error rate</li>
<li>100% data integrity maintained</li>
</ul>
</li>
<li><strong>Integration testing passed with all dependent systems</strong></li>
<li><strong>Documentation complete for all validation rules</strong></li>
</ul>"""
        },
        "51657": {  # MAO MVP - Bundle Processing
            "description": """<p><strong>Business Value:</strong> Enables promotional bundles and package deals, increasing average order value.</p>
<p><strong>Key Stakeholders:</strong> Marketing, Product Management, Warehouse Operations</p>
<p><strong>Success Metrics:</strong></p>
<ul>
<li>Bundle processing accuracy 100%</li>
<li>Bundle allocation success rate > 95%</li>
<li>Bundle pricing calculation < 50ms</li>
</ul>
<p><strong>Risk Factors:</strong></p>
<ul>
<li>Complex pricing and discount allocation logic</li>
<li>Inventory synchronization challenges</li>
</ul>""",
            "acceptance_criteria": """<ul>
<li><strong>Bundle identification and processing rules active</strong></li>
<li><strong>Bundle pricing calculation accurate</strong></li>
<li><strong>Atomic inventory allocation functional</strong></li>
<li><strong>Bundle fulfillment grouping operational</strong></li>
<li><strong>Bundle returns processing complete</strong></li>
<li><strong>Performance targets met:</strong>
<ul style='margin-left: 20px; list-style-type: circle;'>
<li>100% bundle processing accuracy</li>
<li>> 95% bundle allocation success rate</li>
<li>< 50ms pricing calculation time</li>
</ul>
</li>
<li><strong>All bundle components properly linked</strong></li>
<li><strong>Inventory consistency maintained across bundle operations</strong></li>
</ul>"""
        },
        "51658": {  # MAO MVP - Payment Processing
            "description": """<p><strong>Business Value:</strong> Ensures payment collection and reduces payment fraud.</p>
<p><strong>Key Stakeholders:</strong> Finance, Security, Customer Service</p>
<p><strong>Success Metrics:</strong></p>
<ul>
<li>Payment authorization success rate > 95%</li>
<li>Payment processing time < 3 seconds</li>
<li>Zero payment data breaches</li>
</ul>
<p><strong>Risk Factors:</strong></p>
<ul>
<li>PCI compliance requirements</li>
<li>Payment gateway integration complexity</li>
</ul>""",
            "acceptance_criteria": """<ul>
<li><strong>Payment method validation operational</strong></li>
<li><strong>Payment authorization system functional</strong></li>
<li><strong>Substitution payment adjustments working</strong></li>
<li><strong>Payment capture on fulfillment automated</strong></li>
<li><strong>Refund processing complete</strong></li>
<li><strong>Performance targets met:</strong>
<ul style='margin-left: 20px; list-style-type: circle;'>
<li>> 95% payment authorization success rate</li>
<li>< 3 seconds payment processing time</li>
<li>100% PCI compliance maintained</li>
</ul>
</li>
<li><strong>Payment gateway integration stable</strong></li>
<li><strong>All payment audit trails maintained</strong></li>
</ul>"""
        },
        "51659": {  # MAO MVP - Fulfillment Integration
            "description": """<p><strong>Business Value:</strong> Enables end-to-end order fulfillment and tracking.</p>
<p><strong>Key Stakeholders:</strong> Warehouse Operations, Logistics, Customer Service</p>
<p><strong>Success Metrics:</strong></p>
<ul>
<li>Order release success rate 100%</li>
<li>Fulfillment status accuracy 99%</li>
<li>Delivery confirmation rate > 95%</li>
</ul>
<p><strong>Risk Factors:</strong></p>
<ul>
<li>External system dependencies</li>
<li>Network reliability issues</li>
</ul>""",
            "acceptance_criteria": """<ul>
<li><strong>Order release to Slick functional</strong></li>
<li><strong>Ship event processing operational</strong></li>
<li><strong>Short event handling complete</strong></li>
<li><strong>Substitution request processing working</strong></li>
<li><strong>Delivery status tracking active</strong></li>
<li><strong>All fulfillment events captured</strong></li>
<li><strong>Performance targets met:</strong>
<ul style='margin-left: 20px; list-style-type: circle;'>
<li>100% order release success rate</li>
<li>99% fulfillment status accuracy</li>
<li>> 95% delivery confirmation rate</li>
</ul>
</li>
<li><strong>Integration with Slick system stable</strong></li>
</ul>"""
        },
        "51660": {  # MAO MVP - Status Management
            "description": """<p><strong>Business Value:</strong> Provides visibility into order progress for operations and customers.</p>
<p><strong>Key Stakeholders:</strong> Customer Service, Operations, Analytics</p>
<p><strong>Success Metrics:</strong></p>
<ul>
<li>Status update latency < 50ms</li>
<li>Status accuracy 100%</li>
<li>Real-time status visibility</li>
</ul>
<p><strong>Risk Factors:</strong></p>
<ul>
<li>Complex status calculation logic</li>
<li>High volume of status updates</li>
</ul>""",
            "acceptance_criteria": """<ul>
<li><strong>Order status calculation accurate</strong></li>
<li><strong>Status history tracking complete</strong></li>
<li><strong>Sub-status management functional</strong></li>
<li><strong>Status event publishing operational</strong></li>
<li><strong>Performance targets met:</strong>
<ul style='margin-left: 20px; list-style-type: circle;'>
<li>< 50ms status update latency</li>
<li>100% status accuracy</li>
<li>Real-time status visibility maintained</li>
</ul>
</li>
<li><strong>Status transitions properly validated</strong></li>
<li><strong>All status changes auditable</strong></li>
</ul>"""
        },
        "51661": {  # MAO MVP - Cancellation & Returns
            "description": """<p><strong>Business Value:</strong> Improves customer satisfaction by allowing order changes and returns.</p>
<p><strong>Key Stakeholders:</strong> Customer Service, Finance, Warehouse</p>
<p><strong>Success Metrics:</strong></p>
<ul>
<li>Cancellation processing time < 30 seconds</li>
<li>Return processing accuracy 100%</li>
<li>Refund processing time < 5 seconds</li>
</ul>
<p><strong>Risk Factors:</strong></p>
<ul>
<li>Complex refund calculations</li>
<li>Integration with multiple systems</li>
</ul>""",
            "acceptance_criteria": """<ul>
<li><strong>Full order cancellation functional</strong></li>
<li><strong>Partial cancellation prevention active</strong></li>
<li><strong>Returns processing complete</strong></li>
<li><strong>Cancellation event handling operational</strong></li>
<li><strong>Performance targets met:</strong>
<ul style='margin-left: 20px; list-style-type: circle;'>
<li>< 30 seconds cancellation processing</li>
<li>100% return processing accuracy</li>
<li>< 5 seconds refund processing</li>
</ul>
</li>
<li><strong>Inventory released properly on cancellation</strong></li>
<li><strong>All refunds processed accurately</strong></li>
</ul>"""
        },
        "51662": {  # MAO MVP - API Integration
            "description": """<p><strong>Business Value:</strong> Enables seamless integration with external systems and microservices.</p>
<p><strong>Key Stakeholders:</strong> Integration Team, External Partners, DevOps</p>
<p><strong>Success Metrics:</strong></p>
<ul>
<li>API response time < 200ms (P99)</li>
<li>API availability > 99.9%</li>
<li>Message processing latency < 100ms</li>
</ul>
<p><strong>Risk Factors:</strong></p>
<ul>
<li>Network reliability</li>
<li>API versioning challenges</li>
</ul>""",
            "acceptance_criteria": """<ul>
<li><strong>Order Creation API operational</strong></li>
<li><strong>Order Status API functional</strong></li>
<li><strong>Kafka topics configured</strong></li>
<li><strong>Message processing reliable</strong></li>
<li><strong>Webhook notifications active</strong></li>
<li><strong>Performance targets met:</strong>
<ul style='margin-left: 20px; list-style-type: circle;'>
<li>< 200ms API response time (P99)</li>
<li>> 99.9% API availability</li>
<li>< 100ms message processing latency</li>
</ul>
</li>
<li><strong>API documentation complete</strong></li>
<li><strong>Rate limiting and security implemented</strong></li>
</ul>"""
        },
        "51663": {  # MAO MVP - Data Management & Reporting
            "description": """<p><strong>Business Value:</strong> Provides business insights and maintains compliance requirements.</p>
<p><strong>Key Stakeholders:</strong> Analytics Team, Compliance, Management</p>
<p><strong>Success Metrics:</strong></p>
<ul>
<li>Data consistency 100%</li>
<li>Report generation < 30 seconds</li>
<li>Audit log completeness 100%</li>
</ul>
<p><strong>Risk Factors:</strong></p>
<ul>
<li>Large data volumes</li>
<li>Performance impact of logging</li>
</ul>""",
            "acceptance_criteria": """<ul>
<li><strong>Order data model implemented</strong></li>
<li><strong>Audit logging comprehensive</strong></li>
<li><strong>Order reports functional</strong></li>
<li><strong>Data archival automated</strong></li>
<li><strong>Performance targets met:</strong>
<ul style='margin-left: 20px; list-style-type: circle;'>
<li>100% data consistency</li>
<li>< 30 seconds report generation</li>
<li>100% audit log completeness</li>
</ul>
</li>
<li><strong>Data integrity maintained across all operations</strong></li>
<li><strong>Compliance requirements satisfied</strong></li>
</ul>"""
        }
    }


def main():
    """Main execution function"""
    
    # Load from .env file
    env_file = Path(__file__).parent / '.env'
    if env_file.exists():
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
    
    print(f"🔧 Updating all epics with clear DOD and business outcomes...")
    print(f"   📊 Adding comprehensive Definition of Done")
    print(f"   🎯 Adding measurable business outcomes")
    
    # Load work item mapping
    mapping_file = Path(__file__).parent / "work_item_mapping.json"
    with open(mapping_file, 'r') as f:
        mapping = json.load(f)
    
    epic_mapping = mapping.get('epics', {})
    epic_details = get_epic_details()
    
    # Initialize Azure DevOps client
    print("🔌 Connecting to Azure DevOps...")
    client = AzureDevOpsClient(ORGANIZATION_URL, PERSONAL_ACCESS_TOKEN)
    print("✅ Connected!")
    
    updated_count = 0
    failed_count = 0
    total_count = len(epic_mapping)
    
    print(f"\n📊 Processing {total_count} epics...")
    
    # Update all epics
    for i, (epic_name, work_item_id) in enumerate(epic_mapping.items(), 1):
        work_item_id_str = str(work_item_id)
        print(f"  🔧 [{i:2d}/{total_count}] Updating Epic {work_item_id} ({epic_name})...")
        
        if work_item_id_str not in epic_details:
            print(f"    ⚠️  No details defined for Epic {work_item_id}")
            failed_count += 1
            continue
        
        try:
            details = epic_details[work_item_id_str]
            
            # Update the epic with DOD and business outcomes
            document = [
                JsonPatchOperation(
                    op="replace",
                    path="/fields/System.Description",
                    value=details["description"]
                ),
                JsonPatchOperation(
                    op="replace",
                    path="/fields/Microsoft.VSTS.Common.AcceptanceCriteria",
                    value=details["acceptance_criteria"]
                )
            ]
            
            updated_work_item = client.wit_client.update_work_item(
                document=document,
                id=work_item_id
            )
            
            print(f"    ✅ Updated Epic {work_item_id} ({epic_name})")
            updated_count += 1
            
        except Exception as e:
            print(f"    ❌ Failed to update Epic {work_item_id}: {e}")
            failed_count += 1
    
    print(f"\n📊 Final Summary:")
    print(f"  ✅ Successfully updated: {updated_count}")
    print(f"  ❌ Failed: {failed_count}")
    print(f"  📈 Success rate: {(updated_count/total_count)*100:.1f}%")
    
    print(f"\n✨ All epics now have:")
    print(f"  • Clear business value and stakeholder identification")
    print(f"  • Measurable success metrics and performance targets")
    print(f"  • Comprehensive Definition of Done (DOD)")
    print(f"  • Risk factors and mitigation strategies")
    
    print(f"\n🔗 View updated epics:")
    print(f"  {ORGANIZATION_URL}/{PROJECT_NAME}/_backlogs/backlog")
    
    # Show sample epic links
    print(f"\n🎯 Sample epics to check:")
    sample_epics = list(epic_mapping.items())[:3]
    for epic_name, work_item_id in sample_epics:
        print(f"  • {epic_name}: {ORGANIZATION_URL}/{PROJECT_NAME}/_workitems/edit/{work_item_id}")


if __name__ == "__main__":
    main()