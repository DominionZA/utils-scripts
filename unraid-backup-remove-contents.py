import paramiko
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def run_ssh_command(ssh, command):
    stdin, stdout, stderr = ssh.exec_command(command)
    output = stdout.read().decode('utf-8').strip()
    error = stderr.read().decode('utf-8').strip()
    if error and "Error" in error:
        print(f"Command error: {error}")
    return output, error

def remove_backup_contents(ssh, backup_dir):
    print(f"Removing all contents from {backup_dir}")
    
    # Remove all contents including hidden files
    _, err = run_ssh_command(ssh, f"rm -rf {backup_dir}/* {backup_dir}/.*")
    if err and "rm: cannot remove '.' or '..': Is a directory" not in err:
        raise Exception(f"Error removing directory contents: {err}")
    
    print("All contents have been removed from the backup directory.")

def main():
    hostname = os.getenv('UNRAID_HOST')
    username = os.getenv('UNRAID_USER')
    password = os.getenv('UNRAID_PASSWORD')
    backup_dir = os.getenv('UNRAID_BACKUPS') + '/mysql'

    if not all([hostname, username, password, backup_dir]):
        raise ValueError("Missing environment variables. Please check your .env file.")

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        print("Connecting to Unraid server...")
        ssh.connect(hostname, username=username, password=password)
        print("Connected to Unraid server successfully.")

        remove_backup_contents(ssh, backup_dir)

    except Exception as e:
        print(f"An error occurred: {str(e)}")

    finally:
        if ssh:
            ssh.close()
            print("SSH connection closed.")

if __name__ == "__main__":
    main()