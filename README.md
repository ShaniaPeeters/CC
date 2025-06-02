# Inhoud:
- Video
- Stap voor stap
- Code
- Valkuilen

## Video
*// hier komt de link + thumbnail*

## Stap voor stap
### Benodigdheden:


### De doos:

### De LEDS:

### De connectors:

### De Raspberry Pi:

### Alles samen:

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
