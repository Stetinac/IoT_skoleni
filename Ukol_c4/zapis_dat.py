"""
Nacte data ze sensoru a ulozi je do SQL lite DB

"""
import time
import busio
import board
import sys
import sqlite3
from adafruit_bme280 import basic as adafruit_bme280

try:
    # senzor BME280 pripojeny na SDA a SCL
    i2c = busio.I2C(board.SCL, board.SDA)
    sensor = adafruit_bme280.Adafruit_BME280_I2C(i2c)
except Exception as e:
    sys.exit(f"Chyba inicializace hardwaru: {e}")

with sqlite3.connect('sensors.db') as conn:
    conn.execute('''
    CREATE TABLE IF NOT EXISTS sensor_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        temperature REAL,
        humidity REAL,
        pressure REAL
    )
    ''')

try:
    temperature = round(sensor.temperature,2)
    humidity = round(sensor.humidity,2)
    pressure = round(sensor.pressure,2)
    print(f"Temp:{temperature} Humidity:{humidity}% Pressure:{pressure}hPa")
    conn.execute('''
    INSERT INTO sensor_data (timestamp, temperature, humidity, pressure) VALUES (datetime('now', 'localtime'), ?, ?, ?)
    ''', (temperature, humidity, pressure))
    conn.commit()

except Exception as e:
    print(f"Jiná neočekávaná chyba: {e}")
conn.close()
