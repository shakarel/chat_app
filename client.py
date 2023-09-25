import socket
import threading
import sys


class ChatClient:
    def __init__(self, server_ip, server_port):
        self.server_ip = server_ip
        self.server_port = server_port

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self.client.connect((self.server_ip, self.server_port))
            self.nickname = self.get_nickname()
            self.client.send(self.nickname.encode("utf-8"))

            receive_thread = threading.Thread(target=self.receive_messages)
            send_thread = threading.Thread(target=self.send_messages)

            receive_thread.start()
            send_thread.start()
        except Exception as e:
            print(f"Error connecting to the server: {str(e)}")
            sys.exit(1)

    @staticmethod
    def get_nickname():
        while True:
            nickname = input("Choose a nickname: ")
            if nickname.strip():
                return nickname
            else:
                print("Nickname cannot be empty. Please try again.")

    def receive_messages(self):
        while True:
            try:
                message = self.client.recv(1024).decode("utf-8")
                if not message:
                    print("Disconnected from the server.")
                    self.client.close()
                    sys.exit()
                else:
                    print(message)
            except Exception as e:
                print(f"Error receiving message from the server: {str(e)}")
                self.client.close()
                sys.exit()

    def send_messages(self):
        while True:
            message = input("")
            if message.strip():
                try:
                    self.client.send(message.encode("utf-8"))
                except Exception as e:
                    print(f"Error sending message to the server: {str(e)}")
                    self.client.close()
                    sys.exit()


if __name__ == "__main__":
    SERVER_IP = "127.0.0.1"
    SERVER_PORT = 12345
    client = ChatClient(SERVER_IP, SERVER_PORT)
