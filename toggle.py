import socket

def main():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('127.0.0.1', 54123))
        s.send(b'SHOW')
        s.close()
    except (ConnectionRefusedError, OSError):
        print("ContextFlow daemon is not running.")

if __name__ == "__main__":
    main()