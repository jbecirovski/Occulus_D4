# script de test pour faire bouger les moteurs durant le test de longévité des batteries

import subprocess
import time


# centrer la caméra
cmd = "python3 servomotor_master.py 33 45"
subprocess.Popen(cmd, shell=True)

time.sleep(1)

cmd = "python3 servomotor_master.py 32 45"
subprocess.Popen(cmd, shell=True)

time.sleep(1)

# opérations sur la caméra
cmd = "python3 servomotor_master.py 33 20"
subprocess.Popen(cmd, shell=True)

time.sleep(1)

cmd = "python3 servomotor_master.py 33 70"
subprocess.Popen(cmd, shell=True)

time.sleep(1)

cmd = "python3 servomotor_master.py 32 20"
subprocess.Popen(cmd, shell=True)

time.sleep(1)

cmd = "python3 servomotor_master.py 33 70"
subprocess.Popen(cmd, shell=True)

time.sleep(1)