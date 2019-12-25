# This file is executed on every boot (including wake-boot from deepsleep)
import network as n
n.WLAN(n.STA_IF).active(False)
n.WLAN(n.AP_IF).active(False)
import gc
gc.collect()
