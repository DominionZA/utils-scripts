"""
File operations module for the ReportSync package.
Contains functions for copying files and directories.
"""

import os
import shutil
import glob


def copy_files(source, destination):
    """
    Copy all .mrt files from source to destination.
    
    Args:
        source: Source directory
        destination: Destination directory
    """
    # Create destination directory if it doesn't exist
    os.makedirs(destination, exist_ok=True)
    
    # Find all .mrt files in source directory and its subdirectories
    for file_path in glob.glob(os.path.join(source, "**", "*.mrt"), recursive=True):
        # Copy the file to the destination
        shutil.copy2(file_path, destination)
        print(f"Copied: {file_path} -> {destination}")


def copy_files_with_categories(source, destination):
    """
    Copy files from source to destination, preserving category folders.
    
    Args:
        source: Source directory
        destination: Destination directory
    """
    # Get all folders in the source directory
    folders = [f for f in os.listdir(source) if os.path.isdir(os.path.join(source, f))]
    
    # Process each folder (category)
    for folder in folders:
        source_with_category = os.path.join(source, folder)
        destination_with_category = os.path.join(destination, folder)
        
        # Copy files from this category
        copy_files(source_with_category, destination_with_category) 