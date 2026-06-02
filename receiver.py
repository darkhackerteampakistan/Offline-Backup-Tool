import socket
import os

SERVER_IP = input("Enter sender IP (default 192.168.43.1): ").strip()
if SERVER_IP == "":
    SERVER_IP = "192.168.43.1"

PORT = 5000
CHUNK = 4096

SAVE_PATH = "/storage/emulated/0/Download"

def receive_file():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((SERVER_IP, PORT))

    print("[+] Connected to sender!")

    # Receive header
    header = client.recv(1024).decode().strip()
    file_name, file_size = header.split("|")
    file_size = int(file_size)

    print(f"[+] Receiving: {file_name} ({file_size} bytes)")

    full_path = os.path.join(SAVE_PATH, file_name)

    # Resume support
    offset = 0
    if os.path.exists(full_path):
        offset = os.path.getsize(full_path)

    client.send(str(offset).encode())

    received = offset

    with open(full_path, "ab") as f:
        while received < file_size:
            data = client.recv(CHUNK)
            if not data:
                break

            f.write(data)
            received += len(data)

            percent = (received / file_size) * 100
            print(f"\rReceiving: {percent:.2f}%", end="")

    print("\n[+] Backup received successfully!")
    print("[+] Saved at:", full_path)

    client.close()


if __name__ == "__main__":
    print("=== OFFLINE BACKUP RECEIVER ===")
    receive_file()
