#!/usr/bin/env python3
"""
Non-interactive version - WILL DELETE ALL PROJECTS IMMEDIATELY
"""

from delete_group_projects import GitLabCleaner

def delete_all_projects_now():
    """Delete all projects without prompts - USE WITH CAUTION!"""
    
    # Your GitLab token
    token = "glpat-NS4KHCapUCgCY_KCYXwf3G86MQp1Omhla2xvCw.01.120fd2k9l"
    
    # Group to clean
    group_path = "tomerrab21-group"
    
    print("💥 IMMEDIATE DELETION MODE - NO PROMPTS")
    print("=" * 50)
    print(f"🎯 Target Group: {group_path}")
    print("⚠️  ALL PROJECTS WILL BE DELETED NOW!")
    print("=" * 50)
    
    # Initialize cleaner
    cleaner = GitLabCleaner(token)
    
    # Run deletion immediately (dry_run=False)
    cleaner.cleanup_group_projects(group_path, dry_run=False)
    
    print("\n✅ CLEANUP COMPLETE!")

if __name__ == "__main__":
    delete_all_projects_now()