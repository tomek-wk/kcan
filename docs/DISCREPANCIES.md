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
