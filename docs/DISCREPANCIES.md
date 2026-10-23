# Rejestr rozbieżności i testów rozstrzygających

Cel: **nie nadpisywać wcześniejszych danych** przy pojawieniu się różnych wersji firmware, aplikacji lub konstrukcji PCB. Pozycje obejmują zarówno prawdziwe rozbieżności metadanych, jak i potencjalne niezgodności wymagające testów.

Statusy: `OPEN` — niezweryfikowane; `RESOLVED` — wyjaśnione z dowodem; `NOT_A_PROTOCOL_CONFLICT` — różnica nie dotyczy potwierdzonych bajtów protokołu. **Żadnej z poniższych kwestii nie zweryfikowano na konkretnym niebieskim adapterze.**

| ID | Materiał A | Materiał B | Czego nie wiemy | Test / rozstrzygnięcie | Status |
| --- | --- | --- | --- | --- | --- |
| **KCAN-D001** | Nazwa pakietu `1[X].4` | Zasoby EXE `FileVersion=1.0.0.1`, `ProductVersion=1.0.0.1` | Czy to ta sama numeracja? Co mówi o wersji firmware? | Porównać metadane z kolejnymi **różnymi SHA-256** wersjami EXE oraz ewentualną odpowiedzią identyfikacyjną adaptera. Nie wnioskować o firmware z wersji pliku. | OPEN |
| **KCAN-D002** | Plik `VAG-K+CAN Commander.exe` | Nazwa modułu eksportów PE `VWTester.exe` | Czy nazwa pochodzi z ochrony/oryginalnego programu? | Porównać identyczność binariów z innymi kopiami oraz wewnętrzne nazwy kolejnych wersji. **Najpierw analiza statyczna; nie wymaga testu CAN.** | OPEN |
| **KCAN-D003** | Instrukcja pakietu wymaga osobnego dongla USB i interfejsu | Fizyczny niebieski klon użytkownika, zgodność nieustalona | Czy konkretna aplikacja działa z danym adapterem bez drugiego klucza? | Sprawdzić niezależnie identyfikatory USB i PCB; ewentualne zachowanie aplikacji tylko w odizolowanym i uprzednio zweryfikowanym środowisku. Nie obchodzić ochrony. | OPEN |
| **KCAN-D004** | `J2534KCAN.dll` używa Win32 Virtual COM (ustalone z importów) | Oryginalny EXE ma jedynie importy widoczne przez warstwę ochrony; w pakiecie jest także `FTD2XX.dll` | Czy oryginalny EXE komunikuje się z PIC przez COM czy D2XX? | Porównać zachowanie dostępnych implementacji: zarejestrować API i surowe TX/RX, baudrate, stany RTS/DTR na stanowisku bez samochodu. | OPEN |
| **KCAN-D005** | Kodowanie CAN11 wyinterpretowane z DLL | Wszystkie wcześniejsze logi obejmują wyłącznie CAN ID `0x7E0/0x7E8` | Czy dekoder poprawnie działa dla CAN ID z niezerowymi 3 najmłodszymi bitami, np. `0x123`? | Test CAN ID `0x123`, `0x7FF` na odizolowanej magistrali, porównanie nadanych i odebranych bajtów z DLL. | OPEN |

## Zapis wyników przyszłych badań

Dla każdej pozycji po teście dopisać: **model PIC**, oznaczenia PCB, mostek USB, wersję/hashe programu i sterownika, konfigurację COM i DTR/RTS, warunki zasilania, ramki HEX, spodziewany vs faktyczny wynik, datę i interpretację. Ustalenia dotyczące jednej płytki nie stają się automatycznie prawdą dla wszystkich klonów.

### Notatki o statusie

- **2026-10-23:** otwarto KCAN-D001–D005 po otrzymaniu pierwszego archiwum oryginalnej aplikacji. Na razie **żadna z pozycji nie podważa potwierdzonych bajtów komend z J2534/KCANTEST**. Wiele jest rozbieżnościami nazw/wersji lub brakami dowodowymi, nie wykazanymi konfliktami protokołu.
- EXE SHA-256 `ea69c09b51fda25107d9926d7d033f4e25f5374ec0dd2b1bc4a9867a7b19b932` jest **identyczny** z wcześniej zlokalizowanym plikiem na GitHubie (Git blob SHA-1 `daffe47c50f0e6554c91c723f3774aacc6d9b845`), dlatego nie stanowi drugiego niezależnego wariantu do porównań.


## Nowe obserwacje z pakietu 2026-10-23 — `commander vag-k can.zip`

| ID | Materiał A | Materiał B | Pytanie do rozstrzygnięcia | Test | Status |
| --- | --- | --- | --- | --- | --- |
| **KCAN-D006** | Pierwszy pakiet: bezpośredni chroniony `VAG-K+CAN Commander.exe` | Drugi pakiet: instalator `Setup VAG K+CAN COMMANDER 1.4.exe` (Setup Factory 8.0) | Czy wewnętrzny EXE jest identyczny, czy to inna wersja aplikacji/protokołu? | Statycznie wyodrębnić zawartość instalatora, policzyć SHA-256 i zestawić pliki/wywołania portu; do tego czasu **brak dowodu różnicy protokołu**. | OPEN |
| **KCAN-D007** | Dokumentacja pierwszego pakietu mówi o osobnym donglu USB | Polska instrukcja drugiego pakietu opisuje jeden interfejs USB–COM; nie wspomina osobnego dongla | Różne licencje czy różne warianty aplikacji? | Porównać wersje programu i modele dystrybucji, ewentualnie ruch USB na odizolowanym stanowisku. **Brak wzmianki ≠ brak wymogu.** | OPEN |
| **KCAN-D008** | `ftdiport.inf`: `DriverVer=03/13/2008,2.04.06` | Polska instrukcja wymienia FTDI `2.6.0.0` z 22.10.2009 | Które wydanie sterownika rzeczywiście było używane? | Sprawdzić zainstalowany sterownik i zachowanie adaptera. Nie instalować starych sterowników bez konieczności. | OPEN |
| **KCAN-D009** | Pierwszy pakiet podaje FTDI Latency Timer 1 ms | Polska instrukcja: dodatkowo bufory USB RX/TX po 512 B i COM1–4 | Czy bufory i numer COM wpływają na zgodność/timing? | Porównać sesje 512/4096 B, 1/16 ms i różne porty; odróżnić ograniczenie UI od sprzętu/protokołu. | OPEN |
| **KCAN-D010** | Model z Viaken (instrukcja PDF) podaje zasilanie 12,5–15 V przez OBD | Konkretny niebieski egzemplarz nie został zmierzony | Czy PIC działa przy samym USB i z jakiego źródła zasilana jest elektronika CAN? | Pomiar napięć PIC i transceiverów przy kontrolowanych wariantach zasilania na stanowisku, bez auta. | OPEN |

**Uwaga metodologiczna:** nie wykryto nowej sprzeczności w kodowaniu bajtów `0x52/0x53/0x55/0x60/0x70`, ponieważ nowe materiały nie pokazują niskopoziomowej transmisji. Są to kwestie dystrybucji, sterowników i sprzętu.


## KCAN-D011 — różne ustawienia w `Tester.ini` pakietów tego samego EXE

| ID | Materiał A | Materiał B | Pytanie | Test rozstrzygający | Status |
| --- | --- | --- | --- | --- | --- |
| **KCAN-D011** | `VAG-K_CAN_Commander_1[X].4.zip`: pierwsze `[CHANNEL] TARGET=0`, `[TRACE] FILEINDEX=3221` | `VAG K CAN COMMANDER FULL 1.4.zip`: pierwsze `[CHANNEL] TARGET=6`, `[TRACE] FILEINDEX=1956` | Pliki mają także **drugie `[CHANNEL] TARGET=0`**: która wartość jest stosowana i czy wpływa na komunikację? | Analiza parsera konfiguracji w innej wersji programu; ewentualnie test porównawczy widocznego celu i pierwszych ramek PC↔PIC, wyłącznie na odizolowanym stanowisku; niezależna obserwacja indeksu logów. | **OPEN** |

**Ważne:** identyczne binaria EXE i DLL potwierdzają, że różnice w `Tester.ini` nie są dowodem istnienia nowej komendy protokołu ani nowej wersji firmware. [Dowody](ANALYSIS_FULL14_2026-10-23.md).


---

## Nowe różnice wykryte w kodzie Commandera FULL 2.5

| ID | Ustalenie A | Ustalenie B | Co należy rozstrzygnąć | Plan testu | Status |
| --- | --- | --- | --- | --- | --- |
| **KCAN-D012** | `J2534KCAN.dll` i wszystkie logi KCANTEST korzystają z `0x60/0x70` z **N=8** | `VWTester.exe` 2.5 oblicza `L=N+4` dla nadawania i `N=L-4` dla odbioru | Czy firmware obsługuje fizyczne ramki CAN DLC 0–7 oraz czy uzupełnianie do 8 jest właściwością aplikacji J2534? | Na odizolowanej magistrali, po zweryfikowaniu inicjalizacji, spróbować `N=3`, ID `0x123`, payload `11 22 33`; porównać odczyt niezależnym interfejsem, DLC i odpowiedź Commandera. Najpierw obserwacja znanego EXE bez pojazdu. | **OPEN — różnica hosta potwierdzona** |
| **KCAN-D013** | Starszy rejestr `0x50` opierał się jedynie o zewnętrzne logi; `0x51` nie był udokumentowany | EXE 2.5 wysyła `50 00` i `51 00`, weryfikuje opkod odpowiedzi | Jakie funkcje mają oba kody, czy są zależne od kolejności i wersji firmware? | Obserwować sesję inicjalizacji 2.5 i identyfikować odpowiedzi; bez automatycznego nadawania do auta. | **OPEN** |
| **KCAN-D014** | Funkcja `0x5F` znana z J2534; zestaw opkodów niepełny | EXE 2.5 inicjalizuje `0x54` oraz `0x6F` obok `0x50–0x53/0x60/0x70` | Czy są to funkcje sterowania CAN, potwierdzenia lub zdarzenia? | Kontynuować deasemblację dyspozytora; następnie porównać odczytane bajty z własnego logu PC↔PIC. | **OPEN — znaczenie nieustalone** |
| **KCAN-D015** | Oznaczenie dystrybucji „Commander FULL 2.5” | Zasób VERSIONINFO w EXE 2.5 nadal `FileVersion=1.0.0.1` | Który numer oznacza produkt, kompilację, firmware? | Porównać SHA-256 i zasoby kolejnych wersji; sprawdzić odpowiedź identyfikacji adaptera, jeśli istnieje. Powiązane KCAN-D001. | **OPEN** |
| **KCAN-D016** | Polaryzacja DTR/RTS i reset dla konkretnego PCB pozostają nieznane | EXE 2.5 wykonuje `SETDTR`, 500 ms, `CLRDTR`, potem `SETRTS` albo `CLRRTS` | Jaki skutek ta sekwencja ma na konkretnym niebieskim klonie? | Pomiar analizatorem logicznym stanów DTR/RTS na FTDI i resetu/sterowania PIC w kontrolowanym zasilaniu, bez auta. | **OPEN** |
| **KCAN-D017** | INI FULL 1.4: `TARGET=6`, `DIAGNOSTICID=1761195548`, `FILEINDEX=1956` | INI FULL 2.5: `TARGET=0`, `DIAGNOSTICID=-674897751`, `FILEINDEX=1802` | Które parametry pochodzą z programu, które są zmienne użytkownika i czy mają wpływ na protokół? | Prześledzić parser INI / przygotować porównawcze logi na izolowanym stanowisku. Powiązane KCAN-D011. | **OPEN** |

**Uwaga:** różnice KCAN-D012–D017 są na razie udokumentowane kodem lub plikami programu, **nie pomiarem adaptera**. Nie zakładać, że ten sam firmware działa ze wszystkimi dystrybucjami. Pełne miejsca kodu: [ANALYSIS_VWTESTER_25_2026-10-23.md](ANALYSIS_VWTESTER_25_2026-10-23.md).
