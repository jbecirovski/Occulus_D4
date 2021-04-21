# script de tests pour la longévité des batteries

import threading
import time
import subprocess
import i2c_master

from picamera import PiCamera

camera = PiCamera()
camera.resolution = (1920, 1080)
camera.framerate = 30

battery_manager = i2c_master.BMSCom()


def write_file(batt_manager):
    while True:
        time.sleep(900)
        battery = str(batt_manager.get_charge1000())
        temps = time.localtime()
        temps_modifie = time.strftime("%H:%M:%S", temps)
        file = open("/home/pi/test.txt", "at")
        file.write("{}, pourcentage de la batterie: {}%".format(temps_modifie, battery))
        if int(battery) <= 5:
            file.write("ALERT! BATTERY BELOW 5%! I'M ALMOST EMPTY!")
        file.close()


def move_motor():
    while True:
        time.sleep(900)
        cmd = "python3 longevite_motor.py"
        subprocess.Popen(cmd, shell=True)


# on va chercher la charge de la batterie
battery = str(battery_manager.get_charge1000())

# on vient créer le fichier ou faire l'enregistrement de la charge de la batterie restant
file = open("/home/pi/test.txt", "at")
temps = time.localtime()
temps_modifie = time.strftime("%H:%M:%S", temps)
file.write("Début du test à {} avec la charge {}%".format(temps_modifie, battery))
file.close()

# on vient garder un compte général du temps, juste pour avoir une idée de on est rendu où
count = 0

# on vient initialiser les thread pour écrire la charge dans le fichier et bouger les moteurs
threading.Thread(target=write_file, args=(battery_manager,), daemon=True)
threading.Thread(target=move_motor, args=(), daemon=True)

# on vient démarrer la caméra
camera.start_recording("/home/pi/test_longevite.h264")

# boucle principale du programme
while True:
    if count == 14400:
        camera.stop_recording()
        count = count + 1
        time.sleep(1)

    if count > 43200:
        break

    else:
        count = count + 1
        time.sleep(1)

print("Test of 12 hours completed")
