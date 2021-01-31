# script de définition des fonctions
import socket


# fonction pour trouver l'adresse ip locale
def get_wifi_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.shutdown(socket.SHUT_RDWR)
    s.close()
    return ip


# fonction pour fermer le socket lors de la fermeture de l'application
def close_port(skt: socket):
    # essaie et si le port n'est pas connecté, on fait juste le fermer. Autrement on coupe la connexion avant de fermer
    try:
        skt.shutdown(socket.SHUT_RDWR)
    except OSError:
        pass
    skt.close()
