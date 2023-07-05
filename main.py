import time                   # Allows use of time.sleep() for delays
from mqtt import MQTTClient   # For use of MQTT protocol to talk to Adafruit IO
import machine                # Interfaces with hardware components
import micropython            # Needed to run any MicroPython code
import random                 # Random number generator
from machine import Pin       # Define pin
import config                 # Contain all keys used here
import wifiConnection         # Contains functions to connect/disconnect from WiFi
import sensors                # All sensors functions


# BEGIN SETTINGS
# These need to be change to suit your environment
INTERVAL = 20000    # milliseconds
last_sent_ticks = 0  # milliseconds
led = Pin("LED", Pin.OUT)   # led pin initialization for Raspberry Pi Pico W

# Pin Settings



# Callback Function to respond to messages from Adafruit IO
def sub_cb(topic, msg):          # sub_cb means "callback subroutine"
    print((topic, msg))          # Outputs the message that was received. Debugging use.
    if msg == b"ON":             # If message says "ON" ...
        led.on()                 # ... then LED on
    elif msg == b"OFF":          # If message says "OFF" ...
        led.off()                # ... then LED off
    else:                        # If any other message is received ...
        print("Unknown message") # ... do nothing but output that it happened.

# Function to generate a random number between 0 and the upper_bound
def random_integer(upper_bound):
    return random.getrandbits(32) % upper_bound

# Function to publish sensor values to MQTT server at fixed interval
def send_sensor_values():
    global last_sent_ticks
    global INTERVAL

    if ((time.ticks_ms() - last_sent_ticks) < INTERVAL):
        return; # Too soon since last one sent.

    try:
        dht_temp, dht_humid = sensors.dhtReading()
        ds_temp = sensors.dsReading()
        darkness = sensors.ldrReading()
        soil = sensors.soilReading()
        client.publish(topic=config.DHT_TEMP_FEED, msg=str(dht_temp))
        client.publish(topic=config.DHT_HUMI_FEED, msg=str(dht_humid))
        client.publish(topic=config.DS_TEMP_FEED, msg=str(ds_temp))
        client.publish(topic=config.LDR_FEED, msg=str(darkness))
        client.publish(topic=config.SOIL_FEED, msg=str(soil))
        print("DONE")
    except Exception as e:
        print("FAILED")
    finally:
        last_sent_ticks = time.ticks_ms()

# Active debugging buffer
micropython.alloc_emergency_exception_buf(100)

# Try WiFi Connection
try:
    ip = wifiConnection.connect()
except KeyboardInterrupt:
    print("Keyboard interrupt")

# Use the MQTT protocol to connect to Adafruit IO
client = MQTTClient(config.CLIENT_ID, config.SERVER, config.PORT, config.USER, config.KEY)

# Subscribed messages will be delivered to this callback
client.set_callback(sub_cb)
client.connect()
client.subscribe(config.LIGHT_FEED)
print("Connected to %s, subscribed to %s topic" % (config.SERVER, config.LIGHT_FEED))

while True:
    try:
        client.check_msg()# Action a message if one is received. Non-blocking.
        send_sensor_values()     # Send a random number to Adafruit IO if it's time.
        wifiConnection.watchdog.feed()
    except:                  # If an exception is thrown ...
        client.disconnect()   # ... disconnect the client and clean up
        client = None
        wifiConnection.disconnect()
        print("Disconnected from MQTT Mosquitto.")

