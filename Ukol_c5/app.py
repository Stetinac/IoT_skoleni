import sys
import pandas as pd
import plotly.express as px
import plotly.io as pio
import sqlite3
import os
from flask import Flask, request, render_template, send_file, redirect, url_for, session, flash
from gpiozero import LED


# base app trida pro Flask
app = Flask(__name__)
app.secret_key = os.urandom(24)  # potřebné pro sessions, generuje se kazde spusteni (odhlasi existujici sessions)


# Demo "databáze" uživatelů (v praxi by se načítalo z DB)
USERS = {
    'jendauzivatel': 'mojehelso',
}

red_led = LED('GPIO27')  # inicializace GPIO až po spuštění serveru

# --- Uchování hodnot ve Flask config (sdílené napříč requesty) ---
app.config['CURRENT_SLIDER'] = 22  # výchozí hodnota slideru
app.config['HYST'] = 2 # výchozi hodnota hystereze
app.config['MAN'] = "off" # výchozí hodnota

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

# vypis dat pro graf
def List_Sensor_Data():
    with sqlite3.connect('sensors.db') as conn:
        sql = "SELECT timestamp, temperature, humidity, pressure FROM sensor_data WHERE timestamp >= datetime('now', '-7 day','localtime') ORDER BY timestamp"
        return pd.read_sql_query(sql, conn)

# Root for webapp
@app.get('/')
def home():
    if not 'username' in session:
         return redirect(url_for('login'))  
    
    x = List_Last_Data()
    xled_status = red_led.value
    print(xled_status)

    data = List_Sensor_Data()
    fig = px.line(data, x='timestamp', y='temperature', title="Naměřené hodnoty za posledních 7 dní", labels={'timestamp': 'Timestamp', 'temperature': 'Teplota v °C'})
    # zobrazení barvy linky teploty v popisku
    fig.data[0].name = "Templota °C"
    fig.data[0].showlegend = True

    fig.add_scatter(x=data['timestamp'], y=data['humidity'], mode='lines', name='Vlhkost (%)')
    fig.add_scatter(x=data['timestamp'], y=[pressure / 10 for pressure in data['pressure']], mode='lines', name='Tlak v kPa')
   
    data['temp_roll_avg'] = data ['temperature'].rolling(window=5).mean()
    fig.add_scatter(x=data['timestamp'], y=data['temp_roll_avg'], mode='lines', name='Průměrná teplota (5 samples)')
    
    data['humi_roll_avg'] = data ['humidity'].rolling(window=5).mean()
    fig.add_scatter(x=data['timestamp'], y=data['humi_roll_avg'], mode='lines', name='Průměrná vlhkost (5 samples)')
        
    #prirpava dat pro injektování do html
    graph_html = pio.to_html(fig, full_html=False)  
    
    # predani dat pro render stranky
    return render_template("index.html", timestamp=x[0][1], temp=x[0][2], humi=x[0][3], presso=x[0][4], led=xled_status, man=app.config['MAN'], slider=app.config['CURRENT_SLIDER'], plot=graph_html, user=session['username'])

# API pro ziskani aktualnich dat o teplote
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

@app.post('/api/switch')
def set_switch2():
    data = request.json
#    print(data)
    if data.get('state') == "on":
        red_led.on()
    elif data.get('state') == "off":
        red_led.off()
    elif data.get('manstate') == "on":
        app.config['MAN'] = "on"
#        print("Setuji mautomat na on")
    elif data.get('manstate') == "off":
        app.config['MAN'] = "off"
        red_led.off()
#        print("Setuji mautomat na off")  
    else:
        return {"Status": "Invalid data"},400
    return {"Status": "OK"},200

# API pro nastaveni hodnoty ze slideru
@app.post('/api/slider')
def set_slider():
    data = request.json
    app.config['CURRENT_SLIDER'] = int(data.get('slider'))
    print(f"Slider nastaven na: {app.config['CURRENT_SLIDER']}")
    return {"Status": "OK"},200

## login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # kontrola uživatele
        if username in USERS and USERS[username] == password:
            session['username'] = username
            flash('Přihlášení proběhlo úspěšně!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Neplatné přihlašovací údaje.', 'error')

    return render_template('login.html')

## logout page po stisknuti odhlasit
@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('Byl jsi odhlášen.', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5006, debug=True, use_reloader=False)
