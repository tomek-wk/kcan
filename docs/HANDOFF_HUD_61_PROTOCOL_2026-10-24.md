# HANDOFF — VAG K+CAN Commander, protokół UART; po analizie HUD ECU Hacker 6.1

**Stan: 2026-10-24.** Ten plik jest **krótkim, aktualnym punktem startowym nowej rozmowy**, uzupełniającym rozbudowane [HANDOFF_NEXT_CHAT.md](HANDOFF_NEXT_CHAT.md). Repo: **https://github.com/tomek-wk/kcan**, gałąź `main`. Ostatni etap: zakończona wąska statyczna analiza `RID2688` (odrzucanie bajtów po resecie) i `RID2694` (częściowe odczyty i timeout), **bez testów fizycznych**.

## 0. Najważniejsze zasady użytkownika

- **Cel wyłącznie:** odtworzyć protokół **PC ↔ interfejs VAG K+CAN Commander** (FTDI/UART ↔ PIC), by wykorzystać konkretny adapter do własnych zastosowań CAN/sniffera. **Nie szukać i nie analizować przypadkowych firmware innych adapterów CAN** ani nie utożsamiać projektu `PSA-comm` / diagnostyki Start-Stop z celem `kcan`.
- Wartościowe źródła: firmware **Commandera**, czytelne implementacje hosta (EXE/DLL/J2534), logi UART i statyczne zachowanie HUD ECU Hacker. Wersje 1.4, 2.5, 3.0, 3.6, 4.5, 5.x mogą się różnić. Rozróżniać **dowód host-side**, symulację IL, log fizycznego adaptera i hipotezę firmware.
- **Repozytorium:** zapisuj autorskie **Markdown / własne skrypty offline / krótkie wektory HEX**, ale **nie commituj** plików firm trzecich: EXE, DLL, ZIP/RAR, HEX firmware, zrzutów ECU ani surowych logów. Nie uruchamiać starych, nieznanych EXE i nie reflaszować adaptera bez osobnej decyzji użytkownika.
- Nie twierdzić, że „show all” oznacza fizyczny **listen-only**; HUD jawnie informuje, że **ACK dla VAG K+CAN nie można wyłączyć** (w jego obsługiwanym sterowniku).
- Każdą nieudaną próbę, brak potwierdzenia i różnicę między implementacjami zachować jako materiał badawczy. Nie nadpisywać sprzecznych obserwacji wnioskami bez dowodu.

## 1. Materiał wejściowy / niezbędne artefakty

Użytkownik przekazał `HUD-ECU-Hacker v6.1(1).zip` z `Installer HUD ECU Hacker 6.1.exe`. Zasób `CRYP` (~30MB), zaszyfrowany Blowfish CAB, został **wydobyty statycznie** bez instalacji. Jest w nim:
- `ECU_Hacker.exe`: **6 449 152 B**, SHA256 `b70fa891953927da0600eac420d18acdc15a39bdba25dad366e1c52a602eeeb8`;
- `Help.chm`, `Version History.rtf`, `Translation/Template.xml`, makra;
- brak rzeczywistego `ECU_Hacker.pdb` w archiwum.
- W bieżącym środowisku podczas ostatniego handoff plik EXE był dostępny jako `/mnt/data/hud_ecu_extracted/ECU_Hacker.exe`, a ZIP jako `/mnt/data/HUD-ECU-Hacker v6.1(1).zip`. **W nowej rozmowie nie zakładać automatycznej dostępności tej ścieżki**: sprawdzić runtime, ewentualnie poprosić o załączenie pliku lub skorzystać z informacji już zapisanych w repo.
- Poprzedni [raport ekstrakcji](ANALYSIS_HUD_ECU_HACKER_61_KCAN_2026-10-24.md) zawiera formę zasobu/algorytmu i SHA. **Nie ma potrzeby ponownie prosić o instalację programu Windows.**

## 2. Odtworzone komendy PC ↔ Commander (HUD 6.1)

| Operacja | Format/wynik statyczny | Miejsce dowodu |
| --- | --- | --- |
| Framing UART | `opcode(1) length(1) payload(length)` | RID3649, RID3650 |
| CAN bitrate | `55 03 N FA 07`, gdzie **`N = round(1000000/bitrate)-1`**; 500k → `55 03 01 FA 07` **niezależnie obecne w wcześniejszym logu/DLL** | RID3643/3644, [PROTOCOL.md](PROTOCOL.md) |
| Odczyt statusu | `54 00` → `54 02 S0 S1` | RID3654 |
| Filtry 11bit, show-all | `53 20` + **6×`00 00 00 00` + 2×`00 40 00 00`** | RID3647/3648/3655 |
| Filtry 29bit, show-all | `53 20` + **8×`00 40 00 00`** | RID3647/3648/3655 |
| TX CAN11, ID 0x123, data 11 22 33 | `60 07 24 0C 00 00 11 22 33` | RID3651/3655/3649 |
| RX CAN11 przykładowy | `70 07 24 0C 00 00 11 22 33` → ID 0x123 | RID3650/3656 |
| CAN29 przykład **host-side** | ID `0x01ABCDE3` → `0D 4B CD E3` | RID3655/3656 |

**Kodowanie ID (4B big-endian)**:
```text
v = extended ? can_id : (can_id << 18)
w = (((v & 0xFFE00000) << 3) | (v & 0x001FFFFF)) & 0xffffffff
if extended OR is_filter_mask: w |= 0x00400000
if RTR: w |= 0x00800000
wire_id = to_big_endian(w, 4)
```
Dekoder identyfikuje 11/29bit według **trybu instancji adaptera** (RID3656), a nie wyłącznie flagi ID. **To nie dowodzi, że dany firmware PIC faktycznie obsługuje CAN29**. Ponadto w kodzie HUD bitrate COM żądany jako **830000**, a w innych programach Commandera jako **833333**; rzeczywista kwantyzacja FTDI nie była mierzona.

## 3. Znaczenie odpowiedzi statusowej 0x54 (oryginalne zasoby HUD)

**S0**: `0x40 Tx aborted`, `0x10 Tx bus error`.

**S1**: `0xC0 Rx Buffer Overflow` (jeden wspólny komunikat dla bitów 6/7), `0x20 Tx Bus Off`, `0x10 Tx Bus Passive`, `0x08 Rx Bus Passive`, `0x04 Tx Warning`, `0x02 Rx Warning`.

Mapę potwierdzono **odszyfrowanymi napisami HUD i 512/512 testów wykonania IL**. `S0` odpowiada układem bitów `TXBnCON`, `S1` rejestrowi `COMSTAT` PIC18; to **silna hipoteza**, nie udowodniony surowy odczyt rejestrów. **UWAGA `S1 & 0x80`: w ECAN mode 2 bit 7 COMSTAT może oznaczać FIFOEMPTY, nie overflow.** Brak overflow nie wyklucza strat w FTDI/host. Pełne [statusy](ANALYSIS_HUD_61_STATUS_0x54_2026-10-24.md).

## 4. Odbiór 0x70, timeouty i reset

- **RID3650**: dwuetapowy parser UART: najpierw `opcode,length`, potem reszta; dla `0x70` długość **4..12** (4B ID + 0..8B Classic CAN). Ramki `0x70` przeplatane z odpowiedziami `0x53/0x54/0x55` trafiają do kolejki FIFO; asynchroniczne `0x60` może być pomijane. Nieoczekiwany opcode albo niedozwolona długość prowadzą do błędu w tej warstwie. Nie dowiedziono resynchronizacji po uszkodzonym bajcie.
- **RID3652**: pobiera FIFO i **co najmniej po 2 sekundach** od zapisanego czasu uruchamia zapytanie statusowe `0x54`. To warunkowe zachowanie odbiorcy, nie niezależny timer sprzętowy.
- **RID2695**: lista bajtów, sygnały `DataReceived → EventWaitHandle.Set`, `WaitOne`, dopełnianie brakujących bajtów, deadline z `Stopwatch`. Pod spodem `SerialPort.Read(byte[1],0,1)`; `ReadTimeout/WriteTimeout=2000 ms` w konfiguracji portu Windows, niezależnie od krótszych limitów komend. Szczegóły [transportu](ANALYSIS_HUD_61_UART_TRANSPORT_2026-10-24.md).
- **RID3646 reset / przełączenie:** **DTR=1 → `Sleep(50ms)` → DTR=0 → RTS=arg → `RID2688(false)`**. Inicjalizacja Commandera wybiera **RTS=1**, osobna procedura zakończenia **RTS=0**; nazwy funkcjonalne RTS zależą od konkretnej płytki. [Dowód](ANALYSIS_HUD_61_RESET_DTR_RTS_SERIAL_ERRORS_2026-10-24.md).
- **RID7420** ma catch `IOException` dla `SerialPort.Read(byte[1])`, ale **nie lokalny catch `TimeoutException`**; `RID2695/3650` również nie mają własnych sekcji catch. `PinChanged` w badanej klasie loguje stan CTS/DSR/CD/Break/Ring, nie jest udowodnionym mechanizmem auto-reconnect.

## 5. OSTATNI ETAP przed handoff: RID2688 i RID2694 — wynik NEGATYWNY istotny dla sniffera

**Pełny raport:** [ANALYSIS_HUD_61_DRAIN_RID2688_PARTIAL_TIMEOUTS_2026-10-24.md](ANALYSIS_HUD_61_DRAIN_RID2688_PARTIAL_TIMEOUTS_2026-10-24.md).

- **RID2688** (TypeDef183, RVA **`0x2AFE94`**, 329 B IL) po resecie **odczytuje i ODRZUCA bajty oczekujące w COM**. Nie zna `0x70`, nie zachowuje granic wiadomości i nie jest algorytmem naprawiającym framing. Normalna ścieżka odrzuca dostępne bajty do opróżnienia, o ile inne zdarzenia nie dopiszą kolejnych danych.
- **Wyjątek ważny dla zgodności sprzętowej:** `RID3420().flags & 1` powoduje opuszczenie pętli po **jednym odczytanym bajcie**; w pozostałych zbadanych wariantach pobiera cały dostępny strumień. **Nie ustalono wartości tej flagi przy aktywnym Commanderze na konkretnej płytce**.
- `RID3646` wywołuje `RID2688(false)` (bez logowania treści odrzuconych bajtów); inna ścieżka błędu `RID3650` może wywołać `RID2688(true)` (z logowaniem). **Logować stratę danych po resecie osobno od sprzętowego overflow**.
- W niezależnej symulacji interpreterem IL dla `RID2688` i modelem [`tools/hud_kcan_drain_model.py`](../tools/hud_kcan_drain_model.py) **768/768 scenariuszy** było zgodnych (0..63 bajty, flagi 0,1,2,3,4,9, logowanie tak/nie); wynik **powtórzono podczas handoff**, testy `check_drain.py` i lokalnego modelu przechodzą.
- **RID2694** (TypeDef183, RVA **`0x2B08DC`**, 474 B IL) przy niepełnym odbiorze przez `RID2695` dla **`flags&4` zwraca `false` bez wyjątku** (inne ustawienia mogą rzucać). Oba odczyty `RID3650` używają `flags=4`: do 2 B nagłówka i potem do `length+2` bajtów całej odpowiedzi; sam parser sprawdza `List.Count`.
- **Nowe ostrzeżenie:** `RID3650` tworzy lokalną listę na wywołanie. Nie dowiedziono utrzymania niepełnego prefiksu między kolejnymi wywołaniami lub przy resecie. Utracona wiadomość może wynikać z **czyszczenia bufora przez HUD**, nawet kiedy `COMSTAT` nie sygnalizuje przepełnienia.

## 6. Reprodukowalne autorskie skrypty offline (w repo, bez I/O)

- [`tools/hud_kcan_codec.py`](../tools/hud_kcan_codec.py): CAN11/CAN29, RTR, maski, `0x53`, `0x55`, TX `0x60`; testy wektorów.
- [`tools/hud_kcan_rx_parser.py`](../tools/hud_kcan_rx_parser.py): składanie fragmentów i przeplatanie `0x70` z odpowiedziami sterującymi — **model, nie kopia dokładnej polityki resynchronizacji HUD**.
- [`tools/hud_kcan_status.py`](../tools/hud_kcan_status.py): 8 klas zdarzeń statusowych 0x54, oryginalne nazwy HUD.
- [`tools/hud_kcan_drain_model.py`](../tools/hud_kcan_drain_model.py): zachowanie `RID2688`, 768 scenariuszy.

Uruchamianie: `python tools/hud_kcan_codec.py`, `python tools/hud_kcan_rx_parser.py`, `python tools/hud_kcan_status.py`, `python tools/hud_kcan_drain_model.py`. Brak zależności zewnętrznych dla skryptów; wszystkie działają offline.

## 7. Następne zadania — uporządkowana kolejność

1. **Odtworzyć zachowanie częściowej wiadomości UART w realnym `RID3650`**: wywołanie po timeout nagłówka, po timeout payloadu, po niespodziewanym opcode; zbadać `RID2694/2695` oraz wpływ `RID2688(true)` na pozostałość strumienia. Rozróżnić *bajt odebrany z FTDI*, *bajt buforowany w hoście*, *bajt celowo usunięty* i *bajt stracony fizycznie*. W repo raport opisuje, co już potwierdzono i czego nadal nie znamy; nie odtwarzać automatycznie resynchronizacji, której nie wykazano.
2. **Zweryfikować pochodzenie `RID3420().flags & 1` w klasie konkretnego transportu Commandera.** To wpływa na to, czy `RID2688` odrzuca jeden bajt czy dostępne dane.
3. **Odtworzyć semantykę `0x54` na konkretnym firmware** i zachowanie kasowania zatrzasków COMSTAT/overflow. Bez sprzętu to hipoteza rejestrowa.
4. Zaprojektować **bezpieczny bench test** przy użyciu jednego FTDI / izolowanej magistrali CAN: pomiary DTR/RTS, `55 03...`, `53 20...`, `54 00`; sprawdzić CAN29 na konkretnej rewizji firmware, overflow i wpływ resetu na bufor; nie pracować na samochodzie bez świadomej decyzji użytkownika.
5. Sniffer: jeden konsument UART, stanowy parser, osobne kolejki, monitoring opóźnień i **liczników świadomego odrzucenia** (host) vs `0x54` (MCU), surowe heksy + timestamp. **Nie zapewniać true listen-only / braku ACK** w oryginalnym firmware.

## 8. Uwaga dotycząca pozostałych poszukiwań

Katalog poprzednich tropów firmware to [FD-001–014](FIRMWARE_DUMP_LEADS_2026-10-23.md), [FD-015–026](FIRMWARE_DUMP_FOLLOWUP_2026-10-24.md), [FD-027–033](FIRMWARE_ALTERNATIVE_SOURCES_2026-10-24.md), [FD-034–042](FIRMWARE_DIRECT_DOWNLOADS_AND_NEGATIVE_TESTS_2026-10-24.md). Użytkownik ręcznie potwierdził, że `VKCC_ALL.ZIP` i `VAG_K+CAN_Commander_v36.zip` są **pakietami PC**, a `PGMKCAN2.rar`, `KCAN-ELM327.RAR`, `CAN-PIC18F25K80.RAR` są dla niego **niedostępne**. Nie powtarzać tych linków jako dostępnych plików MCU. Firmware Commander dotychczas **nie uzyskano**; dalsze poszukiwania tylko jeśli są faktycznie związane z protokołem Commandera, a nie inne sterowniki CAN.

## 9. Instrukcja do nowej rozmowy

> Kontynuuj badania repozytorium `tomek-wk/kcan`. Zacznij od `docs/HANDOFF_HUD_61_PROTOCOL_2026-10-24.md` i raportu `docs/ANALYSIS_HUD_61_DRAIN_RID2688_PARTIAL_TIMEOUTS_2026-10-24.md`. Interesuje mnie **protokół komunikacji PC↔VAG K+CAN Commander**, w szczególności bezstratny/diagnozowalny odbiór UART i filtracja CAN. Aktualny punkt: **RID2688 odrzuca oczekujące bajty po resecie**, z wyjątkiem `RID3420.flags&1` ograniczającym liczbę pobranych bajtów; `RID2694(flags=4)` umożliwia niepełny odczyt bez wyjątku. Sprawdź kolejne skutki częściowych ramek w `RID3650` i rzeczywistą wartość flag transportu. Nie myl implementacji hosta z możliwością firmware PIC; dokumentuj ograniczenia i wpisuj wyniki do repo. Nie flashuj ani nie uruchamiaj podejrzanych EXE.
