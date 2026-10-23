# Odczyt / zapis 32-bajtowego bloku konfiguracji CAN

## Zaobserwowany przepływ

```text
PC -> PIC: 52 00
PIC -> PC: 52 20 [32 bajty]

PC -> PIC: 53 20 [nowe 32 bajty]
PIC -> PC: 53 00

PC -> PIC: 52 00
PIC -> PC: 52 20 [te same 32 bajty, które zapisano]
```

Tę sekwencję stwierdzono w logach KCANTEST v1.1. Potwierdza semantykę **odczytu i zapisu bloku**. Nie dowodzi jeszcze, że wszystkie bajty zostały faktycznie zastosowane w rejestrach kontrolera CAN.

## Przykładowy blok (8 grup po 4 bajty)

```text
offset    bajty
0x00      FD 00 00 00
0x04      FF 1F FF FF
0x08      FF 1F FF FF
0x0C      FF 1F FF FF
0x10      FF 1F FF FF
0x14      FF 1F FF FF
0x18      FF 1C 00 00
0x1C      FF 1F FF FF
```

## Hipoteza mapowania

Układ **8 × 4 bajty** przypomina zestaw sześciu filtrów i dwóch masek akceptacyjnych znany z kontrolera CAN PIC18, ale **mapowanie i kolejność rejestrów pozostają niepotwierdzone**.

W kodzie `J2534KCAN.dll` operacja odpowiadająca `PassThruStartMsgFilter` prowadzi do konstrukcji komunikatu `0x53`, co wzmacnia hipotezę o funkcji filtrowania.

### Pytania nierozstrzygnięte

- Jakie pola odpowiadają filtrom RXF0–RXF5 i maskom RXM0–RXM1 (o ile rzeczywiście jest to bezpośrednie mapowanie)?
- Czy w 32-bajtowym bloku znajdują się również bity IDE / EXIDE / maskowania ramek standardowych i rozszerzonych?
- Czy filtracja jest sprzętowa, czy dodatkowo programowa?
- Czy ustawienie pozwala odbierać wszystkie ID CAN11/CAN29 bez utraty ramek?
- Czy rejestry ulegają zmianie przed/po `0x55` i resecie urządzenia?
- Czy istnieje polecenie włączenia ciągłego odbioru, czy `0x70` jest spontaniczną odpowiedzią po konfiguracji?

**Nie wysyłać losowych bloków `0x53` do adaptera w samochodzie.** Najpierw zidentyfikować znaczenie pól na testowej magistrali.
