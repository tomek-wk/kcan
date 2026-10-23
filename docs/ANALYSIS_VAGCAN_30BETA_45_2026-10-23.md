# VAG-CAN Commander 3.0 beta i 4.5 — analiza statyczna CAN (2026-10-23)

**Źródło:** plik użytkownika `VAG-CAN Commander V4.5.zip`, **1 663 886 B**, SHA-256 **`e7980df7b33847af86ad12c52ae99c377b39c1d8f067abbe12e2d8c5de5e2b1c`**, ZIP bez hasła, **32 pliki i 3 katalogi** (łącznie 2 919 948 B danych rozpakowanych). Analizowano wyłącznie **statycznie**: manifest/CRC, SHA-256, importy i sekcje PE, teksty zasobów, deasemblację kodu x86, konfigurację INI i INF. **Nie uruchomiono EXE/DLL, nie instalowano sterowników, nie korzystano z interfejsu ani pojazdu.** Zawartość oryginalna nie jest publikowana.

## 1. Dwie niezależne binarki w jednym pakiecie

| Plik | Rozmiar | SHA-256 | Identyfikacja |
| --- | ---: | --- | --- |
| `VAG-CAN Commander 3.0 beta.exe` | **417 792 B** | `dfb5e3f4724f6898c7c82d5d6e69ed3f795edb5f536f4aa5ff37ab17eae2a39b` | PE32 Win32 GUI x86, **4 sekcje** `.text/.rdata/.data/.rsrc`; czytelna ścieżka CAN; w zasobach „VAG-CAN COMMANDER 3.0 beta - full” |
| `VAG-CAN Commander4.5.exe` | **477 472 B** | `85e89882a434ad83d19381ecbb5f9e77b14b237343b1432feb2f7300810e0050` | PE32 Win32 GUI x86, **5 sekcji**, m.in. `.mackt` i duża niestandardowa sekcja; czytelna część kodu CAN; w zasobach „VAG-CAN COMMANDER 4.5 beta - full” |

**Żadna z dwóch kompilacji nie jest bajtowo identyczna** z dotychczas opisanymi `VAG-K+CAN Commander.exe` 1.4 (`ea69c09b...`), `VWTester.exe` FULL 2.5 (`b90fc612...`) ani chronionym `VWTester.exe` „3.6” (`a448ff31...`). Rozmiar/odmienny SHA sam w sobie nie dowodzi zmiany protokołu, dlatego poniżej przedstawiono **rzeczywiste ślady wykonawcze**.

**Ważny niuans:** sekcja `.mackt` i niestandardowe sekcje 4.5 sugerują ochronę/modyfikację pliku PE, ale **nie czynią całej implementacji nieczytelną**. Funkcje CAN w dostępnej części kodu są bezpośrednio rozpoznawalne. Z drugiej strony nie przeprowadzono pełnej rekonstrukcji wszystkich funkcji w obu programach; nie wolno wyciągać wniosków o nieobecności funkcji w całym EXE z braku jednej ścieżki.

W obu EXE nagłówek PE zawiera TimeDateStamp **2006-12-22 11:02:15 UTC**. Data jest *wartością metadanych*, **nie niezależnym dowodem wydania** programu. Archiwum zawiera też `installation.txt` odwołujące się do folderu **„VAG-CAN Commander 2.0 beta”**, chociaż rzeczywiste EXE mają oznaczenia 3.0 beta/4.5. To niespójność historycznego opisu, **nie dowód trzeciej kompilacji**.

## 2. Wspólny format protokołu CAN11 — potwierdzenie niezależnym kodem

**W obu kompilacjach wykryto bezpośrednią konstrukcję pakietu TX `0x60`:**

| EXE | VA procedury TX | Dowód x86 |
| --- | --- | --- |
| 3.0 beta | `0x403510` (szczególnie `0x40351B–0x403567`) | odczyt długości z rekordu; `add al,4`; przesunięcie ID o 3, `(ID & 7)<<2`; zapis `0x60`; kopiowanie **dokładnie N bajtów** |
| 4.5 | `0x4034F0` (szczególnie `0x4034FB–0x403545`) | analogiczny kod, ze strukturą i zmianami adresów specyficznymi dla tej kompilacji |

Odtworzony format dla udokumentowanej ścieżki **CAN11**:

```text
PC -> PIC: 60 (N+4) SIDH SIDL 00 00 [N bajtów danych]
SIDH = (CAN_ID >> 3) & 0xFF
SIDL = ((CAN_ID & 7) << 2)
N = liczba bajtów danych (Classical CAN: 0..8)
```

Przykład **obliczony offline, NIE pomiar z adaptera**, CAN ID `0x123` i N=3:
`60 07 24 0C 00 00 11 22 33`.

**RX `0x70`:** w 3.0 beta funkcja `0x402C80` akceptuje `length=4..12`, a dyspozytor `0x402D10` odbiera `0x70`. W 4.5 odpowiednio `0x402C40` i `0x402CE0`. Kod dekoduje ID przez `SIDH<<3 | ((SIDL>>2)&7)` i długość `N=length-4`. **Nie jest to dowód CAN29 ani trybu listen-only bez ACK**.

**Istotna różnica między implementacjami parsera odpowiedzi `0x60`:**
- **4.5:** `0x402C64–0x402C74` zawiera osobną ścieżkę dla `0x60`, akceptując `length<=4` — tak jak parser znany z FULL 2.5.
- **3.0 beta:** w badanej funkcji walidatora `0x402C80` nie odnaleziono osobnego wyjątku dla `0x60`, więc pozostałe kody są dopasowywane do tablicy **ośmiu** deskryptorów. **Nie stwierdzamy, że program 3.0 odrzuca wszystkie odpowiedzi `0x60`**: zakres dopuszczany przez deskryptory i zachowanie sprzętu nie zostały prześledzone end-to-end.

`60 00` nadal oznacza odpowiedź *protokołu adaptera*, a **nie potwierdzenie fizycznego ACK** na magistrali CAN.

## 3. Blok konfiguracji `0x53` i prawdopodobne filtry

Obie kompilacje mają osobną procedurę nadającą `53 20 [32 B]`:
- 3.0 beta: `0x403470–0x40350D`, `0x403485: mov BYTE PTR [...],0x53` i `0x40348A: ...0x20`, potem `rep movsd` dla **8 DWORD = 32 bajty**.
- 4.5: `0x403450–0x4034ED`, analogicznie zapis nagłówka i 8 DWORD.

Niezależnie, w ścieżce przygotowania ustawień występują **dwie pętle**:
- 3.0 beta: `0x40A3F9–0x40A465`: pierwsza buduje **6×4 B** (limit offsetu `0x18`), druga **2×4 B** (limit `0x08`), kodując CAN11 przez przesunięcia o 3 i 2;
- 4.5: `0x40A489–0x40A4F5`, analogiczna struktura **6+2**.

Jest to kolejne, niezależne od FULL 2.5, potwierdzenie **konstrukcji bloku w programach PC**. Skojarzenie z **6 filtrami + 2 maskami kontrolera PIC** jest mocne, ale **fizyczne mapowanie RXF0..5 / RXM0..1, EXIDE i efektywna filtracja nie są udowodnione**.

## 4. Różnica w UART — 115200 i 833333 bit/s

**3.0 beta:** w `0x4031A0–0x4031C9` widoczna jest jawna stała `0x0CB735 = 833333` przekazywana jako argument procedury inicjalizacji portu. W tej konkretnej ścieżce nie ma wyboru `115200`.

**4.5:** w `0x403170–0x4031A5` widać rozgałęzienie:

```asm
0x40317E: cmp esi, 2
0x40318F: jae 0x403198
0x403191: push 0x1C200   ; 115200 (parametr < 2)
...
0x403198: push 0xCB735   ; 833333 (parametr >= 2)
0x40319D: push esi
0x4031A0: call 0x408CD0  ; procedura otwierania/konfiguracji portu
```

W **4.5 występuje zatem rzeczywisty warunkowy dobór prędkości zależny od parametru funkcji**: `0/1 -> 115200`, `>=2 -> 833333`. **Nie jest jeszcze udowodnione**, że ten parametr oznacza indeks elementu GUI lub etykietę K-Line/CAN; trzeba prześledzić wywołujących `0x403170`, a potem zweryfikować fizycznie ustawienia COM. To **wartości szeregowego łącza PC↔adapter / ścieżki programu, nie bitrate CAN**.

Jest to nowa istotna różnica implementacji w stosunku do badanej ścieżki 3.0 beta i starego opisu samego `833333` jako uniwersalnego ustawienia.

## 5. Zależności i pliki konfiguracyjne

- 3.0 beta ma jawne importy Windows `CreateFileA`, `ReadFile`, `WriteFile`, `GetCommState`, `SetCommState`, `SetCommTimeouts`, `EscapeCommFunction`, `GetTickCount` — **używa Win32 Virtual COM w badanej ścieżce hosta**. Są to niezależne dowody architektury portu COM.
- W pakiecie **nie ma** `FTD2XX.dll`, `FTChipID.dll` ani `RCMicroDogSetup.dll`. Nie należy z braku dostarczonych bibliotek wnioskować o wszystkich mechanizmach identyfikacji/autoryzacji aplikacji; zwłaszcza kod 4.5 ma niestandardową budowę.
- `USB driver/FTDIBUS.INF` i `FTDIPORT.INF`: **`DriverVer=04/16/2004,1.00.2154`**; przywołują identyfikatory `VID_0403` i kilka PID, w tym `6001` i `8372`. **To tylko zakres obsługiwany przez dołączony stary pakiet sterownika, nie identyfikator konkretnego interfejsu użytkownika**. Nie instalować niezweryfikowanych starych sterowników.
- `Tester.ini`: dwukrotne `[CHANNEL] TARGET=0`, `DIAGNOSTICMODE=137`, `FILEINDEX=716`, **`[COM] PORT=4`** — inny wariant od `CAN_PORT/KWP_PORT` w pakietach Commander 1.4/2.5/3.6. Dołączenie pola `PORT=4` nie dowodzi sposobu wyboru portu przez wszystkie wersje.
- `FixDiag.ini`, `MWB.TXT`, `MWB_de.TXT` i `VAG.txt` są **identyczne** z wcześniejszym źródłem Commander 1.4 po CRLF→LF; sprawdzono **4/4** przez pełne Git blob SHA-1 (a nie nazwę). To **wspólne dane diagnostyczne**, nie potwierdzenie wspólnego firmware.

## 6. Granice dowodu i plan

**Potwierdzone kodem hosta w obu EXE:** format CAN11 `0x60/0x70` z N zależnym od długości, budowa bloku `0x53` długości 32 B w postaci 6+2, obecność UART 833333; w 4.5 dodatkowy wybór 115200 i walidator `0x60 length<=4`.

**Niepotwierdzone:** reakcja konkretnego PIC/PCB, fizyczne ACK/listen-only, CAN29, DLC/RTR w sprzęcie, obsługa bus-off/error-frame, poprawność filtrów/masek w PIC, pełna inicjalizacja K-Line i semantyka `0x50/0x51/0x54/0x55/0x6F` w tych dwóch EXE. Wystąpienie kodu diagnostycznego `0x55` nie jest dowodem komendy `55 03` z J2534.

Nowe zagadnienia do rozstrzygnięcia:
- **KCAN-D044:** zgodność protokołu 3.0 beta/4.5 z 2.5: wariant `0x60` w parserze i rzeczywista zgodność po inicjalizacji, testy izolowane/offline.
- **KCAN-D045:** nazwy, przeznaczenie i faktyczne ustawienia UART w ścieżkach 4.5 wybierających 115200/833333, z porównaniem 3.0 beta.

Testy właściwych ramek CAN i wpływu na magistralę — **wyłącznie na odizolowanym, prawidłowo terminowanym stanowisku**, nigdy przez losowe komendy do samochodu. Nie podmieniać stanów `POTWIERDZONE (kod)` na `POTWIERDZONE (sprzęt)`.

**Powiązana dokumentacja:** [PROTOCOL.md](PROTOCOL.md), [COMMANDS.md](COMMANDS.md), [FILTERS.md](FILTERS.md), [DISCREPANCIES.md](DISCREPANCIES.md), [SAFE_TESTS.md](SAFE_TESTS.md).
