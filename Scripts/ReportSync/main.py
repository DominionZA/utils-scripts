#!/usr/bin/env python3
"""
Main script for the ReportSync package.
Syncs report files from a source location to a destination location.
"""

import os
import sys
from pathlib import Path
import argparse

# Add the parent directory to the path so we can import our modules
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
sys.path.insert(0, parent_dir)

# Import our modules
from ReportSync.utils import ensure_dependencies, get_user_confirmation
from ReportSync.file_operations import copy_files, copy_files_with_categories
from ReportSync.git_operations import check_git_branch, check_git_changes, switch_git_branch, commit_changes, push_changes, create_branch_if_not_exists
from ReportSync.test_utils import test_modify_destination_file
from ReportSync.notifications import send_slack_notification, format_changed_files_for_slack


# ANSI color codes for text colors
RED = "\033[91m"
YELLOW = "\033[93m"
GREEN = "\033[92m"
RESET = "\033[0m"


def main(test_mode=False, notify_frank=False):
    """
    Main function to copy report files and check for Git changes.
    
    Args:
        test_mode: If True, runs in test mode which modifies a file to ensure changes are detected
        notify_frank: If True, sends notifications to Frank's webhook
    """
    # Ensure dependencies are installed
    ensure_dependencies()
    
    # Define source and destination paths
    source = r"C:\Users\msmit\Dropbox\Cloud_Reports\Main"
    # Alternative source: r"C:\Temp\Main"
    destination = r"C:\Source\cloud_reports\Reports"
    repo_path = os.path.dirname(destination)
    
    # Determine which branch to use based on test mode
    required_branch = "test" if test_mode else "develop"
    
    # Check if the destination repository is on the required branch
    is_on_required_branch, current_branch = check_git_branch(repo_path)
    if current_branch.lower() != required_branch:
        warning_message = f"WARNING: Git repository is not on the '{required_branch}' branch. Current branch: '{current_branch}'"
        
        # Print with yellow color as a warning
        print(f"{YELLOW}{warning_message}{RESET}")
        
        # If test mode, create the test branch if it doesn't exist
        if test_mode and required_branch == "test":
            print(f"{YELLOW}Checking if '{required_branch}' branch exists...{RESET}")
            create_success, create_message = create_branch_if_not_exists(repo_path, required_branch)
            print(f"{GREEN if create_success else RED}{create_message}{RESET}")
        
        # Prompt the user to switch to the required branch
        if get_user_confirmation(f"Do you want to switch to the '{required_branch}' branch?"):
            print(f"{YELLOW}Attempting to switch to {required_branch} branch...{RESET}")
            
            # Try to switch to the required branch
            success, message = switch_git_branch(repo_path, required_branch)
            
            if success:
                print(f"{GREEN}{message}{RESET}")
                # Re-check the branch to make sure we're on the required branch now
                is_on_required_branch, current_branch = check_git_branch(repo_path)
                if current_branch.lower() != required_branch:
                    print(f"{RED}Failed to switch to {required_branch} branch. Current branch: {current_branch}{RESET}")
                    send_slack_notification(f"Report deployment aborted: Failed to switch to {required_branch} branch", test_mode=test_mode, notify_frank=notify_frank)
                    return
            else:
                print(f"{RED}{message}{RESET}")
                print(f"{RED}Aborting execution. Please switch to the '{required_branch}' branch manually and try again.{RESET}")
                send_slack_notification(f"Report deployment aborted: Could not switch to {required_branch} branch - {message}", test_mode=test_mode, notify_frank=notify_frank)
                return
        else:
            print(f"{RED}Aborting execution as requested.{RESET}")
            # No Slack notification sent when user declines
            return
    else:
        print(f"Git repository is on the correct branch: {current_branch}")
    
    # Delete target Reports folder if it exists
    if os.path.exists(destination):
        os.system(f"rmdir /s /q \"{destination}\"")  # Using os.system for Windows compatibility
        print(f"Deleted existing destination: {destination}")
    
    # Copy files with the same structure as in the PowerShell script
    copy_files_with_categories(os.path.join(source, "User", "Reports"), 
                               os.path.join(destination, "User", "Reports"))
    
    copy_files(os.path.join(source, "User", "Dashboards"), 
               os.path.join(destination, "User", "Dashboards"))
    
    copy_files_with_categories(os.path.join(source, "Support", "Reports"), 
                               os.path.join(destination, "Support", "Reports"))
    
    copy_files(os.path.join(source, "Support", "Dashboards"), 
               os.path.join(destination, "Support", "Dashboards"))
    
    # If in test mode, modify a destination file to ensure we have changes to detect
    if test_mode:
        print("\nRunning in TEST MODE - will modify a destination file")
        
        # Modify a destination file without committing first
        success, message = test_modify_destination_file(destination)
        print(message)
        
        if not success:
            print(f"{RED}Test failed, cannot proceed with checking for changes{RESET}")
            send_slack_notification("Report deployment test failed: Could not modify test file", test_mode=test_mode, notify_frank=notify_frank)
            return
    else:
        print("\nRunning in NORMAL MODE - will NOT modify any test files")
    
    # Check for Git changes in the repository
    print("\nChecking Git changes in the repository...")
    
    changed_files = check_git_changes(repo_path)
    
    if changed_files:
        print("\nThe following files have changed:")
        
        # Add a line break before the list
        print("")
        
        for status, file_path in changed_files:
            status_desc = {
                "M": "Modified",
                "A": "Added",
                "D": "Deleted",
                "R": "Renamed",
                "C": "Copied",
                "U": "Updated but unmerged",
                "??": "Untracked"
            }.get(status, status)
            
            print(f"{status_desc}: {file_path}")
        
        # Add a line break after the list
        print("")
        
        # Commit the changes with a descriptive message
        try:
            success, message = commit_changes(repo_path, destination, f"Updated reports ({len(changed_files)})")
            if success:
                print(f"\n{GREEN}{message}{RESET}")
                
                # Add a confirmation prompt before pushing to remote
                print(f"\n{YELLOW}The following files will be pushed to the remote repository:{RESET}")
                
                # Add a line break before the list
                print("")
                
                for status, file_path in changed_files:
                    status_desc = {
                        "M": "Modified",
                        "A": "Added",
                        "D": "Deleted",
                        "R": "Renamed",
                        "C": "Copied",
                        "U": "Updated but unmerged",
                        "??": "Untracked"
                    }.get(status, status)
                    
                    print(f"  {status_desc}: {file_path}")
                
                # Add a line break after the list
                print("")
                
                # Get the current branch name
                _, current_branch = check_git_branch(repo_path)
                
                # Ask for confirmation before pushing, with a simpler message
                if get_user_confirmation(f"Do you want to push these changes to {current_branch}?"):
                    # Push the changes to the remote repository
                    print(f"{YELLOW}Pushing changes to {current_branch}. This may take a moment...{RESET}")
                    push_success, push_message = push_changes(repo_path)
                    if push_success:
                        print(f"{GREEN}{push_message}{RESET}")
                        
                        # Format changed files for Slack notification
                        files_list = format_changed_files_for_slack(changed_files)
                        
                        # Send Slack notification on successful push
                        send_slack_notification(f"Reports deployed.\n\n{files_list}", test_mode=test_mode, notify_frank=notify_frank)
                        
                        # Display success message only after successful push
                        success_message = f"Test successful! Changes pushed to {current_branch}." if test_mode else f"Report deployment completed successfully to {current_branch}!"
                        print(f"\n{GREEN}{success_message}{RESET}")
                    else:
                        print(f"{RED}{push_message}{RESET}")
                        print(f"{YELLOW}Changes were committed but not pushed. Please push manually.{RESET}")
                else:
                    print(f"{YELLOW}Changes were committed but not pushed as requested.{RESET}")
                    print(f"{YELLOW}You can push the changes manually later if needed.{RESET}")
            else:
                print(f"\n{YELLOW}{message}{RESET}")
        except Exception as e:
            print(f"{RED}Warning: Could not commit changes: {str(e)}{RESET}")
    else:
        # No changes detected - this is not a failure, just a status
        if test_mode:
            no_changes_message = "Test result: No changes detected in the Git repository."
        else:
            no_changes_message = "No changes detected."
        
        # Print in yellow to indicate this is informational, not an error
        print(f"\n{YELLOW}{no_changes_message}{RESET}")
        
        # Send Slack notification
        send_slack_notification(no_changes_message, test_mode=test_mode, notify_frank=notify_frank)


# If this script is run directly, call main() with default parameters
if __name__ == "__main__":
    # Get test_mode from command line arguments if provided
    parser = argparse.ArgumentParser(description='Sync and deploy report files.')
    parser.add_argument('--test', action='store_true', help='Run in test mode')
    parser.add_argument('--notify-frank', action='store_true', help='Send notifications to Frank')
    
    args = parser.parse_args()
    
    # Run the main function with the appropriate mode
    main(test_mode=args.test, notify_frank=args.notify_frank) 