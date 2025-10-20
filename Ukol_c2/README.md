# Úkol č. 2
Vyčítání dat ze senzoru BME a ukládáni do SQLite DB souboru sensors.db
Zobrazení uložených dat s použitím  vybraných filtrů jako je MIN, MAX, AVG, atd.

## Všeobecné podmínky
1. Senzor BME280
2. RPi s OS Raspbian 12
3. Kabeláž na propojení senzoru a RPi(alternativně BreadBoard)
4. sqlite3 instalovaný v rámci OS

## Zapojeni sezoru a RPi
![RPi and BME280 wiring](wiring_rpi.png)

## Instalace prostředí Python
```
python3 -m venv .env
source .env/bin/activate
pip install -r requirements.txt
```

## Instalace podpory SQLite3 pro OS
```
sudo apt update && sudo apt install sqlite3 -y
```

## Automatizované ukládní dat ze senzoru bme280 do DB
- Vytvoření Bash skriptu ve složce s projektem
```
nano skript.sh
```

- Vložení níže uvedeného obsahu do skript.sh
```
#!/bin/bash
cd <uplna cesta k souboru>
source .env/bin/activate
python zapis_dat.py
```

- Nastavení oprávnění pro spouštění skriptu:
```
chmode +x skript.sh
```

### Kontrola správného fungování skriptu
- Spuštěním `python zapis_dat.py` by mělo dojít k vypsání aktuálních naměřených
hodnot ze senzoru do konzole a vytvoření souboru sensors.db obshaující zopbrazená data.
    
- Spuštěním `./skript.sh` by mělo opět dojít k vypsání aktuálních naměřených hodnot ze
senzoru do konzole a aktualizaci DB o další měření.

### Nastavení Cronu pro opakované spouštění skriptu po 1 minutě
Spuštěním `crontab -e` a vložením níže uvedeného řádku doplněného o cestu k souboru se skript.sh
```
* * * * * /<uplna cesta k souboru>/skript.sh
```
### Kontrola fungování pravidleně spouštěné úlohy
- Spuštěním níže uvedeného příkazu po několika minutách provozu by mělo dojít k vypsání osbahu DB,
který by měl obsahovat jednotlivá získaná data, včetně tiemstampu doby získání dat:
```    
sqlite3 data.db "SELECT * FROM sensor_data;"
```

## Vyčítání a filtrování dat
Soubor vypis-dat.py obsahuje připravené funkce, které zobrazují a případně filtrují data uložená v DB souboru sensors.db.
Odkomentováním příslušné funkce dojde z vypsání jednotlivých dat.

### Popis funkcí:
- **CsvSave**
    - Uložení všech dat z DB od csv soubour pro případné externi zpracování

- **ListAll_Data**
    - Výpis všech dat uložených v DB do konzole

- **FilteredDataFromDB**
    - Výpis MIN a MAX hodnoty jednotlivých měřených veličin skrze všechna data

- **FilterAVG**
    - Výpis celkové průměrné hodnoty teploty, vlhkosti a tlaku skrze všechna data

- **FilterAVGLastDay**
    - Výpis celkové průměrné hodnoty teploty, vlhkosti a tlaku za poslendích 24h

- **GroupByHour**
    - Výpis průměrné hodnoty teploty, vlhkosti a tlaku s rozlišením 1h skrze všechna data

- **GroupByHourLastDay**
    - Výpis průměrné hodnoty teploty, vlhkosti a tlaku s rozlišením 1h za posledních 24h

- **List5minutes**
    - Výpis všech uložených dat za poslendích 5 minut
