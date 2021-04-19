# script secondaire pour la gestion du broadcasting

import socket

# on définit les paramètres pour la communication socket
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
local_ip = s.getsockname()[0]
s.close()

# déclaration du port pour le broadcasting
BROADCAST_PORT = 12345

# création du socket pour le broadcasting
udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# on vient binder le socket
udp_sock.bind(("255.255.255.255", BROADCAST_PORT))

# on regarde si on ne reçoit pas un paquet UDP de broadcast
while True:
    data, address = udp_sock.recvfrom(1024)
    if data:
        print("Message: ", data.decode('utf-8'))
        print(address)
        print("---------------")
        if data.decode('utf_8') == "requesting_broadcast":
            udp_sock.sendto(local_ip.encode('utf-8'), (address[0], address[1]))
            print(f"Sending back data to {address[0]}, {address[1]}")
            print("---------------")
