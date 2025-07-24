"""
Notifications module for the ReportSync package.
Contains functions for sending notifications.
"""

import os
import json
import requests


def send_slack_notification(message, test_mode=False, notify_frank=False):
    """
    Send a simple notification to Slack.
    
    Args:
        message: The message to send
        test_mode: If True, only sends to Mike's webhook
        notify_frank: If True, sends to Frank's webhook (when not in test mode)
        
    Returns:
        bool: True if the message was sent successfully, False otherwise
    """
    # Mike's Slack webhook URL (always used)
    mike_webhook_url = "https://hooks.slack.com/services/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"
    
    # Frank's Slack webhook URL (only used when not in test mode AND notify_frank is True)
    frank_webhook_url = "https://hooks.slack.com/services/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"
    
    success = True
    
    # Send to Mike's webhook
    try:
        payload = {
            "text": message
        }
        
        response = requests.post(
            mike_webhook_url,
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print(f"Slack notification sent to Mike's webhook")
        else:
            print(f"Failed to send Slack notification to Mike's webhook. Status code: {response.status_code}")
            success = False
            
    except Exception as e:
        print(f"Error sending Slack notification to Mike's webhook: {str(e)}")
        success = False
    
    # Send to Frank's webhook if not in test mode AND notify_frank is True
    if not test_mode and notify_frank:
        try:
            payload = {
                "text": message
            }
            
            response = requests.post(
                frank_webhook_url,
                data=json.dumps(payload),
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                print(f"Slack notification sent to Frank's webhook")
            else:
                print(f"Failed to send Slack notification to Frank's webhook. Status code: {response.status_code}")
                success = False
                
        except Exception as e:
            print(f"Error sending Slack notification to Frank's webhook: {str(e)}")
            success = False
    
    return success


def format_changed_files_for_slack(changed_files):
    """
    Format the list of changed files for Slack notification.
    
    Args:
        changed_files: List of tuples (status, file_path)
        
    Returns:
        str: Formatted message with file names and their status
    """
    if not changed_files:
        return "No files changed"
    
    # Format each file as "filename (status)"
    formatted_files = []
    for status, file_path in changed_files:
        # Extract just the filename from the path
        filename = os.path.basename(file_path)
        
        # Skip empty filenames
        if not filename:
            continue
        
        # Use short status indicators
        status_indicator = ""
        if status == "M":
            status_indicator = "(M)"  # Modified
        elif status == "A":
            status_indicator = "(A)"  # Added
        elif status == "D":
            status_indicator = "(D)"  # Deleted
        elif status == "R":
            status_indicator = "(R)"  # Renamed
        elif status == "C":
            status_indicator = "(C)"  # Copied
        elif status == "??":
            status_indicator = "(U)"  # Untracked/Unknown
        else:
            status_indicator = f"({status})"
        
        formatted_files.append(f"• {filename} {status_indicator}")
    
    # Join all formatted files with newlines
    return "\n".join(formatted_files) 