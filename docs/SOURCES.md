# Źródła i pochodzenie wiedzy

Podajemy **odsyłacze, tytuły, nazwy i sumy kontrolne**. Repozytorium nie przechowuje archiwów, oryginalnych programów ani pełnych logów.

## S1 — pięć archiwów udostępnionych do analizy

- `J2534KCANv1.0.0.10.zip` — biblioteka J2534 i konfigurator (informacja o archiwum m.in. w [ClubLexus](https://www.clublexus.com/forums/es-1st-to-4th-gen-1990-2006/977530-programs-delete-keys-rfid.html)).
- `kcantv10.rar`, `kcantv11.rar` — KCANTEST.
- `kcantv10_log.rar`, `kcantv11_log.rar` — pięć logów testera.
- Historyczna dyskusja z załącznikami: [PCCar — TECU III](https://pccar.ru/showthread.php?page=76&t=17386).
- Pełne **SHA-256** materiałów: [EVIDENCE.md](EVIDENCE.md).

**Status źródła:** archiwa zostały wcześniej fizycznie przeanalizowane statycznie; brak upublicznienia ich zawartości w repo.

## S2 — oryginalne oprogramowanie / dokumentacja 1.4

- [Skylakc/BoschME7.5-Tools](https://github.com/Skylakc/BoschME7.5-Tools/tree/main/tools/VAG-K_CAN_Commander_1%5BX%5D.4) — znaleziono `VAG-K+CAN Commander.exe` i pliki opisowe.
- `Tester.ini` — m.in. `[COM] CAN_PORT`, `KWP_PORT`, `[KWP1281]`.
- `installation 1.2-6+.txt` — FTDI USB–COM, sugerowany `Latency Timer=1 ms`, osobny dongle USB w tej dystrybucji.
- `bugfixes open issues.txt` — funkcje aplikacji i historie zmian, nie kodowanie PC–PIC.
- [MHH AUTO — VAG Commander 1.4](https://mhhauto.com/Thread-Vag-commander-1-4-software-please) — historyczny pakiet, dostęp ograniczony.
- [Tlemcen Electronics](https://www.tlemcen-electronic.com/forum/outils-and-diag/outils-de-diagnostique/vas5054-vcds-odis/1110-vag-commander-1-4-a.html) — inna kopia archiwalna, dostęp ograniczony.

**Status źródła:** odczytano dokumenty tekstowe; EXE w GitHub zlokalizowano tylko po metadanych, bez analizy kodu.

## S3 — niezależne implementacje, dyskusje, zewnętrzne logi

- [HUD ECU Hacker](https://www.netcult.ch/elmue/HUD%20ECU%20Hacker/) — niezależna implementacja, informacje o możliwościach i ograniczeniach adaptera (w tym ACK).
- [Malykh: VAG K+CAN](https://malykh.blogspot.com/2014/04/vag-kcan.html) — uwagi o protokole i K-Line.
- [DAP4CS](https://dap4cs.com/adapters) — obsługiwane interfejsy, m.in. K+CAN Commander.
- [PCCar — TECU III](https://pccar.ru/archive/index.php/t-17386-p-13.html) — historyczne logi komend, informacje o KCANTEST i J2534.
- [EconTool](https://t.me/s/econtool) — relacja autora o implementacji K+CAN przy współpracy z autorem TECU III.
- [Subaru SSM Dashboard](https://github.com/surtaeff/subaru-ssm-dashboard) — niezależne wykorzystanie toru K-Line, testowanie kombinacji RTS/DTR; **nie jest** źródłem kodów binarnego protokołu CAN Commandera.
- [Forum cxem.net](https://forum.cxem.net/topic/279806-vag-kcan/) — opis konkretnej konstrukcji; fizyczne połączenia nie muszą odpowiadać innym klonom.

**Status źródeł:** dokumentują funkcje i historyczne eksperymenty; ich twierdzeń nie wolno automatycznie traktować jako potwierdzenia na sprzęcie użytkownika.

## Metodologia aktualizacji

Każde nowe ustalenie powinno zawierać:
1. nazwę wariantu adaptera / firmware;
2. typ źródła (kod, log, pomiar sprzętowy, relacja);
3. krótki przykład HEX lub ślad w kodzie (jeżeli wolno go przytoczyć);
4. poziom pewności i otwarte pytania;
5. datę oraz odnośnik do źródła.

Nie commitować materiałów oryginalnych ani pobranych plików wykonywalnych.


---

## S4 — archiwum oryginalnego programu dostarczone 2026-10-23

- Użytkownik przesłał `VAG-K_CAN_Commander_1[X].4.zip` (SHA-256: `6912218b24524ae629f7ccfa77599aca3823132ea77e42e0145f155a32852028`).
- Statycznie przeanalizowano program `VAG-K+CAN Commander.exe`, ustawienia oraz komponenty pakietu. **Nie wykonywano** plików PE.
- Zgodność EXE z [publicznym repozytorium Skylakc/BoschME7.5-Tools](https://github.com/Skylakc/BoschME7.5-Tools/tree/main/tools/VAG-K_CAN_Commander_1%5BX%5D.4) ustalono po rzeczywistym identyfikatorze Git blob SHA-1, a nie nazwie pliku.
- Pełne podsumowanie techniczne: [ANALYSIS_ORIGINAL_EXE_2026-10-23.md](ANALYSIS_ORIGINAL_EXE_2026-10-23.md). Lista wersji i niepewności: [DISCREPANCIES.md](DISCREPANCIES.md).
- Żadnych binariów z tego źródła nie publikujemy w `kcan`.


---

## S5 — kolejny pakiet dostarczony do analizy (2026-10-23)

- `commander vag-k can.zip`, SHA-256 `5ee88477ab1e7b691b20119a44ce1298c122dcaba7713f17ca98ad90a644c7cf`, otrzymany od użytkownika; 46 plików w tym `Setup VAG K+CAN COMMANDER 1.4.exe` i polskie instrukcje PDF.
- `instrukcja obslugi interfejsu vag k+can.pdf` autorstwa Marcina Laszczewskiego (`auto-interfejsy.pl`): FTDI VCP, ustawienia portu/USB i wskazówki dla Commandera FULL 1.4.
- `korekcja licznika VAG CAN K.pdf` (`viaken.pl`): opis innego, historycznego wariantu interfejsu.
- `ftdiport.inf` z archiwum: metadane wersji FTDI 2.04.06.
- Analiza bez wykonywania programów: [ANALYSIS_SETUP_FACTORY_2026-10-23.md](ANALYSIS_SETUP_FACTORY_2026-10-23.md). Rozbieżności: [DISCREPANCIES.md](DISCREPANCIES.md).
- Brak publikacji zawartości ZIP/PDF/EXE/DLL w GitHubie.


---

## S6 — katalog programu „FULL 1.4” (2026-10-23)

- Archiwum użytkownika: `VAG K CAN COMMANDER FULL 1.4.zip`, SHA-256 `05f138209fb36a97fbb299213ec4e97376c6980887f867836dc9e7b1cca048d1`.
- EXE/DLL odpowiadają **dokładnie** wcześniejszemu pakietowi `1[X].4` i plikom [Skylakc/BoschME7.5-Tools](https://github.com/Skylakc/BoschME7.5-Tools/tree/main/tools/VAG-K_CAN_Commander_1%5BX%5D.4).
- Jedyna różnica zawartości tekstów to konfiguracja `Tester.ini`; szczegóły: [ANALYSIS_FULL14_2026-10-23.md](ANALYSIS_FULL14_2026-10-23.md) i [DISCREPANCIES.md](DISCREPANCIES.md).
- Do GitHub trafiają tylko metadane/opracowanie, **nie źródłowe archiwum ani program**.


---

## S7 — `k+can2.5(1).zip` (2026-10-23)

- Materiał dostarczony przez użytkownika. ZIP SHA-256: `9018525b61f96a23166dcfa8dcff502154bd95b15084c9b24ba39707d3af9835`.
- Oryginalny program `VWTester.exe`, SHA-256: `b90fc612decb04759a77fd0f02946157d832053186c7adf5e50624a1b103a10d`, kod w przeważającej części czytelny statycznie. W zasobach nazwa **Commander FULL 2.5**.
- `RCMicroDogSetup.dll` jest bajtowo identyczne z wcześniejszym pakietem FULL 1.4.
- Raport szczegółowy z adresami VA, algorytmami i ograniczeniami: [ANALYSIS_VWTESTER_25_2026-10-23.md](ANALYSIS_VWTESTER_25_2026-10-23.md). Rozbieżności do testów: [DISCREPANCIES.md](DISCREPANCIES.md).
- Nie dołączono żadnego oryginalnego EXE/DLL ani ZIP do repozytorium.

## S8 — zainstalowany Commander 1.4 (2026-10-23)

- Plik użytkownika `VAG K+CAN COMMANDER 1.4zainstalowany.rar` (RAR5, SHA-256 `8f76b5f4e1b420878e159b42f83367e7a4586c826cae3d5319715268409fdbd2`) zawiera 16 plików i 2 katalogi.
- EXE `VAG K+CAN COMMANDER 1.4.exe`: SHA-256 `ea69c09b51fda25107d9926d7d033f4e25f5374ec0dd2b1bc4a9867a7b19b932` identyczny z wcześniej analizowanym `1[X].4` / `FULL 1.4`. `RCMicroDogSetup.dll`: SHA-256 `5671711caf7446ce3496028375156cf4443c12311ac4e75c626dd740652d8ef4`, także identyczna.
- Użyte pliki: `Tester.ini` oraz **lokalnie** `Uninstall/uninstall.xml` (zawiera dane konta i ścieżki komputera; **nie publikować treści**). Nazwa instalatora podana w XML potwierdza kontekst Setup Factory, ale nie jest hashem konkretnego instalatora.
- Wyniki porównania 8 pozostałych tekstów po CRLF→LF z [repo Skylakc](https://github.com/Skylakc/BoschME7.5-Tools/tree/main/tools/VAG-K_CAN_Commander_1%5BX%5D.4): identyczne; `Tester.ini` wariant `FILEINDEX=1955`.
- Raport: [ANALYSIS_INSTALLED14_2026-10-23.md](ANALYSIS_INSTALLED14_2026-10-23.md). Oryginalne binaria, archiwum, lokalny XML i logi pozostają poza repo.

## S9 — VWTOOL / VDS-PRO 2.09 (2026-10-23)

- Materiał użytkownika: `VWool 2 0 9 en PL.rar` — RAR v4, 482777 B, SHA-256 `70b992d60f4b5cc014b30bca9fb6840ac213e883a7fd9378d92745e568a9079d`; **16 plików, bez hasła**.
- `VWTOOL.EXE` SHA-256 `c83f27287903b4d466b48406db20944be4783a59100b690832e3b134e3bfb93a`; `VWTOOL-pl.EXE` SHA-256 `2a473cb2f55706df9682ec8e78181c1f18dce2c2ea377c468b493e30ddbc5120`. Programy 16-bitowe NE/Visual Basic 3, **nie VAG K+CAN Commander**.
- `ERRCODE4.CSV` oraz `LABELS.CSV` — dane w kodowaniu XOR `0x85` z niezmienionymi CR/LF (opisy błędów i grup pomiarowych). Pełne bazy nie są publikowane.
- Źródła zewnętrzne: [VDSPro 2.09, archiwalna instrukcja](https://www.manualzz.com/doc/6336906/baum-tools-unlimited-vdspro-diagnostic-software-instructi...), [Ross-Tech: podręcznik i historyczny komentarz o VWTool](https://ross-tech.net/vag-com/download/old-manual/PrintableManual4090d.pdf), [Ross-Tech: stare interfejsy](https://www.register.ross-tech.com/vag-com/old-interfaces/discontinued_interfaces.php). Nie dowodzą współpracy z konkretnym interfejsem K+CAN użytkownika.
- Wyniki: [ANALYSIS_VWTOOL_209_2026-10-23.md](ANALYSIS_VWTOOL_209_2026-10-23.md); brak nowych komend CAN PC↔PIC.

## S10 — Polski VAG 4.9 (2026-10-23)

- Archiwum użytkownika `Polski VAG 4.9(1).rar`: RAR4, 9 407 067 B, SHA-256 `3febfd5015830fb6626134f6e13fed107f09ff2d7544e36ad244e4102d0c8e7f`; jeden `setup.exe` (9 414 111 B, SHA-256 `132d7d275a1b3a406a963f1a625a3ceb4bea174ea1a5b22135f4720d8db6046e`, CRC `5037C6C0`).
- Analiza lokalna stuba: **Inno Setup 5.2.1**, zasoby **`Polski VAG` / `4.9` / `www.obd2.pl`**, 8 sekcji PE i 9 350 623 B danych dołączonych. **Nie rozpakowano wewnętrznego ładunku instalatora**; brak podstaw do wskazywania bibliotek lub opkodów aplikacji. Plik uruchamialny *nie był wykonywany*.
- Publiczne potwierdzenie tożsamości poprzez dokładnie ten sam hash: [herdProtect, Polski VAG 4.9](https://www.herdprotect.com/polski-vag-4.9.exe-db8089cd37de46fe56348b93656403e366d0da0a.aspx).
- Kontekst obsługi: [opis Polski VAG 4.9 — brak diagnostyki CAN](https://pliki.pl/polski-vag-4-9/), [historyczna relacja zgodności K+CAN z Polski VAG](https://forum.vw-passat.pl/topic/34160-interfejs-diagnostyczny-co-nim-mozna/), [opis K+CAN 3.6 — Polski VAG po K-Line vs Commander po CAN](https://www.ccy.pl/pl/sklep/interfejs-obd2-vag-k-can-3-6-usb-detail.html). To **relacje/opisy zewnętrzne**, nie pomiary posiadanego interfejsu.
- Raport: [ANALYSIS_POLSKI_VAG_49_2026-10-23.md](ANALYSIS_POLSKI_VAG_49_2026-10-23.md). Archiwum i instalator nie trafiają do repo.

## S11 — VAG Commander „3.6” (2026-10-23)

- Materiał użytkownika: `VAG COMMANDER 3.6(2).rar`, RAR4, 1 730 114 B, SHA-256 `4c4e448077836806c593ef2f08a948ee56d0bde73f6f7dd8f56148b0097403a4`; 28 wpisów (26 plików, 2 katalogi).
- Główna kompilacja: `VAGCAN+K V3.6/VWTester.exe`, 647 168 B, SHA-256 `a448ff313cce8ee2597f14675e51196ca5b677a5561833bb65965b05628d8a23`. **Nowa w stosunku do 1.4/2.5, chroniona sekcjami `.vmp0/.vmp1`**.
- `FTD2XX.dll` 176 128 B, SHA-256 `391644ee8db7dd5fe5ceaf612ea963280a54e4f4e03af8faf2008c35039a3c06` (dwie identyczne kopie); `FTChipID.dll` 61 440 B, SHA-256 `d63d9ec2f0557184aba3d4156d755767cd234fc4b108f4209abbf28c064936c6`; `RCMicroDogSetup.dll` SHA-256 `5671711caf7446ce3496028375156cf4443c12311ac4e75c626dd740652d8ef4` (jak 1.4/2.5).
- Analiza importów programu i eksportów dołączonych bibliotek: D2XX ordinal 1=`FT_Open`, 2=`FT_Close`, 61=`FT_GetDeviceInfo`, FTChipID ordinal 8=`FTID_GetChipIDFromHandle`. **Jest to dowód zależności na etapie importu, nie wykonanych wywołań, sposobu nadawania CAN ani dodatkowego dongla.**
- `FTDIBUS.INF` i `FTDIPORT.INF`: `DriverVer=05/19/2006,2.00.00` (wersja pakietu, nie potwierdzona wersja sterownika na PC). `FixDiag.ini`, `MWB.TXT`, `MWB_de.TXT`, `VAG.txt` identyczne po normalizacji CRLF→LF z publicznym katalogiem [Skylakc/BoschME7.5-Tools](https://github.com/Skylakc/BoschME7.5-Tools/tree/main/tools/VAG-K_CAN_Commander_1%5BX%5D.4), co potwierdzono Git blob SHA-1.
- Raport: [ANALYSIS_VWTESTER_36_2026-10-23.md](ANALYSIS_VWTESTER_36_2026-10-23.md). Wyłącznie własne opracowanie; oryginalne binaria/sterowniki niepublikowane.

## S12 — dwa kolejne archiwa Commandera 3.6: porównanie binarne (2026-10-23)

- `VAG K CAN COMMANDER FULL 3,6.rar` — **RAR4, 1 730 535 B**, SHA-256 `e0059df5cb1e51434ae1eea95d4f7ff7234a176360fb739d2b382dbace83069b`.
- `VAG-K CAN-V3.6.zip` — **ZIP, 1 971 451 B**, SHA-256 `9b59b9490c0011edea1976d9d4ad16a4671e1870b45576088f298ed23b5d8b32`.
- Każde archiwum zawiera **26 plików i 2 katalogi**. Po zdjęciu odmiennego katalogu głównego i porównaniu wszystkich rozpakowanych bajtów, **25/26 plików jest identycznych z wcześniejszym `VAG COMMANDER 3.6(2).rar`** (S11); jedyna różnica to `Tester.ini`. Całe EXE `VWTester.exe` w każdym ma ten sam SHA-256 `a448ff313cce8ee2597f14675e51196ca5b677a5561833bb65965b05628d8a23`.
- `Tester.ini` SHA-256: poprzedni 3.6 `949e7fadb8da0a3dc10a480dd157923dfb8e496c39c526468f91fb486d3bfd62`; nowy FULL `03549d88a2df4d324fed66275ec463e1152dee8046c64f1d43a91cce4f83e949`; nowy ZIP `fbdc181b9aff69b849faea489ea7d0766daf53fdd42840e576ad3f0830fd1caa`. Parametry pierwszego `TARGET` 6/6/0, `FILEINDEX` 1872/1877/1879.
- Metoda i wynik: [ANALYSIS_VWTESTER_36_PACKAGES_2026-10-23.md](ANALYSIS_VWTESTER_36_PACKAGES_2026-10-23.md). Nie publikowano otrzymanych archiwów, EXE/DLL/sterowników ani surowych plików danych.

## S13 — VAG-CAN Commander 3.0 beta i 4.5 (2026-10-23)

- Materiał użytkownika: `VAG-CAN Commander V4.5.zip` — **1 663 886 B**, SHA-256 `e7980df7b33847af86ad12c52ae99c377b39c1d8f067abbe12e2d8c5de5e2b1c`, 32 pliki w 3 katalogach (bez haseł). Nie uruchamiano żadnych programów/sterowników.
- `VAG-CAN Commander 3.0 beta.exe` — **417792 B**, SHA-256 `dfb5e3f4724f6898c7c82d5d6e69ed3f795edb5f536f4aa5ff37ab17eae2a39b` (PE32, 4 sekcje). `VAG-CAN Commander4.5.exe` — **477472 B**, SHA-256 `85e89882a434ad83d19381ecbb5f9e77b14b237343b1432feb2f7300810e0050` (PE32, 5 sekcji m.in. `.mackt`; czytelne funkcje CAN).
- Własna deasemblacja obu EXE ujawniła wykonywalne kody `0x60/0x70` CAN11 ze zmienną długością danych, `0x53` o budowie **6×4 + 2×4 B**, UART 833333, a w 4.5 także selekcję **115200/833333**. Raport z adresami: [ANALYSIS_VAGCAN_30BETA_45_2026-10-23.md](ANALYSIS_VAGCAN_30BETA_45_2026-10-23.md). **Nie jest to pomiar adaptera ani potwierdzenie CAN29/listen-only.**
- Dołączone `USB driver/FTDIBUS.INF` oraz `FTDIPORT.INF` deklarują `DriverVer=04/16/2004,1.00.2154`; oznaczenia PID w sterowniku nie dowodzą VID/PID konkretnego adaptera. `Tester.ini`: `[COM] PORT=4`, `FILEINDEX=716`, dwa `TARGET=0`.
- Cztery pliki danych `FixDiag.ini`, `MWB.TXT`, `MWB_de.TXT`, `VAG.txt` są identyczne z pakietem 1.4 po normalizacji CRLF→LF, co potwierdzono przez zgodne SHA-1 obiektów Git z [Skylakc/BoschME7.5-Tools](https://github.com/Skylakc/BoschME7.5-Tools/tree/main/tools/VAG-K_CAN_Commander_1%5BX%5D.4).
- `installation.txt` odnosi się do starszej „2.0 beta”, choć w katalogu są EXE 3.0 beta i 4.5. Nazwy/etykiety dystrybucji nie są identyfikatorem firmware. Nie przechowujemy w `kcan` żadnych surowych plików ani pełnych instrukcji.

## S14 — pogłębiona analiza starych EXE 3.0 beta/4.5 (2026-10-23)

- **Brak nowego zewnętrznego binarium**: wykonano drugą, głębszą deasemblację tych samych `VAG-CAN Commander 3.0 beta.exe` i `VAG-CAN Commander4.5.exe` z archiwum **S13**. Oba SHA-256 oraz hash ZIP pozostają jak w S13.
- Potwierdzono cały łańcuch od **`GetPrivateProfileIntA("COM","PORT",0,....\\TESTER.INI)`** (4.5 `0x409D0A..0x409D11`) przez globalną wartość `0xDC23E4`, otwarcie `0x409EFA`, wybór UART w `0x40317E`, po `CreateFileA("COM%d")` w `0x408CD0`. **Prędkość 115200/833333 zależy od numeru COM, nie od zmapowanego trybu GUI**.
- Inicjalizacja 4.5 zawiera wysyłanie `51 00` (`0x409F0F`), **`C0 00`** (`0x409F25`) i `53 20 [32B]` (`0x409FC4`). Te same fakty potwierdzone kodem 3.0 beta. RX descriptor table 3.0 VA `0x44A998`, 4.5 `0x44C998`: różnica `60 00`/ `60 04` i odrębna walidacja 4.5 `len<=4`. Tablica oczekuje także `54 02`, `6F 00` (bez nadawania dowiedzionego).
- Ograniczenie `CreateFileA("COM%d")` dla COM10+ jest zgodne z dokumentacją [Microsoft Learn — CreateFileA](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-createfilea). Nie dowodzi faktycznej pracy portu na sprzęcie. Szczegóły i zakres dowodu: [ANALYSIS_VAGCAN_30BETA_45_DEEP_2026-10-23.md](ANALYSIS_VAGCAN_30BETA_45_DEEP_2026-10-23.md).

## S15 — audyt CAN29 i inicjalizacji 3.0 beta/4.5 (2026-10-23)

- **Ponowna analiza istniejących plików S13**, bez nowego programu: `VAG-CAN Commander 3.0 beta.exe` SHA-256 `dfb5e3f4724f6898c7c82d5d6e69ed3f795edb5f536f4aa5ff37ab17eae2a39b`, `VAG-CAN Commander4.5.exe` SHA-256 `85e89882a434ad83d19381ecbb5f9e77b14b237343b1432feb2f7300810e0050`. Prześledzono 0x60 TX, 0x70 RX, miejsca bezpośrednich wywołań `0x408BD0`, inicjalizację 0x51/C0/0x53 i dokładny 32-bajtowy blok początkowy, **bez uruchomienia binariów**.
- Odtworzenie: `TX_ID=(ID>>3)&FF,(ID&7)<<2,00,00` i RX `ID=(b2<<3)|((b3>>2)&7)`. **W tych funkcjach brak kodowania CAN29**; nie stwierdza to braku CAN29 we wszystkich firmware czy chronionych wersjach. Init blok `0x53`: 7×`FF 1C 00 00` plus rekord nr 6 `FF 1C 00 FF`.
- Źródło sprzętowe **do porównania, nie ustalenia faktycznego modelu PIC**: [Microchip PIC18F248](https://www.microchip.com/en-us/product/PIC18F248) (CAN2.0B Active, 6 filters, 2 masks), [PIC18FXX8 opis rejestrów RXFnSIDL](https://www.alldatasheet.com/html-pdf/143214/MICROCHIP/PIC18F248ESPSQTP/107208/214/PIC18F248ESPSQTP.html) — standardowe bity SID w rejestrze SIDL leżą w bitach 7–5, a UART przesuwa je na 4–2. **Nie utożsamiać pola protokołu UART z bezpośrednim SIDL PIC**.
- Pełny raport: [ANALYSIS_CAN29_INIT_30BETA_45_2026-10-23.md](ANALYSIS_CAN29_INIT_30BETA_45_2026-10-23.md); nowe [KCAN-D047](DISCREPANCIES.md). Nadal bez plików binarnych, firmware i surowych logów w repo.

## S16 — audyt UART writer i CAN TX w 3.0 beta/4.5 (2026-10-23)

- **Ponowna analiza tych samych EXE co S13/S15**; bez nowego binarium. `VAG-CAN Commander 3.0 beta.exe` SHA-256 `dfb5e3f4724f6898c7c82d5d6e69ed3f795edb5f536f4aa5ff37ab17eae2a39b`; `VAG-CAN Commander4.5.exe` SHA-256 `85e89882a434ad83d19381ecbb5f9e77b14b237343b1432feb2f7300810e0050`.
- Metoda: statyczna deasemblacja x86, parsowanie tablic PE IMAGE_IMPORT_DESCRIPTOR/Import Lookup Table potwierdzające importy po adresach IAT: **4.5 `0x44C278=WriteFile`, `0x44C27C=GetOverlappedResult`, `0x44C2A4=WaitForSingleObject`, `0x44C270=EscapeCommFunction`**, 3.0 odpowiednio `0x44A278`, `0x44A27C`, `0x44A2A4`, `0x44A270`. Nie uruchomiono programu ani sterowników.
- Dowody `0x408BD0` (bezwarunkowy sukces przy otwartym porcie, brak kontroli write result i liczby bajtów), `0x403510/0x4034F0` (TX rejestruje i zwraca sukces bez potwierdzenia CAN), `0x408CD0` (SETDTR/500ms/CLRDTR/SETRTS), lokalny brak walidacji N<=8 w kodzie TX. **Nadal nie oznaczają rzeczywistego zachowania PIC i firmware**.
- Wyniki i szczegółowe adresy: [ANALYSIS_SERIAL_TX_RELIABILITY_30BETA_45_2026-10-23.md](ANALYSIS_SERIAL_TX_RELIABILITY_30BETA_45_2026-10-23.md), zadania [D048–D050](DISCREPANCIES.md). Bez kopii obcych EXE/DLL i surowych logów w repo.

### Win32 API do S16 — weryfikacja niezależna

- [Microsoft Learn: GetOverlappedResult](https://learn.microsoft.com/en-us/windows/win32/api/ioapiset/nf-ioapiset-getoverlappedresult) — `bWait=TRUE` może blokować do zakończenia, mimo wcześniejszego `WaitForSingleObject(258)`; zwraca liczbę rzeczywiście przetransferowanych bajtów.
- [Microsoft Learn: WriteFile](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-writefile) — rozróżnienie `ERROR_IO_PENDING` od błędów oraz zapis częściowy.
- [Microsoft Learn: EscapeCommFunction](https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-escapecommfunction) — znaczenie numerycznych rozkazów DTR/RTS `3/5/6`.

## S17 — VAG-CAN Commander V5.1 (EXE 5.0+ECU), 2026-10-23

- Użytkownik przekazał `VAG-CAN Commander V5.1.zip`, ZIP 1 113 420 B, SHA-256 **`151913526f55e2528ccf153a0d47b69d67d53dde96ed8057af9efe083aeea94f`**, 28 plików w 4 katalogach.
- `VAG-CAN Commander+EDC15.exe` — **466968 B**, SHA-256 **`811bf59355614e0d07aa2e4c10fedd01fbff2b0148feab4491f0f731c98d45ba`**, Win32 x86, czytelne funkcje COM/CAN. Dosłowny napis w zasobach GUI: `VAG-CAN COMMANDER 5.0+ECU (full)` — etykieta ZIP **V5.1 nie jest samodzielnym dowodem wersji**. Główne importy to API Win32 COM, **nie** import FTChipID/FTD2XX (choć sterownik dostarcza D2XX).
- `memory.bin`: **2048 B**, SHA-256 **`739e3bf5eca392955fa70e7aeea725dad3c39e6d3d69d13b1d65c183596d6ea4`**. EXE ma odniesienie do tej nazwy przy `0x4135E0` w ścieżce obsługi pliku; **rola niepotwierdzona**, oryginału ani zawartości nie publikować.
- Sterownik FTDI INF: **`DriverVer=03/13/2008,2.04.06`**, 32/64-bit; `ftdiport.inf`: domyślna propozycja `LatencyTimer=16`, nie wynik na urządzeniu użytkownika. `Tester.ini`: `CAN_PORT=5, KWP_PORT=5, FILEINDEX=1656`.
- Cztery teksty po CRLF→LF mają zgodne SHA-1 obiektów Git jak 1.4: `FixDiag.ini 402da46683ecfa09e3742fae8791e3dea2e4963e`, `MWB.TXT 94aff48b1782e1b42cd9679b48e1303b45a70cf0`, `MWB_de.TXT b665cca873deedf86b1e4887dc1fd9103c150a7e`, `VAG.txt 64a4503a6d5708ecf42e2702946d871bf0ed90ce`.
- Pełna analiza deasemblacji 0x51/C0/0x53/0x60/0x70, UART, CAN29 i statusów Win32: [ANALYSIS_VAGCAN_50ECU_V51_2026-10-23.md](ANALYSIS_VAGCAN_50ECU_V51_2026-10-23.md). Tylko źródło użytkownika i autorskie opracowanie; brak programów, sterowników, surowych logów i `memory.bin` w GitHub.

## S18 — ponowny audyt V5.1: memory.bin i TP2.0 (2026-10-23)

- Ponowna **statyczna analiza wcześniej dostarczonego** `VAG-CAN Commander V5.1.zip`; SHA-256 `151913526f55e2528ccf153a0d47b69d67d53dde96ed8057af9efe083aeea94f`, sprawdzono ZIP CRC (OK) i główny EXE SHA-256 `811bf59355614e0d07aa2e4c10fedd01fbff2b0148feab4491f0f731c98d45ba`. Nie ma nowego binarium.
- Zmapowano vtable CFile (VA `0x459654`): +0x20 `Open 0x449B48`, +0x38 `Write 0x449C9F`, +0x4C `Close 0x449D63`; wywołania `0x413615/0x413A13/0x413A86/0x413DC4`. `memory.bin` w tej ścieżce jest **plikiem wyjściowym** ReadMemory, z flagami `modeCreate|modeWrite`. Weryfikacja API: [Microsoft MFC CFile](https://learn.microsoft.com/en-us/cpp/mfc/reference/cfile-class), [dawne flagi MFC CFile](https://dos-help.soulsphere.org/mfc.hlp/CFile_cln__cln_CFile.html).
- Rozpoznano w `0x414F40` trzy predefiniowane rozmiary odczytu **0x80000, 0x4000, 0x1000** i porcje **0x40/0x40/0x10** oraz wariant pól użytkownika `0xFF` z GUI `0x41F3C6–0x41F43F`. Dostarczony `memory.bin` nadal ma 2048B; jego zawartość nie jest publikowana.
- CAN: `0x420360` dzieli dane po 7 bajtów; buduje TP2.0 seq/flags i przez `0x4207D0` wywołuje `0x403520` CAN11; `0x420580` obsługuje m.in. odpowiedzi i ACK. Kontekst oparty na [VW Transport Protocol 2.0](https://jazdw.net/tp20), [I CAN Hack](https://icanhack.nl/knowledge-base/diagnostics/vw-tp20/) i [ACTIA TP1.6/2.0](https://www.ime-actia.de/en/vehicle-diagnostics/tp1-6-2-0/). Implementacja GUI/hosta, **nie walidacja firmware, CAN29 ani ACK magistrali**.
- Raport: [ANALYSIS_VAGCAN_50ECU_V51_MEMORY_TP20_2026-10-23.md](ANALYSIS_VAGCAN_50ECU_V51_MEMORY_TP20_2026-10-23.md). Bez publikacji binariów/dumpów.

## S19 — kontrolny audyt ośmiu dostępnych archiwów, tylko jawny kod (2026-10-23)

- **Fizycznie zweryfikowane** 8 archiwów: `Polski VAG 4.9(1).rar`, `VAG COMMANDER 3.6(2).rar`, `VAG K CAN COMMANDER FULL 3,6.rar`, `VAG K+CAN COMMANDER 1.4zainstalowany.rar`, `VAG-CAN Commander V4.5.zip`, `VAG-CAN Commander V5.1.zip`, `VAG-K CAN-V3.6.zip`, `VWool 2 0 9 en PL.rar`. Weryfikacja sum SHA-256, odczyt całej zawartości RAR `libarchive`, kontrola rozmiarów i ZIP CRC. Pełny wykaz sum i decyzji analitycznych: [AUDIT_READABLE_FILES_2026-10-23.md](AUDIT_READABLE_FILES_2026-10-23.md).
- **Do reanalizy kodu dopuszczono trzy jawne EXE**: `3.0 beta` SHA-256 `dfb5e3f4724f6898c7c82d5d6e69ed3f795edb5f536f4aa5ff37ab17eae2a39b`, `4.5` SHA-256 `85e89882a434ad83d19381ecbb5f9e77b14b237343b1432feb2f7300810e0050`, `5.0+ECU` SHA-256 `811bf59355614e0d07aa2e4c10fedd01fbff2b0148feab4491f0f731c98d45ba`. W 4.5 pominięto nieczytelne/niestandardowe obszary; analizowano wyłącznie bezpośrednio zdeasemblowane instrukcje.
- **Wyłączono kod** chronionego głównego EXE 1.4, identycznego w trzech pakietach VMProtect „3.6” i program docelowy nieodczytany ze stuba Inno Polski VAG 4.9. `VWTOOL` (NE 16-bit) i XOR `0x85` CSV potwierdzono jako jawne materiały starszej diagnostyki, nie CAN. **Binarka FULL 2.5 nie jest obecnie dostępna do bezpośredniego odczytu** (wcześniejsze raporty pozostają źródłem historycznym).
- Bezpośredni kod TP2.0, RX `DLC=0` oraz nieosiągalny warunek A1/A3 porównano w tych samych funkcjach wszystkich trzech czytelnych EXE; raport zawiera adresy, warianty i zastrzeżenia. Bez wykonywania aplikacji i bez publikowania surowych plików.
