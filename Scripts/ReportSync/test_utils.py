"""
Test utilities module for the ReportSync package.
Contains functions for testing the report sync functionality.
"""

import os
import glob
from datetime import datetime


def test_modify_destination_file(destination_dir):
    """
    Test method to modify a file in the destination directory.
    This ensures we have a legitimate changed file for testing Git change detection
    without altering the source files.
    
    Args:
        destination_dir: The destination directory containing copied report files
        
    Returns:
        tuple: (bool, str) - Success status and path of the modified file or error message
    """
    # Look for StockTake.mrt in the destination directory and its subdirectories
    search_pattern = os.path.join(destination_dir, "**", "StockTake.mrt")
    stock_take_files = list(glob.glob(search_pattern, recursive=True))
    
    if not stock_take_files:
        return False, "StockTake.mrt file not found in the destination directory"
    
    # Use the first found file
    target_file = stock_take_files[0]
    
    try:
        # Read the file content as text to preserve line endings
        with open(target_file, 'r', encoding='utf-8', newline='') as file:
            content = file.read()
        
        # Generate a timestamp
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        
        # Determine the line ending style used in the file
        if '\r\n' in content:
            line_ending = '\r\n'  # Windows style
        else:
            line_ending = '\n'    # Unix style
        
        # Add a small change at the end of the file
        if not content.endswith(line_ending):
            modified_content = content + line_ending
        else:
            modified_content = content
        
        modified_content += f"<!-- Test change {timestamp} -->{line_ending}"
        
        # Write the modified content back to the file with the same line endings
        with open(target_file, 'w', encoding='utf-8', newline='') as file:
            file.write(modified_content)
        
        return True, f"Modified destination file {target_file}"
    
    except Exception as e:
        return False, f"Error modifying file: {str(e)}" 