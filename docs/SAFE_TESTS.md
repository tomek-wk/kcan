# Plan bezpiecznej walidacji protokołu

**Cel:** sprawdzić, czy opis z analizy `J2534KCAN.dll` i KCANTEST pasuje do konkretnego niebieskiego K+CAN Commander 1.4. To plan badań, nie skrypt wykonujący polecenia.

## Etap 0 — identyfikacja bez nadawania

1. Sprawdzić oznaczenie USB VID/PID, FTDI, port COM i wersję sterownika. Zanotować wyniki.
2. Obejrzeć obie strony PCB, model PIC, transceiver CAN/K-Line i zasilanie mikrokontrolera.
3. Ustalić wymagane zasilanie układu przez OBD; samo USB może nie zasilać PIC.
4. Nie podłączać adaptera do samochodu na etapie odtwarzania protokołu.

## Etap 1 — obserwacja i rozpoznanie

1. Rejestrować komunikację znanego programu PC ↔ adapter, łącznie z DTR/RTS.
2. Zidentyfikować baudrate/8N1 oraz moment resetu i wpływ zmian stanów linii.
3. Jeżeli bezpieczne i możliwe: rozpoznać znane żądanie `52 00`, nie zakładając zgodności firmware przed testem.
4. Porównać strukturę odpowiedzi z roboczym schematem. W razie różnic przerwać automatyczne wysyłanie.

## Etap 2 — izolowana magistrala testowa

1. Podłączyć adapter do kontrolowanej, terminowanej magistrali CAN z drugim znanym interfejsem, nie do samochodu.
2. Rozpocząć od jednej, powtarzalnej pary ID CAN11 i porównać faktyczne wyniki z logami.
3. Zbadać konfigurację filtrów `0x52/0x53` pojedynczymi kontrolowanymi zmianami i każdorazowym odczytem zwrotnym.
4. Przetestować błędy i saturację RX dopiero po zdefiniowaniu timeoutów i procedury resetu.
5. Osobno sprawdzić, czy adapter generuje ACK oraz czy oferuje tryb *listen-only*.

## Etap 3 — zgodność w szerszym zakresie

- Różne ID 11-bitowe (w tym `0x000`, `0x123`, `0x7FF`).
- Długości danych 0–8, jeżeli protokół pozwoli jednoznacznie je kodować.
- CAN29, dopiero po rozwiązaniu niespójności kodera.
- Różne prędkości CAN i zachowanie po resecie.

## Zasady

- Nie uruchamiać nieznanych EXE/DLL bez izolacji i kontroli bezpieczeństwa.
- Nie wysyłać w ciemno `0x53`, `0x55` i `0x60` do samochodu.
- Odpowiedź `60 00` nie jest dowodem na fizyczny ACK.
- Logi badań i pliki pobrane **nie trafiają do repozytorium**. Dodawać tylko wyniki zanonimizowane/opisowe, małe przykłady HEX, hashe i linki.


---

## Testy porównawcze zgłoszone przez analizę oryginalnego pakietu

1. **Nie uruchamiać otrzymanego EXE ani starych instalatorów USB bez analizy bezpieczeństwa i izolacji.** Rozpoznanie importów spakowanego programu nie jest oceną bezpieczeństwa.
2. Test **KCAN-D001** (oznaczenia wersji): porównać zasoby plików kolejnych wersji i identyfikację adaptera w ich legalnie przechwyconych sesjach, aby ustalić, czy nazwa `1.4` dotyczy aplikacji czy firmware.
3. Test **KCAN-D003** (dongle): na wyłączonym układzie sprawdzić oznaczenia posiadanego interfejsu i konfigurację USB, a ewentualne żądania klucza porównywać wyłącznie w kontrolowanym środowisku; **nie obchodzić zabezpieczeń**.
4. Test **KCAN-D004** (transport): zarejestrować ewentualne wywołania wirtualnego COM i D2XX, stany RTS/DTR oraz faktyczne bajty UART, bez zakładania tożsamości protokołu obu programów.
5. Test **KCAN-D005** (CAN11 ID): przy późniejszym uruchomieniu na stanowisku CAN wysłać ID `0x123` i porównać z potwierdzoną funkcją DLL; nie rozstrzygać na podstawie istniejących logów obejmujących wyłącznie `0x7E0/0x7E8`.

Szczegóły i interpretacja stanów: [DISCREPANCIES.md](DISCREPANCIES.md).


---

## Testy wyprowadzone z dokumentacji dystrybucji Setup Factory

- **KCAN-D006** — statyczne wydobycie EXE z instalatora lub pozyskanie niezależnego, legalnego pakietu rozpakowanego; porównanie hashy i tabel komend. Nie uruchamiać nieznanego instalatora dla samego rozpakowania.
- **KCAN-D008** — sprawdzić urządzenie w Menedżerze urządzeń oraz jego rzeczywistą wersję sterownika; PDF podaje FTDI 2.6.0.0, a INF w ZIP 2.04.06.
- **KCAN-D009** — w izolowanym eksperymencie ze stałą sekwencją odczytów porównać ustawienia Latency Timer 1/16 ms i USB TX/RX 512/4096 B, rejestrując pełny TX/RX, liczbę timeoutów i opóźnienia. To parametry sterownika, nie opkody Commandera.
- **KCAN-D010** — zweryfikować zasilanie PIC i transceivera przy podłączeniu **tylko USB** oraz na bezpiecznie przygotowanym zasilaniu laboratoryjnym OBD; nie zakładać, że Viaken i niebieski klon mają tę samą architekturę.


---

## Test KCAN-D011 — duplikaty `[CHANNEL]` i konfiguracja `Tester.ini`

- Najpierw porównać działanie parsera INI (analiza statyczna, jeśli dostępny niechroniony program).
- Jeśli eksperyment z programem jest dopuszczalny po weryfikacji bezpieczeństwa: na **odizolowanym stanowisku, bez samochodu**, porównać widoczny cel i inicjalne komunikaty UART przy `TARGET=0` i `TARGET=6`, zachowując **obie** sekcje `[CHANNEL]`. Każdorazowo notować wersję EXE i stan dongla.
- Oddzielnie porównać zachowanie `[TRACE] FILEINDEX`, aby nie mieszać dziennika programu z protokołem adaptera.
- Ponieważ EXE w obu pakietach jest bitowo identyczny, rozbieżność nie upoważnia do zmiany opkodów w [COMMANDS.md](COMMANDS.md).


---

## Badania wynikające z Commander FULL 2.5

**Wszystkie próby z nadawaniem należy przeprowadzać na osobnej, prawidłowo terminowanej magistrali testowej, nie na samochodzie.**

- **KCAN-D012:** po potwierdzeniu inicjalizacji PC↔PIC wysłać CAN11 `0x123` z N=3 i danymi `11 22 33` w izolowanym układzie. Sprawdzić, czy na rzeczywistej magistrali wystąpił **DLC=3**, a nie osiem bajtów/padding; porównać zapis HEX i timestampy drugiego interfejsu.
- **KCAN-D013/D014:** najpierw obserwować oryginalne komunikaty `50 00`, `51 00` i kody `0x54/0x6F` w legalnej, kontrolowanej sesji testowej; nie zgadywać nieznanych payloadów i nie wysyłać ich w ciemno.
- **KCAN-D016:** zarejestrować wywołania `EscapeCommFunction` oraz rzeczywiste poziomy DTR/RTS; kod 2.5 używa `SETDTR(5)`, `Sleep(500)`, `CLRDTR(6)`, następnie `SETRTS(3)` lub `CLRRTS(4)`. Odłączyć od pojazdu.
- **KCAN-D015/D017:** porównać metadane EXE i INI bez instalowania lub uruchamiania nieznanych programów; późniejsze eksperymenty tylko na izolowanym stanowisku.

Kod 2.5 i hipotezy: [ANALYSIS_VWTESTER_25_2026-10-23.md](ANALYSIS_VWTESTER_25_2026-10-23.md). Testy należą do konkretnej kompilacji/wersji sprzętu, a nie całej rodziny produktów.


## Testy po powtórnej analizie 2.5

- **KCAN-D018 (status odpowiedzi TX):** najpierw rejestrować rzeczywiste odpowiedzi `0x60` podczas poprawnych testów na izolowanej magistrali; osobno testować parser programowo offline dla długości 0–4. Nie prowokować awarii CAN w aucie.
- **KCAN-D019 (filtry 6+2):** odczyt `0x52`, zapis pierwotnego bloku poza GitHub i kontrolowane zmiany pojedynczych pól dopiero na izolowanej magistrali. Porównać akceptowane ID przy każdej zmianie. Znaczenie bitów `0x40`/`0x60` nieustalone.
- **KCAN-D020 (ciągły RX):** podać kontrolowany strumień CAN o znanej liczbie ramek, mierzyć straty i przepełnienie przy różnym obciążeniu oraz, osobno, obecność ACK. Dane pełnych logów pozostają poza repozytorium.
- **KCAN-D021 (tryb):** przechwycić selekcję GUI i odpowiadający opcode `0x50`/`0x51`; nie zakładać mapowania CAN/K-Line przed pomiarem.
- **KCAN-D022 (walidacja):** przygotować testy jednostkowe parsera dla `0x70` długość 4 i 12, odrzucenia 3 i 13, `0x60` długości 0..4 i 5 oraz synchronizacji po śmieciach. Wszystkie te testy można zrobić **bez adaptera i bez wykonywania obcego EXE**.

Szczegóły i adresy kodu: [ANALYSIS_VWTESTER_25_FOLLOWUP_2026-10-23.md](ANALYSIS_VWTESTER_25_FOLLOWUP_2026-10-23.md).

## Osobne sprawdzenie Commandera „3.6” (KCAN-D043)

Nowy `VWTester.exe` z pakietu 3.6 zawiera wyłącznie **jawne zależności** `FTD2XX.dll` (`FT_Open/FT_Close/FT_GetDeviceInfo`) i `FTChipID.dll` (`FTID_GetChipIDFromHandle`), a kod CAN jest chroniony. To nie uprawnia do zakładania, że program używa FTDI D2XX do samej transmisji CAN.

1. Zacząć od **statycznej identyfikacji USB/FTDI i modelu PIC**, bez uruchamiania niezweryfikowanego programu i bez pojazdu.
2. Jeżeli uruchomienie będzie zgodne z procedurą bezpieczeństwa: w izolowanym systemie/stanowisku rejestrować **Win32 COM, wywołania D2XX/FTChipID, RTS/DTR oraz surowe bajty UART**, zanim oceni się protokół lub spróbuje nadawać CAN.
3. W razie wykazania znanych komend `0x50/51/52/53/55/60/70` porównywać odpowiedzi z zachowaniem referencyjnym 2.5 na **izolowanym CAN**, rozróżniając sprzęt i host; nie stosować w ciemno komend `0x53/55/60` do auta.
4. Zarejestrować i udokumentować wariant sprzętu/firmware, API, rzeczywisty baudrate, timeouty, odczyt i ACK; **obecność importu nie jest wywołaniem**. Sprawdzić oddzielnie użycie chip ID; nie obchodzić mechanizmów licencyjnych.

Pełna karta analizy: [ANALYSIS_VWTESTER_36_2026-10-23.md](ANALYSIS_VWTESTER_36_2026-10-23.md). Oryginalne programy, sterowniki, logi i dane urządzenia poza repo.

## Testy Commandera 3.0 beta/4.5 i dwóch prędkości COM (D044/D045)

Kod 4.5 ujawnił **warunkowy wybór 115200/833333 bit/s**, a obie nowe kompilacje potwierdziły format hosta CAN11 `0x60/0x70` oraz konstrukcję konfiguracji `0x53` (6+2). To nie są zweryfikowane funkcje posiadanego PIC.

- **Najpierw statycznie/offline:** w programie 4.5 rozpoznać wywołania funkcji `0x403170` i znaczenie parametru `0/1/>=2`; w programie 3.0 beta wyjaśnić ogólną walidację odpowiedzi `0x60` w tablicy deskryptorów. Nie zgadywać semantyki `0x55`, `0x54` itd. na podstawie pojedynczych wartości.
- **Później, w izolowanym środowisku bez pojazdu i po ocenie bezpieczeństwa EXE:** przy obserwacji znanego programu rejestrować użyty numer COM, rzeczywisty `DCB.BaudRate`, DTR/RTS, surowe bajty UART i kolejność inicjalizacji; nie instalować sterownika FTDI 2004 na normalnym systemie.
- **Tylko izolowana magistrala CAN** z drugim referencyjnym interfejsem: CAN11 ID 0x123, DLC=3 i 8, skutki konfiguracji `0x53`, dokładne straty i odpowiedzi `0x60` o długości 0–4, fizyczny ACK. Nie wysyłać niesprawdzonych komend do pojazdu.

Raport: [ANALYSIS_VAGCAN_30BETA_45_2026-10-23.md](ANALYSIS_VAGCAN_30BETA_45_2026-10-23.md), rejestr [DISCREPANCIES.md](DISCREPANCIES.md).

## Testy po odkryciu C0 i mapowania baud→PORT (D044–D046)

**Potwierdzenie z kodu hosta, nie sprzętu:** w starym Commanderze 4.5 `[COM] PORT` określa jednocześnie wybór COM i prędkość `115200` (`PORT=0/1`) albo `833333` (`PORT>=2`); w 3.0 beta zawsze 833333 w tej ścieżce. Oba nadają sekwencję `51 00 → C0 00 → 53 20[32]`. `C0` jest **nowym nierozpoznanym rozkazem** — nie wysyłać go w ciemno do własnego adaptera, szczególnie podłączonego do samochodu.

**Bezpieczny plan:**
1. **Offline**: porównać kod i tablice RX (3.0 `60 00` ściśle; 4.5 `0x60` N=0..4); opisać przyczynę dziwnego baud dla COM1 i granice tablicy 16 portów.
2. Przy badaniu komunikacji **bez samochodu** użyć izolowanego środowiska, zweryfikowanej aplikacji i bezpiecznych numerów **COM2–COM9**. **COM10+** w tych starych EXE jest problematyczne przez nazwę `COM%d`, a `PORT>=16` może przekraczać tablicę rekordów. Weryfikować systemowy `DCB.BaudRate`, rzeczywisty UART i DTR/RTS, bez założenia, że inne wydania sprzętu zadziałają.
3. Do eksperymentów `C0/53/60` używać **tylko odizolowanego, prawidłowo zakończonego stanowiska CAN** po poznaniu rodzaju płytki i trybu; nie wykonywać losowych rozkazów na pojeździe.
4. Pełny raport: [ANALYSIS_VAGCAN_30BETA_45_DEEP_2026-10-23.md](ANALYSIS_VAGCAN_30BETA_45_DEEP_2026-10-23.md). Wzorce `54 02` i `6F 00` to **sam walidator RX**, bez potwierdzenia, że zostały wygenerowane przez firmware.

## CAN29: izolowany test ID standardowego i rozszerzonego (D047)

Ponowna deasemblacja 3.0 beta/4.5 potwierdziła, że opisane funkcje `0x60/0x70` **gubią 18 wyższych bitów identyfikatora**. Nie można na tej podstawie przesądzić, jak konkretny PIC obsługuje *inne* komendy albo czy może obserwować EID29 bez wystawiania informacji hostowi.

1. **Offline:** przeprowadzić na własnym dekoderze test kolizji `ID 0x110` (standard) i `ID 0x18DAF110` (extended) — obydwa powodują w badanym kodzie ten sam nagłówek `22 00 00 00`. Nie proponować użytkownikowi wysyłki 29-bit po obecnym TX `0x60`.
2. Zidentyfikować faktyczny PIC/kontroler i firmware, zmapować cztery bajty UART osobno od *rejestrów* kontrolera (PIC `TXBnSIDL` ma inne przesunięcie, EXIDE nie wyznacza się bezpośrednio z `0x1C`).
3. **Odizolowana, terminowana magistrala CAN**, niezależny analizator obsługujący zarówno CAN11 jak CAN29. Najpierw nadać referencyjnie **ramkę standardową 0x110 i rozszerzoną 0x18DAF110** (nie na magistrali samochodu), obserwować RX PC↔PIC i ACK/listen-only, sprawdzać ewentualne aliasowanie i brak ramek. Jedynie po rozpoznaniu rzeczywistych komend można rozważyć TX extended.
4. `C0`, `51`, `53`, `55` i `60` **nie są** obecnie udowodnionymi przełącznikami CAN29; nie wysyłać ich do auta ani w ciemno do nieznanego sprzętu.

[Analiza z adresami kodu](ANALYSIS_CAN29_INIT_30BETA_45_2026-10-23.md), [KCAN-D047](DISCREPANCIES.md).

## Niezawodność COM, statusy TX i granice DLC (D048–D050; 2026-10-23)

Nowy audyt statyczny [ANALYSIS_SERIAL_TX_RELIABILITY_30BETA_45_2026-10-23.md](ANALYSIS_SERIAL_TX_RELIABILITY_30BETA_45_2026-10-23.md) pokazuje, dlaczego sama lista TX starego Commandera nie dowodzi CAN TX: writer portu ignoruje wynik `WriteFile/GetOverlappedResult`, nie weryfikuje `bytesWritten`, a funkcja TX zwraca sukces po `Sleep(10)`. Pozorny 258ms timeout 4.5 nie jest skuteczny po późniejszym `GetOverlappedResult(...,TRUE)`.

1. **Offline/własny mock portu:** sprawdzić i odtworzyć oddzielnie `WriteFile` pełny/częściowy, `ERROR_IO_PENDING`, błąd natychmiastowy, `WAIT_TIMEOUT`, zakończenie/cancel. W nowym programie nie kopiować semantyki „return 1”; wymagać sprawdzenia `bytesWritten==requested` i końcowego timeoutu.
2. **Kontrolowana inicjalizacja bez samochodu:** zmierzyć kolejność **SETDTR→500ms→CLRDTR→SETRTS** i skutki na konkretnym interfejsie; nie zakładać, że DTR resetuje PIC ani że RTS ma impuls w obie strony.
3. **Izolowana CAN z interfejsem referencyjnym:** zestawić cztery zdarzenia: wywołanie UART, ukończenie UART, odpowiedź PIC `0x60`, faktyczna ramka na CAN wraz z ACK/błędem; nie utożsamiać `GetTickCount` programu z czasem ramki CAN.
4. **DLC tylko offline:** własny encoder jawnie odrzuca `N>8`, test `N=0,3,8,9,255` wykonywać na własnym kodzie/mocku, **nigdy w starym EXE**, ponieważ kopiuje N bajtów do ograniczonego bufora stosu bez lokalnej walidacji.

Powiązane **KCAN-D048–D050** w [DISCREPANCIES.md](DISCREPANCIES.md), a testy sprzętowe **wyłącznie poza autem**.

## Weryfikacja pakietu 5.0+ECU z etykietą V5.1 (D051/D052)

**Rozpoznane statycznie:** `VAG-CAN Commander+EDC15.exe` z ZIP `V5.1` wyświetla w zasobach `5.0+ECU`, używa zwykłych komend hosta `51 00 → C0 00 → 53 20`, CAN11 `0x60/0x70` oraz UART 833333 w badanej ścieżce. Nie wykazano CAN29/IDE ani bezpieczeństwa transmitera. `memory.bin` 2048 B jest powiązany z obsługą plików, lecz jego rola jest nieznana.

1. **Offline:** ustalić semantykę kodu przy `0x4135E0` odnoszącego się do `memory.bin` i czy to wejście, wyjście, backup/EEprom lub inne; nie otwierać/rozpowszechniać surowych danych dla celów niekoniecznych. Prześledzić osobno obecność ewentualnych innych nadajników EID29 poza rozpoznanym `0x403520`.
2. **Bez samochodu:** sprawdzić numer COM zgodny z `Tester.ini`, fizyczną sekwencję DTR/RTS i baud; **nie instalować sterowników FTDI 2.04.06 na zwykłym komputerze wyłącznie dla eksperymentu**. `LatencyTimer=16` w INF jest domyślną wartością pakietu, nie aktualnym ustawieniem Windows.
3. **Na odizolowanym CAN z drugim analizatorem**: porównywać stany żądanie nadania / zakończenie UART / odpowiedź PIC / fizyczny CAN, a w pasywnym teście porównać CAN11 `0x110` i CAN29 `0x18DAF110`; **nie wysyłać nieznanych `C0/53/55/60` w samochodzie**. Nie uruchamiać otrzymanego EXE bez oceny bezpieczeństwa i środowiska izolowanego.

[Raport](ANALYSIS_VAGCAN_50ECU_V51_2026-10-23.md), [D051/D052](DISCREPANCIES.md).
