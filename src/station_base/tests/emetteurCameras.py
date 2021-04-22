#!/usr/bin/python
# -*- coding: utf-8 -*-
# script pour tester la communication Wi-Fi de l"emetteur

import socket

# to get local IP address of WiFi connection
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
localIP = s.getsockname()[0]
s.close()

# create socket for communication (BLOCKING FOR NOW)
skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
skt.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# bind the address and port for communication
skt.bind((localIP, 8000))

# make socket listen for incoming connections
skt.listen()

while True:
    # accept connections to this specific address and port
    connection, address = skt.accept()
    with connection:
        print("Connexion établie par: ", address[0], "sur le socket du récepteur ", address[1])
        data = connection.recv(1024)
        if data == b"Hello, world":
            data = b"Hello world, my name is dad!"
        elif data == b"Movie":
            data = b"My favorite movie is Interstellar"
        elif data == b"Music":
            data = b"I've been playing piano for the past 12 years"
        else:
            break
        connection.sendall(data)
