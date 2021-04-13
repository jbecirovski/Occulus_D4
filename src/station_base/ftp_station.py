# script pour la gestion du serveur FTP du côté de la station

import os
import src.other.functions

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

# on vient chercher l'adresse IP locale
local_ip = src.other.functions.get_wifi_ip_address()

# on vient commencé le serveur FTP
authorizer = DummyAuthorizer()
authorizer.add_user("user", "12345", os.getcwd(), perm="elradfmw")

handler = FTPHandler
handler.authorizer = authorizer

# on envoie un message au client lors de la connection
handler.banner = "Hello from FTP server!"

server = FTPServer((local_ip, 2121), handler)
server.serve_forever()
