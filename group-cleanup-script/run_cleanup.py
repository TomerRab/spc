#!/usr/bin/env python3
"""
Easy runner for GitLab Group Projects Cleanup Script
This version runs non-interactively for easier automation
"""

from delete_group_projects import GitLabCleaner

def run_cleanup():
    """Run the cleanup with your specific configuration"""
    
    # Your GitLab token
    token = "glpat-NS4KHCapUCgCY_KCYXwf3G86MQp1Omhla2xvCw.01.120fd2k9l"
    
    # Group to clean
    group_path = "tomerrab21-group"
    
    print("🧹 GitLab Group Projects Cleanup Script")
    print("=" * 50)
    print(f"🎯 Target Group: {group_path}")
    print(f"🔑 Using provided token: {token[:12]}...")
    
    # Initialize cleaner
    cleaner = GitLabCleaner(token)
    
    print("\n" + "="*50)
    print("🔍 STEP 1: DRY RUN (See what would be deleted)")
    print("="*50)
    
    # First run dry-run to show what would be deleted
    cleaner.cleanup_group_projects(group_path, dry_run=True)
    
    print("\n" + "="*50)
    print("💥 STEP 2: ACTUAL DELETION")
    print("="*50)
    
    # Ask for confirmation
    print("⚠️  The above projects will be PERMANENTLY DELETED!")
    print("⚠️  This action is IRREVERSIBLE!")
    
    while True:
        confirm = input("\n❓ Do you want to proceed with DELETING ALL PROJECTS? [y/N]: ").strip().lower()
        if confirm in ['n', 'no', '']:
            print("❌ Operation cancelled")
            return
        elif confirm in ['y', 'yes']:
            break
        else:
            print("Please enter 'y' for yes or 'n' for no")
    
    # Final confirmation
    final_confirm = input("\n❓ Type 'DELETE ALL PROJECTS' to confirm: ").strip()
    if final_confirm != "DELETE ALL PROJECTS":
        print("❌ Operation cancelled - confirmation text did not match")
        return
    
    # Run actual deletion
    cleaner.cleanup_group_projects(group_path, dry_run=False)

if __name__ == "__main__":
    run_cleanup()