# Archiwum `VAG K CAN COMMANDER FULL 1.4.zip` — porównanie binarne

Data analizy: 2026-10-23. Dostarczone przez użytkownika. **Analiza wyłącznie statyczna.** Nie uruchamiano EXE/DLL, nie podłączano pojazdu ani interfejsu. Oryginalnych plików nie przechowuje się w repozytorium.

## 1. Archiwum

| Pole | Wynik |
| --- | --- |
| Nazwa | `VAG K CAN COMMANDER FULL 1.4.zip` |
| Rozmiar | **1 667 457 B** |
| SHA-256 | `05f138209fb36a97fbb299213ec4e97376c6980887f867836dc9e7b1cca048d1` |
| Liczba pozycji ZIP | 14, w tym 2 katalogi i **12 plików** |
| Suma rozmiarów po dekompresji | **3 425 594 B** |
| Lokalizacja | folder `VAG K CAN COMMANDER FULL 1.4/VAG K+CAN COMMANDER FULL 1.4/` |

## 2. Wynik porównania z dystrybucją `VAG-K_CAN_Commander_1[X].4.zip`

**Program i biblioteka zabezpieczenia są identyczne bitowo.** Poniższe SHA-256 są zgodne z wynikami analizy poprzedniego pakietu:

| Plik | Rozmiar | SHA-256 | Wynik |
| --- | ---: | --- | --- |
| `VAG-K+CAN Commander.exe` | 1 060 864 B | `ea69c09b51fda25107d9926d7d033f4e25f5374ec0dd2b1bc4a9867a7b19b932` | **identyczny** |
| `RCMicroDogSetup.dll` | 2 146 304 B | `5671711caf7446ce3496028375156cf4443c12311ac4e75c626dd740652d8ef4` | **identyczny** |

EXE pozostaje chroniony/kompresowany (ASPack/EXECryptor). **W nowym archiwum nie znaleziono innej kompilacji ani nowych, potwierdzonych poleceń protokołu PC↔PIC.** Metadane EXE opisano w [analizie poprzedniej dystrybucji](ANALYSIS_ORIGINAL_EXE_2026-10-23.md).

### Pliki tekstowe

Dziewięć z dziesięciu plików TXT/INI ma identyczną zawartość **po normalizacji znaków końca linii CRLF → LF**. Potwierdzono to przez obliczenie Git blob SHA-1 z zawartości po normalizacji i porównanie z rzeczywistymi identyfikatorami tych plików w [Skylakc/BoschME7.5-Tools](https://github.com/Skylakc/BoschME7.5-Tools/tree/main/tools/VAG-K_CAN_Commander_1%5BX%5D.4). Zgodne są: `bugfixes open issues.txt`, `FixDiag.ini`, `FLASH MEMORY.txt`, `installation 1.2-6+.txt`, `k-line usage.txt`, `MWB.TXT`, `MWB_de.TXT`, `usage of value fields for adaptations.txt`, `VAG.txt`.

**Jedynym plikiem o zmienionej treści jest `Tester.ini`.** Ma on tę samą liczbę bajtów po normalizacji (359), ale różne wartości dwóch pól:

| Lokalizacja | Poprzedni pakiet | Nowy pakiet |
| --- | --- | --- |
| Pierwsza sekcja `[CHANNEL]`: `TARGET` | `0` | **`6`** |
| Sekcja `[TRACE]`: `FILEINDEX` | `3221` | **`1956`** |

**W obu plikach istnieje również druga sekcja `[CHANNEL]` zawierająca `TARGET=0`.** Nie ustalono, czy parser aplikacji stosuje pierwszy wpis, ostatni wpis lub inne reguły, ani czy `TARGET` wpływa na komunikację PC↔PIC. Pole `FILEINDEX` najpewniej dotyczy śledzenia/logowania, ale jego faktyczna semantyka nie została wykazana.

### Wniosek o wersji

Nazwa `FULL 1.4` opisuje tę samą kompilację programu, którą mieliśmy już wcześniej (co najmniej w dwóch dystrybucjach: archiwum 1[X].4 i publiczny plik GitHub). **Nie dowodzi ona istnienia innego protokołu lub firmware.** W tej paczce nie ma sterowników FTDI ani instalatora — to katalog samych plików aplikacji.

## 3. Nowy test do rejestru

**KCAN-D011 — wpływ pierwszego `[CHANNEL] TARGET=6` i `[TRACE] FILEINDEX=1956` oraz zduplikowanego `[CHANNEL]`.**

1. Najpierw zbadać sposób odczytu INI w kolejnej, łatwiejszej do analizy wersji programu albo obserwować zachowanie tylko na odizolowanym stanowisku.
2. Zanotować, jaka wartość celu jest widoczna w interfejsie użytkownika po otwarciu `Tester.ini` w obu wersjach.
3. Porównać inicjalne ramki UART przy identycznym podłączeniu i różnych plikach INI, *bez połączenia z pojazdem*, jeżeli program jest bezpieczny i działa na danym adapterze.
4. Osobno porównać utworzone identyfikatory/indeksy logów. **Nie interpretować zmiany FILEINDEX jako nowego opkodu.**
5. Udokumentować dokładną wersję adaptera i stan dongla, o ile wymagany.

Stan: **OPEN**. To rozbieżność konfiguracji aplikacji, **nie zaobserwowana różnica protokołu**.

## 4. Powiązania

- Wcześniejszy program i metadane: [ANALYSIS_ORIGINAL_EXE_2026-10-23.md](ANALYSIS_ORIGINAL_EXE_2026-10-23.md).
- Wcześniejszy pakiet instalatora Setup Factory (nadal nierozpakowany): [ANALYSIS_SETUP_FACTORY_2026-10-23.md](ANALYSIS_SETUP_FACTORY_2026-10-23.md).
- Centralna lista rozbieżności: [DISCREPANCIES.md](DISCREPANCIES.md).
- Informacje o źródłach: [SOURCES.md](SOURCES.md).

**Brak nowo potwierdzonych bajtów komend `0x52/0x53/0x55/0x60/0x70` i brak nowych testów na sprzęcie.**
