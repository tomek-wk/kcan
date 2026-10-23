# VWTester 2.5 — trzecia analiza statyczna (2026-10-23)

**Źródło:** `k+can2.5(1).zip`; `VWTester.exe` (688128 B), SHA-256 `b90fc612decb04759a77fd0f02946157d832053186c7adf5e50624a1b103a10d`. Analiza kodu x86 offline, bez uruchamiania EXE/DLL i bez kontaktu ze sprzętem. Adresy są VA tylko tej kompilacji. Nie dodano do GitHub oryginalnych materiałów.

## 1. Sekwencja otwierania kanału — dwa różne bloki `0x53`

W funkcji `0x41A9E0`:

1. Otwarcie portu przez `0x403CE0`.
2. Wybrana pozycja w GUI (`CB_GETCURSEL=0x147`) decyduje o wysłaniu `50 00` lub `51 00` (`0x41AA33–0x41AA5D`).
3. `Sleep(50 ms)` (`0x41AA62`).
4. Wysłanie pierwszego `53 20` z **32 bajtami stałej konfiguracji**, funkcja `0x404270` (`0x41AA6F–0x41AAF8`).
5. Wysłanie **drugiego** `53 20`, tym razem wygenerowanego przez `0x419510` z parametrem jednobajtowym `x` (`0x41AB01–0x41AB0B`). Funkcja nie sprawdza statusu obu zapisów w miejscu ich wywołania.

### Pierwszy blok: 32 bajty

```text
53 20
FF 1C 00 00  FF 1C 00 00  FF 1C 00 00  FF 1C 00 00
FF 1C 00 00  FF 1C 00 00  FF 1C 00 FF  FF 1C 00 00
```

Istotny szczegół: **czwarty bajt przedostatniego wpisu to `FF`**, nie zero.

### Drugi blok zależny od `x`

```text
SIDH = ((x >> 3) | 0x40) & 0xFF
SIDL = (x & 7) << 2

53 20
SIDH SIDL 00 00  FF 1C 00 00  FF 1C 00 00  FF 1C 00 00
60   00   00 00  SIDH SIDL 00 00  FF 1C 00 FF  FF 1C 00 00
```

`x` w obu badanych wywołaniach funkcji `0x419510` ograniczany jest do **jednego bajtu**. Kodowanie CAN11 daje `CAN ID = 0x200 + x`; `60 00 00 00` odpowiada CAN ID **`0x300`**.

**Przykład wyłącznie wyliczony, nie przechwycony z interfejsu:** przy `x=0x37`, ID = `0x237`:

```text
53 20
46 1C 00 00 FF 1C 00 00 FF 1C 00 00 FF 1C 00 00
60 00 00 00 46 1C 00 00 FF 1C 00 FF FF 1C 00 00
```

Blok ma układ **6 grup po 4 bajty + 2 grupy po 4 bajty**. Hipoteza: 6 filtrów i 2 maski sprzętowe PIC, a para `0x200+x`/`0x300` może być powiązana z VW CAN TP2.0. **Nie zweryfikowano fizycznej semantyki filtrów, kolejności RXF/RXM, działania maskowania ani znaczenia flag.** Nie wgrywać tych bloków do auta w ciemno.

## 2. Odrębne formatowanie wiadomości K-Line/KWP

Funkcja `0x42B250–0x42B449` jest używana w wielu miejscach kodu i ma dyspozytor na 4 warianty (argument 0..3):

| Wariant | Rekonstrukcja kodu |
| --- | --- |
| 0 | Kopiuje payload do lokalnego bufora, bez nadawania w tej gałęzi |
| 1 | Kopiuje i wysyła payload bez dodatkowego nagłówka przez `WriteFile` |
| 2 | Tworzy `[0x80+N, target, F1, data(N), checksum]` |
| 3 | Tworzy `[N, data(N), checksum]` |

Dla wariantów 2–3 kod liczy **sumę wszystkich poprzednich bajtów modulo 256**, a pętla `0x42B3C0–0x42B431` wysyła bajty pojedynczo przez wywołanie zgodne z `TransmitCommChar`, z osobną funkcją interbyte timing `0x42AED0`.

Przykłady *syntetyczne*, nie logi:
- wariant 2, `target=33`, `data=10 81`: `82 33 F1 10 81 37`;
- wariant 3 z `data=10 81`: `02 10 81 93`.

Te wiadomości reprezentują **formatowanie diagnostyki K-Line/KWP**, nie dodatkowe opkody binarnego protokołu Commandera. Istnieje osobny parser synchronizacji `0x42B1B7–0x42B240`, który poszukuje bajtu `0x55` i w pewnym stanie wysyła negację kolejnego bajtu. **Nie mylić `0x55` synchronizacji K-Line z `55 03...` konfiguracji CAN z biblioteki J2534.** Dokładny przebieg inicjalizacji 5-baud/fast-init nie został jeszcze ustalony.

## 3. Co oznacza `60 00` w kodzie hosta

Gdy dyspozytor `0x403A58–0x403A70` zobaczy wiadomość `0x60` o długości zero, zeruje zmienną `0x49C698`. Druga klasa robi analogicznie z `0x49C6B4` w `0x40970C–0x409724`.

**Twardy wniosek:** `60 00` wyzwala wyzerowanie stanu hosta. **Nie dowodzi** potwierdzenia transmisji fizycznej ani otrzymania ACK na magistrali CAN. Interpretacja payloadów dla `60 01`.. `60 04` pozostaje otwarta.

## 4. Niepełna walidacja zapisu COM

Wrapper `0x40A3D0–0x40A440`: gdy uchwyt portu jest `INVALID_HANDLE_VALUE`, zwraca `0`; w przeciwnym razie wywołuje `WriteFile` i przy błędzie czeka do **500 ms**, po czym wywołuje `GetOverlappedResult`. **Na końcu zwraca `1` bez kontroli powodzenia tego ostatniego wywołania** (`0x40A439`). To ograniczenie **hosta**, a nie funkcja firmware.

Własny sterownik powinien jawnie sprawdzać liczbę zapisanych bajtów, błędy Win32, timeout oraz osobną odpowiedź PIC.

## 5. Dodatkowy przypadek błędu konfiguracji baudrate

W `0x40A4F0` po nieudanej próbie ustawienia COM funkcja wywołuje konfigurację z wartością `0x2580=9600` (`0x40A5EB–0x40A603`), **po czym zwraca błąd inicjalizacji**. To może być ścieżka przywracania portu, **nie dowód drugiej obsługiwanej przez adapter prędkości**. Wcześniej ustalona prędkość hosta CAN to 833333 bps.

## Nadal nieustalone

Pełna semantyka `0x54`, `0x6F`, `0x5F`; CAN29; listen-only bez ACK; pełna obsługa błędów PIC; interpretacja wszystkich pól 32-bajtowej konfiguracji i zgodność tej wersji EXE z niebieskim adapterem. Nowe kwestie wpisano do [DISCREPANCIES.md](DISCREPANCIES.md). Dane nie zostały sprawdzone na sprzęcie.
