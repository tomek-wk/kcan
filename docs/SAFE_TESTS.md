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
