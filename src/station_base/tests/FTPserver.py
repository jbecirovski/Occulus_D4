# exemple de base pour un serveur FTP
# possibilité de serveur threadé, gérer les vitesses read/write
import os

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

authorizer = DummyAuthorizer()
authorizer.add_user("user", "12345", os.getcwd(), perm="elradfmw")

handler = FTPHandler
handler.authorizer = authorizer

# on envoie un message au client lors de la connection
handler.banner = "Helle from FTP server!"

server = FTPServer(("127.0.0.1", 2121), handler)
server.serve_forever()
