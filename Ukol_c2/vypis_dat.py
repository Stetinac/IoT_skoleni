"""
Vypise data z SQLite DB a provede nekolik zakladnich filtru s daty

"""
import sqlite3
import pandas as pd

velicina = ("temperature", "humidity", "pressure")
filtr = ("MIN", "MAX")

# pomocna funkcne pro pripojeni a ziskani dat z DB
def ConToDB(sql, oneline=False):
    with sqlite3.connect('sensors.db') as conn:
        cursor = conn.cursor()
        cursor = conn.execute(sql)
        if oneline:
            data = cursor.fetchone()            
        else:
            data = cursor.fetchall()
    conn.close
    return data

# ulozeni vsech dat z DB do CSV pro externi zpracovani
def CsvSave():
    with sqlite3.connect('sensors.db') as conn:    
        df = pd.read_sql_query('SELECT * FROM sensor_data', conn)
        df.to_csv("vystup.csv", index=False)
   
# vypis vsech dat
def ListAll_Data():
    sql = 'SELECT * FROM sensor_data'
    data = ConToDB(sql)
    for row in data:
        print(f"Dne: {row[1]} byla teplota: {row[2]}C, vlhkost: {row[3]}%, tlak: {row[4]}hPa")
    print(80*"#")

def FilteredDataFromDB():
    for x in velicina:
        for y in filtr:
            sql = f"""
                SELECT timestamp, {x} FROM sensor_data
                WHERE {x} = (SELECT {y}({x}) FROM sensor_data)
            """
            data = ConToDB(sql)
            print(f"{y} {x}: {data[0][1]} bylo namereno: {data[0][0]}")
    print(80*"#")

# vypis celkove prumerne hodnoty teploty, vlhkosti a tlaku
def FilterAVG():
    for x in velicina:
        sql = f'SELECT AVG({x}) FROM sensor_data'
        data = ConToDB(sql, True)
        print(f"Prumerna hodnota {x} je: {round(data[0],2)}")
    print(80*"#")


# vypis prumerne hodnoty teploty, vlhkosti a tlaku za poslednich 24h
def FilterAVGLastDay():
    for x in velicina:
        sql = f"SELECT AVG({x}) FROM sensor_data WHERE timestamp >= datetime('now', '-1 day','localtime')"
        data = ConToDB(sql, True)
        print(f"Prumerna hodnota {x} za poslednich 24h je: {round(data[0],2)}")
    print(80*"#")


# vypis prumerne hodinove hodnoty teploty, vlhkosti a tlaku z cele DB
def GroupByHour():
    sql = f"""
        SELECT strftime('%Y-%m-%d %H:00', timestamp) AS hodina,
                AVG(temperature) AS avg_temp,
                AVG(humidity) AS avg_humi,
                AVG(pressure) AS avg_press
            FROM sensor_data
            GROUP BY hodina
            ORDER BY hodina;
        """
    data = ConToDB(sql)
    print(data)
    print(80*"#")

# vypis prumerne hodinove hodnoty teploty, vlhkosti a tlaku z cele DB
def GroupByHourLastDay():
    sql = f"""
        SELECT strftime('%Y-%m-%d %H:00', timestamp) AS hodina,
                AVG(temperature) AS avg_temp,
                AVG(humidity) AS avg_humi,
                AVG(pressure) AS avg_press
            FROM sensor_data
            WHERE timestamp >= datetime('now', '-1 day','localtime')
            GROUP BY hodina
            ORDER BY hodina;
        """
    data = ConToDB(sql)
    print(data)
    print(80*"#")

def List5minutes():
    sql = "SELECT * FROM sensor_data WHERE timestamp >= datetime('now', '-5 minutes', 'localtime')"
    data = ConToDB(sql)
    for row in data:
        print(f"Dne: {row[1]} byla teplota: {row[2]}C, vlhkost: {row[3]}%, tlak: {row[4]}hPa")
    print(80*"#")


if __name__ == "__main__":
#    ListAll_Data()
#    FilteredDataFromDB()
#    FilterAVG()
    FilterAVGLastDay()
#    GroupByHour()
#    GroupByHourLastDay()
    List5minutes()

