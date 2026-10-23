# Materiał dowodowy i granice wnioskowania

Stan: **2026-10-23**. Analiza statyczna przekazanych archiwów (bez uruchamiania EXE/DLL) i dekodowanie pięciu logów KCANTEST. Dokumentujemy wyłącznie rezultaty, nie przechowujemy plików źródłowych.

## Archiwa analizowane poza repozytorium

| Archiwum | SHA-256 |
| --- | --- |
| `J2534KCANv1.0.0.10.zip` | `3f3a28acc6fea0feaac4da68f54f50109fc245b00b77da88355aa81050187f1d` |
| `kcantv10.rar` | `528eeb8bbd52198c61fa7df78e4a499b16c56918abc17616f58db99c3a955d82` |
| `kcantv11.rar` | `f83e9d4f4e445d2246d1de20ba7e67ab71a8aa3794bd988c11b36f1b6c1f2f12` |
| `kcantv10_log.rar` | `da73e54ab01d0f0d3b647bb6b070a25761294c035c9619dc540597f746aca9e9` |
| `kcantv11_log.rar` | `cb9eff5fd6373745de08ce2e780f2c4aa22d79272a3db7f01d015c7a10bba17e` |

SHA-256 sprawdzono ponownie na oryginalnych pięciu archiwach. Służą identyfikacji materiałów, **nie do ich rozpowszechniania**.

### Istotne binaria z archiwów (metadane; pliki nie znajdują się w repo)

| Plik | Rozmiar | SHA-256 |
| --- | ---: | --- |
| `J2534KCAN.dll` | 154624 B | `3b8cc66f95a174a0a3b5c94a5a8976e34c5211798dbdfd8105903038fd2bf09b` |
| `j2534KCAN.exe` | 520704 B | `6115f8ec95c58c3c891499ebed90e6983b2464837d255d2276deff765c4474d6` |
| `kcant.exe` v1.0 | 712192 B | `16e085139658b2392d990a14370710d46fa3f4a2af82778d77ad54116e3db4cf` |
| `kcant.exe` v1.1 | 712192 B | `bfd1f0fadbffc2b33cec6541450216ef556074543dbb540ef1830e5e435470fc` |

Biblioteka J2534 jest 32-bitowym PE. W kodzie są importy Win32 Virtual COM, prędkość UART `833333`, konstrukcja poleceń `0x52,0x53,0x55,0x5F,0x60` i dekodowanie `0x70`. Szczegóły: [COMMANDS.md](COMMANDS.md).

## Wyniki dekodowania pięciu logów

| Log | TX `0x60` | RX `0x70` | Uwagi |
| --- | ---: | ---: | --- |
| `100515_145927.log` | 726 | 726 | ucięty końcowy wpis, wiele zer |
| `100515_145938.log` | 1355 | 1355 | |
| `100515_145946.log` | 812 | 812 | |
| `100515_162815.log` | 547 | 547 | odmienna kolejność inicjalizacji |
| `100515_162820.log` | 641 | 641 | |
| **RAZEM** | **4081** | **4081** | |

Zliczono **4081 transakcji testera**, ale tylko dla CAN11: ID `0x7E0` / `0x7E8`. Nie jest to potwierdzenie różnych adresów, obsługi CAN29, filtrów, sniffera ani ACK na magistrali.

W jednym logu jest uszkodzony / ucięty wpis. Zrzut ekranu KCANTEST wykazuje również komunikat błędu transmisji; nie należy wyprowadzać z równej liczby TX/RX twierdzenia o bezbłędnej komunikacji.

## Krótkie przykłady zaobserwowane w logach

```text
52 00
52 20 FF 1F FF FF ... (32 B payload)

55 03 01 FA 07
55 00

60 0C FC 00 00 00 01 3E 00 00 00 00 00 00
60 00
70 0C FD 00 00 00 01 7E 00 00 00 00 00 00
```

Niniejsze fragmenty są **opracowaniem dokumentacyjnym**, nie kopią logów w całości.

## Odrębny pakiet oryginalnego programu

W publicznym repozytorium `Skylakc/BoschME7.5-Tools` znaleziono plik `tools/VAG-K_CAN_Commander_1[X].4/VAG-K+CAN Commander.exe` (1 060 864 B, Git blob SHA `daffe47c50f0e6554c91c723f3774aacc6d9b845`). Kod binarny **nie został pobrany i nie wykonano jego deasemblacji**. Analizowano tekstowe pliki `Tester.ini`, `installation 1.2-6+.txt`, `bugfixes open issues.txt`. Instrukcja opisuje też oddzielny klucz sprzętowy USB; kompatybilność pakietu z niebieskim klonem jest nieznana.

Źródła i linki: [SOURCES.md](SOURCES.md).


---

## Uzupełnienie — dostarczony oryginalny pakiet Commander 1[X].4 (2026-10-23)

- `VAG-K_CAN_Commander_1[X].4.zip`: **SHA-256** `6912218b24524ae629f7ccfa77599aca3823132ea77e42e0145f155a32852028`; 56 pozycji ZIP, z tego **53 pliki**, 3 katalogi, 7 404 037 bajtów danych po rozpakowaniu.
- `VAG-K+CAN Commander.exe`: **1 060 864 B**, SHA-256 `ea69c09b51fda25107d9926d7d033f4e25f5374ec0dd2b1bc4a9867a7b19b932`, Git blob SHA-1 `daffe47c50f0e6554c91c723f3774aacc6d9b845`. **Git blob SHA odpowiada dokładnie** plikowi w `Skylakc/BoschME7.5-Tools`, zatem jest to ta sama wersja binarna, nie drugi niezależny egzemplarz.
- Pliki `Tester.ini`, `RCMicroDogSetup.dll`, `installation 1.2-6+.txt`, `bugfixes open issues.txt`, `FixDiag.ini`, `FTD2XX.dll` i `VAG.txt` również mają Git blob SHA zgodny z tym pakietem GitHub; nie potwierdzano zgodności 53/53 plików osobno.
- EXE: PE32 i386 GUI, **5 sekcji**, `aspack` / `.adata`; bardzo wysoka entropia dwóch dużych sekcji (**7,970 / 7,897 bitów/bajt**). Eksportuje funkcje `_EXECryptor_*`. Jawna tablica importów podaje wyłącznie `KERNEL32!CreateFileA`, `KERNEL32!ExitProcess`, `COMCTL32!InitCommonControls`. **Nie można z tego wywnioskować, że aplikacja używa tylko tych funkcji ani jakiego API używa do komunikacji z PIC**, ponieważ kod jest spakowany/chroniony.
- EXE: pole wersji w zasobach `FileVersion=1, 0, 0, 1`, `ProductVersion=1, 0, 0, 1`; PE export name `VWTester.exe`, podczas gdy plik jest nazwany `VAG-K+CAN Commander.exe`. Nie świadczy to samo w sobie o wersji firmware adaptera.
- PE TimeDateStamp: **2007-11-12 12:55:33** (wartość pola PE, nie potwierdzona data zbudowania programu); czas pozycji ZIP **2023-01-09** (data przepakowania, nie wersja protokołu).
- Odczytane teksty konfiguracji mówią o `[COM] CAN_PORT=3; KWP_PORT=3`, `[KWP1281]` timing i ustawieniu **FTDI latency timer 1 ms**; instrukcja wspomina również **osobny dongle USB**.
- Nie znaleziono w jawnym kodzie EXE czytelnej, powtarzalnej implementacji protokołu CAN; **nie wolno stwierdzać braku komend** — są prawdopodobnie schowane w chronionym programie. Żaden plik EXE/DLL nie był uruchamiany.

Szczegółowa karta analizy: [ANALYSIS_ORIGINAL_EXE_2026-10-23.md](ANALYSIS_ORIGINAL_EXE_2026-10-23.md).


---

## Pakiet `commander vag-k can.zip` (2026-10-23)

- ZIP: **7 159 335 B**, SHA-256 `5ee88477ab1e7b691b20119a44ce1298c122dcaba7713f17ca98ad90a644c7cf`; **53 pozycji (46 plików, 7 katalogów)**, 10 122 682 B plików po rozpakowaniu.
- Instalator `Setup VAG K+CAN COMMANDER 1.4.exe`: **2 189 988 B**, SHA-256 `07c476c9cb21d250a7f34049c455f08b6d46c22f01145fda38ef41555371aefa`; Windows PE32 x86 z jawnymi metadanymi `Setup Factory 8.0 Run-time`, sygnatura `irsetup.exe` / `irsetup.dat`.
- W ZIP są osobne instrukcje PDF (2010), pakiet sterowników FTDI (z lat 2003–2009), instalator, ale **nie ma samodzielnego `VAG-K+CAN Commander.exe`** jako pozycji ZIP.
- Nie uruchamiano instalatora. Nie rozpakowano wewnętrznego formatu Setup Factory — **brak możliwości porównania programu instalowanego przez EXE** z wcześniejszym `VAG-K+CAN Commander.exe`.
- Odczytane `ftdiport.inf`: `DriverVer=03/13/2008,2.04.06`, `VID_0403&PID_6001` i `VID_0403&PID_6010`. Nie przesądza to rzeczywistego VID/PID adaptera użytkownika.
- Instrukcja `instrukcja obslugi interfejsu vag k+can.pdf` (21 stron, `auto-interfejsy.pl`) zaleca **Latency Timer 1 ms**, bufor USB RX **512 B** / TX **512 B**, wybór **COM1–COM4**. Wymienia instalację sterownika **2.6.0.0 z 22.10.2009**, niezgodną z wersją INF w tym ZIP (2.04.06). Instrukcja wskazuje archiwum `VAG K+CAN COMMANDER FULL 1.4.rar` na **osobnej płycie CD**, które nie jest składnikiem przesłanego ZIP.
- Dokument `korekcja licznika VAG CAN K.pdf` (Viaken, 18 stron) podaje dla opisywanego wariantu zasilanie 12,5–15 V z gniazda diagnostycznego. **Nie jest to pomiar ani specyfikacja zasilania konkretnej niebieskiej płytki**.
- Nie znaleziono nowych, potwierdzonych bajtów protokołu PC ↔ PIC; dokumenty dotyczą instalacji i używania funkcji diagnostycznych, nie niskopoziomowego protokołu USB–UART.

Szczegóły: [ANALYSIS_SETUP_FACTORY_2026-10-23.md](ANALYSIS_SETUP_FACTORY_2026-10-23.md).
