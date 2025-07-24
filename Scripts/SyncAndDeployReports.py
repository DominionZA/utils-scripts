#!/usr/bin/env python3
"""
SyncAndDeployReports.py

This script is a wrapper for the ReportSync package.
It syncs report files from a source location to a destination location.
"""

import os
import sys
import subprocess
import pkg_resources

# Add the current directory to the path so we can import our modules
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

# Function to install required packages
def install_requirements():
    requirements_path = os.path.join(script_dir, 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path) as f:
            required = {line.split('#')[0].strip() for line in f if line.strip() and not line.startswith('#')}
        
        installed = {pkg.key for pkg in pkg_resources.working_set}
        missing = required - installed
        
        if missing:
            print("Installing required packages...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', *missing])
            print("Required packages installed successfully.")

# Install required packages before importing other modules
install_requirements()

# Import the main function from the ReportSync package
from ReportSync.main import main

if __name__ == "__main__":
    # Simple toggle for test mode - set to True to run in test mode, False for normal mode
    TEST_MODE = False
    
    # Toggle for sending notifications to Frank - set to True to enable, False to disable
    NOTIFY_FRANK = True
    
    print(f"Starting script with TEST_MODE = {TEST_MODE}, NOTIFY_FRANK = {NOTIFY_FRANK}")
    
    # Run the main function with the appropriate mode
    main(test_mode=TEST_MODE, notify_frank=NOTIFY_FRANK)