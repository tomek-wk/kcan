# Piąta analiza VWTester 2.5 — wyłącznie komunikacja CAN

Data: **2026-10-23**. Materiał: `k+can2.5(1).zip`, `VWTester.exe` **688128 B**, SHA-256 `b90fc612decb04759a77fd0f02946157d832053186c7adf5e50624a1b103a10d`.

Metoda: ponowne, ukierunkowane czytanie **deasemblacji x86**; weryfikacja bezpośrednio w lokalnym pliku PE. Nie uruchamiano EXE ani DLL; nie podłączano sprzętu/pojazdu. Adresy poniżej są **VA tego EXE**, nie adresami firmware PIC. Rozróżniono **dowód kodowy hosta**, **wyliczenie offline** i **zachowanie adaptera niepotwierdzone**.

## 1. Mapa rzeczywistych funkcji CAN w tej kompilacji

| Funkcja | Adres VA i dowód | Pewność |
| --- | --- | --- |
| Otwieranie COM dla CAN (833333 bit/s) | `0x403CE0/0x403CF8`, analogicznie `0x4099B0/0x4099C4` → `0x40A4F0` | kod |
| Inicjalny wybór dwóch trybów hosta | `0x41AA33–0x41AA5D`: indeks GUI `0` → `50 00`, inny → `51 00` | kod; nazwy trybów GUI nieustalone |
| Inicjalizacyjny zapis konfiguracji | `0x404270`: `53 20 [32B]`, po zapisie oczekiwanie do 100 ms na opcode `0x53` | kod |
| Pierwszy, stały i drugi adresowy blok `0x53` | `0x41AA66–0x41AB0B`; kodowanie `0x200+x`, `0x300` w `0x419510` | kod, efekt filtracji w PIC niepotwierdzony |
| **Oddzielne ustawianie filtrów z GUI** | `0x40E490–0x40E560`: 6×4 B + 2×4 B, wywołuje ogólny sender `0x404300` | **nowe rozróżnienie** |
| Kolejka TX i wątek CAN11 | `0x403D1C–0x403D2C` tworzy wątek `0x403DC0`; analog `0x4099EA` → `0x409A80` | kod |
| Nadawanie pakietu `0x60` | `0x403E54–0x403EC1` i `0x409B14–0x409B80`: `length=N+4`, CAN11 i N bajtów | kod |
| Parser strumienia UART | `0x404070–0x4041A7`, wariant `0x409D30` | kod |
| Wątek odbiorczy Win32 COM | `0x40A160–0x40A275`; bufor ReadFile **1024 B** | kod |
| Kontrola nagłówków | `0x4037D0` → `0x70 length=4..12`; `0x60 length=0..4`, pozostałe przez listę deskryptorów | kod |
| Odbiór CAN11 `0x70` | `0x403850–0x4038D0`, analog `0x409500` | kod |
| Obsługa `60 00` | `0x403A58–0x403A70`, analog `0x40970C`; zerowanie wewnętrznego statusu | kod, znaczenie fizycznego ACK niepotwierdzone |

## 2. Nowa różnica: inicjalizacja filtrów a „Set Filter” z GUI

### A. Zapis inicjalizacyjny `0x404270`

- Przygotowuje `53 20 [32 bajty]`.
- Wysyła **34 B** funkcją `0x40A3D0`.
- Po zapisie czeka maksymalnie **100 ms** na zdarzenie i **porównuje opcode odpowiedzi z `0x53`**.
- Zwraca sukces/porażkę do swojego wywołującego (ale nie każdy wywołujący sprawdza wynik).

### B. Ścieżka ustawiania filtrów `0x40E490`

- Przyjmowane wartości z okna konfiguracji zamienia na blok **6 × 4 B + 2 × 4 B** (`0x40E4E5–0x40E545`).
- Dla każdego wpisu standardowego ID tworzy `SIDH=ID>>3`, `SIDL=(ID&7)<<2`, dwa bajty zerowe. W gałęzi występuje warunek związany z `[object+0x5C]`, więc **nie każdy przypadek używa tej samej pętli**.
- Wysyła pakiet z funkcji **`0x404300`**, która tylko przekazuje bajty do `0x40A3D0` i **nie czeka bezpośrednio** na opcode `0x53`.

**Praktyczna rozbieżność:** wnioskowanie o skutecznym zastosowaniu filtrów tylko na podstawie zwrotu z okna GUI jest nieuprawnione. Konieczna jest kontrola odpowiedzi PIC i ewentualny odczyt zwrotny `0x52`. To **różnica implementacji hosta**, nie dowód nowej komendy.

## 3. Wątki i kolejki CAN — szczegóły

- `0x403CE0` tworzy worker TX (`0x403DC0`) przez `0x44EA50`; analogicznie `0x4099B0` tworzy `0x409A80`.
- Wątek pobiera rekordy po **20 B** (`rep movs dword ptr`, licznik 5), inkrementuje indeks i zawija go przez **`&0x7FF`**, czyli 2048 pozycji.
- Buduje CAN11 `[60,N+4,SIDH,SIDL,00,00,N danych]` i wywołuje ogólny sender COM.
- Podobny bufor/indeks 2048 występuje po stronie RX (`0x403850`) oraz w zbiorczej historii pakietów TX/RX.
- Po każdej iteracji wątek nadajnika wywołuje **`Sleep(10 ms)`** (`0x404040`, analogicznie `0x409D02`). To *odstęp pętli hosta*, nie dowód 10 ms opóźnienia między wszystkimi ramkami na samej magistrali, ale może ograniczać szybkość emisji tego programu.
- Kod historii odbioru przesuwa wskaźnik odczytu przy pełnej kolejce, więc **bezstratność przy dużym obciążeniu nie jest zapewniona**.
- Analizowana ścieżka TX nie pokazuje własnej walidacji `N<=8` przed kopiowaniem danych z 20-bajtowego rekordu; walidacja może istnieć u producenta wiadomości, **nie wolno zakładać jej nieobecności w całej aplikacji**. Własny sterownik powinien jawnie ograniczyć DLC do 0..8.

## 4. CAN11 i CAN29

W dwóch ścieżkach TX standardowy ID jest kodowany:

```text
SIDH = (id >> 3) & 0xFF
SIDL = ((id & 7) << 2)
TX   = 60 (N+4) SIDH SIDL 00 00 [N bajtów]
```

RX `0x70`: `id=(SIDH<<3)|((SIDL>>2)&7)`, `N=length-4`. Weryfikacja **offline** dla wszystkich **2048** możliwych ID CAN11 dała poprawny round-trip 2048/2048. **To test matematyczny, nie pomiar sprzętu.**

**CAN29 nie zostało wykazane w żadnej z tych konkretnych ścieżek**. Dwa dodatkowe bajty nagłówka nie stanowią same w sobie dowodu CAN29; nadawanie CAN11 w EXE ustawia je na zero, a RX dekoduje standardowy ID. Nie przenosić niezweryfikowanego algorytmu CAN29 z innej DLL.

## 5. Czas przy RX i TX

`0x40386C` i `0x40951C` wywołują **`GetTickCount`** (Win32 import IAT `0x47D328`) i odejmują zapamiętany początek sesji; przy zapisie TX do historii jest analogiczny `GetTickCount` (`0x403ED3`). Później rekordy są kopiowane do wspólnej struktury historii, porównywane z wartościami czasu poprzednich wpisów i w pewnych przypadkach przesuwane w tablicy (`0x4038F3–0x40396E`).

**Wniosek:** to znaczniki **aplikacji Windows**, a nie sprzętowe timestampy SOF CAN. Nie można na ich podstawie odtwarzać mikrosekundowej kolejności zdarzeń magistrali ani gwarantować, że historia reprezentuje dokładnie kolejność odbioru z kontrolera PIC. Test sniffera musi osobno analizować utratę ramek i opóźnienia UART/FTDI.

## 6. Statusy i błędy

- `60 00` powoduje zerowanie zmiennej `0x49C698` albo `0x49C6B4`. **Nie dowodzi fizycznego ACK na CAN**.
- Parser odbiera `0x60` o długości **0..4 B**, ale dyspozytor traktuje jawnie tylko **length=0**. Dodatkowe statusy 1..4 B pozostają **nierozpoznane**.
- `0x404300` nie sprawdza odpowiedzi PIC; `0x404270` sprawdza opcode w oknie 100 ms, ale wrapper `0x40A3D0` może niedoskonale sygnalizować błąd `WriteFile/GetOverlappedResult` (opisany we wcześniejszym raporcie).
- Nie znaleziono potwierdzonego trybu CAN **listen-only bez ACK**, ramki błędów, szczegółów bus-off, pełnego zestawu statusów kontrolera lub mechanizmu znaczników czasowych PIC.

## 7. Uważna inwentaryzacja opkodów

| Opcode | Stan w analizowanym EXE 2.5 |
| --- | --- |
| `0x50`, `0x51` | **nadawane** w zależności od indeksu GUI, funkcje `0x404210`/`0x4041B0` |
| `0x53` | **nadawane**, dwie ścieżki z różną kontrolą odpowiedzi |
| `0x60` | **nadawany** przez worker TX, odpowiedź `60 00` obsługiwana |
| `0x70` | **odbierany** jako CAN11 |
| `0x52`, `0x54`, `0x6F` | kod obecny w deskryptorach; pełne funkcje nadawania/semantyka **nieudowodnione w zbadanych ścieżkach EXE**. `0x52` jako odczyt pochodzi z osobnej DLL/logów |
| `0x55`, `0x5F` | znane z **innej implementacji J2534**, **niepotwierdzone** jako wykonana komenda PC→PIC w tym EXE 2.5 |

Dosłownej sekwencji bajtów `55 03 01 FA 07` **nie znaleziono w pliku EXE**. To **nie jest dowód**, że firmware jej nie obsługuje (program może konstruować ją dynamicznie lub korzystać z domyślnych parametrów).

## 8. Nowe testy CAN (kolejność)

1. **KCAN-D036:** w logu portu porównać inicjalizacyjny zapis `0x53` i ten z okna „Set Filter”; obie odpowiedzi PIC; odczyt `0x52` po konfiguracji.
2. **KCAN-D037:** test TX worker `Sleep(10 ms)`: porównać żądaną częstotliwość ramek, czas na UART i fizycznym CAN na izolowanej magistrali.
3. **KCAN-D038:** test pełności RX 2048 slotów: strumień znanych ramek + niezależne referencyjne timestampy i identyfikatory sekwencji; zmierzyć straty.
4. **KCAN-D039:** sprawdzić warianty `60 length=1..4` tylko przez obserwację/symulację offline; `60 00` nie równa się ACK.
5. **KCAN-D040:** przypisać konkretne `0x50/0x51` do tekstów opcji GUI i aktywności magistrali; bez samochodu.
6. **KCAN-D041:** najpierw porównać deskryptory `0x52/0x54/0x6F` i konfigurację `0x55` z **prawdziwym logiem PC↔PIC**, nie próbować nieznanych rozkazów w ciemno.
7. **KCAN-D042:** wyłącznie offline weryfikować limity DLC/N oraz segmentację i ponowną synchronizację parsera.

**Wniosek:** EXE 2.5 pozwala już wiarygodnie napisać **prototyp warstwy hosta CAN11**. Zgodność z konkretnym PIC, faktyczny tryb nasłuchu bez ACK, CAN29 i odczyty stanu błędów pozostają niepotwierdzone.

Pliki oryginalne nie są zapisywane w GitHub. Projektowe zasady i dalsze kroki: [HANDOFF_NEXT_CHAT.md](HANDOFF_NEXT_CHAT.md).
