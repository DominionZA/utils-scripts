IS_PROD = True
SANITISE_DATABASE = True

# ---------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------
import sys
import subprocess
import os
import datetime
import threading
import time
import argparse
import mysql.connector
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Parse command line arguments first
def parse_arguments():
    parser = argparse.ArgumentParser(description='MySQL Database Backup Tool')
    parser.add_argument('--host', help='MySQL host (overrides environment variables)')
    parser.add_argument('--port', type=int, help='MySQL port (overrides environment variables)')
    parser.add_argument('--user', help='MySQL username (overrides environment variables)')
    parser.add_argument('--password', help='MySQL password (overrides environment variables)')
    parser.add_argument('--file', help='Full path for the backup file (overrides automatic naming)')
    return parser.parse_args()

args = parse_arguments()

# Determine environment based on IS_PROD setting
if IS_PROD:
    environment = 'PROD'
else:
    environment = 'TEST'

# Connection details from environment variables, overridden by args
config = {
    'host': args.host or os.getenv(f'MYSQL_{environment}_HOST'),
    'port': args.port or int(os.getenv(f'MYSQL_{environment}_PORT', 3306)),
    'user': args.user or os.getenv(f'MYSQL_{environment}_USER'),
    'password': args.password or os.getenv(f'MYSQL_{environment}_PASSWORD')
}

# Backup directory
backup_dir = os.getenv('BACKUP_DIR', r'C:\Temp\Backups')
os.makedirs(backup_dir, exist_ok=True)

# Generate backup filename, overridden by args
if args.file:
    backup_file = args.file
else:
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = os.path.join(backup_dir, f'{environment.lower()}-{timestamp}.sql')

backup_file = "C:\Temp\Backups\prod-20250725_205700.sql"

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
def show_progress(total_tables, backup_complete):
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
            output_line = f"Progress: {progress:.2f}% ({current_tables}/{total_tables} tables) | Time elapsed: {time_str}"
            # Add padding with spaces to ensure the previous line is fully overwritten
            print(f"\r{output_line:<100}", end="", flush=True)
        time.sleep(1)

# Function to execute custom SQL commands


# Function to setup MySQL Docker container
def setup_mysql_docker_container():
    """Setup MySQL 8 Docker container for testing restore."""
    container_name = "temp-mysql-8"
    mysql_port = "3307"  # Use different port to avoid conflicts
    mysql_password = "testpassword"
    
    print(f"\n=== Setting up MySQL Docker Container ({container_name}) ===")
    
    try:
        # Check if Docker is available
        print("Checking Docker availability...")
        result = subprocess.run(["docker", "--version"], 
                              capture_output=True, text=True, check=True)
        print(f"Docker found: {result.stdout.strip()}")
        
        # Check if container is already running
        print(f"Checking if {container_name} container is already running...")
        check_result = subprocess.run(["docker", "ps", "--filter", f"name={container_name}", "--format", "{{.Names}}"], 
                                    capture_output=True, text=True, check=False)
        
        if container_name in check_result.stdout:
            print(f"✅ Container {container_name} is already running!")
            return {
                'host': 'localhost',
                'port': mysql_port,
                'user': 'root',
                'password': mysql_password,
                'container_name': container_name
            }
        
        # Stop and remove existing container if it exists
        print(f"Stopping and removing existing {container_name} container...")
        subprocess.run(["docker", "stop", container_name], 
                      capture_output=True, check=False)
        subprocess.run(["docker", "rm", container_name], 
                      capture_output=True, check=False)
        
        # Start new MySQL container
        print(f"Starting new MySQL 8 container on port {mysql_port}...")
        docker_cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "-e", f"MYSQL_ROOT_PASSWORD={mysql_password}",
            "-e", "MYSQL_DATABASE=testdb",
            "-p", f"{mysql_port}:3306",
            "mysql:8.0"
        ]
        
        result = subprocess.run(docker_cmd, capture_output=True, text=True, check=True)
        container_id = result.stdout.strip()
        print(f"Container started with ID: {container_id[:12]}")
        
        # Wait for MySQL to be ready
        print("Waiting for MySQL to be ready...")
        max_attempts = 60
        for attempt in range(max_attempts):
            try:
                # Try to connect to the container
                test_cmd = [
                    "docker", "exec", container_name,
                    "mysql", "-uroot", f"-p{mysql_password}",
                    "-e", "SELECT 1"
                ]
                subprocess.run(test_cmd, capture_output=True, check=True)
                print(f"\nMySQL is ready! (took {attempt + 1} seconds)")
                break
            except subprocess.CalledProcessError:
                if attempt < max_attempts - 1:
                    print(f"\rWaiting... ({attempt + 1}/{max_attempts})", end="", flush=True)
                    time.sleep(1)
                else:
                    raise Exception("MySQL failed to start within 60 seconds")
        
        print(f"\n✅ MySQL container '{container_name}' is running and ready!")
        print(f"   Connection details:")
        print(f"   Host: localhost")
        print(f"   Port: {mysql_port}")
        print(f"   User: root")
        print(f"   Password: {mysql_password}")
        
        return {
            'host': 'localhost',
            'port': mysql_port,
            'user': 'root',
            'password': mysql_password,
            'container_name': container_name
        }
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error setting up Docker container: {e}")
        if e.stderr:
            print(f"Error details: {e.stderr}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

def compress_to_7z(filename):
    """
    Compress a file to .gz format using Python's built-in gzip.
    
    Args:
        filename (str): Path to the file to compress
        
    Returns:
        str: Path to the compressed .gz file if successful, None if failed
    """
    import gzip
    
    print(f"🗜️ Compressing {os.path.basename(filename)} to .gz...")
    compressed_file = f"{filename}.gz"
    
    try:
        with open(filename, 'rb') as f_in:
            with gzip.open(compressed_file, 'wb') as f_out:
                f_out.writelines(f_in)
        
        print(f"✅ Compressed file created: {os.path.basename(compressed_file)}")
        return compressed_file
        
    except Exception as e:
        print(f"❌ Compression failed: {e}")
        return None

def execute_backup():
    """Execute the main database backup process."""
    # Get total table count
    total_tables = get_total_table_count()
    print(f"Total tables to backup: {total_tables}")

    # Flag to signal backup completion
    backup_complete = threading.Event()

    # Start progress thread
    progress_thread = threading.Thread(target=show_progress, args=(total_tables, backup_complete))
    progress_thread.start()

    # Execute mysqldump for each database separately
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    cursor.execute("SHOW DATABASES")
    databases = [db[0] for db in cursor.fetchall() if db[0] not in ['information_schema', 'mysql', 'performance_schema', 'sys']]

    try:
        with open(backup_file, 'wb') as f:
            for db in databases:
                # Manually add CREATE DATABASE and USE statements for each database
                # This ensures schema is preserved and is version-agnostic.
                f.write(f"CREATE DATABASE IF NOT EXISTS `{db}`;\n".encode('utf-8'))
                f.write(f"USE `{db}`;\n".encode('utf-8'))
                f.flush()  # Force python's buffer to write to the file

                # Get only tables (not views) from this database
                cursor.execute(f"SELECT table_name FROM information_schema.tables WHERE table_schema = '{db}' AND table_type = 'BASE TABLE'")
                tables = [table[0] for table in cursor.fetchall()]
                
                # Exclude PingHistory table from aura_cloud_device database
                if db == 'aura_cloud_device' and 'PingHistory' in tables:
                    tables.remove('PingHistory')
                
                if not tables:
                    continue # Skip if there are no tables to back up in this database

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

                # Run the mysqldump command and append output to the file
                subprocess.run(mysqldump_cmd, stdout=f, stderr=subprocess.PIPE, check=True)
        
        backup_complete.set()
        progress_thread.join()
        print(f"\nBackup completed successfully. File saved as: {backup_file}")
        
    except subprocess.CalledProcessError as e:
        backup_complete.set()
        progress_thread.join()
        print(f"\nBackup failed. Error: {e.stderr.decode()}")
        raise
    finally:
        cursor.close()
        conn.close()

def restore_to_docker_container(container_info):
    """Restore backup to Docker container."""
    print(f"\n🚀 Restoring backup to container...")
    restore_cmd = [
        sys.executable, "Scripts/MySql/Restore.py",
        "--host", container_info['host'],
        "--port", container_info['port'],
        "--user", container_info['user'],
        "--password", container_info['password'],
        "--file", backup_file,  # Use the backup we just created
        "--auto-confirm"
    ]
    
    try:
        subprocess.run(restore_cmd, check=True, text=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Restore failed during sanitise workflow: {e.returncode}")
        sys.exit(1)

def execute_clean_data_script(container_info):
    """Execute CleanData.sql to sanitize the data."""
    print(f"\n🧹 Executing CleanData.sql to sanitize data...")
    clean_data_file = os.path.join(os.path.dirname(__file__), "CleanData.sql")
    
    mysql_path = os.getenv('MYSQL_EXE_PATH') or 'mysql'
    clean_cmd = [
        mysql_path,
        f"--host={container_info['host']}",
        f"--port={container_info['port']}",
        f"--user={container_info['user']}"
    ]
    
    env = os.environ.copy()
    env['MYSQL_PWD'] = container_info['password']
    
    try:
        with open(clean_data_file, 'r', encoding='utf-8', errors='ignore') as f:
            process = subprocess.run(
                clean_cmd,
                stdin=f,
                env=env,
                check=True,
                capture_output=True,
                text=True
            )
        print("✅ Data sanitization completed!")
    except FileNotFoundError:
        print(f"❌ Error: CleanData.sql not found at {clean_data_file}")
        return False
    except subprocess.CalledProcessError as e:
        print(f"❌ Data sanitization failed: {e.returncode}")
        if e.stderr:
            print(f"Error details: {e.stderr}")
        return False
    
    return True

def backup_cleaned_database(container_info):
    """Simple backup of the entire cleaned Docker container database."""
    # Generate cleaned backup filename
    base_name, extension = os.path.splitext(backup_file)
    cleaned_backup_file = f"{base_name}-cleaned{extension}"
    
    print(f"\n💾 Backing up cleaned database to {os.path.basename(cleaned_backup_file)}...")
    
    # Get non-system databases and use --databases switch for CREATE DATABASE statements
    conn = mysql.connector.connect(
        host=container_info['host'],
        port=int(container_info['port']),
        user=container_info['user'],
        password=container_info['password']
    )
    cursor = conn.cursor()
    cursor.execute("SHOW DATABASES")
    databases = [db[0] for db in cursor.fetchall() if db[0] not in ['information_schema', 'mysql', 'performance_schema', 'sys']]
    cursor.close()
    conn.close()

    # Simple mysqldump with --databases for all tables including PingHistory
    mysqldump_cmd = [
        MYSQL_DUMP_PATH,
        f'--host={container_info["host"]}',
        f'--port={container_info["port"]}',
        f'--user={container_info["user"]}',
        f'--password={container_info["password"]}',
        '--single-transaction',
        '--quick',
        '--lock-tables=false',
        '--set-gtid-purged=OFF',
        '--compress',
        '--skip-triggers',
        '--skip-routines',
        '--skip-events',
        '--databases'
    ] + databases

    try:
        with open(cleaned_backup_file, 'wb') as f:
            subprocess.run(mysqldump_cmd, stdout=f, stderr=subprocess.PIPE, check=True)
        print(f"✅ Cleaned backup completed: {cleaned_backup_file}")
        
        # Compress the backup file
        compressed_file = compress_to_7z(cleaned_backup_file)
        if compressed_file:
            print(f"✅ Final compressed backup: {compressed_file}")
        else:
            print(f"✅ Final backup: {cleaned_backup_file}")
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Cleaned backup failed: {e.returncode}")
        if e.stderr:
            print(f"Error details: {e.stderr.decode()}")
        sys.exit(1)
    


def sanitize_database():
    """Complete database sanitization workflow."""
    print("\n🧹 SANITISING: Setting up Docker container for restore testing...")
    
    # Setup Docker container (check if running, create if needed)
    container_info = setup_mysql_docker_container()
    
    # Check if backup file exists before trying to restore
    if not os.path.exists(backup_file):
        print(f"⚠️  Warning: Backup file not found: {backup_file}")
        print("Cannot restore to container - backup file missing")
        return
    
    # Restore the backup we just created to container
    restore_to_docker_container(container_info)
    
    # Execute CleanData.sql to sanitize the data
    if not execute_clean_data_script(container_info):
        print("❌ Sanitize workflow stopped due to CleanData.sql failure")
        return
    
    # Backup the cleaned database
    backup_cleaned_database(container_info)
    
    print("✅ Sanitise workflow completed!")

if __name__ == "__main__":
    # Display current configuration
    display_configuration()
    
    # Check if mysqldump exists
    if not os.path.exists(MYSQL_DUMP_PATH):
        print(f"Error: mysqldump not found at {MYSQL_DUMP_PATH}")
        print("Please install MySQL and set the correct path in the MYSQL_DUMP_PATH environment variable")
        sys.exit(1)

    # execute_backup()
    
    # Execute sanitization if requested
    if IS_PROD and SANITISE_DATABASE:
        sanitize_database()