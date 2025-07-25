import sys
import subprocess

def check_and_install_packages():
    """Check for required packages and install if missing."""
    required_packages = {
        'mysqlclient': 'mysqlclient',  # This provides MySQLdb
        'python-dotenv': 'python-dotenv'
    }
    
    for import_name, package_name in required_packages.items():
        try:
            if import_name == 'mysqlclient':  # Special case since we import as MySQLdb
                __import__('MySQLdb')
            else:
                __import__(import_name)
        except ImportError:
            print(f"Package {package_name} not found. Installing...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
                print(f"Successfully installed {package_name}")
            except subprocess.CalledProcessError as e:
                print(f"Failed to install {package_name}. Error: {e}")
                sys.exit(1)

# Install required packages
check_and_install_packages()

# Now import the required packages
import os
import time
import re 
import argparse
from dotenv import load_dotenv
import MySQLdb
import msvcrt

# Load environment variables
load_dotenv()

# Rest of your original script starts here - manual file paths for standalone use 
RESTORE_FILE = r'C:\Temp\Backups\test-20250725_173620.sql'
# RESTORE_FILE = r'C:\Temp\Backups\prod-20250725_131448.sql'
TESTING = True  # Skip prompts for testing

# Parse command line arguments
def parse_arguments():
    parser = argparse.ArgumentParser(description='MySQL Database Restore Tool')
    parser.add_argument('--host', help='MySQL host (default: from MYSQL_LOCAL_HOST env var)')
    parser.add_argument('--port', type=int, help='MySQL port (default: from MYSQL_LOCAL_PORT env var or 3306)')
    parser.add_argument('--user', help='MySQL username (default: from MYSQL_LOCAL_USER env var)')
    parser.add_argument('--password', help='MySQL password (default: from MYSQL_LOCAL_PASSWORD env var)')
    parser.add_argument('--file', help='Backup file path to restore (required)')
    parser.add_argument('--auto-confirm', action='store_true', help='Skip confirmation prompt')
    parser.add_argument('--mysql-path', help='Path to the mysql command-line executable.')
    return parser.parse_args()

# Parse arguments
args = parse_arguments()

# Configuration with command line argument fallbacks
config = {
    'host': args.host or os.getenv('MYSQL_LOCAL_HOST', 'localhost'),
    'port': args.port or int(os.getenv('MYSQL_LOCAL_PORT', 3306)),
    'user': args.user or os.getenv('MYSQL_LOCAL_USER'),
    'password': args.password or os.getenv('MYSQL_LOCAL_PASSWORD'),
    'charset': 'utf8mb4',
    'use_unicode': True,
}

# Override with command line argument if provided
if args.file:
    RESTORE_FILE = args.file

# Validate restore file exists
if not os.path.exists(RESTORE_FILE):
    print(f"Error: Restore file not found: {RESTORE_FILE}")
    sys.exit(1)

# The rest of your original functions and code remain exactly the same
def print_config_and_prompt():
    print("Current configuration:")
    print(f"Host: {config['host']}")
    print(f"Port: {config['port']}")
    print(f"User: {config['user']}")
    print(f"Password: {'*' * len(config['password']) if config['password'] else 'None'}")
    print(f"Restore file: {RESTORE_FILE}")
    
    # Skip prompt if auto-confirm is set or if in testing mode
    if args.auto_confirm or TESTING:
        if TESTING:
            print("\nTesting mode enabled. Auto-confirming...")
        else:  # auto-confirm was used
            print("\nAuto-confirm enabled. Proceeding with restore...")
        return True
    
    while True:
        response = input("\nDo you want to continue with the restore? (yes/no): ").lower()
        if response in ['yes', 'y']:
            return True
        elif response in ['no', 'n']:
            return False
        else:
            print("Please enter 'yes' or 'no'.")

def restore_backup():
    """
    Parses the SQL file statement by statement, executes it, and waits for
    user confirmation before proceeding to the next statement.
    """
    print(f"\nExecuting statements from: {RESTORE_FILE}")
    
    statement_count = 0
    start_time = time.time()
    current_statement = []
    connection = None
    
    try:
        # Establish a single, persistent database connection
        print("Connecting to database...")
        connection = MySQLdb.connect(**config)
        cursor = connection.cursor()
        print("Connection successful.")

        with open(RESTORE_FILE, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                stripped_line = line.strip()
                # Skip empty lines and single-line block comments
                if not stripped_line or (stripped_line.startswith('/*') and stripped_line.endswith('*/;')):
                    continue
                
                current_statement.append(line)
                
                # A simple check: if the trimmed line ends with ';', we
                # consider the statement complete.
                if stripped_line.endswith(';'):
                    full_statement = ''.join(current_statement)
                    
                    statement_count += 1
                    print(f"\n--- Statement {statement_count} ---")
                    sys.stdout.write(full_statement)
                    sys.stdout.flush()

                    # Execute the statement
                    try:
                        print("\n\nExecuting statement...")
                        cursor.execute(full_statement)
                        connection.commit()
                        print("Statement executed successfully.")
                    except MySQLdb.Error as e:
                        print(f"\nERROR EXECUTING STATEMENT: {e}")
                        print("Skipping to next statement.")
                        try:
                            connection.rollback()
                        except MySQLdb.Error as rb_e:
                            print(f"Could not rollback: {rb_e}")
                    
                    print("\nPress any key to continue...")
                    msvcrt.getch()

                    # Reset for the next statement
                    current_statement = []
        
        elapsed_time = time.time() - start_time
        print(f"\n--- End of file ---")
        
        # Print any remaining content in the buffer
        if current_statement:
            print("\n--- Remaining partial statement (not executed) ---")
            sys.stdout.write(''.join(current_statement))

        print(f"\nSuccessfully processed {statement_count} statements in {elapsed_time:.2f} seconds.")

    except FileNotFoundError:
        print(f"\nError: Restore file not found: {RESTORE_FILE}")
        sys.exit(1)
    except MySQLdb.Error as e:
        print(f"\nA critical database error occurred: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        sys.exit(1)
    finally:
        if connection:
            connection.close()
            print("\nDatabase connection closed.")


if __name__ == "__main__":
    if print_config_and_prompt():
        restore_backup()
    else:
        print("Operation aborted.")