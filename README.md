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
