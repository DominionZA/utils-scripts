"""
Git operations module for the ReportSync package.
Contains functions for interacting with Git repositories.
"""

import os
import subprocess


def check_git_changes(repo_path):
    """
    Check which files have changed in the Git repository.
    
    Args:
        repo_path: Path to the Git repository
        
    Returns:
        list: List of tuples (status, file_path) for changed files
    """
    # Save current working directory
    original_dir = os.getcwd()
    
    try:
        # Change to the repository directory
        os.chdir(repo_path)
        
        # Check if this is a git repository
        try:
            subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], 
                          check=True, 
                          stdout=subprocess.PIPE, 
                          stderr=subprocess.PIPE)
        except subprocess.CalledProcessError:
            print(f"Error: {repo_path} is not a Git repository.")
            return []
        
        # Get list of changed files
        result = subprocess.run(["git", "status", "--porcelain"], 
                               check=True, 
                               stdout=subprocess.PIPE, 
                               text=True)
        
        # Parse the output to get the list of changed files
        changed_files = []
        for line in result.stdout.splitlines():
            if line.strip():
                # The first two characters indicate the status, the rest is the file path
                status = line[:2].strip()
                file_path = line[3:].strip()
                changed_files.append((status, file_path))
        
        return changed_files
    
    finally:
        # Restore original working directory
        os.chdir(original_dir)


def check_git_branch(repo_path):
    """
    Check if the Git repository is on a specific branch.
    
    Args:
        repo_path: Path to the Git repository
        
    Returns:
        tuple: (bool, str) - True if on develop branch, False otherwise, and the current branch name
    """
    # Save current working directory
    original_dir = os.getcwd()
    
    try:
        # Change to the repository directory
        os.chdir(repo_path)
        
        # Check if this is a git repository
        try:
            subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], 
                          check=True, 
                          stdout=subprocess.PIPE, 
                          stderr=subprocess.PIPE)
        except subprocess.CalledProcessError:
            return False, "Not a Git repository"
        
        # Get current branch
        result = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], 
                               check=True, 
                               stdout=subprocess.PIPE, 
                               text=True)
        
        current_branch = result.stdout.strip()
        
        # Check if on develop branch
        return current_branch.lower() == "develop", current_branch
    
    except Exception as e:
        return False, str(e)
    
    finally:
        # Restore original working directory
        os.chdir(original_dir)


def switch_git_branch(repo_path, branch_name):
    """
    Switch the Git repository to the specified branch.
    
    Args:
        repo_path: Path to the Git repository
        branch_name: Name of the branch to switch to
        
    Returns:
        tuple: (bool, str) - Success status and message
    """
    # Save current working directory
    original_dir = os.getcwd()
    
    try:
        # Change to the repository directory
        os.chdir(repo_path)
        
        # Check if the branch exists
        result = subprocess.run(["git", "show-ref", "--verify", "--quiet", f"refs/heads/{branch_name}"],
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
        
        if result.returncode != 0:
            return False, f"Branch '{branch_name}' does not exist in the repository"
        
        # Check for uncommitted changes
        result = subprocess.run(["git", "status", "--porcelain"],
                               check=True,
                               stdout=subprocess.PIPE,
                               text=True)
        
        if result.stdout.strip():
            return False, "Cannot switch branch: You have uncommitted changes in your repository"
        
        # Switch to the branch
        result = subprocess.run(["git", "checkout", branch_name],
                               check=True,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               text=True)
        
        return True, f"Successfully switched to branch '{branch_name}'"
    
    except Exception as e:
        return False, f"Error switching branch: {str(e)}"
    
    finally:
        # Restore original working directory
        os.chdir(original_dir)


def commit_changes(repo_path, path_to_add, commit_message):
    """
    Commit changes to the Git repository.
    
    Args:
        repo_path: Path to the Git repository
        path_to_add: Path to add to the commit
        commit_message: Commit message
        
    Returns:
        tuple: (bool, str) - Success status and message
    """
    # Save current working directory
    original_dir = os.getcwd()
    
    try:
        # Change to the repository directory
        os.chdir(repo_path)
        
        # Add files
        subprocess.run(["git", "add", path_to_add], check=True)
        
        # Commit
        result = subprocess.run(["git", "commit", "-m", commit_message], 
                               check=False,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               text=True)
        
        if "nothing to commit" in result.stderr:
            return False, "Nothing to commit"
        
        return True, f"Changes committed with message: '{commit_message}'"
    
    except Exception as e:
        return False, f"Error committing changes: {str(e)}"
    
    finally:
        # Restore original working directory
        os.chdir(original_dir)


def push_changes(repo_path, branch_name=None):
    """
    Push changes to the remote repository.
    
    Args:
        repo_path: Path to the Git repository
        branch_name: Name of the branch to push (if None, pushes the current branch)
        
    Returns:
        tuple: (bool, str) - Success status and message
    """
    # Save current working directory
    original_dir = os.getcwd()
    
    try:
        # Change to the repository directory
        os.chdir(repo_path)
        
        # If branch name is not provided, get the current branch
        if branch_name is None:
            result = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], 
                                  check=True, 
                                  stdout=subprocess.PIPE, 
                                  text=True)
            branch_name = result.stdout.strip()
        
        # Push to the remote
        push_command = ["git", "push", "origin", branch_name]
        result = subprocess.run(push_command,
                              check=False,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE,
                              text=True)
        
        if result.returncode != 0:
            return False, f"Failed to push changes: {result.stderr}"
        
        return True, f"Successfully pushed changes to origin/{branch_name}"
    
    except Exception as e:
        return False, f"Error pushing changes: {str(e)}"
    
    finally:
        # Restore original working directory
        os.chdir(original_dir)


def create_branch_if_not_exists(repo_path, branch_name):
    """
    Create a Git branch if it doesn't exist.
    
    Args:
        repo_path: Path to the Git repository
        branch_name: Name of the branch to create
        
    Returns:
        tuple: (bool, str) - Success status and message
    """
    # Save current working directory
    original_dir = os.getcwd()
    
    try:
        # Change to the repository directory
        os.chdir(repo_path)
        
        # Check if the branch exists
        result = subprocess.run(["git", "show-ref", "--verify", "--quiet", f"refs/heads/{branch_name}"],
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)
        
        if result.returncode == 0:
            # Branch already exists
            return True, f"Branch '{branch_name}' already exists"
        
        # Create the branch
        result = subprocess.run(["git", "branch", branch_name],
                              check=False,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE,
                              text=True)
        
        if result.returncode != 0:
            return False, f"Failed to create branch '{branch_name}': {result.stderr}"
        
        return True, f"Successfully created branch '{branch_name}'"
    
    except Exception as e:
        return False, f"Error creating branch: {str(e)}"
    
    finally:
        # Restore original working directory
        os.chdir(original_dir) 