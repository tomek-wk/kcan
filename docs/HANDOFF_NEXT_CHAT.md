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

## Nowe wyniki pogłębione: PORT i C0 w 3.0 beta/4.5 (2026-10-23)

**Ważna korekta i nowy rozkaz hosta**, opisane szczegółowo w [ANALYSIS_VAGCAN_30BETA_45_DEEP_2026-10-23.md](ANALYSIS_VAGCAN_30BETA_45_DEEP_2026-10-23.md). Analiza *tych samych dwóch EXE z ZIP 4.5*, bez nowych plików i bez uruchamiania.

1. **115200/833333 w 4.5 to nie wybór trybu CAN/K-Line.** `GetPrivateProfileIntA("COM","PORT",0,...\\TESTER.INI)` `0x409D0A` → globalne `0xDC23E4` `0x409D11` → otwarcie `0x409EFA` → `0x403110/0x403170`; ta sama wartość formatuje nazwę **`COM%d`** w `0x408CD0`. Jeżeli `PORT=0/1`, baud=115200, a `PORT>=2`, baud=833333; w pakiecie `PORT=4` → COM4 / 833333. W 3.0 beta analogiczny odczyt INI do `0x015B0364`, bez gałęzi 115200. **D045 częściowo rozstrzygnięte w kodzie; fizyczny UART niezmierzony.**
2. **Nowe rzeczywiste PC→PIC `C0 00`** w obu starych aplikacjach: sekwencja inicjalizacji (4.5 `0x409F0F`, `0x409F25`, `0x409FC4`) **`51 00` → Sleep(50) → `C0 00` → Sleep(50) → `53 20 [32B]`**. 3.0 beta analogiczna. **Nie utożsamiać `C0` z `50` w FULL 2.5**, semantyka i obsługa firmware niepotwierdzone.
3. Tablice **8×34 B** RX: 3.0 VA `0x44A998`, 4.5 VA `0x44C998`; opkody i długości **`C0 00, 51 00, 52 20, 53 00, 54 02, 60 00 (3.0) / 60 04 (4.5), 6F 00, 70 00`**. Walidator 3.0 `0x402C80` dopuszcza **dokładnie `60 00`**, 4.5 `0x402C64` pozwala na `60 length=0..4`; obie wersje specjalnie akceptują `70 length=4..12`. `54 02` i `6F 00` są **wzorami oczekiwanych odpowiedzi, nie dowodem nadania odpowiednich żądań**. **D044 częściowo rozstrzygnięte w kodzie, brak weryfikacji sprzętu.**
4. Oba EXE `CreateFileA("COM%d")` bez prefiksu `\\\\.\\` dla COM10+, więc taka ścieżka nie obsługuje standardowo COM10+ (Microsoft CreateFileA). Program tworzy 16 rekordów, lecz brak jawnej kontroli `PORT` w `0x403170`; potencjalny problem dla `PORT>=16`. Nowe **D046**; rekomendowane laboratoryjne COM2–COM9. FULL 2.5 ma już rozpoznane wsparcie COM10+.

Zaktualizowano `PROTOCOL.md`, `COMMANDS.md`, `DISCREPANCIES.md`, `SAFE_TESTS.md`. Nie wysyłać `C0/53/60` do samochodu ani uruchamiać niezweryfikowanych EXE na głównym komputerze. Do potwierdzenia firmware potrzebny **własny bezpieczny zrzut PC↔PIC/stanowisko CAN**.

### Istotne przy reprodukcji: bieżący katalog i COM0

W 3.0 beta/4.5 `GetCurrentDirectoryA` + `\\TESTER.INI` i `GetPrivateProfileIntA("COM","PORT",0,...)` oznacza, że uruchomienie z innym katalogiem roboczym może prowadzić do **braku INI → PORT=0 → próby otwarcia COM0** (4.5 z UART 115200, 3.0 z UART 833333). To wniosek z wykonawczego kodu hosta, nie test systemowy. Wszelkie porównania powinny rejestrować working directory. Zob. [dalszą analizę](ANALYSIS_VAGCAN_30BETA_45_DEEP_2026-10-23.md).

## Uzupełnienie: pełniejszy audyt inicjalizacji i CAN29 w 3.0 beta/4.5 (2026-10-23)

Użytkownik poprosił o **ponowną analizę inicjalizacji oraz możliwości CAN 29-bit** w dwóch EXE z wcześniej przesłanego `VAG-CAN Commander V4.5.zip` (bez nowego pliku). Raport: [ANALYSIS_CAN29_INIT_30BETA_45_2026-10-23.md](ANALYSIS_CAN29_INIT_30BETA_45_2026-10-23.md).

**Wynik istotny dla niezależnego oprogramowania:** TX 3.0 beta `0x403510` / 4.5 `0x4034F0` czyta ID jako **WORD** i wysyła `60 (N+4) ((ID>>3)&FF) ((ID&7)<<2) 00 00 [dane]`. RX 3.0 beta `0x402D10` / 4.5 `0x402CE0` z `70` buduje **wyłącznie 11-bitowy ID** `(b2<<3)|((b3>>2)&7)` i pomija dalsze dwa bajty pola. **29-bit nie jest reprezentowalny w tych ścieżkach**, mimo 4B nagłówka. Test aliasowania: CAN29 `0x18DAF110` i CAN11 `0x110` oba dają nagłówek `22 00 00 00` w TX tego kodu. W obu EXE bezpośrednich wywołań UART-writera `0x408BD0` jest 5 (51, C0, 53, 60, generic raw); brak dodatkowego potwierdzonego kodowania extended-ID.

**Inicjalizacja:** COM (`Tester.ini [COM] PORT`) → Sleep(50) → `51 00` → Sleep(50) → `C0 00` → Sleep(50) → `53 20 [32B]` (oczekiwanie do 100 ms w podprocedurach). W **obu** programach statycznie zrekonstruowano osiem 4-bajtowych wpisów bloku init: rekordy 0–5 = `FF 1C 00 00`, nr 6 = **`FF 1C 00 FF`**, nr 7 = `FF 1C 00 00`. Znaczenie `C0` i specjalnego ostatniego `FF` nieznane, brak jawnego przełączenia IDE29. 4.5 prędkość UART nadal zależy od numeru COM (PORT<2:115200, >=2:833333), a nie od CAN/K-Line; to nie bitrate CAN.

**Bardzo ważny niuans:** bajt nazwany `SIDL` w protokole **NIE JEST surowym PIC SIDL**: UART `(ID&7)<<2` umieszcza SID w bitach 4–2, a w rejestrze potencjalnego PIC18F248/258 to bity 7–5; `EXIDE` (bit 3 PIC) nie może być odczytany z hostowego `0x1C`. Rodzina PIC sprzętowo może CAN 2.0B Active, ale **typ PCB/firmware konkretnego adaptera i faktyczna obsługa CAN29 pozostają nieznane**. Chroniony 3.6 nie został rozstrzygnięty.

Nowe **KCAN-D047** w [DISCREPANCIES.md](DISCREPANCIES.md), test w [SAFE_TESTS.md](SAFE_TESTS.md): referencyjny CAN11 `0x110` kontra CAN29 `0x18DAF110` tylko na izolowanej magistrali, obserwacja UART i fizycznego CAN, bez prób w pojeździe. Nie wymyślać nowego opkodu CAN29.

## Uzupełnienie: krytyczne błędy obsługi UART i pozorny sukces TX (2026-10-23)

Po poprzednim audycie CAN29 użytkownik polecił **szukać dalej**. Ponownie statycznie analizowano te same EXE 3.0 beta/4.5 z `VAG-CAN Commander V4.5.zip`, szczególnie niskopoziomowy COM, bez uruchamiania ani testów sprzętowych. Pełny raport: [ANALYSIS_SERIAL_TX_RELIABILITY_30BETA_45_2026-10-23.md](ANALYSIS_SERIAL_TX_RELIABILITY_30BETA_45_2026-10-23.md).

**Trzy nowe istotne wnioski:**
1. **Funkcja UART `0x408BD0`** w obu EXE: `WriteFile OVERLAPPED` → przy FALSE `WaitForSingleObject` → **`GetOverlappedResult(...,TRUE)` bez sprawdzania BOOL ani `bytesWritten`** → zawsze **return 1** jeśli uchwyt COM nie jest `INVALID_HANDLE_VALUE`. W **3.0 beta pierwszy wait jest INFINITE**, w **4.5 pierwszy wait to 258 ms**, ALE **GetOverlappedResult(TRUE) może nadal czekać bez limitu**. Nie ma skutecznego końcowego timeoutu ani prawdziwego potwierdzenia WriteFile.
2. **TX CAN11 `0x403510` (3.0) i `0x4034F0` (4.5)** po wywołaniu writer **nie sprawdza jego wyniku**, odnotowuje próbę jako lokalny rekord TX z `GetTickCount` i statusem, `Sleep(10)`, **return 1**. W tej ścieżce nie czeka na `0x60` status PIC, tym bardziej fizyczny ACK CAN. Oznaczenie TX w starym GUI **nie dowodzi** transmisji na magistrali. Dodatkowe potwierdzenie braku CAN29: wewnętrzna mapa TX/RX ma indeks `(channel<<11)|(ID&0x7FF)`.
3. **DTR/RTS** w otwarciu portu `0x408CD0`: **SETDTR(5)→Sleep(500ms)→CLRDTR(6)→SETRTS(3)** w obu. Skutek na niebieskim PIC nieznany. TX pobiera N jako **bajt**, kopiuje **N bajtów do lokalnego bufora stosu bez lokalnego ograniczenia do 8**. Ograniczenia mogą istnieć w caller/GUI; testy błędnych N robić wyłącznie na własnym kodzie/mocku, NIE w starym EXE.

**Nowe zadania:** [KCAN-D048, D049, D050](DISCREPANCIES.md); uaktualniono `README.md`, `PROTOCOL.md`, `COMMANDS.md`, `SAFE_TESTS.md`, `SOURCES.md`. Nie znaleziono nowego protokołu CAN29 ani nie poznano semantyki `C0/54/6F`. Nie używać nieznanych komend ani starych niezweryfikowanych EXE w aucie.

**Następne priorytety:** w osobnym, bezpiecznym kliencie rozdzielić stany `request/write/adapter/CAN`, implementować skuteczny timeout, walidować DLC i przetestować retry/missing responses. Przy testach sprzętu tylko odizolowany CAN i referencyjny analizator.

## Uzupełnienie: ZIP „V5.1”, ale EXE 5.0+ECU (2026-10-23)

Nowy materiał użytkownika `VAG-CAN Commander V5.1.zip`, **1 113 420 B**, SHA-256 `151913526f55e2528ccf153a0d47b69d67d53dde96ed8057af9efe083aeea94f` (28 plików, 4 katalogi). Zawiera **nową kompilację** `VAG-CAN Commander+EDC15.exe`, **466 968 B**, SHA-256 **`811bf59355614e0d07aa2e4c10fedd01fbff2b0148feab4491f0f731c98d45ba`**. W zasobach GUI jawnie `VAG-CAN COMMANDER 5.0+ECU (full)` i `VAG-EDC15x`; **nie utożsamiać nazwy ZIP V5.1 z wersją binarium lub firmware**.

**Najważniejsze wykonawcze ścieżki CAN:** TX `0x403520`: `60 (N+4) ((ID>>3)&FF) ((ID&7)<<2) 00 00 [N]`, ID pobierany jako WORD; RX `0x402CE0`: `70` długości 4..12 i dekoder tylko 11-bit; walidator `0x402C40` dopuszcza `0x60` N=0..4 pomimo tablicy z `60 00`. Brak obsługi CAN29 w tych funkcjach, bez wniosku o całym firmware. Inicjalizacja `0x40AE9C` → `0x403370` **51 00**, `0x4033F0` **C0 00**, `0x403470` **53 20[32]** (7 rekordów `FF 1C 00 00`, jeden nr 6 `FF 1C 00 FF`); znaczenie C0 i ostatniego FF nadal nieznane. UART `0x4031BA` **833333 bit/s** w zbadanej ścieżce; `Tester.ini` ma **CAN_PORT=5/KWP_PORT=5** rozpoznawane osobno przez `GetPrivateProfileIntA`.

**Nowy materiał poboczny:** `memory.bin` 2048 B, SHA-256 `739e3bf5eca392955fa70e7aeea725dad3c39e6d3d69d13b1d65c183596d6ea4`, nazwa odnaleziona także jako referencja w EXE `0x4135E0`. Nie ustalono, czy to backup EEPROM, przykład czy inne dane. **Nie publikować ani nie określać firmware PIC bez dowodu**. Cztery TXT/INI danych po CRLF→LF identyczne z 1.4, FTDI INF **2.04.06 (2008), i386 + amd64**, domyślny zapis `LatencyTimer=16`. EXE bez bezpośredniego importu D2XX, choć paczka zawiera DLL w sterownikach.

**Powtórzone ryzyka:** write COM `0x408BF0` = OVERLAPPED, brak walidacji wyniku `GetOverlappedResult`, potencjalny `INFINITE`; CAN TX lokalny sukces po `Sleep(10)`, brak potwierdzenia PIC i CAN; brak lokalnej walidacji N<=8. Powiązania D047–D050. **Nowe D051/D052** w [DISCREPANCIES.md](DISCREPANCIES.md). [Pełna analiza](ANALYSIS_VAGCAN_50ECU_V51_2026-10-23.md).

Dalsza praca: offline prześledzić obsługę `memory.bin` i czy w aplikacji EDC15 ukryto jakiś alternatywny format komunikacji. Do testów CAN29 i listen-only nadal potrzeba własnych danych PC↔PIC, kontrolera/PIC i drugiego referencyjnego interfejsu na **izolowanej magistrali**, nie pojeździe. Repo zawiera tylko dokumentację, bez plików źródłowych EXE/ZIP/BIN i sterowników.

## Pogłębione odkrycia V5.1: CFile memory.bin i transport CAN TP2.0 (2026-10-23)

Po poleceniu użytkownika „szukaj dalej” wykonano powtórną **statyczną** analizę `VAG-CAN Commander+EDC15.exe` SHA-256 `811bf59355614e0d07aa2e4c10fedd01fbff2b0148feab4491f0f731c98d45ba`. Raport: [ANALYSIS_VAGCAN_50ECU_V51_MEMORY_TP20_2026-10-23.md](ANALYSIS_VAGCAN_50ECU_V51_MEMORY_TP20_2026-10-23.md). Nie uruchomiono żadnych binariów.

**Nowy przełom w D052:** `memory.bin` jest w zbadanej ścieżce **NAZWĄ WYJŚCIOWĄ eksportu pamięci ECU**. W `0x4135E0–0x413615` `CFile::Open` z flagami **0x1001 = modeCreate|modeWrite** (vtable `0x459654`, +0x20→`0x449B48`); w `0x413A13/0x413A86` `CFile::Write(1 byte)` (vtable +0x38→`0x449C9F`), `0x413DC4` `Close` (+0x4C→`0x449D63`), tekst `ReadMemory - Done.`. Funkcja `0x414F40` pokazuje predefiniowane limity odczytu **512 KiB/16 KiB/4 KiB**, porcje **64/64/16 B**, adresy startowe zależne od stanu, oraz **custom mode 0xFF** z GUI. `memory.bin` z ZIP to 2048 B — nie odpowiada predefiniowanym limitom i nadal nie znamy pochodzenia. **Może zostać nadpisany przez `modeCreate`**. Nie nazywać firmware PIC, nie publikować danych.

**D053: kod rzeczywistego VAG TP2.0!** `0x420360` oblicza `ceil(len/7)`, dzieli payload KWP2000 na segmenty **do 7 B + 1 B nagłówka**, inkrementuje nibble sekwencji mod16, ustawia górny nibble sterowania: **0x20** (więcej bez czekania ACK), **0x00** (więcej, granica block-size z oczekiwaniem), **0x10** (ostatni, ACK). Przekazuje do `0x4207D0 → 0x403520` i dalej **UART `0x60`**, gdyż TP2.0 to *payload ramki CAN*, a nie opcode mikrokontrolera. RX `0x420580` zawiera `D0/A8/B0` i kod wysłania `B0|seq`. Wzorzec potwierdzony kontekstowo przez [VW TP2.0](https://jazdw.net/tp20) i [ACTIA](https://www.ime-actia.de/en/vehicle-diagnostics/tp1-6-2-0/). Pełny handshake niepotwierdzony; jedna gałąź A1 wygląda na nieosiągalną (`ID & 0xFF` vs `0x300`). **To nadal tylko CAN11, nie CAN29**. WAŻNE: UART `C0 00` do PIC ≠ CAN TP2.0 `C0...` przy otwarciu kanału.

**D054: dwa potencjalne deadlocki/busy-wait:** `0x420371..` i `0x420498..` to aktywne pętle na globalnych flagach bez lokalnego Sleep/timeout. Przy `0x42046D` `idiv` parametrem block-size bez lokalnej walidacji `>0`; sprawdzić kontrakt negocjacji, nie testować złych parametrów na starym EXE. Nowy własny klient wymaga timeoutów ACK, cancel, walidacji rozmiaru bloku.

Zaktualizowano D052, dodano D053 i D054 w `DISCREPANCIES.md`, opis warstw w `PROTOCOL.md`, plan testów w `SAFE_TESTS.md`. Pozostają otwarte: firmware PIC, CAN29, prawdziwy listen-only/ACK, skutki błędów i skąd pochodzi dołączony BIN. Cały wynik bez nowych binariów/plików użytkownika w GitHub.

## Najnowszy stan: audyt wszystkich dostępnych plików bez analizy chronionych EXE (2026-10-23)

Na polecenie użytkownika **ponownie sprawdzono wszystkie 8 dostępnych archiwów**. Nie uruchamiano plików, nie próbowano deprotektować 1.4 ani trzech pakietów identycznej chronionej 3.6, nie analizowano wnętrza nieodczytanego instalatora Polski VAG. Przedmiotem analizy kodu były **wyłącznie jawne funkcje** `VAG-CAN Commander 3.0 beta.exe` SHA `dfb5e3f4724f6898c7c82d5d6e69ed3f795edb5f536f4aa5ff37ab17eae2a39b`, `VAG-CAN Commander4.5.exe` SHA `85e89882a434ad83d19381ecbb5f9e77b14b237343b1432feb2f7300810e0050`, `VAG-CAN Commander+EDC15.exe` SHA `811bf59355614e0d07aa2e4c10fedd01fbff2b0148feab4491f0f731c98d45ba`; osobno zdekodowano jawne dane VWTOOL (NE/VB3, XOR 0x85). **BIN FULL 2.5 nie był fizycznie dostępny**, więc nie dokonano nowej weryfikacji jego kodu.

**Duże nowe ustalenie:** TP2.0 istnieje w KAŻDEJ z tych trzech czytelnych kompilacji: nadanie segmentów w `0x4166E0/0x417FB0/0x420360`; odbiór `0x416900/0x4181D0/0x420580`. Wygenerowane segmenty 1+do7 B, numery seq mod16, negocjowany block-size, ACK. W jawnej deasemblacji znaleziono odpowiednio **70/108/107** bezpośrednich call-site segmentera. Kod i wady są tak podobne, że **nie są trzema niezależnymi realizacjami** — prawdopodobne dziedziczenie tej samej implementacji; koryguje interpretację wcześniejszego raportu o „odkryciu w 5.0+ECU”.

**KCAN-D055 NOWE, priorytet P0:** RX `0x70` dopuszcza legalny `CAN DLC=0`, a trasa do TP2.0 nie ma ogólnej walidacji DLC>=1 (przed handlerem znajduje się filtrowanie stale `return 1`). W ogólnej gałęzi handler `dec ecx` po `N=0`, następnie `shr ecx,2; rep movsd` daje **0x3FFFFFFF DWORD** do skopiowania — możliwa awaria/korupcja pamięci. 3.0 `0x416A41/0x416A4E`; 4.5 `0x418311/0x41831E`; 5.0 `0x4206C1/0x4206CE`. **Nie każda pusta ramka musi dotrzeć do tej gałęzi**, ale parser nie jest lokalnie bezpieczny. Testować tylko własny mock decoder; w ogólnym snifferze CAN DLC0 jest dozwolone, w TP2.0 wymagany 1B sterowania.

**KCAN-D056 NOWE, P1:** we wszystkich trzech RX `AND EAX,0xFF` bezpośrednio przed `CMP AX,0x300` czyni **gałąź A1/A3 nieosiągalną** (3.0 `0x416924/0x416926`, 4.5 `0x4181F4/0x4181F6`, 5.0 `0x4205A4/0x4205A6`). Nie oznacza to braku innych dróg handshake (D0 istnieje). Maskowanie `control & 0xB0 == 0xB0` dla ACK może zaakceptować również `0xF0`; 3.0 i 4.5/5.0 różnią się też rygorem rozpoznawania nagłówków wymagających ACK. Własny parser stosować ścisły nibble `0xB0` i walidację sekwencji.

**D053/D054 uzupełnione:** istniejące pętle busy-wait i brak lokalnej kontroli dzielnika block-size występują także w 3.0/4.5. Nadal **bez dowodu firmware CAN29, fizycznego ACK i listen-only**. Pełny raport: [AUDIT_READABLE_FILES_2026-10-23.md](AUDIT_READABLE_FILES_2026-10-23.md), zmiany rejestru [DISCREPANCIES.md](DISCREPANCIES.md); wyniki statyczne, bez binariów w repo.

## Nowe źródła: lista zrzutów firmware procesorów i nieudanych odczytów (2026-10-23)

Na żądanie użytkownika przeszukano fora i indeksy stron pod kątem *obrazów wykonywalnej pamięci mikrokontrolera* K+CAN oraz relacji o nieudanym odczycie. Stworzono **[FIRMWARE_DUMP_LEADS_2026-10-23.md](FIRMWARE_DUMP_LEADS_2026-10-23.md)** — **FD-001–FD-014** z oryginalnymi linkami, datami, dokładnymi nazwami załączników, stopniem pewności i planem statycznej weryfikacji.

Najbardziej obiecujące: **FD-001** CXEM `KCAN-ELM327.RAR` z `pic18f2480.hex` (PIC18F2480); **FD-003** Carmasters `PIC18F248.rar` oraz porównanie do PIC18F258; **FD-005** 4PDA `CAN-PIC18F25K80.rar` (36,65KB); **FD-002** wypowiedź Valentin8080, że firmware 1.4 zostało wcześniej zgrane z fizycznego adaptera; **FD-007** alternatywna rewizja sprzętowa **NXP LPC2119FBD64** z „flasherem i firmware 3.6”.

**FD-004, ważny negatywny wynik:** 4PDA 26–27.07.2025: użytkownik `cxem` nie może odczytać FLASH ani EEPROM PIC18F25K80 z K+CAN, inny uczestnik podaje aktywną ochronę kodu. **FD-006** PCCar 2016: udało się zgrać *poprzedni firmware ELM327*, ale po zapisaniu zmodyfikowanego firmware K+CAN programator nie zaliczył VERIFY i zgubił identyfikację PIC — nie jest to dowód nieudanego readout K+CAN. **FD-009** Autoprogs 2020: nieudany ponowny zapis po kasowaniu, a nie błąd czytania. **FD-012–014** to wyjaśnione fałszywe identyfikacje dumpów (FTDI EEPROM, dump raportu dongla, ECU memory.bin).

**Stan:** żadnego nowego HEX/Flash obrazu nie pobrano, nie rozpakowano ani nie zweryfikowano; brak hashy firmware. Nie uruchamiano binariów, nie czytano ani nie programowano interfejsu. W kolejnej rozmowie priorytetem statyczne sprawdzenie prawdziwej zawartości archiwów z FD-001/003/005; porównać `0x53` konfigurację filtrów oraz RX `0x70`, pamiętając że protokół może być niezgodny i właśnie ta rozbieżność jest cenna.

## 2026-10-24 — dodatkowy audyt dumpów/aktualizatorów 1.4–6.0 i statycznie sprawdzony HEX

**Wynik poszerzonych poszukiwań:** dodano [FIRMWARE_DUMP_FOLLOWUP_2026-10-24.md](FIRMWARE_DUMP_FOLLOWUP_2026-10-24.md) (FD-015–FD-024) jako uzupełnienie [FIRMWARE_DUMP_LEADS_2026-10-23.md](FIRMWARE_DUMP_LEADS_2026-10-23.md) (FD-001–014). Poszukiwano również Commandera **2.5, 3.6, 4.8, 5.1, 5.5, 6.0**, nowej wersji **PIC18F25K80** i pokrewnych aktualizatorów dla **ARM SuperVAG**, **bez domniemania zgodności protokołów**.

**Nowe konkretne źródło:** [CXEM VAG K+CAN 27.07.2025](https://forum.cxem.net/topic/279806-vag-kcan/) zawiera dwa załączniki `CAN-PIC18F25K80.RAR` i `FT232RL.RAR`; próby ich otwarcia nie powiodły się. [Wpis cxem2 29.07.2025](https://forum.cxem.net/topic/279806-vag-kcan/#findComment-4140128) opisuje **RTS OFF→K-Line, RTS ON→PIC/CAN, DTR ON→reset PIC** w pewnym klonie z PIC18F258 / PIC18LF2685, co odpowiada tematowi DTR/RTS w naszym projekcie, ale wymaga sprawdzenia sprzętu.

**5.5/4.8–6.0:** fora Carmasters/Autoprogs opisują niezgodność firmware 5.5 z 1.4 i poszukiwanie PIC18F258 wsadu. **SuperVAG** od 3.0 do 4.8 posiadał **10** historycznych adresów ZIP dla aktualizatorów firmware `resettools.com/app/supervag_k_can/updater*.zip` — **domena niedostępna/parkowana lub timeout**. To **prawdopodobnie inna platforma z ARM**, nie ten sam Commander. Inne mirrory w [raporcie](FIRMWARE_DUMP_FOLLOWUP_2026-10-24.md).

**Pierwszy sukces faktycznego odczytu tekstowego Intel HEX z publicznego Github, ale NIE firmware Commandera:** `qnx425/mpcanflash/test/app.hex` i `test1.hex/test2.hex`, przykłady dla innego bootloadera PIC18FxxK80. Statyczna walidacja rekordów Intel HEX i sum: **app 32 rekordy/448 B danych, test1 9/126 B, test2 10/144 B, zero błędów**. Nie posiadają potwierdzonej obsługi UART Commandera `0x53/0x70`, więc nie wolno zgłaszać ich jako zdobytego wsadu. Również repo `darkspr1te/elm327_clone` udostępnia kod C dla PIC18F25K80, nie Commander.

**Stan: nadal 0 autentycznych obrazów MCU Commandera pobranych / zweryfikowanych.** Brak uruchamiania plików, zapisów PIC i dostępu do samochodu; dokumentacja i odnośniki GitHub, bez kopiowania cudzych binariów.
