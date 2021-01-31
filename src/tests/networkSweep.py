import os

# scanner naïf des adresses ip
network = '192.168.2.'
cmd = "ping -n 1 "
for i in range(0, 256):
    ip = network + str(i)
    comm = cmd + ip
    rep = os.popen(comm)

    for line in rep.readlines():
        if line.count("TTL"):
            break
        if line.count("TTL"):
            print(ip, "--> Live")
