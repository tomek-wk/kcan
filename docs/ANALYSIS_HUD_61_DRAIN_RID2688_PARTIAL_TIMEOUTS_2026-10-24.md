# HUD ECU Hacker 6.1 — RID2688: odrzucanie bajtów po resecie i zachowanie częściowych pakietów UART

**Data:** 2026-10-24. Kontynuacja [DTR/RTS i błędów COM](ANALYSIS_HUD_61_RESET_DTR_RTS_SERIAL_ERRORS_2026-10-24.md), [transportu RID2695](ANALYSIS_HUD_61_UART_TRANSPORT_2026-10-24.md) oraz [maszyny stanów RID3650](ANALYSIS_HUD_61_RX_STATE_MACHINE_2026-10-24.md). Materiał: `HUD-ECU-Hacker v6.1(1).zip` przekazany przez użytkownika; analizowany `ECU_Hacker.exe` ma SHA256 **`b70fa891953927da0600eac420d18acdc15a39bdba25dad366e1c52a602eeeb8`**.

**Cel:** faktyczne zachowanie protokołu **PC↔VAG K+CAN Commander** podczas resetu, czyszczenia UART i timeoutów. Wyłącznie analiza statyczna + interpretacja wybranych metod IL z kontrolowanym buforem wejściowym. **Nie uruchamiano programu Windows ani nie podłączano interfejsu.**

## Metoda i poprawność parsera IL

Na nowo odczytano PE32/CLR, strumienie ECMA-335 `#~`, `#Strings`, `#Blob`; granica tabel metadanych pokrywa się **dokładnie** z początkiem `#Strings`. Pobrano rzeczywiste RVA i rozmiary metod: `RID2688` RVA `0x2AFE94`, **329 bajtów IL**; `RID2694` RVA `0x2B08DC`, **474 bajty IL**; `RID3646` RVA `0x2CA750`, **162 bajty IL**; `RID3650` RVA `0x2CAE80`, **1253 bajty IL**. Zbudowano wąski interpreter stosowej semantyki `ldarg,ldloc,br,switch,mul,xor,rem.un,callvirt` dla RID2688 i RID2694. Emulator pracuje na podstawionym wyniku `BytesToRead` oraz atrapie `ReadByte`, nie korzysta z realnego portu. Wersje wrażliwych fragmentów zbadano na oryginalnym EXE o podanym SHA.

## 1. Co **faktycznie** robi RID2688

Sygnatura metody `RID2688` (TypeDef183): **`bool Drain(bool logDrained)`** — nazwa `Drain` jest nadana do celów dokumentacji, oryginalna nazwa w metadanych jest obfuskowana.

Kluczowe offsety IL:

- `0x012F–0x013A`: `new List<byte>()`.
- `0x0100–0x0106`: `this.BytesToRead()` przez wirtualny `RID2674`. Dla Windows COM override `RID7409` zwraca `SerialPort.BytesToRead` przez `RID7436`.
- `0x0050–0x0059`: `this.ReadByte(14)` przez wirtualny `RID2687`, następnie `List<byte>.Add`. Windows COM override `RID7420` faktycznie używa `SerialPort.Read(byte[1],0,1)`; samo znaczenie argumentu `14` dla pozostałych implementacji transportu nie jest jeszcze ustalone.
- `0x0065–0x008B`: bada flagi `RID3420() & 1`, gdzie `RID3420` jest getterem `FieldDef 0x040007A9` (**Field1961**) z klasy ustawień `TypeDef311`. Gdy bit0 jest ustawiony, metoda może **zakończyć odczyt po jednym bajcie**; w zwykłej ścieżce, gdy bit0 nie jest ustawiony, pętla działa do `BytesToRead==0`.
- `0x008D–0x00AD`, `0x013F–0x0148`: jeśli lista ma niezerową liczbę bajtów, funkcja zwraca **true**; przy braku bajtów zwraca **false**.
- `0x00B2–0x00E7`: jeśli argument `logDrained=true` i lista niepusta, generuje komunikat diagnostyczny przez `RID2696(this,string,list)`. Przy `logDrained=false` dane są usuwane **bez tego logu**. `RID2696` przekazuje listę do logowania, ale **nie kolejkuje** jej w parserze CAN.
- `Field1558` (`0x04000616`) jest dodatkową statyczną flagą obfuskacji/inicjalizacji: `RID2698` ustawia ją na true; konstruktor transportu `RID2680` w ścieżce warunkowej resetuje na false; symulacja zwykłej ścieżki odczytu wybiera **false**. Wartość true w prologu `RID2688` wchodzi w inną (pozorną) drogę — nie interpretować jej jako zwykłego trybu adaptera.

**Najważniejsze:** `RID2688` **nie parsuje** `0x70`, **nie synchronizuje** wiadomości i **nie oddaje** odczytanych bajtów do kolejki CAN. To mechanizm **drain/discard**, który ewentualnie może logować utracony fragment.

## 2. Kontekst wywołań: po resecie milcząco, po błędzie diagnostycznie

Dokładne wywołania w **tej samej klasie Commandera TypeDef328**:

| Miejsce | IL | Wywołanie | Znaczenie |
| --- | --- | --- | --- |
| `RID3646` (reset DTR/RTS) | `0x0094–0x00A0` | `this.transport.RID2688(false)`, wynik ignorowany | Po **DTR=1 → 50ms → DTR=0 → RTS=arg** odrzuca dostępne bajty UART **bez diagnostycznego logu listy**. |
| `RID3650` (parser odpowiedzi) | `0x00B8–0x00C4` | `this.transport.RID2688(true)`, wynik ignorowany | W **jednej ze ścieżek błędu parsera** odrzuca dostępne bajty i żąda ich logowania; kompletne warunki wejścia do tej gałęzi wymagają interpretacji reszty CFG i nie należy uogólniać jej na każdy timeout. |

W pozostałym kodzie aplikacji są także wywołania `RID2688` z innych klas adapterów i warstwy wspólnej; nie przypisywać ich wszystkich protokołowi Commandera.

**Ważne:** samo wywołanie `Drain(false)` po resecie nie rozpoznaje granicy `[opcode,length,payload]`. Jeżeli przyczepione są dwa kompletne pakiety `0x70` i `0x54`, mogą zostać usunięte jedną pętlą. Jeżeli kolejny bajt poprzedniej wiadomości dotrze **po** zakończeniu czyszczenia, może być potraktowany przez następny odczyt jako nowy nagłówek.

## 3. Kontrolowane testy oryginalnego IL RID2688

Własny interpreter obsłużył dwa wyniki `RID2674` (symulowane `BytesToRead` na podstawie tablicy) i `RID2687` (symulowany odczyt 1 bajtu). Porównano z niezależnym Pythonowym modelem [`tools/hud_kcan_drain_model.py`](../tools/hud_kcan_drain_model.py): **768/768 zgodnych** przypadków: długości 0..63, `transport_flags` ∈ {0,1,2,3,4,9}, argument `log` ∈ {false,true}. Testy modelu można uruchomić bez Windows i bez adaptera: `python tools/hud_kcan_drain_model.py`.

| Dane zastane w COM | `Field1961 & 1` | `log` | Odczytane i odrzucone | Reszta w atrapie portu | Wynik |
| --- | --- | --- | --- | --- | --- |
| pusty | 0 | false | 0 B | 0 B | false |
| `70 04 24 0C 00 00 54 02 AA BB` | 0 | false | **10 B**, brak diagnostycznego wpisu o bajtach | 0 B | true |
| to samo | 0 | true | 10 B i wpis diagnostyczny listy | 0 B | true |
| to samo | **1** | false | **tylko pierwszy bajt `70`** | `04 24 0C 00 00 54 02 AA BB` | true |
| 25 sztucznych bajtów | 0 | true | wszystkie 25 B i log | 0 B | true |

**Ograniczenie:** w danym momencie nie udowodniono, jakie wartości flag `Field1961` są ustawiane dla konkretnej rewizji sprzętu użytkownika — **nie wolno bezwarunkowo przypisać jej wariantu all-drain ani single-byte**. Również `BytesToRead` może zmieniać się w trakcie działania; nasze wejście było deterministyczne.

## 4. RID2694: timeout czy wyjątek? Ważne rozróżnienie

`RID2694` jest wrapperem odczytu transportowego `RID2695`, z argumentem flag `arg3`. Na wejściu wywołuje `RID2695` i sprawdza jego bool (offset `0x0000–0x000D`).

Jeśli `RID2695` zwróci **false**, `RID2694` wykonuje:

- `IL 0x0144–0x0158`: sprawdzenie **`arg3 & 4`**;
- jeśli bit `0x04` ustawiony → **zwraca false bez rzucenia wyjątku** (ścieżka `IL 0x00EC–0x00ED` w emulacji);
- bez bitu `0x04` → sprawdza dodatkowe statusy sterownika `RID3430, RID3468, RID3476, RID3431`, może logować częściowo odebrane bajty i **rzuca wyjątek** reprezentujący problem komunikacji (w modelu przy neutralnych statusach dochodzi do `newobj RID1528; throw`). Dokładne semantyki statusów i typy poszczególnych wyjątków poza tym zakresem są jeszcze nieodtworzone.

Przetestowano w interpreterze warianty `RID2695 true/false`, pustego/częściowo zapełnionego bufora oraz `arg3=0,4,8,12`. Wyniki ze wszystkimi wyłączonymi statusami: sukces odczytu zawsze → true; porażka z bitem4 → false; porażka bez bitu4 → wyjątek. Wszystkie te testy są **symulacją funkcji hosta** i nie dowodzą realnego timeoutu FTDI.

**Nowe powiązanie z Commanderem:** `RID3650` wywołuje `RID2694` w **obu miejscach odbioru** z `arg3=4`:
- **header:** `IL 0x0343–0x0354` → `RID2694(..., flags=4, target=2, readOptions=14)`, potem sprawdza `List.Count`;
- **payload:** `IL 0x02B0–0x02C2` → `RID2694(..., flags=4, target=length+2, readOptions=14)`, potem sprawdza `List.Count >= required`.

W konsekwencji **zwykły brak kompletu bajtów** na tych ścieżkach jest widoczny jako niedomknięta lista, a nie bezwarunkowy `TimeoutException` z `RID2694`. Wyjątki z samego `SerialPort.Read`, odłączenie FTDI i inny nieprzechwycony błąd nadal mogą przechodzić wyżej, zgodnie z wcześniejszą analizą `RID7420`.

## 5. Ryzyko utraty początku ramki przy timeoutcie

`RID3650` tworzy **nową lokalną `List<byte>` na początku każdego wywołania** (`IL 0x0000–0x0005`). W obu odczytach sprawdza liczbę otrzymanych bajtów. Nie znaleziono w tym fragmencie **oddzielnego trwałego bufora niepełnej ramki** współdzielonego między kolejnymi wywołaniami parsera; istnieje natomiast kolejka gotowych ramek CAN i niższy bufor portu.

**Implikacja jako przypadek testowy, NIE pomiar:** jeśli prefiks `70 07 24` zostanie skonsumowany do lokalnej listy i zakończy się obsługa z błędem/timeoutem przed otrzymaniem reszty, później przybyłe `0C 00 00 11 22 33` może trafić jako nowy początek wiadomości. `RID2688` nie zna granic ramki i nie naprawia takiego stanu. **Nie twierdzimy**, że powyższy przypadek zaszedł w rzeczywistym HUD bez benchmarku; pełna ścieżka wyjątku/zwrotu z `RID3650` nadal wymaga weryfikacji dla wszystkich kombinacji statusów i budżetów.

Opróżnianie portu `RID2688` (przed następnym `0x53/0x54` lub po resecie) może świadomie utracić również **ważne ramki `0x70` już widoczne w COM**, nawet jeśli parser potrafiłby je poprawnie zdekodować. To nie jest dowód *utraty sprzętowej*: utrata następuje w programie hosta.

## 6. Zalecenia do dalszego testowania i własnego sniffera

1. **Rozdzielić dwa tryby opróżniania:** `drain-after-reset` (świadomie odrzucone bajty, zapisać surowe i licznik) oraz `stream-parse` (zachować wszystkie `0x70` nawet podczas odpowiedzi statusowych `0x54`). Nigdy nie traktować samego `BytesToRead==0` jako dowodu synchronizacji ramki.
2. **Pełny zapis surowego UART** z nanosekundowym/milisekundowym znacznikiem czasu lub monotonicznym odczytem, zdarzeniem resetu DTR, RTS oraz powodem czyszczenia. Oddzielnie liczyć `software_discarded_bytes` i `can_controller_rx_overflow` (z `54 02 S0 S1`, z ostrożnością co do trybu ECAN).
3. **Stanowy parser buforujący fragmenty** i świadoma polityka odzysku. Własny kod nie musi kopiować stratnej polityki HUD. Przy błędzie wyświetlić surowy prefiks i zachować go do diagnostyki. Projektować limit bufora oraz walidację `0x70 length 4..12`.
4. **Bezpieczny test bench:** odtworzyć sztucznie `70 07 24`, opóźnić resztę ponad timeout żądania, sprawdzić zachowanie programu/portu i czy pojawiają się niepoprawne opkody. Drugi test: dostarczyć `0x70` tuż przy impulsem DTR i porównać liczbę bajtów faktycznie odrzuconych z logiem. Bez fizycznej magistrali pojazdu i bez reflasha.
5. **Nie wnioskować o bezstratności** na podstawie samego poprawnego parsowania. Dla dużego CAN są trzy odrębne potencjalne przyczyny braków: kontroler PIC/COMSTAT, USB/FTDI, oraz świadome czyszczenie bufora przez hosta.

**Wynik:** `RID2688` to konkretna, zidentyfikowana funkcja **odrzucająca** bajty, a nie mechanizm resynchronizacji; `RID2694` na ścieżkach Commandera umożliwia odczyt częściowy bez natychmiastowego wyjątku. Kwestia utrzymania niepełnej ramki między wywołaniami pozostaje ryzykiem do przetestowania.
