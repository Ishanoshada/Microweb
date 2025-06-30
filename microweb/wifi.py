import network
import time

def setup_ap(ssid="ESP32-MicroWeb", password="12345678"):
    """Setup ESP32 as Access Point only."""
    sta = network.WLAN(network.STA_IF)
    sta.active(False)
    
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    
    ap.config(
        essid=ssid,
        password=password,
        authmode=network.AUTH_WPA_WPA2_PSK,
        channel=11
    )
    
    while not ap.active():
        time.sleep(0.1)
    
    print("=" * 40)
    print("ESP32 Access Point Ready!")
    print(f"SSID: {ssid}")
    print(f"Password: {password}")
    print("IP Address:", ap.ifconfig()[0])
    print("Connect to this WiFi and visit:")
    print(f"http://{ap.ifconfig()[0]}")
    print("=" * 40)
    
    return ap.ifconfig()[0]


def connect_wifi(ssid, password):
    import network, time
    print(f"Connecting to WiFi SSID: {ssid}")
    sta = network.WLAN(network.STA_IF)
    sta.active(True)
    sta.connect(ssid, password)

    timeout = 10
    start = time.time()
    while not sta.isconnected() and (time.time() - start) < timeout:
        print("Trying to connect...")
        time.sleep(1)

    if sta.isconnected():
        ip = sta.ifconfig()[0]
        print("Connected. IP:", ip)
        return ip
    else:
        raise OSError("WiFi Internal Error")



def get_ip():
    """Get the AP IP address."""
    ap = network.WLAN(network.AP_IF)
    if ap.active():
        return ap.ifconfig()[0]
    return None

def stop_ap():
    """Deactivate the ESP32 Access Point."""
    ap = network.WLAN(network.AP_IF)
    if ap.active():
        ap.active(False)
        print("=" * 40)
        print("ESP32 Access Point Stopped!")
        print("=" * 40)
    else:
        print("Access Point is already stopped.")


def disconnect_wifi():
    """Disconnect from external WiFi and disable STA interface."""
    sta = network.WLAN(network.STA_IF)
    if sta.active():
        sta.disconnect()
        sta.active(False)
        print("=" * 40)
        print("Disconnected from WiFi and disabled STA mode.")
        print("=" * 40)
    else:
        print("STA (WiFi client) is already inactive.")


def is_connected():
    """Check if the ESP32 is connected to a WiFi network."""
    sta = network.WLAN(network.STA_IF)
    return sta.isconnected() if sta.active() else False


def scan_wifi_networks():
    """Scan for available WiFi networks"""
    sta = network.WLAN(network.STA_IF)
    sta.active(True)
    networks = sta.scan()
    results = []
    
    for net in networks:
        ssid = net[0].decode('utf-8')
        bssid = ':'.join(['%02x' % b for b in net[1]])
        channel = net[2]
        rssi = net[3]
        auth = net[4]
        hidden = net[5]
        
        results.append({
            'ssid': ssid,
            'bssid': bssid,
            'channel': channel,
            'rssi': rssi,
            'auth': auth,
            'hidden': hidden
        })
    
    return sorted(results, key=lambda x: x['rssi'], reverse=True)

