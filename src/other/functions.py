# script de définition des fonctions
import socket
import os


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
    cmd = 'ping -n 1 '
    while True:
        ip = job_queue.get()
        lastIp = ip.split('.')[3]
        comm = cmd + ip
        rep = os.popen(comm)
        # pour avoir seulement l'élément de réponse voulue
        response = rep.readlines()[2]
        # pour avoir la dernière partie de l'adresse ip retourner par la réponse
        responseIP = response.split()[2]
        # évite de faire un split sur un request time out (response.split()[2] différent, sans ip)
        if responseIP != "out.":
            lastResponse = responseIP.split('.')[3]
        else:
            lastResponse = responseIP
        # pour enlever le caractère ':' sur une réponse valide
        lastResponse = lastResponse.replace(':', '')
        if lastIp == lastResponse:
            results_queue.put(ip)
        job_queue.task_done()


def get_preview():
    print("Getting preview")
