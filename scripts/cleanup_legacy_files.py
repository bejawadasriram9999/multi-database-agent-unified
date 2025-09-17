#!/usr/bin/env python3
"""
Cleanup Legacy Files Script
Safely removes unnecessary legacy files after implementing the unified architecture.
"""

import os
import shutil
import sys
from pathlib import Path

def main():
    """Main cleanup function."""
    print("🧹 Multi-Database Agent - Legacy Files Cleanup")
    print("=" * 60)
    print("This script will remove legacy files that are no longer needed")
    print("with the unified MCP server approach.")
    print("=" * 60)
    
    # Get project root directory
    project_root = Path(__file__).parent.parent
    
    # Files to delete (legacy files)
    files_to_delete = [
        # Legacy agent files
        "mongodb_agent/agent.py",
        "mongodb_agent/prompt.py",
        
        # Legacy MCP servers
        "mcp_servers/mongodb_mcp_server.py",
        "mcp_servers/oracle_mcp_server.py",
        
        # Database router (now built into unified MCP server)
        "database_router.py",
        
        # Legacy test scripts
        "scripts/test_router.py",
        "scripts/test_mongodb_mcp.py",
    ]
    
    # Directories to delete (cache directories)
    dirs_to_delete = [
        "__pycache__",
        "mcp_servers/__pycache__",
        "mongodb_agent/__pycache__",
    ]
    
    print("\n📋 Files to be deleted:")
    for file_path in files_to_delete:
        full_path = project_root / file_path
        if full_path.exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} (not found)")
    
    print("\n📋 Directories to be deleted:")
    for dir_path in dirs_to_delete:
        full_path = project_root / dir_path
        if full_path.exists():
            print(f"  ✅ {dir_path}")
        else:
            print(f"  ❌ {dir_path} (not found)")
    
    # Ask for confirmation
    print("\n⚠️  WARNING: This action cannot be undone!")
    response = input("\nDo you want to proceed with the cleanup? (y/N): ").strip().lower()
    
    if response not in ['y', 'yes']:
        print("❌ Cleanup cancelled.")
        return 0
    
    print("\n🗑️  Starting cleanup...")
    
    # Delete files
    deleted_files = 0
    for file_path in files_to_delete:
        full_path = project_root / file_path
        if full_path.exists():
            try:
                full_path.unlink()
                print(f"  ✅ Deleted: {file_path}")
                deleted_files += 1
            except Exception as e:
                print(f"  ❌ Failed to delete {file_path}: {e}")
        else:
            print(f"  ⚠️  Skipped: {file_path} (not found)")
    
    # Delete directories
    deleted_dirs = 0
    for dir_path in dirs_to_delete:
        full_path = project_root / dir_path
        if full_path.exists():
            try:
                shutil.rmtree(full_path)
                print(f"  ✅ Deleted: {dir_path}")
                deleted_dirs += 1
            except Exception as e:
                print(f"  ❌ Failed to delete {dir_path}: {e}")
        else:
            print(f"  ⚠️  Skipped: {dir_path} (not found)")
    
    print(f"\n🎉 Cleanup completed!")
    print(f"  - Deleted {deleted_files} files")
    print(f"  - Deleted {deleted_dirs} directories")
    
    # Show remaining structure
    print("\n📁 Remaining project structure:")
    print("=" * 40)
    
    essential_files = [
        "mcp_servers/unified_mcp_server.py",
        "mongodb_agent/simplified_agent.py",
        "mongodb_agent/simplified_prompt.py",
        "scripts/test_unified_approach.py",
        "README.md",
        "BUSINESS_DEMO_GUIDE.md",
        "ARCHITECTURE_COMPARISON.md",
        "ARCHITECTURE_ANSWERS.md",
        "UNIFIED_ARCHITECTURE_SUMMARY.md",
    ]
    
    for file_path in essential_files:
        full_path = project_root / file_path
        if full_path.exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} (missing)")
    
    print("\n📚 Next steps:")
    print("  1. Test the unified approach: python scripts/test_unified_approach.py")
    print("  2. Update any remaining references to deleted files")
    print("  3. Commit the cleanup to version control")
    print("  4. Enjoy the cleaner, simpler architecture!")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
