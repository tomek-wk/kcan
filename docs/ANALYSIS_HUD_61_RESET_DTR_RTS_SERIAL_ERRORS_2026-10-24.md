# HUD ECU Hacker 6.1: reset i tryb DTR/RTS, wyjątki portu, zdarzenia modemowe

**Data:** 2026-10-24. Kontynuacja [analizy transportu UART](ANALYSIS_HUD_61_UART_TRANSPORT_2026-10-24.md) i [protokołu VAG K+CAN](ANALYSIS_HUD_ECU_HACKER_61_PROTOCOL_2026-10-24.md). Materiał użytkownika: `HUD-ECU-Hacker v6.1(1).zip` → statycznie wydobyty `ECU_Hacker.exe`, SHA256 `b70fa891953927da0600eac420d18acdc15a39bdba25dad366e1c52a602eeeb8`.

**Przedmiot:** **protokół PC ↔ VAG K+CAN Commander**. **Nie wykonywano HUD, nie resetowano adaptera ani nie podłączano magistrali CAN.** Odczyt instrukcji i tablic wyjątków ECMA-335 oraz emulacja wąskiego wycinka IL z atrapami metod portu.

## 1. NOWOŚĆ: rzeczywista sekwencja resetu Commandera (TypeDef328 / RID3646)

Odtworzono obfuskowany `MethodDef RID3646`, RVA **`0x2CA750`**, IL **162 bajty**: stanowy `switch` oparty o `mul/xor/rem.un`, sprawdzony w interpreterze IL dla argumentów `arg1=0` i `arg1=1`. Wynik obu prób jest identyczny poza poziomem RTS:

| Kolejność wykonywania | Offset IL | Wywołanie | Faktyczny skutek na poziomie Windows API |
| ---: | --- | --- | --- |
| 1 | `0x0074` | `RID2669(this.transport, true)` | **DTR=1** (`RID2669` → override TypeDef522 **RID7402** → **RID7432** → `SerialPort.set_DtrEnable`) |
| 2 | `0x0059` | `RID1773(ui,50)` | **`Thread.Sleep(50)`**, ponieważ `RID1773 → RID1852 → System.Threading.Thread.Sleep` |
| 3 | `0x003D` | `RID2669(this.transport,false)` | **DTR=0** |
| 4 | `0x008F` | `RID2671(this.transport,arg1)` | **RTS=arg1** (`RID2671` → override TypeDef522 **RID7404** → **RID7434** → `SerialPort.set_RtsEnable`) |
| 5 | `0x009B` | `RID2688(this.transport,0)` | Dodatkowe czytanie/porządkowanie danych portu; nie nazywać go bezwarunkowo `DiscardInBuffer`: RID2688 posługuje się metodami `BytesToRead` i `ReadByte`. Pełna analiza tej ścieżki wraz z wszystkimi flagami jest otwarta. |

Symulacja zapisanych zdarzeń:

```text
RID3646(arg1=0) → DTR 1 → Sleep 50 ms → DTR 0 → RTS 0 → RID2688(0)
RID3646(arg1=1) → DTR 1 → Sleep 50 ms → DTR 0 → RTS 1 → RID2688(0)
```

**Śledzenie wywołań:**
- Inicjalizacja Commandera `RID3643`, IL `0x0073–0x0076` wywołuje **`RID3646(arg1=1,...)`**, czyli koniec resetu z **RTS=1**.
- Oddzielna metoda `RID3645`, IL `0x0024–0x0028` wywołuje **`RID3646(arg1=0,...)`**, kończąc z **RTS=0**.
- W RID3646 odszyfrowany z `MethodSpec 4`, key `0x7777AFFC`, oryginalny napis: **`Error resetting adapter`**.
- Należy oddzielić **poziomy bool w API FTDI/SerialPort** od **elektrycznej interpretacji** na konkretnym PCB; sprzętowe odwzorowanie DTR→RESET PIC, RTS→CAN/K-line jest zależne od wariantu płytki, a 50 ms z `Thread.Sleep` nie stanowi pomiaru dokładnego impulsu na pinie.
- RID2688 zawiera `RID2674` → override TypeDef522 `RID7409` → `RID7436` → `SerialPort.get_BytesToRead`, oraz w kodzie `RID2687` (fizyczny odczyt bajtu); dlatego może opróżniać napływające po resecie bajty. **Nie ustalono jeszcze, czy zawsze je czyści we wszystkich warunkach**, więc nie należy przypisywać mu bezwarunkowego skutku resetowania kolejki.

## 2. Potwierdzone ustawienia Windows COM

**TypeDef522 / RID7412**:
- `SerialPort.set_ReceivedBytesThreshold(1)` — `IL 0x01DD–0x01E4` → `RID7447` → `MemberRef2580`.
- `SerialPort.add_DataReceived` na `RID7416`, `SerialPort.add_PinChanged` na `RID7417`.
- `ReadTimeout=2000 ms`, `WriteTimeout=2000 ms` — osobne od timeoutów protokołu.
- `DTR=false` i `RTS=false` w tej metodzie inicjalizacji portu `IL 0x0258..0x026B`. Należy traktować te poziomy jako stan *początkowy* warstwy COM, nie stały stan Commandera. Następnie wywołania `RID3646` zmieniają sygnały.
- W ogólnej fabryce COM `RID7412` występuje `0x2580=9600` jako wartość w konstruktorze portu. **To nie jest docelowa prędkość UART dla K+CAN!** Dedykowana metoda `RID3643` ustawia następnie **830000**, zgodnie z [poprzednim raportem](ANALYSIS_HUD_ECU_HACKER_61_PROTOCOL_2026-10-24.md).
- `ReceivedBytesThreshold=1` oznacza próg zdarzenia po stronie API .NET, **nie transakcje USB po 1 bajcie** ani gwarantowane jedno zdarzenie na każdy bajt.

## 3. Nowe potwierdzenie: zakres wyjątków w metadanych CLR (EH sections)

Zinterpretowano rzeczywiste *Exception Handling clauses* dla następujących metod; te tablice nie zależą od obfuskowanego CFG:

| MethodDef | Sekcja catch z metadanych | Zachowanie jawnie obecne w metodzie |
| --- | --- | --- |
| `RID7420` (`Read(byte[1],0,1)`) | **`System.IO.IOException`** (try IL `0x0067..0x0077`, handler `0x0078..0x00B3`) | `catch` przekazuje wyjątek i kod `-1` do **RID7421**, który konstruuje komunikat o błędzie portu. |
| `RID7417` (`PinChanged`) | **`System.Exception`** | W razie wyjątku podczas obsługi zdarzenia zapisuje komunikat **`Error processing COM port events`**. |
| `RID7418` (`DiscardOutBuffer`) | **`System.IO.IOException`** | Obsługa błędu przekazywana do RID7421. |
| `RID7419` (`SerialPort.Write`) | **`System.IO.IOException`** | Obsługa błędu przekazywana do RID7421. |
| `RID7412` (otwarcie portu) | `UnauthorizedAccessException`, `IOException`, dodatkowo specjalny handler `Object` w innej podścieżce | Rozróżnia m.in. zajęty port i problemy urządzenia; oryginalne teksty to **`The port is probably used by another application or in another window.`** oraz **`Error opening COM port`**. |
| `RID2694`, `RID2695`, `RID3650`, `RID3652` | **Brak własnych sekcji EH** | Wyjątki mogą przejść wyżej; brak lokalnego `catch` nie dowodzi zakończenia całej aplikacji. |

**Niezależny wniosek dot. timeoutu:** `System.TimeoutException` z blokującego `SerialPort.Read` **nie dziedziczy po `IOException`**, więc lokalny handler `RID7420` nie obejmuje go. Może zostać przechwycony wyżej, ale w badanej ścieżce `RID2695` i `RID3650` nie ma odpowiednich własnych `catch`. W połączeniu z `ReadTimeout=2000ms` i krótszymi deadline'ami komend wymaga ostrożnej implementacji. **Nie mierzono realnych 2000 ms ani reakcji przy fizycznym odłączeniu FTDI.**

## 4. `PinChanged`: diagnostyka sygnałów, nie kod przełączający tryb

`RID7417` wywołuje `SerialPinChangedEventArgs.EventType` przez `RID7456`; testuje wartości odpowiadające znanym enum Windows/.NET:
- **8 — CtsChanged** → odczytuje `SerialPort.CtsHolding` przez `RID7423`, odszyfrowany log **`CTS = ON/OFF`**.
- **16 — DsrChanged** → `RID7424` / `DsrHolding`, log **`DSR = ON/OFF`**.
- **32 — CDChanged** → `RID7425` / `CDHolding`, log **`CarrierDetect = ON/OFF`**.
- **64 — Break** → `RID7426` / `BreakState`, log **`BREAK = ON/OFF`**.
- **256 — Ring** → oryginalny log **`RING`**.
- Wykonuje `callvirt RID2682` dla zdekodowanych zdarzeń diagnostycznych. Jego konkretne nadpisanie **TypeDef522/RID7414** wywołuje **logowanie UI** i *nie* zawiera `SerialPort.Open`, `Close`, ani `set_DtrEnable`/`set_RtsEnable`. To ważne, ponieważ wcześniejsza interpretacja `PinChanged` jako potencjalnego elementu przełączania CAN↔K-line nie miała takiego dowodu.

**Nie ma podstaw, by nazwać `PinChanged` automatycznym wykrywaniem odpięcia USB** — FT232 i sterownik mogą zgłaszać różne przejścia; fizyczna utrata USB zwykle objawia się też błędami operacji portu, a nie koniecznie PinChanged.

## 5. Co faktycznie wyszło ze statycznej analizy, a czego brak

**Potwierdzone przez IL:** dokładna kolejność DTR1 → 50ms → DTR0 → RTS(arg), wspólna obsługa wyjątków IO, diagnostyka CTS/DSR/CD/Break/Ring, próg 1 bajtu `DataReceived`, wyodrębnione statusy `0x54` (opisane osobno) i brak lokalnego `catch` dla TimeoutException w RID7420.

**Niepotwierdzone i wymagające bench:** docelowe napięcia pinów DTR/RTS na konkretnym FTDI, reboot PIC i skuteczność przełączenia K-Line/CAN, wahania zegara `Thread.Sleep(50)`, to czy `RID2688` czyści resztki ramki dla każdej konfiguracji, reset po odłączeniu USB, samodzielne auto-reconnect, realne opóźnienia FTDI, bezstratny RX i sprzętowe CAN29.

## 6. Zalecenia do projektu kcan

1. Własną inicjalizację reprezentować jako **jawną maszynę stanów** (port configured → DTR pulse → RTS mode → drain policy → UART commands → CAN RX), aby logować i testować zmiany.
2. Przy zbieraniu logów rozdzielać **status linii Windows COM** od fizycznego ACK na CAN, a przy odczycie ACK nie mylić zdarzeń `PinChanged` z `0x54 COMSTAT`.
3. Przy błędzie `Read` lub `Write` zachować **rodzaj wyjątku, częściowy bufor, znacznik czasu i ostatni stan DTR/RTS**, a nie automatycznie pulsować RESET i tracić resztę transmisji. Później eksperymentalnie porównać restart transportu z pełnym resetem adaptera.
4. Na stole, bez aktywnego pojazdu, przechwycić stany DTR/RTS i strumień UART podczas inicjalizacji HUD: zweryfikować **DTR high ~50ms → DTR low, RTS high**, następnie `55 03...`, `53 20...`, `54 00`. Faktyczną kolejność pozostałych komend (ponad sekwencją RID3646) jeszcze sprawdzić.
5. Nie kopiować `ReceivedBytesThreshold=1` lub `SerialPort.Read(...,1)` jako wymogu protokołu: to wybór implementacyjny HUD, mogący wpływać na wydajność hosta; zbenchować duże odczyty i bufor pierścieniowy.

**Podsumowanie:** udało się odtworzyć pełny *host-side* impuls resetujący FTDI i diagnostykę wyjątków portu. Nie stwierdzono automatycznego reconnection w badanych handlerach, ale nie analizowano wszystkich mechanizmów całej aplikacji.
