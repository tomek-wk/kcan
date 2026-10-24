# kcan — VAG K+CAN Commander 1.4: dokumentacja protokołu

Repozytorium dokumentuje **protokół binarny między komputerem a interfejsem VAG K+CAN Commander 1.4** (FTDI / UART / mikrokontroler). Nie jest to opis protokołów diagnostycznych pojazdu, takich jak UDS, KWP2000, ISO-TP lub VW TP2.0.

**Status:** dokumentacja robocza, częściowo odtworzona przez analizę statyczną biblioteki J2534 oraz logów KCANTEST. **Nie zweryfikowano jej jeszcze na konkretnym niebieskim adapterze.** Klony i wersje firmware mogą się różnić.

## Dokumentacja

| Plik | Zawartość |
| --- | --- |
| [docs/PROTOCOL.md](docs/PROTOCOL.md) | Warstwa szeregowa, format pakietów, CAN11/CAN29 |
| [docs/COMMANDS.md](docs/COMMANDS.md) | Rejestr poleceń z poziomami pewności |
| [docs/FILTERS.md](docs/FILTERS.md) | 32-bajtowy blok konfiguracji / filtrów |
| [docs/EVIDENCE.md](docs/EVIDENCE.md) | Materiał dowodowy, liczby, adresy kodu, sumy kontrolne |
| [docs/SOURCES.md](docs/SOURCES.md) | Źródła, odnośniki i pochodzenie ustaleń |
| [docs/EXTERNAL_SOFTWARE.md](docs/EXTERNAL_SOFTWARE.md) | Inne implementacje i oryginalne oprogramowanie |
| [docs/OPEN_QUESTIONS.md](docs/OPEN_QUESTIONS.md) | Nierozstrzygnięte kwestie i priorytety |
| [docs/SAFE_TESTS.md](docs/SAFE_TESTS.md) | Plan ostrożnej weryfikacji na urządzeniu |

## Jak interpretować ustalenia

- **POTWIERDZONE (DLL + log):** zgodne przykłady z faktycznej transmisji oraz rozpoznany kod biblioteki.
- **POTWIERDZONE (DLL):** wynik analizy statycznej konkretnej biblioteki, niekoniecznie wszystkich wersji firmware.
- **OBSERWOWANE (log):** komunikacja widoczna w logu bez pełnej semantyki.
- **HIPOTEZA:** interpretacja do przetestowania; nie może być podstawą niekontrolowanego nadawania.

Skrót: `PC → PIC` oznacza kierunek danych *komputer → mikrokontroler adaptera*, nie ramkę CAN. Odpowiedź `60 00` nie dowodzi otrzymania ACK na fizycznej magistrali.

## Zasada repozytorium: tylko własna dokumentacja

**Nie umieszczamy tutaj pobranych ani dostarczonych plików:** archiwów RAR/ZIP, sterowników EXE/DLL, oryginalnego firmware, pełnych logów i obrazów instalacyjnych. Repozytorium zawiera wyłącznie opracowanie, krótkie przykłady protokołu, metadane (w tym SHA-256) i odnośniki do źródeł. Archiwa źródłowe pozostają poza repozytorium.

Nie uruchamiano nieznanych plików wykonywalnych; dotychczasowe wnioski pochodzą z analizy statycznej i logów.

**Stan dokumentacji:** 2026-10-23.

## Ostatnia analiza źródłowa

- **2026-10-23:** otrzymano `VAG-K_CAN_Commander_1[X].4.zip`, zinwentaryzowano 53 pliki i zbadano statycznie zabezpieczony `VAG-K+CAN Commander.exe`. Główny EXE jest **identyczny bajt po bajcie** z plikiem wskazanym wcześniej na GitHubie; nie odzyskano nowych poleceń komunikacji CAN. Wyniki: [ANALYSIS_ORIGINAL_EXE_2026-10-23.md](docs/ANALYSIS_ORIGINAL_EXE_2026-10-23.md).
- Sprzeczności, warianty i pytania wymagające testów zapisujemy w [DISCREPANCIES.md](docs/DISCREPANCIES.md), bez arbitralnego rozstrzygania ich na podstawie samej nazwy archiwum.

- **2026-10-23:** druga dystrybucja: `commander vag-k can.zip` (polskie instrukcje, instalator Setup Factory 8.0, sterowniki FTDI 2008). **Nie jest potwierdzoną nową wersją firmware ani nową implementacją protokołu.** Różnice i plan testów: [ANALYSIS_SETUP_FACTORY_2026-10-23.md](docs/ANALYSIS_SETUP_FACTORY_2026-10-23.md) oraz [DISCREPANCIES.md](docs/DISCREPANCIES.md).

- **2026-10-23:** archiwum `VAG K CAN COMMANDER FULL 1.4.zip` — ten sam EXE i DLL co w pakiecie `1[X].4`, dziewięć identycznych po normalizacji plików tekstowych; jedyna różnica zawartości to `Tester.ini` (`TARGET` i `FILEINDEX`). [Porównanie binarne](docs/ANALYSIS_FULL14_2026-10-23.md), [test KCAN-D011](docs/DISCREPANCIES.md).

- **2026-10-23:** otrzymano pierwszą rzeczywiście **inną kompilację** — `VWTester.exe` „Commander FULL 2.5”, rozmiar 688 128 B. Jego czytelny kod niezależnie potwierdza UART 833333 i CAN11 `0x60/0x70`, **ujawnia zmienną długość danych** oraz `0x50/0x51` i `0x53`. [Analiza 2.5](docs/ANALYSIS_VWTESTER_25_2026-10-23.md). Nowe testy: [rejestr rozbieżności](docs/DISCREPANCIES.md).

- **2026-10-23 — powtórna analiza FULL 2.5:** parser `0x70` długość 4–12 i `0x60` długość 0–4, strumieniowy odbiór COM, kolejki 2048 rekordów, wybór `0x50`/`0x51` zależny od GUI, oraz bloki `0x53` budowane jako **6 filtrów + 2 maski (hipoteza z kodu)**. [Raport uzupełniający](docs/ANALYSIS_VWTESTER_25_FOLLOWUP_2026-10-23.md); [testy](docs/DISCREPANCIES.md).

- **2026-10-23, trzecia analiza `VWTester.exe` FULL 2.5:** odtworzono dwa kompletne bloki konfiguracji `0x53`, w tym ID `0x200+x` i `0x300`; odnaleziono cztery tryby budowania wiadomości K-Line, rolę `60 00` w stanie programu, niepełną obsługę błędów zapisu COM i dodatkową ścieżkę `9600` po nieudanym ustawieniu portu. [Raport](docs/ANALYSIS_VWTESTER_25_DEEP_2026-10-23.md), [filtry](docs/FILTERS.md), [testy KCAN-D023–D028](docs/DISCREPANCIES.md). Nadal **brak testów na konkretnym adapterze**.

- **2026-10-23 — czwarta analiza `VWTester.exe` FULL 2.5:** wykryto bitowe inicjalizacje K-Line przez `SETBREAK/CLRBREAK` (8-bit oraz 7-bit+parity), osobne ustawienie COM **10472 bit/s**, parser echa i `7F ... 78`, możliwą nieskończoną pętlę ponawiania `TransmitCommChar` oraz obsługę COM10+. [Raport](docs/ANALYSIS_VWTESTER_25_KLINE_INIT_RX_2026-10-23.md) · [testy KCAN-D029–D035](docs/DISCREPANCIES.md). Te mechanizmy K-Line **nie są dodatkowymi opkodami protokołu CAN PC↔PIC**.


## Najnowsze ustalenia CAN i przekazanie do kolejnego czatu

- **2026-10-23, piąta analiza `VWTester.exe` 2.5 (tylko CAN):** oddzielne ścieżki `0x53` (inicjalizacja z kontrolą odpowiedzi vs okno „Set Filter” bez bezpośredniej kontroli), **dwa 2048-slotowe workery TX z `Sleep(10 ms)` po iteracji**, czas `GetTickCount` pochodzi z hosta i **nie jest sprzętowym timestampem CAN**, brak pewnej semantyki CAN29/listen-only. [Pełny raport](docs/ANALYSIS_VWTESTER_25_CAN_FOCUS_2026-10-23.md), [nowe testy KCAN-D036–D042](docs/DISCREPANCIES.md).
- **Przed następnym plikiem w nowym czacie:** zacząć od **[HANDOFF_NEXT_CHAT.md](docs/HANDOFF_NEXT_CHAT.md)**. Podano tam kompletny stan projektu, hashe wszystkich znanych wersji, źródła, mapę CAN, niedowiedzione funkcje, plan testów i zasady zapisu do repo.

Nadal obowiązuje zakaz umieszczania w repozytorium oryginalnych archiwów, programów, bibliotek i logów.

## Nowa analiza — wersja zainstalowana 1.4 (2026-10-23)

- Otrzymane `VAG K+CAN COMMANDER 1.4zainstalowany.rar` zawiera **ten sam bajtowo EXE 1.4** (`ea69c09b...`) i `RCMicroDogSetup.dll` (`5671711c...`) co wcześniejsze archiwa. Nie stwierdzono nowej implementacji CAN.
- `Uninstall/uninstall.xml` wskazuje jako źródło instalacji `Setup VAG K+CAN COMMANDER 1.4.exe`; jest to **pośrednia**, a nie kryptograficzna weryfikacja zawartości wcześniejszego instalatora. `Tester.ini` ma `FILEINDEX=1955` zamiast `1956` w `FULL 1.4`. Zaktualizowano **KCAN-D006 i D011**.
- [Pełne porównanie i ograniczenia](docs/ANALYSIS_INSTALLED14_2026-10-23.md). Nie dodano do repo żadnych materiałów źródłowych ani lokalnych danych użytkownika.

## Analiza VWTOOL / VDS-PRO 2.09 (2026-10-23)

- Archiwum `VWool 2 0 9 en PL.rar` (RAR4, 16 plików, SHA-256 `70b992d60f4b5cc014b30bca9fb6840ac213e883a7fd9378d92745e568a9079d`) zawiera **16-bitowy program VWTOOL/VDS-PRO 2.09**, a **nie nowy Commander ani implementację protokołu CAN PC↔PIC**.
- Dwie wersje `VWTOOL.EXE` / `VWTOOL-pl.EXE` różnią się bajtowo, w znacznej części przez polskie komunikaty; program używa Windows NE, Visual Basic 3 i portu szeregowego COM, z plikiem `VWTOOL.INI`.
- **Nowe ustalenie:** `ERRCODE4.CSV` i `LABELS.CSV` dekodują się przez **XOR 0x85** na każdym bajcie z wyjątkiem CR/LF; zawierają opisy usterek i 569 rekordów etykiet grup pomiarowych starszych ECU VAG. To **dane aplikacyjne**, nie ramki CAN.
- [Szczegółowy raport i hashe](docs/ANALYSIS_VWTOOL_209_2026-10-23.md). Brak zmiany protokołu i nowych zadań KCAN-D0xx. Nie publikowano binariów ani pełnych danych z programu.

## Nowy materiał — Polski VAG 4.9 (2026-10-23)

- Archiwum `Polski VAG 4.9(1).rar` (RAR4, SHA-256 `3febfd5015830fb6626134f6e13fed107f09ff2d7544e36ad244e4102d0c8e7f`) zawiera **jeden plik** `setup.exe`, SHA-256 `132d7d275a1b3a406a963f1a625a3ceb4bea174ea1a5b22135f4720d8db6046e`, zidentyfikowany jako **Inno Setup 5.2.1** / `Polski VAG` / `4.9` / `www.obd2.pl`.
- Rozpoznano stub PE32 i duże dane dołączone (99,33% EXE), ale **nie wydobyto wewnętrznych plików aplikacji**; nie ma potwierdzonego nowego kodu CAN Commandera. Publiczne źródła wskazują na **diagnostykę K-Line** i doniesienia o zgodności z *niektórymi* Commanderami K+CAN, bez dowodu współpracy z konkretnym egzemplarzem.
- [Analiza, hashe i ograniczenia](docs/ANALYSIS_POLSKI_VAG_49_2026-10-23.md). Nie zmieniono protokołu ani listy opkodów; brak nowych testów KCAN-D0xx. Bez publikowania oryginalnego RAR/EXE.

## Nowa kompilacja — VAG Commander „3.6” (2026-10-23)

- Archiwum `VAG COMMANDER 3.6(2).rar` — RAR4, **26 plików + 2 katalogi**, SHA-256 `4c4e448077836806c593ef2f08a948ee56d0bde73f6f7dd8f56148b0097403a4`.
- `VWTester.exe` **647 168 B**, SHA-256 **`a448ff313cce8ee2597f14675e51196ca5b677a5561833bb65965b05628d8a23`** — **nowa, różna kompilacja** od 1.4/2.5. Sekcje `.vmp0/.vmp1`, zaszyfrowana/skompresowana reprezentacja właściwego kodu; nie udało się statycznie odtworzyć wykonawczych funkcji CAN. **Numer „3.6” wynika z nazwy pakietu**, zasób FileVersion nadal `1.0.0.1`.
- **Nowy ślad:** jawne importy `FTD2XX.dll` ordinal `1/2/61` = `FT_Open/FT_Close/FT_GetDeviceInfo` oraz `FTChipID.dll` ordinal `8` = `FTID_GetChipIDFromHandle`. Są też importy Win32 COM; **nie ustalono**, która ścieżka służy do ramek CAN. `RCMicroDogSetup.dll` jest identyczne z 1.4/2.5. Sterowniki FTDI pochodzą z pakietu `2.00.00` (2006).
- [Raport statyczny i granice wnioskowania](docs/ANALYSIS_VWTESTER_36_2026-10-23.md); nowy **KCAN-D043** dotyczy zgodności protokołu tej wersji, powiązany z D003/D004/D015/D016. Brak nowych potwierdzonych opkodów CAN; oryginalne pliki poza repo.

## Porównanie trzech pakietów Commander „3.6” (2026-10-23)

- Dwa nowe źródła: `VAG K CAN COMMANDER FULL 3,6.rar` (RAR4, SHA-256 `e0059df5cb1e51434ae1eea95d4f7ff7234a176360fb739d2b382dbace83069b`) oraz `VAG-K CAN-V3.6.zip` (SHA-256 `9b59b9490c0011edea1976d9d4ad16a4671e1870b45576088f298ed23b5d8b32`).
- Zestawiono je z wcześniej analizowanym `VAG COMMANDER 3.6(2).rar`. We **wszystkich trzech dokładnie 25/26 plików jest bajtowo identycznych**; różni się wyłącznie `Tester.ini`: pierwsze `TARGET` to **6/6/0**, `FILEINDEX` to **1872/1877/1879**, przy niezmiennych COM2/COM2 i reszcie ustawień.
- `VWTester.exe` ma w każdym pakiecie SHA-256 **`a448ff313cce8ee2597f14675e51196ca5b677a5561833bb65965b05628d8a23`**. Nie znaleziono kolejnej kompilacji ani nowych informacji o opkodach CAN. [Porównanie z hashami](docs/ANALYSIS_VWTESTER_36_PACKAGES_2026-10-23.md). Zaktualizowano zagadnienia **D011 i D043**; nie dodano D044.

## Najnowsza analiza: VAG-CAN Commander 3.0 beta oraz 4.5 (2026-10-23)

- Archiwum `VAG-CAN Commander V4.5.zip`, **1 663 886 B**, SHA-256 `e7980df7b33847af86ad12c52ae99c377b39c1d8f067abbe12e2d8c5de5e2b1c`; **32 pliki, 3 katalogi**. Zawiera **dwie odrębne kompilacje**: `VAG-CAN Commander 3.0 beta.exe` (417 792 B; SHA-256 `dfb5e3f4724f6898c7c82d5d6e69ed3f795edb5f536f4aa5ff37ab17eae2a39b`) i `VAG-CAN Commander4.5.exe` (477 472 B; SHA-256 `85e89882a434ad83d19381ecbb5f9e77b14b237343b1432feb2f7300810e0050`).
- **Nowe niezależne potwierdzenie w wykonawczym kodzie hosta** dla obu EXE: CAN11 `0x60` TX z `length=N+4`, `0x70` RX z `length=4..12`, i konstrukcja `53 20` jako **6×4 + 2×4 B**. W 4.5 parser dodatkowo akceptuje odpowiedzi `0x60 length<=4`.
- **Istotna różnica:** 4.5 w kodzie otwierania COM wybiera **115200 bit/s przy parametrze <2** albo **833333 bit/s przy parametrze >=2**; 3.0 beta w badanej ścieżce używa **833333**. Nie mapowano parametru do nazw trybów GUI ani działania konkretnego adaptera.
- `Tester.ini` używa `[COM] PORT=4` (a nie osobnych `CAN_PORT/KWP_PORT`); dołączone FTDI INF są wersji **1.00.2154 z 2004**. Teksty diagnostyczne identyczne z 1.4 po normalizacji końców linii. [Pełna analiza z adresami x86](docs/ANALYSIS_VAGCAN_30BETA_45_2026-10-23.md); nowe **KCAN-D044/D045**. Wyłącznie analiza statyczna, bez uruchamiania programów i bez pomiaru interfejsu.

## Pogłębiona analiza 3.0 beta/4.5 — inicjalizacja, numer COM i odpowiedzi (2026-10-23)

- **Rozstrzygnięto znaczenie warunku `115200/833333` w 4.5:** argument `0x403170` to **numer portu odczytany z `[COM] PORT` w `Tester.ini`**, **nie tryb CAN/K-Line**. `PORT=0/1` wybiera 115200 bit/s, `PORT>=2` wybiera 833333 bit/s. W dołączonym pliku `PORT=4`, zatem kod wybiera COM4/833333. Podobna sekwencja INI istnieje w 3.0 beta, ale bez rozgałęzienia prędkości.
- **Nowy faktyczny rozkaz hosta:** oba EXE w badanej inicjalizacji wysyłają kolejno **`51 00` → `C0 00` → `53 20 [32B]`**, z przerwami 50 ms; to **`C0`**, nie `50` obserwowane w innych wersjach. Semantyka `C0` i zgodność firmware nieudowodnione.
- **Rozstrzygnięto różnicę odpowiedzi `0x60`** na poziomie kodu: 3.0 beta ma w deskryptorze `60 00` i przyjmuje dokładnie zero bajtów; 4.5 ma osobny walidator akceptujący **0–4**. Ośmiowpisowe tablice RX obejmują także `C0 00, 51 00, 52 20, 53 00, 54 02, 6F 00` (oczekiwane odpowiedzi, nie automatycznie wykonane komendy).
- **Ryzyko COM10+:** oba starsze EXE przekazują do `CreateFileA` nazwę `COM%d` bez prefiksu `\\\\.\\`, dlatego w typowym Windows **COM10+ nie zadziała tą ścieżką**; 2.5 ma osobne wsparcie rozszerzonego formatu.
- [Raport z adresami i tabelami](docs/ANALYSIS_VAGCAN_30BETA_45_DEEP_2026-10-23.md); aktualizacja **D044/D045**, nowy **D046**. Potwierdzenia dotyczą hosta, nie firmware.

## Audyt inicjalizacji i CAN29 w Commander 3.0 beta/4.5 (2026-10-23)

Po ponownej deasemblacji obu EXE potwierdzono **ograniczenie do CAN11 w zbadanych wykonawczych ścieżkach TX/RX**: funkcje `0x403510`/ `0x4034F0` pobierają ID jako **WORD**, emitują tylko `(ID>>3)&FF`, `(ID&7)<<2`, `00 00`; odbiorniki `0x402D10`/`0x402CE0` rekonstruują tylko 11 bitów. Na przykład CAN29 `0x18DAF110` i CAN11 `0x110` dałyby **identyczne cztery bajty nagłówka `22 00 00 00`**. To ograniczenie **kodu hosta**, nie dowód braku CAN29 w każdym firmware/adapterze.

Sekwencja init obu: COM → `51 00` → `C0 00` → `53 20[32 B]`; początkowy blok 0x53 składa się z sześciu `FF 1C 00 00`, następnie `FF 1C 00 FF` i `FF 1C 00 00`. **Nie znaleziono jawnego przełączenia CAN29**. Bajt formatu UART nie jest rejestrem PIC `SIDL`: standardowe bity ID są przesunięte o 2 (protokół PC↔PIC), a w hipotetycznym PIC18F248/258 byłyby w bitach 7–5. Nie interpretować wartości `1C` jako flagi EXIDE.

[Pełny raport z adresami i ograniczeniami](docs/ANALYSIS_CAN29_INIT_30BETA_45_2026-10-23.md), nowe **KCAN-D047**, bez modyfikowania potwierdzonych opkodów. Nadal brak fizycznej walidacji konkretnego adaptera.

## Audyt niezawodności UART i pozornego sukcesu CAN TX (2026-10-23)

- Odtworzono niskopoziomową funkcję **`0x408BD0`** z niezależnych EXE **3.0 beta i 4.5**: `WriteFile` z OVERLAPPED, błędnie uproszczona obsługa wyniku, bez weryfikacji liczby zapisanych bajtów. Jeśli uchwyt COM nie ma wartości `INVALID_HANDLE_VALUE`, funkcja zwraca **1 nawet po nieudanej próbie**, bez sprawdzenia błędu API.
- **Wersja 3.0 beta** wywołuje `WaitForSingleObject(INFINITE)`; **4.5** używa tam `258 ms`, ale następne **`GetOverlappedResult(...,TRUE)` może nadal czekać bez limitu**. Nie jest to skuteczny końcowy timeout.
- **CAN TX `0x60`** `0x403510/0x4034F0` ignoruje wynik funkcji write, zapisuje lokalny rekord TX i `GetTickCount`, wykonuje **`Sleep(10)`**, po czym zwraca sukces **bez oczekiwania na fizyczny ACK ani potwierdzenie transmisji przez PIC**. Lista TX nie jest dowodem obecności ramki na CAN.
- Przy otwieraniu COM obie wersje żądają **SETDTR → Sleep(500 ms) → CLRDTR → SETRTS**; fizyczny wpływ na FTDI/PIC pozostaje nieznany.
- TX kopiuje **N bajtów do lokalnego bufora stosu bez jawnej w tej funkcji walidacji `0<=N<=8`**. Przetestowanie złych N w oryginalnym EXE jest niebezpieczne; własny klient powinien walidować na wejściu. Dodatkowo rozpoznano surową ścieżkę GUI nadawania bajtów i indeksowanie rekordów według `channel<<11|ID11`, ale to **nie dowodzi CAN29**.
- [Raport statyczny z adresami i sprawdzonymi importami](docs/ANALYSIS_SERIAL_TX_RELIABILITY_30BETA_45_2026-10-23.md). Zaktualizowano [D048–D050](docs/DISCREPANCIES.md); bez nowego protokołu sprzętowego.

## V5.1 ZIP — faktyczny program 5.0+ECU, nowe EDC15 i CAN11 (2026-10-23)

- `VAG-CAN Commander V5.1.zip`: 1 113 420 B, SHA-256 `151913526f55e2528ccf153a0d47b69d67d53dde96ed8057af9efe083aeea94f`, **28 plików i 4 katalogi**. `VAG-CAN Commander+EDC15.exe` **466 968 B**, SHA-256 **`811bf59355614e0d07aa2e4c10fedd01fbff2b0148feab4491f0f731c98d45ba`**. Zasób UI mówi **`VAG-CAN COMMANDER 5.0+ECU (full)`**, więc nazwa „V5.1” archiwum nie jest dowodem wersji EXE/firmware.
- Nowy, częściowo czytelny **PE32 Win32 COM**, w badanej ścieżce UART **833333**; `Tester.ini` ma `CAN_PORT=5`, `KWP_PORT=5`. Inicjalizacja hosta **`51 00 → C0 00 → 53 20 [32B]`**; blok początkowy **7×`FF 1C 00 00` + rekord #6 `FF 1C 00 FF`**.
- CAN TX `0x403520` i RX `0x402CE0` w kodzie przenoszą **tylko 11-bitowe ID** (`0x60/0x70`); brak ujawnionej alternatywy EID29 w tych funkcjach. Kontynuują też starsze ryzyka: UART writer może oczekiwać bez limitu i nie kontroluje `bytesWritten`; TX wpisuje historię i zwraca sukces bez dowodu sprzętowego ACK.
- **Nowy plik `memory.bin`, 2048 B**, ma odniesienie w EXE; nieustalone dane/rola (nie dowiedziono firmware PIC), **nie publikować**. Wszystkie cztery pliki tekstowe danych identyczne z 1.4 po CRLF→LF. FTDI sterowniki **2.04.06 (13.03.2008), i386+amd64**, brak bezpośredniego importu D2XX przez EXE.
- [Raport analizy](docs/ANALYSIS_VAGCAN_50ECU_V51_2026-10-23.md), nowe **KCAN-D051/D052**, aktualizacja wiedzy D047/D048/D049/D050. Analiza statyczna, bez uruchamiania i bez dodawania archiwum/binarki.

## Dalsza analiza V5.1: plik memory.bin i pełniejszy transport TP2.0 (2026-10-23)

- **Rozstrzygnięto istotną część D052:** `memory.bin` jest w badanej ścieżce **plikiem wynikowym ReadMemory**, nie potwierdzonym obrazem firmware PIC: `0x4135E0` otwiera go przez `CFile::Open(0x1001 = modeCreate|modeWrite)`, `0x413A13/0x413A86` zapisuje bajty, `0x413DC4` zamyka, a `0x413DD0` używa komunikatu `ReadMemory - Done.`. **Uruchomienie tej procedury może nadpisać istniejący plik!** Pochodzenie 2048B próbki w ZIP nadal nieznane.
- Nowe rozpoznanie `0x414F40`: trzy predefiniowane nominalne limity odczytu **512 KiB / 16 KiB / 4 KiB**, porcje odpowiednio **64/64/16 B**, różne adresy startowe i tryb parametrów własnych `0xFF`. Nie utożsamiać z długością dołączonej próbki.
- **Potwierdzono w kodzie transport VAG TP2.0 ponad CAN11**: `0x420360` tnie wiadomości na maks. **7 bajtów danych/ramkę**, dodaje 4-bitową sekwencję i znaczniki `0x10/0x20/0x00`, respektuje parametr block-size i kieruje każdą ramkę przez `0x4207D0→0x403520` do opkodu UART `0x60`; RX ma obsługę potwierdzeń `B0|sequence`. To **nie nowy protokół CAN29**.
- W `0x420360` wykryto dwie **potencjalnie nieograniczone pętle aktywnego oczekiwania** oraz lokalnie niezweryfikowany dzielnik block-size (możliwość dzielenia przez 0, o ile nie sprawdzono go wcześniej). **Nowe D053/D054** dotyczą protokołu transportowego i odporności aplikacji, a nie zmian firmware.
- [Pełny raport z adresami, mapą MFC, stanami i ograniczeniami](docs/ANALYSIS_VAGCAN_50ECU_V51_MEMORY_TP20_2026-10-23.md).

## Ponowny audyt wszystkich dostępnych plików — bez chronionych EXE (2026-10-23)

- Sprawdzono integralność i manifesty **8 dostępnych archiwów**. Do analizy kodu użyto **wyłącznie czytelnych instrukcji** trzech różnych programów: Commander **3.0 beta**, **4.5** oraz **5.0+ECU** z ZIP V5.1. Chronione główne EXE **1.4**, trzy identyczne **3.6** i niedostępną zawartość programu Polski VAG z instalatora **pominięto bez prób odszyfrowywania**; VWTOOL NE/VB3 sprawdzono tylko pod kątem jawnych danych K-Line.
- **Nowość:** wszystkie trzy dostępne czytelne EXE mają rzeczywisty kod **VAG TP2.0**, a nie wyłącznie 5.0+ECU: segmentery `0x4166E0`, `0x417FB0`, `0x420360`. Zbieżność instrukcji i wspólne błędy wskazują na **dziedziczony kod**, nie trzy niezależne projekty.
- **Wspólna nieosiągalna gałąź handshake:** `AND EAX,0xFF` bezpośrednio przed `CMP AX,0x300` uniemożliwia wejście do wskazanej obsługi A1/A3. Nie oznacza to automatycznie niesprawności całego TP2.0.
- **Ważne ryzyko odbioru:** legalna ramka CAN z **DLC=0** może trafić do ogólnego składania TP2.0, gdzie `dec ecx` przed `rep movsd` zamienia długość `0` w `0xFFFFFFFF`. Zbadana ścieżka ma brak ogólnej walidacji `DLC>=1`; **nie twierdzimy**, że awaria występuje dla każdej pustej ramki.
- Dodatkowo odbiór ACK sprawdza `control & 0xB0 == 0xB0`, przez co m.in. `0xF0` również przechodzi test maski (przy zgodnym ID kanału). Nie znaleziono nowego CAN29 ani opkodu.
- [Pełny audyt z adresami, inwentarzem i poziomami dowodów](docs/AUDIT_READABLE_FILES_2026-10-23.md), aktualizacje **D053/D054**, nowe **D055/D056**. Bez uruchamiania obcych plików i bez binariów w repo.

## Lista kandydatów na dumpy PIC i nieudanych odczytów (2026-10-23)

W nowym [rejestrze **14 tropów firmware i prób odczytu**](docs/FIRMWARE_DUMP_LEADS_2026-10-23.md) zapisano odnośniki do potencjalnych obrazów PIC18F2480 (`pic18f2480.hex` w `KCAN-ELM327.RAR`), PIC18F248/PIC18F258 (`PIC18F248.rar`), PIC18F25K80 (`CAN-PIC18F25K80.rar`, 36,65 KB) i aktualizatora firmware dla alternatywnego **NXP LPC2119FBD64**. Zweryfikowano też pierwotną relację o zgraniu firmware z Commandera 1.4 oraz **nieudane próby odczytu FLASH/EEPROM przy ochronie kodu**, a także przypadki błędnej weryfikacji i zapisu. **Żaden wsad procesora nie został jeszcze pobrany ani zweryfikowany kryptograficznie**. Odróżniono EEPROM FTDI, ECU `memory.bin` i raporty dongla od kodu mikrokontrolera. Repo zawiera **wyłącznie dokumentację i odnośniki**.

## Szersze poszukiwania firmware 1.4–6.0 i próby otwierania plików (2026-10-24)

Uzupełniono [rejestr kandydatów FD-001–014](docs/FIRMWARE_DUMP_LEADS_2026-10-23.md) o [**FD-015–024: niezależne źródła, wersje 5.5 i 4.8–6.0, wyniki prób pobierania oraz sprawdzony przykład Intel HEX**](docs/FIRMWARE_DUMP_FOLLOWUP_2026-10-24.md). Najważniejszy nowy załącznik z CXEM 2025: `CAN-PIC18F25K80.RAR` w osobnym wątku **VAG K+CAN** (dostęp do bajtów zablokowany); ten sam autor opisuje RTS jako przełączenie K-Line/PIC oraz DTR jako reset. Potwierdzono nieaktywne historyczne odnośniki do dziesięciu aktualizatorów **innego urządzenia, ARM SuperVAG K+CAN**. Odczytano i sprawdzono sumy kontrolne trzech **publicznych, niepowiązanych z Commanderem przykładów** `.hex` PIC18FxxK80 z GitHub — **nie są wsadami naszego urządzenia**. Nadal **nie ma żadnego pobranego i zweryfikowanego wsadu MCU Commandera**.

**FD-025 (2026-10-24):** [Carmasters — VAG K+CAN Commander, 27.03.2015](https://carmasters.org/topic/5640-vag-kcan-commander/) wymienia **`PGMKCAN2.rar`** jako „firmware i program do testowania”, odpowiadając użytkownikowi adaptera **FT232RL + LPC2119FBD64** (wcześniej działał z PC Commander 1.4). **Nie pobrano; forum 403, brak mirrora; nieznane wnętrze/target**. Historyczne skargi na brak pobrania już w 2015 i 2019. Szczegóły i ważne zastrzeżenia w [FIRMWARE_DUMP_FOLLOWUP_2026-10-24.md](docs/FIRMWARE_DUMP_FOLLOWUP_2026-10-24.md).

## Inne źródła firmware i aktualizatorów — nowe ślady 2026-10-24

Nowy raport: [FIRMWARE_ALTERNATIVE_SOURCES_2026-10-24.md](docs/FIRMWARE_ALTERNATIVE_SOURCES_2026-10-24.md) — **FD-027–FD-033**, poszukiwania na GarageForum, MHH Auto, Elektrodzie, GitHub i otwartych indeksach/mirrorach, wraz z oceną prób pobrania oraz relacjami o błędach aktualizacji.

- **FD-027, inny protokół:** GarageForum 2018 potwierdza nazwę konkretnego HEX **`cable_7i_PIC18F4685__SN17000_firmware44.hex`**, a także firmware 58 i starszy PIC18F2685 w rodzinie SuperVAG. Treść forum dostępna, **odnośniki HEX ukryte przez logowanie, brak bajtów**.
- **FD-028, kandydat do przeanalizowania w pierwszej kolejności dla Commandera:** MHH „**K+can com 3.6 UPDATER TOOL**” — zindeksowany opis twierdzi, że aktualizuje firmware interfejsu 1.4 do 3.6. **HTTP403; nie pozyskano aktualizatora**, więc nie wiadomo, czy zawiera obraz PIC i jak działa.
- **FD-029:** Elektroda 2011 `vag can.rar` 1,54 MB opisany jako **„program i wsad do naprawy kabelka”** po nieudanym upgrade VCDS; autor zgłosił skuteczną naprawę. **Wymagane logowanie, pobranie nie powiodło się**. Może dotyczyć **tylko EEPROM FTDI**, nie przypisywać procesorowi bez dowodu.
- **FD-030, korekta:** `VAGKCANUpdate V1.0.6/1.0.8/1.1.0/1.1.2` z archiwów 2011 jest **Super VAG K+CAN Plus 2.0** w MHH, a **nie potwierdzonym aktualizatorem Commandera**.
- **FD-031:** „cable not responding” przy próbie aktualizacji SuperVAG firmware 58 (09.2018) jest **niepowodzeniem aktualizacji, a nie odczytu Flash**.
- **Wynik:** **nadal żaden nowy oryginalny obraz MCU ani updater nie został pobrany**, brak analizy bajtów takich plików, żaden adapter nie był dotykany. Zebrane referencje i cele statycznej analizy bez publikowania cudzych binariów.

## 2026-10-24 — bezpośrednie archiwa i negatywny test firmware 3.6 w 1.4

Nowy raport: [**FIRMWARE_DIRECT_DOWNLOADS_AND_NEGATIVE_TESTS_2026-10-24.md**](docs/FIRMWARE_DIRECT_DOWNLOADS_AND_NEGATIVE_TESTS_2026-10-24.md), **FD-034–FD-042**. Na [tieCAR.net](https://www.tiecar.net/forums/index.php?topic=1587.0) odnaleziono bezpośrednie archiwa `https://www.tiecar.net/downloads/sw/VAG_K%2BCAN_Commander_v36.zip` oraz `https://www.tiecar.net/downloads/sw/VKCC_ALL.ZIP`, do których WWW otrzymuje odpowiedź **`application/zip` (nierozpoznawana przez czytnik; NIE pobrano bajtów)**, podczas gdy linki 1.4/2.5 zwracają **404**. Osobny [katalog producenta](https://www.tiecar.net/support.html) zawiera `winCAN_FW_v1000087.zip` opisany jako firmware własnego USB-CAN (również ZIP, bez analizy zawartości).

**Ważny negatywny wynik (FD-039):** [Elektroda, dob12, 16.04.2014, post #34](https://www.elektroda.pl/rtvforum/topic2198051-30.html) — autor pisze, że **wsad 3.6 zastosowany do kabla 1.4 „nie ruszył”**, bez szczegółów procesora, programatora ani pliku; w tym samym wątku inny użytkownik deklaruje zgodność **aplikacji PC** 1.4/2.5/4.5/5.1 z jednym kablem (nie oznacza firmware MCU!). **FD-042: korekta pewności** — MHH Auto o `K+can com 3.6 UPDATER TOOL` zawiera **sprzeczne sugestie**, czy aktualizuje Commander 1.4 czy **Super VAG**, dlatego target klasyfikujemy **nieznany** aż do pozyskania programu. Żadnych nowych wsadów MCU nie uzyskano ani nie wykonywano.


## HUD ECU Hacker 6.1 — instalator odzyskany i analizowany (2026-10-24)

Raport: [**ANALYSIS_HUD_ECU_HACKER_61_KCAN_2026-10-24.md**](docs/ANALYSIS_HUD_ECU_HACKER_61_KCAN_2026-10-24.md). Udało się **bez uruchamiania instalatora** wydobyć z zaszyfrowanego Blowfish kontenera `CRYP` pełny CAB (278 plików), w tym rzeczywisty `ECU_Hacker.exe` **6 449 152 B; SHA256 `b70fa891953927da0600eac420d18acdc15a39bdba25dad366e1c52a602eeeb8`**. Poprzedni wymóg dostarczenia osobnego EXE jest **nieaktualny**. Wydobyto `Version History.rtf` potwierdzający dedykowane VAG K+CAN **v5.3**, wydajność szybkiego CAN **v5.6** i dodatkowe prędkości **v5.9**. W .NET IL potwierdzono referencje do `SerialPort`: `set_BaudRate`, `set_DtrEnable`, `set_RtsEnable`, `Read`, `Write`; zlokalizowano kandydatów bitrate **MethodDef RID 6013 (RVA 0x351A24)** i **RID 7728 (RVA 0x3ABB7C)**. **Nie wykazano jeszcze powiązania RID z interfejsem Commander, konkretnych bajtów UART, filtrowania 0x53, trybu listen-only ani CAN29**. Kod jest silnie obfuskowany. Brak PDB w rzeczywistej zawartości. Przyszły etap: call graph IL → identyfikacja ścieżki Commander → format komend → capture pasywny. Nie commitować cudzych binariów.


## 2026-10-24 — HUD ECU Hacker 6.1: potwierdzona ścieżka protokołu VAG K+CAN Commander

**Nowsze ustalenia zastępują wcześniejszą hipotezę o RID 6013:** [ANALYSIS_HUD_ECU_HACKER_61_PROTOCOL_2026-10-24.md](docs/ANALYSIS_HUD_ECU_HACKER_61_PROTOCOL_2026-10-24.md). W statycznej analizie obfuskowanego IL odnaleziono **TypeDef328**, w którym spójnie występują operacje `0x53` (RID3648; 8×4 B: 6 filtrów, 2 maski), `0x54` (RID3654), `0x55` (RID3643; bitrate), `0x60` (RID3651; CAN TX), `0x70` (RID3652; CAN RX). **RID3644** oblicza `round(1000000 / bitrate)-1`; nadawany pakiet `55 03 N FA 07` jest **niezależnie zgodny z wcześniej znanym kodem DLL i logiem 500 kbit/s (`55 03 01 FA 07`) w [PROTOCOL.md](docs/PROTOCOL.md)**. HUD ustawia żądane UART **830000**, nie utożsamiać bez pomiaru z fizyczną prędkością FTDI. `RID3647` ustawia show-all poprzez osiem zerowych wartości logicznych (samo 32B na UART może mieć dodatkowe flagi). `RID3655` ma ścieżkę pakowania 29-bit CAN po stronie hosta, **bez potwierdzenia możliwości MCU**. W lokalnym `Translation/Template.xml` autor twierdzi, że dla VAG K+CAN **ACK nie można wyłączyć** — HUD nie oferuje true listen-only. **Wcześniejsza metoda RID6013 dotyczy innego, tekstowego adaptera**, nie dowodzi Commandera. Nie uruchamiano Windows EXE i nie podłączano sprzętu.


## 2026-10-24 — HUD 6.1: dokładny format 4-bajtowego CAN ID i maski 0x53

[**Analiza wykonania RID3655/RID3656/RID3649 i parsera RID3650**](docs/ANALYSIS_HUD_ECU_HACKER_61_CODEC_RX_FOLLOWUP_2026-10-24.md) · [**Koder referencyjny Python (offline)**](tools/hud_kcan_codec.py). **Źródło:** odzyskany `ECU_Hacker.exe` 6.1, SHA256 `b70fa891953927da0600eac420d18acdc15a39bdba25dad366e1c52a602eeeb8`. Obfuskowane IL wykonano w interpreterze instrukcji i porównano z wcześniejszymi wynikami DLL oraz EXE 2.5; **żadnego fizycznego adaptera nie testowano**.

- `RID3655` **CAN11** ID `0x123` → `24 0C 00 00`; **CAN29** ID `0x01ABCDE3` → `0D 4B CD E3`; `RTR` ustawia bit `0x00800000` w czterobajtowym słowie. `extended || isMask` ustawia `0x00400000`.
- **Formuła:** `v = extended ? id : (id << 18)`; `w = (((v & 0xFFE00000) << 3) | (v & 0x001FFFFF)) & 0xffffffff`; następnie dodanie flag, `w` zapisane **big-endian**.
- `RID3656` wykonuje operację odwrotną, ale używa **osobnego globalnego trybu `mode29` z FieldDef 0x0400085F** do odróżnienia CAN11 od CAN29. Zdekodowano `out RTR` z bitu 23. Wynik **nie dowodzi CAN29 w MCU PIC**, ale potwierdza implementację protokołu po stronie HUD.
- **`0x53` show-all CAN11**: `53 20` + 6×`00 00 00 00` (filtry) + 2×`00 40 00 00` (maski); **CAN29**: `53 20` + 8×`00 40 00 00`. To są **bajty hosta**, nie gwarancja skuteczności lub true listen-only.
- `RID3649` emulowany z interceptem `Write`: `54 00`, `55 03 01 FA 07`, `60 07 24 0C 00 00 11 22 33`; szczególny wariant **`0x60` kończy się bez synchronicznego wywołania parsera odpowiedzi**. `0x53/0x54/0x55` odczytują odpowiedź przez RID3650, z timeoutem zadanym przez caller.
- `RID3650` **RX**: buforuje opcode i długość, po `0x70` dekoduje ID z **offsetu 2** przez RID3656, a dane CAN z **offsetu 6**; odkłada pakiety w kolejce. Pełna maszyna stanów, resynchronizacja i dokładna semantyka innych statusów **do dalszego odtworzenia**.
- 8 lokalnych testów zestawów wektorów oraz 20 000 dodatkowych losowych round-tripów kodera/dekodera przeszło poprawnie. Wszystkie wyniki kodera są **potwierdzone w symulacji IL hosta, nie na fizycznym adapterze**.


## 2026-10-24 — HUD 6.1: odbiór asynchroniczny i kolejka CAN (RID3650/3652)

[**Pełna analiza maszyny stanów RX**](docs/ANALYSIS_HUD_61_RX_STATE_MACHINE_2026-10-24.md) · [**Referencyjny parser offline**](tools/hud_kcan_rx_parser.py). Wykonanie obfuskowanego IL `RID3650` w interpreterze z atrapą portu: odbiera `opcode,length` i dalsze `length` bajtów; **`0x70` jest odkładane do FIFO nawet podczas oczekiwania na odpowiedź `0x54` lub `0x55`**. Potwierdzony przypadek dwóch kolejnych `0x70` i następnie `54 02 AA BB` → dwie ramki zakolejkowane, zwrócona odpowiedź `0x54`. Przeplatane `0x60` przed odpowiedzią sterującą jest pomijane. Format `0x70` dopuszcza **length 4..12** (4 B identyfikatora, 0..8 B Classic CAN); `<4` albo `>12` powoduje błąd, nie akceptację. Nieoczekiwane opcode inne niż specjalne `0x70/0x60` zgłasza wyjątek. `RID3650` ani `RID3652` nie mają własnych sekcji wyjątków — **brak dowodu automatycznej resynchronizacji** po korupcji UART w tej warstwie.

`RID3652` pobiera ramki FIFO i **co najmniej po 2000 ms od poprzedniego sprawdzenia** wywołuje `RID3654` / polecenie **`54 00`**, z którego zapisuje statusy `response[2],response[3]` (semantyka poszczególnych bitów jeszcze nieznana). Wskazówka architektoniczna: obsługiwać jednocześnie odbiór strumieniowy i odpowiedzi synchroniczne, nie uruchamiać dwóch konsumentów COM. Model transportu z atrapami nie jest pomiarem FTDI/PIC, nie dowodzi niezawodności w dużym ruchu. Skrypt parsera nie otwiera COM; porównania z symulacją IL dla opisanych wektorów i testy fragmentacji przeszły. **Ważna poprawka badawcza:** początkowe błędne wyniki emulatora wynikały z braku implementacji `List.Clear`, a nie z pętli w HUD.
