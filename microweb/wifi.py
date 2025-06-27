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

def get_ip():
    """Get the AP IP address."""
    ap = network.WLAN(network.AP_IF)
    if ap.active():
        return ap.ifconfig()[0]
    return None