# script de définition des fonctions
import socket
import os
import subprocess


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


# fonction pour faire le ping multiprocess
def sweep_network(job_queue, results_queue):
    # ouvrir le null pour écriture
    DEVNULL = open(os.devnull, 'w')
    while True:
        ip = job_queue.get()
        if ip is None:
            break
        try:
            subprocess.check_call(['ping', '-c1', ip], stdout=DEVNULL)
            results_queue.put(ip)
        except:
            pass
