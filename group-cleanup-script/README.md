# GitLab Group Projects Cleanup Script

This script deletes all projects from the GitLab group `tomerrab21-group`.

## ⚠️ WARNING
**This action is IRREVERSIBLE!** All projects in the specified group will be permanently deleted.

## Prerequisites

1. **GitLab Access Token** with the following scopes:
   - `api` (full API access)
   - `read_user`
   - `read_repository`
   - `write_repository`

2. **Python 3.6+**

3. **requests library**

## Setup

1. Install dependencies:
   ```bash
   cd gitlab-cleanup
   pip install -r requirements.txt
   ```

2. Get your GitLab access token:
   - Go to GitLab.com → Profile → Access Tokens
   - Create a token with `api` scope
   - Copy the token

## Usage

### Option 1: Set Environment Variable (Recommended)
```bash
export GITLAB_TOKEN="your_gitlab_token_here"
python delete_group_projects.py
```

### Option 2: Enter Token When Prompted
```bash
python delete_group_projects.py
# Script will prompt for token if not in environment
```

## Safety Features

1. **Dry Run Mode**: Always run in dry-run mode first to see what projects will be deleted
2. **Confirmation Required**: Must type exact confirmation phrase to proceed
3. **Progress Tracking**: Shows progress and results for each deletion
4. **Error Handling**: Continues if individual deletions fail
5. **Summary Report**: Shows final statistics

## Example Output

```
🧹 GitLab Group Projects Cleanup Script
==================================================
🔍 Do you want to run in DRY RUN mode first? (recommended) [y/N]: y

🔍 Looking up group: tomerrab21-group
📁 Found group ID: 12345
📋 Fetching projects...
📊 Found 5 projects:
  1. test-microservice (ID: 67890) - https://gitlab.com/tomerrab21-group/test-microservice
  2. demo-library (ID: 67891) - https://gitlab.com/tomerrab21-group/demo-library
  ...

🔍 DRY RUN MODE - No projects will be deleted
```

## What You Need to Provide

Please provide your **GitLab Access Token**. You can either:

1. **Set it as environment variable**: `export GITLAB_TOKEN="your_token"`
2. **Enter it when prompted** by the script

### How to Get GitLab Access Token:

1. Go to https://gitlab.com/-/profile/personal_access_tokens
2. Click "Add new token"
3. Name: `Project Cleanup Script`
4. Expiration: Set appropriate date
5. Scopes: Select `api`
6. Click "Create personal access token"
7. Copy the token (you won't see it again!)

## Script Features

- ✅ **Safe by default**: Dry-run mode recommended
- ✅ **User confirmation**: Requires typing exact phrase
- ✅ **Progress tracking**: Shows what's happening
- ✅ **Error handling**: Continues on individual failures
- ✅ **Summary reporting**: Final statistics
- ✅ **Rate limiting**: Small delays between deletions
- ✅ **Detailed logging**: Clear success/failure messages

## Group Configuration

The script is currently configured to delete projects from: `tomerrab21-group`

If you need to change the group, edit the `GROUP_PATH` variable in the script.