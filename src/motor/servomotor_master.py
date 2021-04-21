import RPi.GPIO as GPIO
from time import sleep
import argparse

parser = argparse.ArgumentParser(description='set angle of servomotor')
parser.add_argument('servoPin', type=int, help='pin of the servomotor')
parser.add_argument('angle', type=int, help='angle wanted for the servomotor')
args = parser.parse_args()

GPIO.setmode(GPIO.BOARD)
GPIO.setup(args.servoPin, GPIO.OUT)

# 50 représente la fréquence du PWM
pwm = GPIO.PWM(args.servoPin, 50)
pwm.start(0)


def setAngle(angle):
    duty = 5/90 * angle + 2.5
    GPIO.output(args.servoPin, True)
    pwm.ChangeDutyCycle(duty)
    sleep(0.5)
    GPIO.output(args.servoPin, False)
    pwm.ChangeDutyCycle(0)


setAngle(args.angle)
# TODO correction de code, à voir si ça continue de marcher
pwm.stop()
GPIO.cleanup()
