# script pour tester et faire la démonstration du fonctionnement des servomoteurs

import subprocess
import time


# centrer la caméra
cmd = "python3 servomotor_master.py 33 45"
subprocess.Popen(cmd, shell=True)

time.sleep(1)

cmd = "python3 servomotor_master.py 32 45"
subprocess.Popen(cmd, shell=True)

time.sleep(1)

cmd = "python3 servomotor_master.py 32 40"
subprocess.Popen(cmd, shell=True)

time.sleep(1)

cmd = "python3 servomotor_master.py 32 50"
subprocess.Popen(cmd, shell=True)

time.sleep(1)

cmd = "python3 servomotor_master.py 32 10"
subprocess.Popen(cmd, shell=True)

time.sleep(1)

cmd = "python3 servomotor_master.py 32 80"
subprocess.Popen(cmd, shell=True)

time.sleep(1)

cmd = "python3 servomotor_master.py 32 45"
subprocess.Popen(cmd, shell=True)

time.sleep(1)

cmd = "python3 servomotor_master.py 33 40"
subprocess.Popen(cmd, shell=True)

time.sleep(1)

cmd = "python3 servomotor_master.py 33 50"
subprocess.Popen(cmd, shell=True)

time.sleep(1)

cmd = "python3 servomotor_master.py 33 20"
subprocess.Popen(cmd, shell=True)

time.sleep(1)

cmd = "python3 servomotor_master.py 33 75"
subprocess.Popen(cmd, shell=True)

time.sleep(1)

cmd = "python3 servomotor_master.py 33 45"
subprocess.Popen(cmd, shell=True)