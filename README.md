# Inhoud:
- Video
- Stap voor stap
- Code
- Valkuilen

## Video
[![Bekijk de video](https://img.youtube.com/vi/g39wajMhOLU/0.jpg)](https://www.youtube.com/watch?v=g39wajMhOLU)

## Stap voor stap
### Benodigdheden:
- 3 programeerbare LED strips van 150 LEDS (en stroomvoorziening)
- 3 Houten panelen van 38 op 118
- 10 houten panelen van 38 op 38
- 3 plexiglas platen van 38 op 118
- 18 enkele connectors
- 6 dubbele connectors
- raspberry pi 4 (met gpio expansion)
- soldeerbout
- boormachine
- een USB microfoon
- veel bouten van 6mm op 20 ( en bijpassende moeren)
- kabeltjes voor de LEDS
- Een licht doorlatende zwarte doek van minstens 1.5m op 3m
- keramieke borden
- Een 3D printer
- lijm
- Laptop met visual studio code
- Ethernet kabel
- lasercutter of een zaag
- Zwarte acrylverf

### De doos:
Lasercut of zaag de panelen op de gewenste grote. Bij Lasercutten voorzij best de gaatjes voor de connectors al op voorhand, deze zijn 6mm in diameter. De gaatjes kan je echter later ook nog boren. 
Op een van de kleine houte panelen voorzie je gaatjes om het geluid van de vallende borden door te laten naar de microfoon. Verf alle houten panelen zwart.
### De LEDS:
Van de 3 LED strips maken we 6 door deze doormidden te knippen. Zorg ervoor dat bijde kanten 74 LEDS hebben.
Soldeer dan elks 2 LED strips aan elkaar (doolmiddel van kabbeltjes) met voldoende spatie ertussen zodat we later deze over de grond kunnen versprijden.
### De connectors:
Gebruik een 3D printer om de connectors af te printen. Gebruik hiervoor PLA of PetG. Best in een zwart fillament, anders kan je ze ook gewoon zwart schilderen.
### De Raspberry Pi:
Zorg ervoor dat je visual studio code op de raspberry pi instaleert zodat je via ssh de code op de raspberry kan zetten. Instaleer dan al de benodigde libraries voor de code. 
### Alles samen:
Sluit de microfoon en de LEDS aan op de raspberry pi. Gebruik de connectors om de houten en plexiglas panelen aan elkaar te bevestigen. 6 van de kleine panelen komen vanonder, de 6 grote vanboven. De 4 overblijvende panelen lijm je aan elkaar om een cubus vormige doos te maken zonder voor of onderkant, hier steken we de microfoon en raspberry pi onder. Bevestig de LEDS op de gewenste locatie op de vloer. Leg een stuk hout of iets dergerlijk onder waar de doos komt te staan. Bedek deze dan met de zwarte doek. Plaats dan de doos op zijn plaats. Steek alles in het stopcontact en gebruik het commando in de code om het programma op te runnen in de terminal.
## Code
Deze code ( main.py ) is bedoeld om een NeoPixel LED-strip aan te sturen op basis van het geluidsniveau dat wordt gemeten via een microfoon. Het script werkt als volgt:

1. **Audio-invoer**  
   De code gebruikt de pyaudio-bibliotheek om continu audio op te nemen via de microfoon. Het geluidsniveau wordt berekend met behulp van RMS (Root Mean Square) en piekwaarde.

2. **Berekenen van het aantal actieve LEDs**  
   Op basis van het gemeten geluidsniveau wordt bepaald hoeveel LEDs moeten oplichten. Hoe harder het geluid, hoe meer LEDs er aan gaan.

3. **Kleuren en animatie**  
   De LEDs worden verdeeld in drie kleurzones (rood, oranje, geel) afhankelijk van hun positie en het aantal actieve LEDs. Bij verandering van het geluidsniveau wordt een vloeiende overgang (fade) tussen het oude en nieuwe aantal actieve LEDs weergegeven.

4. **Aansturen van meerdere strips**  
   De code ondersteunt drie LED-strips die allemaal hetzelfde patroon tonen.

5. **Uitschakelen**  
   Bij het stoppen van het script (Ctrl+C) worden alle LEDs netjes uitgezet.

## Valkuilen
**Let op:**
- Het script moet met rootrechten worden uitgevoerd vanwege toegang tot de hardware (sudo ...).
- De gebruikte pinnen en het aantal LEDs moeten overeenkomen met je hardware-opstelling.
