import multiprocessing
import os
import queue
import threading
from src.other.functions import sweep_network, get_wifi_ip_address

if __name__ == '__main__':
    # scanner naïf des adresses ip
    ip = get_wifi_ip_address()
    ip = ip.split('.')
    network = ip[0] + '.' + ip[1] + '.' + ip[2] + '.'

    """cmd = "ping -n 1 "
    for i in range(10, 20):
        ip = network + str(i)
        comm = cmd + ip
        rep = os.popen(comm)
        # pour avoir seulement l'élément de réponse voulue
        response = rep.readlines()[2]
        if response.find(ip) != -1:
            print(ip + " was found on network!")

    # version multitaskée du scan d'adresses ip
    POOL_SIZE = 10

    jobs = multiprocessing.Queue()
    results = multiprocessing.Queue()

    pool = [multiprocessing.Process(target=sweep_network, args=(jobs, results)) for i in range(POOL_SIZE)]

    for process in pool:
        process.start()

    for i in range(10, 20):
        jobs.put(network + str(i))

    for process in pool:
        jobs.put(None)

    for process in pool:
        process.join()

    while not results.empty():
        ip = results.get()
        print(ip)"""

    # version avec threads du scan de network
    size = 20
    num_of_threads = 20
    jobs = queue.Queue()

    for i in range(0, size+1):
        jobs.put(network + str(i))

    for i in range(num_of_threads):
        thread = threading.Thread(target=sweep_network, args=(jobs,), daemon=True)
        thread.start()

    jobs.join()




