import gc
import uasyncio as asyncio
import logging

if True:  # dummy if to keep formatter from moving imports
    logging.basicConfig(level=logging.INFO)
    log = logging.getLogger('main')

    import measure
    gc.collect()
    from wifi_manager import WifiManager
    gc.collect()
    import housekeeping
    gc.collect()
    import mqtt
    gc.collect()
    import console
    gc.collect()

log.info('www.sensemakersams.org rain gauge')

loop = asyncio.get_event_loop()

WifiManager.setup_network()
WifiManager.start_managing()

mqtt.setup()
loop.create_task(mqtt.poll())

housekeeping.setup()
loop.create_task(housekeeping.janitor())

measure.setup()
loop.create_task(measure.poll())

log.info('Working')
loop.run_forever()
