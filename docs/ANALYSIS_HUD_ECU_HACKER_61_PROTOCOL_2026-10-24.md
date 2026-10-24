# HUD ECU Hacker v6.1 — odtworzone komendy protokołu VAG K+CAN Commander

Data: **2026-10-24**. Kontynuacja [pierwszej analizy HUD 6.1](ANALYSIS_HUD_ECU_HACKER_61_KCAN_2026-10-24.md). Materiał pierwotny: przesłane przez użytkownika `HUD-ECU-Hacker v6.1(1).zip`. **Analiza statyczna IL .NET** odzyskanego `ECU_Hacker.exe` o SHA-256 `b70fa891953927da0600eac420d18acdc15a39bdba25dad366e1c52a602eeeb8`. Nie wykonywano EXE, nie komunikowano się z interfejsem. Cel: **protokół host↔VAG K+CAN Commander**, nie inne adaptery CAN.

## WYNIK: identyfikacja implementacji VAG K+CAN

Potwierdzono w jednej i tej samej klasie .NET **TypeDef #328** (dziedziczy po TypeDef #174) spójny zestaw opkodów: `0x53`, `0x54`, `0x55`, `0x60`, `0x70`, UART **830000 bit/s** i pakowanie identyfikatorów CAN. Korelacja wielu niezależnych elementów z wcześniejszymi analizami PC Commandera usuwa wątpliwość, że przypadkowe bajty `0x53/0x70` są instrukcjami obfuskacji. Odpowiednie metody są wywoływane jako **argumenty do wspólnego nadajnika RID 3649** albo **parsera odbiorczego RID 3650**, a nie znalezione tylko przez grep.

### Mapa metod z bezpośrednim dowodem

| RID | RVA | IL offset / operacja | Ustalenie |
| --- | --- | --- | --- |
| **3643** | `0x2CA404` | `0x0051–0x0057`: `ldarg.0; ldc.i4.s 85; ldc.i4.s 100; ldloc.0; call 3649` | **`0x55`** wysyła konfigurację prędkości CAN; timeout oczekiwania w kodzie **100 ms**. W tym samym RID `0x0180–0x018B`: `ldc.i4 830000; callvirt 2662` — prośba do warstwy szeregowej o **830000 bodów**. |
| **3644** | `0x2CA5B4` | IL `0x0000`: stała double `0x412E848000000000 = 1000000.0`, `ldarg.1`, `conv.r8`, `div`; dalej `Math.Round`, porównanie tolerancji `0.01`, `conv.i4`, `-1`, `conv.u1` | **Kod dzielnika bitrate CAN = round(1000000 / bitrate) - 1**. Sprawdza również dopuszczalność wartości (~1–64) i przybliżonej całkowitości dzielnika (tolerancja **0.01**). |
| **3647** | `0x2CA800` | `0x01C7–0x01D2` tworzy `int[8]` wyzerowany i woła `3648`; `0x0206–0x023E` tworzy `int[8]` z elementami `[A,A,B,B,B,B,C,D]` | Konfiguracja filtrów dla **show all** i dla filtrów selektywnych. Elementy 0–5 to **6 filtrów**, 6–7 to **2 maski**. Źródła A/B/C/D są ustawieniami użytkownika i wymagają zidentyfikowania semantycznych pól. |
| **3648** | `0x2CAB84` | `0x004F–0x0058`: `ldc.i4.s 83; ldc.i4 150; call 3649`; pętla 8 elementów, `call 3655`, `List<byte>.AddRange`, `i>=6` | **`0x53`** wysyła **8×4 = 32 bajty** filtrów/masek; timeout w kodzie **150 ms**. Ostatnie dwa rekordy otrzymują flagę `isMask`. |
| **3649** | `0x2CACB4` | `new List<byte>`, `Add(opcode)`, `Add(payloadLength)` lub `Add(0)` dla null, `AddRange(payload)`, `ToArray`, `callvirt 2691` | Funkcja konstrukcji wiadomości UART: ogólnie **opcode · payload_len · payload**. Ma osobną gałąź dla `opcode == 0x60` — nie przenosić uogólnienia bez sprawdzenia tej gałęzi. Następnie `call 3650` po odpowiedź. |
| **3650** | `0x2CAE80` | parser portu z `callvirt 2688`, buforami, analizą typu odpowiedzi; jawne wartości `0x60`, `0x70` i in. | Odbiór odpowiedzi, potencjalne ramki asynchroniczne i kolejka. **Pełny framing odpowiedzi oraz obsługa przepełnienia do dalszego odtworzenia.** |
| **3651** | `0x2CB374` | `0x0043–0x0081`: odczytuje pola pakietu, `call 3655`, `AddRange(data)`, wywołuje `3649(0x60, 500, payload)` | **`0x60`** transmisja CAN; timeout w kodzie **500 ms**. Buduje dane na podstawie pól bool `b29`, bool `RTR`, int `CanID`, dane ramki — **również ścieżka kodowania extended ID** na poziomie hosta. Nie dowodzi jeszcze faktycznej kompatybilności firmware MCU z CAN29. |
| **3652** | `0x2CB41C` | `0x0120–0x0124`: `call 3650(this,112,timeout)` | **`0x70`** parser ramki odbiorczej CAN. W metodzie widać kolejkę i logikę 2-sekundowego czasu związanej z poprzednią komunikacją. |
| **3654** | `0x2CB5C0` | `0x000B–0x0011`: `3649(this,84,100,null)`; `0x0056–0x0063`: czytanie `answer[2]`, `answer[3]` | **`0x54`** odczyt dwóch bajtów flag/stanu możliwości adaptera; timeout w kodzie **100 ms**. **Nie przypisano jeszcze dokładnego znaczenia bitów**. |
| **3655** | `0x2CB9E8` | cztery argumenty `bool,bool,int,bool`, return `byte[4]`; używa masek `0x1FFFFF`, `0x400000`, `0x800000`, przesunięć `<<18` i `<<3` | **PackID** 11-/29-bit i dodatkowe flagi. W `3648` ostatni bool to `isMask=(i>=6)`; w `3651` ostatni bool = `false`. Dokładną mapę bitów zdekodować po usunięciu obfuskacji CFG, nie zgadywać. |

### Odtworzona komenda `0x55` — szczegół

W `RID 3643` konstrukcja `List<byte>` zawiera trzy `Add`: wywołanie `RID 3644` (kod dzielnika), stałą **250 (`0xFA`)** i stałą **7 (`0x07`)**. Początkowo kolejność nie była dowiedziona, ponieważ instrukcje IL są przemieszane przez obfuskację CFG. Po prześledzeniu *dispatcher state* w `RID 3643` (klucz inicjalny, transformacja mnożeniem i XOR, `rem.un 12`, tablica skoków) uzyskano rzeczywistą drogę wykonywania:

`case 4 → case 3 → case 6 (set UART 830000) → case 5 → case 11 (new List) → case 7 (Add(divisor), Add(250)) → case 0 (Add(7)) → case 8 (send opcode 0x55) → case 9 (warunek)`.

Stąd w tej gałęzi **najbardziej prawdopodobny konkretny zapis** `55 03 [divisor] FA 07`, pod warunkiem że `RID 3649` jest zwykłym opakowaniem bez modyfikacji payloadu poza swoją osobną gałęzią `0x60`. Dla **500 kbit/s**: `55 03 01 FA 07`; dla **250 kbit/s**: `55 03 03 FA 07`. Te konkretne bajty **nie zostały zweryfikowane przechwyceniem fizycznej transmisji**; wymagają jeszcze porównania z wcześniejszymi programami PC lub testem na adapterze.

Przykładowe wartości pierwszego bajtu parametru:

| Bitrate [bit/s] | `round(1e6/bitrate)-1` | HEX |
| ---: | ---: | --- |
| 1000000 | 0 | `00` |
| 500000 | 1 | `01` |
| 250000 | 3 | `03` |
| 125000 | 7 | `07` |
| 100000 | 9 | `09` |
| 83333 | 11 | `0B` |
| 50000 | 19 | `13` |
| 33333 | 29 | `1D` |
| 25000 | 39 | `27` |
| 20000 | 49 | `31` |

**Różnica wartości UART:** `RID 3643` prosi `SerialPort` o **830000**, podczas gdy wcześniejsza dokumentacja `kcan` identyfikowała nominalnie **~833333**. Są to różne poziomy: *wartość żądana w API* vs *rzeczywista prędkość zaokrąglona do dzielnika sprzętowego FTDI*. **Kwantyzacji FTDI nie zmierzono i nie wolno traktować jej jako dowiedzionej w tym badaniu**. Wywołanie abstrakcyjnej metody `TypeDef183/RID2662` jest zgodne z setterem baudrate w transportowej klasie `TypeDef522/RID7400→7429→SerialPort.set_BaudRate`.

### Ustawienia filtrów — dwa warianty

W `RID 3647`:
1. **Show all**: wyraźnie buduje **`new int[8]`**, domyślnie same zera, następnie `call 3648` (kodowanie 32 bajtów i wysłanie `0x53`). **Nie oznacza to, że wszystkie 32 bajty na UART będą zerowe** — `RID 3655` może dodawać bity specjalne w kodowanych maskach.
2. **Filtrowanie:** buduje `int[8]`: pierwsze dwa rekordy `A`, kolejne cztery `B`, końcowe `C,D`. `RID 3648` ustawia `isMask = !(i<6)`. Wartości zostają przekodowane przez `RID 3655` na cztery bajty każda.

Tym samym **6 filtrów + 2 maski** jest potwierdzone **bezpośrednio w gałęzi HUD 6.1**, a nie tylko przywołane z danych technicznych PIC.

### Extended CAN IDs — ważna wskazówka, nie dowód sprzętowy

`RID 3651` odczytuje z modelu pakietu (TypeDef #166) pola o sygnaturach: `bool` (Field #1431), `int32` (Field #1432), `bool` (Field #1440) i tablicę danych; przekazuje je do `RID 3655` jako `bool, bool, int, false`. `RID 3655` ma dwie gałęzie zależne od pierwszego bool i używa rozkładu bitów identyfikatora rozszerzonego. **HUD 6.1 rzeczywiście koduje CAN29 w ścieżce nadajnika Commandera po stronie hosta.** Nadal brak testu, że każdy firmware PIC ten wariant rozumie; wcześniejsze wersje PC Commandera mogły go nie wykorzystywać.

### ACK / prawdziwy listen-only — jawne ograniczenie HUD

W wypakowanym **`Translation/Template.xml`**, `FormConnectSettg`, autor oświadczył dosłownie:

> „For J2534 and VAG K+CAN adapters ACK cannot be turned off.”

To oznacza, że **HUD ECU Hacker 6.1 nie oferuje dla VAG K+CAN wyłączenia ACK**, więc funkcji „Show all packets on the bus” **nie utożsamiać z pasywnym kontrolerem w trybie listen-only**. Jest to stwierdzenie autora o jego sterowniku/obsługiwanym sprzęcie, **nie niezależny dowód, że przeflashowany PIC nie mógłby obsługiwać CAN listen-only**.

Obok na ekranie połączeń widnieje tekst „Show all 11 bit and 29 bit packets from all CAN ID's (all filters are disabled)”, ale jest to opis **ogólnego UI**, a nie samoistne potwierdzenie K+CAN CAN29.

### Krytyczna korekta poprzedniej hipotezy o RID 6013

Poprzedni raport jako możliwą ścieżkę K+CAN podawał **RID 6013 (TypeDef 464)**, ponieważ miał zestaw stałych prędkości CAN, w tym 83333. **Ta przesłanka była niewystarczająca**. Obecna analiza ustaliła, że `RID 6017` w tej samej klasie dopisuje **CR (`0x0D`) do stringa** przez `System.String.Concat`, potem wysyła tekst przez `TypeDef183/RID2689` (konwersja do bajtów i niskopoziomowy nadajnik). **TypeDef464 to ścieżka protokołu tekstowego**, nie zidentyfikowany tutaj **binarny** sterownik Commandera. Nie używać `RID6013` do dowodzenia komend `0x55` Commandera.

Zamiast niej **TypeDef328** zawiera spójny zestaw komend i potwierdzoną transmisję binarną. To eliminuje istotny fałszywy trop z wcześniejszych notatek.

## Otwarte pytania (do dalszej statycznej pracy albo capture)

- Pełne **znaczenie parametrów** `0x54`, dodatkowych pól `0x55` (`FA,07`), pól flag pakowania `RID3655`.
- Dokładna kolejność i znaczenie 32 bajtów `0x53`, zwłaszcza bity EXIDE/MIDE/maska, porównanie do rejestrów PIC i faktyczna konfiguracja accept-all CAN11 i CAN29.
- Wszystkie warunki parsera `RID3650` oraz format odpowiedzi asynchronicznych `0x70`, reakcje na przeciążenie i wiadomości niepowiązane z bieżącym zapytaniem.
- **Czy hardware K+CAN PIC obsługuje rzeczywistą transmisję CAN29**, mimo że kod HUD 6.1 zawiera taką ścieżkę.
- **Czy istnieje firmware/hardware sposób na prawdziwy listen-only**; HUD twierdzi tylko, że jego sterownik nie potrafi wyłączyć ACK.
- Zweryfikować *baud 830000 żądany vs 833333 wykonany* na rzeczywistym FTDI (nie scalać bez pomiaru). Porównać `55 03 code FA 07` z przechwyceniami.
- Sposób sterowania DTR/RTS w `RID3646` i warunki błędów `0x54` pozostają do wyjaśnienia.

## Identyfikatory i powtarzalność

- Artefakt: `ECU_Hacker.exe`, 6 449 152 B, SHA256 `b70fa891953927da0600eac420d18acdc15a39bdba25dad366e1c52a602eeeb8`.
- Statyczny parser własny ECMA-335: PE CLR, `#~` i tabele TypeDef/MethodDef/MemberRef/MethodSpec; **10 112 MethodDef, 838 TypeDef**. Ważny szczegół implementacyjny: `Constant` to *U1,U1,HasConstant,Blob*, a `PropertyMap` to *TypeDef,Property*. Poprawne tabele kończą się dokładnie na początku `#Strings`; wcześniejsza niepoprawna definicja tablic może przesuwać MethodSpec.
- Odzyskany `Help.chm` pozostaje plikiem binarnym CHM/LZX; w środowisku nie ma dekodera LZX. Treść historycznych zmian i tłumaczeń odczytano bezpośrednio z rozpakowanych plików.
- Obfuskacja przepływu kodu: skoki `switch` sterowane stanem po `mul/xor` — porządek tekstowy IL to **nie porządek wykonania**. Tabele zamieszczone powyżej wskazują jawne argumenty wywołań, zastrzegając przypadki zależne od CFG.
- Wyniki **nie wymagają** reflasha ani eksperymentów na magistrali samochodu. Testy powinny być pasywne, na stole i ze świadomym ryzykiem ACK.

**Stan: po raz pierwszy w HUD ECU Hacker 6.1 udało się potwierdzić i zlokalizować faktyczne bajty komend w jednej spójnej klasie Commandera, wyprowadzić mapowanie bitrate i konfigurację filtrów.**

## Niezależna walidacja z dotychczasowego protokołu kcan

Po zakończeniu identyfikacji gałęzi HUD 6.1 porównano wynik z [PROTOCOL.md](PROTOCOL.md), napisanym wcześniej na podstawie **innej implementacji DLL i logu z interfejsu**. Tam niezależnie ustalono `55 03 N FA 07` i **`55 03 01 FA 07` zaobserwowane w logu przy CAN 500000 bit/s**. Jest to **mocna niezależna zgodność** dla całej struktury komendy i konkretnego testu 500 kbit/s; pozostałe wartości bitrate są nadal wyliczeniami z kodu, a nie potwierdzonymi przechwyceniami dla każdej szybkości.

Drobna różnica formuł: wcześniejszy raport używa `round(1000000/bitrate - 1)`, HUD wykonuje `round(1000000/bitrate) - 1`; dla udokumentowanych dzielników całkowitych dają identyczny rezultat, lecz przy danych granicznych/zaokrągleniach nie należy uogólniać równoważności bez testu.
