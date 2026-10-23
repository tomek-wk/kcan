# Audyt niskopoziomowego COM, nadawania CAN i obsługi błędów — Commander 3.0 beta / 4.5 (2026-10-23)

**Zakres:** ponowne badanie dokładnie dwóch binariów z pliku użytkownika `VAG-CAN Commander V4.5.zip`, bez nowych plików: `VAG-CAN Commander 3.0 beta.exe` (SHA-256 `dfb5e3f4724f6898c7c82d5d6e69ed3f795edb5f536f4aa5ff37ab17eae2a39b`) oraz `VAG-CAN Commander4.5.exe` (SHA-256 `85e89882a434ad83d19381ecbb5f9e77b14b237343b1432feb2f7300810e0050`).

**Metoda:** odczyt statycznych deasemblacji x86, surowych PE/IAT i dopasowanie importów przez parsowanie IMAGE_IMPORT_DESCRIPTOR/Import Lookup Table do adresów wywołań. Żadnego uruchamiania EXE/DLL, instalowania sterowników, pracy z PIC ani samochodem. „Potwierdzone” oznacza **kod hosta**. Nie publikowano programów, archiwów, danych osobowych ani logów.

## 1. Nowy problem: serial writer `0x408BD0` nie sprawdza wyniku zapisu i może wisieć

W obu binariach pisanie danych PC→adapter prowadzi do tej samej funkcji VA `0x408BD0`, z różnicą w parametrze oczekiwania.

Sekwencja potwierdzona mapą importów dołączoną do *konkretnych* EXE:

| VA / wywołanie | 3.0 beta | 4.5 | Wniosek |
| --- | --- | --- | --- |
| `0x408BD4..0x408BE1` | sprawdzenie `port.handle==-1` | to samo | Tylko zamknięty/nieprawidłowy uchwyt powoduje bezpośredni **return 0** |
| `0x408BE6` | `ResetEvent` IAT `0x44A2A0` | `ResetEvent` IAT `0x44C2A0` | Przygotowanie struktury OVERLAPPED |
| **`0x408C03`** | `WriteFile` IAT `0x44A278` | `WriteFile` IAT `0x44C278` | Zapis `n` bajtów, wskaźnik `lpNumberOfBytesWritten` oraz `LPOVERLAPPED` |
| `0x408C09` | test wyniku BOOL | to samo | `FALSE` uruchamia gałąź oczekiwania, **bez sprawdzania GetLastError()==ERROR_IO_PENDING** |
| **`0x408C0D..0x408C16`** | `WaitForSingleObject(overlapped.hEvent,INFINITE=0xFFFFFFFF)` | `WaitForSingleObject(overlapped.hEvent,0x102=258ms)` | Różny pierwszy timeout |
| **`0x408C1C..0x408C28`** | `GetOverlappedResult(..., bWait=TRUE)`, IAT `0x44A27C` | `GetOverlappedResult(..., bWait=TRUE)`, IAT `0x44C27C` | **Wynik BOOL i liczba zapisanych bajtów nie są sprawdzane** |
| `0x408C2B..0x408C36` | `mov eax,1; ret 8` | `mov eax,1; ret 8` | **Zwraca 1 nawet dla nieudanego/niedokończonego zapisu**, jeżeli uchwyt nie był już -1 |

**Ważny niuans:** choć 4.5 ogranicza `WaitForSingleObject` do **258 ms**, to następnie *bez warunku* wywołuje `GetOverlappedResult(...,TRUE)`. Według semantyki Win32 parametr TRUE może czekać aż operacja się zakończy. **258 ms nie jest więc gwarantowanym końcowym timeoutem**; również 4.5 potencjalnie może zawisnąć. W obu wersjach brak rozróżnienia pomiędzy oczekiwanym `ERROR_IO_PENDING` a natychmiastowym błędem `WriteFile`, `WAIT_TIMEOUT` czy częściowym zapisem.

To **dowodzi niepoprawnej obsługi statusów API przez kod hosta**, ale nie dowodzi, że konkretne urządzenie faktycznie wywołało takie błędy w przeszłości.

**Rekomendacja dla własnego klienta:** egzekwować limit czasu obejmujący całą operację, obsługiwać `ERROR_IO_PENDING` i inne błędy oddzielnie, kontrolować `bytesWritten == requested`, umożliwić przerwanie I/O. Powodzenie `WriteFile` to nadal nie potwierdzenie wykonania komendy przez PIC.

## 2. Inna pułapka: TX `0x60` raportuje lokalny sukces, a nie potwierdzony CAN

Funkcje TX:
- 3.0 beta: `0x403510..0x40375x`
- 4.5: `0x4034F0..0x40373C`

W 4.5 widać następującą kolejność:
1. `0x4034FB..0x403545`: buduje `60 (N+4) [4 B CAN11 ID] [N B danych]`; **brak lokalnego testu `N<=8`**.
2. `0x403598`: **`call 0x408BD0`**, a po powrocie `0x40359D` przechodzi bez sprawdzenia `EAX`.
3. `0x4035A4`: ustawia `BYTE PTR [ebx+4]=1` (lokalny status wiadomości), `0x4035A8` zapisuje lokalny timestamp `GetTickCount`.
4. `0x4035BD..0x40371C`: rejestruje rekord w 2048-slotowym buforze (licznik `&0x7FF`) i w strukturze indeksowanej **`(channel<<11) + (ID&0x7FF)`**.
5. `0x40371E`: zeruje globalne pole `0x461F38`.
6. `0x403728`: **`Sleep(10)`**, następnie `0x403733` **`return 1`**. W tej funkcji **nie ma oczekiwania na odpowiedź `0x60` PIC, ACK CAN, sprawdzenia `WriteFile` ani rzeczywistego timestampu kontrolera CAN**.
7. Analogiczne instrukcje występują w 3.0 beta: niskopoziomowe write przy `0x4035B[...]`, lokalny status, zapis historii, `Sleep(10)` przy `0x403748`; brak weryfikacji sprzętowej w tej ścieżce.

**RX `0x60`** istnieje w osobnym parserze, lecz zwykła ścieżka TX nie weryfikuje jego otrzymania przed oznaczeniem wiadomości jako wysłanej. **Lista TX to historia żądanych/transmitowanych do interfejsu danych, nie wiarygodny rejestr potwierdzonych ramek fizycznego CAN.**

**Dodatkowe potwierdzenie ograniczenia CAN29:** obie ścieżki indeksera zapisów TX/RX stosują **`(ID & 0x7FF)`** (4.5 `0x403690` oraz RX `0x402E49`), poza już znanym kodowaniem nagłówka CAN11. Indeks obejmuje port/kanal oraz ID11, **bez miejsca na CAN29**. To kolejny dowód ograniczenia tej implementacji hosta.

## 3. Brak lokalnej walidacji DLC przed kopiowaniem do pakietu

Oba funkcje TX `0x60` zaczynają od `mov cl, BYTE PTR [ebx+2]` oraz `mov dx, WORD PTR [ebx]`, następnie:
- `length = (N+4) & 0xFF` bez jawnej kontroli `N <= 8`;
- `rep movsd` + `rep movsb` kopiuje dokładnie **N bajtów** ze źródła `[ebx+0x0C]` do lokalnego bufora pakietu (4.5 `0x40353E..0x403545`, 3.0 beta `0x40355E..0x403565`).
- Bufor konstruowany jest w stosie po `sub esp,0x28` i zachowaniu rejestrów; **nie stanowi bezpiecznej przestrzeni na dowolne 255 bajtów**. Dla wartości N większych niż zaalokowane miejsce możliwe nadpisanie sąsiednich danych stosu. Dokładny próg zależy od rekonstrukcji ramki stosu i konwencji wywołania; **nie wnioskować, że istnieje automatyczna obsługa CAN-FD**.

**Granica dowodu:** brak *lokalnej* walidacji w TX nie dowodzi braku ograniczeń w wywołujących GUI (mogą filtrować N). Nie należy testować skrajnych N przez dostarczony EXE — użyć własnej implementacji z kontrolą `0<=N<=8` i offline testów granicznych.

## 4. Potwierdzona sekwencja sterowania DTR/RTS przy otwarciu COM

W 4.5 `0x408D5E..0x408D95` (3.0 beta te same adresy) w funkcji otwarcia `0x408CD0`:
1. `EscapeCommFunction(handle,5)` = **SETDTR**;
2. `Sleep(0x1F4)` = **500 ms**;
3. `EscapeCommFunction(handle,6)` = **CLRDTR**;
4. `EscapeCommFunction(handle,3)` = **SETRTS**.

Każde niepowodzenie `EscapeCommFunction` (poza `Sleep`) jest w tej ścieżce sprawdzane, z przejściem do gałęzi błędu otwarcia. **Nie potwierdzono tutaj CLRRTS**, więc nie należy opisywać impulsu RTS jako mającego ustalone oba zbocza. Poprawna semantyka stałych Win32: SETRTS=3, SETDTR=5, CLRDTR=6.

**Nie znamy skutku fizycznego** DTR/RTS dla konkretnego schematu FTDI↔PIC, nie wolno automatycznie utożsamiać impulsu DTR z resetem kontrolera lub zmianą trybu K-Line. Sekwencję należy uwzględnić w izolowanym badaniu, bo wyjaśnia stałe opóźnienie rozruchu i zależność od linii sterujących.

## 5. RX i ścieżka „raw send” — dodatkowe fakty, nie dowód CAN29

- W 4.5 `0x402CE0..0x402F2B` dla komunikatu `0x70` dekoduje 11-bit ID, układa 20-bajtowe rekordy i aktualizuje 2048-slotowy pierścień. **`0x403770` (wywołanie przy `0x402EDF`) zwraca zawsze `AL=1`**; nie prowadzi w tej konkretnej procedurze filtrowania CAN, ale nie wyklucza filtracji sprzętowej ani GUI w innych miejscach.
- Istnieje też ogólny writer `0x403740`, z wywołaniami `0x40A1C4` i `0x40A517`. W `0x40A160..0x40A1E0` tekstowe bajty są parsowane do bufora i wysyłane, a `0x40A440..0x40A559` dostarcza ścieżki konfiguracyjne dla `0x53`. **Możliwość wysłania dowolnych bajtów protokołu UART nie dowodzi istnienia w firmware komendy CAN29**.
- Lista znanych i potwierdzonych komend/walidatorów `C0,51,52,53,54,60,6F,70` pozostaje bez nowych wartości. W tym audycie **nie znaleziono nowego formatu rozszerzonego EID29, ani dowodu semantyki `0x54/0x6F/C0`**.

## 6. Wpływ na projekt i testy

- **KCAN-D048 (nowe):** wyłapać błędy pisania UART, ignorowany `GetOverlappedResult`, pozorny limit 258ms (możliwy drugi nieskończony wait); osobno potwierdzić rzeczywiste `bytesWritten`. Priorytet wysoki przy własnej aplikacji.
- **KCAN-D049 (nowe):** rozdzielić `TX_requested`, `UART_written`, `PIC_acknowledged`, `CAN_observed/acknowledged`; nie sugerować przez GUI/kolumnę TX, że `Sleep(10)` i `return 1` znaczą powodzenie fizycznego CAN; uwzględnić realną rolę DTR/RTS.
- **KCAN-D050 (nowe):** niezależne sprawdzenie walidacji `N<=8` na każdej ścieżce konstrukcji CAN, testy *offline* wartości granicznych i odporności parsera. Niewalidowane wartości N nigdy nie powinny być podawane staremu EXE ani nieznanemu firmware.

Powiązania z istniejącymi: D012 (DLC), D016 (DTR/RTS), D022 (RX), D037/D038 (rzeczywista przepustowość/straty), D039 (odpowiedź `0x60`), D046 (numery COM), D047 (CAN29). Nie przypisywać obserwacji z programu do fizycznego zachowania danego adaptera. **Wszystkie testy z komunikacją CAN tylko na stanowisku izolowanym**, bez samochodu i bez losowych poleceń.

**Raport poprzedni:** [ANALYSIS_CAN29_INIT_30BETA_45_2026-10-23.md](ANALYSIS_CAN29_INIT_30BETA_45_2026-10-23.md), [ANALYSIS_VAGCAN_30BETA_45_DEEP_2026-10-23.md](ANALYSIS_VAGCAN_30BETA_45_DEEP_2026-10-23.md).

## 7. Niezależna weryfikacja semantyki Win32

Zestawiono z aktualną dokumentacją producenta systemu, niezależną od samego pliku EXE:
- [Microsoft, GetOverlappedResult](https://learn.microsoft.com/en-us/windows/win32/api/ioapiset/nf-ioapiset-getoverlappedresult): `bWait=TRUE` **nie zwraca przed ukończeniem wciąż oczekującej operacji**, a `lpNumberOfBytesTransferred` podaje rzeczywisty rozmiar — oba aspekty są istotne dla zidentyfikowanej wady.
- [Microsoft, WriteFile](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-writefile): dla asynchronicznego `WriteFile` wynik FALSE z `ERROR_IO_PENDING` wymaga późniejszego zakończenia; inne błędy muszą być rozróżnione. Brak sprawdzenia to błąd hosta.
- [Microsoft, EscapeCommFunction](https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-escapecommfunction): stałe Win32 **SETRTS=3, SETDTR=5, CLRDTR=6** są udokumentowane. **Nie wynika** z tego połączenie fizycznego pinu FTDI z określoną funkcją PIC.

Nie wykonywano dynamicznych testów Windows, więc ewentualne konsekwencje na konkretnej maszynie i urządzeniu pozostają prognozą na podstawie kodu i kontraktów API.
