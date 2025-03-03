import socket
import os

# Define host IP and port (Change IP to the host machine's IP)
HOST_IP = "192.168.140.179"  # Replace with host machine's actual IP
PORT = 5005
DOWNLOAD_FOLDER = "Downloads"  # Folder where downloaded files will be saved

# Create download folder if not exists
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

def request_file_list(client_socket):
    """Request and display a list of files from the host."""
    client_socket.sendall(b"LIST")
    files = client_socket.recv(4096).decode()
    print("\nAvailable Files:\n", files)

def download_file(client_socket, filename):
    """Request a file from the host and save it locally."""
    client_socket.sendall(f"GET {filename}".encode())
    
    response = client_socket.recv(1024)
    if response == b"ERROR: File not found!":
        print("❌ File not found on the host!")
        return
    
    file_path = os.path.join(DOWNLOAD_FOLDER, filename)
    with open(file_path, "wb") as f:
        while True:
            data = client_socket.recv(1024)
            if data.endswith(b"EOF"):  # Check if it's the end of the file
                f.write(data[:-3])  # Remove EOF marker
                break
            f.write(data)
    
    print(f"✅ File '{filename}' downloaded successfully to {file_path}!")

# Connect to the host
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST_IP, PORT))

print("✅ Connected to the host. Type 'LIST' to see files or 'GET <filename>' to download.")

while True:
    command = input("Enter command: ").strip()
    
    if command.upper() == "LIST":
        request_file_list(client)
    
    elif command.upper().startswith("GET "):
        filename = command[4:].strip()
        download_file(client, filename)
    
    elif command.upper() == "EXIT":
        break

client.close()
