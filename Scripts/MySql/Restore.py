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

# Load environment variables
load_dotenv()

# Rest of your original script starts here - manual file paths for standalone use
RESTORE_FILE = r'C:\Temp\Backups\full_backup_20250724_102426.sql'
RESTORE_FILE = r'C:\Temp\Backups\prod-20250725_131448.sql'

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
    
    # Skip prompt if auto-confirm is set
    if args.auto_confirm:
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

def ensure_users_exist(cursor):
    users = ['frank', 'admin', 'aura']
    password = 'P@ssw0rd1'
    for user in users:
        cursor.execute(f"CREATE USER IF NOT EXISTS '{user}'@'%' IDENTIFIED BY '{password}';")
        cursor.execute(f"GRANT ALL PRIVILEGES ON *.* TO '{user}'@'%' WITH GRANT OPTION;")
    cursor.execute("FLUSH PRIVILEGES;")

def ensure_pinghistory_table_exists(cursor):
    """Check if aura_cloud_device.PingHistory table exists and create it if not."""
    try:
        # Check if the table exists
        cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'aura_cloud_device' AND table_name = 'PingHistory'")
        table_exists = cursor.fetchone()[0] > 0
        
        if not table_exists:
            print("\nPingHistory table not found. Creating table...")
            
            # Create the table
            create_table_sql = """
            CREATE TABLE aura_cloud_device.PingHistory (
              Id bigint UNSIGNED NOT NULL AUTO_INCREMENT,
              DeviceId int NOT NULL,
              Time datetime NOT NULL,
              PRIMARY KEY (Id)
            )
            ENGINE = INNODB,
            AUTO_INCREMENT = 11857178,
            AVG_ROW_LENGTH = 59,
            CHARACTER SET utf8mb4,
            COLLATE utf8mb4_0900_ai_ci
            """
            cursor.execute(create_table_sql)
            
            # Add the index
            cursor.execute("ALTER TABLE aura_cloud_device.PingHistory ADD INDEX IDX_PingHistory (DeviceId, Time)")
            
            # Add the foreign key constraint
            cursor.execute("ALTER TABLE aura_cloud_device.PingHistory ADD CONSTRAINT FK_PingHistory_DeviceId FOREIGN KEY (DeviceId) REFERENCES aura_cloud_device.Device (Id)")
            
            print("PingHistory table created successfully.")
        else:
            print("PingHistory table already exists.")
            
    except Exception as e:
        print(f"Warning: Error checking/creating PingHistory table: {e}")

def drop_non_system_databases(cursor):
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

def restore_backup():
    try:
        connection = MySQLdb.connect(**config)
        cursor = connection.cursor()
        
        # Drop all non-system databases
        try:
            drop_non_system_databases(cursor)
        except Exception as e:
            print(f"Warning: Error dropping databases: {e}")
            print("Continuing with restore...")
        
        # Ensure users exist with full DBA access
        try:
            ensure_users_exist(cursor)
        except Exception as e:
            print(f"Warning: Error creating users: {e}")
            print("Continuing with restore...")
        
        start_time = time.time()
        restored_tables = 0
        error_count = 0
        errors = []
        
        # Disable foreign key checks and autocommit
        try:
            cursor.execute("SET foreign_key_checks = 0")
            connection.autocommit(False)
        except Exception as e:
            print(f"Warning: Error setting MySQL options: {e}")
        
        print("Starting optimized file processing...")
        
        # Use larger buffer for faster I/O, process in bigger chunks
        CHUNK_SIZE = 8 * 1024 * 1024  # 8MB chunks
        current_statement = []
        
        try:
            with open(RESTORE_FILE, 'r', encoding='utf-8', errors='ignore', buffering=CHUNK_SIZE) as file:
                print("File opened with 8MB buffer. Beginning SQL execution...")
                
                buffer = ""
                processed_bytes = 0
                
                while True:
                    chunk = file.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    
                    buffer += chunk
                    processed_bytes += len(chunk)
                    
                    # Process complete lines from buffer
                    lines = buffer.split('\n')
                    buffer = lines[-1]  # Keep incomplete line for next iteration
                    
                    for line in lines[:-1]:  # Process all complete lines
                        line += '\n'  # Add back the newline
                        
                        if line.strip().endswith(';'):
                            current_statement.append(line)
                            full_statement = ''.join(current_statement)
                            try:
                                cursor.execute(full_statement)
                                if re.search(r'CREATE\s+TABLE', full_statement, re.IGNORECASE):
                                    restored_tables += 1
                                    elapsed_time = int(time.time() - start_time)
                                    hours, remainder = divmod(elapsed_time, 3600)
                                    minutes, seconds = divmod(remainder, 60)
                                    time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                                    print(f"\rTables restored: {restored_tables} | Time elapsed: {time_str}", end="", flush=True)
                            except MySQLdb.Error as e:
                                error_count += 1
                                errors.append(str(e))
                            except Exception as e:
                                error_count += 1
                                errors.append(str(e))
                            current_statement = []
                        else:
                            current_statement.append(line)
                
                # Process any remaining buffer content
                if buffer.strip():
                    if buffer.strip().endswith(';'):
                        current_statement.append(buffer)
                        full_statement = ''.join(current_statement)
                        try:
                            cursor.execute(full_statement)
                            if re.search(r'CREATE\s+TABLE', full_statement, re.IGNORECASE):
                                restored_tables += 1
                        except:
                            pass
        except Exception as e:
            print(f"\nWarning: Error reading restore file: {e}")
            print("Attempting to continue...")
        
        # Re-enable foreign key checks and commit
        try:
            cursor.execute("SET foreign_key_checks = 1")
            connection.commit()
        except Exception as e:
            print(f"\nWarning: Error finalizing restore: {e}")
        
        # Ensure PingHistory table exists after restore
        try:
            print()  # Add newline after progress display
            ensure_pinghistory_table_exists(cursor)
            connection.commit()
        except Exception as e:
            print(f"Warning: Error ensuring PingHistory table after restore: {e}")
        
        try:
            cursor.close()
            connection.close()
        except Exception as e:
            print(f"\nWarning: Error closing connection: {e}")
        
        print(f"\nDatabase restore completed from {RESTORE_FILE}")
        print(f"Tables restored: {restored_tables}")
        if error_count > 0:
            print(f"Total errors encountered (statements skipped): {error_count}")
            print("\nErrors encountered during restore:")
            for error in errors:
                print(f"  - {error}")
        else:
            print("No errors encountered during restore")
            
    except Exception as e:
        print(f"\nWarning: An error occurred during restore: {e}")
        print("The restore process has completed with potential issues.")
        # Don't exit or raise - just log and continue

if __name__ == "__main__":
    if print_config_and_prompt():
        restore_backup()
    else:
        print("Restore operation aborted.")