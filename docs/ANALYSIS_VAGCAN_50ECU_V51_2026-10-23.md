# VAG-CAN Commander „V5.1” — kod hosta, CAN29, inicjalizacja i memory.bin (2026-10-23)

**Materiał:** przesłany `VAG-CAN Commander V5.1.zip`. SHA-256 archiwum **`151913526f55e2528ccf153a0d47b69d67d53dde96ed8057af9efe083aeea94f`**, **1 113 420 B**, ZIP bez hasła, 32 wpisy (**28 plików + 4 katalogi**). Analiza **statyczna**: odczyt ZIP, hashe i porównania, tablica sekcji i importów PE, czytelne fragmenty disassembly `objdump -D -Mintel`, napisy ASCII/UTF-16, źródłowe INF/INI. **Nie wykonywano EXE/SYS/DLL, nie instalowano drivera ani nie podłączano pojazdu/adaptera.** Publikujemy tylko własny Markdown, hashe, krótkie fragmenty HEX i adresy. Nie umieszczamy oryginałów ani `memory.bin` w repo.

## 1. Manifest i rzeczywista nazwa kompilacji

| Pozycja | B | SHA-256 | Rola |
| --- | ---: | --- | --- |
| `VAG-CAN Commander+EDC15.exe` | **466 968** | **`811bf59355614e0d07aa2e4c10fedd01fbff2b0148feab4491f0f731c98d45ba`** | **Nowa binarka** w stosunku do 3.0 beta (417792), 4.5 (477472), FULL 2.5 (688128) i „3.6” (647168) |
| `memory.bin` | **2 048** | `739e3bf5eca392955fa70e7aeea725dad3c39e6d3d69d13b1d65c183596d6ea4` | Dane niezerowe o niewyjaśnionym znaczeniu; **nie potwierdzono, że to firmware PIC** |
| `Tester.ini` | 325 | `9c31753018df20bf73bad9a85df2ffc897261c6ec691fc792f610390746ebec4` | Ustawienia GUI i COM |
| `drivers/i386/ftd2xx.dll` | 202048 | `b052d6dcf61b864e948743cd02c29f0bf80f94e6c705bc4dbe858b55eeabbbb2` | Biblioteka FTDI dostarczona **ze sterownikami**, nie jawnie importowana przez aplikację |
| `drivers/amd64/ftd2xx64.dll` | 320840 | `40b71c4eab9b8b6801bab4575a64fea73961471aa8bdfc11083a3890f9bc7c30` | Biblioteka FTDI x64 |
| `FixDiag.ini`, `MWB.TXT`, `MWB_de.TXT`, `VAG.txt` | 1158, 37988, 21277, 151443 | patrz sekcja 5 | Wspólne dane diagnostyczne znane z 1.4 |

**Rozbieżność nazewnictwa:** ZIP nazywa się **V5.1**, program `+EDC15` ma w zasobach UTF-16 napis **`VAG-CAN COMMANDER 5.0+ECU (full)`** i **`VAG-EDC15x`**. To niezależny ślad identyfikacji interfejsu użytkownika; **nie jest potwierdzeniem wersji firmware 5.1 ani 5.0**.

PE to **Win32 x86**, 5 sekcji `.text`, `.rdatU`, `.data…`, `.!rc!`, `.rsrc`; **czytelne funkcje CAN** w `.text`. Data w nagłówku PE to **2007-03-07 12:40:39 UTC**, nie traktować jej jako niezależnie poświadczonej daty dystrybucji. **Brak bezpośrednich importów `FTD2XX.dll` i `FTChipID.dll` w głównym EXE** (mimo obecności D2XX w katalogu sterowników). EXE importuje Win32 `CreateFileA`, `ReadFile`, `WriteFile`, `GetCommState`, `SetCommState`, `EscapeCommFunction`, `GetPrivateProfileIntA`. Możliwości ładowania dynamicznego bibliotek nie wykluczono, nie obserwowano ich wykonania.

## 2. Inicjalizacja PC↔adapter: C0 i ustawienia COM

`Tester.ini`:
```ini
[CHANNEL]
TARGET=6
APLTYPE=0x01
[CHANNEL]
TARGET=0
[DIAG]
DIAGNOSTICMODE=134
[TRACE]
FILEINDEX=1656
[COM]
CAN_PORT=5
KWP_PORT=5
[PROTOKOL]
Protokol=KWP2000
UseSrcAddress=1
```
`//Protokol=CAN` jest **wyłącznie skomentowaną linią**, nie dowodem aktywnego trybu CAN. Pola `CAN_PORT` i `KWP_PORT` mają **osobne odwołania w kodzie** `0x409D3B` i `0x409D59` do `GetPrivateProfileIntA`; wartości w tym pakiecie jednakowo **5/5**. Ścieżka INI jest budowana od `GetCurrentDirectoryA` + `\\TESTER.INI`; dotyczy katalogu roboczego, nie musi dotyczyć położenia EXE.

W czytelnej ścieżce uruchamiania `0x40AE9C..0x40AF6D`, po otwarciu portu `0x403110` są wysyłane:
1. `0x40AEB4` → `0x403370`: szablon **`51 00`** (`0x456952`), `Sleep(50)`.
2. `0x40AEC5` → `0x4033F0`: **`C0 00`** (`0x456930`), `Sleep(50)`.
3. `0x40AF6D` → `0x403470`: **`53 20 [32B]`**. Słowa parametrów RX table znajdują się w `0x456A20`; znaczenie komend po stronie PIC **niepotwierdzone**.

Początkowy blok złożony w `0x40AEE1..0x40AF69`:
```text
53 20
FF 1C 00 00
FF 1C 00 00
FF 1C 00 00
FF 1C 00 00
FF 1C 00 00
FF 1C 00 00
FF 1C 00 FF
FF 1C 00 00
```
Część GUI ma też drugi podobny blok konfiguracji zależny od stanu dialogu; **nie zakładać, że każda sesja nadaje obydwa bloki**. Interpretacja **6×4 + 2×4** jako filtrów i masek kontrolera PIC pozostaje hipotezą mapowania na fizyczne RXF/RXM, a wyjątkowy `FF` w 7. wpisie ma nieznane znaczenie.

Otwieranie portu (`0x4031BA`): w czytelnej ścieżce przekazuje **833333 bit/s UART** (`0xCB735`) do funkcji `0x408CF0`, nie jest to 500 kbit/s CAN i **nie zaobserwowano w tej ścieżce alternatywnego 115200 zależnego od numeru COM** jak w 4.5. Port `0x408D10` jest tworzony jako **`COM%d`**, bez prefiksu COM10+ w tej ścieżce. `EscapeCommFunction` w `0x408D72..0x408DA9`: **SETDTR (5) → Sleep(500) → CLRDTR (6) → SETRTS(3) lub CLRRTS(4)** zależnie od przekazanego parametru; w rozpoznanej ścieżce z `0x4031AF` jest przekazany parametr **1**, więc żąda SETRTS. Efekt elektryczny na płytce nieznany.

## 3. CAN11 potwierdzony wykonawczym kodem, CAN29 nie w tej ścieżce

| Element | Kod 5.0+ECU | Dokładny wniosek |
| --- | --- | --- |
| TX `0x60` | `0x403520..0x403577` | Pobiera **WORD ID** (`mov dx,WORD PTR [ebx]`), buduje `60 (N+4) (ID>>3)&FF ((ID&7)<<2) 00 00 [N B]` i kopiuje N bajtów |
| RX `0x70` | `0x402CE0..0x402D51` | Odzyskuje `(B2<<3)|((B3>>2)&7)` do WORD; **nie rekonstruuje 29-bitowego ID ani flagi IDE** |
| RX walidator | `0x402C40..0x402CB9` | Dla `0x70` `length=4..12`; dla `0x60` **specjalna gałąź akceptuje 0..4 B** |
| RX descriptor | **`0x456A20`**, 8 × 34 B | Nagłówki `C0 00, 51 00, 52 20, 53 00, 54 02, 60 00, 6F 00, 70 00`; `60 00` w tabeli **nie ogranicza** specjalnego walidatora do zera |
| TXT RX/TX records | TX `0x4036BB..0x4036D1`, RX `0x402D27` | Mapa rekordów grupuje przez `(channel<<11)|(ID&0x7FF)` i bufor 2048 slotów, nadal **11 bitów** |

**Dowód nieobsługi CAN29 przez te wykonawcze funkcje:** `ID=0x18DAF110` (extended) i `ID=0x110` (standard) przekształcą się w identyczny 4-bajtowy nagłówek **`22 00 00 00`**. Pomimo czterobajtowego nagłówka protokół ten nie niesie 29-bitowego ID. **Nie twierdzimy, że PIC, firmware lub inne nieodkryte opkody nie mogą CAN29** — to wymaga oddzielnego testu.

**Różnice w stosunku do poprzedników:** rozpoznana inicjalizacja **`51 → C0 → 53`** jak w starszych 3.0 beta/4.5, ale **oddzielne CAN_PORT/KWP_PORT** (jak w późniejszych dystrybucjach) oraz sztywne **833333** w sprawdzonej ścieżce. Na tym etapie **nie stwierdzono nowego, potwierdzonego opkodu ani nadajnika EID29**.

## 4. Nadal obecne błędy hosta w zapisie UART/CAN TX

Funkcja UART `0x408BF0..0x408C53` używa `WriteFile` z OVERLAPPED, a przy wyniku FALSE wywołuje **`WaitForSingleObject(INFINITE)`** i **`GetOverlappedResult(...,TRUE)`**, **nie sprawdza wyniku ani `bytesWritten`**, po czym zwraca **1** dla ważnego uchwytu portu. To ten sam typ **potencjalnej blokady i pozornego sukcesu**, który opisano dla starszych kompilacji (KCAN-D048).

CAN TX `0x4035CE` wywołuje writer, a `0x4035D3` przechodzi dalej bez weryfikacji `EAX`; lokalna struktura wiadomości dostaje status 1, timestamp z `GetTickCount`, wpis do historii TX, `Sleep(10)` i **return 1** (KCAN-D049). To **nie jest dowód rzeczywistej transmisji CAN ani fizycznego ACK**. W `0x40352B..0x403575` nie ma lokalnej walidacji `N<=8` przed kopiowaniem N bajtów do pakietu na stosie (KCAN-D050); walidacja w GUI/wywołujących może istnieć — nie przebadano wszystkich callerów.

## 5. Dane diagnostyczne i `memory.bin`: nowe pytanie

- `FixDiag.ini`: Git blob SHA-1 po CRLF→LF **`402da46683ecfa09e3742fae8791e3dea2e4963e`**
- `MWB.TXT`: **`94aff48b1782e1b42cd9679b48e1303b45a70cf0`**
- `MWB_de.TXT`: **`b665cca873deedf86b1e4887dc1fd9103c150a7e`**
- `VAG.txt`: **`64a4503a6d5708ecf42e2702946d871bf0ed90ce`**

Wszystkie cztery są **identyczne po ujednoliceniu końców linii** z poprzednio opisanym pakietem 1.4 i katalogiem publicznym [Skylakc/BoschME7.5-Tools](https://github.com/Skylakc/BoschME7.5-Tools/tree/main/tools/VAG-K_CAN_Commander_1%5BX%5D.4); nie jest to nowa baza ramek CAN.

`memory.bin` (2048 B) nie ma nagłówka PE i nie jest pusty. **Sama nazwa/rozmiar/układ bajtów nie ustala, czy to EEPROM ECU, próbka danych, backup czy inny artefakt.** Co więcej, kod głównego EXE przy `0x4135E0` zawiera **jawne odwołanie do napisu `memory.bin` w ścieżce obsługi plików**, więc plik jest powiązany z workflow programu. Nie zidentyfikowano go jako pliku flash/PIC-firmware ani nie badano w pełni semantyki jego zapisu/odczytu. **Nie publikować całego pliku lub potencjalnie wrażliwych wartości danych ECU**, dopóki jego charakter nie jest jasny.

## 6. Sterownik, możliwe skutki i otwarte zagadnienia

Oba `drivers/ftdibus.inf` i `drivers/ftdiport.inf` deklarują **`DriverVer=03/13/2008,2.04.06`**, także platformy **i386 oraz amd64**. `ftdiport.inf` zawiera `LatencyTimer=16` (wartość **domyślna z INF**, nie pomiar na komputerze użytkownika). Lista VID/PID obejmuje standardowe FTDI `0403:6001` i `0403:6010`; **nie świadczy o tożsamości konkretnego adaptera**. Nie instalować nieznanych sterowników tylko dla badania.

**Otwarte zadania:**
- **KCAN-D051:** czy oznaczenie „V5.1” w archiwum odpowiada innej wersji programu/firmware, skoro zasób GUI głosi „5.0+ECU”; osobno potwierdzić zgodność transportu CAN11 i wykazać brak dostępnego EID29 w tych konkretnych funkcjach (sprzęt nadal nieznany). Rozszerza D015/D047, nie modyfikuje protokołu.
- **KCAN-D052:** znaczenie `memory.bin` w kodzie i źródło 2048 B danych; prześledzić wywołujących i użycie pliku bez ujawniania zawartości.
- **D048–D050:** dowiedziono zachowania tego samego typu w kolejnej kompilacji; naprawy wymagane **we własnym programie**, nie przez bezrefleksyjne kopiowanie klienta Win32.

**Wniosek:** pakiet oznaczony V5.1 jest **nową kompilacją hosta z funkcjami EDC15 i nowym artefaktem pamięci**, ale **nie dostarcza udokumentowanego nowego formatu CAN29**. Wspólne opkody `51/C0/53/60/70` i wady write/TX są odtwarzalne po stronie EXE. Żadnego pomiaru firmware, CAN ACK, listen-only lub CAN29 nie wykonano. Testy sprzętowe wyłącznie na stanowisku izolowanym, nie na samochodzie.
