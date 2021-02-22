#!/usr/bin/python
# -*- coding: utf-8 -*-
# script pour tester le broadcasting côté serveur (caméras)

import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM,)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# pour avoir l'adresse locale
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
local_ip = s.getsockname()[0]
s.close()

# déclaration du port pour le broadcast
BROADCAST_PORT = 12345

# on va binder le socket à l'addresse et port de broadcast
sock.bind(("255.255.255.255", BROADCAST_PORT))

while True:
    data, address = sock.recvfrom(1024)
    if data:
        print("Message: ", data.decode("utf-8"))
        print(address)
        print("---------------")
        sock.sendto(local_ip.encode('utf-8'), (address[0], address[1]))
