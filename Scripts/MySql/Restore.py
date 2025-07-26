# Rest of your original script starts here - manual file paths for standalone use  
RESTORE_FILE = r'C:\Temp\Backups\test-20250725_173620.sql'
RESTORE_FILE = r'C:\Temp\Backups\prod-20250725_205700-cleaned.sql'
AUTO_CONFIRM = True  # Skip prompts for testing

# ---------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------
import sys
import subprocess
import msvcrt
import os
import time 
import argparse 
from dotenv import load_dotenv
import MySQLdb

# --- Cursor Control Functions ---
def hide_cursor():
    """Hides the console cursor using ANSI escape codes."""
    sys.stdout.write("\x1b[?25l")
    sys.stdout.flush()

def show_cursor():
    """Shows the console cursor using ANSI escape codes."""
    sys.stdout.write("\x1b[?25h")
    sys.stdout.flush()
# --------------------------------

# Load environment variables
load_dotenv()

# Parse command line arguments
def parse_arguments():
    parser = argparse.ArgumentParser(description='MySQL Database Restore Tool')
    parser.add_argument('--host', help='MySQL host (default: from MYSQL_LOCAL_HOST env var)')
    parser.add_argument('--port', type=int, help='MySQL port (default: from MYSQL_LOCAL_PORT env var or 3306)')
    parser.add_argument('--user', help='MySQL username (default: from MYSQL_LOCAL_USER env var)')
    parser.add_argument('--password', help='MySQL password (default: from MYSQL_LOCAL_PASSWORD env var)')
    parser.add_argument('--file', help='Backup file path to restore (required)')
    parser.add_argument('--auto-confirm', action='store_true', help='Skip confirmation prompt')
    return parser.parse_args()

# Parse arguments
args = parse_arguments()

# Override with command line argument if provided
if args.file:
    RESTORE_FILE = args.file

# Validate restore file exists
if not os.path.exists(RESTORE_FILE):
    print(f"⚠️  Warning: Restore file not found: {RESTORE_FILE}")
    print("Please check the file path and try again.")
    print("Restore operation cannot continue without a valid backup file.")
    exit()  # Exit gracefully

# Configuration with command line argument fallbacks
config = {
    'host': args.host or os.getenv('MYSQL_LOCAL_HOST', 'localhost'),
    'port': args.port or int(os.getenv('MYSQL_LOCAL_PORT', 3306)),
    'user': args.user or os.getenv('MYSQL_LOCAL_USER'),
    'password': args.password or os.getenv('MYSQL_LOCAL_PASSWORD'),
    'charset': 'utf8mb4',
    'use_unicode': True,
}

# The rest of your original functions and code remain exactly the same
def print_config_and_prompt():
    print("Current configuration:")
    print(f"Host: {config['host']}")
    print(f"Port: {config['port']}")
    print(f"User: {config['user']}")
    print(f"Password: {'*' * len(config['password']) if config['password'] else 'None'}")
    print(f"Restore file: {RESTORE_FILE}")
    
    # Skip prompt if auto-confirm is set or if in testing mode
    if args.auto_confirm or AUTO_CONFIRM:
        if AUTO_CONFIRM:
            print("\nAuto-confirm enabled. Proceeding with restore...")
        else:  # auto-confirm was used
            print("\nAuto-confirm enabled. Proceeding with restore...")
        return True
    
    while True:
        print("\nDo you want to continue with the restore? (y/n): ", end='', flush=True)
        key = msvcrt.getch().decode('utf-8').lower()
        print(key)  # Echo the key pressed
        if key == 'y':
            print("Yes - proceeding with restore...")
            return True
        elif key == 'n':
            print("No - aborting restore.")
            return False
        else:
            print("Please press 'y' for yes or 'n' for no.")

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
    Restores the database by first dropping all non-system databases and then
    executing the restore from the backup file using the high-performance
    mysql command-line utility.
    """
    connection = None
    try:
        # Step 1: Connect with Python to drop databases
        print("Connecting to database to clear existing data...")
        connection = MySQLdb.connect(**config)
        cursor = connection.cursor()
        drop_non_system_databases(cursor)
        cursor.close()
        connection.close()
        print("\nDatabase cleared. Proceeding with restore.")

        # Step 2: Use mysql.exe for the high-performance restore
        filename_only = os.path.basename(RESTORE_FILE)
        print(f"\nStarting database restore from {filename_only} to {config['host']}:{config['port']}")
        start_time = time.time()
        
        hide_cursor() # Hide cursor before the restore process starts

        mysql_path = os.getenv('MYSQL_EXE_PATH') or 'mysql'

        command = [
            mysql_path,
            f"--host={config['host']}",
            f"--port={config['port']}",
            f"--user={config['user']}",
            "--verbose", # Ask for verbose output to create a feedback loop
            "mysql"  # Connect to default 'mysql' db to resolve "No database selected"
        ]
        
        env = os.environ.copy()
        if config['password']:
            env['MYSQL_PWD'] = config['password']

        with open(RESTORE_FILE, 'r', encoding='utf-8', errors='ignore') as f:
            process = subprocess.Popen(
                command,
                stdin=f,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                text=True,
                encoding='utf-8',
                errors='ignore',
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
            )
            
            # Show a timer to indicate activity without printing the full log
            if process.stdout:
                while process.stdout.readline():
                    elapsed = int(time.time() - start_time)
                    minutes, seconds = divmod(elapsed, 60)
                    time_str = f"{minutes:02d}:{seconds:02d}"
                    sys.stdout.write(f'\rRestoring: {time_str}')
                    sys.stdout.flush()
            
            # Wait for the process to complete and capture any final error output
            stderr_output = process.stderr.read() if process.stderr else ""
            process.wait()

        # Overwrite the timer line with a final status message
        elapsed_time = int(time.time() - start_time)
        hours, remainder = divmod(elapsed_time, 3600)
        minutes, seconds = divmod(remainder, 60)
        time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

        if process.returncode == 0:
            # Add padding with spaces to ensure the previous line is fully overwritten
            print(f"\rDatabase restore completed successfully in {time_str}.          ")
            if stderr_output:
                print("Warnings from mysql client:")
                print(stderr_output)
        else:
            print(f"\nDatabase restore FAILED after {time_str}.")
            print(f"Return code: {process.returncode}")
            if stderr_output:
                print("Error details from mysql client:")
                print(stderr_output)
            sys.exit(1)

    except FileNotFoundError:
        print(f"\nError: `{mysql_path}` command not found.")
        print("Please ensure the MySQL command-line client is installed and in your system's PATH,")
        print("or set its full path in the MYSQL_EXE_PATH environment variable.")
        sys.exit(1)
    except MySQLdb.Error as e:
        print(f"\nAn error occurred during the database cleaning phase: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        sys.exit(1)
    finally:
        show_cursor() # Always show the cursor at the very end
        # This is for the python connection, which should be closed already,
        # but it's good practice to have it just in case of an early exit.
        if connection and connection.open:
            connection.close()
            print("\nDatabase connection closed.")


if __name__ == "__main__":
    if print_config_and_prompt():
        restore_backup()
    else:
        print("Operation aborted.")