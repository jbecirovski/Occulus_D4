# script pour tester le broadcasting côté client (caméras)

import socket
from src.other.functions import get_wifi_ip_address

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
local_ip = get_wifi_ip_address().split('.')
broadcast_address = local_ip[0] + '.' + local_ip[1] + '.' + local_ip[2] + '.255'
sock.bind((broadcast_address, 60000))
mess = sock.recv(1024)
print(mess.decode('utf-8'))


