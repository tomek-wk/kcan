# Protokół PC ↔ VAG K+CAN Commander 1.4

> Zakres: ustalenia dla `J2534KCAN.dll` v1.0.0.10 i logów testera KCANTEST v1.0/v1.1. Nie zweryfikowano na konkretnym niebieskim adapterze. Zobacz [dowody](EVIDENCE.md).

## Warstwa transportowa

- Fizyczny tor PC ↔ adapter: USB–UART (często FTDI).
- Analizowana `J2534KCAN.dll` używa **wirtualnego portu COM przez Win32** (`CreateFileA`, `SetCommState`, `ReadFile`, `WriteFile`, `EscapeCommFunction`), a nie importów `FT_*` z D2XX.
- DLL ustawia prędkość portu **833333 bit/s**, 8N1. **To nie jest prędkość CAN.**
- W innych programach spotyka się API FTDI D2XX; nie należy przenosić implementacji jednej aplikacji na wszystkie.
- DTR/RTS występują w kodzie i historycznych logach. Faktyczne znaczenie i polaryzacja zależą od konkretnej płytki; na niebieskiej wersji niezweryfikowane.

## Format wiadomości

Dla obserwowanych poleceń:

```text
+0         +1            +2 ...
opcode:u8  length:u8     payload[length]
```

Liczba bajtów kompletnego komunikatu to `2 + length`. Dotyczy udokumentowanych przykładów, niekoniecznie całej przestrzeni protokołu.

```text
PC -> PIC: 52 00
PIC -> PC: 52 20 [32 bajty]

PC -> PIC: 60 0C FC 00 00 00 01 3E 00 00 00 00 00 00
PIC -> PC: 60 00

PIC -> PC: 70 0C FD 00 00 00 01 7E 00 00 00 00 00 00
```

W powyższej parze rama `0x60` oznacza żądanie transmisji CAN11 ID `0x7E0`, a `0x70` odebraną ramkę CAN11 ID `0x7E8`. Dalsze szczegóły komend: [COMMANDS.md](COMMANDS.md).

## Format CAN11 (potwierdzony DLL i logami)

Cztery bajty nagłówka CAN są *przed* ośmioma bajtami danych.

```text
header[0] = (can_id >> 3) & 0xFF
header[1] = ((can_id & 7) << 2) & 0x1C
header[2] = 0
header[3] = 0

can_id = (header[0] << 3) | ((header[1] >> 2) & 7)
```

Zakres `can_id`: `0x000..0x7FF`.

| CAN ID | 4 bajty nagłówka |
| --- | --- |
| `0x7E0` | `FC 00 00 00` |
| `0x7E8` | `FD 00 00 00` |

**Uwaga dotycząca długości:** analizowana ścieżka DLL wysyła 4 bajty nagłówka + 8 bajtów danych CAN. Nie rozstrzygnięto, jak kodowany jest oryginalny DLC mniejszy niż osiem, w tym ramki RTR. Nie zakładać, że każde zero na końcu jest paddingiem, jeśli pracujemy z innym firmware.

### Przykładowy komunikat transmisji

```text
60 0C | FC 00 00 00 | 01 3E 00 00 00 00 00 00
opcode  długość=12    CAN ID 0x7E0   8 bajtów
```

`60 00` to odpowiedź protokołu adaptera. **Nie można z niej wnioskować, że inny węzeł CAN wysłał fizyczne ACK.**

### Przykładowy komunikat odbioru

```text
70 0C | FD 00 00 00 | 01 7E 00 00 00 00 00 00
opcode  długość=12    CAN ID 0x7E8   8 bajtów
```

## CAN29 — niezweryfikowane

W kodzie DLL występują oddzielne gałęzie obsługi identyfikatorów 29-bitowych. Dla wejściowych 4 bajtów ID `a b c d` kodowanie wyinterpretowane z deasemblacji wygląda następująco:

```text
header = [ ((a << 3) | (b >> 3)) & 0xFF,
           b & 0x1F, c, d ]
```

W analizowanej ścieżce odczytu występuje przesunięcie i złożenie bajtów, które **nie są oczywistą odwrotnością** powyższej transformacji przy standardowym big-endian J2534. Może to wskazywać na inny układ pól, błąd konkretnej wersji lub brakujący kontekst. **Nie używać tego jako potwierdzonego kodera CAN29.**

## Konfiguracja prędkości CAN (`0x55`)

DLL oblicza dla zadanego `bitrate`:

```text
N = round(1_000_000 / bitrate - 1)
polecenie: 55 03 N FA 07
```

`55 03 01 FA 07` potwierdzono w logu dla 500000 bit/s. Wartości dla 1000000 (`N=0`), 250000 (`N=3`) i 125000 (`N=7`) **obliczono z kodu, ale nie przetestowano w badanych logach**. Pozostałe parametry `FA 07` są stałe w tej ścieżce; ich semantyka po stronie PIC jest nieznana.

## Zastrzeżenia

- Nie należy mylić protokołu USB–UART z ISO-TP/UDS/KWP/TP2.0 realizowanymi na magistrali pojazdu.
- Nie potwierdzono trybu *listen-only* bez ACK ani możliwości pełnego dumpu CAN.
- Zachowanie innych klonów i firmware może być inne.
