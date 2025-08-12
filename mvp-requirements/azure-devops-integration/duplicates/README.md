# Duplicate Epic References

This directory contains files that reference duplicate epic IDs that were created and later replaced.

## Epic ID History

### Old Epics (Duplicates - Moved Here)
- **51656**: MAO MVP - Order Creation & Validation
- **51657**: MAO MVP - Bundle Processing  
- **51658**: MAO MVP - Payment Processing
- **51659**: MAO MVP - Fulfillment Integration
- **51660**: MAO MVP - Status Management
- **51661**: MAO MVP - Cancellation & Returns
- **51662**: MAO MVP - API Integration
- **51663**: MAO MVP - Data Management & Reporting

### Current Epics (Active in work_item_mapping.json)
- **51703**: Order Creation & Validation
- **51704**: Bundle Processing
- **51705**: Payment Processing  
- **51706**: Fulfillment Integration
- **51707**: Status Management
- **51708**: Cancellation & Returns
- **51709**: API Integration
- **51710**: Data Management & Reporting

## Files in This Directory

### COMPLETION_SUMMARY.md
- Contains summary of the first iteration of work items
- References the old epic IDs (51656-51663)
- Has been moved here to avoid confusion with current work items

## Current Active Files

The current active files using the correct epic IDs (51703-51710) are:
- `../work_item_mapping.json` - Current mapping
- `../commands/create_work_items.py` - Creation script
- `../commands/update_from_markdown.py` - Update script

## Cleanup Scripts

The delete duplicate scripts in `../commands/` can safely delete the old work items:
- `delete_duplicates.py` - Interactive deletion with safety checks
- `delete_duplicates_auto.py` - Automated deletion

These scripts specifically target the old IDs and have safety checks to avoid deleting current work items.