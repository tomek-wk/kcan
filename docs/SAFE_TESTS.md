# Plan bezpiecznej walidacji protokołu

**Cel:** sprawdzić, czy opis z analizy `J2534KCAN.dll` i KCANTEST pasuje do konkretnego niebieskiego K+CAN Commander 1.4. To plan badań, nie skrypt wykonujący polecenia.

## Etap 0 — identyfikacja bez nadawania

1. Sprawdzić oznaczenie USB VID/PID, FTDI, port COM i wersję sterownika. Zanotować wyniki.
2. Obejrzeć obie strony PCB, model PIC, transceiver CAN/K-Line i zasilanie mikrokontrolera.
3. Ustalić wymagane zasilanie układu przez OBD; samo USB może nie zasilać PIC.
4. Nie podłączać adaptera do samochodu na etapie odtwarzania protokołu.

## Etap 1 — obserwacja i rozpoznanie

1. Rejestrować komunikację znanego programu PC ↔ adapter, łącznie z DTR/RTS.
2. Zidentyfikować baudrate/8N1 oraz moment resetu i wpływ zmian stanów linii.
3. Jeżeli bezpieczne i możliwe: rozpoznać znane żądanie `52 00`, nie zakładając zgodności firmware przed testem.
4. Porównać strukturę odpowiedzi z roboczym schematem. W razie różnic przerwać automatyczne wysyłanie.

## Etap 2 — izolowana magistrala testowa

1. Podłączyć adapter do kontrolowanej, terminowanej magistrali CAN z drugim znanym interfejsem, nie do samochodu.
2. Rozpocząć od jednej, powtarzalnej pary ID CAN11 i porównać faktyczne wyniki z logami.
3. Zbadać konfigurację filtrów `0x52/0x53` pojedynczymi kontrolowanymi zmianami i każdorazowym odczytem zwrotnym.
4. Przetestować błędy i saturację RX dopiero po zdefiniowaniu timeoutów i procedury resetu.
5. Osobno sprawdzić, czy adapter generuje ACK oraz czy oferuje tryb *listen-only*.

## Etap 3 — zgodność w szerszym zakresie

- Różne ID 11-bitowe (w tym `0x000`, `0x123`, `0x7FF`).
- Długości danych 0–8, jeżeli protokół pozwoli jednoznacznie je kodować.
- CAN29, dopiero po rozwiązaniu niespójności kodera.
- Różne prędkości CAN i zachowanie po resecie.

## Zasady

- Nie uruchamiać nieznanych EXE/DLL bez izolacji i kontroli bezpieczeństwa.
- Nie wysyłać w ciemno `0x53`, `0x55` i `0x60` do samochodu.
- Odpowiedź `60 00` nie jest dowodem na fizyczny ACK.
- Logi badań i pliki pobrane **nie trafiają do repozytorium**. Dodawać tylko wyniki zanonimizowane/opisowe, małe przykłady HEX, hashe i linki.


---

## Testy porównawcze zgłoszone przez analizę oryginalnego pakietu

1. **Nie uruchamiać otrzymanego EXE ani starych instalatorów USB bez analizy bezpieczeństwa i izolacji.** Rozpoznanie importów spakowanego programu nie jest oceną bezpieczeństwa.
2. Test **KCAN-D001** (oznaczenia wersji): porównać zasoby plików kolejnych wersji i identyfikację adaptera w ich legalnie przechwyconych sesjach, aby ustalić, czy nazwa `1.4` dotyczy aplikacji czy firmware.
3. Test **KCAN-D003** (dongle): na wyłączonym układzie sprawdzić oznaczenia posiadanego interfejsu i konfigurację USB, a ewentualne żądania klucza porównywać wyłącznie w kontrolowanym środowisku; **nie obchodzić zabezpieczeń**.
4. Test **KCAN-D004** (transport): zarejestrować ewentualne wywołania wirtualnego COM i D2XX, stany RTS/DTR oraz faktyczne bajty UART, bez zakładania tożsamości protokołu obu programów.
5. Test **KCAN-D005** (CAN11 ID): przy późniejszym uruchomieniu na stanowisku CAN wysłać ID `0x123` i porównać z potwierdzoną funkcją DLL; nie rozstrzygać na podstawie istniejących logów obejmujących wyłącznie `0x7E0/0x7E8`.

Szczegóły i interpretacja stanów: [DISCREPANCIES.md](DISCREPANCIES.md).


---

## Testy wyprowadzone z dokumentacji dystrybucji Setup Factory

- **KCAN-D006** — statyczne wydobycie EXE z instalatora lub pozyskanie niezależnego, legalnego pakietu rozpakowanego; porównanie hashy i tabel komend. Nie uruchamiać nieznanego instalatora dla samego rozpakowania.
- **KCAN-D008** — sprawdzić urządzenie w Menedżerze urządzeń oraz jego rzeczywistą wersję sterownika; PDF podaje FTDI 2.6.0.0, a INF w ZIP 2.04.06.
- **KCAN-D009** — w izolowanym eksperymencie ze stałą sekwencją odczytów porównać ustawienia Latency Timer 1/16 ms i USB TX/RX 512/4096 B, rejestrując pełny TX/RX, liczbę timeoutów i opóźnienia. To parametry sterownika, nie opkody Commandera.
- **KCAN-D010** — zweryfikować zasilanie PIC i transceivera przy podłączeniu **tylko USB** oraz na bezpiecznie przygotowanym zasilaniu laboratoryjnym OBD; nie zakładać, że Viaken i niebieski klon mają tę samą architekturę.


---

## Test KCAN-D011 — duplikaty `[CHANNEL]` i konfiguracja `Tester.ini`

- Najpierw porównać działanie parsera INI (analiza statyczna, jeśli dostępny niechroniony program).
- Jeśli eksperyment z programem jest dopuszczalny po weryfikacji bezpieczeństwa: na **odizolowanym stanowisku, bez samochodu**, porównać widoczny cel i inicjalne komunikaty UART przy `TARGET=0` i `TARGET=6`, zachowując **obie** sekcje `[CHANNEL]`. Każdorazowo notować wersję EXE i stan dongla.
- Oddzielnie porównać zachowanie `[TRACE] FILEINDEX`, aby nie mieszać dziennika programu z protokołem adaptera.
- Ponieważ EXE w obu pakietach jest bitowo identyczny, rozbieżność nie upoważnia do zmiany opkodów w [COMMANDS.md](COMMANDS.md).


---

## Badania wynikające z Commander FULL 2.5

**Wszystkie próby z nadawaniem należy przeprowadzać na osobnej, prawidłowo terminowanej magistrali testowej, nie na samochodzie.**

- **KCAN-D012:** po potwierdzeniu inicjalizacji PC↔PIC wysłać CAN11 `0x123` z N=3 i danymi `11 22 33` w izolowanym układzie. Sprawdzić, czy na rzeczywistej magistrali wystąpił **DLC=3**, a nie osiem bajtów/padding; porównać zapis HEX i timestampy drugiego interfejsu.
- **KCAN-D013/D014:** najpierw obserwować oryginalne komunikaty `50 00`, `51 00` i kody `0x54/0x6F` w legalnej, kontrolowanej sesji testowej; nie zgadywać nieznanych payloadów i nie wysyłać ich w ciemno.
- **KCAN-D016:** zarejestrować wywołania `EscapeCommFunction` oraz rzeczywiste poziomy DTR/RTS; kod 2.5 używa `SETDTR(5)`, `Sleep(500)`, `CLRDTR(6)`, następnie `SETRTS(3)` lub `CLRRTS(4)`. Odłączyć od pojazdu.
- **KCAN-D015/D017:** porównać metadane EXE i INI bez instalowania lub uruchamiania nieznanych programów; późniejsze eksperymenty tylko na izolowanym stanowisku.

Kod 2.5 i hipotezy: [ANALYSIS_VWTESTER_25_2026-10-23.md](ANALYSIS_VWTESTER_25_2026-10-23.md). Testy należą do konkretnej kompilacji/wersji sprzętu, a nie całej rodziny produktów.


## Testy po powtórnej analizie 2.5

- **KCAN-D018 (status odpowiedzi TX):** najpierw rejestrować rzeczywiste odpowiedzi `0x60` podczas poprawnych testów na izolowanej magistrali; osobno testować parser programowo offline dla długości 0–4. Nie prowokować awarii CAN w aucie.
- **KCAN-D019 (filtry 6+2):** odczyt `0x52`, zapis pierwotnego bloku poza GitHub i kontrolowane zmiany pojedynczych pól dopiero na izolowanej magistrali. Porównać akceptowane ID przy każdej zmianie. Znaczenie bitów `0x40`/`0x60` nieustalone.
- **KCAN-D020 (ciągły RX):** podać kontrolowany strumień CAN o znanej liczbie ramek, mierzyć straty i przepełnienie przy różnym obciążeniu oraz, osobno, obecność ACK. Dane pełnych logów pozostają poza repozytorium.
- **KCAN-D021 (tryb):** przechwycić selekcję GUI i odpowiadający opcode `0x50`/`0x51`; nie zakładać mapowania CAN/K-Line przed pomiarem.
- **KCAN-D022 (walidacja):** przygotować testy jednostkowe parsera dla `0x70` długość 4 i 12, odrzucenia 3 i 13, `0x60` długości 0..4 i 5 oraz synchronizacji po śmieciach. Wszystkie te testy można zrobić **bez adaptera i bez wykonywania obcego EXE**.

Szczegóły i adresy kodu: [ANALYSIS_VWTESTER_25_FOLLOWUP_2026-10-23.md](ANALYSIS_VWTESTER_25_FOLLOWUP_2026-10-23.md).
