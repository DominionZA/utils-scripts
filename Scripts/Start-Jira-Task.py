#!/usr/bin/env python3
import re
import sys
import subprocess
import os
import requests
from requests.auth import HTTPBasicAuth
from urllib.parse import urlparse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Script variables - Configure these before running
JIRA_TICKET = "API-692"      # Replace with your ticket number
SELECTED_PROJECT = 2         # 1 = cloud_backend, 2 = aura_portal, 3 = cloud_reports
BRANCH_TYPE = "feature"      # "feature" or "hotfix"
TEST_MODE = False            # If True, will cleanup (switch to develop and delete branch) when done

# Configuration - Rarely changes
SOURCE_ROOT = r"C:\Source"
JIRA_BASE_URL = "https://cosoft.atlassian.net"  # Cosoft JIRA instance
JIRA_EMAIL = os.getenv('JIRA_EMAIL')
JIRA_API_TOKEN = os.getenv('JIRA_API_TOKEN')

def test_jira_connection():
    """Test JIRA API connection."""
    if not JIRA_EMAIL or not JIRA_API_TOKEN:
        print("Error: JIRA credentials not configured")
        sys.exit(1)
        
    try:
        response = requests.get(
            f"{JIRA_BASE_URL}/rest/api/3/myself",
            auth=HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN)
        )
        response.raise_for_status()
        print("Successfully connected to JIRA API")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to JIRA: {str(e)}")
        sys.exit(1)

def get_ticket_summary(ticket):
    """Get the summary of a JIRA ticket."""
    try:
        response = requests.get(
            f"{JIRA_BASE_URL}/rest/api/3/issue/{ticket}",
            auth=HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN)
        )
        response.raise_for_status()
        data = response.json()
        return data['fields']['summary']
    except requests.exceptions.RequestException as e:
        print(f"Error fetching ticket {ticket}: {str(e)}")
        sys.exit(1)
    except KeyError:
        print(f"Error: Could not find summary for ticket {ticket}")
        sys.exit(1)

def validate_jira_ticket(ticket):
    """Validate the JIRA ticket format and existence."""
    if not re.match(r'^[A-Z]+-\d+$', ticket):
        print(f"Error: Invalid JIRA ticket format. Expected format: ABC-123")
        sys.exit(1)
    # Try to fetch the ticket to validate it exists
    get_ticket_summary(ticket)
    return True

def validate_branch_type(branch_type):
    """Validate the branch type."""
    valid_types = ["feature", "hotfix"]
    if branch_type.lower() not in valid_types:
        print(f"Error: Invalid branch type. Must be one of: {', '.join(valid_types)}")
        sys.exit(1)
    return True

def get_project_folder(project_num):
    """Get project folder name."""
    project_map = {
        1: "cloud_backend",
        2: "aura_portal",
        3: "cloud_reports"
    }
    if project_num not in project_map:
        print(f"Error: Invalid project number. Must be 1 (cloud_backend), 2 (aura_portal), or 3 (cloud_reports)")
        sys.exit(1)
    return project_map[project_num]

def get_project_path(project_num):
    """Get the full path for the selected project."""
    folder_name = get_project_folder(project_num)
    return os.path.join(SOURCE_ROOT, folder_name)

def run_command(command, error_message, cwd=None, exit_on_error=True):
    """Run a command and handle any errors."""
    print(f"Running: {command} in {cwd if cwd else 'current directory'}")
    try:
        result = subprocess.run(command, 
                              check=True, 
                              shell=True, 
                              text=True,
                              capture_output=True,
                              cwd=cwd)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error: {error_message}")
        print(f"Command output: {e.stderr}")
        if exit_on_error:
            sys.exit(1)
        raise

def verify_git_repo(project_path):
    """Verify that the directory is a git repository."""
    try:
        run_command("git rev-parse --git-dir",
                   "Not a git repository",
                   cwd=project_path,
                   exit_on_error=False)
        return True
    except subprocess.CalledProcessError:
        print(f"\nError: {project_path} is not a git repository.")
        print("Please ensure you're in a git repository and try again.")
        sys.exit(1)

def create_branch(ticket, project_num, branch_type):
    """Create and checkout a new git branch."""
    summary = get_ticket_summary(ticket)
    # Convert summary to lowercase, replace spaces with hyphens, remove special chars
    clean_summary = re.sub(r'[^a-zA-Z0-9\s-]', '', summary.lower()).replace(' ', '-')
    # Limit length of summary in branch name
    clean_summary = clean_summary[:50]
    branch_name = f"{branch_type}/{ticket}-{clean_summary}"
    
    project_path = get_project_path(project_num)
    folder_name = get_project_folder(project_num)
    
    # Verify the project directory exists
    if not os.path.exists(project_path):
        print(f"Error: Project directory not found: {project_path}")
        print(f"Looking for: {project_path}")
        print(f"SOURCE_ROOT is set to: {SOURCE_ROOT}")
        sys.exit(1)
    
    # Verify it's a git repository
    verify_git_repo(project_path)
    
    print(f"\nCreating branch for ticket: {ticket}")
    print(f"Summary: {summary}")
    
    # All git commands will run in the project directory
    run_command("git checkout master",
               "Failed to checkout master branch",
               cwd=project_path)
               
    run_command("git pull",
               "Failed to pull latest changes from master",
               cwd=project_path)
               
    run_command(f"git checkout -b {branch_name}",
               f"Failed to create and checkout branch {branch_name}",
               cwd=project_path)
    
    print(f"\nSuccessfully created branch '{branch_name}' in {folder_name} project")
               
    if TEST_MODE:
        print("\nTest mode cleanup:")
        run_command("git checkout develop",
                   "Failed to checkout develop branch",
                   cwd=project_path)
        run_command(f"git branch -D {branch_name}",
                   f"Failed to delete test branch {branch_name}",
                   cwd=project_path)
        print(f"Cleaned up test branch '{branch_name}'")

def main():
    print(f"Starting task for:")
    print(f"JIRA Ticket: {JIRA_TICKET}")
    print(f"Project: {get_project_folder(SELECTED_PROJECT)}")
    print(f"Branch Type: {BRANCH_TYPE}")
    print(f"Test Mode: {TEST_MODE}")
    print(f"Project Path: {get_project_path(SELECTED_PROJECT)}")
    
    validate_jira_ticket(JIRA_TICKET)
    validate_branch_type(BRANCH_TYPE)
    create_branch(JIRA_TICKET, SELECTED_PROJECT, BRANCH_TYPE.lower())

if __name__ == "__main__":
    main() 