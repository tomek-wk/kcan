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


---

## Druga analiza statyczna tego samego `VWTester.exe` 2.5 — nowe zagadnienia

| ID | Dotychczasowa dokumentacja / wynik | Nowy dowód | Pytanie i test rozstrzygający | Status |
| --- | --- | --- | --- | --- |
| **KCAN-D018** | Z logów znano tylko odpowiedź `60 00` | Parser `0x4037D0` akceptuje `0x60 length=0..4` | Co oznacza payload długości 1..4 i czy zawiera błędy CAN? Najpierw obserwacja oryginalnego programu na izolowanym stanowisku oraz sztuczne odpowiedzi offline parserowi; bez wywoływania usterek w samochodzie. | **OPEN** |
| **KCAN-D019** | `0x53` ma 32 B, hipoteza 6 filtrów i 2 masek | Kod `0x40E490–0x40E565` tworzy 6×4 B + 2×4 B, `0x419510` ustawia dodatkowe `0x40/0x60` | Czy kolejność to RXF0..5 / RXM0..1? Co oznaczają flagi? Odczyt `0x52`, pojedyncze zmiany `0x53`, weryfikacja akceptacji na izolowanym CAN. | **OPEN — format 6+2 poparty kodem** |
| **KCAN-D020** | Odbiór `0x70` rozpoznano z logów | Wątek `0x40A160`, parser `0x404070`, kolejki 2048×20 B | Czy przy pełnym obciążeniu CAN host lub firmware gubi ramki? Zmierzyć ilość ramek wstrzykniętych i odebranych, przepełnienia oraz ACK na izolowanej magistrali. | **OPEN — architektura hosta potwierdzona** |
| **KCAN-D021** | `0x50`/`0x51` bez przypisania do trybu | Wybór przez `CB_GETCURSEL=0x147` w `0x41AA33–0x41AA5D` | Która pozycja GUI to CAN, a która K-Line? Przypisać nazwy pozycji i przechwycić `50 00` / `51 00` w kontrolowanym środowisku. **Uzupełnia KCAN-D013.** | **OPEN — wybór GUI potwierdzony** |
| **KCAN-D022** | Ogólny schemat pakietów `[opcode,length,payload]` | `0x4037D0` waliduje `0x70` length 4..12, `0x60` 0..4, a inne pakiety z ośmioma deskryptorami; parser próbuje resynchronizacji | Czy konkretne firmware generuje wszystkie warianty; jakie są statusy i recovery? Przechwycenie transmisji + test jednostkowy offline parsera. | **OPEN — reguły hosta potwierdzone** |

Doprecyzowanie: problem `KCAN-D013` pozostaje otwarty tylko co do **semantyki CAN/K-Line na adapterze**; fakt przełączania `0x50/0x51` przez wybór w GUI został ustalony kodem. Żadne z powyższych nie dowodzi trybu *listen-only* bez ACK.

 
## Trzecia analiza VWTester 2.5 — testy KCAN-D023–D028

| ID | Nowy wynik w EXE | Co sprawdzić | Status |
| --- | --- | --- | --- |
| **KCAN-D023** | Po wyborze `50 00` / `51 00` program wysyła kolejno **dwa** bloki `53 20`: stały i adresowy | Przechwycić kolejność, dwie odpowiedzi PIC i wynik `52 00` po każdym zapisie; bez pojazdu | OPEN; kolejność hosta potwierdzona |
| **KCAN-D024** | Blok adresowy używa identyfikatorów CAN **`0x200+x`** (dwa wpisy) oraz **`0x300`** (jeden wpis), maska robocza M0 ma `FF1C00FF` | Zmieniać x tylko na izolowanej magistrali, sprawdzić reakcję RX i dokładne mapowanie masek/filtrów PIC | OPEN; algorytm hosta potwierdzony |
| **KCAN-D025** | `0x42B250` składa 4 formaty K-Line/KWP, w tym `[80+N,target,F1,data,sum]` i `[N,data,sum]` | Określić warunki wyboru wariantów i timeouty transmisji, bez mieszania z protokołem PC↔PIC | OPEN |
| **KCAN-D026** | Parser synchronizacji K-Line `0x42B1B7` wykorzystuje `0x55` i negację bajtu | Zarejestrować fazy inicjalizacji i odpowiedzi urządzenia, nie interpretować jako `55 03` dla CAN | OPEN |
| **KCAN-D027** | Wrapper `0x40A3D0` może zwrócić `1` mimo błędu zakończenia `WriteFile/GetOverlappedResult` | Własny sterownik powinien osobno testować sukces Win32, liczbę zapisanych bajtów, odpowiedź PIC oraz nadawanie CAN | OPEN; ograniczenie EXE rozpoznane |
| **KCAN-D028** | Przy błędnym ustawieniu COM program próbuje `9600` i zwraca błąd inicjalizacji | Czy to tylko procedura przywracająca ustawienia portu; nie wnioskować o pracy PIC z 9600 | OPEN |

Adresy, zawartość obu bloków i ograniczenia: [ANALYSIS_VWTESTER_25_DEEP_2026-10-23.md](ANALYSIS_VWTESTER_25_DEEP_2026-10-23.md). Żadnej z kwestii nie zweryfikowano jeszcze na niebieskim adapterze.


## Czwarta analiza FULL 2.5 — nowe testy KCAN-D029–D035

| ID | Nowy wynik statyczny | Test rozstrzygający | Status |
| --- | --- | --- | --- |
| **KCAN-D029** | `0x42AE00`: 5-baud LSB-first, 8 bitów adresu + start/stop, generowane przez `EscapeCommFunction(8=SETBREAK,9=CLRBREAK)`, okres ~199 ms | Zarejestrować na izolowanej płytce przebieg TXD FTDI i K-Line; zmierzyć okres oraz sprawdzić drogę elektryczną | **OPEN — kod hosta potwierdzony** |
| **KCAN-D030** | **Oddzielna** funkcja `0x434120`: 7 bitów LSB-first + bit parzystości z licznika jedynek, prawdopodobnie odd parity | Porównać tryby z różnych opcji diagnostycznych, pomierzyć wszystkie bity i polaryzację; nie zakładać jednego formatu 5-baud | **OPEN — kod hosta potwierdzony** |
| **KCAN-D031** | `0x42AD62`: szybka sekwencja `CLRBREAK 15, SETBREAK 30, CLRBREAK 22`; odrębne dłuższe wzorce w `0x42B540` | Pomiar rzeczywistych czasów i identyfikacja zastosowania; nie utożsamiać z normą przed pomiarem | **OPEN** |
| **KCAN-D032** | `0x42AFB0–0x42B249`: parser RX K-Line z osobnym przypadkiem `00` i długością `next+3`, eliminacją echa, oraz szczególną obsługą NRC `7F 78` | Symulowany strumień K-Line: rama standardowa, rozszerzona, echo identyczne, odpowiedź `7F ... 78`; porównać eventy i timeouty | **OPEN — mechanizmy hosta potwierdzone** |
| **KCAN-D033** | `0x42B3FC–0x42B40A`: `TransmitCommChar` ponawiane bez lokalnego licznika/limitu czasu | W implementacji własnej wymusić błędy portu na mocku, zapewnić abort i limit prób. Nie powielać potencjalnego zapętlenia hosta | **OPEN — luka hosta zidentyfikowana** |
| **KCAN-D034** | `0x42B575`: ścieżka K-Line otwiera COM przy `0x28E8=10472` bit/s (w przeciwieństwie do UART 833333 dla ścieżek CAN) | Przy symulowanym K-Line odczytać DCB po otwarciu, pomierzyć bitrate i odróżnić inicjalizację 5-baud od transferu danych | **OPEN — kod hosta potwierdzony** |
| **KCAN-D035** | `0x40A543–0x40A56D`: EXE 2.5 obsługuje nazwy `COM%d` dla COM1–9 i `\\.\COM%d` dla COM10+ | Test otwarcia wyższego COM w izolowanej instancji; odróżnić limit starszej instrukcji COM1–4 od zachowania 2.5 | **OPEN — format nazw potwierdzony** |

Pełne adresy i ograniczenia: [ANALYSIS_VWTESTER_25_KLINE_INIT_RX_2026-10-23.md](ANALYSIS_VWTESTER_25_KLINE_INIT_RX_2026-10-23.md).

**Zasada:** funkcje `SETBREAK/CLRBREAK` i diagnostyczne `7F 78` są elementami pracy K-Line, nie nowymi opkodami binarnego protokołu `0x50–0x70`. Żadnej z nowych funkcji nie testowano dotąd na niebieskim adapterze.


## Piąta analiza VWTester 2.5 — wyłącznie CAN (2026-10-23)

Źródło: [ANALYSIS_VWTESTER_25_CAN_FOCUS_2026-10-23.md](ANALYSIS_VWTESTER_25_CAN_FOCUS_2026-10-23.md). Dowody pochodzą z **kodu EXE 2.5**, **nie** z testów adaptera.

| ID | Nowe ustalenie | Test rozstrzygający / zadanie | Status |
| --- | --- | --- | --- |
| **KCAN-D036** | Inicjalizacja filtrów: `0x404270` oczekuje na odpowiedź `0x53`. Ścieżka okna filtrów `0x40E490→0x404300` nadaje ten sam typ bloku **bez bezpośredniego sprawdzenia odpowiedzi**. | Na izolowanym CAN porównać surowe TX/RX obu ścieżek, odpowiedzi `0x53`, wynik odczytu `0x52`; sprawdzić warunek `[object+0x5C]`. Nie wnioskować o aplikacji filtra z samego GUI. | **OPEN**, różnica hosta potwierdzona kodem |
| **KCAN-D037** | Worker TX `0x403DC0` i analog `0x409A80` wywołują **Sleep(10 ms)** po iteracji kolejki 2048 rekordów. | Izolowana magistrala, kontrolowane obciążenie i dwa zegary UART/CAN: porównać throughput i opóźnienia z rzeczywistym wątkiem EXE oraz własnym senderem bez sztucznej pauzy. | **OPEN**, Sleep potwierdzony |
| **KCAN-D038** | Odbiór `0x70` i TX używają historii 20-bajtowych rekordów i indeksów 2048; timestamp `GetTickCount` jest **hostowy**, historia ma mechanizm przesuwania wpisów. | Niezależny logger CAN ze sprzętowymi timestampami, ramki z numerami sekwencji; zmierzyć straty, zmianę kolejności i precyzję czasu, zwłaszcza po nasyceniu UART/GUI. | **OPEN**, architektura hosta potwierdzona |
| **KCAN-D039** | Parser uznaje odpowiedź `0x60 length=0..4`, ale dyspozytor jawnie interpretuje wyłącznie `60 00`, zerując lokalny status. | Obserwować odpowiedzi adaptera na izolowanym CAN, bez prowokowania usterek pojazdu; parser fuzzować wyłącznie offline dla długości 0..4. | **OPEN** |
| **KCAN-D040** | Wyborowi indeksu GUI odpowiada `50 00` lub `51 00`; nie ustalono nazwy opcji CAN dla każdego indeksu ani wpływu na firmware. | Zmapować listę opcji GUI do kodów i rejestrować odpowiedzi, RTS/DTR na laboratoryjnym adapterze. Uzupełnia KCAN-D013/021. | **OPEN** |
| **KCAN-D041** | W tej kompilacji kod `0x52/0x54/0x6F` potwierdzono w deskryptorach, **nie w ścieżkach wykonawczych komend**; `0x55/0x5F` udokumentowano w **innej DLL**. Dosłownej sekwencji `55 03 01 FA 07` nie znaleziono w PE 2.5. | Poszukać produkcji pakietów przez xrefs i w **legalnym, własnym logu PC↔PIC**; nie twierdzić o braku tych funkcji w firmware ani nie wysyłać nieznanych payloadów. | **OPEN** |
| **KCAN-D042** | TX worker kopiuje N bajtów z 20-bajtowego rekordu do lokalnego pakietu, a bezpośrednio w tej funkcji brak jawnej kontroli `N<=8`. RX dopuszcza `0x70 length 4..12`. | Odnaleźć walidację w producentach wiadomości; własne testy/parser fuzz wyłącznie offline dla N=0,8,9,255 i podzielonych pakietów. Na magistrali testować tylko poprawny Classical CAN N<=8. | **OPEN**, brak walidacji dotyczy wyłącznie tej ścieżki |

**Priorytet:** D036 (rzeczywiste potwierdzenie filtrów), D037/038 (przepustowość i straty sniffera), D041 (nieznane opkody), D042 (bezpieczeństwo hosta). **Tryb listen-only bez ACK i CAN29 wciąż niepotwierdzone.**

Następna rozmowa: [HANDOFF_NEXT_CHAT.md](HANDOFF_NEXT_CHAT.md).
