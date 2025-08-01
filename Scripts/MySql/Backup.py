import sys
import subprocess

# Configuration variable - set to True for production backup, False for test backup
isProd = True

def install_base_packages():
    """Install the base packages needed for package management."""
    try:
        import setuptools
    except ImportError:
        print("Installing setuptools...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "setuptools"])
        print("Successfully installed setuptools")

# Install base packages first
install_base_packages()

# Now we can safely import pkg_resources and other modules
import pkg_resources
import os
import datetime
import threading
import time
from importlib import util

def check_and_install_packages():
    """Check for required packages and install if missing."""
    required_packages = {
        'mysql-connector': 'mysql-connector-python',
        'dotenv': 'python-dotenv'
    }
    
    for import_name, package_name in required_packages.items():
        try:
            __import__(import_name)
        except ImportError:
            print(f"Package {package_name} not found. Installing...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
                print(f"Successfully installed {package_name}")
            except subprocess.CalledProcessError as e:
                print(f"Failed to install {package_name}. Error: {e}")
                sys.exit(1)

# Check and install required packages
check_and_install_packages()

# Now import the required packages
import mysql.connector
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Determine environment based on isProd setting
if isProd:
    environment = 'PROD'
else:
    environment = 'TEST'

# Connection details from environment variables
config = {
    'host': os.getenv(f'MYSQL_{environment}_HOST'),
    'port': int(os.getenv(f'MYSQL_{environment}_PORT', 3306)),
    'user': os.getenv(f'MYSQL_{environment}_USER'),
    'password': os.getenv(f'MYSQL_{environment}_PASSWORD')
}

# Backup directory
backup_dir = os.getenv('BACKUP_DIR', r'C:\Temp\Backups')
os.makedirs(backup_dir, exist_ok=True)

# Generate backup filename
timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
backup_file = os.path.join(backup_dir, f'{environment.lower()}-{timestamp}.sql.gz')

# Path to mysqldump from environment variable
MYSQL_DUMP_PATH = os.getenv('MYSQL_DUMP_PATH', r"C:\Program Files\MySQL\MySQL Workbench 8.0 CE\mysqldump.exe")

def display_configuration():
    """Display the current configuration being used for the backup."""
    print(f"=== Backup Configuration ({environment}) ===")
    print(f"Host: {config['host']}")
    print(f"Port: {config['port']}")
    print(f"User: {config['user']}")
    print(f"Password: {'*' * len(config['password']) if config['password'] else 'None'}")
    print(f"Backup file: {backup_file}")
    print(f"MySQL dump path: {MYSQL_DUMP_PATH}")
    print("=" * 50)

# Function to get total table count
def get_total_table_count():
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema NOT IN ('information_schema', 'mysql', 'performance_schema', 'sys') AND TABLE_TYPE = 'BASE TABLE'")
    total_tables = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return total_tables

# Function to show progress
def show_progress(total_tables):
    start_time = time.time()
    while not backup_complete.is_set():
        if os.path.exists(backup_file):
            with open(backup_file, 'rb') as f:
                current_tables = f.read().count(b'CREATE TABLE')
            progress = min(float(current_tables) / float(total_tables) * 100, 100)
            elapsed_time = int(time.time() - start_time)
            hours, remainder = divmod(elapsed_time, 3600)
            minutes, seconds = divmod(remainder, 60)
            time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            print(f"\rProgress: {progress:.2f}% ({current_tables}/{total_tables} tables) | Time elapsed: {time_str}", end="", flush=True)
        time.sleep(1)

# Function to execute custom SQL commands
def execute_custom_sql_commands():
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    try:
        # Custom SQL commands
        custom_commands = [
            # Add more commands as needed
        ]
        
        for command in custom_commands:
            print(f"Executing: {command}")
            cursor.execute(command)
            conn.commit()
        
        print("Custom SQL commands executed successfully")
    except mysql.connector.Error as err:
        print(f"Error executing custom SQL commands: {err}")
    finally:
        cursor.close()
        conn.close()

# Main execution
if __name__ == "__main__":
    # Display current configuration
    display_configuration()
    
    # Check if mysqldump exists
    if not os.path.exists(MYSQL_DUMP_PATH):
        print(f"Error: mysqldump not found at {MYSQL_DUMP_PATH}")
        print("Please install MySQL and set the correct path in the MYSQL_DUMP_PATH environment variable")
        sys.exit(1)

    # Execute custom SQL commands
    execute_custom_sql_commands()
 
    # Get total table count
    total_tables = get_total_table_count()

    print(f"Total tables to backup: {total_tables}")

    # Flag to signal backup completion
    backup_complete = threading.Event()

    # Start progress thread
    progress_thread = threading.Thread(target=show_progress, args=(total_tables,))
    progress_thread.start()

    # Execute mysqldump for each database separately
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    cursor.execute("SHOW DATABASES")
    databases = [db[0] for db in cursor.fetchall() if db[0] not in ['information_schema', 'mysql', 'performance_schema', 'sys']]

    try:
        with open(backup_file, 'wb') as f:
            for db in databases:
                # Get only tables (not views) from this database
                cursor.execute(f"SELECT table_name FROM information_schema.tables WHERE table_schema = '{db}' AND table_type = 'BASE TABLE'")
                tables = [table[0] for table in cursor.fetchall()]
                
                # Exclude PingHistory table from aura_cloud_device database
                if db == 'aura_cloud_device' and 'PingHistory' in tables:
                    tables.remove('PingHistory')
                
                # Constructing mysqldump command for the current database with specific tables
                mysqldump_cmd = [
                    MYSQL_DUMP_PATH,
                    f'--host={config["host"]}',
                    f'--port={config["port"]}',
                    f'--user={config["user"]}',
                    f'--password={config["password"]}',
                    '--single-transaction',
                    '--quick',
                    '--lock-tables=false',
                    '--set-gtid-purged=OFF',
                    '--compress',
                    '--skip-triggers',      # Skip triggers
                    '--skip-routines',      # Skip stored procedures and functions
                    '--skip-events',        # Skip events
                    db,                     # Database name
                    '--tables'              # Tables flag
                ] + tables                  # Add specific table names

                # Run the mysqldump command for the current database
                subprocess.run(mysqldump_cmd, stdout=f, stderr=subprocess.PIPE, check=True)
        
        backup_complete.set()
        progress_thread.join()
        print(f"\nBackup completed successfully. File saved as: {backup_file}")
    except subprocess.CalledProcessError as e:
        backup_complete.set()
        progress_thread.join()
        print(f"\nBackup failed. Error: {e.stderr.decode()}")
    finally:
        cursor.close()
        conn.close()