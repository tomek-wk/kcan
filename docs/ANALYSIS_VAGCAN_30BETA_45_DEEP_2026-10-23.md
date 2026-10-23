# Dalsza analiza Commander 3.0 beta/4.5: PORT, C0 i parser odpowiedzi — 2026-10-23

**Źródło:** dostarczone przez użytkownika `VAG-CAN Commander V4.5.zip` (SHA-256 `e7980df7b33847af86ad12c52ae99c377b39c1d8f067abbe12e2d8c5de5e2b1c`). Pliki, po statycznym rozpakowaniu: `VAG-CAN Commander 3.0 beta.exe` SHA-256 `dfb5e3f4724f6898c7c82d5d6e69ed3f795edb5f536f4aa5ff37ab17eae2a39b`, `VAG-CAN Commander4.5.exe` SHA-256 `85e89882a434ad83d19381ecbb5f9e77b14b237343b1432feb2f7300810e0050`. Rozszerzenie poprzedniego raportu [ANALYSIS_VAGCAN_30BETA_45_2026-10-23.md](ANALYSIS_VAGCAN_30BETA_45_2026-10-23.md).

**Metoda:** analiza *wyłącznie statyczna*: `objdump -D -Mintel`, analiza offsetów pliku/VA, tablic importów PE i tablic danych, kontrola surowych bajtów kodu. **Nie uruchomiono** żadnego EXE, sterownika, firmware ani nie użyto adaptera/pojazdu. Opisy „potwierdzone” poniżej dotyczą tylko kodu programu na PC, chyba że podano wyraźnie inaczej. Nie publikowano binariów ani surowych logów.

## 1. ROZSTRZYGNIĘCIE: warunek UART 115200/833333 odnosi się do numeru COM, nie trybu GUI

Pierwszy raport prawidłowo identyfikował rozgałęzienie w **4.5 `0x40317E`**, ale **nie ustalił znaczenia argumentu**. Teraz prześledzono pełny łańcuch:

| Etap | 4.5 | 3.0 beta | Dowód |
| --- | --- | --- | --- |
| Odczyt konfiguracji | `0x409CA5..0x409D11` | `0x409C25..0x409C85` | Buduje ścieżkę `\\TESTER.INI` od katalogu bieżącego; `GetPrivateProfileIntA("COM","PORT",0,path)` |
| Globalna numeracja | **`0xDC23E4`** (`0x409D11`) | **`0x015B0364`** (`0x409C85`) | Wartość `[COM] PORT` składowana bez pośredniego mapowania w tej ścieżce |
| Wywołanie open | `0x409EEB..0x409EFA` | `0x409E5F..0x409E6E` | `push [PORT]` → wrapper `0x403110` / `0x403140` |
| Konfiguracja obiektu | `0x403170..0x4031A0` | `0x4031A0..0x4031C4` | Numer `PORT` służy jednocześnie do indeksowania struktury połączenia i jako argument funkcji otwierającej |
| Baud | **`cmp esi,2`** (`0x40317E`) | stałe `push 0xCB735` (`0x4031B2`) | W 4.5 **PORT 0/1→115200**, **PORT >=2→833333**. W badanej funkcji 3.0 beta zawsze 833333. |
| Nazwa urządzenia | `0x408CD0..0x408D18` | te same adresy | `sprintf("COM%d", PORT & 0xFF)` i bezpośrednie `CreateFileA` |

**Dekodowanie importów** przy użyciu tablicy PE: 4.5 `[0x44C260]=GetCurrentDirectoryA`, `[0x44C264]=GetPrivateProfileIntA`, `[0x44C26C]=CreateFileA`; w pliku dosłownie `COM`, `PORT`, `\\TESTER.INI`, `COM%d`. Wersja 3.0 beta wykonuje analogiczną sekwencję z globalną `0x015B0364`.

**Wniosek dla dostarczonego INI:** `[COM] PORT=4` → 4.5 wybiera **833333 bit/s** i nazwę **COM4**, tak samo prędkość 833333 w zbadanej ścieżce 3.0. **Nie ma tu dowodu na selekcję CAN/K-Line przez gałąź 115200/833333.** Jest to zależność od *numeru portu COM* i potencjalna pułapka implementacji (COM1=115200 przy oczekiwanym adapterze 833333). Nie jest to pomiar UART na FTDI/PIC.

**Dodatkowa obserwacja:** kod tworzy **16 obiektów portu** (4.5 `0x402FF8..0x403013`) i mnoży indeks `PORT` przez rozmiar rekordu 332 B w `0x403170`. Nie zidentyfikowano kontroli zakresu we wskazanej funkcji. Nie należy próbować `PORT>15` bez odrębnej analizy granic pamięci. Niezależnie, dopuszczalność `PORT=0` lub liczby ujemnej nie została wykazana.

## 2. Ograniczenie COM10+ względem FULL 2.5

Obie starsze kompilacje konstruują **dosłownie `COM%d`** i przekazują je do `CreateFileA` (4.5 `0x408CF0..0x408D18`; 3.0 te same adresy). Nie zaobserwowano w tej ścieżce prefiksu `\\\\.\\` dla COM10+.

- Microsoft [CreateFileA](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-createfilea) explicite wymaga dla numerów **COM10+** nazwy **`\\\\.\\COM10`**.
- **Wynik statyczny:** otwieranie COM10+ w tej ścieżce starych EXE ma **przewidywaną niezgodność** ze standardową semantyką Win32; test sprzętowy nie jest niezbędny do wykazania problemu w tym konkretnym wywołaniu. Nie wykluczono specjalnego środowiska, przekierowania nazw lub innej nieodnalezionej ścieżki.
- W **FULL 2.5** odnotowano już jawne wsparcie nazwy **`\\\\.\\COM%d`** dla COM10+, zatem kompatybilność numeracji portu różni się między wersjami. Do porównawczych testów 3.0/4.5 wskazane są **COM2–COM9** (COM1 w 4.5 jest dodatkowo obciążony odmiennym baud, nieznana kompatybilność sprzętowa).

## 3. NOWY ROZKAZ: `C0 00` (nie `50 00`) w inicjalizacji starszych kompilacji

W obu EXE znajduje się tablica *szablonów TX* po 34 B, start **4.5 `0x44C8A8`, 3.0 `0x44A8A8`**. Przykładowe wpisy: `C0 00`, `51 00`, `52 00`, `53 20`, `54 00`. Sam szablon nie dowodzi wywołania funkcji TX — poniżej wykazano użycie.

**4.5, wykonawcza sekwencja inicjalizacji w `0x409EEB..0x409FC4`:**
1. `0x409EFA`: otwiera **port z `[COM] PORT`**, przez wrapper `0x403110`; bez sprawdzenia wyniku warunkującego dalszy kod w widocznym fragmencie.
2. `0x409F0F`: wywołuje `0x403350` — funkcję zapisującą dokładnie 2 bajty **`51 00`** (szablon `0x44C8CA`) i oczekującą odpowiedzi/zdarzenia z timeoutem **100 ms**.
3. `Sleep(50 ms)`.
4. `0x409F25`: wywołuje `0x4033D0` — nadaje **`C0 00`** (szablon `0x44C8A8`), oczekuje odpowiedzi z timeoutem **100 ms**.
5. `Sleep(50 ms)`.
6. `0x409FC4`: wywołuje `0x403450` — konstruuje i nadaje **`53 20 [32 B]`**. Komponuje przy tym osiem wpisów po cztery bajty (patrz poprzedni raport). Procedura również używa oczekiwania do 100 ms.
 
**3.0 beta:** analogiczne wywołania `0x409E84`→`0x403370` (`51 00`), `0x409E99`→`0x4033F0` (`C0 00`), `0x409F38`→`0x403470` (`53 20`). Dostępna sekwencja potwierdza te same opkody i kolejność.

W szczególności to **faktycznie zbudowany kod TX `C0 00`**, a nie przypadkowa para bajtów. W FULL 2.5 wykazano z kolei polecenia **`50 00` / `51 00`** w określonej ścieżce. **Rola `C0` i jego zgodność firmware z `50` nieznane**; numer wersji archiwum nie udowadnia zgodności adapterów.

## 4. Ośmiowpisowe tablice RX: dowód dokładnego `60 00` vs zakres `60 00..04`

Tablice walidacji RX składają się z 8 rekordów po 34 B:
- **3.0 beta:** VA `0x44A998`.
- **4.5:** VA `0x44C998`.

Zdekodowano pierwsze dwa bajty każdego rekordu bezpośrednio z rozpakowanych binariów:

| Indeks | Odpowiedź: 3.0 beta | Odpowiedź: 4.5 | Uwagi |
| --- | --- | --- | --- |
| 0 | `C0 00` | `C0 00` | Oczekiwany echo/status polecenia C0, semantyka nieznana |
| 1 | `51 00` | `51 00` | Oczekiwana odpowiedź na 51 |
| 2 | `52 20` | `52 20` | 32-bajtowy blok odpowiedzi |
| 3 | `53 00` | `53 00` | Odpowiedź na zapis bloku |
| 4 | `54 02` | `54 02` | **Dwa bajty** odpowiedzi są oczekiwane przez walidator, bez potwierdzenia znaczenia |
| 5 | **`60 00`** | **`60 04`** | W 4.5 dodatkowa gałąź akceptuje **0..4**, więc deskryptor `60 04` nie oznacza ograniczenia do dokładnie 4 |
| 6 | `6F 00` | `6F 00` | Nieznana semantyka |
| 7 | `70 00` | `70 00` | RX CAN jest obsługiwany *oddzielną* gałęzią dopuszczającą length 4..12 |

**Walidator 3.0 `0x402C80..0x402CE6`:** dla `0x70` bezpośrednio akceptuje długość **4..12**; dla pozostałych kodów przegląda 8 rekordów i porównuje **zarówno opcode, jak i długość równą zapisanej**. Zatem **w tej konkretnej funkcji** dopuszcza dokładnie `60 00`, nie 1..4.

**Walidator 4.5 `0x402C40..0x402CB9`:** dla `0x70` dopuszcza **4..12**, a dla `0x60` osobny blok `0x402C64..0x402C74` wykonuje `length<=4`, tzn. **0..4**; pozostałe opkody przechodzą przez tablicę. **Ten kod potwierdza różnicę hosta, nie fizyczne ACK CAN**.

**Uwaga metodologiczna:** rekord `54 02` albo `6F 00` w tabeli walidacji dowodzi jedynie, że program umie taki format *zaakceptować*. **Nie dowodzi** nadawania odpowiednich rozkazów przez GUI lub firmware. Odrębne szablony TX `52 00`/`54 00` nie są same w sobie wywołaniami nadającymi.

## 5. Korekty i otwarte hipotezy

**Poprawka do wcześniejszego raportu:** frazę „w 4.5 parametr prędkości `<2`/ `>=2` bez mapowania do GUI” należy zastąpić silniejszym ustaleniem: **wartość jest wprost numerem `[COM] PORT`**. Nic w tym rozgałęzieniu nie potwierdza trybu K-Line/CAN. Poprzedni dokument zachowujemy jako chronologiczny, a to badanie stanowi jego korektę.

**Potwierdzone z aplikacji:** rzeczywista kolejność wysyłania `51 00` → `C0 00` → `53 20` w ścieżkach init obu starych EXE; format `C0 00` i tabelka odbioru; zależność baud od COM nr w 4.5; ścieżka COM%d, bez obsługi COM10+ przez standardowy namespace; dokładny zakres walidatora `0x60`.

**Wciąż niepotwierdzone:** wynik komunikacji z konkretną płytką PIC, działanie firmware i czy `C0` ma związek z `50`; efekty `53` na rejestry CAN, listen-only bez ACK, CAN29, zachowanie gdy brak odpowiedzi `C0`/ `51`, poprawność `54` i `6F`, oraz czy port COM1 z 115200 odpowiada odmiennemu wariantowi urządzenia.

**Testy:** aktualizacja **KCAN-D044** (C0, walidatory), **KCAN-D045** (mapowanie baud→PORT), nowy **KCAN-D046** (COM10+ i granice 16-slotowej tablicy). Walidację sprzętową przeprowadzić wyłącznie na izolowanym stanowisku, nie w samochodzie. W repo tylko niniejszy raport, bez bajtów programu w całości.

## 6. Skutek braku Tester.ini w bieżącym katalogu

Kod obu aplikacji pobiera katalog wywołaniem **`GetCurrentDirectoryA`**, dołącza dosłowne `\\TESTER.INI`, po czym `GetPrivateProfileIntA("COM","PORT",0,path)` pobiera numer COM. Jest to **current working directory**, nie jawnie ustalony katalog zawierający EXE.

**Implikacja bez uruchamiania:** jeśli w katalogu roboczym nie ma poprawnego `TESTER.INI` albo brak pola `[COM] PORT`, Windows API zwróci domyślne **0**. Program 4.5 następnie spróbuje skonstruować **`COM0`** przy baud **115200**, 3.0 beta **`COM0`** przy baud **833333**. Nie wiadomo, czy istnieją dodatkowe globalne mechanizmy korekty przy innych ścieżkach aplikacji, ale zrekonstruowana inicjalizacja używa tej wartości bezpośrednio. Do porównywania stanów błędu koniecznie zapisać katalog roboczy uruchomienia i widoczny plik INI. **Nie jest to dowód fizycznej prędkości UART.**
