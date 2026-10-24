# HUD ECU Hacker 6.1 — transport UART: zdarzenia, timeouty, odczyt pojedynczego bajtu

**Data:** 2026-10-24. Kontynuacja [parsera RID3650](ANALYSIS_HUD_61_RX_STATE_MACHINE_2026-10-24.md), [dekodowania statusu 0x54](ANALYSIS_HUD_61_STATUS_0x54_2026-10-24.md) i [protokółu](ANALYSIS_HUD_ECU_HACKER_61_PROTOCOL_2026-10-24.md). Cel: **rzeczywista komunikacja HUD ECU Hacker 6.1 ↔ VAG K+CAN Commander**. Materiał dowodowy: dostarczony ZIP użytkownika → statycznie wydobyty `ECU_Hacker.exe`, 6 449 152 B, **SHA256 `b70fa891953927da0600eac420d18acdc15a39bdba25dad366e1c52a602eeeb8`**.

## Metodologia i granice

Prześledzono metadane .NET **MethodImpl/TypeDef/MethodDef/MemberRef**, oryginalne instrukcje IL oraz wybrane ścieżki w **kontrolowanym interpreterze IL** z atrapami `WaitHandle`, listy bajtów, zegara i fizycznego odczytu. **Nie wykonano programu EXE, nie podłączono sprzętu, nie użyto CAN.** Symulacja weryfikuje przepływ sterowania i format danych, **nie** mierzy prawdziwych opóźnień, reakcji FTDI lub prędkości/niezawodności wątku Windows.

Istotna korekta w trakcie analizy: pierwszy model `RID1504` zwracał sztuczne 4 ms i powodował nierealistyczną pętlę przy braku danych. Sprawdzono faktyczny **RID1504** i zmieniono atrapę na `max(0,deadline - elapsed_ms)`. Dopiero po tej korekcie testy timeoutu są wiarygodnym odwzorowaniem wybranej ścieżki IL.

## 1. Łańcuch wykonania: parser Commandera aż do `SerialPort.Read`

| Poziom | Dowód w IL / metadanych | Rola |
|---|---|---|
| **TypeDef328 RID3650** (RVA `0x2CAE80`) | `callvirt RID2694` (m.in. offsety IL `0x02BD` / `0x034F`, według wcześniejszej analizy) | Zleca transportowi odbiór dwubajtowego nagłówka i reszty wiadomości. |
| **TypeDef183 RID2694** (RVA `0x2B08DC`, 474 B IL) | `0x0000..0x0008`: `ldarg.0, ldarg.2, ldarg.1, ldarg.3, ldarg.s 4, ldarg.s 5, call RID2695` | Wrapper transportu, dodatkowo ocenia niepowodzenie i status portu. |
| **TypeDef183 RID2695** (RVA `0x2B0AC4`, **1471 B IL**) | `IL 0x0149..0x0150` wylicza pozostały limit; `0x01DA..0x01E6` wywołuje `WaitHandle.WaitOne` przez RID2715; `0x03BD..0x03C5` wywołuje wirtualny `RID2687` dla jednego bajtu; `0x0435..0x043D` dodaje otrzymany bajt do `List<byte>`. | Koordynacja wątku, gromadzenie danych do żądanej długości, kontrola deadline i statusu. |
| **TypeDef522 RID7420** (RVA `0x39F8B4`, 354 B IL) | W **MethodImpl** jawny override `RID7420 → deklaracja RID2687` (tabela `MethodImpl`: `Class=522, MethodBody=14840, MethodDeclaration=5374`, indeksy tagowane ×2). `IL 0x0065..0x0075`: tworzy `byte[1]`, wykonuje `SerialPort.Read(array, 0, 1)` przez RID7461. | Konkretna implementacja abstrakcyjnego odczytu bajtu dla **Windows COM / SerialPort**. |
| **TypeDef522 RID7461** (RVA `0x39FE3C`, 10 B IL) | `IL 0x0000..0x0009`: `ldarg.0, ldarg.1, ldarg.2, ldarg.3, callvirt MemberRef2589 = System.IO.Ports.SerialPort.Read`. | Bezpośrednie wywołanie .NET `SerialPort.Read(byte[],int,int)`. |

**Wniosek:** implementacja HUD 6.1 pobiera bajty UART w podstawowej ścieżce **po jednym bajcie** (`Read(...,0,1)`), a z tych bajtów warstwa wyżej składa `opcode,length,payload`. To nie znaczy, że każde fizyczne przesłanie USB obejmuje tylko jeden bajt — sterownik FTDI i OS mogą buforować strumień w większych blokach.

## 2. DataReceived i EventWaitHandle

W **RID7412 (TypeDef522)** podczas inicjalizacji portu:
- `IL 0x01F0`: `ldftn RID7416`, `IL 0x01FB` → `RID7448`, który wywołuje `MemberRef2581 System.IO.Ports.SerialPort.add_DataReceived`. Zatem **RID7416 jest callbackiem DataReceived**.
- W **RID7416**, `IL 0x0080..0x008B`: pobiera pole **`0x0400061A`** i wywołuje **RID7455**, który woła `MemberRef1319 System.Threading.EventWaitHandle.Set`. Oznacza to, że przy zdarzeniu odbioru **sygnalizowany jest EventWaitHandle** używany przez `RID2695`.
- `IL 0x0216` `ldftn RID7417`, `IL 0x0221` `RID7449 → SerialPort.add_PinChanged`: osobny handler zmian linii sygnałowych. Nie wykazano bezpośrednio, że ten callback jest używany w normalnej ścieżce UART Commandera; może obsługiwać utratę połączenia/stany modemu.

**Schemat:** `FTDI/SerialPort → DataReceived callback(RID7416) → EventWaitHandle.Set → RID2695.WaitOne → virtual RID2687/override RID7420 → Read(byte[1],0,1) → List<byte> → RID3650`.

## 3. Weryfikacja timeoutów

Dwa odrębne mechanizmy:

### A. Deadline / budżet czasu wywołania

**RID1504** (TypeDef81, RVA `0x28732C`) zawiera ścieżkę:
- `Field0x040003B4` — liczba ms budżetu (typ int32);
- `Field0x040003B3` — `System.Diagnostics.Stopwatch`;
- `RID1508` (offset `0x007A..0x0088`) odczytuje `Stopwatch.ElapsedMilliseconds`;
- `remaining = budget - elapsed_ms`, potem `Math.Max(0, remaining)` przez `RID1510` (standardowa gałąź dodatniego limitu);
- `RID2695` wywołuje tę metodę z argumentem flag `4`, a wynik podaje jako czas do **RID2715 → WaitHandle.WaitOne(remaining)`**. Opcje specjalne dla deadline równego zero/trybów oznaczonych flagami nie zostały przeanalizowane w całości.

W symulacji standardowej ścieżki pozytywnego limitu przy `budget=100 ms`, braku danych i `WaitOne` zwracającym timeout: pierwszy odczyt nie otrzymuje sygnału, kolejne `RID1504` oddaje zero, a **RID2695 zwraca bool false**. Jest to **test z atrapą upływu czasu**, nie rzeczywisty pomiar.

### B. Timeout w API SerialPort

W **TypeDef522 RID7412** są jawne instrukcje:
- `IL 0x0238..0x0243`: `ldc.i4 2000; call RID7445` → `SerialPort.set_WriteTimeout` (MemberRef2578).
- `IL 0x0248..0x0253`: `ldc.i4 2000; call RID7446` → `SerialPort.set_ReadTimeout` (MemberRef2579).

To **2000 ms dla obu kierunków Windows COM**, niezależne od deadline komendy w RID1504 i interwału `0x54` (HUD co ~2000 ms w RID3652). Nie mylić tych wartości.

**Możliwe ryzyko w sytuacji wyścigu:** sygnał `DataReceived` lub zdarzenie może obudzić RID2695, który następnie wejdzie w blokujący `SerialPort.Read(byte[1],0,1)`, a tam istnieje osobny timeout **2000 ms**. Wtedy zadany przez wyższą warstwę limit np. 100 ms **nie musi stanowić bezwarunkowej granicy czasu rzeczywistego**. Jest to uzasadniony model ryzyka, **nie potwierdzony pomiarem**.

## 4. Wyniki wykonania symulacji RID2695

Odtworzono złożony `switch` obfuskowany `mul/xor/rem.un 39` (wciąż oparty na atrapach wymienionych wyżej).

| Scenariusz | Wynik symulacji |
| --- | --- |
| input `11 22 33`, target=3, budget=100ms, ready event | `return true`, lista `[0x11,0x22,0x33]`; wykonane trzy `RID2687` i trzy `List.Add` |
| input `33`, lista wstępna `[0x11,0x22]`, target=3 | `return true`, lista ma 3 bajty; wykazano **doklejanie danych**, a nie wymazanie bufora |
| input pusty, target=3, budget=100ms, event bez sygnału | `WaitOne(100)` symulowane jako timeout; `RID1504` zwraca potem 0; `RID2695` **return false** |
| budget=0, input pusty, brak sygnału | model standardowej gałęzi od razu zwraca `false`, bez wywołania `Read`; **przy budżecie zero oryginalna metoda RID1504 ma dodatkowe semantyki opcji, więc tego przypadku nie uogólniać** |
| `arg3 & 1` przy poprawnych bajtach | wykonywane dodatkowe `callvirt RID3443` po pierwszym bajcie; dane nadal gromadzone. **Nie ustalono sensu flagi**, nie nazywać jej kontrolą poprawności lub resynchronizacją bez dalszego dowodu. |
| „zdarzenie gotowe”, ale stub nie ma bajtu | emulator trafia w atrapę `ReadByte` na pustym strumieniu. **Nie stanowi to wyniku działania HUD**: rzeczywiste `SerialPort.Read` może blokować do 2000 ms albo rzucić wyjątek. |

Ważne **ograniczenie**: interpreter ma w niektórych miejscach uproszczone stuby metod portu i wywołań typu `RID3443`, `RID1517`, dlatego nie wolno ekstrapolować wyników na wszystkie flagi, wszystkie stany portu ani fizyczne opóźnienia.

## 5. Konsekwencje dla implementacji sniffera kcan

1. **Jeden czytnik COM** i niezależne kolejki `CAN RX 0x70` oraz odpowiedzi na komendy. Tak wynika z wcześniejszych [RID3650/3652](ANALYSIS_HUD_61_RX_STATE_MACHINE_2026-10-24.md) i obecnego dolnego transportu.
2. **Nie kopiować bezrefleksyjnie schematu `SerialPort.Read(...,1)`**: każdorazowy odczyt 1 bajtu ma narzut wywołania .NET; większe odczyty/odpowiedni bufor pierścieniowy mogą poprawić wydajność, ale różnicy **nie zmierzono** i trzeba zbenchować obydwa warianty na adapterze.
3. **Timeout całkowity** zależy od budgetu komendy i timeoutu faktycznej operacji COM. Implementacja powinna mieć jeden monotoniczny deadline dla żądania, wykrywać pozostały budżet i mieć świadomą strategię na rozłączony port.
4. **Nie mylić timeoutów:** `SerialPort.ReadTimeout 2000`, `WriteTimeout 2000`, komendy `0x54` ~100 ms, `0x53` ~150 ms, `0x60` nie oczekuje synchronicznej odpowiedzi w HUD, sondowanie `0x54` ~2000ms jako **interwał**, nie timeout.
5. **Walidacja błędów:** po błędzie framingu `0x70` nie udowodniono automatycznej resynchronizacji HUD. Nowy sniffer może wprowadzić jawne logowanie surowego strumienia, resynchronizację według ograniczonej listy opkodów i ochronę przed niekontrolowaną utratą bufora — ale nie przypisywać tej funkcji oryginalnemu programowi.
6. **Diagnostyka strat:** nadal odczytywać `54 02 S0 S1`, a nie opierać oceny kompletności wyłącznie na UI. `S1 & 0xC0` może sygnalizować overflow zależny od trybu ECAN; brak tej flagi nie dowodzi braku utraty danych później (USB/bufory hosta).

## 6. Nowe fakty w skrócie

- Potwierdzony **łańcuch MethodImpl** łączący abstrakcyjny `RID2687` z konkretnym `RID7420`.
- Potwierdzone **pojedyncze `SerialPort.Read(byte[],0,1)`** i rejestrowane po kolei bajty w `List<byte>`.
- Potwierdzony callback **`SerialPort.DataReceived`**, który sygnalizuje `EventWaitHandle`.
- Potwierdzony **deadline `RID1504` oparty o `Stopwatch.ElapsedMilliseconds`** oraz osobne timeouty **`SerialPort.ReadTimeout/WriteTimeout=2000ms`**.
- Rozdzielono fakty pochodzące z statycznego IL, wyniki interpretacji kodu z atrapami oraz hipotezy rzeczywistego wpływu na duży ruch CAN.

Nie zidentyfikowano nowych opkodów protokołu ani mechanizmu true listen-only, ale udało się znacznie dokładniej odtworzyć jego transport.
