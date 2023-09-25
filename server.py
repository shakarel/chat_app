import socket
import threading
import logging
import datetime


class ChatServer:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.clients = []
        self.nicknames = {}

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.ip, self.port))
        self.server.listen()

        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s')  # some logging configurations

    def broadcast(self, message, sender=None):
        for client in self.clients:
            try:
                if sender is not None and client == sender:
                    continue
                client.send(message.encode("utf-8"))
            except Exception as e:
                logging.error(f"Error sending message to client: {str(e)}")

    def handle_client(self, client):
        try:
            nickname = self.nicknames[client]
            logging.info(f"Connected with {nickname} at {client.getpeername()}")

            while True:
                message = client.recv(1024).decode("utf-8")
                if not message:
                    break

                if message.startswith('/'):
                    self.handle_command(client, message)

                else:
                    formatted_message = f'{datetime.datetime.now().strftime("%H:%M:%S")} - {nickname}: {message}'
                    self.broadcast(formatted_message, sender=client)

        except (ConnectionResetError, OSError):
            logging.info(f"Client disconnected: {self.nicknames[client]}")

        except Exception as e:
            logging.error(f"Error receiving message from client: {str(e)}")

        finally:
            client.close()
            self.remove_client(client)

    def remove_client(self, client):
        if client in self.clients:
            nickname = self.nicknames.pop(client)
            self.clients.remove(client)
            self.broadcast(f"{nickname} left the chat")
            logging.info(f"{nickname} disconnected")

    def handle_command(self, client, command):
        parts = command.split()
        if parts[0] == '/help':
            help_message = "Available commands: /help, /list, /quit, /msg <user> <message>"
            client.send(help_message.encode("utf-8"))
        elif parts[0] == '/list':
            online_users = ", ".join(self.nicknames.values())
            client.send(f"Online users: {online_users}".encode("utf-8"))
        elif parts[0] == '/quit':
            client.send("Goodbye!".encode("utf-8"))
            client.close()
        elif parts[0] == '/msg' and len(parts) >= 3:
            recipient_name = parts[1]
            if recipient_name in self.nicknames.values():
                recipient = [client for client, name in self.nicknames.items() if name == recipient_name][0]
                message = ' '.join(parts[2:])
                formatted_message = (f'{datetime.datetime.now().strftime("%H:%M:%S")} - (Private) '
                                     f'{self.nicknames[client]}: {message}')
                recipient.send(formatted_message.encode("utf-8"))
            else:
                client.send("User not found.".encode("utf-8"))
        else:
            client.send("Invalid command. Type '/help' for a list of commands.".encode("utf-8"))

    def accept_clients(self):
        while True:
            try:
                client, address = self.server.accept()
                nickname = client.recv(1024).decode("utf-8").strip()

                if not nickname or nickname in self.nicknames.values():
                    client.send("Nickname already in use or empty. Please choose another.".encode("utf-8"))
                    client.close()
                    continue

                self.nicknames[client] = nickname
                self.clients.append(client)

                self.broadcast(f"{nickname} joined the chat")
                thread = threading.Thread(target=self.handle_client, args=(client,))
                thread.start()
            except Exception as e:
                logging.error(f"Error accepting client connection: {str(e)}")

    def start(self):
        logging.info("Server is up and running...")
        logging.info(f"Listening on {self.ip}:{self.port}")
        self.accept_clients()


if __name__ == "__main__":
    SERVER_IP = "127.0.0.1"
    SERVER_PORT = 12345
    server = ChatServer(SERVER_IP, SERVER_PORT)
    server.start()
