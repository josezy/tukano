import settings

from settings import HOOK

if settings.PROD:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    for gpio_pin in HOOK.values():
        GPIO.setup(gpio_pin, GPIO.OUT)


class Hook():
    def __init__(self, trigger_pin=HOOK['trigger']):
        self.trigger_pin = trigger_pin
        self.released = False

    def release(self):
        trigger_pin_on()
        self.released = True
        print("Hook released")

    def trigger_pin_on(self):
        if settings.PROD:
            GPIO.output(self.trigger_pin, GPIO.HIGH)