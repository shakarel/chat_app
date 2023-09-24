import socket
import threading
import sys
import datetime

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

    def get_nickname(self):
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
                elif message.startswith('/'):
                    self.handle_command(message)
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

    def handle_command(self, command):
        parts = command.split()
        if parts[0] == '/help':
            print("Available commands: /help, /quit, /list, /msg <user> <message>, /nick <new_nickname>")
        elif parts[0] == '/quit':
            self.client.send("/quit".encode("utf-8"))
            self.client.close()
            sys.exit()
        elif parts[0] == '/list':
            self.client.send("/list".encode("utf-8"))
        elif parts[0] == '/msg' and len(parts) >= 3:
            recipient = parts[1]
            message = ' '.join(parts[2:])
            self.client.send(f"/msg {recipient} {message}".encode("utf-8"))
        elif parts[0] == '/nick' and len(parts) == 2:
            new_nickname = parts[1]
            self.client.send(f"/nick {new_nickname}".encode("utf-8"))
            self.nickname = new_nickname
        else:
            print("Invalid command. Type '/help' for a list of commands.")

if __name__ == "__main__":
    SERVER_IP = "127.0.0.1"
    SERVER_PORT = 12345
    client = ChatClient(SERVER_IP, SERVER_PORT)
