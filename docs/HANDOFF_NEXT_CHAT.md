# HANDOFF — kontynuacja badań K+CAN w nowym czacie

**Stan:** 2026-10-23, po **piątej** analizie `VWTester.exe` 2.5 (tym razem tylko CAN). **Ten dokument jest przeznaczony do przekazania kontekstu kolejnej rozmowie.**

## Cel użytkownika i zasady pracy

Badanie protokołu pomiędzy **aplikacją PC a interfejsem VAG K+CAN Commander** (USB/FTDI ↔ UART ↔ PIC), w szczególności zastosowanie niebieskiego Commandera jako interfejsu CAN do własnych projektów diagnostycznych/sniffera. Wcześniejszy, odrębny projekt samochodowy to `PSA-comm`; repo `kcan` jest **bazą dokumentacji protokołu adaptera**, nie miejscem na binaria.

**Bezwzględna decyzja użytkownika:** nie commitować **żadnych otrzymanych/pobranych ZIP/RAR/EXE/DLL/PDF, surowych logów ani firmware**. Wolno commitować tylko autorskie Markdown, krótkie przykłady HEX, wyniki i metadane/SHA, linki. Nie uruchamiać niesprawdzonych EXE/DLL. Nowy czat ma przeanalizować **następny archiwalny plik**, który użytkownik prześle, porównać z niniejszą bazą i **dopisać rozbieżności do testów** zamiast nadpisywać wcześniejsze wnioski.

**Aktualne repo użytkownika:** https://github.com/tomek-wk/kcan (gałąź `main`, użytkownik pozwolił bezpośrednio zapisywać dokumentację). Po zakończeniu tego etapu wszystkie wyniki mają być już zapisane w GitHubie, nie trzeba pytać ponownie o miejsce docelowe.

## Materiał już przeanalizowany

| Archiwum / komponent | SHA-256 | Wynik |
| --- | --- | --- |
| `J2534KCANv1.0.0.10.zip` | `3f3a28acc6fea0feaac4da68f54f50109fc245b00b77da88355aa81050187f1d` | J2534/KCANTEST: potwierdzone z kodu i logów `0x52/0x53/0x55/0x60/0x70` |
| `J2534KCAN.dll` | `3b8cc66f95a174a0a3b5c94a5a8976e34c5211798dbdfd8105903038fd2bf09b` | UART 833333, CAN bitrate `55 03 01 FA 07` dla 500 kbit/s, 32-bajtowy blok filtrów |
| `VAG-K_CAN_Commander_1[X].4.zip` | `6912218b24524ae629f7ccfa77599aca3823132ea77e42e0145f155a32852028` | Oryginalny chroniony/spakowany Commander 1.4 |
| `VAG-K+CAN Commander.exe` 1.4 | `ea69c09b51fda25107d9926d7d033f4e25f5374ec0dd2b1bc4a9867a7b19b932` | **Identyczny bajtowo** w oryginalnym ZIP, pakiecie FULL 1.4 i publicznym GitHub Skylakc; `ASPack/EXECryptor` |
| `commander vag-k can.zip` | `5ee88477ab1e7b691b20119a44ce1298c122dcaba7713f17ca98ad90a644c7cf` | Inna **dystrybucja/instalator Setup Factory 8.0**, nie udało się statycznie wydobyć właściwego EXE; polskie instrukcje FTDI VCP, opóźnienie 1 ms |
| `VAG K CAN COMMANDER FULL 1.4.zip` | `05f138209fb36a97fbb299213ec4e97376c6980887f867836dc9e7b1cca048d1` | **Ten sam EXE i DLL**, różnice tylko w `Tester.ini` (np. `TARGET`, `FILEINDEX`) |
| **`k+can2.5(1).zip`** | **`9018525b61f96a23166dcfa8dcff502154bd95b15084c9b24ba39707d3af9835`** | **Pierwszy nowy, czytelniejszy EXE FULL 2.5** |
| **`VWTester.exe` FULL 2.5** | **`b90fc612decb04759a77fd0f02946157d832053186c7adf5e50624a1b103a10d`** | 688128 B, kod x86 Win32; wielokrotna statyczna analiza, patrz poniżej |

W pakietach FULL 1.4 i FULL 2.5 `RCMicroDogSetup.dll` jest bajtowo identyczne (SHA-256 `5671711caf7446ce3496028375156cf4443c12311ac4e75c626dd740652d8ef4`). **To nie dowodzi zgodności firmware ani użycia drugiego dongla w każdej płytce.**

W pięciu wcześniej analizowanych logach KCANTEST: **4081 TX `0x60` i 4081 RX `0x70`**, jedynie ID CAN11 `0x7E0/0x7E8`. Wnioski z logów nie dowodzą CAN29, listen-only ani pełnej diagnostyki.

## Potwierdzony **kodem hosta** protokół CAN (nie sprzętem)

```text
PC↔PIC UART: Win32 Virtual COM, 833333 bps w zbadanej ścieżce CAN.
Ramka protokołu: [opcode:u8][payload_length:u8][payload].

TX CAN11:
  60 (N+4) SIDH SIDL 00 00 [N bajtów]
RX CAN11:
  70 (N+4) SIDH SIDL 00 00 [N bajtów]

SIDH = (CAN_ID >> 3) & 0xFF
SIDL = ((CAN_ID & 7) << 2)
CAN_ID = (SIDH << 3) | ((SIDL >> 2) & 7)
N = 0..8 w parserze RX programu 2.5
```

Kodowanie CAN11 sprawdzono też **offline** dla wszystkich 2048 ID (2048/2048 zgodnych). TX `0x60` i RX `0x70` obsługują zmienną długość danych po stronie EXE 2.5; wcześniej obserwowano w J2534 głównie N=8.

Inne kody:
- `50 00` / `51 00` — dwa warianty inicjalizacji wybierane przez **indeks opcji GUI**, mapowanie do nazw CAN/K-Line **nieustalone**.
- `53 20 [32 B]` — zapis konfiguracji, **6 wpisów po 4 B + 2 wpisy po 4 B**; host ma **dwie drogi nadawania** o różnej kontroli potwierdzenia.
- `52 00` — odczyt bloku 32 B **potwierdzony w starszej DLL i logach**, lecz **nie odnaleziono jednoznacznego wykonawczego wywołania w zbadanych ścieżkach EXE 2.5**.
- `55 03 01 FA 07` — konfiguracja CAN 500 kbit/s **z DLL J2534**, niepotwierdzona ścieżka wykonawcza EXE 2.5.
- `5F 00` — tylko rozpoznane w DLL J2534, znaczenie nieustalone.
- `0x54`, `0x6F` — w deskryptorach/buforach EXE, **nie przypisywać semantyki bez ścieżki nadawania**.
- Odpowiedź `60 00` zeruje stan hosta, **nie dowodzi fizycznego ACK CAN**. Parser EXE 2.5 dopuszcza odpowiedzi `60 length=0..4`, ale dodatkowe statusy pozostają nieznane.

### Odkrycia specyficzne dla piątej analizy CAN

Główny raport: **[ANALYSIS_VWTESTER_25_CAN_FOCUS_2026-10-23.md](ANALYSIS_VWTESTER_25_CAN_FOCUS_2026-10-23.md)**.

- `0x404270` — zapis inicjalizacyjny `0x53`, **oczekiwanie do 100 ms** i sprawdzenie opcode odpowiedzi.
- `0x40E490` → `0x404300` — ścieżka ustawiania filtrów z GUI: 6 filtrów i 2 maski, **bez bezpośredniego czekania na odpowiedź `0x53`**. Ważna różnica semantyki błędów.
- `0x403DC0` i `0x409A80` — odrębne workery TX, 20-bajtowe rekordy, kolejka 2048 slotów (`&0x7FF`), `Sleep(10 ms)` po każdej iteracji pętli.
- `0x403850` i `0x409500` — odrębne ścieżki CAN RX; parser `0x4037D0` akceptuje `0x70 length 4..12`; asynchroniczny odczyt z COM buforem 1024 B (`0x40A160`).
- **Czasy `GetTickCount` hosta**, brak dowodu sprzętowych znaczników PIC ani gwarancji bezstratnej kolekcji; kolejki RX przy przepełnieniu nadpisują/przesuwają odczyt.
- W ramach tego EXE **nie wykazano** CAN29, listen-only bez ACK, raportowania bus-off, fizycznych błędów CAN ani mapy kodów statusu.

### Konfiguracje `0x53`

Z [FILTERS.md](FILTERS.md):
- Dwa kolejno zapisywane bloki inicjalizacyjne: stały i zależny od jednobajtowego `x`.
- Stały: F0–F5 = `FF 1C 00 00`, M0 = `FF 1C 00 FF`, M1 = `FF 1C 00 00`.
- Zależny od x: F0 i F5 kodują `CAN_ID=0x200+x`; F4 koduje `0x300`; pozostałe jak w bloku stałym.
- **UWAGA:** nazwy F0–F5, M0–M1 są hipotezą mapowania na rejestry PIC, nie pomiarem na sprzęcie. Znaczenia `FF 1C`, maski M0, wyboru x nie wyjaśniono fizycznie.

## Aktualny porządek dokumentacji

- [README.md](../README.md) — indeks i zasady.
- [PROTOCOL.md](PROTOCOL.md) — formaty UART i CAN.
- [COMMANDS.md](COMMANDS.md) — rejestr komend ze statusem.
- [FILTERS.md](FILTERS.md) — 32-bajtowe bloki konfiguracji i hipotezy.
- [EVIDENCE.md](EVIDENCE.md), [SOURCES.md](SOURCES.md) — źródła i SHA.
- [ANALYSIS_VWTESTER_25_2026-10-23.md](ANALYSIS_VWTESTER_25_2026-10-23.md) — pierwsza deasemblacja 2.5.
- [ANALYSIS_VWTESTER_25_FOLLOWUP_2026-10-23.md](ANALYSIS_VWTESTER_25_FOLLOWUP_2026-10-23.md) — parser, kolejki, GUI.
- [ANALYSIS_VWTESTER_25_DEEP_2026-10-23.md](ANALYSIS_VWTESTER_25_DEEP_2026-10-23.md) — dwa bloki filtrów i dodatkowe szczegóły.
- [ANALYSIS_VWTESTER_25_CAN_FOCUS_2026-10-23.md](ANALYSIS_VWTESTER_25_CAN_FOCUS_2026-10-23.md) — **ostatnia, CAN-only** analiza.
- [DISCREPANCIES.md](DISCREPANCIES.md) — rejestr testów `KCAN-D001`–`KCAN-D042`.
- [SAFE_TESTS.md](SAFE_TESTS.md) — zasady laboratoryjne. **Nie wysyłać przypadkowych konfiguracji `0x53` ani nieznanych rozkazów do auta.**

Starsze analizy K-Line są osobno, m.in. [ANALYSIS_VWTESTER_25_KLINE_INIT_RX_2026-10-23.md](ANALYSIS_VWTESTER_25_KLINE_INIT_RX_2026-10-23.md); nie mieszać ich z rozkazami PIC/CAN. Użytkownik w ostatnim zadaniu **polecił skupienie tylko na CAN**.

## Początek kolejnego czatu — instrukcja operacyjna

Użytkownik zapowiedział **następny plik w nowym czacie**. Gdy go prześle:

1. Przeczytać **ten handoff** i powiązany najnowszy raport CAN z repo `tomek-wk/kcan`; w razie potrzeby sprawdzić aktualną gałąź `main` przed zapisem.
2. Zinwentaryzować archiwum i policzyć rzeczywiste SHA-256, szczególnie głównego EXE/DLL. Porównać z powyższymi znanymi wersjami. **Inna nazwa ZIP ≠ inna kompilacja**.
3. Statycznie przeanalizować nową binarkę (PE imports, sekcje, packer, bez uruchamiania); śledzić **konstrukcję i odczyt wiadomości protokołu**. Oddzielić CAN11, CAN29, CAN bitrate, filtry, ACK/listen-only, komendy PIC, timeouty i recovery.
4. W razie rozbieżności zachować oba warianty i dopisać **nowy test z identyfikatorem KCAN-D0xx** do [DISCREPANCIES.md](DISCREPANCIES.md), z warunkami rozstrzygającymi. Nie ogłaszać potwierdzenia hardware, jeśli dowód pochodzi tylko z EXE.
5. **Commitować wyłącznie raporty Markdown i metadane**, weryfikować GitHub po zapisie. **Nie commitować otrzymanych ani pobranych plików**.
6. W odpowiedzi wskazać nowe, sprawdzone ustalenia, otwarte pytania i linki do konkretnego commita. Nie rozpoczynać pracy nad nowym plikiem bez załącznika użytkownika.

**Priorytet z perspektywy przyszłych testów:** fizyczny model niebieskiego adaptera i zasilanie, `52 00` read-only po inicjalizacji, dwa różne tryby wysyłania `0x53`, CAN11 z N=3 vs N=8 i niezależnym DLC, TX/RX przy obciążeniu, ACK/listen-only, CAN29 i rozkazy `0x54/0x6F`. Testy tylko na odizolowanym stanowisku CAN, nie na samochodzie.

## Uzupełnienie stanu: zainstalowany Commander 1.4 (2026-10-23)

Po piątej analizie 2.5 użytkownik przesłał `VAG K+CAN COMMANDER 1.4zainstalowany.rar` (SHA-256 `8f76b5f4e1b420878e159b42f83367e7a4586c826cae3d5319715268409fdbd2`). Zainstalowany EXE 1.4 i DLL są **identyczne bajtowo** z już opisanymi plikami (hashe w tabeli powyżej). Metadane deinstalacji podają `Setup VAG K+CAN COMMANDER 1.4.exe` jako źródło, co **częściowo przybliża KCAN-D006**, bez bezpośredniej ekstrakcji oryginalnego instalatora. `Tester.ini` zawiera `FILEINDEX=1955` względem `1956` dla wcześniejszego FULL 1.4; aktualizacja **D011**. Bez nowych opkodów, bez pomiaru CAN. Raport: [ANALYSIS_INSTALLED14_2026-10-23.md](ANALYSIS_INSTALLED14_2026-10-23.md).

Dalsze zadanie zależy od kolejnego materiału lub badań laboratoryjnych. Przy przyszłym porównywaniu instalatorów nie publikować lokalnych ścieżek, danych konta ani surowego XML deinstalatora.

## Uzupełnienie stanu: VWTOOL / VDS-PRO 2.09 (2026-10-23)

Kolejny otrzymany plik: `VWool 2 0 9 en PL.rar` (SHA-256 `70b992d60f4b5cc014b30bca9fb6840ac213e883a7fd9378d92745e568a9079d`). Zawiera `VWTOOL.EXE` i polski `VWTOOL-pl.EXE` (po 99121 B, różne SHA-256), `CONFIGVW.EXE`, `DATAVIEW.EXE`, komponenty VB3 i dwa kodowane pliki danych. Jest to **stara diagnostyka szeregowa VAG ISO/K-Line, nie kolejna wersja Commandera**. Zidentyfikowano kodowanie `ERRCODE4.CSV` i `LABELS.CSV`: XOR `0x85` dla bajtów poza CR/LF. Baza etykiet zawiera **569 sześciopolowych rekordów**, baza błędów **1194 dwupolowych pozycji** (plus wiersze opisowe). `VWTOOL.INI` ma `CommPort=2`; `CONFIGVW` umożliwia COM1–4. Nie wynika z tego zgodność z niebieskim adapterem ani nowe komendy PC↔PIC CAN.

Pełny raport: [ANALYSIS_VWTOOL_209_2026-10-23.md](ANALYSIS_VWTOOL_209_2026-10-23.md). Dokumentację `PROTOCOL.md` i `COMMANDS.md` oraz istniejące testy CAN pozostawiono bez zmian; nie utworzono `KCAN-D043`. W przyszłości nie mieszać starych ramek ECU ISO/K-Line z rozkazami mikrokontrolera Commandera.

## Uzupełnienie stanu: Polski VAG 4.9 (2026-10-23)

Dostarczono `Polski VAG 4.9(1).rar` (SHA-256 `3febfd5015830fb6626134f6e13fed107f09ff2d7544e36ad244e4102d0c8e7f`). RAR4 zawiera **jeden `setup.exe`**, SHA-256 `132d7d275a1b3a406a963f1a625a3ceb4bea174ea1a5b22135f4720d8db6046e`, CRC zgodny. Stub to **PE32/Inno Setup 5.2.1**, zasoby `Polski VAG` v4.9 / `www.obd2.pl`. Nie wykonano go i **nie wydobyto wewnętrznych plików instalowanej aplikacji** — brak pewnej deasemblacji komunikacji COM docelowego programu. Zewnętrzne materiały wskazują na starszą diagnostykę VAG bez CAN i możliwą współpracę `Polski VAG 4.9` z niektórymi Commanderami przez **K-Line**, lecz **bez pomiaru na posiadanym interfejsie** i bez potwierdzenia użycia binarnych opkodów CAN. Raport: [ANALYSIS_POLSKI_VAG_49_2026-10-23.md](ANALYSIS_POLSKI_VAG_49_2026-10-23.md).

Jeśli projekt wróci do tego materiału: offline wypakować ten dokładny instalator narzędziem obsługującym Inno Setup 5.2.1 (np. `innoextract`) i dopiero wtedy badać aplikację, nie używając niezweryfikowanego programu na zwykłym komputerze ani w pojeździe. Nie zmieniono `PROTOCOL.md`, `COMMANDS.md` ani rejestru CAN `KCAN-D001..D042`.

## Uzupełnienie stanu: nowy chroniony VWTester „3.6” (2026-10-23)

Przesłano `VAG COMMANDER 3.6(2).rar` (RAR4, SHA-256 `4c4e448077836806c593ef2f08a948ee56d0bde73f6f7dd8f56148b0097403a4`, 26 plików + 2 katalogi). Zawiera **nowe `VWTester.exe` 647 168 B**, SHA-256 **`a448ff313cce8ee2597f14675e51196ca5b677a5561833bb65965b05628d8a23`** (różny od obu znanych EXE), **sekcje `.vmp0/.vmp1`**, `.text/.rdata/.data` z zerowym surowym rozmiarem, `.vmp1` o entropii ~7.91. **Statyczne odtworzenie wykonywalnego kodu CAN 3.6 nie było możliwe**. Oznaczenie 3.6 to nazwa dystrybucji; VERSIONINFO wciąż `1.0.0.1`.

EXE jawnie importuje `FTD2XX.dll` ordinals **1,2,61** = `FT_Open`, `FT_Close`, `FT_GetDeviceInfo`; `FTChipID.dll` ordinal **8** = `FTID_GetChipIDFromHandle`. W imporcie Win32 są `CreateFileA/ReadFile/WriteFile/SetCommState/EscapeCommFunction`. **Rola D2XX w komunikacji danych, chip ID/licencji, bitrate 833333, opkodów `0x50..0x70`, CAN29, listen-only i kompatybilność firmware są nieustalone.** Biblioteka `RCMicroDogSetup.dll` ma ten sam SHA-256 co w 1.4 i 2.5; dołączone FTDI INF są wersji **2.00.00 (2006)**. `Tester.ini`: pierwszy `TARGET=6`, drugi `TARGET=0`, `DIAGNOSTICID=-674897751`, `FILEINDEX=1872`, `CAN_PORT=2`, `KWP_PORT=2`. Cztery wspólne pliki TXT/INI identyczne po CRLF→LF z 1.4 (Git blob SHA).

**Raport:** [ANALYSIS_VWTESTER_36_2026-10-23.md](ANALYSIS_VWTESTER_36_2026-10-23.md), **nowe KCAN-D043** w [DISCREPANCIES.md](DISCREPANCIES.md). Nie modyfikowano formatu `PROTOCOL.md`/`COMMANDS.md`. Przed dalszym testowaniem **nie uruchamiać niezweryfikowanych EXE, nie podłączać do samochodu**, nie importować prawd o transmisji z 2.5 jako potwierdzonych dla 3.6.

## Uzupełnienie stanu: drugi i trzeci pakiet „3.6” (2026-10-23)

Użytkownik przesłał dwa dalsze pakiety:
- `VAG K CAN COMMANDER FULL 3,6.rar` (RAR4, 1 730 535 B, SHA-256 `e0059df5cb1e51434ae1eea95d4f7ff7234a176360fb739d2b382dbace83069b`).
- `VAG-K CAN-V3.6.zip` (ZIP, 1 971 451 B, SHA-256 `9b59b9490c0011edea1976d9d4ad16a4671e1870b45576088f298ed23b5d8b32`).

Porównano je **bajtowo po rozpakowaniu** z poprzednim `VAG COMMANDER 3.6(2).rar` (S11). Każde ma **26 plików**, z czego **25/26 identycznych we wszystkich trzech pakietach**: `VWTester.exe` SHA-256 **`a448ff313cce8ee2597f14675e51196ca5b677a5561833bb65965b05628d8a23`**, `FTChipID.dll`, `FTD2XX.dll`, `RCMicroDogSetup.dll`, kompletny `CDM_Setup`, dane VAG/INI/TXT. **Wyłącznie `Tester.ini` różni się**: pierwszy `TARGET=6/6/0`, drugi `TARGET=0`, `FILEINDEX=1872/1877/1879`; `CAN_PORT=2`, `KWP_PORT=2`, `DIAGNOSTICID=-674897751` bez zmian.

Szczegółowy raport: [ANALYSIS_VWTESTER_36_PACKAGES_2026-10-23.md](ANALYSIS_VWTESTER_36_PACKAGES_2026-10-23.md). **Brak nowego EXE, nowej deasemblacji CAN, nowego opkodu oraz dowodu działania na sprzęcie.** Zaktualizowano **KCAN-D011** i **D043**, bez D044. Nie wysyłać nieznanych komend do samochodu; do dalszego rozpoznania CAN potrzebne są nowe bajty EXE lub własne logi PC↔PIC/izolowany CAN.

## Uzupełnienie stanu: dwie nowe kompilacje 3.0 beta i 4.5 (2026-10-23)

**Nowy, ważny pakiet:** `VAG-CAN Commander V4.5.zip`, SHA-256 `e7980df7b33847af86ad12c52ae99c377b39c1d8f067abbe12e2d8c5de5e2b1c`, 32 pliki, 3 katalogi. **Dwa odrębne EXE z wykonywalnymi i statycznie czytelnymi fragmentami protokołu CAN:**

- `VAG-CAN Commander 3.0 beta.exe` — **417 792 B**, SHA-256 `dfb5e3f4724f6898c7c82d5d6e69ed3f795edb5f536f4aa5ff37ab17eae2a39b`; PE32 x86, 4 sekcje, Win32 COM `CreateFileA/ReadFile/WriteFile/SetCommState/EscapeCommFunction`.
- `VAG-CAN Commander4.5.exe` — **477 472 B**, SHA-256 `85e89882a434ad83d19381ecbb5f9e77b14b237343b1432feb2f7300810e0050`; PE32 x86 z sekcją `.mackt`, ale duża część kodu CAN jest czytelna, nie jest to ta sama chroniona kompilacja co „3.6”.

**Nowe potwierdzenia kodowe:** 3.0 beta `0x403510`, 4.5 `0x4034F0`: TX `60 (N+4) SIDH SIDL 00 00 [N]` z CAN11; RX `0x70 length=4..12` i ten sam dekoder ID. Zapis `53 20 [32 B]` w `0x403470` i `0x403450`; niezależne konstrukcje **6 filtrów + 2 maski (interpretacja fizyczna nadal hipoteza)** w `0x40A3F9` i `0x40A489`. **4.5** ma jawny walidator `0x60 length<=4` w `0x402C64`; w 3.0 beta w badanej funkcji nie ma takiego osobnego wyjątku. **Nowa ważna różnica:** w 4.5 `0x403170` wybiera **115200 przy parametrze 0/1** oraz **833333 przy parametrze >=2**, natomiast 3.0 beta `0x4031A0` przekazuje 833333; **brak potwierdzonego mapowania tych parametrów na GUI/CAN/K-Line**. Nie jest to bitrate CAN.

Pozostałe dane: stare INF FTDI `DriverVer=04/16/2004,1.00.2154`; `Tester.ini` ma `[COM] PORT=4`, `FILEINDEX=716`, dwa `TARGET=0`; cztery pliki tekstów/INI po CRLF→LF identyczne z 1.4. `installation.txt` niekonsekwentnie opisuje „2.0 beta”; nie zmienia to zawartości EXE.

Raport: [ANALYSIS_VAGCAN_30BETA_45_2026-10-23.md](ANALYSIS_VAGCAN_30BETA_45_2026-10-23.md). **Nowe testy KCAN-D044 i KCAN-D045** w [DISCREPANCIES.md](DISCREPANCIES.md). Uaktualniono `PROTOCOL.md`, `COMMANDS.md`, `FILTERS.md`. Nadal nie ma pomiarów konkretnego niebieskiego adaptera, potwierdzenia CAN29, listen-only/ACK, rzeczywistego efektu filtrów i pełnej procedury inicjalizacji. Nigdy nie mieszać poziomu dowodów z hosta z zachowaniem firmware.

**Priorytety dalszej pracy:** statycznie prześledzić wywołujących funkcję 4.5 `0x403170` i zmapować warianty 115200/833333; porównać pełny parser odpowiedzi `0x60` w 3.0 beta z 4.5 i 2.5; następnie laboratoryjny zrzut TX/RX PC↔PIC oraz odizolowany CAN. Tylko autorska dokumentacja w repo, nie programy, sterowniki, archiwa ani logi.
