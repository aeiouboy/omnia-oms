# Azure DevOps Integration Toolkit

A clean, reusable toolkit for managing Azure DevOps work items from markdown specifications.

## Quick Start

### 1. Setup Configuration
```bash
# Copy the example config
cp .env.example .env

# Edit .env with your Azure DevOps details
AZURE_DEVOPS_ORG_URL=https://dev.azure.com/yourorg
AZURE_DEVOPS_PROJECT=Your Project Name
AZURE_DEVOPS_PAT=your_personal_access_token
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Commands

**Create new work items from markdown:**
```bash
python commands/create_work_items.py
```

**Update existing work items with latest markdown:**
```bash
python commands/update_from_markdown.py
```

## Architecture

### Core Components

- **`azure_devops_manager.py`** - Main library with all Azure DevOps operations
- **`commands/`** - Clean command-line tools for common operations
- **`legacy/`** - Previous iteration scripts (preserved for reference)

### Key Classes

- **`AzureDevOpsManager`** - Main interface for Azure DevOps operations
- **`MarkdownParser`** - Extracts epics and user stories from markdown
- **`ConfigManager`** - Handles configuration and work item mapping

## Features

✅ **Clean Architecture** - Unified library with reusable components  
✅ **Markdown Parsing** - Extracts epics and user stories with full details  
✅ **Epic Management** - Creates rich epics with business value, metrics, risks  
✅ **Story Management** - Handles user stories with proper acceptance criteria  
✅ **HTML Formatting** - Generates proper HTML for Azure DevOps fields  
✅ **Work Item Updates** - Updates existing items with latest markdown content  
✅ **Configuration Management** - Environment-based configuration  
✅ **Error Handling** - Comprehensive error handling and validation  

## Data Flow

```
Markdown File → MarkdownParser → Data Objects → AzureDevOpsManager → Azure DevOps
```

### Epic Structure
- Epic Overview (from markdown `### Epic Overview`)  
- Business Value (from `**Business Value:**`)  
- Key Stakeholders (from `**Key Stakeholders:**`)  
- Success Metrics (from `**Success Metrics:**` list)  
- Risk Factors (from `**Risk Factors:**` list)  

### Story Structure  
- User Story statement (As a/I want/So that)  
- Dependencies  
- Technical Notes  
- Acceptance Criteria (Given/When/Then in dedicated field)  

## Configuration Files

- **`.env`** - Azure DevOps connection details (not committed)
- **`work_item_mapping.json`** - Maps stories/epics to Azure DevOps IDs
- **`requirements.txt`** - Python dependencies

## Usage Examples

### Creating Work Items
```python
from azure_devops_manager import AzureDevOpsManager, MarkdownParser, ConfigManager

# Load config and connect
org_url, project, pat = ConfigManager.load_config(Path.cwd())
manager = AzureDevOpsManager(org_url, pat, project)

# Parse markdown and create items
epics = MarkdownParser.parse_epics("path/to/stories.md")
for epic in epics.values():
    epic_id = manager.create_epic(epic)
```

### Updating Existing Items
```python
# Load existing mapping and update from markdown
mapping = ConfigManager.load_work_item_mapping(Path.cwd())
epics = MarkdownParser.parse_epics("path/to/stories.md")

for epic_name, work_item_id in mapping['epics'].items():
    epic_data = epics[epic_name]
    manager.update_epic_from_data(work_item_id, epic_data)
```

## Best Practices

### Markdown Structure
- Use consistent epic headers: `## Epic N: Title`
- Include all epic sections: Overview, Business Value, Stakeholders, Metrics, Risks
- Use consistent story headers: `#### ID-NNN: Title`
- Structure acceptance criteria with Given/When/Then

### Azure DevOps Integration
- Use separate Description and Acceptance Criteria fields for stories
- Apply HTML formatting for rich content display
- Maintain parent-child relationships between epics and stories
- Use consistent tagging for organization

### Development Workflow
1. Update markdown specifications
2. Run `update_from_markdown.py` to sync changes
3. Verify updates in Azure DevOps web interface
4. Commit markdown changes to version control

## Troubleshooting

### Connection Issues
- Verify PAT has necessary permissions (Work Items: Read & Write)
- Check organization URL format: `https://dev.azure.com/yourorg`
- Ensure project name matches exactly (case-sensitive)

### Parsing Issues  
- Verify markdown follows expected structure
- Check for consistent header formats
- Ensure epic/story sections are properly formatted

### Update Issues
- Verify work_item_mapping.json exists and has correct IDs
- Check that Azure DevOps work items still exist
- Ensure user has permissions to modify work items

## Migration from Legacy Scripts

The legacy scripts in `/legacy/` folder were consolidated into this clean architecture. The new system provides:
- Better error handling and validation
- Cleaner separation of concerns  
- Reusable components for future projects
- Consistent HTML formatting
- Precise epic-to-content matching

All functionality from the previous scripts is preserved but organized into maintainable, reusable components.