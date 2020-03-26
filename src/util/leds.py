import sys

sys.path.append("..")
import settings
from settings import LED_PINS


if settings.PROD:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    for led_pin in LED_PINS.values():
        GPIO.setup(led_pin, GPIO.OUT)


def led_on(color):
    print(f"{color} led ON")
    if settings.PROD:
        for led_color, led_pin in LED_PINS.items():
            state = GPIO.HIGH if led_color == color else GPIO.LOW
            GPIO.output(led_pin, state)


def led_off():
    print("Leds OFF")
    if settings.PROD:
        for _, led_pin in LED_PINS.items():
            GPIO.output(led_pin, GPIO.LOW)


def error():
    led_on('red')


def info():
    led_on('blue')


def success():
    led_on('green')
