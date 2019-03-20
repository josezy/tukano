import RPi.GPIO as GPIO

from settings import LED_PINS


GPIO.setmode(GPIO.BCM)
for _, led_pin in LED_PINS.items():
    GPIO.setup(led_pin, GPIO.OUT)


def led_on(color):
    for led_color, led_pin in LED_PINS.items():
        state = GPIO.HIGH if led_color == color else GPIO.LOW
        GPIO.output(led_pin, state)


def error():
    led_on('red')

def info():
    led_on('blue')

def success():
    led_on('green')
