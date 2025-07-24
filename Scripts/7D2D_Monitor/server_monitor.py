# Server Configuration
SERVER = "45.134.108.117:27290"

import subprocess
import sys
import socket
import time
import re

def install_requirements():
    try:
        import a2s
    except ImportError:
        print("Installing required packages...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'python-a2s'])
        print("Requirements installed successfully!")

# Install requirements if needed
install_requirements()

import a2s

# Parse server address
SERVER_IP, SERVER_PORT = SERVER.split(':')
SERVER_ADDRESS = (SERVER_IP, int(SERVER_PORT))
TELNET_PORT = int(SERVER_PORT) + 1  # Telnet port is usually game port + 1

def get_game_time():
    try:
        print(f"Attempting to get game day via port {TELNET_PORT}...")
        # Create socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        
        # Connect to the server
        s.connect((SERVER_IP, TELNET_PORT))
        
        # Wait for initial response
        response = s.recv(4096).decode('utf-8')
        if "password" in response.lower():
            print("Server requires authentication")
            return
        
        # Send gettime command
        s.send(b"gettime\n")
        time.sleep(1)
        
        # Get response
        response = s.recv(4096).decode('utf-8')
        
        # Look for day information
        day_match = re.search(r"Day\s+(\d+),", response)
        if day_match:
            print(f"Current Game Day: {day_match.group(1)}")
        else:
            print("Could not get game day information")
            
        s.close()
        
    except ConnectionRefusedError:
        print("Server's telnet port is not accessible")
    except socket.timeout:
        print("Connection timed out while getting game day")
    except Exception as e:
        print(f"Error getting game day: {str(e)}")
    print()

def get_server_info():
    try:
        print(f"Attempting to connect to server {SERVER}...")
        # Get server info with timeout
        info = a2s.info(SERVER_ADDRESS, timeout=5.0)
        
        # Print basic server information
        print("Server Info:")
        print(f"Server Name: {info.server_name}")
        print(f"Map: {info.map_name}")
        print(f"Player Count: {info.player_count}/{info.max_players}")
        
    except socket.timeout:
        print("Error: Connection timed out")
    except ConnectionRefusedError:
        print("Error: Connection refused - server might be offline")
    except Exception as e:
        print(f"Error connecting to server: {str(e)}")
    
if __name__ == "__main__":
    get_server_info()
    get_game_time() 