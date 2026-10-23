# Rejestr rozkazów (roboczy)

**Dotyczy** badanej biblioteki `J2534KCAN.dll` i pięciu logów KCANTEST. Nie jest to oficjalna dokumentacja producenta. Kodowane wartości to bajty HEX.

| Kod | Kierunek | Przykład | Interpretacja | Dowód / pewność |
| --- | --- | --- | --- | --- |
| `0x50` | PC → PIC | `50 00` | Początkowe polecenie w historycznym opisie programu CASCADE; funkcja nieznana | Zewnętrzny log; nie występuje w pięciu analizowanych logach |
| `0x52` | PC → PIC | `52 00` | Odczyt bloku konfiguracji (32 B) | **DLL + log** |
| `0x52` | PIC → PC | `52 20 [32 B]` | Dane odczytane z konfiguracji | **log** |
| `0x53` | PC → PIC | `53 20 [32 B]` | Zapis bloku konfiguracji używanego m.in. przez funkcję filtrów | **DLL + log** |
| `0x53` | PIC → PC | `53 00` | Odpowiedź na zapis (bez payloadu) | **log** |
| `0x55` | PC → PIC | `55 03 01 FA 07` | Ustawienie parametrów CAN, przykład 500 kbit/s | **DLL + log** |
| `0x55` | PIC → PC | `55 00` | Odpowiedź na `0x55` | **log** |
| `0x5F` | PC → PIC | `5F 00` | Polecenie inicjalizacyjne — szczegóły nieznane | **DLL**, bez przykładu w pięciu logach |
| `0x60` | PC → PIC | `60 0C ...` | Nadawanie klasycznej ramki CAN (nagłówek 4 B + dane 8 B) | **DLL + log** |
| `0x60` | PIC → PC | `60 00` | Krótka odpowiedź adaptera na żądanie nadawania | **log** |
| `0x70` | PIC → PC | `70 0C ...` | Odebrana ramka CAN (nagłówek 4 B + dane 8 B) | **DLL + log** |

## Ważne ograniczenia

1. **`60 00` nie stanowi potwierdzenia ACK przez inne urządzenie na CAN.**
2. Komendy `0x53`, `0x55`, `0x60` zmieniają stan adaptera lub magistrali. Nie należy ich wysyłać do samochodu bez zweryfikowania warunków.
3. Odczyt/zapis bloku `0x52/0x53` nie oznacza, że w pełni poznano mapowanie rejestrów PIC.
4. Nie wykazano listy błędów, kodów wyjątków ani pełnego protokołu synchronizacji i recovery.

## Ślady w DLL (adresy wirtualne z poprzedniej analizy statycznej)

| Obszar | Adres (VA) |
| --- | --- |
| UART 833333 | `0x41D32D` |
| Inicjalizacja `0x5F` | `0x41D499` |
| Odczyt `0x52` | `0x41D4AD` |
| Ustawienie CAN `0x55` | `0x41D4CE–0x41D508` |
| Budowa `0x60` | `0x41B6DC–0x41B7B7` |
| Dekodowanie `0x70` | `0x41B286–0x41B319` |
| Konstrukcja `0x53` / filtry | `0x41EC62` |

Adresy odnoszą się wyłącznie do biblioteki SHA-256 `3b8cc66f95a174a0a3b5c94a5a8976e34c5211798dbdfd8105903038fd2bf09b`. Inne kompilacje mogą mieć inne adresy.


---

## Dodatkowe potwierdzenia z innej kompilacji — `VWTester.exe` FULL 2.5

EXE 2.5 SHA-256: `b90fc612decb04759a77fd0f02946157d832053186c7adf5e50624a1b103a10d`. Poniższe są **potwierdzone w kodzie tej kompilacji**, lecz nie zostały zweryfikowane na fizycznym adapterze.

| Kod | Zidentyfikowane zachowanie | Adresy VA 2.5 | Status |
| --- | --- | --- | --- |
| `0x50` | Nadanie krótkiego polecenia z bufora, zwykle `50 00`, i kontrola opkodu odpowiedzi | `0x403B4C`, `0x404210` | **EXE 2.5**; dokładny sens nieznany |
| `0x51` | Nadanie krótkiego polecenia `51 00` i kontrola opkodu odpowiedzi | `0x403B53`, `0x4041B0` | **EXE 2.5**; dokładny sens nieznany |
| `0x52` | Inicjalizowany bufor polecenia (wcześniej 32-bajtowy odczyt z DLL + logów) | `0x403B5A` | **EXE 2.5** (inicjalizacja bufora), semantyka z wcześniejszej DLL |
| `0x53` | Zapis **32 bajtów** jako `53 20 [32 B]`, kontrola opkodu odpowiedzi | `0x404270–0x4042ED` | **EXE 2.5 + wcześniejsze DLL/logi** |
| `0x54` | Kod inicjalizowany w buforach wiadomości | `0x403B68`, `0x403B8F` | **EXE 2.5**; semantyka i kierunek nieustalone |
| `0x60` | Nadanie CAN11 z **N-bajtowym** payloadem i `length=N+4` | `0x403E54–0x403EC1` | **EXE 2.5**; niezależne potwierdzenie kodowania |
| `0x6F` | Kod inicjalizowany w buforze wiadomości | `0x403B95` | **EXE 2.5**; semantyka nieustalona |
| `0x70` | Odebrana ramka CAN11 z **N=length-4** bajtami danych | `0x403850–0x4038D0` | **EXE 2.5**; niezależne potwierdzenie RX |

**Uściślenie względem tabeli na początku dokumentu:** stwierdzenie „`0x50` tylko w zewnętrznym logu” dotyczyło **materiału dostępnego przed analizą EXE 2.5**. Teraz mamy osobne, mocniejsze potwierdzenie kodowe `0x50` oraz pierwszą przesłankę `0x51`.

Zgodność 2.5 z konkretnym firmware oraz znaczenie `0x54`/`0x6F` pozostają otwarte; nie traktować tych kodów jako poleceń gotowych do nadawania do samochodu. [Pełny raport](ANALYSIS_VWTESTER_25_2026-10-23.md).


### Ważne doprecyzowania (ponowna analiza EXE 2.5)

- `0x50` i `0x51`: w `0x41AA33–0x41AA5D` wywołanie Windows `SendMessage(..., CB_GETCURSEL=0x147,...)` wybiera przy pozycji 0 **`50 00`**, a w innych przypadkach **`51 00`**. Są to więc alternatywne polecenia zależne od opcji w GUI, **bez jeszcze ustalonego mapowania CAN/K-Line**. Ich funkcje sprawdzają odpowiedź w oknie do 100 ms.
- Odpowiedź `0x60` z PIC: parser `0x4037D0` akceptuje **`length<=4`**, a nie tylko `60 00`. Kody/payloady 1..4 pozostają niezidentyfikowane.
- `0x70`: parser dopuszcza **`length=4..12`**, czyli 0..8 B CAN; to ograniczenie wykonawcze tej wersji EXE.
- `0x54` / `0x6F`: występują w deskryptorach rozpoznawania odpowiedzi, ale nie ustalono, w jakich warunkach są nadawane ani co oznaczają. Nie są gotowymi do wysyłania komendami.
- `0x55`: występuje wielokrotnie także w kodzie dotyczącym diagnostyki ECU. **Nie należy przypisywać tych wystąpień komendzie konfiguracji prędkości CAN** znanej z innej DLL.

Zobacz [ANALYSIS_VWTESTER_25_FOLLOWUP_2026-10-23.md](ANALYSIS_VWTESTER_25_FOLLOWUP_2026-10-23.md).

## Potwierdzenia wykonawczego kodu z Commandera 3.0 beta i 4.5 (2026-10-23)

| Polecenie | 3.0 beta | 4.5 | Uwaga |
| --- | --- | --- | --- |
| **`0x60` PC→PIC** | TX `0x403510` | TX `0x4034F0` | Budowa **CAN11 `length=N+4`** z ID i N bajtami; dowód z kodu hosta |
| **`0x70` PIC→PC** | RX `0x402D10`; walidator `0x402C80` | RX `0x402CE0`; walidator `0x402C40` | Akceptowane `length=4..12`; dekodowanie ID CAN11 |
| **`0x53` PC→PIC** | `0x403470`, budowa filtrów `0x40A3F9` | `0x403450`, budowa filtrów `0x40A489` | `53 20 [32B]`, **6×4 + 2×4 B** |
| **`0x60` PIC→PC** | walidacja poprzez ogólne deskryptory; brak osobnej gałęzi w zbadanej funkcji | `0x402C64`: **`length<=4`** | Nie jest to fizyczny ACK; semantyka statusów nieznana |

**Uwaga dotycząca `0x50/0x51/0x52/0x54/0x55`:** ich wartości występują również w kodzie niezwiązanym bezpośrednio z ramkowaniem CAN; **nie przypisujemy żadnego nowego znaczenia PC↔PIC bez wywołania nadawczego i kontekstu**. To szczególnie ważne dla `0x55` z bibliotek J2534. Raport: [ANALYSIS_VAGCAN_30BETA_45_2026-10-23.md](ANALYSIS_VAGCAN_30BETA_45_2026-10-23.md). Zgodność z konkretnym PIC/firmware pozostaje do przetestowania.

## Dodatkowe opkody ze starych EXE: C0 i odpowiedzi (2026-10-23)

Wykonawcze funkcje TX **3.0 beta** i **4.5** ujawniają sekwencję inicjalizacji **`51 00` → `C0 00` → `53 20 [32B]`**, rozdzieloną dwoma `Sleep(50)`. W 4.5 odpowiednie adresy wywołań to `0x409F0F`, `0x409F25`, `0x409FC4`, w 3.0 `0x409E84`, `0x409E99`, `0x409F38`.

| Opcode/ramka | Kierunek | Dowód | Ograniczenie |
| --- | --- | --- | --- |
| **`C0 00`** | **PC→PIC** w 3.0 beta i 4.5 | Szablon TX `0x44A8A8/0x44C8A8`, rzeczywiste wywołania TX `0x4033F0/0x4033D0`, oczekiwana odpowiedź RX `C0 00` | **Nowa komenda na poziomie kodu hosta. Semantyka NIEZNANA, nie wysyłać jej w ciemno**, nie utożsamiać z `50 00` z FULL 2.5 |
| `51 00` | PC→PIC | 3.0 `0x403370`, 4.5 `0x403350` | Starsza komenda inicjalizacji |
| `53 20 [32B]` | PC→PIC | 3.0 `0x403470`, 4.5 `0x403450` | Potwierdzona budowa hosta, działanie filtrów w PIC nieznane |
| `52 20` | PIC→PC (oczekiwany format RX) | Tablice walidacji 3.0/4.5 | Długość danych 32 B; nie jest dowodem, że GUI w tych ścieżkach nadaje `52 00` |
| `54 02` | PIC→PC (oczekiwany RX) | Tablice walidacji 3.0/4.5 | **Oczekiwana odpowiedź o 2 B**, treść i semantyka nieznane; nie znaleziono wykonawczego TX w badanej inicjalizacji |
| `6F 00` | PIC→PC (oczekiwany RX) | Tablice walidacji 3.0/4.5 | Semantyka nieznana |
| **`60 00`** | PIC→PC | Tablica 3.0 `0x44A998`, walidator `0x402C80` | **Dokładnie N=0** w badanym parserze 3.0 |
| **`60 00..04`** | PIC→PC | Walidator 4.5 `0x402C64` | **N=0–4**, semantyka dodatkowego payloadu nadal nieznana |
| `70 04..0C` | PIC→PC | Obie wersje mają osobny walidator | CAN11, N=0..8, kod hosta |

Pełny kontekst adresowy i rozróżnienie TX/RX w [ANALYSIS_VAGCAN_30BETA_45_DEEP_2026-10-23.md](ANALYSIS_VAGCAN_30BETA_45_DEEP_2026-10-23.md). **Żadna z nowych danych nie jest pomiarem konkretnego adaptera**.

## Granice komend 0x60/0x70 i init w audycie CAN29 (2026-10-23)

**Audyt wykonawczych ścieżek 3.0 beta/4.5:** `0x60` TX pobiera **WORD ID**, konstruuje nagłówek wyłącznie `((ID>>3)&FF),((ID&7)<<2),00,00`. `0x70` RX zwraca ID `(byte2<<3)|((byte3>>2)&7)` zapisane jako WORD, bez odtworzenia wyższych 18 bitów i bez flagi IDE. **Nie należy oferować tych funkcji jako CAN29.** Przykład `0x18DAF110` i `0x110` kodują się w tym TX identycznie (`22 00 00 00`). Nie odnaleziono drugiej, jawnie zakodowanej ścieżki CAN29 w prześledzonym kodzie; **sam surowy zapis bajtów przez interfejs GUI `0x403740` nie oznacza obsługi EID29**.

Przy starcie oba EXE nadają **`51 00` → `C0 00` → `53 20[32]`**; żadna z tych komend **nie ma jeszcze potwierdzonej funkcji włączania CAN29**. Nie dorabiać nowych opkodów do `0x54/0x6F/0x61/0x71` bez dowodu TX/RX. Szczegóły: [ANALYSIS_CAN29_INIT_30BETA_45_2026-10-23.md](ANALYSIS_CAN29_INIT_30BETA_45_2026-10-23.md).

## Co znaczy sukces transmisji 0x60 — uwaga z audytu UART (2026-10-23)

**Rozdzielać `UART_write_requested` / `UART_write_completed` / `PIC_0x60_status` / `physical_CAN_TX/ACK`.** Stare EXE 3.0 beta i 4.5 w funkcji `0x408BD0` nie sprawdzają końcowego wyniku `WriteFile/GetOverlappedResult` ani `bytesWritten`, zaś funkcje `0x403510/0x4034F0` **ignorują** wynik writer, zapisują historię CAN TX i zwracają **1 po `Sleep(10)`**, bez powiązania z odpowiedzią `0x60` PIC. Wpis TX w GUI nie jest dowodem sprzętowej transmisji lub ACK.

W `0x60` PC→PIC odczytywane jest N z pojedynczego bajtu rekordu i kopiowane do pakietu **bez lokalnego ograniczenia do Classical CAN DLC 0..8**; nie wnioskować stąd o CAN-FD, a w własnej implementacji zawsze walidować `N<=8`. Rozpoznano także GUI/raw-writer `0x403740` (ogólny strumień binarny UART) — **nie jest to nowa komenda CAN29 ani deklaracja zdolności firmware**. [Dokładne adresy i zastrzeżenia](ANALYSIS_SERIAL_TX_RELIABILITY_30BETA_45_2026-10-23.md).
