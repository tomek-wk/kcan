# Porównanie trzech pakietów VAG K+CAN Commander „3.6” (2026-10-23)

**Zakres:** dwa nowe archiwa użytkownika porównano bajt po bajcie po rozpakowaniu ze znanym `VAG COMMANDER 3.6(2).rar` opisanym wcześniej w [ANALYSIS_VWTESTER_36_2026-10-23.md](ANALYSIS_VWTESTER_36_2026-10-23.md). Analiza **wyłącznie statyczna**: odczyt RAR/ZIP, kontrola poprawności dekompresji, inwentarz, SHA-256 i porównanie poszczególnych plików, treść INI. **Nie uruchomiono żadnego EXE/DLL/SYS**, nie wykonano instalacji ani testów sprzętu/pojazdu. Repozytorium nie przechowuje źródłowych archiwów, binariów, logów ani danych osobowych.

## 1. Identyfikacja i wynik weryfikacji

| Pakiet | Typ | Rozmiar (B) | SHA-256 archiwum | Zawartość |
| --- | --- | ---: | --- | --- |
| `VAG COMMANDER 3.6(2).rar` (**odniesienie**) | RAR4 | **1 730 114** | `4c4e448077836806c593ef2f08a948ee56d0bde73f6f7dd8f56148b0097403a4` | 26 plików, 2 katalogi, korzeń `VAGCAN+K V3.6/` |
| `VAG K CAN COMMANDER FULL 3,6.rar` | RAR4 | **1 730 535** | `e0059df5cb1e51434ae1eea95d4f7ff7234a176360fb739d2b382dbace83069b` | 26 plików, 2 katalogi, korzeń `VAG K CAN COMMANDER FULL 3,6/` |
| `VAG-K CAN-V3.6.zip` | ZIP | **1 971 451** | `9b59b9490c0011edea1976d9d4ad16a4671e1870b45576088f298ed23b5d8b32` | 26 plików, 2 katalogi, korzeń `VAG K+CAN V3.6/` |

**Metodologia:** w każdym pakiecie usunięto *wyłącznie* pierwszy komponent ścieżki (różne nazwy katalogów głównych). Wszystkie 26 ścieżek względnych są jednakowe. Dla każdej porównano pełne rozpakowane bajty (nie nazwę, rozmiar, czas ani CRC). RAR dekompresowano przez libarchive, ZIP przez Python zipfile. Każda para pakietów ma **25/26 plików bajtowo identycznych**; dokładnie **jeden plik się różni: `Tester.ini`**.

### Kluczowe pliki identyczne we wszystkich trzech pakietach

| Relatywna nazwa | Rozmiar (B) | SHA-256 (w każdym pakiecie) |
| --- | ---: | --- |
| `VWTester.exe` | **647 168** | **`a448ff313cce8ee2597f14675e51196ca5b677a5561833bb65965b05628d8a23`** |
| `FTChipID.dll` | **61 440** | `d63d9ec2f0557184aba3d4156d755767cd234fc4b108f4209abbf28c064936c6` |
| `FTD2XX.dll` oraz `CDM_Setup/FTD2XX.dll` | **176 128 każda** | `391644ee8db7dd5fe5ceaf612ea963280a54e4f4e03af8faf2008c35039a3c06` |
| `RCMicroDogSetup.dll` | **2 146 304** | `5671711caf7446ce3496028375156cf4443c12311ac4e75c626dd740652d8ef4` |
| `CDM_Setup/FTDIBUS.INF` | **2 366** | `b6dc834181d49ddffb017d672f7efb4d9805045f6bd3d1b30aafa979c8113fb7` |
| `CDM_Setup/FTDIPORT.INF` | **3 507** | `a60a807ee7295c3f216ed25bfbe74b2900981736aa67b84cf9377fabca2be4ee` |

Identyczne są **również pozostałe** sterowniki, EXE instalatora sterownika, biblioteki, `FixDiag.ini`, `MWB.TXT`, `MWB_de.TXT` i `VAG.txt`. Zawartość `CDM_Setup` jest w 100% jednakowa. Osobnych wariantów kodu CAN, FTDI API ani innej kompilacji **nie wykryto**.

## 2. Jedyna różnica: `Tester.ini`

| Parametr | Poprzedni `VAG COMMANDER 3.6(2).rar` | Nowy `FULL 3,6.rar` | Nowy `V3.6.zip` |
| --- | --- | --- | --- |
| pierwsze `[CHANNEL] TARGET` | **6** | **6** | **0** |
| drugie `[CHANNEL] TARGET` | 0 | 0 | 0 |
| `[TRACE] FILEINDEX` | **1872** | **1877** | **1879** |
| `[COM] CAN_PORT` | 2 | 2 | 2 |
| `[COM] KWP_PORT` | 2 | 2 | 2 |
| `[DIAG] DIAGNOSTICID` | -674897751 | -674897751 | -674897751 |
| `[PROTOKOL] Protokol` | KWP2000 | KWP2000 | KWP2000 |
| SHA-256 całego `Tester.ini` | `949e7fadb8da0a3dc10a480dd157923dfb8e496c39c526468f91fb486d3bfd62` | `03549d88a2df4d324fed66275ec463e1152dee8046c64f1d43a91cce4f83e949` | `fbdc181b9aff69b849faea489ea7d0766daf53fdd42840e576ad3f0830fd1caa` |

Wariant RAR FULL różni się od odniesienia **jedną wartością**: `FILEINDEX=1872→1877`. Wariant ZIP różni się **dwiema wartościami**: pierwsze `TARGET=6→0`, `FILEINDEX=1872→1879`. Innych różnic w INI nie znaleziono. Nie jest to różnica kodu EXE ani biblioteki.

**Interpretacja:** trzy różne ustawienia `FILEINDEX` przy tym samym programie i bibliotekach wzmacniają hipotezę, że `FILEINDEX` jest lokalnym indeksem plików/śladów, potencjalnie modyfikowanym przy użyciu lub pakowaniu programu. **Nie dowodzą**, że program go inkrementuje ani że `TARGET` wpływa na protokół UART. Ponieważ `[CHANNEL]` występuje **dwukrotnie**, bez zbadania parsera INI nie wiadomo, czy skuteczny jest pierwszy czy drugi `TARGET`. Weryfikacja należy do istniejącego **KCAN-D011**.

## 3. Znaczenie dla potwierdzania protokołu CAN / KCAN-D043

- **To nie są dwie kolejne nowe kompilacje.** Każdy pakiet zawiera dokładnie ten sam chroniony `VWTester.exe` o SHA-256 `a448ff31...`; powtórna deasemblacja tych samych bajtów nie dostarczy nowej wersji algorytmu CAN.
- Jawne importy `FT_Open`, `FT_Close`, `FT_GetDeviceInfo` i `FTID_GetChipIDFromHandle` opisane w [raporcie 3.6](ANALYSIS_VWTESTER_36_2026-10-23.md) są **identyczne we wszystkich trzech pakietach**. Nadal **nie można stwierdzić**, czy D2XX służy do danych CAN, czy tylko do wykrycia/identyfikacji FTDI.
- **Nie zyskano nowego potwierdzenia** UART 833333, komend `0x50/51/52/53/55/60/70`, CAN11/CAN29, filtrowania, ACK/listen-only ani obsługi błędów przez konkretny adapter 3.6. Kod EXE nadal ma ochronę `.vmp0/.vmp1`.
- **Nie tworzymy KCAN-D044.** Uzupełniamy istniejące **D011** (warianty `Tester.ini`) i **D043** (zgodność protokołu 3.6), nie ogłaszając ich rozwiązania. Szczegółowe testy sprzętowe pozostają w [SAFE_TESTS.md](SAFE_TESTS.md).

## 4. Zalecany następny krok

Z perspektywy rozpoznania możliwości CAN bardziej wartościowy niż kolejne archiwum tego samego EXE jest (a) plik aplikacji z **innym SHA-256** i czytelną ścieżką wykonawczą, (b) **własny surowy zrzut UART PC↔PIC** z kontrolowanej sesji, lub (c) test z odizolowanym CAN, podczas którego zapisze się bajty protokołu i fizyczne ramki drugim interfejsem. Żaden nowy materiał nie uzasadnia wysyłania nieznanych rozkazów na magistralę pojazdu.
