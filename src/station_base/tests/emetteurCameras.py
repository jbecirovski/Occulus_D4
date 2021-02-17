# script pour tester la communication Wi-Fi de l"emetteur

# TODO Regarder pour mettre le process en sleep lorsque pas actif (pendant qu"il n"y a aucune connexion)?
import socket
from src.station_base.other.functions import get_wifi_ip_address

# to get local IP address of WiFi connection
localIP = get_wifi_ip_address()
# TODO remove print
print(localIP)

# TODO Voir si on doit le garder en blocking si plusieurs cameras ou envoi des images
# create socket for communication (BLOCKING FOR NOW)
skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

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
