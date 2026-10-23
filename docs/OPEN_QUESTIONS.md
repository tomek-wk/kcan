# Nierozstrzygnięte zagadnienia — priorytety

## P0 — konieczne przed sterownikiem ogólnego zastosowania

- [ ] Znaczenie `0x5F` i `0x50` oraz pełna sekwencja inicjalizacji / recovery.
- [ ] Mapowanie 32 bajtów `0x52/0x53` na filtry, maski i rejestry PIC.
- [ ] Obsługa RX asynchronicznego `0x70`, przepełnienia buforów i błędów CAN.
- [ ] Polaryzacja DTR/RTS i zachowanie resetu na **tym konkretnym niebieskim adapterze**.
- [ ] Rozpoznanie trybu monitorowania, ACK i dostępności *listen-only*.

## P1 — kompatybilność i funkcje rozszerzone

- [ ] Poprawny format CAN29 i niezależny round-trip wielu identyfikatorów.
- [ ] Oryginalny DLC 0–8, ramki zdalne (RTR) i bity błędów.
- [ ] Prędkości inne niż 500 kbit/s: potwierdzenie 125/250/1000 kbit/s na sprzęcie.
- [ ] Odczyt wersji firmware / identyfikacja odmian i zachowania pierwszej komendy.
- [ ] Zachowanie filtra `PassThruStartMsgFilter` po kolejnych modyfikacjach.
- [ ] Oddzielenie transportu K-Line od obsługi CAN.

## P2 — długoterminowa analiza

- [ ] Statyczna analiza `VAG-K+CAN Commander.exe` (po pozyskaniu legalnej kopii bajtów, bez uruchamiania).
- [ ] Porównanie oryginalnej aplikacji z `J2534KCAN.dll` i KCANTEST.
- [ ] Odtworzenie protokołu w całości i specyfikacja kodów statusu.
- [ ] Ocena alternatywnego firmware/bootloadera wyłącznie po inwentaryzacji konkretnego MCU i PCB.

## Polityka dowodowa

Przy zamykaniu zadania dopisać źródło, wersję sprzętu, próbkę HEX lub parametry pomiaru i ograniczenia. Nie zastępować `nieustalone` słowem `potwierdzone` tylko na podstawie podobnej płytki.


---

## Kolejny materiał — oryginalny EXE 1[X].4

- [ ] **P0** Uzyskać czytelną implementację komunikacji PC ↔ PIC z innej, niechronionej wersji programu lub własnych przechwyconych sesji. Ten EXE jest spakowany/chroniony; jego jawne importy nie ujawniają funkcji CAN.
- [ ] **P1** Porównać oznaczenia wersji **1.4**, zasobów EXE **1.0.0.1** i informacji o firmware na konkretnym interfejsie. Nie utożsamiać ich bez dowodu.
- [ ] **P1** Ustalić, czy wymaganie **oddzielnego dongla USB** dotyczy badanej dystrybucji, a nie zwykłych klonów.
- [ ] **P1** Porównać zachowanie programu Commander i sterownika J2534 względem transportu COM/D2XX po uzyskaniu wiarygodnych przechwyceń komunikacji.
- [ ] **P1** Sprawdzić CAN11 dla ID **niepodzielnych przez 8** (np. `0x123`), ponieważ istniejące logi obejmują tylko `0x7E0/0x7E8`.

Lista rozbieżności, proponowanych testów i statusów: [DISCREPANCIES.md](DISCREPANCIES.md).


---

## Po analizie `commander vag-k can.zip`

- [ ] **P1 / KCAN-D006:** ustalić zawartość instalatora Setup Factory 8.0 bez uruchamiania go; porównać wewnętrzny EXE z wersją chronioną EXECryptor przez SHA-256.
- [ ] **P1 / KCAN-D007:** czy w dokumentacji różnych dystrybucji występuje osobny dongle USB z powodu odmiennego modelu licencjonowania?
- [ ] **P1 / KCAN-D008:** weryfikacja wersji sterownika FTDI (własny INF 2.04.06 versus PDF 2.6.0.0) i faktycznie zainstalowanego na PC.
- [ ] **P1 / KCAN-D009:** pomiar wpływu buforów USB 512/4096 B i Latency Timer 1/16 ms na zachowanie starej aplikacji; **nie zakładać**, że te wartości są częścią protokołu UART.
- [ ] **P1 / KCAN-D010:** określić, czy konkretny egzemplarz PIC jest zasilany z USB czy OBD (i jakie ma wartości napięcia); instrukcje różnych urządzeń nie rozstrzygają tego.


---

## Po otrzymaniu `FULL 1.4`

- [ ] **KCAN-D011 / P2:** rozstrzygnąć kolejność interpretacji podwójnej sekcji `[CHANNEL]` w `Tester.ini` oraz wpływ `TARGET=6` zamiast `TARGET=0` na wybrany cel diagnostyczny i/lub bajty PC↔PIC.
- [ ] **KCAN-D011 / P2:** ustalić semantykę `[TRACE] FILEINDEX=1956` vs `3221`, bez traktowania wartości jako poleceń adaptera.
- [ ] **P1:** dostarczyć **inny SHA-256 EXE** lub log UART do faktycznego porównania implementacji. Plik z pakietu FULL 1.4 jest identyczny z poprzednim.


---

## Priorytety po analizie Commandera 2.5

- [ ] **P0 / KCAN-D012:** potwierdzić na izolowanej magistrali, czy firmware obsługuje `0x60/0x70` z N różnym od 8 (zwłaszcza DLC=3).
- [ ] **P0 / KCAN-D013:** rozstrzygnąć rolę `0x50`/`0x51` w inicjalizacji i recovery; kod 2.5 wysyła oba.
- [ ] **P0 / KCAN-D014:** odnaleźć pełną semantykę `0x54`, `0x6F` i konfiguracji szybkości `0x55` w EXE 2.5.
- [ ] **P0 / KCAN-D016:** zweryfikować na płytce sekwencję DTR 5→6 i RTS 3/4 (stan rzeczywisty, PIC reset, wersje FTDI).
- [ ] **P1 / KCAN-D015:** rozróżnić wersję widoczną „2.5” i zasób `1.0.0.1` od wersji firmware.
- [ ] **P1 / KCAN-D017:** sprawdzić różnice `DIAGNOSTICID`/`FILEINDEX`/podwójne `[CHANNEL]` w INI.
- [ ] **P1:** odtworzyć obsługę CAN29, przepełnienia kolejki i asynchronicznych statusów w tej kompilacji (bez uruchamiania nieznanego EXE).

[Adresy kodu i wyniki analizy 2.5](ANALYSIS_VWTESTER_25_2026-10-23.md).


## Priorytety po drugiej analizie FULL 2.5

- [ ] **P0 / KCAN-D019:** zweryfikować kolejność i bitowe znaczenie 6 filtrów oraz 2 masek w `0x53`; w nowej analizie **6+2 jest potwierdzone konstrukcją EXE**.
- [ ] **P0 / KCAN-D021:** zmapować `50 00` / `51 00` na pozycje CAN/K-Line GUI. Wybór przez `CB_GETCURSEL` jest już potwierdzony.
- [ ] **P0 / KCAN-D022:** opracować tolerancyjny parser PC→PIC, kody odpowiedzi i resynchronizację po błędach.
- [ ] **P1 / KCAN-D020:** oszacować rzeczywistą przepustowość ciągłego RX i nadpisywanie kolejek 2048-slotowych.
- [ ] **P1 / KCAN-D018:** ustalić strukturę innych niż `60 00` odpowiedzi TX CAN, dopuszczonych przez kod hosta.
- [ ] **P1:** dokończyć znaczenie `0x54`/`0x6F`; **wystąpienie w deskryptorze nie dowodzi użycia**. Nadal brak wiarygodnego CAN29 i listen-only.

[Uzupełniająca analiza](ANALYSIS_VWTESTER_25_FOLLOWUP_2026-10-23.md).
