import sys
import sqlite3
from flask import Flask, request, render_template
from gpiozero import LED


# base app trida pro Flask
app = Flask(__name__)

red_led = LED('GPIO27')  # inicializace GPIO až po spuštění serveru
# --- Uchování hodnot ve Flask config (sdílené napříč requesty) ---
app.config['CURRENT_SLIDER'] = 22  # výchozí hodnota slideru
app.config['HYST'] = 2 # výchozi hodnota hystereze
app.config['MAN'] = "off" # výchozí hodnota přepínaše Manual/Termostat

# pomocna funkcne pro pripojeni a ziskani dat z DB
def List_Last_Data():
    with sqlite3.connect('sensors.db') as conn:
        sql = '''
        SELECT * FROM sensor_data 
        ORDER BY id DESC
        LIMIT 1;'''        
        cursor = conn.cursor()
        cursor = conn.execute(sql)
        data = cursor.fetchall()
    conn.close
    return data

# Root aplikace, ktery zaroven posila zakladni nastaveni a stav vyctenych teplot z DB pro render stranky, nez dojde k pravidelne aktualizaci
@app.get('/')
def index():
    x = List_Last_Data()
    xled_status = red_led.value
    print(xled_status)
    return render_template("index.html", timestamp=x[0][1], temp=x[0][2], humi=x[0][3], presso=x[0][4], led=xled_status, man=app.config['MAN'], slider=app.config['CURRENT_SLIDER'])

# API pro ziskani aktualnich dat o teplote a stavu prepinacu
# zaroven obsahuje fukci hystereze pro termostat
@app.get('/api/data')
def get_data():
        xc = List_Last_Data()
        if app.config['MAN'] == "on":
            print("Ted to ridi pocitac!")
            lower_temp = app.config['CURRENT_SLIDER'] - 2
            upper_temp = app.config['CURRENT_SLIDER'] + 2
            if lower_temp > xc[0][2]:
                red_led.on()
            elif upper_temp < xc[0][2]:
                red_led.off()

        if red_led.value:
            led_status = "on"
        else:
            led_status = "off"
        return {"timestamp": xc[0][1], "temp": xc[0][2], "humi": xc[0][3], "press": xc[0][4], "led": led_status, "man": app.config['MAN'], "slider": app.config['CURRENT_SLIDER']}    # vrati data a HTTP 200    


# API pro setovani funkcionalit prepianci na strance
@app.post('/api/switch')
def set_switch2():
    data = request.json
    if data.get('state') == "on":
        red_led.on()
    elif data.get('state') == "off":
        red_led.off()
    elif data.get('manstate') == "on":
        app.config['MAN'] = "on"
    elif data.get('manstate') == "off":
        app.config['MAN'] = "off"
        red_led.off()
    else:
        return {"Status": "Invalid data"},400
    return {"Status": "OK"},200

# API pro nastavovani hodnoty termostatu ze slideru
@app.post('/api/slider')
def set_slider():
    data = request.json
    app.config['CURRENT_SLIDER'] = int(data.get('slider'))
    print(f"Slider nastaven na: {app.config['CURRENT_SLIDER']}")
    return {"Status": "OK"},200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5006, debug=True, use_reloader=False)
