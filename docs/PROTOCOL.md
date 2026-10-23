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


---

## Uzupełnienie — niezależny kod Commandera FULL 2.5 (2026-10-23)

W chronionym, ale w znacznej części czytelnym `VWTester.exe` 2.5 (SHA-256 `b90fc612decb04759a77fd0f02946157d832053186c7adf5e50624a1b103a10d`) potwierdzono **Win32 COM 833333 bit/s** oraz format CAN11. W przeciwieństwie do dotychczasowej ścieżki DLL używającej N=8, oryginalny EXE 2.5 obsługuje **N w parametrze długości pakietu**:

```text
PC -> PIC: 60 (N+4)  ID_HI ID_LO 00 00 [N bajtów danych CAN]
PIC -> PC: 70 (N+4)  ID_HI ID_LO 00 00 [N bajtów danych CAN]

ID_HI = (CAN_ID >> 3) & 0xFF
ID_LO = ((CAN_ID & 7) << 2) & 0x1C
N = length - 4 przy dekodowaniu
```

Przykład **wyłącznie wyliczony z kodu** (`CAN_ID=0x123`, N=3): `60 07 24 0C 00 00 11 22 33`. **Nie jest to wynik pomiaru z interfejsu.** Warianty DLC/RTR i obsługiwany zakres N po stronie konkretnego PIC nadal wymagają testów. Funkcje: TX `0x403DC0/0x403E73`, RX `0x403850`.

W EXE 2.5 odkryto również **prawdziwe użycie `0x50` i `0x51`**, oraz niezależne nadawanie `53 20 + 32 bajty`. Patrz [COMMANDS.md](COMMANDS.md), [ANALYSIS_VWTESTER_25_2026-10-23.md](ANALYSIS_VWTESTER_25_2026-10-23.md). Nie zmieniać wcześniejszych ustaleń dla konkretnej DLL, lecz traktować dane jako **wariant implementacji hosta**.


## Uzupełnienie: parser i ciągły odbiór w hostcie 2.5

Ponowna deasemblacja **tego samego EXE 2.5** (SHA-256 `b90fc612decb04759a77fd0f02946157d832053186c7adf5e50624a1b103a10d`) wykazała, że w `0x4037D0` nagłówek `0x70` jest akceptowany tylko dla `length 4..12` (N=0..8); `0x60` w **kierunku PIC→PC** tylko dla `length 0..4`. W `0x404070` jest stanowy parser strumienia, który synchronizuje się ponownie po niepoprawnym nagłówku. Praca RX jest asynchroniczna — wątek `0x40A160` odczytuje do 1024 B z COM, a `0x403850` i `0x409500` demultipleksują `0x70` do kolejki hosta. Dwa bajty `[opcode,length]` nie muszą dotrzeć jednym odczytem USB. [Analiza szczegółowa](ANALYSIS_VWTESTER_25_FOLLOWUP_2026-10-23.md).

**Uściślenie:** obserwowane `60 00` to jeden możliwy wariant; parser 2.5 dopuszcza także odpowiedzi `60 01`.. `60 04` z payloadem, których semantyka jest nieustalona. Odbiór ciągły **nie dowodzi trybu bez ACK** ani bezstratnego monitorowania pełnej magistrali CAN.


## Ważne rozróżnienie: transport CAN Commandera a niezależne funkcje K-Line w EXE 2.5

Ponowna analiza `VWTester.exe` 2.5 wykazała, że **833333 bit/s** dotyczy przeanalizowanych funkcji hosta CAN, ale nie wyczerpuje wszystkich trybów portu COM w tym programie. Przynajmniej jedna ścieżka K-Line konfiguruje COM na **`0x28E8 = 10472` bit/s** (`0x42B575`), a inicjalizacja korzysta z **`SETBREAK=8`** i **`CLRBREAK=9`** przez `EscapeCommFunction` (`0x40A710`, `0x40A790`). Program zawiera dwie różne odmiany bitowej inicjalizacji o ok. 200 ms/bit: **8 bitów LSB-first** (`0x42AE00`) oraz **7 bitów + parzystość** (`0x434120`), a także krótką sekwencję impulsów (15/30/22 ms z kodu). Są to **działania hosta/warstwy fizycznej**, nie polecenia PC→PIC `0x50–0x70`.

W odbiorze K-Line (`0x42AFB0`) rozpoznano osobne formaty długości, odfiltrowywanie echa TX oraz obsługę negatywnej odpowiedzi diagnostycznej z NRC `0x78` (`Response Pending`). Konkretny przebieg sprzętowy i zachowanie firmware pozostają niepotwierdzone.

Program 2.5 potrafi również użyć nazwy **`\\.\COM%d`** dla COM10+; dawna wskazówka instalacyjna COM1–COM4 nie jest ogólnym ograniczeniem protokołu.

[Pełny raport z dowodami i adresami](ANALYSIS_VWTESTER_25_KLINE_INIT_RX_2026-10-23.md) · [testy KCAN-D029–D035](DISCREPANCIES.md).

## Dodatkowe potwierdzenie z Commander 3.0 beta i 4.5 (2026-10-23)

Z dwóch **różnych** EXE dostarczonych razem w `VAG-CAN Commander V4.5.zip` odtworzono **wykonawczy kod** budowy TX CAN11 `0x60`, dekodera RX `0x70` oraz `0x53` — niezależnie od wcześniejszych wyników DLL J2534 i FULL 2.5. Kody TX `0x403510` (3.0 beta) i `0x4034F0` (4.5) liczą `length=N+4`, kodują `SIDH=ID>>3`, `SIDL=(ID&7)<<2` i kopiują N bajtów danych. Parsery `0x402C80` (3.0) i `0x402C40` (4.5) wymagają `0x70 length=4..12`. Fizyczny DLC, CAN29, filtrowanie i tryb bez ACK nadal niepotwierdzone.

**Nowe ograniczenie uogólniania UART:** w 3.0 beta kod `0x4031A0` ustawia `833333` w badanej ścieżce, ale 4.5 w `0x403170` **warunkowo** wybiera `115200` (parametr 0 lub 1) albo `833333` (parametr >=2). Jest to konfiguracja po stronie **COM/UART**, nie prędkość CAN. Semantyka parametru i przypisanie do CAN/K-Line wymagają sprawdzenia. Zatem `833333` **nie jest udowodnioną uniwersalną prędkością wszystkich trybów Commandera**.

W 4.5 walidator `0x402C64` jawnie przyjmuje `0x60 length=0..4`; w 3.0 beta w badanym walidatorze nie ma takiego specjalnego wyjątku (inne wiadomości przechodzą przez tablicę deskryptorów). Nie interpretować dodatkowych bajtów odpowiedzi jako sprzętowego ACK. [Dowody z deasemblacji i ograniczenia](ANALYSIS_VAGCAN_30BETA_45_2026-10-23.md) · [testy D044/D045](DISCREPANCIES.md).

## Korekta 3.0 beta/4.5: prędkość zależy od numeru COM (2026-10-23)

W 4.5 argument wybierający `115200` przy `arg<2` i `833333` przy `arg>=2` ma **konkretne źródło**: `GetPrivateProfileIntA("COM","PORT",0,.....\\TESTER.INI)` → globalne `0xDC23E4` → `0x409EFA` → `0x403110` → `0x403170`. Ta sama wartość jest formatowana jako **`COM%d`** w `0x408CD0`. Nie jest to selektor trybu CAN/K-Line! W dostarczonym `Tester.ini` ustawiono **`PORT=4`**, więc 4.5 żąda **833333 bit/s**. W 3.0 beta odpowiadająca ścieżka używa zawsze 833333. **Na sprzęcie nadal niezweryfikowane.**

Nowe fakty **PC↔PIC** w 3.0 beta/4.5: w zbadanej inicjalizacji `51 00` → `C0 00` → `53 20 [32B]`. Polecenie **`C0 00`** jest potwierdzone kodem nadawczym i walidatorem odbioru, ale nie jego znaczenie. 3.0 beta akceptuje odpowiedź `60 00` dokładnie, 4.5 `0x60 length 0..4`. Dla obu RX `0x70 length 4..12`. Pełne tablice spod `0x44A998` (3.0) i `0x44C998` (4.5) opisano w [raporcie](ANALYSIS_VAGCAN_30BETA_45_DEEP_2026-10-23.md).

**Ograniczenie hosta:** stare wersje otwierają `COM%d` bez `\\\\.\\`; według [Microsoft CreateFileA](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-createfilea) to nie wystarcza do COM10+. FULL 2.5 ma ścieżkę z długą nazwą. [D044–D046](DISCREPANCIES.md). Przypominamy: żadne odkrycie nie potwierdza pracy fizycznego CAN ani firmware.

## Granica formatu CAN11: audyt CAN29 w 3.0 beta i 4.5 (2026-10-23)

Ponowny audyt wykonawczych ścieżek obu programów dowodzi, że **zwykłe `0x60`/ `0x70` niosą w nich wyłącznie 11-bitowy identyfikator**: TX odczytuje `WORD ID`, używa `ID_H=(ID>>3)&0xFF`, `ID_L=(ID&7)<<2`, kolejne bajty **`00 00`**; RX rekonstruuje `(ID_H<<3)|((ID_L>>2)&7)` do pola WORD i ignoruje 2 pozostałe bajty przy odtwarzaniu ID. `ID=0x18DAF110` oraz `ID=0x110` aliasują do `22 00 00 00` w tej ścieżce. Jest to **potwierdzone ograniczenie kodu hosta 3.0 beta/4.5**, nie dowód braku jakiejkolwiek innej metody CAN29 w sprzęcie/firmware; 3.6 pozostaje chroniony, bez dowodu CAN29.

**Istotne sprostowanie semantyczne:** w tym protokole `ID_L` przenosi dolne 3 bity identyfikatora na pozycjach **4..2**, a nie **7..5** jak fizyczne rejestry `TXBnSIDL` rozważanego PIC18F248/258. Sama nazwa `SIDL` w dokumentacji to wygodny skrót **bajtu protokołu PC↔PIC**, nie gwarancja surowego zapisu rejestru. Dlatego bitu EXIDE **nie należy odczytywać z surowego `ID_L`** ani oznaczać jako 0/1 bez analizy firmware. Patrz [Microchip PIC18F248](https://www.microchip.com/en-us/product/PIC18F248) i [opis pól rejestru PIC18FXX8](https://www.alldatasheet.com/html-pdf/143214/MICROCHIP/PIC18F248ESPSQTP/107208/214/PIC18F248ESPSQTP.html).

Inicjalizacja obu starych programów: `51 00`, `C0 00`, `53 20[32]`; blok init zawiera **7×`FF 1C 00 00` i 1×`FF 1C 00 FF` w pozycji nr 6 (od zera)**. **Nie ma w prześledzonej sekwencji jawnej konfiguracji extended-ID**, a znaczenie C0 / ostatniego FF jest nieznane. [Szczegółowe adresy TX/RX/init](ANALYSIS_CAN29_INIT_30BETA_45_2026-10-23.md), [KCAN-D047](DISCREPANCIES.md).
