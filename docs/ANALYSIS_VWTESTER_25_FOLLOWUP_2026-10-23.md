# Commander FULL 2.5 — druga analiza: brakujące funkcjonalności

**Data:** 2026-10-23. **Analiza statyczna** otrzymanego `k+can2.5(1).zip` i `VWTester.exe`; bez uruchamiania EXE/DLL i bez komunikacji z pojazdem. Kontrolny SHA-256 EXE: `b90fc612decb04759a77fd0f02946157d832053186c7adf5e50624a1b103a10d`. Adresy VA tylko dla tej binarki.

**Cel ponownej analizy:** szukać funkcji wcześniej nieopisanych, nie mylić wzorców bajtów z wykonującym się kodem, oddzielić protokół *PC–PIC* od K-Line/KWP i CAN magistrali.

## Wnioski — skrót

1. Kod hosta zawiera **parser strumieniowy** potwierdzający komunikaty `0x70` z długością `4–12`, `0x60` z długością `0–4` oraz porównujący inne odpowiedzi do ośmiu zdefiniowanych opisów.
2. **Wersja 2.5 ma mechanizm ciągłego odbioru asynchronicznego** i osobne kolejki ramek CAN; nie musi wysyłać zapytania PC→PIC na każdą ramkę odbieraną przez CAN.
3. Dwie klasy komunikacyjne mają **bardzo podobny kod** RX/TX, co wspiera tezę o współdzielonym protokole hosta, ale nie wystarcza do przypisania jednej klasy do CAN, a drugiej do K-Line.
4. **`0x50` vs `0x51` wybiera UI:** kod odczytuje wybraną pozycję listy rozwijanej (`CB_GETCURSEL = 0x147`), a potem wywołuje jedną z dwóch funkcji wysyłających `50 00` lub `51 00`. Kierunki CAN/K-Line trzeba jeszcze zmapować do pozycji.
5. Osobna ścieżka tworzenia `0x53` grupuje **6 × 4 B + 2 × 4 B**. To dużo mocniejszy dowód na sześć filtrów i dwie maski akceptacyjne niż sam rozmiar 32 B.
6. Kod rozpoznaje i obsługuje krótkie odpowiedzi `0x60` z **długością do 4**, a nie tylko `60 00`. Znaczenie dodatkowych bajtów i potwierdzenia fizycznego ACK nie zostało wyjaśnione.
7. **Nadal nie wykazano** poprawnej konfiguracji trybu listen-only, CAN29, kodów błędów firmware ani jednoznacznej semantyki `0x54`, `0x6F`, `0x5F`.

## 1. Parser ramkowania i sprawdzanie poprawności odpowiedzi

### Funkcja `0x4037D0`

Podczas napływania bajtów przez COM program sprawdza, czy nagłówek `[opcode, length]` jest akceptowalny.

| Opkod | Warunek w kodzie | Znaczenie |
| --- | --- | --- |
| `0x70` | `4 <= length <= 12` | 4-bajtowy nagłówek CAN + 0–8 B danych |
| `0x60` | `length <= 4` | Krótkie odpowiedzi adaptera, także `60 00` |
| Inne | kod i długość zgodne z jednym z **8 wpisów** tablicy buforów przy `0x490828` | Walidacja odpowiedzi na polecenia skonfigurowane przez program |
| Inne / niezidentyfikowane | odrzucane | Próba ponownej synchronizacji strumienia |

Weryfikacja: `0x4037D8–0x403845`. Tablica ma elementy o kroku `0x22` (34 B). W konstruktorze `0x403B38–0x403B9C` widoczne są przygotowane kody `50,51,52,53,54,60,6F,70`. **Zarejestrowanie bajtu `0x54` lub `0x6F` jako kodu oczekiwanego nie dowodzi jeszcze, że funkcja jest inicjowana w konkretnej sesji.**

### Asynchroniczne składanie komunikatów

- `0x404070–0x4041A7`: stanowy parser napływających bajtów, najpierw opcode, potem length, potem `length` bajtów payloadu.
- `0x404110`: walidacja przez `0x4037D0`. Po nieprawidłowym nagłówku wykonywany jest reset parsera (`0x4094F0`) i **ponowna interpretacja problematycznego bajtu** jako możliwego początku nowej wiadomości (dekrementacja indeksu).
- `0x40418A`: wywołanie kompletnego dyspozytora odpowiedzi `0x403850`.
- Druga, pokrewna ścieżka: `0x409D30` jako parser i `0x409500` jako dyspozytor.
- W buforze parsera indeks danych jest **8-bitowy** (`[object+0x456]`), co samo w sobie nie określa maksymalnego dopuszczalnego rozmiaru innych wiadomości. Należy polegać na rzeczywistych limitach protokołu, nie na samym rozmiarze wskaźnika.

**Wniosek dla własnego sterownika:** potrzebny jest parser strumieniowy odporny na podzielone/łączone odczyty USB–COM, z walidacją długości, timeoutem i synchronizacją. Nie zakładać „jedno ReadFile = jedna wiadomość”.

## 2. Mechanizm ciągłego odbioru

- Wątek czytający COM w `0x40A160` wykonuje `ReadFile` z buforem **0x400 = 1024 B**, a następnie przekazuje otrzymane bajty do funkcji przetwarzającej `0x404070` albo drugiej klasy.
- Funkcje `0x403850` i `0x409500` rozpoznają `0x70` i odkładają ramki do struktur pamięci programu.
- `0x403E01–0x403E2F`, `0x403970–0x4039B8` i analogiczne gałęzie stosują indeksy kolejki maskowane przez **`0x7FF`**: **2048 slotów**.
- Obiekty ramki kopiowane są instrukcją `rep movs DWORD PTR` z licznikiem **5**: zapis **20 B na slot**, obejmujący ID, DLC, dane i pola towarzyszące (konkretna semantyka wszystkich pól nieodtworzona).
- W przypadku dogonienia indeksu odczytu przez zapis kod przesuwa indeks odczytu, co może oznaczać **utratę najstarszego rekordu przy zapełnieniu kolejki**.
- W kodzie występuje mechanizm nadpisania/skonsolidowania rekordów zależnie od ich znaczników czasu i powiązanych wskaźników. Bez testów nie wolno twierdzić, że każde `0x70` jest bezstratnie rejestrowane pod wysokim obciążeniem.

**Rozdzielamy:** aktywny, ciągły odczyt hosta `0x70` jest mocno udokumentowany; elektryczna pasywność CAN (bez ACK), pełny dump wszystkich ID oraz zachowanie filtrów pozostają niepotwierdzone.

## 3. Wybór trybu przez GUI — `0x50` / `0x51`

W funkcji **`0x41A9E0`** aplikacja po otwarciu portu odczytuje wybrany element kontrolki combo. Ślad:

```text
0x41AA33: identyfikator kontrolki 0x42A
0x41AA44: komunikat Win32 0x147 (CB_GETCURSEL)
0x41AA50: test wyniku
0x41AA56: wywołanie 0x404210 -> 50 00
0x41AA5D: wywołanie 0x4041B0 -> 51 00
```

Ponieważ kod `test al, al` porównuje **najmłodszy bajt wyniku**, istnieje teoretyczny szczegół implementacyjny dotyczący większych indeksów; normalnie lista ma niewiele pozycji. W praktyce dla indeksu 0 wykonywane jest `50 00`, dla pozostałych `51 00`.

Obie funkcje po wysłaniu odczekują do **100 ms** na zdarzenie i porównują zwrócony opcode (`0x4041B0–0x40420A`, `0x404210–0x40426A`). Ten timeout dotyczy ścieżki hosta w EXE, nie jest deklaracją uniwersalnej charakterystyki firmware.

**Hipoteza**: dwa tryby odpowiadają CAN/K-Line, ale kod nie przypisuje jeszcze tekstów pozycji kontrolki do `0x50/0x51`. Test KCAN-D013 zostaje **częściowo rozstrzygnięty po stronie hosta**, nie po stronie PIC.

## 4. Rozszerzenie struktury 32-bajtowego bloku `0x53`

W `0x40E490–0x40E565` program buduje polecenie z nagłówkiem `53 20` i dwoma osobnymi pętlami:

```text
0x40E4E3–0x40E513: 6 iteracji x 4 B
0x40E515–0x40E545: 2 iteracje x 4 B
0x40E547–0x40E560: nadanie 2 + 32 B
```

Dla każdego z ośmiu wpisów tej ścieżki składane są bajty:

```text
SIDH = (id >> 3) & 0xFF
SIDL = ((id & 7) << 2) & 0x1C
EID8 = 00
EID0 = 00
```

Wynikowy układ to **6 wpisów po 4 B, następnie 2 wpisy po 4 B**. Najbardziej prawdopodobna interpretacja: **6 filtrów akceptacyjnych + 2 maski** kontrolera PIC18. Jest to **mocna hipoteza funkcjonalna z konstrukcji kodu**, a nie jeszcze niezależny odczyt rejestrów PIC.

**Ważny szczegół:** istnieje także inna ścieżka `0x419510–0x4195C9`, która ustawia dodatkowe stałe bity, w tym `0x40` w pierwszym bajcie określonego wpisu i `0x60` w jednym z dalszych pól. Nie wolno więc opisywać każdego bloku `0x53` jako wyłącznie ośmiu identyfikatorów CAN11. Co oznaczają te flagi — nieustalone. Użytkownik nie powinien eksperymentalnie kopiować losowych bloków filtrów do pojazdu.

## 5. Potwierdzenia TX i inne braki

### TX `0x60`

- Walidator odpowiedzi akceptuje `0x60 length=0..4`; dotychczasowa analiza logów pokazuje przypadek `60 00`. **Nie znamy semantyki innych payloadów odpowiedzi.**
- `0x403E54–0x403EC1` pozostaje potwierdzeniem wysyłania `length=N+4` dla CAN11.
- Przed nadaniem i w trakcie programu występuje zapis/odczyt współdzielonego statusu dotyczącego `0x60`, ale nie zidentyfikowano kompletnego mapowania błędów CAN.

### USB/COM i odtwarzanie po błędzie

- `0x40A4F0`: ponownie potwierdzono UART 833333 oraz `SETDTR → 500 ms → CLRDTR → SETRTS/CLRRTS`.
- `0x40A3D0`: asynchroniczny `WriteFile`, `WaitForSingleObject` do 500 ms i próba `GetOverlappedResult`.
- `0x40A160`: wątek odbioru COM i `ReadFile`.
- **Nie rozpoznano jeszcze** pełnej procedury automatycznego ponownego otwierania portu, timeoutów poszczególnych opkodów ani komunikatów błędów samego PIC.

### Co nadal nie ma wiarygodnego potwierdzenia

| Funkcjonalność | Stan po ponownej analizie |
| --- | --- |
| `0x54`, `0x6F` | Obecność w deskryptorach wiadomości, ale brak pewnej funkcji/formatu w obserwowanej ścieżce |
| `0x5F` | Poznane z DLL J2534, nie potwierdzone w tej ścieżce EXE 2.5 |
| `0x55` do konfiguracji CAN bitrate | Wewnętrzny kod EXE nie dał niezależnego potwierdzenia tej samej sekwencji co DLL; `0x55` występuje również jako **zwykła wartość diagnostyczna**, więc nie wolno uznawać każdego wystąpienia za opcode PC↔PIC |
| CAN29 | Brak zweryfikowanej ścieżki kodowania i odbierania dla 29-bitowych ID w tym EXE |
| listen-only / ACK | Brak dowodu sterowania trybem CAN bez ACK |
| DLC/RTR/statusy | Host obsługuje N=0..8 w RX, ale nie rozpoznano obsługi flag RTR ani pełnej listy kodów błędów |
| K-Line | Widoczne liczne ścieżki formatowania diagnostyki, bez kompletnej mapy opcode PC↔PIC dla tego toru |

## 6. Rekomendowana kolejność testów

1. **Bez auta, na stanowisku**: ustalić który wariant wyboru w GUI prowadzi do `50 00` / `51 00`; przechwycić opcode, odpowiedź i DTR/RTS.
2. Po potwierdzeniu zgodności adaptera: użyć **odczytu `52 00`** i zanotować surowy 32-bajtowy blok konfiguracji bez zapisywania.
3. Na izolowanym CAN: porównać `0x60` o N=3 i N=8; niezależnie zarejestrować rzeczywisty DLC.
4. Dla `0x53`: wyłącznie na izolowanej magistrali i po zachowaniu kopii konfiguracji ustalić odwzorowanie **6+2** oraz znaczenie bitów `0x40/0x60`.
5. Zmierzyć limit odbioru ciągłego i skutki przepełnienia hosta; sprawdzić, co pozostaje w strumieniu `0x70`, gdy CAN jest obciążony.
6. Zbadać odmienne odpowiedzi `0x60` (length 1..4) jedynie przez obserwację bez celowego generowania awarii pojazdu.

**Rejestr rozbieżności:** [DISCREPANCIES.md](DISCREPANCIES.md). Żaden kod ani surowe pliki nie były wykonywane ani commitowane.
