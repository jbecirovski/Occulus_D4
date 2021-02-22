# script pour tester le broadcasting côté client (station de base)

import socket
import time

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

# pour avoir l'addresse locale
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
local_ip = s.getsockname()[0]
s.close()

# déclaration du port pour le broadcast
BROADCAST_PORT = 12345

# on va créer le string avec l'adresse de broadcast
ip = local_ip.split(".")
broadcast_address = ip[0] + '.' + ip[1] + '.' + ip[2] + ".255"
print(broadcast_address)
message = "This is a broadcast from %s!" % local_ip

while True:
    sock.sendto(message.encode('utf_8'), ("255.255.255.255", BROADCAST_PORT))
    data, address = sock.recvfrom(1024)
    if data:
        print(data.decode('utf_8'))
    time.sleep(1)
