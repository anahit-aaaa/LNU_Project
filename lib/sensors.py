import dht
from machine import Pin, ADC
import time
import onewire
import ds18x20
 

# Pin Settings of All sensors
dhtSensor = dht.DHT22(Pin(22))  # DHT22 connected to pin 22
oneWire_pin = Pin(27)           # DS18x20 connected to pin 27
# Initailize pin with Dallas Semiconductor temperature sensor DS18X20 
oneWire_sensor = ds18x20.DS18X20(onewire.OneWire(oneWire_pin))
# Scan and print the address of all sensors connected to pin 27 
dsSensor = oneWire_sensor.scan()
ldr = ADC(Pin(28))              # LDR connected to pin 28
soil = ADC(Pin(26))             # Moisture sensor connected to pin 26 
min_moisture=0
max_moisture=65535

# Reading DHT Temperature and Humididty
def dhtReading():
    try:
        dhtSensor.measure()
        temperature = dhtSensor.temperature()
        humidity = dhtSensor.humidity()
        if(temperature >= -5 and humidity >= 0 and temperature <= 50 and humidity <= 100):
            print("Temperature is {} degrees Celsius and Humidity is {}%".format(temperature, humidity))
            return temperature, humidity
    except Exception as error:
        print("Exception occurred", error)
    pass 

# Reading DS18B20 Temperature
def dsReading():
    try:
        oneWire_sensor.convert_temp()
        time.sleep_ms(750)
        temperature = oneWire_sensor.read_temp(dsSensor[0])
        if(temperature >= -5 and temperature <= 50):
           print("Temperature is {} degrees Celsius".format(temperature))
           return temperature
    except Exception as error:
        print("Exception occurred", error)
    pass

# Reading Photoresistor
def ldrReading():
    try:
        light = ldr.read_u16()
        darkness = round(light / 65535 * 100, 2)
        if(darkness >= 0 and darkness <= 100):
            print("Darkness is {}%".format(darkness))
            return darkness
    except Exception as error:
        print("Exception occurred", error)
    pass

# Reading soil moisture
def soilReading():
    try:
        moisture = round((max_moisture-soil.read_u16())*130/(max_moisture-min_moisture))
        if(moisture >= 0 and moisture <= 100):
            print("Moisture is {}%".format(moisture))
            return moisture
    except Exception as error:
        print("Exception occurred", error)
    pass
            
    