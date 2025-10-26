import busio
import board
import sys
import sqlite3
from adafruit_bme280 import basic as adafruit_bme280
from flask import Flask, request, render_template, jsonify

try:
    # senzor BME280 pripojeny na SDA a SCL
    i2c = busio.I2C(board.SCL, board.SDA)
    sensor = adafruit_bme280.Adafruit_BME280_I2C(i2c)
except Exception as e:
    sys.exit(f"Chyba inicializace hardwaru: {e}")

app = Flask(__name__)


@app.route('/api/data')
def get_data():
    try:
        temperature = round(sensor.temperature,2)
        humidity = round(sensor.humidity,2)
        pressure = round(sensor.pressure,2)
        print(f"Temp:{temperature} Humidity:{humidity}% Pressure:{pressure}hPa")

        return {"temp": temperature, "humi": humidity, "press": pressure}    # vrati data a HTTP 200 
    
    # chyby(vyjimky) pri cteni dat je nutno osetrit, jinak skript havaruje
    except KeyboardInterrupt:
        print("\nUkončeno uživatelem (Ctrl+C)")
    except Exception as e:
        print(f"Jiná neočekávaná chyba: {e}")

@app.route('/')
def index():
    x = get_data() # zavola nacteni dat a ty pak poslu do indexu pri generovani template, jinak se musi cekat na refresh ze strany JavaScriptu
    # print(x)
    return render_template("index.html", temp=x["temp"], humi=x["humi"], presso=x["press"])


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5006, debug=True)
