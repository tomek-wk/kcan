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
