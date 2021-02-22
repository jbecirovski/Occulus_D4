# script pour tester la communication Wi-Fi du récepteur

import socket

# to get local IP address of WiFi connection
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
localIP = s.getsockname()[0]
print(localIP)
s.close()

HOST = ['192.168.0.101']  # à modifier pour correspondre aux IPs des cameras
PORT = 8000

skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
skt.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# TODO À voir si ça affecte les performances lors de l'envoi de gros fichiers (images)
# bind a port so the host always use the same port(to avoid creating too many different ports)
skt.bind((localIP, 61515))

# connect the socket to the host
skt.connect((HOST[0], PORT))
skt.sendall(b"Hello, world")
data = skt.recv(1024)

data = data.decode('utf-8')
print("Received: ", data)

skt.shutdown(socket.SHUT_RDWR)
skt.close()
