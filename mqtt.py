import umqtt.simple as mqtt
import json
from wifi_manager import WifiManager as WM
import logging
import utime as time
import gc
import uasyncio as asyncio

log = logging.getLogger("mqtt")

user = b'test_project'
password = b'test1234'
dev_id = b'gauge001'

client = None
connect_time = 0


# TODO ssl encrypt....
def setup():
    global client

    server = b'mqtt.sensemakersams.org'
    port = 9998

    client = mqtt.MQTTClient(dev_id, server, port=port,
                             user=user, password=password)


def _connect():
    global connect_time

    try:
        if not WM.wlan().active():
            log.info('No wifi; discarded.')
            return False
        client.connect()
        connect_time = time.time()
    except Exception as e:
        log.error('Connect%s; discarded.', e)
        return False
    return True


def disconnect():
    """ poll routine to disconnect if > n min inactive. Publish willauto-reconnect. """

    global connect_time
    n = 15 * 60             # in seconds

    if time.time() - connect_time > n:
        try:
            client.disconnect()
            connect_time = time.time()  # hack to prevent unnecessarily failing disconnects
        except Exception:
            pass


def publish(payload):

    try:
        topic = b'pipeline/' + user + b'/' + dev_id
        d = {'app_id': user, 'dev_id': dev_id, 'payload_fields': payload}
        ds = json.dumps(d)
        log.info('payload: %s', ds)

        client.publish(topic, ds)
    except Exception:
        if _connect():
            try:
                client.publish(topic, ds)
            except Exception as e:
                log.error('cannot publish %s', e)


_queue = []


def enqueue(pl_dict):
    _queue.append(pl_dict)


async def poll():
    global _queue

    while True:
        if len(_queue) > 0:
            publish(_queue.pop(0))
            gc.collect()
            await asyncio.sleep(1)
        else:
            disconnect()
            await asyncio.sleep(5)

    # -----BEGIN CERTIFICATE-----
    # MIIEAzCCAuugAwIBAgIJAOivfmNlq59aMA0GCSqGSIb3DQEBCwUAMIGXMQswCQYD
    # VQQGEwJOTDEWMBQGA1UECAwNTm9vcmQtSG9sbGFuZDESMBAGA1UEBwwJQW1zdGVy
    # ZGFtMREwDwYDVQQKDAhTVVJGc2FyYTELMAkGA1UECwwCRFAxFDASBgNVBAMMC0Rh
    # dmlkIFNhbGVrMSYwJAYJKoZIhvcNAQkBFhdkYXZpZC5zYWxla0BzdXJmc2FyYS5u
    # bDAeFw0xOTA0MTExMTEyNDVaFw0yMDA0MTAxMTEyNDVaMIGXMQswCQYDVQQGEwJO
    # TDEWMBQGA1UECAwNTm9vcmQtSG9sbGFuZDESMBAGA1UEBwwJQW1zdGVyZGFtMREw
    # DwYDVQQKDAhTVVJGc2FyYTELMAkGA1UECwwCRFAxFDASBgNVBAMMC0RhdmlkIFNh
    # bGVrMSYwJAYJKoZIhvcNAQkBFhdkYXZpZC5zYWxla0BzdXJmc2FyYS5ubDCCASIw
    # DQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBANjvozKChKbDgWzNptdstonaxi8s
    # wUY7BCIOE54Q6PZyJ9OyqHlxQAtVvM/jQIxxejpTAf6vQfcjeCXCzIGbUai4kYSq
    # 6LX5ps0Zg71IF2M0eCOuiK+dw6RZuPFcSQcxjl2MIAKaHOk0b8SFPa7WV5Mi/XHB
    # Pv4eZpxSz7AA6tmX+26PKL3cpswuyQCVBYuBuXRWsone2d2MaUK6uOsp8UUNIHG/
    # 51Iwq3AvNpiMi3kuweQTIW4kbrTW6TAYR5XhoKQmMXal9utxtKTvDwLPan8SybN+
    # M4Gu0Z2lRHr3v7CTFBV8yO11xwuqnQPPInv7jJMrzbkoFFWNVdljc4xQhosCAwEA
    # AaNQME4wHQYDVR0OBBYEFBOjzB6KzrO4C4jQmF+pNsET2GyJMB8GA1UdIwQYMBaA
    # FBOjzB6KzrO4C4jQmF+pNsET2GyJMAwGA1UdEwQFMAMBAf8wDQYJKoZIhvcNAQEL
    # BQADggEBALfq73a4T0UxeIIx2uOFLYvGIW499dfoq1U6WzdVcWi98biYCa1gNGCO
    # 3JptYWdV1+42dqZ+rLGu2+ig/aFf7luaAeOXUcZZV8vDNEXthvVEcghq5cV0F3vT
    # zNmHCj7jkqgz8PYa+KK7qUdBVepFg2jOvpl/nefz/eiOBKQTqFDimjNYTxWuDZ4O
    # bEUDVRNDD8nAvoToNEGjxBJtuKalCoTsbATDxJ6dgO+Mb54muWWCfsBCl4ynoObi
    # srpB1deANCPqdtyQyxgt6H5mvDbc+ZxsXvwDTWX/9vlVUpiLJsagC+DA1SIXdeJA
    # f3fDRaV/tCLQgsn2aDBM6JPAZKagW4o=
    # -----END CERTIFICATE-----
