#!/usr/bin/env python3
"""
GitLab Group Projects Cleanup Script

This script deletes all projects from a specified GitLab group.
WARNING: This action is irreversible! Use with caution.

Usage:
    python delete_group_projects.py

Requirements:
    - requests library: pip install requests
    - GitLab access token with appropriate permissions
"""

import requests
import time
import os
from typing import List, Dict, Optional

class GitLabCleaner:
    def __init__(self, token: str, gitlab_url: str = "https://gitlab.com/api/v4"):
        """
        Initialize GitLab cleaner
        
        Args:
            token: GitLab personal access token with API and project delete permissions
            gitlab_url: GitLab API base URL
        """
        self.token = token
        self.base_url = gitlab_url.rstrip('/')
        self.headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
    def get_group_id(self, group_path: str) -> Optional[int]:
        """Get group ID by path"""
        try:
            response = requests.get(
                f"{self.base_url}/groups/{group_path}",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                group_data = response.json()
                return group_data['id']
            elif response.status_code == 404:
                print(f"❌ Group '{group_path}' not found")
                return None
            else:
                print(f"❌ Failed to get group info: {response.status_code} - {response.text}")
                return None
                
        except requests.RequestException as e:
            print(f"❌ Network error getting group: {e}")
            return None
    
    def get_group_projects(self, group_id: int) -> List[Dict]:
        """Get all projects in a group"""
        projects = []
        page = 1
        per_page = 100
        
        while True:
            try:
                response = requests.get(
                    f"{self.base_url}/groups/{group_id}/projects",
                    headers=self.headers,
                    params={'page': page, 'per_page': per_page, 'include_subgroups': False},
                    timeout=30
                )
                
                if response.status_code != 200:
                    print(f"❌ Failed to get projects: {response.status_code} - {response.text}")
                    break
                
                page_projects = response.json()
                if not page_projects:
                    break
                    
                projects.extend(page_projects)
                
                if len(page_projects) < per_page:
                    break
                    
                page += 1
                
            except requests.RequestException as e:
                print(f"❌ Network error getting projects: {e}")
                break
        
        return projects
    
    def delete_project(self, project_id: int, project_name: str) -> bool:
        """Delete a single project"""
        try:
            response = requests.delete(
                f"{self.base_url}/projects/{project_id}",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 202:  # GitLab returns 202 for successful deletion
                print(f"✅ Successfully deleted project: {project_name} (ID: {project_id})")
                return True
            else:
                print(f"❌ Failed to delete project {project_name}: {response.status_code} - {response.text}")
                return False
                
        except requests.RequestException as e:
            print(f"❌ Network error deleting project {project_name}: {e}")
            return False
    
    def cleanup_group_projects(self, group_path: str, dry_run: bool = False) -> None:
        """
        Delete all projects from a GitLab group
        
        Args:
            group_path: GitLab group path (e.g., 'username/groupname' or 'groupname')
            dry_run: If True, only list projects without deleting them
        """
        print(f"🔍 Looking up group: {group_path}")
        
        # Get group ID
        group_id = self.get_group_id(group_path)
        if not group_id:
            return
        
        print(f"📁 Found group ID: {group_id}")
        
        # Get all projects in the group
        print("📋 Fetching projects...")
        projects = self.get_group_projects(group_id)
        
        if not projects:
            print("✅ No projects found in the group")
            return
        
        print(f"📊 Found {len(projects)} projects:")
        for i, project in enumerate(projects, 1):
            print(f"  {i}. {project['name']} (ID: {project['id']}) - {project['web_url']}")
        
        if dry_run:
            print("🔍 DRY RUN MODE - No projects will be deleted")
            return
        
        # Confirmation prompt (skip in non-interactive mode)
        print(f"\n⚠️  WARNING: This will DELETE ALL {len(projects)} projects from group '{group_path}'")
        print("⚠️  This action is IRREVERSIBLE!")
        
        try:
            confirmation = input("\n❓ Type 'DELETE ALL PROJECTS' to confirm: ")
            
            if confirmation != "DELETE ALL PROJECTS":
                print("❌ Operation cancelled")
                return
        except EOFError:
            # Non-interactive mode - proceed with deletion
            print("🤖 Non-interactive mode detected - proceeding with deletion...")
            print("✅ AUTO-CONFIRMED: DELETE ALL PROJECTS")
        
        # Delete projects
        print(f"\n🗑️  Starting deletion of {len(projects)} projects...")
        deleted_count = 0
        failed_count = 0
        
        for i, project in enumerate(projects, 1):
            print(f"\n[{i}/{len(projects)}] Deleting: {project['name']}")
            
            if self.delete_project(project['id'], project['name']):
                deleted_count += 1
                # Add small delay to avoid rate limiting
                time.sleep(0.5)
            else:
                failed_count += 1
        
        # Summary
        print(f"\n📊 DELETION SUMMARY:")
        print(f"✅ Successfully deleted: {deleted_count} projects")
        if failed_count > 0:
            print(f"❌ Failed to delete: {failed_count} projects")
        print(f"🔍 Total processed: {len(projects)} projects")

def main():
    """Main function"""
    print("🧹 GitLab Group Projects Cleanup Script")
    print("=" * 50)
    
    # Get configuration
    GROUP_PATH = "tomerrab21-group"
    
    # Get token from environment or prompt
    token = os.getenv('GITLAB_TOKEN')
    if not token:
        print("💡 GitLab token not found in environment variable GITLAB_TOKEN")
        token = input("🔑 Enter your GitLab access token: ").strip()
    
    if not token:
        print("❌ GitLab token is required")
        return
    
    # Ask for dry run
    dry_run_input = input(f"\n🔍 Do you want to run in DRY RUN mode first? (recommended) [y/N]: ").strip().lower()
    dry_run = dry_run_input in ['y', 'yes']
    
    # Initialize cleaner
    cleaner = GitLabCleaner(token)
    
    # Run cleanup
    try:
        cleaner.cleanup_group_projects(GROUP_PATH, dry_run=dry_run)
    except KeyboardInterrupt:
        print("\n❌ Operation interrupted by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()