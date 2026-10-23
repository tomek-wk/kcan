# Pogłębiona analiza VAG-CAN Commander 5.0+ECU (ZIP V5.1): ReadMemory i VAG TP2.0 — 2026-10-23

**Materiał:** wcześniej dostarczony `VAG-CAN Commander V5.1.zip` (SHA-256 `151913526f55e2528ccf153a0d47b69d67d53dde96ed8057af9efe083aeea94f`). Przed ponowną analizą zweryfikowano integralność ZIP (`testzip()` bez błędów) oraz pliku `VAG-CAN Commander+EDC15.exe`, SHA-256 `811bf59355614e0d07aa2e4c10fedd01fbff2b0148feab4491f0f731c98d45ba`. Badanie **statyczne**, tylko podgląd danych i kodu x86; żadnych uruchomień EXE, DLL, sterowników, połączeń z pojazdem ani adapterem.

**To istotne rozszerzenie** wcześniejszego [ANALYSIS_VAGCAN_50ECU_V51_2026-10-23.md](ANALYSIS_VAGCAN_50ECU_V51_2026-10-23.md). Dodatkowo zestawiono kod z niezależnym opisem [VAG TP2.0](https://jazdw.net/tp20) oraz [ACTIA — TP1.6/TP2.0](https://www.ime-actia.de/en/vehicle-diagnostics/tp1-6-2-0/). Dokumentację Microsoft [MFC CFile](https://learn.microsoft.com/en-us/cpp/mfc/reference/cfile-class) wykorzystano tylko do interpretacji API MFC; wynik oparto również na **bezpośredniej inspekcji jego wykonawczej implementacji w tym samym EXE**.

## 1. Rozstrzygnięcie D052: `memory.bin` to docelowa nazwa **eksportu pamięci**

W poprzednim raporcie ustalono tylko wystąpienie nazwy przy VA `0x4135E0`; nie było wiadomo, czy plik jest wczytywany czy zapisywany. Teraz prześledzono w pełni konstrukcję i vtable obiektu `CFile`:

- `0x40953D`: konstruktor obiektu pliku `0x449A36`, vtable **`0x459654`** w `[app_object+0xD0A90]`.
- Vtable `0x459654 + 0x20` = **`0x449B48`**, realizuje `CFile::Open`. W `0x4135E0–0x413615` aplikacja przekazuje literalny string **`memory.bin`**, **`0x1001` = `CFile::modeCreate | CFile::modeWrite`**, i wywołuje tę funkcję. W implementacji `0x449B48` `0x1000` powoduje utworzenie/wyzerowanie istniejącego pliku. **Nie jest to otwarcie pliku do odczytu.**
- Vtable `+0x38` = **`0x449C9F`**, wewnątrz potwierdzone wywołanie Win32 `WriteFile`. Aplikacja wywołuje je w `0x413A13` i `0x413A86`, za każdym razem z argumentem **długości 1** (kolejne bajty z odbieranej wiadomości/obsługi pamięci).
- Vtable `+0x4C` = **`0x449D63`**, wywołuje `CloseHandle`. W `0x413DC4` jest zamknięcie tego samego obiektu; następnie `0x413DD0` odwołuje się do tekstu **`ReadMemory - Done.`**.
- W tym konkretnym wywołaniu `memory.bin` jest zatem **nazwą pliku wyjściowego procedury odczytu pamięci ECU/instrument cluster**, a nie obrazem firmware adaptera. Nie oznacza to, że dołączony do ZIP plik był *na pewno* utworzony przez tę kopię programu ani że w całym programie nie ma innych sposobów otwierania zewnętrznych plików.

**Ryzyko:** `CFile::modeCreate` bez `modeNoTruncate` oznacza, że istniejący `memory.bin` może zostać **nadpisany/wyzerowany** przez kolejny eksport. Nie uruchamiać otrzymanego EXE; w niezależnym kliencie robić zapis atomowy z potwierdzeniem celu i bez nadpisania archiwalnej próbki.

### Dane w pliku dostarczonym z ZIP

Dostarczony `memory.bin`: **2048 bajtów**, SHA-256 `739e3bf5eca392955fa70e7aeea725dad3c39e6d3d69d13b1d65c183596d6ea4`. Statystyka offline (bez kopiowania/wyświetlania danych): entropia **~5,77 bitu/bajt**, **356** bajtów `00` i **410** bajtów `FF`, **210** różnych wartości; nie jest ciągiem samych zer ani samych `FF`. Sama długość czy entropia **nie rozpoznaje** ECU, EEPROM, identyfikatorów lub firmware. Pełna zawartość może ujawniać dane konkretnego pojazdu; nie publikować.

## 2. Nowe: trzy **predefiniowane zakresy** operacji ReadMemory, plus wariant użytkownika

Funkcja **`0x414F40`** ustawia parametry rozmiaru i początku odczytu na podstawie globalnego selektora `[0xDCDCA0]`; źródło tego selektora jest w widocznej ścieżce GUI `0x41F3C6–0x41F43F`. Stany 0, 1, 2 i **`0xFF` (parametry użytkownika)**:

| Selektor | Limit z `[+0xD0AA4]` | Wielkość porcji z `[+0xD0AA8]` | Początek `[+0xD0AAC]` (zależny też od `[0xDCDCA1]`) |
| --- | ---: | ---: | --- |
| `0` | **`0x80000`** (512 KiB) | **`0x40`** (64 B) | `0x00000` lub `0x80000` |
| `1` | **`0x4000`** (16 KiB) | **`0x40`** (64 B) | `0xC00000` lub `0x40000` |
| `2` | **`0x1000`** (4 KiB) | **`0x10`** (16 B) | `0x80000` lub `0x70000` |
| `0xFF` | **pola formularza GUI** | **pola formularza GUI** | **pola formularza GUI** |

Własne dane kodowe: `0x414F40..0x41505A` i formularz `0x41F3FB..0x41F43F`. Pola w obiekcie odpowiadają kolejno m.in. licznikowi przetworzonych bajtów `[+0xD0A80]`, zadanej długości `[+0xD0AA4]`, wielkości porcji `[+0xD0AA8]` i bieżącemu adresowi `[+0xD0AAC]`. Potwierdzeniem rozdzielenia liczników jest `0x413C30` (zwiększenie adresu i licznika), `0x413D38` (warunek stopu) oraz format tekstowy **`0x%06X`** do raportowania postępu.

**Ostrożność interpretacji:** powyższe wartości są parametrami z *kodu hosta*; bez sesji ECU nie dowodzą długości faktycznie odczytanego dumpu ani typu kości pamięci. Dołączony przykładowy **2048-bajtowy** `memory.bin` ma inną długość niż trzy limity predefiniowane, więc **nie wolno** automatycznie uznać go za kompletny odczyt jednego z tych wariantów (może być skrócony, pochodzić z trybu własnego lub innego źródła).

## 3. Nowa odnaleziona warstwa: rzeczywista segmentacja VAG **TP2.0** ponad CAN11

Funkcja **`0x420360..0x4204E9`** jest wyraźną implementacją transportu wieloramkowego, odrębną od prywatnego protokołu PC↔PIC:

1. Otrzymuje **bufor danych i jego długość**, oblicza `ceil(length/7)` (stała `0x24924925` i dzielenie przez 7 w `0x42039A–0x4203D5`).
2. Dzieli bajty na fragmenty **maksymalnie 7 B** w `0x420403–0x420440`; CAN DLC ustawia jako **1 + liczba danych**.
3. Pierwszy bajt ramki to `(sequence & 0x0F) | flags`, sekwencja wzrasta **modulo 16** (`0x420438–0x42045B`).
4. Kodek rozróżnia flagi **`0x10`** dla ostatniej porcji oraz **`0x20`** dla pośredniej bez oczekiwania na ACK. Jeżeli osiągnięto granicę bloku (modulo negocjowanego parametru `[+0x0C]`), pośredni segment ma **górny nibble `0x0`** i wymaga synchronizacji.
5. Pakiet trafia do funkcji **`0x4207D0`**, a ona wywołuje znane **`0x403520`**: TX CAN11. **Na UART** nadal idzie `0x60`; bajty TP2.0 leżą w **payloadzie CAN**, a nie w polu opkodu PIC.
6. Po segmentach wymagających potwierdzenia funkcja woła procedurę stanu/oczekiwania `0x420310`; rolę ACK po stronie RX dokumentuje `0x420580..`, zawierająca kontrolę **`D0`**, **`B0`**, `A8` i kod odpowiedzi `B0 | sequence`. Występują też szablony `A0`, `A1`, `A3` charakterystyczne dla połączeń transportowych.

**Weryfikacja zewnętrzna:** te nibble/segmenty odpowiadają [VW Transport Protocol 2.0](https://jazdw.net/tp20), [opisowi I CAN Hack](https://icanhack.nl/knowledge-base/diagnostics/vw-tp20/) i [ACTIA](https://www.ime-actia.de/en/vehicle-diagnostics/tp1-6-2-0/). Dokumentacja potwierdza interpretację górnych nibbli 0/1/2, 7-bajtowe segmenty, negocjowany block size i ACK `B0`. Sam interfejs CAN nadal używa **11-bit ID**. **Wniosek: statycznie potwierdzona implementacja fragmentacji TP2.0 w tym EXE.**

**Ważna granica:** w odbiorniku `0x420580` istnieje fragment budujący odpowiedź `A1`, ale w wyświetlonej wersji x86 warunek w `0x4205A2–0x4205AA` maskuje ID przez `0xFF` i porównuje do `0x300`, co wygląda na **nieosiągalną gałąź**. Dlatego mimo obecności kodu nie twierdzimy, że konkretny warunek rzeczywiście prowadzi do `A1` podczas działania bez analizy wszystkich obejść i przejść. **Nie utożsamiać przyjęcia/osiągalności całej procedury handshake z potwierdzonym połączeniem fizycznym**; konieczny zrzut CAN i test stanu.

**Bardzo ważne trzy odrębne znaczenia:**
- `C0 00` jako polecenie **host→PIC UART** przy inicjalizacji (wcześniej potwierdzone, znaczenie nieznane),
- `C0 ...` jako **payload ramki CAN** używany w VAG TP2.0 do otwarcia kanału,
- `0x60` jako **hostowy opcode UART**, który opakowuje już przygotowaną ramkę CAN (a nie transport ISO-TP lub samo TP2.0).

Łączy je wyłącznie to, że dotyczą komunikacji. **Nie są tym samym protokołem.**

## 4. Nowy problem niezawodności: potencjalna aktywna pętla i brak limitu synchronizacji TP2.0

Funkcja `0x420360` ma dwie pętle:

- `0x420371–0x42038A`,
- `0x420498–0x4204B3`.

W obu sprawdza globalne flagi `[0x17CDD6C]` i `[0x17CDD6D]`, powracając do odczytu **bez lokalnego Sleep, skutecznego timeoutu ani własnego licznika prób**. Jeśli odpowiedni stan nie zmieni się (np. brak ACK / zatrzymana obsługa zdarzenia), badany kod **może aktywnie zajmować CPU i nigdy nie wyjść z oczekiwania**. Wniosku nie należy automatycznie przenosić na faktyczny przebieg każdej sesji; flagi mogą być zmieniane asynchronicznie.

Dodatkowo w `0x420462–0x42046F` parametr **block size** jest używany w instrukcji `idiv ebx` bez widocznego w tej funkcji sprawdzenia, czy `[+0x0C]` jest różny od zera. **Zero oznaczałoby błąd dzielenia** przy osiągnięciu określonej gałęzi segmentacji. Może istnieć walidacja przy negocjacji kanału, ale nie udowodniono jej; nie testować uszkodzonych parametrów przez niezweryfikowany EXE.

**Wniosek do własnego klienta:** konieczne są: timeout transportowy ACK, limit liczby fragmentów, poprawne przetwarzanie block size `>0`, możliwość przerwania sesji i rozdzielenie stanu `UART` / `CAN TP2.0` / `KWP2000`.

## 5. Wnioski / rejestr testów

- **KCAN-D052 (istniejące): częściowo ROZSTRZYGNIĘTE** — funkcja `memory.bin` to **eksport**, nie rozpoznany wsad PIC, potwierdzony `CFile::Open(modeCreate|modeWrite)` → `Write(1)` → `Close()` oraz komunikatem `ReadMemory - Done.`. Otwarte pozostaje **pochodzenie 2048B próbki**, typ/źródło pamięci i zgodność jej zawartości z konkretnym ECU. Własny klient nie powinien przypadkowo nadpisywać istniejącego dumpu.
- **KCAN-D053 (NOWE): segmentacja TP2.0 i wiarygodność transportu** — forma ramek, ACK, negocjacja block size, wielkości i flagi potwierdzone w kodzie hosta; testować offline parser/framer, a potem wyłącznie na izolowanej magistrali. Nie tworzyć nowych opkodów PC↔PIC; specyfikację TP2.0 zachować jako **osobną warstwę**.
- **KCAN-D054 (NOWE): odporność na stany oczekiwania TP2.0** — dwie pętle bez timeoutu/odstępów i brak lokalnej walidacji `blockSize!=0`. Własny kod musi posiadać timeouty, anulowanie i walidację wejścia.
- **KCAN-D047/CAN29**: bez zmiany — wszystkie odnalezione ramki TP2.0 przechodzą przez **znane `0x403520` CAN11**, a nie poprzez alternatywny format CAN29. **D048/D049** o błędach Win32 TX pozostają aktualne.

Nie opublikowano całego pliku `memory.bin`, danych konkretnego ECU, sterowników, EXE ani surowych logów. Całą analizę przeprowadzono offline.

## Suplement audytu: TP2.0 dziedziczony z 3.0 beta i 4.5 (2026-10-23)

**Nowa weryfikacja:** segmentacja TP2.0, wcześniej szczegółowo opisana na przykładzie `0x420360` (5.0+ECU), **nie jest specyficzna dla tego EXE**. Ta sama konstrukcja występuje w **3.0 beta `0x4166E0`** oraz **4.5 `0x417FB0`** (RX odpowiednio `0x416900` i `0x4181D0`), z bardzo podobnym kodem x86 i wspólnym błędem `AND EAX,0xFF`/ `CMP AX,0x300` przed gałęzią A1/A3. To sugeruje **odziedziczoną implementację**, nie trzy niezależne projekty. Część inicjalizacji D0 istnieje niezależnie, a gałąź A1/A3 w tym miejscu jest matematycznie nieosiągalna.

**Kolejne ryzyko (D055):** handler odbioru TP2.0 w 5.0+ECU `0x4206BD–0x4206CE` robi `DLC-1` przed masowym kopiowaniem, bez wcześniejszej ochrony `DLC>=1` w ogólnej gałęzi; dla pustej ramki dopuszczonej przez `0x70` licznik może zawinąć. Ten sam kod jest w 3.0 beta/4.5. Dopasowanie ACK `&0xB0 ==0xB0` jest szersze niż poprawne sprawdzenie górnego nibble. Patrz [pełny audyt wszystkich ośmiu archiwów z wyłączeniem chronionego kodu](AUDIT_READABLE_FILES_2026-10-23.md) i D053–D056.
