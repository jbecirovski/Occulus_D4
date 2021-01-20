# script pour tester la communication Wi-Fi du récepteur

import socket

HOST = ['192.168.50.160', '192.168.50.161']  # à modifier pour correspondre aux IPs des cameras
PORT = 8000

skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# connect the socket to the host
skt.connect((HOST[0], PORT))
skt.sendall(b'Hello, world')
data = skt.recv(1024)

print('Received', repr(data))
