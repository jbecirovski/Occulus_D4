# script pour tester la communication Wi-Fi du récepteur

import socket
from src.other.functions import get_wifi_ip_address

# to get local IP address of WiFi connection
localIP = get_wifi_ip_address()
# TODO remove print
print(localIP)

# TODO change to the IPs of the cameras
HOST = ['192.168.50.160', '192.168.50.161']  # à modifier pour correspondre aux IPs des cameras
PORT = 8000

skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# TODO À voir si ça affecte les performances lors de l'envoi de gros fichiers (images)
# bind a port so the host always use the same port(to avoid creating too many different ports)
skt.bind((localIP, 61515))

# connect the socket to the host
skt.connect((HOST[0], PORT))
skt.sendall(b"Music")
data = skt.recv(1024)

data = data.decode('utf-8')
print("Received", data)

skt.shutdown(socket.SHUT_RDWR)
skt.close()
