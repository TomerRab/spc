# Quick Usage Guide

## ✅ Ready to Use!

Your GitLab cleanup script is ready with your token already configured.

## 📊 Current Status
- **Group**: `tomerrab21-group` (ID: 111460281)
- **Projects Found**: 30 projects
- **Token**: Configured and tested ✅

## 🚀 How to Run

### Option 1: Quick Run (Recommended)
```bash
cd gitlab-cleanup
source venv/bin/activate
python3 run_cleanup.py
```

### Option 2: Manual Run
```bash
cd gitlab-cleanup
source venv/bin/activate
python3 delete_group_projects.py
```

### Option 3: Test Only (See what would be deleted)
```bash
cd gitlab-cleanup
source venv/bin/activate  
python3 test_script.py
```

## 🛡️ Safety Features Active

1. ✅ **Dry-run first** - Shows what will be deleted
2. ✅ **Double confirmation** - Must confirm twice
3. ✅ **Progress tracking** - See each deletion
4. ✅ **Error handling** - Continues on failures
5. ✅ **Token validated** - Already tested with your group

## 📋 Projects That Will Be Deleted

The script found **30 projects** including:
- `river-project` and `river-project-delivery`
- `ouiluoiuo`, `dfgfdg`, `hamou`, `jjjjj`, `etzbaz`
- Many `-deletion_scheduled-` projects (already scheduled for deletion)
- Various test projects

## ⚠️ Important Notes

- **All 30 projects will be permanently deleted**
- **This action cannot be undone**
- **Projects already scheduled for deletion will also be removed**
- **The script handles rate limiting automatically**

## 🔧 Files Created

- `delete_group_projects.py` - Main script with full safety features
- `run_cleanup.py` - Easy runner with your token pre-configured  
- `test_script.py` - Test script to see what will be deleted
- `setup.sh` - Setup virtual environment
- Documentation and configuration files

**Your token is already configured and tested - you're ready to go!** 🚀