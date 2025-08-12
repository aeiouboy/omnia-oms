#!/usr/bin/env python3
"""
Comprehensive Story Check - Use Playwright MCP to visually inspect all 39 stories
and identify any remaining corruption or formatting issues
"""

import sys
import time
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from azure_devops_manager import AzureDevOpsManager, ConfigManager


def main():
    """Check all stories using visual inspection to find remaining issues"""
    
    # Load configuration
    config_dir = Path(__file__).parent.parent
    try:
        org_url, project, pat = ConfigManager.load_config(config_dir)
        print(f"🔧 Configuration loaded for project: {project}")
    except ValueError as e:
        print(f"❌ {e}")
        return
    
    # Load our current work item mapping
    mapping = ConfigManager.load_work_item_mapping(config_dir)
    user_stories = mapping.get('stories', {})
    
    if not user_stories:
        print("❌ No user stories found in mapping")
        return
    
    print(f"📋 Will check {len(user_stories)} user stories using Playwright MCP...")
    print("=" * 80)
    
    # Create a list of URLs to check
    stories_to_check = []
    for story_id, work_item_id in sorted(user_stories.items()):
        url = f"https://dev.azure.com/centralgroup/Product%20-%20New%20OMS/_workitems/edit/{work_item_id}"
        stories_to_check.append({
            'story_id': story_id,
            'work_item_id': work_item_id,
            'url': url
        })
    
    # Save the list for reference
    output_file = Path(__file__).parent / "stories_to_check.json"
    with open(output_file, 'w') as f:
        json.dump(stories_to_check, f, indent=2)
    
    print(f"📄 Story list saved to: {output_file}")
    print(f"🌐 First story URL: {stories_to_check[0]['url']}")
    print(f"📊 Total stories to check: {len(stories_to_check)}")
    
    return stories_to_check


if __name__ == "__main__":
    stories_to_check = main()
    print("\n🚀 Ready to use Playwright MCP to check stories systematically")
    print("Next step: Use browser automation to inspect each story for corruption")