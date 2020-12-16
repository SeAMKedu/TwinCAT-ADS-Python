# Ohjelmointiesimerkkejä TwinCAT ADS -rajapinnan käyttöön Python-ohjelmointikielellä

Tässä dokumentissa on selostettu esimerkkien avulla, miten Python ohjelma voi kommunikoida Beckhoffin ohjaimen kanssa käyttäen TwinCATin ADS-rajapintaa.

# TwinCAT ADS

Beckhoffin ohjaimet ja muut TwinCATia ajavat ohjaimet voivat kommunikoida keskenään ADS-rajapinnan kautta. Lisäksi ADS-yhteys mahdollistaa ohjaimen ja PC-ohjelman välisen kommunikoinnin. TwinCAT-moduulien (PLC, NC) välinen kommunikointi noudataa asiakas-palvelin-mallia (Client-Server). TwinCAT-moduulit toimivat siis joko asiakkaan tai palvelimen roolissa.

ADS-kommunikointi PLC:n ja PC-ohjelman välillä tapahtuu TCP/IP-yhteyttä käyttäen. PLC:n ja PC-ohjelman välinen kommunikointi voidaan toteuttaa useilla eri ohjelmointikielillä. Python-ohjelmointikielen tapauksessa käytetään pyads-kirjastoa. Myös C#- ja C++-ohjelmointikielille löytyy oma kirjastonsa.

TwinCAT ADS on helppo tapa siirtää tietoa PLC:stä muihin tietojärjestelmiin. Vaihtoehtoinen japa on välittää data OPC UA -protokollan avulla. OPC UA on standardoitu tiedonsiirtotapa, jonka avulla eri valmistajien laitteet ja ohjelmistot voivat keskustella tietoturvallisesti keskenään. Jos käytetään vain Beckhoffin laitteita, ADS tarjoaa yksinkertaisemman tavan välittää tietoa. ADS-yhteyden avulla voidaan esimerkiksi muuttaa TwinCAT-ohjelman muuttujan arvoa PC-ohjelmasta käsin. Vastaavasti TwinCAT-ohjelman muuttujien arvoja voidaan siirtää PLC-ohjelmasta PC-ohjelmaan.

# TwinCAT-ohjelmat ADS-yhteyden testaamista varten

TwinCAT-ohjelma 


