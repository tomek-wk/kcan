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
