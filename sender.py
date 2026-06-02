import socket
import os
import zipfile
import time

HOST = "0.0.0.0"
PORT = 5000
CHUNK = 4096

BACKUP_NAME = "full_backup.zip"

def zip_folder(folder_path, output_name):
    print("[+] Creating backup zip...")

    with zipfile.ZipFile(output_name, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    zipf.write(file_path, 
                               os.path.relpath(file_path, folder_path))
                except:
                    pass

    print("[+] Backup created:", output_name)


def send_file(conn, file_path):
    file_size = os.path.getsize(file_path)
    file_name = os.path.basename(file_path)

    # Send header
    conn.send(f"{file_name}|{file_size}".encode().ljust(1024))

    ack = conn.recv(1024).decode()

    offset = int(ack) if ack.isdigit() else 0

    sent = offset

    with open(file_path, "rb") as f:
        f.seek(offset)

        while True:
            data = f.read(CHUNK)
            if not data:
                break

            conn.send(data)
            sent += len(data)

            percent = (sent / file_size) * 100
            print(f"\rSending: {percent:.2f}%", end="")

    print("\n[+] Transfer Complete!")


def main():
    print("=== OFFLINE BACKUP SENDER ===")

    path = input("Enter folder path to backup (e.g. /storage/emulated/0): ")

    if not os.path.exists(path):
        print("Invalid path!")
        return

    zip_folder(path, BACKUP_NAME)

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(1)

    print(f"[+] Waiting for receiver on port {PORT}...")

    conn, addr = server.accept()
    print("[+] Connected:", addr)

    send_file(conn, BACKUP_NAME)

    conn.close()
    server.close()

    # optional cleanup
    os.remove(BACKUP_NAME)
    print("[+] Done!")

if __name__ == "__main__":
    main()
