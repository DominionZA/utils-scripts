import paramiko
import time
from datetime import datetime
import os
from dotenv import load_dotenv

def run_ssh_command(ssh, command):
    stdin, stdout, stderr = ssh.exec_command(command)
    output = stdout.read().decode('utf-8').strip()
    error = stderr.read().decode('utf-8').strip()
    if error and "Error" in error:
        print(f"Command error: {error}")
    return output, error

def ensure_directory_exists(ssh, path):
    _, err = run_ssh_command(ssh, f"mkdir -p {path}")
    if err and "Error" in err:
        raise Exception(f"Error creating directory {path}: {err}")
    print(f"Ensured directory exists: {path}")

def remove_existing_backup(ssh, backup_path):
    print(f"Checking for existing backup at {backup_path}")
    out, err = run_ssh_command(ssh, f"[ -d {backup_path} ] && echo 'exists'")
    if out == 'exists':
        print(f"Removing existing backup at {backup_path}")
        _, err = run_ssh_command(ssh, f"rm -rf {backup_path}")
        if err and "Error" in err:
            raise Exception(f"Error removing existing backup: {err}")
        print("Existing backup removed successfully")
    else:
        print("No existing backup found")

def get_directory_size(ssh, path):
    out, _ = run_ssh_command(ssh, f"du -s {path} | cut -f1")
    return int(out) if out.isdigit() else 0

def show_progress(ssh, source_size, backup_path):
    print("\nBackup progress:")
    start_time = time.time()
    last_size = 0
    no_change_count = 0
    while True:
        current_size = get_directory_size(ssh, backup_path)
        progress = min(current_size / source_size * 100, 99.9)  # Cap at 99.9% until rsync finishes
        elapsed_time = time.time() - start_time
        print(f"\r[{'#' * int(progress / 2)}{' ' * (50 - int(progress / 2))}] {progress:.1f}% - Elapsed time: {elapsed_time:.0f}s", end='', flush=True)
        
        if current_size == last_size:
            no_change_count += 1
        else:
            no_change_count = 0
        
        if no_change_count >= 10:  # If size hasn't changed for 10 iterations, assume it's complete
            break
        
        last_size = current_size
        time.sleep(1)
    
    print(f"\r[{'#' * 50}] 100.0% - Elapsed time: {time.time() - start_time:.0f}s")
    print("Backup completed!")

def main():
    hostname = os.getenv('UNRAID_HOST')
    username = os.getenv('UNRAID_USER')
    password = os.getenv('UNRAID_PASSWORD')

    backup_dir = os.getenv('UNRAID_BACKUPS') + '/mysql'
    mysql_dir = os.getenv('UNRAID_APPDATA_ROOT') + '/mysql'    

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        print("Connecting to Unraid server...")
        ssh.connect(hostname, username=username, password=password)
        print("Connected to Unraid server successfully.")

        backup_name = datetime.now().strftime("%Y%m%d_%H%M%S")
        print(f"Using backup name: {backup_name}")

        ensure_directory_exists(ssh, backup_dir)

        print("Stopping MySQL container...")
        out, err = run_ssh_command(ssh, "docker stop MySQL")
        if err and "Error" in err:
            raise Exception(f"Error stopping MySQL container: {err}")
        print("MySQL container stopped.")

        backup_path = f"{backup_dir}/{backup_name}"
        remove_existing_backup(ssh, backup_path)

        print("Calculating source directory size...")
        source_size = get_directory_size(ssh, mysql_dir)
        print(f"Source size: {source_size} KB")

        print(f"Starting backup to {backup_path}...")
        rsync_command = f"rsync -av --delete {mysql_dir}/ {backup_path}"
        ssh.exec_command(rsync_command)
        
        show_progress(ssh, source_size, backup_path)

        print("Starting MySQL container...")
        out, err = run_ssh_command(ssh, "docker start MySQL")
        if err and "Error" in err:
            raise Exception(f"Error starting MySQL container: {err}")
        print("MySQL container started.")

        out, _ = run_ssh_command(ssh, f"du -sh {backup_path}")
        print(f"Final backup size: {out}")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

    finally:
        if ssh:
            ssh.close()
            print("SSH connection closed.")

if __name__ == "__main__":
    main()