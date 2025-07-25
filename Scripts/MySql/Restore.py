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
import collections

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

def drop_non_system_databases(cursor):
    """Drops all non-system databases."""
    system_databases = ['mysql', 'information_schema', 'performance_schema', 'sys']
    
    # Disable foreign key checks
    cursor.execute("SET foreign_key_checks = 0;")
    
    cursor.execute("SHOW DATABASES;")
    databases = cursor.fetchall()
    for (database,) in databases:
        if database not in system_databases:
            print(f"Dropping database: {database}")
            cursor.execute(f"DROP DATABASE IF EXISTS `{database}`;")
    
    # Re-enable foreign key checks
    cursor.execute("SET foreign_key_checks = 1;")
    print("Finished dropping databases.")

def restore_backup():
    """
    Parses, prints, and executes each SQL statement, waiting for user
    confirmation before proceeding.
    """
    print(f"\nExecuting statements from: {RESTORE_FILE}")
    
    table_count = 0
    start_time = time.time()
    current_statement = []
    connection = None
    recent_lines = collections.deque(maxlen=200)
    
    try:
        # Establish a single, persistent database connection
        print("Connecting to database...")
        connection = MySQLdb.connect(**config)
        cursor = connection.cursor()
        print("Connection successful.")

        # Drop all non-system databases before restore
        print("\nDropping non-system databases...")
        drop_non_system_databases(cursor)

        try:
            print("\nDisabling foreign key checks for restore...")
            cursor.execute("SET foreign_key_checks = 0;")

            with open(RESTORE_FILE, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    recent_lines.append(line)
                    stripped_line = line.strip()
                    # Skip empty lines and whole-line comments
                    if not stripped_line or stripped_line.startswith('--') or stripped_line.startswith('#') or (stripped_line.startswith('/*') and stripped_line.endswith('*/;')):
                        continue
                    
                    current_statement.append(line)
                    
                    # Create a version of the line with inline comments removed
                    # for the sole purpose of checking for the semicolon.
                    line_for_check = stripped_line
                    if '#' in line_for_check:
                        line_for_check = line_for_check.split('#', 1)[0].strip()
                    if '--' in line_for_check:
                        line_for_check = line_for_check.split('--', 1)[0].strip()

                    # Check if the cleaned line ends with ';'.
                    if line_for_check.endswith(';'):
                        full_statement = ''.join(current_statement)
                        
                        # If the statement is just a semicolon or whitespace, skip it
                        if not full_statement.strip() or full_statement.strip() == ';':
                            current_statement = []
                            continue

                        # Check for CREATE TABLE to show progress
                        if re.search(r'\bCREATE\s+TABLE\b', full_statement, re.IGNORECASE):
                            table_count += 1
                            print(f"\rTables restored: {table_count}", end="", flush=True)

                        # Execute the statement
                        try:
                            cursor.execute(full_statement)
                            connection.commit()
                        except MySQLdb.Error as e:
                            # Print a newline to avoid overwriting the progress message
                            print()
                            print("\n--- LAST 200 LINES READ ---")
                            for recent_line in recent_lines:
                                sys.stdout.write(recent_line)
                            print("---------------------------")
                            print("\n--- FAILED SQL STATEMENT ---")
                            sys.stdout.write(full_statement)
                            sys.stdout.flush()
                            print(f"\n\n--- MYSQL ERROR ---\n{e}")
                            print("\nRestore aborted due to error.")
                            return # Exit the function, allowing 'finally' to clean up
                    
                    # Reset for the next statement
                    current_statement = []
            
            print() # Add a newline to move past the progress counter
            elapsed_time = time.time() - start_time
            print(f"\n--- End of file ---")
            
            # Print any remaining content in the buffer
            if current_statement:
                print("\n--- Remaining partial statement (not executed) ---")
                sys.stdout.write(''.join(current_statement))

            print(f"\nSuccessfully processed and restored {table_count} tables in {elapsed_time:.2f} seconds.")
        
        finally:
            print("\nRe-enabling foreign key checks...")
            cursor.execute("SET foreign_key_checks = 1;")
            connection.commit()

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