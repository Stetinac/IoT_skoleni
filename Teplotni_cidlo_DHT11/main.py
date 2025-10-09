"""
cteni teploty a relativni vlhkosti ze senzoru DHT11
ziskana teplota je zaokrouhlena a indikovana prostlednictvim LED diody
"""

import time
import board
import adafruit_dht
from gpiozero import LED

# LED dioda pripojena k fyzickemu pinu 11 (GPIO17)
led = LED(17)
# senzor DHT11 pripojeny na fyzicky pin 12 (GPIO18)
dhtDevice = adafruit_dht.DHT11(board.D18)

def LED_blink(temp:int ) -> None:
    """
    Funkce rozblika diodu dle vstupni teploty zaokrouhlene na cele cislo
    Například teplota -25 se zobrazí jako:
       * rozsviceni LED na 2s (indikace „-“)
       * 2 krátká bliknutí (indikace „2“)
       * 5 krátkých bliknutí (indikace „5“)
       * rozsviceni LED na 4s (indikace "0")
    """
    # kdyz neni nula vyblikej cislo
    if temp != 0:
        # kdyz je teplota pod 0 stupnu, rozsvit LED na 2s
        if temp < 0:
            led.on()
            time.sleep(2)
            led.off()

      # blikni podle hodnoty
        for x in str(temp):
            for _ in range (0, int(x)):
                led.on()
                time.sleep(0.25)
                led.off()

    # kdyz je nula rozsvit na 4s
    else:
        led.on()
        time.sllep(4)
        led.off()
    # pauza 2s pred dalsim pokracovanim vycitani dat
    # kdyz se objevi chyba, tato cast kodu se nespusti a system nebude cekat 2s na dalsi cteni
    time.sleep(2)

# smycka pro opakovane vycitani hodnoty
while True:
    try:
        temperature = dhtDevice.temperature
        humidity = dhtDevice.humidity
        print(f"Temp: {temperature:.1f}C Humidity: {humidity}%")
        LED_blink(round(temperature))

# reseni chyby pri cteni dat
# DHT11 je celkem choulostive na kvailtu kabelaze a pripojeni
# chyby(vyjimky) pri cteni dat je nutno osetrit, jinak skript havaruje
    except RuntimeError as error:
        print(error.args[0])
        time.sleep(1.0)
        continue
    except Exception as error:
        dhtDevice.exit()
        raise error
    time.sleep(1.0)
