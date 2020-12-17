import pyads
import requests    
import time
import json
import msvcrt #kbhit
# sopiva TwinCAT-ohjelma: Y:\Makela_Petteri\AUTE14\Verkko-ohjelmointi\Ads\Ads3SinTestPLC

# yhteyden avaaminen
pyads.open_port()
time.sleep(0.5)
# seuraava palauttaa ADS-osoitteen
print(pyads.get_local_address())
time.sleep(0.5)
# alustus, annetaan ADS-osoite ja portti 851
adr = pyads.AmsAddr('127.0.0.1.1.1',851)
time.sleep(0.5)

i = 0
while True:
    # luetaan muuttujien arvot
    m1 = pyads.read_by_name(adr, 'MAIN.measurementData.measurement1', pyads.PLCTYPE_REAL)
    time.sleep(0.1)
    m2 = pyads.read_by_name(adr, 'MAIN.measurementData.measurement2', pyads.PLCTYPE_REAL)
    time.sleep(0.1)
    m3 = pyads.read_by_name(adr, 'MAIN.measurementData.measurement3', pyads.PLCTYPE_REAL)
    time.sleep(0.1)

    # tulostetaan
    print(m1, m2, m3)

    # dictionary mittauksia varten
    measurement = { }
    measurement['id'] = i
    measurement['pressure'] = m1
    measurement['temperature'] = m2
    measurement['humidity'] = m3

    # muunna json-muotoon ja lähetä POST:lla
    s = json.dumps(measurement)
    r = requests.post('http://localhost:5000/uusimittaus', data = s)

    # kannattaa laittaa sleep väliin
    time.sleep(0.7)

    if msvcrt.kbhit():
        time.sleep(0.5)
        break

    i += 1

time.sleep(0.5)
pyads.close_port()
time.sleep(0.1)