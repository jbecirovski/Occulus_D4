import multiprocessing
from src.other.functions import sweep_network, get_wifi_ip_address

if __name__ == '__main__':
    # scanner naïf des adresses ip
    ip = get_wifi_ip_address()
    print(ip)
    ip = ip.split('.')
    network = ip[0] + '.' + ip[1] + '.' + ip[2] + '.'
    print(network)

    """cmd = "ping -n 1 "
    for i in range(100, 120):
        ip = network + str(i)
        comm = cmd + ip
        rep = os.popen(comm)
    
        for line in rep.readlines():
            if line.count("TTL"):
                break
            if line.count("TTL"):
                print(ip, "--> Live")
    """

    # version multitaskée/threadée du scan d'adresses ip
    POOL_SIZE = 20

    jobs = multiprocessing.Queue()
    results = multiprocessing.Queue()

    pool = [multiprocessing.Process(target=sweep_network, args=(jobs, results)) for i in range(POOL_SIZE)]

    for p in pool:
        p.start()

    for i in range(100, 140):
        jobs.put(network + str(i))

    for p in pool:
        jobs.put(None)

    for p in pool:
        p.join()

    while not results.empty():
        ip = results.get()
        print(ip)
