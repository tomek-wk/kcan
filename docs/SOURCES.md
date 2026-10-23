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
