# HUD ECU Hacker 6.1 — maszyna stanów RX Commandera (analiza kontynuacyjna)

Data: **2026-10-24**. Źródło: użytkownik dostarczył `HUD-ECU-Hacker v6.1(1).zip`, statycznie wydobyty `ECU_Hacker.exe` SHA-256 `b70fa891953927da0600eac420d18acdc15a39bdba25dad366e1c52a602eeeb8`. Poprzednie dowody: [pełny koder CAN11/CAN29](ANALYSIS_HUD_ECU_HACKER_61_CODEC_RX_FOLLOWUP_2026-10-24.md) oraz [rozkodowane komendy](ANALYSIS_HUD_ECU_HACKER_61_PROTOCOL_2026-10-24.md).

**Cel:** odtworzenie rzeczywistego odbioru `0x70`, przeplatania wiadomości i obsługi błędów w protokole PC↔VAG K+CAN Commander. **Nie badano innych adapterów CAN. Nie uruchamiano EXE ani nie korzystano z interfejsu w samochodzie**.

## Metoda i zakres wiarygodności

Rozszerzono własny interpreter wybranych instrukcji ECMA-335 IL i wykonano **RID 3650 (RVA 0x2CAE80, IL 1253 B)** z kontrolowanymi atrapami portu szeregowego, timera, list bajtów, kolejki pakietów i wywołań pomocniczych. Sprawdzono także wykonywanie **RID 3652 (RVA 0x2CB41C, IL 369 B)**. Jest to emulacja **logiki hosta**, z nadzorowanymi stubami metod transportowych **RID 2688/2694** i obsługi czasu; zatem **nie jest** symulacją firmware PIC, błędów fizycznych ani wszystkich szczegółów czasu rzeczywistego.

Istotna naprawa własnego narzędzia analitycznego: w pierwszym modelu `List.Clear` było błędnie traktowane jako no-op; poprawiono to na rzeczywiste czyszczenie. Dopiero po tej poprawce scenariusze interleavingu przeszły poprawnie i nie wpadały w sztuczną pętlę. Tego błędu narzędzia **nie wolno przypisywać aplikacji HUD**.

## 1. Dwuetapowy framing UART

`RID3650` odbiera `opcode,length` (2 bajty), następnie oczekuje **`length` bajtów danych** i traktuje całość jako `length + 2` bajty. Szczegółowe ścieżki IL:

- `0x0343–0x0354`: odczyt początkowych 2 bajtów przez transport `RID2694`.
- `0x014A–0x0151`: `length = buffer[1]`.
- `0x010E–0x0112`: wyliczenie `total = length + 2`.
- `0x02B0–0x02C2`: próba uzupełnienia bufora do `total`.
- `0x02EA–0x02F2`: `opcode = buffer[0]`.
- `0x0192–0x01B9`: dla `0x70` dekoduje CAN ID/RTR (od offsetu 2) i bierze dane od offsetu 6.
- `0x00EE–0x00FB`: gotowy obiekt CAN dodawany do kolejki `FieldDef 0x04000864`.

W modelu poprawnie działa odczyt nagłówka, odczyt brakującej reszty i wrzucenie ramki CAN11 ID `0x123` + danych `11 22 33`:
`70 07 24 0C 00 00 11 22 33`.

**UWAGA:** metody wewnętrznego odczytu portu `2694/2695` mają dodatkową logikę timeoutów i pobierania częściowych danych. Symulowany odczyt pełnej wiadomości nie wyznacza rzeczywistego czasu między bajtami ani liczby wywołań `SerialPort.Read`.

## 2. Przeplatanie odbioru CAN i odpowiedzi na komendy — wynik przełomowy

Scenariusz testowy (wszystkie bajty to sztucznie przygotowany strumień):

```text
oczekujemy odpowiedzi na 0x54
70 04 24 0C 00 00      # CAN11 ID 0x123, zero danych
70 04 24 0C 00 00      # kolejna ramka CAN
54 02 AA BB            # wreszcie odpowiedź 0x54
```

Emulator RID3650:
1. Pobiera pierwszą wiadomość `0x70` i dodaje CAN ID 0x123 do kolejki.
2. **Nie zwraca jej jako odpowiedzi `0x54`**; czyści bufor wiadomości i pobiera drugą `0x70`, również dodając do kolejki.
3. Po pobraniu `54 02 AA BB` **zwraca dokładnie `54 02 AA BB`**. Kolejka zawiera dwie ramki CAN.

Analogicznie `0x70` przed odpowiedzią `0x55` zostaje zbuforowane, a `55 00` poprawnie kończy oczekiwanie.

**Implikacja:** aplikacja potrafi obsługiwać ruch asynchroniczny w czasie synchronicznych wywołań konfiguracji — nie potrzeba dwukrotnie otwierać portu. **Nie dowodzi to zerowej utraty ramek** przy większym ruchu: nie przeanalizowano przepustowości PIC↔USB ani ograniczeń wielkości kolejki.

## 3. Asynchroniczne `0x60` nie blokuje odpowiedzi sterującej

Dla danych `60 00 54 02 11 22` i oczekiwanego `0x54`, RID3650 pomija wiadomość `60 00` i **zwraca `54 02 11 22`**. Przesłane osobno wiadomości `60 length=0..7` przed `0x54` również były pomijane (ograniczenia długości omówione niżej).

Wcześniej `RID3649` potwierdził, że **nadanie komendy TX `0x60` nie czeka synchronicznie na odpowiedź** w tej metodzie. W połączeniu z parserem wyjaśnia to, dlaczego odpowiedź/status `0x60` nie musi zakłócać odbioru `0x54/0x55`. **To nie jest potwierdzenie fizycznego ACK na CAN**.

## 4. Wymuszony zakres długości RX

Emulowano **`0x70` dla kolejnych wartości pola długości 0..15**, z dopasowanym ładunkiem.

| length | Wynik RID3650 |
| --- | --- |
| 0–3 | **rzuca wyjątek**, bo nie ma pełnego czterobajtowego pola CAN ID |
| 4–12 | **akceptuje**, dekoduje 4-bajtowy ID + 0..8 bajtów danych; kolejkuje ramkę |
| 13–15 | **rzuca wyjątek po odczycie nagłówka**, zanim zaakceptuje dalszy payload |

`0x70` ma **minimum 4 bajty pola CAN ID**, a `total=length+2` nie przekracza **14 bajtów UART**. Dotyczy to **Classic CAN** i spójnie zgadza się z parserami starszych wersji Commandera. Nie wynika z tego obsługa CAN FD, DLC>8 ani dowolnych wiadomości większych niż 14 bajtów.

Inne odpowiedzi, np. `54 02 XX YY`, `55 00`, `53 00`, są przyjmowane dla zgodnego oczekiwanego opcode.

## 5. Nieoczekiwane opcode i błąd synchronizacji

Dla `99 02 01 02 54 02 11 22` przy oczekiwaniu na `0x54` metoda:
- odczytuje pełną nieoczekiwaną wiadomość `0x99`,
- wchodzi w ścieżkę diagnostyczną (m.in. wywołuje transport `RID2688`),
- **rzuca wyjątek** zamiast zaakceptować następne `0x54`.

Podobne wyniki dla innych nieoczekiwanych opkodów 0x00, 0x4C, 0x4D, 0x53, 0x55, 0x58, 0x99 przy oczekiwanym `0x54`; **wyjątkami specjalnymi są `0x70` i `0x60`**, które są przetwarzane jako wiadomości przeplatane.

W nagłówku metody .NET **RID3650 flagi `0x13` nie mają `MoreSects`**: nie posiada własnej tablicy obsługi wyjątków; **RID3652 również nie ma takich sekcji**. Obsługa błędu może występować w wyższej warstwie, której tu nie badano. **Nie znaleziono dowodu automatycznej resynchronizacji strumienia po uszkodzonym bajcie w samej RID3650.** Nie należy z tego wnioskować, że cała aplikacja zawsze się zatrzymuje.

## 6. Co robi metoda pobrania ramki RID3652?

W dodatkowej symulacji `RID3652`, na podstawie `Environment.TickCount` (RID3664) oraz `Math.Abs` (RID3665), ustalono:

- Jeśli różnica od ostatniego zapamiętanego sprawdzenia statusu (`FieldDef 0x04000863`) osiągnęła **2000 ms**, metoda **wywołuje RID3654 / polecenie 0x54** z flagą argumentu `true`.
- Jeśli kolejka CAN ma już element, pobiera **pierwszy element** i usuwa go z listy `FieldDef 0x04000864` — FIFO.
- Jeśli kolejka jest pusta, przy aktywnym adapterze i dodatnim pozostałym czasie wywołuje **`RID3650(expected=0x70, timeoutRemaining)`**. Odbiór dopisuje CAN do kolejki i dopiero potem ten sam kod przekazuje go użytkownikowi.
- Wejściowy `RID3654` przesyła `54 00`, a dwa bajty `response[2]` i `response[3]` zachowuje w polach `0x861/0x862`. Ich bity są dalej sprawdzane, np. `0x40` pierwszego bajtu i `0x04/0x08/0x10/0x20/0xC0` drugiego, ale **nazw flag / semantyki zdarzeń nie rozszyfrowano**.

**Uściślenie:** 2000 ms to warunek okresowego wywołania funkcji statusu, **nie częstotliwość żądania pojedynczych ramek CAN**; dane `0x70` pojawiają się asynchronicznie i nie wymagają pytania `0x54` o każdą ramkę.

## 7. Artefakt do testów offline

Nowy skrypt **[`tools/hud_kcan_rx_parser.py`](../tools/hud_kcan_rx_parser.py)**:
- buforuje dowolne porcje bajtów z UART;
- rozpoznaje `[opcode,length,payload]`, waliduje zakres długości, kolejkuje `0x70`;
- pozwala odebrać odpowiedź sterującą **bez utraty przeplatanych ramek `0x70`**;
- pomija `0x60` pojawiające się jako osobna wiadomość przed inną oczekiwaną odpowiedzią;
- przyjmuje tryb CAN11/29 jawnie, używa odwrotnego kodera w `tools/hud_kcan_codec.py`;
- dla nieoczekiwanego opcode / błędnej długości jawnie rzuca wyjątek, **zamiast udawać potwierdzony mechanizm odzysku synchronizacji**;
- **nie otwiera portu szeregowego**, nie kontaktuje się z urządzeniem, nie wykonuje testów na samochodzie.

Skrypt testowano na przypadkach: fragmentacja nagłówka i payloadu, dwie `0x70` przed odpowiedzią `0x54`, pomijanie `0x60`, odbiór CAN29 (po stronie hosta), błędne długości, nieoczekiwany opcode. Wszystkie testy offline zakończyły się powodzeniem.

## 8. Ryzyka i dalsza praca

1. **Niepotwierdzona semantyka flag `0x54`**: obie maski bajtów statusu wymagają odtworzenia komunikatów lub statycznej analizy `RID3654`. To może dostarczyć diagnozy przeciążenia, ale na razie **nie ma dowodu**.
2. **Gubienie ramek / limit kolejki:** HUD przechowuje odebrane ramki w zarządzanej liście; bez badania jej limitu i zachowania MCU brak gwarancji bezstratności.
3. **Resynchronizacja:** własna implementacja może korzystać z polityki świadomego resetu parsera / flush portu po błędzie, ale **nie wolno dopisywać jej jako zachowania HUD ani firmware**, dopóki nie zostanie udowodniona.
4. **Czas rzeczywisty:** symulacja podaje bajty natychmiast i używa atrap transportu. Dokładna semantyka timeoutów i pracy przy częściowych pakietach nadal wymaga analizy RID2695 lub pomiaru na sprzęcie.
5. **ACK / listen-only:** niezależnie od rozpoznanych komunikatów, HUD w dokumentacji stwierdza, że **dla VAG K+CAN nie może wyłączyć ACK**, więc „show all filters” nie jest pasywnym trybem.

### Konkluzja

**Parser HUD 6.1 umie przeplatać asynchroniczne `0x70` i `0x60` z odpowiedziami na polecenia synchroniczne, utrzymując kolejkę FIFO.** Zidentyfikowano granice długości, 2-sekundowe sondowanie statusu i ścieżki błędów. **Nie dowiedziono bezstratności, sprzętowego CAN29, wyłączenia ACK ani automatycznej resynchronizacji po korupcji UART.**
