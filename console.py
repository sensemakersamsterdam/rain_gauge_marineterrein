from wifi_manager import WifiManager as wm
import json
from uio import open


def _read_config():
    with open(wm.config_file, 'r') as f:
        return json.load(f)


def status():
    w = wm.wlan()
    if w is None:
        print('No WLAN')
        return
    if w.active():
        print('WLAN active')
    else:
        print('WLAN inactive')
        return

    print('Available WLAN:')
    nets = []
    for n in w.scan():
        nets.append((n[3], n[0].decode()))
    nets.sort(reverse=True)
    for n in nets:
        print('   ', '"', n[1], '",  ', n[0], sep='')

    config = _read_config()
    print()
    print('Listed:')
    for n in config['known_networks']:
        print('   ', '"', n['ssid'], '",  "', n['password'], '"', sep='')

    print()
    apc = config['access_point']['config']
    print('essid=', apc['essid'], 'pw=', apc['password'], 'channel=', apc['channel'])


def _delete_wifi_config(s):
    new = []
    for n in wm.preferred_networks:
        if s == n['ssid']:
            print('Deleting     "', s, '",  "', n['password'], '"', sep='')
        else:
            new.append(n)
    return new


def _write_config(nets=None, ap=None):
    if nets is None and ap is None:
        return
    with open(wm.config_file, 'r') as f:
        config = json.load(f)
    if nets is not None:
        config['known_networks'] = nets
    if ap is not None:
        config['access_point'] = ap
    with open(wm.config_file, 'w') as f:
        json.dump(config, f)


def delete_wifi(s):
    _write_config(nets=_delete_wifi_config(s))


def add_wifi(s, pw):
    new = _delete_wifi_config(s)
    new.append({'ssid': s, 'password': pw, 'enables_webrepl': False})
    _write_config(nets=new)


def new_ap(new_essid=None, new_pw=None, new_ch=None):
    with open(wm.config_file, 'r') as f:
        ap = json.load(f)['access_point']
    apc = ap['config']
    if new_essid is not None:
        print('Essid', apc['essid'], 'to', new_essid)
        apc['essid'] = new_essid
    if new_pw is not None:
        print('Password', apc['password'], 'to', new_pw)
        apc['password'] = new_pw
    if new_ch is not None:
        print('Channel', apc['channel'], 'to', new_ch)
        apc['channel'] = new_ch
    ap['config'] = apc
    _write_config(ap=ap)

