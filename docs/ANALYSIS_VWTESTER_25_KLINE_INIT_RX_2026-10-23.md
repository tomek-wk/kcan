# Czwarta analiza statyczna VWTester 2.5 — K-Line, inicjalizacja, echo, retry i COM10+

**Data:** 2026-10-23. Badany plik: `VWTester.exe` z `k+can2.5(1).zip`, **688128 B**, SHA-256 `b90fc612decb04759a77fd0f02946157d832053186c7adf5e50624a1b103a10d`. Porównanie wykonano na binariach i istniejącej deasemblacji objdump, **bez uruchamiania EXE/DLL**. Wszystkie adresy to VA dla tej jednej kompilacji. Wnioski o zachowaniu hosta **nie są jeszcze testami fizycznego interfejsu**.

## 1. Nowy mechanizm: generowanie 5-baud przez Windows BREAK

Kod korzysta z importu `KERNEL32!EscapeCommFunction` (IAT `0x47D2DC`). Zaimplementowano pomocnicze funkcje:
- `0x40A710–0x40A77B` → `EscapeCommFunction(handle, 8)`, czyli **SETBREAK**;
- `0x40A790–0x40A7A6` → `EscapeCommFunction(handle, 9)`, czyli **CLRBREAK**;
- `0x42AED0` → opóźnienie oparte na `QueryPerformanceCounter/Frequency` z próbkowaniem czasu;
- `0x42AE00–0x42AEC9` → inicjalizator wysyłający adres **od najmłodszego bitu**.

Dla `0x42AE00` sekwencja z kodu:
1. `CLRBREAK` (linia zwolniona), opóźnienie `0x1F4 = 500` jednostek czasu;
2. `SETBREAK` (bit startu), opóźnienie `0xC7 = 199`;
3. `edi = 8`, dla **każdego z 8 bitów** parametru `addr`: jeżeli `addr & 1` to `CLRBREAK`, w przeciwnym razie `SETBREAK`; po każdym bicie `delay(199)`, następnie `addr >>= 1`;
4. `CLRBREAK` (bit stopu), `delay(199)`; przywrócenie normalnego priorytetu wątku.

Odpowiada to **programowemu generowaniu inicjalizacji 5-baud o 8 bitach danych i stopie**. Przyjmuje się, że opóźnienie ma jednostki zbliżone do ms — uzasadnia to funkcja oparta na QPC; **należy zmierzyć realne impulsy**, bo Windows nie gwarantuje dokładności 5 baud.

Ta ścieżka jest wywoływana m.in. bezpośrednio i przez `0x42AD00`, gdy parametr trybu nie jest zerowy. **Nie określono, na który fizyczny pin K-Line adaptera trafia BREAK:** Windows steruje TXD portu FTDI; zależy to od PCB.

## 2. Drugi wariant startu — 7 bitów plus bit parzystości

W **odrębnym** inicjalizatorze `0x434120–0x43424D`:
- `0x43419F`: `SETBREAK` i opóźnienie `0xC7=199`;
- `0x4341B8`: pętla ma **7 iteracji**, każda bit adresu LSB-first przez `CLRBREAK`/ `SETBREAK`, co 199 jednostek;
- `0x4341C2–0x4341CA`: dla bitów o wartości 1 zwiększany jest licznik;
- `0x4341ED–0x434212`: po siedmiu bitach obliczana jest parzystość licznika i generowany **dodatkowy bit parzystości**; przy standardowej polaryzacji BREAK wygląda to na **odd parity** (nieparzysta liczba jedynek), lecz polaryzację i interpretację trzeba zmierzyć;
- `0x434220`: `CLRBREAK` (stop), po czym procedura przechodzi do oczekiwania/odbioru.

To jest **inny kod i inny format** niż pętla 8-bitowa z `0x42AE00`. Również wykorzystuje przybliżony czas jednego bitu 200 ms.

**KCAN-D030:** ustalić, do jakiego trybu diagnostycznego używana jest odmiana 7-bit + parity, a do jakiego 8-bit bez parzystości, i sprawdzić to analizatorem logicznym. Nie utożsamiać odmian tylko na podstawie podobieństwa do norm.

## 3. Krótka inicjalizacja BREAK

W `0x42AD62–0x42AD91` gałąź alternatywna dla bitowego 5-baud wykonuje:
- `CLRBREAK`, opóźnienie `0x0F=15`;
- `SETBREAK`, opóźnienie `0x1E=30`;
- `CLRBREAK`, opóźnienie `0x16=22`.

To rzeczywista ścieżka **inicjalizacji impulsowej** w kodzie (zależna od argumentu funkcji), lecz jej dokładne czasy na fizycznej linii i zgodność z klasyczną procedurą fast-init wymagają pomiaru.

Inna procedura `0x42B540–0x42B68C` ustawia jeszcze dłuższe sekwencje BREAK (kilka odcinków `0xC7`, odcinek `0x578=1400` oraz `0x1E=30`). **Jej cel nie jest odtworzony**, więc nie klasyfikujemy jej jako standardowej 5-baud/fast-init.

## 4. Fizyczny K-Line: co jest ustalone, a co nie

- **CAN transport hosta** w funkcjach `0x403CF8/0x4099C4`: UART **833333 bit/s** (wcześniejsze raporty).
- **Odrębna ścieżka K-Line**: wywołania `0x40A4F0` z argumentem `0x28E8 = 10472 bit/s`, np. `0x42B575` oraz `0x40ADC1`.
- **Nie twierdzimy**, że wszystkie sesje K-Line pracują stale dokładnie przy 10472, ponieważ kod ma również inicjalizacje 5-baud i parametryzowane konfiguracje COM. Istotne jest to, że **833333 nie jest jedynym baudrate obecnym w programie**.
- `SETBREAK`/`CLRBREAK` sterują stanem linii nadajnika UART, a `SETDTR`/`CLRDTR` i `SETRTS`/`CLRRTS` występują osobno. To **różne mechanizmy**: nie utożsamiać inicjalizacji K-Line przez BREAK z resetowaniem przez DTR/RTS.

## 5. Parser K-Line: co potrafi

Funkcja `0x42AFB0–0x42B249` utrzymuje stan i bufor odebranej wiadomości:
- Jeśli pierwszy bajt ma wysoki bit ustawiony: wylicza wstępną długość jako `(first_byte & 0xFF) - 0x7C` (`0x42B079–0x42B08F`).
- W przeciwnym razie (niezerowy bajt): długość jako `first_byte + 2` (`0x42B087–0x42B08F`).
- Gdy pierwszy bajt to **`00`**, przechodzi do specjalnego stanu `0x55AA` i z następnego bajtu tworzy długość `next_byte+3` (`0x42B060–0x42B04F`). **Znaczenie protokołowe tego wyjątku nie zostało w pełni rozpoznane** — nie interpretować bez sesji.
- Po złożeniu wiadomości porównuje ją bajt po bajcie z zapamiętanym buforem nadawczym: `repz cmpsb` `0x42B100–0x42B120`. **Identyczny ciąg nie przechodzi zwykłą ścieżką publikowania odpowiedzi**. To wyraźny mechanizm *echo suppression*.
- W `0x42B137–0x42B183` wykrywa dwie postacie **odpowiedzi negatywnej NRC=0x78**: `83 ... 7F ... 78` lub `03 7F ... 78`; wybiera specjalny obiekt zdarzenia do powiadomienia zamiast standardowego. Wniosek: odpowiedzi *Response Pending* są rozróżniane. **Nie odtworzono pełnego algorytmu ponawiania diagnostyki ani timeoutów UDS/KWP.**
- W innym stanie `0x42B1B7–0x42B240` rozpoznaje **sync 0x55** i nadaje dopełnienie jednego bajtu, związane z wymianą keywordów. To **nie** komenda CAN `55 03 ...`.

## 6. TX K-Line — potencjalna pętla bez limitu prób

W generatorze ramek `0x42B250` warianty z sumą kontrolną wysyłają bajty przez import `TransmitCommChar`:
- `0x42B3EC–0x42B3F8` — pierwsza próba;
- `0x42B3FC–0x42B40A` — **ponawiaj ten sam bajt, dopóki `TransmitCommChar` nie zwróci sukcesu**; w tej pętli nie ma licznika ani timeoutu;
- `0x42B40C–0x42B423` — odstęp interbyte, parametryzowany polem obiektu;
- `0x42B440–0x42B449` — funkcja kończy się zwróceniem `1`.

**Ryzyko:** przy trwale nieudanym `TransmitCommChar` wywołanie może zapętlić wątek. Własny sterownik powinien mieć limit prób/czasu, rejestrować `GetLastError`, obsługiwać zamknięcie portu. To **zidentyfikowane ograniczenie programu Windows**, nie cecha PIC.

## 7. COM10+ wbrew starym wskazówkom instalacyjnym

W `0x40A543–0x40A56D` program sprawdza numer COM:
- **1–9**: format `COM%d` pod adresem `0x490C1C`;
- **10 i więcej**: format `\\.\COM%d` pod adresem `0x490C10`.

Oba ciągi odczytano **bezpośrednio z sekcji .data EXE**, nie z instrukcji. Zatem **kod 2.5 przewiduje otwieranie COM10+**; zalecenie COM1–COM4 z polskiej instrukcji wcześniejszej dystrybucji **nie jest ograniczeniem tego kodu ani protokołu PC↔PIC**. Nie rozstrzyga to ograniczeń UI i konkretnych starszych wydań aplikacji.

## 8. Co nie zostało odtworzone

- Właściwa semantyka `0x54`, `0x6F` w protokole PC↔PIC.
- Pełna mapa CAN29, statusy kontrolera CAN, listen-only bez ACK.
- Dokładna elektryczna ścieżka BREAK → FTDI → PIC/transceiver → K-Line na konkretnym niebieskim adapterze.
- Gwarantowane czasy 5-baud / szybkie init w fizycznym sprzęcie, choć instrukcje hosta są jawne.
- Zachowanie rzeczywistych ECU na otrzymane ramki; nie wykonywano testów na samochodzie.

## Proponowane testy — bez pobranych binariów w GitHubie

Szczegóły i numery KCAN-D029–D035: [DISCREPANCIES.md](DISCREPANCIES.md). Priorytet: pomiar stanów BREAK i czasów bitowych na odizolowanym adapterze, weryfikacja konfiguracji `10472`, odbioru echa i zachowania `Response Pending` na symulowanym torze K-Line; porównanie rzeczywistego firmware dopiero później.
