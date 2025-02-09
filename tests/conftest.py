from datetime import datetime

import pytest
from pytz import timezone

from src.models import DealModel, PriceModel


@pytest.fixture
def deal0() -> DealModel:
    return DealModel(
        category="Family & Kids",
        description=""""""
        '<br /><img height="100" src="https://static.mydealz.de/threads/raw/CeUop/2520045_1/re/150x150/qt/55/2520045_1.jpg" width="100" /><br />Gestern im Müller Göppingen gefunden. <br />Das Vierer Pack Funko Pop Pocket im Valentinsgeschenkset. Finde die eigentlich ziemlich niedlich. Preisvergleich ist schwer, bei eBay nur um ca 25€ gesehen. <br /><br />Achtung: andere Funkos auch im Angebot!!! vom jungen Luke für 5€ über Jar-Jar-Binks bis hin zu anderen Franchises (zB Chelast von Pokémon). <br />Einfach mal in eurem Müller nachschauen!',
        image_url="https://static.mydealz.de/threads/raw/CeUop/2520045_1/re/768x768/qt/60/2520045_1.jpg",
        link="https://www.mydealz.de/deals/lokal-muller-funko-pop-pocket-4-pack-star-wars-valentinstags-bundle-2520045",
        merchant="",
        price=PriceModel(amount=6.0, currency="€"),
        published=datetime(2025, 2, 9, 16, 59, 15, tzinfo=timezone("Europe/Berlin")),
        title="(Lokal Müller) Funko Pop Pocket 4-Pack Star Wars Valentinstags Bundle",
    )


@pytest.fixture
def deal1() -> DealModel:
    return DealModel(
        category="Auto & Motorrad",
        description='<br /><img height="100" src="https://static.mydealz.de/threads/raw/3XImL/2520048_1/re/150x150/qt/55/2520048_1.jpg" width="100" /><br />EU Neuwagen Knott hat den Preis für den Skoda Octavia Combi mit dem beliebten 1.5 eTSI in Verbindung mit DSG gesenkt und ist jetzt schon ab 24.990€ zu haben. <br /><br />UVP laut Skoda Konfigurator: 36.860€<br /><br />Antrieb: 1,5-l-Vierzylinder-Benziner, Turbo.<br /><br />Leistung: 150 PS (110 kW) bei 5.000 U/min.<br /><br />Drehmoment: 250 Nm bei 1.500-3.500 U/min.<br /><br />Getriebe: Siebengang-Doppelkupplung, Frontantrieb.<br /><br />0-100 km/h: 8,4 s.<br /><br />Höchstgeschwindigkeit: 218 km/h.<br /><br />Da der Konfigurator von Knott mal wieder spinnt(wie auch schon bei anderen Modellen)und wahllos Felgen oder Farben dazu gebucht werden am besten manuel eine Anfrage stellen.<br /><br />Kraftstoffverbrauch:<br />Kombiniert:	4.9 l/100km<br />Innenstadt:	6.0 l/100km<br />Stadtrand:	4.7 l/100km<br />Landstraße:	4.2 l/100km<br />Autobahn:	5.2 l/100km<br /><br /><br />Ausstattung:<br /><br />Serienausstattung<br />Sicherheits- und Assistenzsysteme<br />Notruffunktion eCall+<br />Frontradarassistent (Front Assist)<br />Abbiege- und Ausweichassistent (Emergency Steering and Turn Assist)<br />Aufmerksamkeits- und Müdigkeitserkennung<br />Spurhalteassistent (Lane Assist)<br />Verkehrszeichenerkennung<br />Geschwindigkeitsregelanlage<br />Speedlimiter (Geschwindigkeitsbegrenzer)<br />Regensensor<br />Fahrlichtassistent (Easy Light Assist)<br />Berganfahrassistent<br />Elektronische Parkbremse inklusive Auto-Hold-Funktion<br />Parksensoren hinten mit Rangierbremsfunkion<br />Fahrer- und Beifahrerairbag sowie Knieairbag auf Fahrerseite und Beifahrerairbag-Deaktivierung<br />Seitenairbags vorn sowie Center-Airbag und Kopfairbags<br />ISOFIX-Verankerung auf dem Beifahrersitz und den äußeren Rücksitzen inklusive Top-Tether<br /><br />Funktions- und Komfortausstattung<br />12 Volt-Steckdose im Gepäckraum<br />Reifenmobilitätsset (Reifenpannenspray inklusive Kompressor)<br />Bordwerkzeug<br />Automatisch abblendbarer Innenspiegel<br />Elektrisch einstell- und beheizbare Außenspiegel<br />Zentralverriegelung inklusive im Schlüssel integrierter Funkfernbedienung und Easy Start<br />Klimaanlage Climatronic (2-Zonen) mit Allergenfilter &amp; Geruchsfilter<br />Beheizbare Vordersitze<br /><br />Außenausstattung<br />LED-Hauptscheinwerfer<br />LED-Heckleuchten<br />16" Stahlfelgen<br />Radzierblenden Tekton<br />Reifen 205/60 R16 92V<br />Verchromter Kühlergrillrahmen<br />Dachreling in Schwarz<br />Heckscheibenwischer inklusive Scheibenwaschanlage<br /><br />Interieur<br />Lederlenkrad mit Multifunktionstasten und Schaltwippen<br />Armaturentafelmittelteil genarbt<br />Dekorleisten Silber-Square und Piano-Schwarz<br />Elektrische Fensterheber vorn und hinten<br />Rücksitzlehne geteilt umlegbar<br />Höheneinstellbare Vordersitze<br />Sitzbezüge in Stoff<br /><br />Infotainment<br />Digital Cockpit<br />Infotainmentsystem mit 10" Bildschirm<br />Digitaler Radioempfang DAB+<br />Bluetooth Freisprecheinrichtung<br />SmartLink sowie Wireless SmartLink (Apple CarPlay &amp; Android Auto)<br />2 USB-Anschlüsse vorn<br />8 Lautsprecher',
        image_url="https://static.mydealz.de/threads/raw/3XImL/2520048_1/re/768x768/qt/60/2520048_1.jpg",
        link="https://www.mydealz.de/deals/skoda-octavia-combi-15-etsi-dsg150psautomatikfacelift-modelleu-neuwagenledklimaautomatiknavi-2520048",
        merchant="EU Neuwagen Knott GmbH",
        price=PriceModel(amount=24.99, currency="€"),
        published=datetime(2025, 2, 9, 17, 7, 22, tzinfo=timezone("Europe/Berlin")),
        title="Skoda Octavia Combi 1.5 eTSI DSG(150PS/Automatik)Facelift Modell/EU Neuwagen/LED/Klimaautomatik/Navi",
    )


@pytest.fixture
def deal2() -> DealModel:
    return DealModel(
        category="Garten & Baumarkt",
        description='<br /><img height="100" src="https://static.mydealz.de/threads/raw/4bi8m/2520049_1/re/150x150/qt/55/2520049_1.jpg" width="100" /><br />Beim Kauf eines 2,5L Reinigungsmittels bekommt ihr den 2. günstigere in eurem Warenkorb gratis dazu. Im Fall vom "2x Active Stone Cleaner" macht das 24% gegenüber dem günstigsten Preisvergleich.<br /><br />Bei dem "Stone and Wood" sind es aber z.B. nur 8%, wenn ihr die Behälter selbst im Globus abholt gar noch weniger. <br /><br />Alle anderen auf der Seite habe ich jetzt mal nicht durchgerechnet. ✌️<br /><br />Über die Quali von dem Reiniger kann ich leider nix sagen.',
        image_url="https://static.mydealz.de/threads/raw/4bi8m/2520049_1/re/768x768/qt/60/2520049_1.jpg",
        link="https://www.mydealz.de/deals/nilfisk-reinigungsmittel-2-fur-1-24-ggu-pvg-2520049",
        merchant="",
        price=PriceModel(amount=22.99, currency="€"),
        published=datetime(2025, 2, 9, 17, 4, 48, tzinfo=timezone("Europe/Berlin")),
        title="Nilfisk Reinigungsmittel 2 für 1 (-24% ggü PVG))",
    )


@pytest.fixture
def deal3() -> DealModel:
    return DealModel(
        category="Home & Living",
        description='<br /><img height="100" src="https://static.mydealz.de/threads/raw/ni0kW/2520050_1/re/150x150/qt/55/2520050_1.jpg" width="100" /><br />Bei Bauhaus lässt sich für den GAS 18V-10 L Akku-Staubsauger ein Preis von 109,99€ erzielen, indem man lokal in der Filiale die Tiefpreisgarantie beansprucht, da es den Staubsauger für 124,99€ lokal bei Globus Baumarkt gibt:<br /><a href="https://www.globus-baumarkt.de/p/bosch-professional-akku-staubsauger-gas-18v-10-l-solo-0761181101/?utm_source=idealo&amp;utm_medium=produkt&amp;utm_campaign=preissuchmaschinen&amp;utm_content=Bosch_Professional_Akku-Staubsauger_GAS_18V-10_L_Solo_GLO761181101" target="_blank">https://www.globus-baumarkt.de/p/bosch-professional-akku-staubsauger-gas-18v-10-l-solo-0761181101/?utm_source=idealo&amp;utm_medium=produkt&amp;utm_campaign=preissuchmaschinen&amp;utm_content=Bosch_Professional_Akku-Staubsauger_GAS_18V-10_L_Solo_GLO761181101</a><br /><br />Link zur Bauhaus:<br /><a href="https://www.bauhaus.info/akku-nass-trockensauger/bosch-professional-ampshare-18v-akku-nass-trockensauger-gas-18v-10-l-kit/p/28673389?pk_campaign=psm&amp;pk_kwd=idealo_28673389&amp;cid=PSEGerIde20210907000001" target="_blank">https://www.bauhaus.info/akku-nass-trockensauger/bosch-professional-ampshare-18v-akku-nass-trockensauger-gas-18v-10-l-kit/p/28673389?pk_campaign=psm&amp;pk_kwd=idealo_28673389&amp;cid=PSEGerIde20210907000001</a><br /><br /><br /><hr />Alternativ kann lokal bei Hornbach ebenfalls die Tiefpreisgarantie beansprucht werden, wodurch es 10% Rabatt auf den niedrigsten Preis gibt. Hornbach akzeptiert auch Online-Angebote, daher kann man auch ein Ebay-Angebot für 124€ nutzen, wodurch sich ein Preis von 111,60€ ergibt:<br /><a href="https://www.ebay.de/itm/316056652793?var=0&amp;mkevt=1&amp;mkcid=1&amp;mkrid=707-53477-19255-0&amp;toolid=20006&amp;campid=5337770552&amp;customid=zCKSr4XqCtuM3NrmLnB_SQ" target="_blank">https://www.ebay.de/itm/316056652793?var=0&amp;mkevt=1&amp;mkcid=1&amp;mkrid=707-53477-19255-0&amp;toolid=20006&amp;campid=5337770552&amp;customid=zCKSr4XqCtuM3NrmLnB_SQ</a><br /><br />Link zu Hornbach:<br /><a href="https://www.hornbach.de/p/akku-staubsauger-l-klasse-sauger-bosch-professional-gas-18v-10-l-inkl-1-x-schlauch-1-6-m-und-3tlg-saugrohr-set-ohne-akku-und-ladegeraet/10501839/?wt_mc=de.paid.price_search_engines_portals.idealo.alwayson_assortment.mas.product..." target="_blank">https://www.hornbach.de/p/akku-staubsauger-l-klasse-sauger-bosch-professional-gas-18v-10-l-inkl-1-x-schlauch-1-6-m-und-3tlg-saugrohr-set-ohne-akku-und-ladegeraet/10501839/?wt_mc=de.paid.price_search_engines_portals.idealo.alwayson_assortment.mas.product...</a><br /><br /><hr /><br /><a href="https://www.amazon.de/dp/B07WH4QD8H/?smid=AJTEMFXEXI0XS&amp;tag=idealode-mp-pk-21&amp;linkCode=asn&amp;creative=6742&amp;camp=1638&amp;creativeASIN=B07WH4QD8H&amp;ascsubtag=2025-02-09_ade0e0f609ccf6d7f7666ebfc776e9da1f1268271dd408aeb2355fecabf33588&amp;th=1" target="_blank">Amazon-Bewertungen:</a><br /><img alt="2520050-OtIdR.jpg" src="https://static.mydealz.de/threads/raw/OtIdR/2520050_1/fs/895x577/qt/65/2520050_1.jpg" /><br /><div>Preisverlauf:</div><div><img alt="2520050-wNMA6.jpg" src="https://static.mydealz.de/threads/raw/wNMA6/2520050_1/fs/895x577/qt/65/2520050_1.jpg" /><br /></div><div><br /><br /><strong>Produktdetails:</strong><br /><br />Der Akku-Nass-Trockensauger GAS 18V-10 L Kit ist ein mobiler 18V-Staubsauger der Staubklasse L.<br /><br /><em>product specifications:</em><br /><br /><ul><li>Staubklasse L</li><li>Rotationsluftstromtechnologie</li><li>Geringes Gewicht</li><li>Kompakte Bauform</li><li>Akku betrieben</li><li>Nass- und Trockensaugen</li></ul></div>',
        image_url="https://static.mydealz.de/threads/raw/ni0kW/2520050_1/re/768x768/qt/60/2520050_1.jpg",
        link="https://www.mydealz.de/deals/bauhaushornbach-tpg-bosch-professional-gas-18v-10-l-akku-staubsauger-solo-version-06019c6302-2520050",
        merchant="BAUHAUS",
        price=PriceModel(amount=109.99, currency="€"),
        published=datetime(2025, 2, 9, 17, 12, 59, tzinfo=timezone("Europe/Berlin")),
        title="Bauhaus/Hornbach TPG: Bosch Professional GAS 18V-10 L Akku-Staubsauger Solo Version (06019C6302)",
    )


@pytest.fixture
def deal4() -> DealModel:
    return DealModel(
        category="Lebensmittel & Haushalt",
        description='<br /><img height="100" src="https://static.preisjaeger.at/threads/raw/iQv2I/342993_1/re/150x150/qt/55/342993_1.jpg" width="100" /><br />BIO-Dinkelbrot 500 g ab 10.02. bis 13.02. beim Hofer in Aktion um 1,79 statt 2,99.<br /><br />A Gschmackiges und saftiges Brot zum Reinbeißen.',
        image_url="https://static.preisjaeger.at/threads/raw/iQv2I/342993_1/re/768x768/qt/60/342993_1.jpg",
        link="https://www.preisjaeger.at/deals/hofer-backbox-bio-dinkelbrot-500-g-342993",
        merchant="Hofer",
        price=PriceModel(amount=1.79, currency="€"),
        published=datetime(2025, 2, 9, 9, 5, 1, tzinfo=timezone("Europe/Berlin")),
        title="[Hofer - Backbox] BIO-Dinkelbrot 500 g",
    )


@pytest.fixture
def deal5() -> DealModel:
    return DealModel(
        category="Elektronik",
        description='<br /><img height="100" src="https://static.preisjaeger.at/threads/raw/yz7sl/343002_1/re/150x150/qt/55/343002_1.jpg" width="100" /><br />Hallo Leute,<br /><br />Da Amazon mit der Aktion von Foto Erhard in Deutschland mitgezogen ist, erhaltet ihr derzeit das Pentax SMC DA F3.5-5.6 ED AL IF DC WR O...',
        image_url="https://static.preisjaeger.at/threads/raw/yz7sl/343002_1/re/768x768/qt/60/343002_1.jpg",
        link="https://www.preisjaeger.at/deals/pentax-smc-da-f35-56-ed-al-if-dc-wr-objektiv-18-135-mm-343002",
        merchant="Amazon",
        price=PriceModel(amount=372.1, currency="€"),
        published=datetime(2025, 2, 9, 15, 35, 47, tzinfo=timezone("Europe/Berlin")),
        title="120° - Pentax SMC DA F3.5-5.6 ED AL IF DC WR Objektiv 18-135 mm",
    )
