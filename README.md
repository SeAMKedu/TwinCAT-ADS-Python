# Ohjelmointiesimerkkejä TwinCAT ADS -rajapinnan käyttöön Python-ohjelmointikielellä

Tässä dokumentissa on selostettu esimerkkien avulla, miten Python ohjelma voi kommunikoida Beckhoffin ohjaimen kanssa käyttäen TwinCATin ADS-rajapintaa. 

# TwinCAT ADS

Beckhoffin ohjaimet ja muut TwinCATia ajavat ohjaimet voivat kommunikoida keskenään ADS-rajapinnan kautta. Lisäksi ADS-yhteys mahdollistaa ohjaimen ja PC-ohjelman välisen kommunikoinnin. TwinCAT-moduulien (PLC, NC) välinen kommunikointi noudataa asiakas-palvelin-mallia (Client-Server). TwinCAT-moduulit toimivat siis joko asiakkaan tai palvelimen roolissa.

ADS-kommunikointi PLC:n ja PC-ohjelman välillä tapahtuu TCP/IP-yhteyttä käyttäen. PLC:n ja PC-ohjelman välinen kommunikointi voidaan toteuttaa useilla eri ohjelmointikielillä. Python-ohjelmointikielen tapauksessa käytetään pyads-kirjastoa. Myös C#- ja C++-ohjelmointikielille löytyy oma kirjastonsa.

TwinCAT ADS on helppo tapa siirtää tietoa PLC:stä muihin tietojärjestelmiin. Vaihtoehtoinen japa on välittää data OPC UA -protokollan avulla. OPC UA on standardoitu tiedonsiirtotapa, jonka avulla eri valmistajien laitteet ja ohjelmistot voivat keskustella tietoturvallisesti keskenään. Jos käytetään vain Beckhoffin laitteita, ADS tarjoaa yksinkertaisemman tavan välittää tietoa. ADS-yhteyden avulla voidaan esimerkiksi muuttaa TwinCAT-ohjelman muuttujan arvoa PC-ohjelmasta käsin. Vastaavasti TwinCAT-ohjelman muuttujien arvoja voidaan siirtää PLC-ohjelmasta PC-ohjelmaan.

# TwinCAT-ohjelma ADS-yhteyden testaamista varten

ADS-yhteyden tastaamisessa tarvittava TwinCAT-ohjelma löytyy [täältä](/Ads3SinTestPLC/).

TwinCAT-ohjelma alkaa generoi simuloituja mittauksia, jotka on aikaleimattu. Mittausdata on tietueessa Measurements, joka löytyy TwinCAT-projektin DUTS-kansioista.

```
TYPE Measurements :
STRUCT
	timeHi : UDINT; 		// aika
	timeLo : UDINT;	 		// aika
	measurement1 : REAL;	// mittaus 1
	measurement2 : REAL;	// mittaus 2
	measurement3 : REAL;	// mittaus 3
	counter : INT;			// juokseva numero
	arrayValue: INT;		
END_STRUCT
END_TYPE
```
Ohjelmakoodi on tiedostossa MAIN, joka löytyy POUs-kansioista.

Ohjelman muuttujien määrittelyosa näyttää tältä:

```
PROGRAM MAIN

VAR	
    // tietue mittauksia varten
    measurementData : Measurements;

    start: BOOL; // start-painike
    reset: BOOL; // reset-painike
	
    // yksi ajastin riittaa
    timer1: TON;
    // tilat esitetaan INT-muuttujalla
    step: INT;
    counter: INT;
    // triggeri start-painiketta varten
    startTriggered: BOOL;
    trigger: F_TRIG;	
	
    sysTime : GETSYSTEMTIME;
END_VAR
```
Itse ohjelmakoodi on alla:

```
timer1.IN := TRUE;   // timer päälle
  
IF reset THEN
    step := 0;
END_IF 

// otetaan nouseva reuna start-paimikkeesta
trigger(CLK := start, Q => startTriggered);

CASE step OF
  0 : 
    // mennään start-painikkeesta tilaan 1
    IF start THEN
      // nollataan ajastin
      timer1(IN := FALSE);
      step := 1;
    END_IF
    
  1 : // odotellaan 0.5 sek
    // asetetaan aika
    timer1.PT := T#500MS;
    counter := counter + 1;
   
    IF timer1.Q THEN
        // IN arvoon FALSE ja timerin kutsu
        timer1(IN := FALSE);
        // seuraavaan tilaan
        step := 2;
    END_IF

   2 : 	// tehdään mittauksia
	
    // otetaan kellonaika ja kopioidaan output structiin
    sysTime(timeLoDW => measurementData.timeLo, 
          timeHiDW =>  measurementData.timeHi);
    measurementData.counter := counter;
	
    // generoi mittauksia. amplitudi +/- 1. Jaksonaika 5-10 sekuntia
    // eri mittausten välillä noin 120 asteen vaihe-ero
    measurementData.measurement1 := SIN(counter / 24.0);
    measurementData.measurement2 := 1.1 * SIN(counter / 240.0 + 2);
    measurementData.measurement3 := 0.9 * SIN(counter / 240.0 + 4);
   
    measurementData.arrayValue := 1;
	
    // mennään takaisin odotustilaan
    step := 1;
END_CASE	
// kutsutaan ajastinta joka kierroksella
timer1();  
```
Ohjelma alkaa tuottamaan mittauksia, kun muuttuja start saa arvon TRUE. Tämän muuttujan arvo voidaan asettaa myös PC-ohjelmasta ADS:n välityksella.

Mittausten arvoja päivitetään puolen sekunnin välein. Ohjelma ei mittaa oikeasti mitään, vaan mittausten arvot generoidaan sini-funktion avulla. Tietueen measurementData sisältö voidaan lukea PC-ohjelmasta ADS:n kautta.

# ADS-yhteyttä käyttävä Python-ohjelma

Python-ohjelma [adsreader.py](/adsreader.py/) avaa ensin ADS-yhteyden TwinCAT-ohjelmaan ja asettaa TwinCAT-ohjelman muuttujan start arvon TRUEksi. Tämän jälkeen Python-ohjelma lukee mittausdataa ADS-yhteyden kautta. Huom: esimerkkiohjelma ei toimi pyads-kirjaston uusimmilla versioilla. Käytä pyads-kirjaston versiota 3.2.0.

ADS-yhteyden muodostamista varten täytyy asentaa pyads-kirjasto. Lisäksi tarvitaan kirjasto requests, jos mittaukset halutaan välittää HTTP POST -metodilla eteen päin. Kirjastot asennetaan pip-ohjelmalla:
```
pip install pyads==3.2.0
pip install requests
```
Lisää ohjelman alkuun seuraavat import-lauseet:
```Python
import pyads
import requests    
import time
import json
import msvcrt #kbhit
```
Ohjelman alussa avataan ADS-yhteys lauseilla pyads.open_port() ja pyads.AmsAddr('127.0.0.1.1.1',851). Jälkimmäisessä lauseessa annetaan ADS-osoite ja portti. ADS-osoite muistuttaa IP-osoitetta. Portti on yleensä 851, mutta sen voi tarkistaa vielä TwinCATin puolelta.
```Python
# yhteyden avaaminen
pyads.open_port()
time.sleep(0.5)
# seuraava palauttaa ADS-osoitteen
print(pyads.get_local_address())
time.sleep(0.5)
# alustus, annetaan ADS-osoite ja portti 851
adr = pyads.AmsAddr('127.0.0.1.1.1',851)
time.sleep(0.5)
```
ADS-komentojen välillä on hyvä odottaa puoli sekuntia, muuten TwinCAT-ohjelma saattaa kaatua.

Alustusten jälkeen luetaan toistolauseessa mittauksia ADS:n kautta. 
```Python
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
```
Muuttujien arvojen lukeminen tapahtuu lauseella pyads.read_by_name. Ensimmäinen parametri on edellä muodostettu ADS-osoite, toinen parametri on luettava TwinCAT-muuttuja ja kolmas parametri on luettavan muuttujan tyyppi.

Muuttujan arvojen lukemisten väliin täytyy laittaa sleep (toistolauseen lopussa). Toisto loppuu, kun käyttäjä painaa jotain näppäintä. Lopuksi suljetaan ADS-portti.

```Python
    # kannattaa laittaa sleep väliin
    time.sleep(0.7)

    if msvcrt.kbhit():
        time.sleep(0.5)
        break

    i += 1

time.sleep(0.5)
pyads.close_port()
time.sleep(0.1)
```
Alla on vielä esimerkki, jossa näytetään, miten mittaukset kootaan dictionaryyn, sarjallistetaan JSON-muotoon ja lähetetään palvelimelle HTTP POST:lla.
```Python
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
```
