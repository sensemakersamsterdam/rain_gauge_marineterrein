from machine import Pin, enable_irq, disable_irq, I2C, ADC
import utime as time
import uasyncio as asyncio
import logging
from bme280 import BME280
import mqtt

log = logging.getLogger('Measure')

# The below are set from the interrupt routine _do_count
last_tick = time.ticks_ms()
pulse_counter = None
count_time = time.ticks_ms()

# Objects to access the sensor hardware
bme = None
rain_pin = None
drop_adc = None

boot_time = None


def _do_count(p):
    global pulse_counter, count_time, last_tick
    BOUNCE_DELAY = const(500)     # 0.5 sec

    if time.ticks_diff(time.ticks_ms(), last_tick) > BOUNCE_DELAY:
        pulse_counter += 1
        count_time = time.time()
        last_tick = time.ticks_ms()


def setup():
    global rain_pin, pulse_counter, bme, drop_adc, boot_time

    RAIN_PIN = const(12)
    SDA_PIN = const(14)
    SCL_PIN = const(16)

    boot_time = time.time()

    pulse_counter = 0

    rain_pin = Pin(RAIN_PIN, Pin.IN, Pin.PULL_UP)
    rain_pin.irq(trigger=Pin.IRQ_FALLING, handler=_do_count)

    i2c = I2C(freq=400000, scl=Pin(SCL_PIN), sda=Pin(SDA_PIN))
    bme = BME280(i2c=i2c)

    drop_adc = ADC(0)


def read_drop(n):
    sum = 0
    for _ in range(n):
        sum += drop_adc.read()
        time.sleep_ms(10)
    return sum / n


async def poll():
    global pulse_counter, count_time, msg_type

    last_sent_counter = pulse_counter
    previous_time = boot_time

    last_case_temp, last_case_pres, last_case_hum = bme.values_f
    last_drop_ec = read_drop(5)

    do_publish = True
    msg_type = 'I'

    while True:

        mask = disable_irq()
        pc = pulse_counter
        t = count_time
        enable_irq(mask)

        if pc > last_sent_counter:
            last_sent_counter = pc
            do_publish = True
        else:
            # secondary measurements may trigger a write
            pc = last_sent_counter
            t = time.time()

        case_temp, case_pres, case_hum = bme.values_f
        drop_ec = read_drop(5)

        if abs(drop_ec - last_drop_ec) > 100:
            do_publish = True
            last_drop_ec = drop_ec

        if not(0.95 < case_temp / last_case_temp < 1.05):
            do_publish = True
            last_case_temp = case_temp

        if not(0.99 < case_pres / last_case_pres < 1.01):
            do_publish = True
            last_case_pres = case_pres

        if not(0.95 < case_hum / last_case_hum < 1.05):
            do_publish = True
            last_case_hum = case_hum

        if (t - previous_time) > (6 * 3600) and not do_publish:
            # insert an extra one every 6 hours
            msg_type = 'T'
            do_publish = True

        if do_publish:
            pl = {
                'case_humidity': case_hum,
                'case_temperature': case_temp,
                'case_pressure': case_pres,
                'rain_counter': pc,
                'drop_ec': drop_ec,
                'msg_type': msg_type,
                'previous_time': previous_time,
                'boot_time': boot_time,
                'measurement_time': t
            }
            mqtt.enqueue(pl)
            # prepare for next time
            msg_type = 'M'
            do_publish = False
            previous_time = t

        await asyncio.sleep_ms(1000)
