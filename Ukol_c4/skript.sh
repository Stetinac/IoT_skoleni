#!/bin/bash
#### Skkrip je spousten cronem a uklada data do DB souboru, ktery nasledne vycita webova aplikace
cd /home/iotskoleni/ukol_c3/
source .env/bin/activate
python zapis_dat.py
