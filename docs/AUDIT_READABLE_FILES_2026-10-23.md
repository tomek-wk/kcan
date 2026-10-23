# Audyt wszystkich dostępnych materiałów: wyłącznie czytelny kod i jawne dane (2026-10-23)

## Cel i rygor analizy

Na polecenie użytkownika przeprowadzono **kolejną weryfikację zawartości wszystkich ośmiu archiwów dostępnych w bieżącym środowisku**, **bez analizowania kodu programów zaszyfrowanych/spakowanych ochroną**, której nie udało się zdjąć. Użyto wyłącznie odczytu binarnego, dekompresji archiwum, SHA-256, nagłówków PE/NE oraz statycznej deasemblacji *jawnych* instrukcji x86. Nie uruchomiono EXE/DLL/SYS, nie instalowano sterowników, nie uruchamiano programów w Wine, nie wykonywano żadnych rozkazów do adaptera, nie pracowano na samochodzie. Żaden oryginalny program, RAR, ZIP, sterownik, `memory.bin` ani pełna tabela diagnostyczna nie trafia do GitHub.

**Ograniczenie „nie analizuj tych, których nie da się odszyfrować”:** rozpoznanie typu/rozmiaru/SHA i przyczyny pominięcia jest **inwentarzem**, nie próbą rekonstrukcji nieczytelnego kodu. Wersja 4.5 ma częściowo niestandardowe sekcje, ale **poniższe adresy odnoszą się wyłącznie do rzeczywiście jawnych instrukcji wykonywalnych**, nie do `.mackt` ani innych nieodtworzonych obszarów.

## 1. Pełna kontrola ośmiu archiwów

Każde archiwum zostało wczytane i dekompresowane statycznie; zweryfikowano rozmiar każdej pozycji RAR przez `libarchive`, a w ZIP sumę CRC przez `zipfile.testzip()` (wszystkie trzy ZIP: brak błędów). SHA-256 archiwów pozostały zgodne z poprzednimi raportami.

| Archiwum | SHA-256 | Plików | Werdykt dla tego audytu |
| --- | --- | ---: | --- |
| `VAG-CAN Commander V4.5.zip` | `e7980df7b33847af86ad12c52ae99c377b39c1d8f067abbe12e2d8c5de5e2b1c` | **32** | **ANALIZOWANO** czytelne `3.0 beta.exe` i czytelne fragmenty `4.5.exe` |
| `VAG-CAN Commander V5.1.zip` | `151913526f55e2528ccf153a0d47b69d67d53dde96ed8057af9efe083aeea94f` | **28** | **ANALIZOWANO** czytelne `VAG-CAN Commander+EDC15.exe`, `Tester.ini` i statystyki `memory.bin` |
| `VWool 2 0 9 en PL.rar` | `70b992d60f4b5cc014b30bca9fb6840ac213e883a7fd9378d92745e568a9079d` | **16** | Analizowano **jawne** NE/VB3, konfigurację COM i dekodowanie tabel; to nie Commander CAN |
| `VAG K+CAN COMMANDER 1.4zainstalowany.rar` | `8f76b5f4e1b420878e159b42f83367e7a4586c826cae3d5319715268409fdbd2` | **16** | **POMINIĘTO chroniony główny EXE** (SHA `ea69c09b...`), brak użytecznej odszyfrowanej ścieżki CAN |
| `VAG COMMANDER 3.6(2).rar` | `4c4e448077836806c593ef2f08a948ee56d0bde73f6f7dd8f56148b0097403a4` | **26** | **POMINIĘTO chroniony `VWTester.exe`**, sekcje `.vmp0/.vmp1` |
| `VAG K CAN COMMANDER FULL 3,6.rar` | `e0059df5cb1e51434ae1eea95d4f7ff7234a176360fb739d2b382dbace83069b` | **26** | **POMINIĘTO** ten sam chroniony `VWTester.exe` |
| `VAG-K CAN-V3.6.zip` | `9b59b9490c0011edea1976d9d4ad16a4671e1870b45576088f298ed23b5d8b32` | **26** | **POMINIĘTO** ten sam chroniony `VWTester.exe` |
| `Polski VAG 4.9(1).rar` | `3febfd5015830fb6626134f6e13fed107f09ff2d7544e36ad244e4102d0c8e7f` | **1** | **POMINIĘTO** kod aplikacji: dostępny tylko sam instalator Inno Setup, jego program docelowy nie został statycznie wypakowany |

Źródłowy `VWTester.exe FULL 2.5` jest szczegółowo **opisany w repo**, ale wśród obecnie fizycznie dostępnych archiwów **nie ma tej binarki**. Dotychczasowe ustalenia 2.5 potraktowano jako wcześniejszą dokumentację, a **nie nową niezależną inspekcję EXE**.

Trzy chronione pakiety „3.6” zawierają ten sam EXE SHA-256 `a448ff313cce8ee2597f14675e51196ca5b677a5561833bb65965b05628d8a23`; różnią się jedynie `Tester.ini` (wcześniejszy audyt). Nie prowadzono prób odpakowania VMProtect, emulowania ani zgadywania instrukcji.

### Wybrane potwierdzenia pozostałych jawnych plików

- `VWTOOL.EXE` i `VWTOOL-pl.EXE` są rzeczywistymi **Windows 16-bit NE**, z importami/komponentami VB3 i `MSComm`. Zwykłe dane tabel `ERRCODE4.CSV` i `LABELS.CSV` dają się w pełni zdekodować XOR `0x85` z zachowaniem CR/LF. Po dekodowaniu **100% bajtów jest drukowalne ASCII lub CR/LF**, odpowiednio 1257 i 569 wierszy. Są to dane DTC/grup pomiarowych i narzędzie COM/K-Line, **nie dowody kodowania CAN29**.
- Cztery pliki diagnostyczne `FixDiag.ini`, `MWB.TXT`, `MWB_de.TXT`, `VAG.txt` są powtarzanymi zasobami aplikacyjnymi; ich identyczność **nie dowodzi** tożsamości firmware.
- Pliki INF/DLL FTDI i `Tester.ini` wykorzystano do identyfikacji zależności oraz kontekstu COM, a nie jako dowód działania firmware.

## 2. Najważniejsze nowe odkrycie: **VAG TP2.0 jest w trzech czytelnych EXE**

Dotychczas raport [ANALYSIS_VAGCAN_50ECU_V51_MEMORY_TP20_2026-10-23.md](ANALYSIS_VAGCAN_50ECU_V51_MEMORY_TP20_2026-10-23.md) przypisywał szczegółową rekonstrukcję TP2.0 przede wszystkim programowi 5.0+ECU. **To nie jest nowa funkcja wyłącznie 5.0+ECU.**

| Otwarty EXE | SHA-256 | Segmentacja TP2.0 | Odbiór/ACK TP2.0 | Bezpośrednie CALL do segmentera w całej jawnej deasemblacji |
| --- | --- | --- | --- | ---: |
| `VAG-CAN Commander 3.0 beta.exe` | `dfb5e3f4724f6898c7c82d5d6e69ed3f795edb5f536f4aa5ff37ab17eae2a39b` | **`0x4166E0`** | **`0x416900`** | **70** |
| `VAG-CAN Commander4.5.exe` | `85e89882a434ad83d19381ecbb5f9e77b14b237343b1432feb2f7300810e0050` | **`0x417FB0`** | **`0x4181D0`** | **108** |
| `VAG-CAN Commander+EDC15.exe` z ZIP V5.1 | `811bf59355614e0d07aa2e4c10fedd01fbff2b0148feab4491f0f731c98d45ba` | **`0x420360`** | **`0x420580`** | **107** |

W każdej funkcji segmentera występują **te same charakterystyczne instrukcje**: mnożnik `0x24924925` przy obliczeniu `ceil(N/7)`, kopiowanie do **7 B** za nagłówkiem 1 B, `seq & 0x0F`, znaczniki `0x10/0x20`, `idiv` przez parametr wielkości bloku, wywołanie transmitera CAN11. Samo odnalezienie bezpośrednich wywołań `call` w deasemblacji nie poświadcza każdej możliwej ścieżki GUI, ale skala i umiejscowienie wywołań potwierdzają, że to kod istotny dla diagnostyki, nie przypadkowy ciąg bajtów.

**Korekta oceny dowodów:** te trzy programy wydają się wykorzystywać **wspólną linię kodową / dziedziczone implementacje** TP2.0. Są to **trzy czytelne egzemplarze kodu**, ale ich zgodność **nie stanowi trzech całkowicie niezależnych projektów protokołu**. Nie należy sztucznie mnożyć siły dowodu przez liczbę archiwów.

## 3. Nowa potwierdzona nieosiągalność gałęzi negocjacji TP2.0 w **wszystkich trzech**

We wszystkich trzech odbiornikach występuje dokładnie analogiczny warunek x86:

```asm
and eax, 0xFF
cmp ax, 0x0300
jne  alternate_path
```

| Wersja | `AND` | `CMP AX,0x300` | Skutek |
| --- | --- | --- | --- |
| 3.0 beta | `0x416924` | **`0x416926`** | Porównanie zawsze nierówne |
| 4.5 | `0x4181F4` | **`0x4181F6`** | Porównanie zawsze nierówne |
| 5.0+ECU | `0x4205A4` | **`0x4205A6`** | Porównanie zawsze nierówne |

Po `eax & 0xFF`, `AX` ma zakres **0..255**, więc nie może być równy **768**. Przez warunek `jne` kod zawsze pomija bezpośrednią gałąź obsługi **`A1` i `A3`** w tym miejscu.

**Czego NIE dowodzi:** że kompletny handshake TP2.0 nie działa. Dalej w funkcji istnieje **inna** osiągalna gałąź dla `D0`, rekonstruująca identyfikator CAN kanału z bajtów danych i porównująca go do `0x300` (np. 5.0+ECU `0x420626..0x420660`). Możliwe są również inne ścieżki inicjalizacji. Konsekwencje pominięcia A1/A3 trzeba modelować offline; nie próbować nieznanych ramek na pojeździe.

Odziedziczenie **takiej samej nieosiągalnej gałęzi** we wszystkich 3 binariach to kolejny silny ślad **wspólnego kodu**, a nie świadectwo trzech niezależnych implementacji.

## 4. Nowe potencjalnie poważne ryzyko: **CAN DLC=0 i niedomiar licznika kopiowania TP2.0**

Prawidłowy **Classical CAN** dopuszcza DLC=0, a dekodery PC↔PIC `0x70` akceptują `length=4` (czyli N=0). Następnie, jeśli ramka przejdzie do **ogólnej** gałęzi składania danych TP2.0, kod odbiornika robi:

```asm
mov cl, BYTE PTR [ebx+2] ; N, rzeczywisty DLC rekordu CAN
dec ecx                 ; N-1 (nagłówek TP2.0)
shr ecx, 2
rep movsd               ; kopiowanie do buf. składanego komunikatu
```

| Wersja | Odczyt N / `dec ecx` | Ogólny kopiujący segment |
| --- | --- | --- |
| 3.0 beta | `0x416A3D` / **`0x416A41`** | `0x416A4B: shr ecx,2`, `0x416A4E: rep movsd` |
| 4.5 | `0x41830D` / **`0x418311`** | `0x41831B: shr ecx,2`, `0x41831E: rep movsd` |
| 5.0+ECU | `0x4206BD` / **`0x4206C1`** | `0x4206CB: shr ecx,2`, `0x4206CE: rep movsd` |

**Dla N=0:** instrukcja `dec ecx` po wyzerowanym `ECX` daje `0xFFFFFFFF`; `shr ecx,2` daje **`0x3FFFFFFF` elementów po 4 bajty**, zanim wykona się jakikolwiek test wielkości docelowego bufora. To potencjalnie krytyczne nadmiarowe kopiowanie / zawieszenie lub błąd pamięci.

**Kontrola osiągalności:** w 5.0+ECU dekoder `0x70` wywołuje **`0x402EF4→0x420580`**. Poprzedzający filtr `0x4037B0` jest **`mov al,1; ret`**. Analogicznie 4.5 `0x402EF4→0x4181D0` przez `0x403770` (stałe 1) oraz 3.0 beta `0x402F24→0x416900` przez `0x403790` (stałe 1). Zewnętrzny walidator `0x70` pozwala na **length=4..12**, więc w tym łańcuchu nie ma ogólnego odrzucenia pustych ramek. Różne wczesne gałęzie samego TP2.0 mogą zatrzymać *niektóre* przypadki; nie twierdzić, że **każda** pusta ramka powoduje awarię. Brak prawidłowego warunku `N>=1` przed ogólnym kopiowaniem jest jednak udokumentowany.

**Bezpieczeństwo:** NIE wywoływać błędnej ścieżki w starym EXE z rzeczywistym adapterem ani pojazdem. Własny dekoder powinien:
- odrzucać `DLC=0` w **kontekście przetwarzania TP2.0** (choć ogólny sniffer CAN musi dopuszczać poprawne puste ramki),
- przed każdym `N-1` sprawdzać `N>=1`,
- kontrolować maksymalną długość całego bufora składanego komunikatu, poprawny numer sekwencji i zadany ID kanału.

## 5. Dodatkowa obserwacja: zbyt szerokie dopasowanie ACK i warianty parserów

W każdym z trzech odbiorników rozpoznanie niektórych odpowiedzi kontrolnych opiera się na:

```asm
and dl, 0xB0
cmp dl, 0xB0
```

Przykłady VA: 3.0 beta `0x416A21–0x416A27`, 4.5 `0x4182F1–0x4182F7`, 5.0+ECU `0x4206A1–0x4206A7`. Ta maska dopuszcza więcej wartości niż tylko `0xB0..0xBF`; np. **`0xF0` również spełnia warunek**, o ile spełniono wcześniejsze kryteria ID kanału i inne warunki. To powód, aby we własnym parserze stosować **`(control & 0xF0) == 0xB0`** i osobno sprawdzać dolny nibble numeru ACK.

**Uwaga o różnicy wersji RX:** 3.0 beta przy wyborze chwili odpowiedzi ACK testuje bity **0x20 i 0x10** w `0x416A77–0x416A81`; 4.5/5.0+ECU porównują **cały górny nibble** do 0 lub 0x10 (`0x418347–0x418351`, `0x4206F7–0x420701`). To **rzeczywista różnica** parserów przy niepoprawnych wartościach sterowania, nie nowy format CAN29. Nie należy wysyłać takich niepoprawnych ramek przez dostarczone programy.

## 6. Potwierdzenia bez zmiany i ograniczenia dowodowe

- Wszystkie trzy jawne nadajniki `0x60` / odbiorniki `0x70` nadal kodują tylko **CAN11**; TP2.0 jest *warstwą ponad CAN11*, nie ścieżką CAN29. Nie odkryto nowego opkodu 29-bit ani flagi IDE w tych ścieżkach.
- `memory.bin` w pakiecie V5.1 ma **2048 B**; poprzednia analiza dowiodła, że nazwa ta występuje jako **plik wyjściowy ReadMemory**. Nowy audyt nie pozwala przypisać dostarczonych 2048 B do konkretnego ECU ani firmware PIC.
- Jawne funkcje Win32 COM mają opisane wcześniej problemy z ukończeniem OVERLAPPED, pozornym statusem TX i granicami buforów (D048–D050); nowego zachowania adaptera nie badano.
- Nie próbowano zdejmować VMProtect/zabezpieczeń z programów 1.4/3.6 ani rozpakowywać docelowej aplikacji z instalatora Polski VAG 4.9. Nie sugerować zgodności protokołu na podstawie zawartości ich nieczytelnych EXE.

## 7. Wpływ na zadania i bezpieczną implementację

- **D053 (uzupełnienie):** TP2.0 i 7-bajtowa segmentacja potwierdzone kodem *we wszystkich trzech* czytelnych kompilacjach. Poprawka do poprzedniego opisu „nowe odkrycie w 5.0+ECU”: to dziedziczona funkcja.
- **D054 (uzupełnienie):** pętle busy-wait i brak lokalnej walidacji dzielnika `blockSize>0` znalezione również w 3.0 beta/4.5, a nie tylko w 5.0+ECU.
- **D055 (NOWE, P0):** błąd `DLC=0`/underflow w składaniu TP2.0, potencjalne nadmiarowe kopiowanie, niezależnie od tego, że 0 jest poprawne na samym CAN. Mock decoder offline, bez uruchamiania starych EXE.
- **D056 (NOWE, P1):** nieosiągalna gałąź A1/A3 po `AND 0xFF` i `CMP 0x300` w trzech wersjach, zbyt szerokie rozpoznanie `B0` przez maskę `0xB0`, różnice logiki generowania ACK. Zmapować poprawny handshake przy użyciu dokumentacji protokołu i własnych testów jednostkowych, nie losowych eksperymentów w samochodzie.

**Rekomendacja architektury własnego klienta:** ścisłe rozdzielenie (a) dekodera pakietów UART PIC `0x50..`, (b) ogólnego CAN11, który *akceptuje* DLC0, (c) TP2.0, który wymaga **co najmniej jednego bajtu kontrolnego**, (d) KWP2000. Każdy parser ma mieć walidację wejścia, sprawdzony limit bufora/fragmentów, limit czasu, anulowanie i jawny stan otrzymanego ACK.

**Raport jest nowym własnym opracowaniem; nie przechowuje żadnych obcych binariów, dumpów ECU, sterowników ani tabel w całości.**
