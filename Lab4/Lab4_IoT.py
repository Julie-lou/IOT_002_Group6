import network, time, json, struct, math
from umqtt.simple import MQTTClient
from machine import Pin, I2C

# WiFi Configuration
SSID = "Robotic WIFI"
PASSWORD = "rbtWIFI@2025"

# MQTT Configuration
BROKER = "test.mosquitto.org"
PORT = 1883
CLIENT_ID = b"esp32_bmp280_group6"
TOPIC = b"/aupp/esp32/group6"
KEEPALIVE = 30

# BMP280 Sensor Class
class BMP280:
    def __init__(self, i2c, addr=0x76):
        self.i2c = i2c
        self.addr = addr
        chip_id = self.i2c.readfrom_mem(self.addr, 0xD0, 1)[0]
        if chip_id != 0x58:
            raise RuntimeError("Not a BMP280, ID=%#x" % chip_id)
        self._load_calibration()
        # Normal mode, temp+press oversampling x1
        self.i2c.writeto_mem(self.addr, 0xF4, b'\x27')
        self.i2c.writeto_mem(self.addr, 0xF5, b'\xA0')
    
    def _load_calibration(self):
        buf = self.i2c.readfrom_mem(self.addr, 0x88, 24)
        (self.T1, self.T2, self.T3,
         self.P1, self.P2, self.P3, self.P4, self.P5,
         self.P6, self.P7, self.P8, self.P9) = struct.unpack("<HhhHhhhhhhhh", buf)
        self.t_fine = 0
    
    def _read_raw(self):
        d = self.i2c.readfrom_mem(self.addr, 0xF7, 6)
        adc_p = (d[0] << 12) | (d[1] << 4) | (d[2] >> 4)
        adc_t = (d[3] << 12) | (d[4] << 4) | (d[5] >> 4)
        return adc_t, adc_p
    
    def _comp_temp(self, adc_t):
        var1 = (((adc_t >> 3) - (self.T1 << 1)) * self.T2) >> 11
        var2 = (((((adc_t >> 4) - self.T1) * ((adc_t >> 4) - self.T1)) >> 12) * self.T3) >> 14
        self.t_fine = var1 + var2
        T = (self.t_fine * 5 + 128) >> 8
        return T / 100.0
    
    def _comp_press(self, adc_p):
        var1 = self.t_fine - 128000
        var2 = var1 * var1 * self.P6
        var2 = var2 + ((var1 * self.P5) << 17)
        var2 = var2 + (self.P4 << 35)
        var1 = ((var1 * var1 * self.P3) >> 8) + ((var1 * self.P2) << 12)
        var1 = (((1 << 47) + var1) * self.P1) >> 33
        if var1 == 0:
            return 0
        p = 1048576 - adc_p
        p = (((p << 31) - var2) * 3125) // var1
        var1 = (self.P9 * (p >> 13) * (p >> 13)) >> 25
        var2 = (self.P8 * p) >> 19
        p = ((p + var1 + var2) >> 8) + (self.P7 << 4)
        return p / 256.0
    
    @property
    def temperature(self):
        adc_t, _ = self._read_raw()
        return self._comp_temp(adc_t)
    
    @property
    def pressure(self):
        adc_t, adc_p = self._read_raw()
        self._comp_temp(adc_t)
        return self._comp_press(adc_p)
    
    @property
    def altitude(self):
        p = self.pressure
        return 44330 * (1 - (p / 101325) ** (1 / 5.255))

# WiFi Connection Function
def wifi_connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Connecting to WiFi...")
        wlan.connect(SSID, PASSWORD)
        t0 = time.ticks_ms()
        while not wlan.isconnected():
            if time.ticks_diff(time.ticks_ms(), t0) > 20000:
                raise RuntimeError("Wi-Fi connect timeout")
            time.sleep(0.3)
    print("WiFi OK:", wlan.ifconfig())
    return wlan

# Create MQTT Client
def make_client():
    return MQTTClient(client_id=CLIENT_ID, server=BROKER, port=PORT, keepalive=KEEPALIVE)

# Connect to MQTT Broker
def connect_mqtt(c):
    time.sleep(0.5)
    c.connect()
    print("MQTT connected")

# Initialize BMP280 Sensor
def init_sensor():
    i2c = I2C(0, scl=Pin(22), sda=Pin(21))
    bmp = BMP280(i2c, addr=0x76)
    print("BMP280 sensor initialized")
    return bmp

# Main Program
def main():
    # Connect to WiFi
    wifi_connect()
    
    # Initialize sensor
    bmp = init_sensor()
    
    # Create MQTT client
    client = make_client()
    
    while True:
        try:
            connect_mqtt(client)
            
            while True:
                # Read sensor data
                temp = round(bmp.temperature, 2)
                press = round(bmp.pressure / 100, 2)  # Convert to hPa
                alt = round(bmp.altitude, 2)
                
                # Create JSON message for Node-RED/InfluxDB
                data = {
                    "temperature": temp,
                    "pressure": press,
                    "altitude": alt
                }
                
                msg = json.dumps(data)
                client.publish(TOPIC, msg)
                
                # Print to console
                print("Published:", msg)
                print("Temp: %.2f°C | Press: %.2fhPa | Alt: %.2fm" % (temp, press, alt))
                print("-" * 50)
                
                time.sleep(5)
                
        except OSError as e:
            print("MQTT error:", e)
            try:
                client.close()
            except:
                pass
            print("Retrying MQTT in 3s...")
            time.sleep(3)
        except Exception as e:
            print("Sensor error:", e)
            print("Retrying in 3s...")
            time.sleep(3)

# Run the program
main()