#!/usr/bin/env python3
"""
Find Duplicate Work Items - Identify and list duplicate stories with same IDs but different work item numbers
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from azure_devops_manager import AzureDevOpsManager, ConfigManager


def main():
    """Find and list all duplicate work items"""
    
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
    
    # Load our current work item mapping
    mapping = ConfigManager.load_work_item_mapping(config_dir)
    current_story_ids = set(mapping.get('stories', {}).keys())
    current_work_items = set(mapping.get('stories', {}).values())
    
    print(f"📋 Our current work items: {len(current_work_items)} stories")
    print(f"🎯 Story IDs: {sorted(current_story_ids)}")
    print(f"📊 Work item range: {min(current_work_items)}-{max(current_work_items)}")
    
    # Search for duplicate stories using Azure DevOps query
    # We'll search for work items with same story ID patterns but different work item numbers
    
    duplicate_candidates = []
    
    # Check for each story ID pattern
    for story_id in current_story_ids:
        try:
            # Use work item tracking client to search for items with same title pattern
            query = f"SELECT [System.Id], [System.Title], [System.State], [System.CreatedDate] FROM WorkItems WHERE [System.TeamProject] = '{project}' AND [System.WorkItemType] = 'User Story' AND [System.Title] CONTAINS '{story_id}:'"
            
            query_result = manager.wit_client.query_by_wiql(
                {"query": query}
            )
            
            if query_result.work_items and len(query_result.work_items) > 1:
                print(f"\n🔍 Found {len(query_result.work_items)} work items for {story_id}:")
                
                work_item_ids = [item.id for item in query_result.work_items]
                work_items = manager.wit_client.get_work_items(work_item_ids)
                
                for work_item in work_items:
                    is_current = work_item.id in current_work_items
                    status = "✅ CURRENT" if is_current else "❌ DUPLICATE"
                    
                    print(f"  {status} - ID: {work_item.id}, Title: {work_item.fields['System.Title']}")
                    print(f"    Created: {work_item.fields['System.CreatedDate']}")
                    
                    if not is_current:
                        duplicate_candidates.append({
                            'id': work_item.id,
                            'title': work_item.fields['System.Title'],
                            'story_id': story_id,
                            'created': work_item.fields['System.CreatedDate']
                        })
        
        except Exception as e:
            print(f"⚠️  Error searching for {story_id}: {e}")
            continue
    
    # Summary
    print(f"\n📊 Duplicate Analysis Summary:")
    print(f"  ✅ Current work items: {len(current_work_items)}")
    print(f"  ❌ Duplicate candidates: {len(duplicate_candidates)}")
    
    if duplicate_candidates:
        print(f"\n🗑️  Recommended for deletion:")
        for dup in sorted(duplicate_candidates, key=lambda x: x['id']):
            print(f"  - {dup['id']}: {dup['title']} (Created: {dup['created']})")
    
    return duplicate_candidates


if __name__ == "__main__":
    main()