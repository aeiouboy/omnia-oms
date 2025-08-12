# Legacy Scripts

This folder contains the previous iteration scripts that were used during development and troubleshooting. They are preserved for reference but should not be used for new projects.

## Script History

These scripts were created during the development process to solve various formatting and content issues:

### Creation Scripts
- `create_azure_work_items.py` - Original work item creation script
- `create_parent_child_relationships.py` - Establish epic-story relationships
- `create_remaining_stories.py` - Create missing stories

### Formatting Fix Scripts  
- `remove_duplicate_acceptance_criteria.py` - Fixed duplicate sections issue
- `fix_acceptance_criteria_line_breaks.py` - Attempted line break fixes
- `move_acceptance_criteria_to_description.py` - Moved criteria to Description field
- `standardize_format_all_items.py` - Standardized all work item formats
- `fix_*_formatting.py` - Various formatting attempts

### Epic Update Scripts
- `update_epics_from_markdown.py` - Original epic update with parsing issues
- `fix_epic_parsing.py` - Improved epic parsing logic  
- `correct_epic_matching.py` - Fixed epic-to-content matching

### Utility Scripts
- `assign_stories.py` - Story assignment utilities
- `update_iterations.py` - Iteration management
- `update_work_item_descriptions.py` - Description updates

## Migration to New Architecture

All functionality from these legacy scripts has been consolidated into the new clean architecture:

- **`azure_devops_manager.py`** - Unified library with all operations
- **`commands/create_work_items.py`** - Clean work item creation
- **`commands/update_from_markdown.py`** - Clean markdown-based updates

## Usage Note

**DO NOT USE THESE SCRIPTS FOR NEW PROJECTS**

Instead, use the new unified commands in the `/commands/` directory. The legacy scripts are kept only for:
- Reference during troubleshooting
- Understanding the evolution of the solution
- Potential code salvage if needed

The new architecture provides:
- Better error handling
- Cleaner separation of concerns
- Reusable components
- Consistent formatting
- Precise content matching