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


---

## Drugie niezależne potwierdzenie układu 6+2: kod programu 2.5

W `VWTester.exe` FULL 2.5 (SHA-256 `b90fc612decb04759a77fd0f02946157d832053186c7adf5e50624a1b103a10d`) funkcja `0x40E490–0x40E565` przygotowuje komunikat `53 20`:

1. pętla `0x40E4E3–0x40E513` koduje **6** identyfikatorów po **4 bajty** (24 B);
2. pętla `0x40E515–0x40E545` koduje **2** identyfikatory/maski po **4 bajty** (8 B);
3. cały blok ma **32 B** i jest wysyłany komendą `0x53`.

Dla wpisów z tej ścieżki użyto kodowania CAN11 `SIDH=(ID>>3)&0xFF`; `SIDL=((ID&7)<<2)&0x1C`; dalsze 2 B = 0. To dobrze odpowiada architekturze **6 filtrów RX + 2 masek RX** w rodzinie PIC18, ale **nie dowodzi wprost kolejności RXF0..RXF5, RXM0..RXM1 w pamięci PIC**. Inna funkcja `0x419510` używa również dodatkowych bitów `0x40` i `0x60` w części bloku, których znaczenia jeszcze nie wyjaśniono.

**Nowe testy KCAN-D019:** na izolowanym CAN odczytać pierwotny blok przez `52 00`, porównywać pojedyncze kontrolowane zmiany w jednym z ośmiu pól i mierzyć rzeczywistą akceptację ID. Nie kopiować losowych konfiguracji do samochodu.


## Dwa bloki inicjalizacji odtworzone w FULL 2.5

**Nowe, mocniejsze ustalenie:** `VWTester.exe` najpierw wysyła **stałą konfigurację** `53 20 [32 B]` (kod `0x41AA6F–0x41AAF8`), następnie **drugą, zależną od jednobajtowego `x`** (funkcja `0x419510`, wywołanie `0x41AB0B`). To nie jest pojedynczy blok 6+2.

| Wpis, 4 bajty | Blok A | Blok B |
| --- | --- | --- |
| 0 | `FF 1C 00 00` | `SIDH SIDL 00 00` |
| 1 | `FF 1C 00 00` | `FF 1C 00 00` |
| 2 | `FF 1C 00 00` | `FF 1C 00 00` |
| 3 | `FF 1C 00 00` | `FF 1C 00 00` |
| 4 | `FF 1C 00 00` | `60 00 00 00` |
| 5 | `FF 1C 00 00` | `SIDH SIDL 00 00` |
| 6 | `FF 1C 00 FF` | `FF 1C 00 FF` |
| 7 | `FF 1C 00 00` | `FF 1C 00 00` |

```text
SIDH = (x >> 3) | 0x40
SIDL = (x & 7) << 2

Wyinterpretowane standardowe CAN ID:
  SIDH/SIDL → 0x200 + x
  60 00 → 0x300

Przykład B, x=0x37 (wyliczony, bez pomiaru):
53 20 46 1C 00 00 FF 1C 00 00 FF 1C 00 00 FF 1C 00 00
      60 00 00 00 46 1C 00 00 FF 1C 00 FF FF 1C 00 00
```

**Interpretacja „6 filtrów + 2 maski” nadal jest hipotezą mapowania na rejestry PIC.** Nie wiemy, jak w firmware działają wpisy `FF1C` i szczególny końcowy `FF` w pozycji 6. Bloki są wynikiem deasemblacji hosta, a nie pomiaru ruchu UART na Twoim adapterze.

[Pełny ślad kodu i metodologia](ANALYSIS_VWTESTER_25_DEEP_2026-10-23.md) · [KCAN-D023/D024](DISCREPANCIES.md).

## Kolejne niezależne potwierdzenie konstrukcji 6+2 (3.0 beta oraz 4.5; 2026-10-23)

W `VAG-CAN Commander 3.0 beta.exe` kod `0x40A3F9–0x40A465` tworzy `53 20` z dwoma pętlami **6×4 B oraz 2×4 B**; odpowiadający kod `VAG-CAN Commander4.5.exe` znajduje się w `0x40A489–0x40A4F5`. Obie kompilacje dodatkowo mają osobne funkcje nadania 32-bajtowego bloku (`0x403470` i `0x403450`). Kodowanie standardowego CAN ID w wpisie: `SIDH=ID>>3`, `SIDL=(ID&7)<<2`, pozostałe 2 B zerowe w zbadanej ścieżce.

Jest to **dalsze potwierdzenie po stronie aplikacji** struktury „6 elementów + 2 elementy”, lecz **nie** bezpośredni odczyt RXF0..RXF5/RXM0..RXM1 na PIC ani test efektywnej filtracji. Wymagane pojedyncze kontrolowane modyfikacje i niezależne pomiary odbioru na stanowisku CAN. [Raport kodowy](ANALYSIS_VAGCAN_30BETA_45_2026-10-23.md).

## Audyt filtrów 29-bitowych: 3.0 beta/4.5 (2026-10-23)

W obu EXE **inicjalizacja** nadaje `53 20` z **32 bajtami**: rekordy 0–5 to `FF 1C 00 00`, rekord **6 to `FF 1C 00 FF`**, rekord 7 to `FF 1C 00 00`. Kod 4.5: `0x409F32..0x409FC4`; 3.0 beta: `0x409EAC..0x409F38`. `EBX=0` jest inicjalizowane na wejściu do tych procedur. Znaczenie specjalnego ostatniego `FF` w rekordzie 6 **niezidentyfikowane**. Osobny algorytm ustawień filtrów (`0x40A3F9`/ `0x40A489`) **koduje wyłącznie 11-bit ID** w pierwszych 2 bajtach, a pozostałe ustawia na 0 — **bez wyprowadzenia EID29 lub flagi IDE**.

**Nie wolno** odczytywać `FF 1C` jako surowych `SIDH/SIDL` kontrolera PIC — w protokole hosta dolne 3 bity są `<<2`, podczas gdy rejestr PIC18F248 `TXBnSIDL` ma standardowe SID[2:0] na bitach 7..5 oraz oddzielny EXIDE. To dowodzi *konieczności translacji* w firmware lub innego prywatnego formatu, a nie tego, czy moduł CAN29 jest sprzętowo włączony. [Raport](ANALYSIS_CAN29_INIT_30BETA_45_2026-10-23.md), [test D047](DISCREPANCIES.md).

## Konfiguracja 0x53 w programie 5.0+ECU (2026-10-23)

W `VAG-CAN Commander+EDC15.exe` (z ZIP nazwanego V5.1) wykryto nadal funkcję wysyłającą `53 20 [32 B]` w `0x403470` i osiem wpisów po 4 B budowanych podczas inicjalizacji `0x40AEE1..0x40AF69`: **rekordy 0–5 oraz 7 = `FF 1C 00 00`, rekord 6 = `FF 1C 00 FF`**. To potwierdzenie struktury **bloku hosta**, nie mapowania filtrów/masek ani znaczenia szczególnego ostatniego `FF` w PIC. Nadal brak flagi IDE i kodowania pełnego EID29 w standardowych ścieżkach TX/RX. [Pełny raport](ANALYSIS_VAGCAN_50ECU_V51_2026-10-23.md).
