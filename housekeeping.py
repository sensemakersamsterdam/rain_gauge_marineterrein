import gc
import utime as time
import logging
from machine import Pin
import uasyncio as asyncio
from wifi_manager import WifiManager as wm
# from micropython import mem_info
import ntptime
# correct for Amsterdam Summertime
ntptime.NTP_DELTA -= 7200

log = logging.getLogger('housekeeping')

LED_PIN = 5
led = None

next_time_set = 0


def adjust_time():

    if wm.wlan().active():
        try:
            ntptime.settime()
            log.info('Time set to %s', str(time.localtime()))
            return True
        except Exception:
            pass
    log.error('Cannot set time...')
    return False


def check_time():
    global next_time_set

    if time.time() > next_time_set:
        if adjust_time():
            next_time_set = time.time() + 24 * 3600
        else:
            next_time_set = time.time() + 120


def setup():
    global led, next_time_set

    led = Pin(LED_PIN, Pin.OUT)
    led.value(1)

    check_time()


async def janitor():

    n = 0

    while True:
        led.value(0 if led.value() else 1)  # blink led
        n += 1
        if n > 30:
            gc.collect()
            n = 0
        # mem_info()

        check_time()

        await asyncio.sleep(1)
