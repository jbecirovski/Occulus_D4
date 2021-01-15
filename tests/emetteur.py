# script pour tester la communication Wi-Fi de l'emetteur

import socket
from other.functions import get_wifi_ip_address

# to get local IP address of WiFi connection
localIP = get_wifi_ip_address()
print(localIP)

# create socket for communication (BLOCKING FOR NOW)
skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# bind the address and port for communication
skt.bind((localIP, 8000))

# make socket listen for incoming connections
skt.listen()

# accept connections to this specific address and port
connection, address = skt.accept()

with connection:
    while True:
        print("Connexion établie par: ", address)
        data = connection.recv(1024)
        if not data:
            break
        connection.sendall(data)
