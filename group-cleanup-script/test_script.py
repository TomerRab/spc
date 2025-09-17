#!/usr/bin/env python3
"""
Test script to check what projects are in the tomerrab21-group
"""

import requests
import os

def test_group_projects():
    token = "glpat-NS4KHCapUCgCY_KCYXwf3G86MQp1Omhla2xvCw.01.120fd2k9l"
    base_url = "https://gitlab.com/api/v4"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    group_path = "tomerrab21-group"
    
    print(f"🔍 Looking up group: {group_path}")
    
    # Get group ID
    try:
        response = requests.get(
            f"{base_url}/groups/{group_path}",
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            group_data = response.json()
            group_id = group_data['id']
            print(f"📁 Found group ID: {group_id}")
        elif response.status_code == 404:
            print(f"❌ Group '{group_path}' not found")
            return
        else:
            print(f"❌ Failed to get group info: {response.status_code} - {response.text}")
            return
            
    except requests.RequestException as e:
        print(f"❌ Network error getting group: {e}")
        return
    
    # Get all projects in the group
    print("📋 Fetching projects...")
    projects = []
    page = 1
    per_page = 100
    
    while True:
        try:
            response = requests.get(
                f"{base_url}/groups/{group_id}/projects",
                headers=headers,
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
    
    if not projects:
        print("✅ No projects found in the group")
        return
    
    print(f"📊 Found {len(projects)} projects:")
    for i, project in enumerate(projects, 1):
        print(f"  {i}. {project['name']} (ID: {project['id']}) - {project['web_url']}")
    
    print(f"\n🔍 DRY RUN COMPLETE - Found {len(projects)} projects that would be deleted")
    print("⚠️  To actually delete these projects, run the main script: python delete_group_projects.py")

if __name__ == "__main__":
    test_group_projects()